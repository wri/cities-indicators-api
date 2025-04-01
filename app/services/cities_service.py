from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from app.const import CITY_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_cities
from app.repositories.projects_repository import fetch_projects
from app.schemas.common_schema import ApplicationIdParam
from app.utils.filters import construct_filter_formula
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

    cities_filter_formula = construct_filter_formula(cities_filters)
    cities_list = fetch_cities(cities_filter_formula)

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
        city_response = {key: city["fields"].get(key) for key in CITY_RESPONSE_KEYS}
        s3_base_path = city_response.get(
            "s3_base_path", "https://cities-indicators.s3.eu-west-3.amazonaws.com"
        )
        city_response["layers_url"] = {
            "pmtiles": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/prd/boundaries/pmtiles/{city_response['id']}.pmtiles",
            "geojson": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/prd/boundaries/geojson/{city_response['id']}.geojson",
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
    filter_formula = f'"{city_id}" = {{id}}'

    # Define the tasks to be executed asynchronously
    future_to_func = {
        lambda: fetch_cities(filter_formula): "city_data",
    }

    city_data = []
    all_projects = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for func, name in future_to_func.items()}
        for future in as_completed(futures):
            func_name = futures[future]
            if func_name == "city_data":
                city_data = future.result()

    if not city_data:
        return None

    city = city_data[0]["fields"]
    projects_filters = {}
    if application_id:
        projects_filters["application_id"] = application_id.value
    projects_filters["cities"] = [city_id]
    project_filter_formula = construct_filter_formula(projects_filters)

    # Asynchronously fetch all projects related to the city
    with ThreadPoolExecutor() as executor:
        all_projects = executor.submit(fetch_projects, project_filter_formula).result()

    project_id_map = {
        project["id"]: project["fields"]["id"] for project in all_projects
    }

    city_projects = [project_id_map.get(project) for project in city["projects"]]
    city["projects"] = city_projects

    city_response = {key: city.get(key) for key in CITY_RESPONSE_KEYS}

    s3_base_path = city_response.get(
        "s3_base_path", "https://cities-indicators.s3.eu-west-3.amazonaws.com"
    )
    if s3_base_path.endswith("/"):
        s3_base_path = s3_base_path[:-1]

    city_response["layers_url"] = {
        "pmtiles": f"{s3_base_path}/data-pmtiles/{city_id}.pmtiles",
        "geojson": f"{s3_base_path}/data-geojson/{city_id}.geojson",
    }
    s3_base_path = city_response.get(
        "s3_base_path", "https://cities-indicators.s3.eu-west-3.amazonaws.com"
    )
    if s3_base_path.endswith("/"):
        s3_base_path = s3_base_path[:-1]

    city_response["layers_url"] = {
        "pmtiles": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/prd/boundaries/pmtiles/{city_id}.pmtiles",
        "geojson": f"https://wri-cities-data-api.s3.us-east-1.amazonaws.com/data/prd/boundaries/geojson/{city_id}.geojson",
    }
    return city_response
