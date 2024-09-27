import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from cartoframes.auth import set_default_credentials

from app.const import CITY_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_cities, fetch_first_city
from app.repositories.indicators_repository import fetch_indicators
from app.repositories.projects_repository import fetch_projects
from app.utils.carto import query_carto
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.formatters import unit_formatter
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
    # Fetch active projects based on provided project IDs
    projects_filters = {"status": "Active"}
    if projects:
        projects_filters["id"] = projects

    projects_filter_formula = construct_filter_formula(projects_filters)
    active_projects = fetch_projects(projects_filter_formula)
    active_project_ids = {
        project["id"]: project["fields"]["id"] for project in active_projects
    }

    # Filter cities based on active projects and country code
    cities_filters = {}
    if active_project_ids:
        cities_filters["projects"] = list(active_project_ids.values())
    if country_code_iso3:
        cities_filters["country_code_iso3"] = country_code_iso3

    cities_filter_formula = construct_filter_formula(cities_filters)
    cities_list = fetch_cities(cities_filter_formula)

    # Return empty list if no cities found
    if not cities_list:
        return []

    # Update project IDs in each city to reflect active projects
    for city in cities_list:
        city_projects = [
            active_project_ids[project]
            for project in city["fields"]["projects"]
            if project in active_project_ids.keys()
        ]
        city["fields"]["projects"] = city_projects

    # Return the filtered cities data
    return [
        {key: city["fields"].get(key) for key in CITY_RESPONSE_KEYS}
        for city in cities_list
    ]


def get_city_by_city_id(city_id: str) -> Optional[Dict]:
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
    project_filter_formula = construct_filter_formula({"cities": [city_id]})

    # Asynchronously fetch all projects related to the city
    with ThreadPoolExecutor() as executor:
        all_projects = executor.submit(fetch_projects, project_filter_formula).result()

    project_id_map = {
        project["id"]: project["fields"]["id"] for project in all_projects
    }

    city_projects = [project_id_map.get(project) for project in city["projects"]]
    city["projects"] = city_projects

    city_response = {key: city[key] for key in CITY_RESPONSE_KEYS if key in city}

    return city_response


