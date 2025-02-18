import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set

from cartoframes.auth import set_default_credentials

from app.const import (
    CITY_INDICATORS_RESPONSE_KEYS,
    INDICATORS_LIST_RESPONSE_KEYS,
    INDICATORS_METADATA_RESPONSE_KEYS,
    INDICATORS_RESPONSE_KEYS,
)
from app.repositories.cities_repository import fetch_cities
from app.repositories.datasets_repository import fetch_datasets
from app.repositories.indicators_repository import (
    fetch_first_indicator,
    fetch_indicators,
)
from app.repositories.layers_repository import fetch_layers
from app.repositories.projects_repository import fetch_projects
from app.utils.carto import query_carto
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.settings import Settings

settings = Settings()

set_default_credentials(
    username=settings.carto_username, api_key=settings.carto_api_key
)

SPECIAL_INDICATOR_TABLES = {
    "AQ_1_airPollution": "indicators_aq_1",
    "AQ_2_exceedancedays_atleastone": "indicators_aq_2",
    "GHG_1_ghg_emissions": "indicators_ghg_1",
}


def list_indicators(
    application_id: str,
    project: Optional[str] = None,
    city_id: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Retrieve a list of indicators, optionally filtered by project.

    Args:
        city_id (Optional[List[str]]): A list of city IDs to filter indicators by.
            If None, indicators from all cities are retrieved.
        project (Optional[str]): The project ID to filter indicators by.

    Returns:
        List[Dict]: A list of indicators with selected fields.

    """
    # Create filters
    indicators_filters = {}
    project_filter = {"application_id": application_id}
    projects = fetch_projects(construct_filter_formula(project_filter))
    projects_dict = {}
    if projects:
        projects_dict = {project["id"]: project["fields"]["id"] for project in projects}
        indicators_filters["projects"] = [
            project["fields"]["id"] for project in projects
        ]
    if city_id:
        indicators_filters["cities"] = city_id
    indicators_filter_formula = construct_filter_formula(indicators_filters)

    # Fetch all necessary data in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_cities): "cities",
            executor.submit(fetch_datasets): "datasets",
            executor.submit(fetch_layers): "layers",
            executor.submit(fetch_indicators, indicators_filter_formula): "indicators",
        }

        results = {}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    # Create dictionaries for quick lookup
    cities_dict = {city["id"]: city["fields"]["id"] for city in results["cities"]}
    indicators_dict = {
        indicator["id"]: indicator["fields"] for indicator in results["indicators"]
    }
    datasets_dict = {
        dataset["id"]: dataset["fields"]["name"] for dataset in results["datasets"]
    }

    layers_dict = {layer["id"]: layer["fields"] for layer in results["layers"]}

    # Format the output
    indicators = []
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get("data_sources_link", [])
        indicator["data_sources_link"] = [
            datasets_dict.get(data_source, data_source)
            for data_source in data_sources_link
        ]
        indicator["projects"] = [
            projects_dict.get(project)
            for project in indicator.get("projects", [])
            if project in projects_dict
        ]
        indicator["layers"] = [
            {
                "id": layer_id,
                "legend": layers_dict[layer_id].get("layer_legend", ""),
                "name": layers_dict[layer_id]["layer_name"],
            }
            for layer_id in indicator.get("layers", [])
            if isinstance(indicator.get("layers"), list)
            and layer_id in layers_dict.keys()
        ]
        indicator["city_ids"] = [
            cities_dict[city_id]
            for city_id in cities_dict.keys()
            if city_id in indicator.get("cities", [])
        ]
        indicators.append(
            {
                key: (
                    json.loads(indicator[key])
                    if key.endswith("styling")
                    else indicator[key]
                )
                for key in INDICATORS_LIST_RESPONSE_KEYS
                if key in indicator
            }
        )

    return indicators


def list_indicators_themes() -> Set[str]:
    """
    Retrieve a unique set of themes from all indicators.

    Returns:
        Set[str]: A set of unique themes.
    """
    indicators = fetch_indicators()
    themes_set = set()

    for indicator in indicators:
        theme_list = indicator["fields"].get("themes")
        for theme in theme_list:
            themes_set.add(theme)

    return themes_set


def get_cities_by_indicator_id(indicator_id: str) -> List[Dict]:
    """
    Retrieve a list of cities associated with a specific indicator.

    Args:
        indicator_id (str): The ID of the indicator to filter cities by.

    Returns:
        List[Dict]: A list of city indicators with selected fields.
    """
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_cities): "cities",
            executor.submit(fetch_indicators): "indicators",
            executor.submit(
                query_carto,
                f"SELECT *, geo_name as city_id FROM indicators WHERE indicator = '{indicator_id}' "
                f"AND indicators.geo_name=indicators.geo_parent_name",
            ): "indicator_df",
        }

        results = {}
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()

    indicator_df = results.get("indicator_df")

    if indicator_df.empty:
        return []

    cities_dict = {city["fields"]["id"]: city["fields"] for city in results["cities"]}
    indicators_dict = {
        indicator["fields"]["id"]: indicator["fields"]
        for indicator in results["indicators"]
    }
    indicator_df["creation_date"] = indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    city_indicators = [
        {
            **item["properties"],
            "city_name": cities_dict.get(item["properties"]["city_id"], {}).get("name"),
            "country_name": cities_dict.get(item["properties"]["city_id"], {}).get(
                "country_name"
            ),
            "country_code_iso3": cities_dict.get(item["properties"]["city_id"], {}).get(
                "country_code_iso3"
            ),
        }
        for item in json.loads(indicator_df.to_json())["features"]
        if item["properties"]["city_id"] in cities_dict
    ]
    return {
        "indicator": city_indicators[0]["indicator"],
        "indicator_version": city_indicators[0]["indicator_version"],
        "unit": indicators_dict[indicator_id].get("unit", None),
        "cities": [
            {
                key: city_indicator[key]
                for key in INDICATORS_RESPONSE_KEYS
                if key in city_indicator
            }
            for city_indicator in city_indicators
        ],
    }


def get_metadata_by_indicator_id(indicator_id: str) -> Dict:
    """
    Retrieve metadata for a specific indicator.

    Args:
        indicator_id (str): The ID of the indicator to retrieve metadata for.

    Returns:
        Dict: A dictionary containing metadata for the specified indicator.

    """
    filter_formula = generate_search_query("id", indicator_id)
    filtered_indicator = fetch_first_indicator(filter_formula)

    if not filtered_indicator:
        return {}

    indicator = filtered_indicator.get("fields", {})

    return {
        key: indicator[key]
        for key in INDICATORS_METADATA_RESPONSE_KEYS
        if key in indicator
    }


def _calculate_total_reduction_percent(city_indicator):
    """Calculates the total reduction percentage for special indicators."""
    year_sums = {}
    for feature in city_indicator["features"]:
        year = feature["properties"]["year"]
        value = feature["properties"]["value"]
        year_sums[year] = year_sums.get(year, 0) + value

    min_year = min(year_sums.keys())
    max_year = max(year_sums.keys())
    sum_min_year = year_sums[max_year]
    sum_max_year = year_sums[min_year]

    return (
        ((sum_min_year - sum_max_year) / sum_min_year) * 100 if sum_min_year != 0 else 0
    )


def _fetch_and_process_data(indicator_id: str, city_id: str):
    """Fetches and pre-processes data for both normal and special indicators."""
    table_name = SPECIAL_INDICATOR_TABLES.get(indicator_id)
    query = (
        f"SELECT * FROM {table_name} WHERE geo_name = '{city_id}'"
        if table_name
        else f"SELECT *, geo_name as city_id FROM indicators WHERE indicator = '{indicator_id}' AND geo_name = '{city_id}'"
    )

    with ThreadPoolExecutor() as executor:
        fetch_cities_future = executor.submit(fetch_cities)
        fetch_indicators_future = executor.submit(fetch_indicators)
        query_carto_future = executor.submit(query_carto, query)

        all_cities = fetch_cities_future.result()
        all_indicators = fetch_indicators_future.result()
        city_indicator_df = query_carto_future.result()

    return city_indicator_df, all_cities, all_indicators


def _format_indicator_data(
    city_indicator_df, all_cities, all_indicators, indicator_id, city_id, table_name
):
    """Formats the indicator data based on its type."""
    if city_indicator_df.empty:
        return {}

    cities_dict = {city["fields"]["id"]: city["fields"] for city in all_cities}
    indicators_dict = {
        indicator["fields"]["id"]: indicator["fields"] for indicator in all_indicators
    }

    if not table_name:
        city_indicator_df["creation_date"] = city_indicator_df[
            "creation_date"
        ].dt.strftime("%Y-%m-%d")
    else:
        city_indicator_df["city_id"] = cities_dict[city_id]["id"]
        city_indicator_df["indicator"] = indicator_id

    special_indicator_value = None
    if table_name == "indicators_aq_2":
        special_indicator_value = int(city_indicator_df["fine_particulate_matter"][0])

    city_indicator_df["unit"] = indicators_dict[indicator_id].get("unit", "").strip()
    city_indicator_df["city_name"] = cities_dict[city_id]["name"]
    city_indicator_df["country_name"] = cities_dict[city_id]["country_name"]
    city_indicator_df["country_code_iso3"] = cities_dict[city_id]["country_code_iso3"]

    city_indicator = json.loads(city_indicator_df.to_json())
    if table_name in ["indicators_aq_1", "indicators_ghg_1"]:
        special_indicator_value = _calculate_total_reduction_percent(city_indicator)

    city_indicator = city_indicator["features"][0]["properties"]

    response = {
        key: city_indicator.get(key)
        for key in CITY_INDICATORS_RESPONSE_KEYS
        if key in city_indicator
    }

    if special_indicator_value is not None:
        response["value"] = special_indicator_value

    return response


def get_city_indicator_by_indicator_id_and_city_id(
    indicator_id: str, city_id: str
) -> Dict:
    """
    Retrieve indicator data for a specific city and indicator.

    Args:
        indicator_id (str): The ID of the indicator to filter by.
        city_id (str): The ID of the city to filter by.

    Returns:
        Dict: A dictionary containing the indicator data for the specified city.
    """

    (
        city_indicator_df,
        all_cities,
        all_indicators,
    ) = _fetch_and_process_data(indicator_id, city_id)

    table_name = SPECIAL_INDICATOR_TABLES.get(indicator_id)
    return _format_indicator_data(
        city_indicator_df,
        all_cities,
        all_indicators,
        indicator_id,
        city_id,
        table_name,
    )
