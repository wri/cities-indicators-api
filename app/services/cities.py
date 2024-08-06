import json
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
import pandas as pd
from app.const import CARTO_API_KEY, CARTO_USERNAME, cities_table, CITY_RESPONSE_KEYS
from app.utils.filters import generate_search_query

set_default_credentials(username=CARTO_USERNAME, api_key=CARTO_API_KEY)


def get_cities(project: str = None, country_code_iso3: str = None):
    filters = []
    if project:
        filters.append(generate_search_query("projects", project))
    if country_code_iso3:
        filters.append(f"{{country_code_iso3}} = '{country_code_iso3}'")

    filter_formula = f"AND({', '.join(filters)})" if filters else ""
    cities_list = cities_table.all(view="api", formula=filter_formula)
    cities = [
        {key: city["fields"].get(key) for key in CITY_RESPONSE_KEYS}
        for city in cities_list
    ]

    return cities


def get_city_by_city_id(city_id: str):
    formula = f'"{city_id}" = {{city_id}}'
    city_data = cities_table.all(view="api", formula=formula)

    if not city_data:
        return []

    city = city_data[0]["fields"]
    # Define the desired keys to extract from the city's data
    city_response = {key: city[key] for key in CITY_RESPONSE_KEYS if key in city}

    return city_response


def get_city_indicators(city_id: str, admin_level: str):
    city_indicators_df = read_carto(
        f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'"
    )
    # Reorder and select city geometry properties fields
    city_indicators_df = city_indicators_df[
        [
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "indicator",
            "value",
            "indicator_version",
        ]
    ]
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


def get_city_geometry(city_id: str, admin_level: str):
    city_geometry_df = read_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    )
    # Reorder and select city geometry properties fields
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


def get_city_geometry_with_indicators(city_id: str, admin_level: str):
    city_geometry_df = read_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    )
    # Reorder and select city geometry properties fields
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