def get_city_indicators(city_id: str, admin_level: str) -> Optional[Dict]:
    """
    Retrieve indicators for a specific city and administrative level.

    Args:
        city_id (str): The ID of the city to retrieve indicators for.
        admin_level (str): The administrative level to filter by.

    Returns:
        Dict: A dictionary containing the city's indicators.
    """
    city_indicators_df = query_carto(
        f"SELECT *, geo_name as name FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'"
    ).copy()

    if city_indicators_df.empty:
        return None

    city_indicators_df = city_indicators_df[
        [
            "name",
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
            "name",
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
    city_geometry_df = query_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    ).copy()

    if city_geometry_df.empty:
        return None

    # Select only necessary columns for GeoJSON response
    city_geometry_df = city_geometry_df[
        [
            "geo_id",
            "geo_level",
            "geo_name",
            "geo_parent_name",
            "geo_version",
            "the_geom",
        ]
    ]

    # Calculate the bounding box for each polygon
    city_geometry_df.loc[:, "bbox"] = city_geometry_df["the_geom"].apply(
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
    city_id: str, admin_level: Optional[str], indicator_id: Optional[str]
) -> Optional[Dict]:
    """
    Retrieve the geometry, bounding boxes, and indicators of a specific city and
    administrative level in GeoJSON format.

    Args:
        city_id (str): The ID of the city to retrieve geometry and indicators for.
        admin_level (Optional[str]): The administrative level to filter the geometry and indicators.
        indicator_id (Optional[str]): The ID of the indicator to retrieve.

    Returns:
        Dict: A GeoJSON dictionary representing the city's geometry along with its indicators and bounding boxes.
    """
    # Fetch city details and handle missing city data
    airtable_city = fetch_first_city(generate_search_query("id", city_id))
    if not airtable_city:
        return None

    # Use the provided admin_level or fallback to the city's admin_level
    admin_level = airtable_city["fields"].get(admin_level, admin_level)
    geo_level_filter = f"AND geo_level = '{admin_level}'" if admin_level else ""
    indicator_filter = f"AND indicator = '{indicator_id}'" if indicator_id else ""

    # Fetch data concurrently for geometry, indicators, and all indicators metadata
    with ThreadPoolExecutor() as executor:
        futures = {
            "geometry": executor.submit(
                query_carto,
                f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' {geo_level_filter}",
            ),
            "indicators": executor.submit(
                query_carto,
                f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' {indicator_filter} {geo_level_filter} AND indicator_version = 0",
            ),
            "all_indicators": executor.submit(fetch_indicators),
        }

        # Retrieve results and handle potential errors
        city_geometry_df = futures["geometry"].result()
        city_indicators_df = futures["indicators"].result()
        all_indicators = futures["all_indicators"].result()

    # Handle empty results
    if city_geometry_df.empty or city_indicators_df.empty:
        return None

    # Prepare the geometry data
    city_geometry_df = city_geometry_df[
        [
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "geo_version",
            "the_geom",
        ]
    ]
    city_geometry_df["bbox"] = city_geometry_df["the_geom"].apply(
        lambda geom: geom.bounds
    )

    # Prepare the indicators data and merge with unit information
    indicators_dict = {
        indicator["fields"]["id"]: indicator["fields"] for indicator in all_indicators
    }

    indicator_unities = [
        {
            "indicator": indicator_name,
            "legend_styling": json.loads(indicator_info.get("legend_styling")),
            "map_styling": json.loads(indicator_info.get("map_styling")),
            "name": indicator_info.get("name"),
            "unit": indicator_info.get("unit"),
        }
        for indicator_name in city_indicators_df["indicator"].unique()
        if (indicator_info := indicators_dict.get(indicator_name, {}))
    ]

    merged_indicators_df = pd.merge(
        pd.DataFrame(indicator_unities), city_indicators_df, on="indicator"
    )

    # Create a new column for unit values and handle missing values
    city_indicators_df["unit_values"] = merged_indicators_df.apply(
        lambda row: {
            "legend_styling": row["legend_styling"],
            "map_styling": row["map_styling"],
            "name": row["name"],
            "unit": row["unit"],
            "value": row["value"] if pd.notna(row["value"]) else None,
        },
        axis=1,
    )

    # Pivot the DataFrame to structure indicators per geo_id
    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="unit_values"
    )

    # Merge geometry and indicators
    city_gdf = pd.merge(city_geometry_df, city_indicators_df, on="geo_id")

    # Convert the merged data to GeoJSON
    city_geojson = json.loads(city_gdf.to_json())

    # Calculate overall bounding box
    bounding_box_coordinates = [180, 90, -180, -90]
    for feature, bbox in zip(city_geojson["features"], city_geometry_df["bbox"]):
        bounding_box_coordinates = [
            min(bounding_box_coordinates[0], bbox[0]),
            min(bounding_box_coordinates[1], bbox[1]),
            max(bounding_box_coordinates[2], bbox[2]),
            max(bounding_box_coordinates[3], bbox[3]),
        ]
        feature["properties"]["bbox"] = bbox

    # Return the final result with bounding box included
    return {
        "bbox": bounding_box_coordinates,
        **city_geojson,
    }


