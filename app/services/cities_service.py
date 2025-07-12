import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from app.const import CITY_RESPONSE_KEYS
from app.repositories.areas_of_interest_repository import fetch_areas_of_interest
from app.repositories.cities_repository import fetch_cities
from app.repositories.projects_repository import fetch_projects
from app.repositories.scenarios_repository import fetch_indicator_values
from app.schemas.common_schema import ApplicationIdParam
from app.utils.filters import construct_filter_formula, construct_filter_formula_v2
from app.utils.settings import Settings

settings = Settings()


def list_cities(
    application_id: Optional[ApplicationIdParam],
    projects: Optional[List[str]],
    country_code_iso3: Optional[str],
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of cities based on the provided filters.

    Args:
        application_id (Optional[str]): A WRI application ID to filter by.
        projects (Optional[List[str]]): List of Project IDs to filter by.
        country_code_iso3 (Optional[str]): ISO 3166-1 alpha-3 country code to filter by.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the filtered cities' data.
    """
    # Fetch projects based on provided project IDs/application ID if provided
    projects_filters = {}
    if application_id:
        projects_filters["application_id"] = application_id.value
    if projects:
        projects_filters["id"] = projects
    projects_filter_formula = construct_filter_formula(projects_filters)
    fetched_projects = fetch_projects(projects_filter_formula)
    if not fetched_projects:
        return None
    fetched_project_ids = {
        project["id"]: project["fields"]["id"] for project in fetched_projects
    }

    # Filter cities based on retrieved projects and country code
    cities_filters = {}
    if fetched_project_ids:
        cities_filters["projects"] = list(fetched_project_ids.values())
    if country_code_iso3:
        cities_filters["country_code_iso3"] = country_code_iso3
    aoi_filters = {}
    if application_id:
        aoi_filters["application_id"] = application_id.value

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                lambda: fetch_cities(construct_filter_formula(cities_filters))
            ): "cities",
            executor.submit(lambda: fetch_indicator_values()): "indicator_values",
            executor.submit(
                lambda: fetch_areas_of_interest(
                    construct_filter_formula_v2(aoi_filters)
                )
            ): "aoi_data",
        }

        results = {}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    cities_list = results["cities"]
    sorted_indicator_values = sorted(
        results["indicator_values"],
        key=lambda x: (x["fields"].get("cities_id", [""])[0]),
    )
    grouped_indicator_values = {
        key: list(group)
        for key, group in itertools.groupby(
            sorted_indicator_values, lambda x: x["fields"].get("cities_id", [""])[0]
        )
    }
    areas_of_interest_list = results["aoi_data"]

    # Return empty list if no cities found
    if not cities_list:
        return []

    # Update project IDs in each city to reflect  projects
    for city in cities_list:
        city_projects = [
            fetched_project_ids[project]
            for project in city["fields"]["projects"]
            if project in fetched_project_ids.keys()
        ]
        city["fields"]["projects"] = city_projects

    # Return the filtered cities data
    city_res_list = []
    for city in cities_list:
        bbox_dict = {}
        area_of_interests = []
        if areas_of_interest_list:
            for aoi in areas_of_interest_list:
                if city["id"] in aoi["fields"].get("cities", []):
                    if "bounding_box" in aoi["fields"]:
                        bbox_dict[aoi["fields"]["id"]] = aoi["fields"]["bounding_box"]
                    area_of_interests.append(aoi["fields"]["id"])

        city_response = {key: city["fields"].get(key) for key in CITY_RESPONSE_KEYS}
        city_id = city_response["id"]
        indicator_values = grouped_indicator_values.get(city_id)
        city_response["indicator_values"] = {}
        if area_of_interests:
            city_response["area_of_interests"] = area_of_interests
            city_response["admin_levels"] = area_of_interests

        if indicator_values:
            sorted_selected_indicator_values = sorted(
                indicator_values if indicator_values else [],
                key=lambda x: (x["fields"]["areas_of_interest_id"][0]),
            )
            grouped_selected_indicator_values = {
                key: list(group)
                for key, group in itertools.groupby(
                    sorted_selected_indicator_values,
                    lambda x: x["fields"]["areas_of_interest_id"][0],
                )
            }
            for aoi, value in grouped_selected_indicator_values.items():
                city_response["indicator_values"][aoi] = {
                    f'{i["fields"]["indicators_id"][0]}__{i["fields"]["areas_of_interest_id"][0]}': (
                        i["fields"]["value"]
                        if i["fields"].get("indicators_id")
                        and i["fields"].get("areas_of_interest_id")
                        and i["fields"].get("value")
                        else None
                    )
                    for i in value
                }
        city_response["bounding_box"] = bbox_dict

        city_response["layers_url"] = {
            "pmtiles": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/{settings.env}/boundaries/pmtiles/{city_id}.pmtiles",
            "geojson": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/{settings.env}/boundaries/geojson/{city_id}.geojson",
        }
        city_res_list.append(city_response)
    return city_res_list


def get_city_by_city_id(
    application_id: Optional[ApplicationIdParam], city_id: str
) -> Optional[Dict]:
    """
    Retrieve city data for a specific city ID.

    Args:
        city_id (str): The ID of the city to retrieve.

    Returns:
        dict: A dictionary containing the city's data based on CITY_RESPONSE_KEYS.
    """
    filter_formula = {}
    if city_id:
        filter_formula["cities"] = city_id
    if application_id:
        filter_formula["application_id"] = application_id.value

    # Define the tasks to be executed asynchronously
    future_to_func = {
        lambda: fetch_projects(construct_filter_formula(filter_formula)): "projects",
        lambda: fetch_cities(f'"{city_id}" = {{id}}'): "city_data",
        lambda: fetch_indicator_values(
            {"cities": city_id} if city_id else {}
        ): "indicator_values",
        lambda: fetch_areas_of_interest(
            construct_filter_formula_v2(filter_formula)
        ): "aoi_data",
    }
    city_data = []
    indicator_values = []
    all_projects = []
    aoi_list = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for func, name in future_to_func.items()}
        for future in as_completed(futures):
            func_name = futures[future]
            if func_name == "projects":
                all_projects = future.result()
            if func_name == "city_data":
                city_data = future.result()
            if func_name == "indicator_values":
                indicator_values = future.result()
            if func_name == "aoi_data":
                aoi_list = future.result()
    if not city_data:
        return None
    sorted_indicator_values = sorted(
        indicator_values if indicator_values else [],
        key=lambda x: (x["fields"].get("cities_id", [""])[0]),
    )
    grouped_indicator_values = {
        key: list(group)
        for key, group in itertools.groupby(
            sorted_indicator_values, lambda x: x["fields"].get("cities_id", [""])[0]
        )
    }

    project_id_map = {
        project["id"]: project["fields"]["id"] for project in all_projects
    }
    city = city_data[0]["fields"]

    city["projects"] = [
        project_id_map.get(project)
        for project in city["projects"]
        if project in project_id_map.keys()
    ]

    city_response = {key: city.get(key) for key in CITY_RESPONSE_KEYS}

    bbox_dict = {}
    area_of_interests = []
    if aoi_list:
        for aoi in aoi_list:
            if city_data[0]["id"] in aoi["fields"].get("cities", []):
                if "bounding_box" in aoi["fields"]:
                    bbox_dict[aoi["fields"]["id"]] = aoi["fields"]["bounding_box"]
                area_of_interests.append(aoi["fields"]["id"])
    city_response["bounding_box"] = bbox_dict
    if area_of_interests:
        city_response["area_of_interests"] = area_of_interests
        city_response["admin_levels"] = area_of_interests

    # s3_base_path = city_response.get(
    #     "s3_base_path", "https://cities-indicators.s3.eu-west-3.amazonaws.com"
    # )
    # if s3_base_path.endswith("/"):
    #     s3_base_path = s3_base_path[:-1]

    # city_response["layers_url"] = {
    #     "pmtiles": f"{s3_base_path}/data-pmtiles/{city_id}.pmtiles",
    #     "geojson": f"{s3_base_path}/data-geojson/{city_id}.geojson",
    # }
    # s3_base_path = city_response.get(
    #     "s3_base_path", "https://cities-indicators.s3.eu-west-3.amazonaws.com"
    # )
    # if s3_base_path.endswith("/"):
    #     s3_base_path = s3_base_path[:-1]

    city_response["indicator_values"] = []
    selected_city_indicator_values = grouped_indicator_values.get(city_id)

    sorted_selected_indicator_values = sorted(
        selected_city_indicator_values if selected_city_indicator_values else [],
        key=lambda x: (x["fields"]["areas_of_interest_id"][0]),
    )
    grouped_selected_indicator_values = {
        key: list(group)
        for key, group in itertools.groupby(
            sorted_selected_indicator_values,
            lambda x: x["fields"]["areas_of_interest_id"][0],
        )
    }
    city_response["indicator_values"] = {}
    for aoi, value in grouped_selected_indicator_values.items():
        city_response["indicator_values"][aoi] = {
            f'{i["fields"]["indicators_id"][0]}__{i["fields"]["areas_of_interest_id"][0]}': (
                i["fields"]["value"]
                if i["fields"].get("indicators_id")
                and i["fields"].get("areas_of_interest_id")
                and i["fields"].get("value")
                else None
            )
            for i in value
        }

    city_response["layers_url"] = {
        "pmtiles": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/{settings.env}/boundaries/pmtiles/{city_id}.pmtiles",
        "geojson": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/{settings.env}/boundaries/geojson/{city_id}.geojson",
    }
    return city_response
