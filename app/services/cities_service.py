import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from cartoframes import read_carto
from cartoframes.auth import set_default_credentials

from app.const import CITY_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_cities, fetch_first_city
from app.repositories.indicators_repository import fetch_indicators
from app.repositories.projects_repository import fetch_projects
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.settings import Settings

settings = Settings()

set_default_credentials(
    username=settings.carto_username, api_key=settings.carto_api_key
)


def list_cities(
    projects: Optional[List[str]], country_code_iso3: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of cities based on the provided filters.

    Args:
        projects (Optional[List[str]]): List of Project IDs to filter by.
        country_code_iso3 (Optional[str]): ISO 3166-1 alpha-3 country code to filter by.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the filtered cities' data.
    """
    filters = {}

    if projects:
        filters["projects"] = projects
    if country_code_iso3:
        filters["country_code_iso3"] = country_code_iso3

    filter_formula = construct_filter_formula(filters)

    # Define the tasks to be executed asynchronously
    future_to_func = {
        lambda: fetch_cities(filter_formula): "cities",
    }

    cities_list = []
    all_projects = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for func, name in future_to_func.items()}
        for future in as_completed(futures):
            func_name = futures[future]
            if func_name == "cities":
                cities_list = future.result()

    if not cities_list:
        return []

    city_ids = [city["fields"]["city_id"] for city in cities_list]

    # Asynchronously fetch all projects related to the cities
    with ThreadPoolExecutor() as executor:
        all_projects = executor.submit(
            fetch_projects, construct_filter_formula({"cities": city_ids})
        ).result()

    project_id_map = {
        project["id"]: project["fields"]["project_id"] for project in all_projects
    }

    for city in cities_list:
        city_projects = [
            project_id_map.get(project) for project in city["fields"]["projects"]
        ]
        city["fields"]["projects"] = city_projects

    return [
        {key: city["fields"].get(key) for key in CITY_RESPONSE_KEYS}
        for city in cities_list
    ]


def get_city_by_city_id(city_id: str) -> Dict:
    """
    Retrieve city data for a specific city ID.

    Args:
        city_id (str): The ID of the city to retrieve.

    Returns:
        dict: A dictionary containing the city's data based on CITY_RESPONSE_KEYS.
    """
    filter_formula = f'"{city_id}" = {{city_id}}'

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
        return {}

    city = city_data[0]["fields"]
    project_filter_formula = construct_filter_formula({"cities": [city_id]})

    # Asynchronously fetch all projects related to the city
    with ThreadPoolExecutor() as executor:
        all_projects = executor.submit(fetch_projects, project_filter_formula).result()

    project_id_map = {
        project["id"]: project["fields"]["project_id"] for project in all_projects
    }

    city_projects = [project_id_map.get(project) for project in city["projects"]]
    city["projects"] = city_projects

    city_response = {key: city[key] for key in CITY_RESPONSE_KEYS if key in city}

    return city_response


def get_city_indicators(city_id: str, admin_level: str) -> Dict:
    """
    Retrieve indicators for a specific city and administrative level.

    Args:
        city_id (str): The ID of the city to retrieve indicators for.
        admin_level (str): The administrative level to filter by.

    Returns:
        Dict: A dictionary containing the city's indicators.
    """
    city_indicators_df = read_carto(
        f"SELECT *, geo_name as city_name FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'"
    ).copy()
    city_indicators_df = city_indicators_df[
        [
            "city_name",
            "geo_id",
            "geo_level",
            "geo_parent_name",
            "indicator_version",
            "indicator",
            "value",
        ]
    ]
    city_indicators_df = city_indicators_df.pivot(
        index=[
            "city_name",
            "geo_id",
            "geo_level",
            "geo_parent_name",
            "indicator_version",
        ],
        columns="indicator",
        values="value",
    )
    city_indicators_df.reset_index(inplace=True)

    city_indicators = json.loads(city_indicators_df.to_json(orient="records"))

    return city_indicators


def get_city_geometry(city_id: str, admin_level: str) -> Optional[Dict]:
    """
    Retrieve the geometry of a specific city and administrative level.

    Args:
        city_id (str): The ID of the city to retrieve geometry for.
        admin_level (str): The administrative level to filter by.

    Returns:
        dict: A GeoJSON dictionary representing the city's geometry.
    """
    city_geometry_df = read_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    ).copy()

    if city_geometry_df.empty:
        return None

    # Select only necessary columns for GeoJSON response
    city_geometry_df = city_geometry_df[
        [
            "geo_id",
            "city_name",
            "geo_level",
            "geo_parent_name",
            "geo_version",
            "the_geom",
        ]
    ]

    # Calculate the bounding box for each polygon
    city_geometry_df["bbox"] = city_geometry_df["the_geom"].apply(
        lambda geom: geom.bounds
    )

    # Convert to GeoJSON and add bounding box to properties
    city_geojson = json.loads(city_geometry_df.to_json())

    # Add bounding box information to each feature in the GeoJSON
    bouding_box_coordinates = [180, 90, -180, -90]
    for feature, bbox in zip(city_geojson["features"], city_geometry_df["bbox"]):
        if bbox[0] < bouding_box_coordinates[0]:
            bouding_box_coordinates[0] = bbox[0]
        if bbox[1] < bouding_box_coordinates[1]:
            bouding_box_coordinates[1] = bbox[1]
        if bbox[2] > bouding_box_coordinates[2]:
            bouding_box_coordinates[2] = bbox[2]
        if bbox[3] > bouding_box_coordinates[3]:
            bouding_box_coordinates[3] = bbox[3]

        feature["properties"]["bbox"] = bbox

    city_geojson = {"bbox": bouding_box_coordinates, **city_geojson}

    return city_geojson


def get_city_geometry_with_indicators(
    city_id: str, indicator_id: str, admin_level: str
) -> Dict:
    """
    Retrieve the geometry, bounding boxes, and indicators of a specific city and administrative level in GeoJSON format.

    Args:
        city_id (str): The ID of the city to retrieve geometry and indicators for.
        indicator_id (str): The ID of the indicator to retrieve.
        admin_level (Optional[str]): The administrative level to filter the geometry and indicators. If no value is provided, "units_boundary_level" value will be used as the default.

    Returns:
        Dict: A GeoJSON dictionary representing the city's geometry along with its indicators and bounding boxes.
    """
    airtable_city = fetch_first_city(generate_search_query("city_id", city_id))
    admin_level = airtable_city["fields"].get(admin_level, admin_level)

    geo_level_filter = f"AND geo_level = '{admin_level}'" if admin_level else ""

    with ThreadPoolExecutor() as executor:
        geometry_future = executor.submit(
            read_carto,
            f"SELECT *, geo_name as city_name FROM boundaries WHERE geo_parent_name = '{city_id}' {geo_level_filter}",
        )
        indicators_future = executor.submit(
            read_carto,
            f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' AND indicator = '{indicator_id}' {geo_level_filter} AND indicator_version = 0",
        )
        city_geometry_df = geometry_future.result()
        city_indicators_df = indicators_future.result()

    city_geometry_df = city_geometry_df[
        [
            "city_name",
            "geo_id",
            "geo_level",
            "geo_parent_name",
            "geo_version",
            "the_geom",
        ]
    ]

    # Fetch indicator metadata
    indicators_dict = {
        indicator["fields"]["indicator_id"]: indicator["fields"]
        for indicator in fetch_indicators()
    }

    city_geometry_df = city_geometry_df.merge(
        city_indicators_df, on="geo_id", how="left"
    )

    # Add indicator information from metadata
    city_geometry_df["indicator_label"] = indicators_dict[indicator_id].get(
        "indicator_label"
    )
    city_geometry_df["indicator_unit"] = indicators_dict[indicator_id].get("unit")

    # Calculate the bounding box for each polygon
    city_geometry_df["bbox"] = city_geometry_df["the_geom"].apply(
        lambda geom: geom.bounds
    )

    # Convert to GeoJSON and add bounding box to properties
    city_geojson = json.loads(city_geometry_df.to_json())

    # Add bounding box information to each feature in the GeoJSON
    bouding_box_coordinates = [180, 90, -180, -90]
    for feature, bbox in zip(city_geojson["features"], city_geometry_df["bbox"]):
        if bbox[0] < bouding_box_coordinates[0]:
            bouding_box_coordinates[0] = bbox[0]
        if bbox[1] < bouding_box_coordinates[1]:
            bouding_box_coordinates[1] = bbox[1]
        if bbox[2] > bouding_box_coordinates[2]:
            bouding_box_coordinates[2] = bbox[2]
        if bbox[3] > bouding_box_coordinates[3]:
            bouding_box_coordinates[3] = bbox[3]

        feature["properties"]["bbox"] = bbox

    city_geojson = {"bbox": bouding_box_coordinates, **city_geojson}

    return city_geojson
