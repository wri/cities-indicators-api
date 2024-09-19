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


def list_indicators(
    project: Optional[str] = None, city_id: Optional[List[str]] = None
) -> List[Dict]:
    """
    Retrieve a list of indicators, optionally filtered by project.

    Args:
        project (Optional[str]): The project ID to filter indicators by.

    Returns:
        List[Dict]: A list of indicators with selected fields.

    """
    # Create filters
    indicators_filters = {}

    if project:
        indicators_filters["projects"] = project
    if city_id:
        indicators_filters["Cities 3"] = city_id

    indicators_filter_formula = construct_filter_formula(indicators_filters)

    # Fetch all necessary data in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_cities): "cities",
            executor.submit(fetch_projects): "projects",
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
    projects_dict = {
        project["id"]: project["fields"]["id"] for project in results["projects"]
    }
    layers_dict = {
        layer["fields"]["id"]: layer["fields"] for layer in results["layers"]
    }

    # Format the output
    indicators = []
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get("data_sources_link", [])
        indicator["data_sources_link"] = [
            datasets_dict.get(data_source, data_source)
            for data_source in data_sources_link
        ]
        indicator["projects"] = [
            projects_dict.get(project, project)
            for project in indicator.get("projects", [])
        ]
        indicator["layers"] = [
            {
                "id": layer_id,
                "legend": layers_dict[layer_id].get("layer_legend", ""),
                "name": layers_dict[layer_id]["layer_name"],
            }
            for layer_id in indicator.get("layer_id", [])
            if isinstance(indicator.get("layer_id"), list)
            and layer_id in layers_dict.keys()
        ]
        indicator["city_ids"] = [
            cities_dict[city_id]
            for city_id in cities_dict.keys()
            if city_id in indicator.get("Cities 3", [])
        ]
        indicators.append(
            {
                key: indicator[key]
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
        "unit": indicators_dict[indicator_id]["unit"],
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
    with ThreadPoolExecutor() as executor:
        # Run fetch_indicators and query_carto in parallel
        fetch_cities_future = executor.submit(fetch_cities)
        fetch_indicators_future = executor.submit(fetch_indicators)
        query_carto_future = executor.submit(
            query_carto,
            f"SELECT *, geo_name as city_id FROM indicators WHERE indicator = '{indicator_id}' "
            f"AND geo_name = '{city_id}'",
        )

        # Get results
        all_cities = fetch_cities_future.result()
        all_indicators = fetch_indicators_future.result()
        city_indicator_df = query_carto_future.result()

    if city_indicator_df.empty:
        return {}

    cities_dict = {city["fields"]["id"]: city["fields"] for city in all_cities}
    indicators_dict = {
        indicator["fields"]["id"]: indicator["fields"] for indicator in all_indicators
    }

    city_indicator_df["creation_date"] = city_indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    city_indicator_df["unit"] = indicators_dict[indicator_id]["unit"]
    city_indicator_df["city_name"] = cities_dict[city_id]["name"]
    city_indicator_df["country_name"] = cities_dict[city_id]["country_name"]
    city_indicator_df["country_code_iso3"] = cities_dict[city_id]["country_code_iso3"]
    city_indicator = json.loads(city_indicator_df.to_json())
    city_indicator = city_indicator["features"][0]["properties"]

    return {
        key: city_indicator[key]
        for key in CITY_INDICATORS_RESPONSE_KEYS
        if key in city_indicator
    }
