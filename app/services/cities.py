import json
from typing import Dict, List, Optional

import pandas as pd
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials

from app.const import (
    CARTO_API_KEY,
    CARTO_USERNAME,
    CITY_RESPONSE_KEYS,
    INDICATORS_RESPONSE_KEYS,
)
from app.dependencies import fetch_cities
from app.utils.filters import construct_filter_formula

set_default_credentials(username=CARTO_USERNAME, api_key=CARTO_API_KEY)


def get_cities(
    project: Optional[List[str]], country_code_iso3: Optional[str]
) -> List[dict]:
    """
    Retrieve a list of cities based on the provided filters.

    Args:
        project (Optional[List[str]]): List of Project IDs to filter by.
        country_code_iso3 (Optional[str]): ISO 3166-1 alpha-3 country code to filter by.

    Returns:
        List[dict]: A list of dictionaries containing the filtered cities' data.
    """
    filters = {}

    if project:
        filters["project"] = project
    if country_code_iso3:
        filters["country_code_iso3"] = country_code_iso3

    filter_formula = construct_filter_formula(filters)
    cities_list = fetch_cities(filter_formula)

    if not cities_list:
        return []

    cities = [
        {key: city["fields"].get(key) for key in CITY_RESPONSE_KEYS}
        for city in cities_list
    ]

    return cities


def get_city_by_city_id(city_id: str) -> Dict:
    """
    Retrieve city data for a specific city ID.

    Args:
        city_id (str): The ID of the city to retrieve.

    Returns:
        dict: A dictionary containing the city's data based on CITY_RESPONSE_KEYS.
    """
    filter_formula = f'"{city_id}" = {{city_id}}'
    city_data = fetch_cities(filter_formula)

    if not city_data:
        return []

    city = city_data[0]["fields"]
    city_response = {key: city[key] for key in CITY_RESPONSE_KEYS if key in city}

    return city_response


def get_city_indicators(city_id: str, admin_level: str) -> List[dict]:
    """
    Retrieve indicators for a specific city and administrative level.

    Args:
        city_id (str): The ID of the city to retrieve indicators for.
        admin_level (str): The administrative level to filter by.

    Returns:
        List[dict]: A list of dictionaries containing the city's indicators.
    """
    city_indicators_df = read_carto(
        f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'"
    )
    city_indicators_df = city_indicators_df[INDICATORS_RESPONSE_KEYS]
    city_indicators_df = city_indicators_df.pivot(
        index=[
            "geo_id",
            "geo_name",
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


def get_city_geometry(city_id: str, admin_level: str) -> Dict:
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
    )
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

    city_indicators_df = read_carto(
        f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}' and indicator_version=0"
    )
    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="value"
    )

    city_geojson = json.loads(city_geometry_df.to_json())

    return city_geojson


def get_city_geometry_with_indicators(city_id: str, admin_level: str) -> Dict:
    """
    Retrieve the geometry and indicators of a specific city and administrative level.

    Args:
        city_id (str): The ID of the city to retrieve geometry and indicators for.
        admin_level (str): The administrative level to filter by.

    Returns:
        dict: A GeoJSON dictionary representing the city's geometry along with its indicators.
    """
    city_geometry_df = read_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    )
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

    city_indicators_df = read_carto(
        f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}' and indicator_version=0"
    )
    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="value"
    )

    city_gdf = pd.merge(city_geometry_df, city_indicators_df, on="geo_id")

    city_geojson = json.loads(city_gdf.to_json())

    return city_geojson