def get_city_geometry_with_indicators_csv(
    city_id: str, admin_level: Optional[str], indicator_id: Optional[str]
) -> Optional[Dict]:
    """
    Retrieve the geometry, bounding boxes, and indicators of a specific city
    and administrative level, and return the data as a list of dictionaries (CSV-like).

    Args:
        city_id (str): The ID of the city to retrieve geometry and indicators for.
        admin_level (Optional[str]): The administrative level to filter the geometry and indicators.
        indicator_id (Optional[str]): The ID of a specific indicator to retrieve.

    Returns:
        Optional[Dict]: A list of dictionaries, where each dictionary represents
                        a row of the city's geometry, indicators, and bounding boxes.
                        If no data is found, returns None.
    """
    # Fetch city details and handle missing city data
    airtable_city = fetch_first_city(generate_search_query("id", city_id))
    if not airtable_city:
        return None

    # Use the provided admin_level or fallback to the city's admin_level
    admin_level = airtable_city["fields"].get(admin_level, admin_level)
    geo_level_filter = f"AND geo_level = '{admin_level}'" if admin_level else ""
    indicator_filter = f"AND indicator = '{indicator_id}'" if indicator_id else ""

    # Fetch data concurrently for geometry, indicators, and all indicators metadata
    with ThreadPoolExecutor() as executor:
        futures = {
            "geometry": executor.submit(
                query_carto,
                f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' {geo_level_filter}",
            ),
            "indicators": executor.submit(
                query_carto,
                f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' {indicator_filter} {geo_level_filter} AND indicator_version = 0",
            ),
            "all_indicators": executor.submit(fetch_indicators),
        }

        # Retrieve results and handle potential errors
        city_geometry_df = futures["geometry"].result()
        city_indicators_df = futures["indicators"].result()
        all_indicators = futures["all_indicators"].result()

    # Handle empty results
    if city_geometry_df.empty or city_indicators_df.empty:
        return None

    # Prepare the indicators data and merge with unit information
    indicators_dict = {
        indicator["fields"]["id"]: indicator["fields"] for indicator in all_indicators
    }

    indicator_columns = city_indicators_df["indicator"].unique()
    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="value"
    )
    city_indicators_df = city_indicators_df.replace([np.inf, -np.inf], np.nan)
    city_indicators_df = city_indicators_df.replace({np.nan: None})

    # Prepare the geometry data
    city_geometry_df = city_geometry_df[
        [
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "geo_version",
        ]
    ]

    for indicator_name in indicator_columns:
        unit = indicators_dict[indicator_name].get("unit", "")

        # Use apply to format each value in the column with the unit_formatter method
        city_indicators_df[indicator_name] = city_indicators_df[indicator_name].apply(
            lambda x: unit_formatter(x, unit) if pd.notna(x) else ""
        )

    # Merge geometry and indicators
    city_gdf = pd.merge(city_geometry_df, city_indicators_df, on="geo_id")

    table_data = city_gdf.to_dict(orient="records")

    # Return the final result with bounding box included
    return table_data


def get_city_stats(
    city_id: str, admin_level: Optional[str], indicator_id: Optional[str]
) -> Optional[Dict]:
    """
    Retrieve stats for an specific city, administrative level, and indicator.

    Args:
        city_id (str): The ID of the city.
        admin_level (Optional[str]): The administrative level. If not provided, the default admin level from the city's data will be used.
        indicator_id (Optional[str]): The ID of the indicator. If not provided, statistics for all indicators will be returned.

    Returns:
        Dict: A dictionary containing:
            - "indicators": A dictionary of indicator statistics, where each key is an indicator ID and the value is a dictionary containing "min" and "max" values for that indicator.
    """
    airtable_city = fetch_first_city(generate_search_query("id", city_id))
    if not airtable_city:
        return None

    admin_level = airtable_city["fields"].get(admin_level, admin_level)

    geo_level_filter = f"AND geo_level = '{admin_level}'" if admin_level else ""
    indicator_filter = f"AND indicator = '{indicator_id}'" if indicator_id else ""

    city_indicators_df = query_carto(
        f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' {indicator_filter} {geo_level_filter} AND indicator_version = 0"
    )
    if city_indicators_df.empty:
        return None

    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="value"
    )

    indicators = {
        indicator: {
            "min": (
                float(city_indicators_df[indicator].min())
                if indicator in city_indicators_df.columns
                and not np.isnan(city_indicators_df[indicator].min())
                else None
            ),
            "max": (
                float(city_indicators_df[indicator].max())
                if indicator in city_indicators_df.columns
                and not np.isnan(city_indicators_df[indicator].max())
                else None
            ),
        }
        for indicator in city_indicators_df.columns
    }

    return {"indicators": indicators}
