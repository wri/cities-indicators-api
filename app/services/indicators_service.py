import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Set

from cartoframes import read_carto
from cartoframes.auth import set_default_credentials

from app.const import (
    CARTO_API_KEY,
    CARTO_USERNAME,
    INDICATORS_LIST_RESPONSE_KEYS,
    INDICATORS_METADATA_RESPONSE_KEYS,
    INDICATORS_RESPONSE_KEYS,
)
from app.repositories.datasets_repository import fetch_datasets
from app.repositories.projects_repository import fetch_projects
from app.repositories.indicators_repository import fetch_indicators, fetch_first_indicator
from app.utils.filters import generate_search_query

set_default_credentials(username=CARTO_USERNAME, api_key=CARTO_API_KEY)


def list_indicators(project: Optional[str] = None) -> List[Dict]:
    """
    Retrieve a list of indicators, optionally filtered by project.

    Args:
        project (Optional[str]): The project ID to filter indicators by.

    Returns:
        List[Dict]: A list of indicators with selected fields.

    Raises:
        Exception: If there is an error fetching data from the underlying sources.
    """
    filter_formula = generate_search_query("projects", project)
    future_to_func = {
        fetch_projects: "projects",
        fetch_datasets: "datasets",
        lambda: fetch_indicators(filter_formula): "indicators",
    }

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for func, name in future_to_func.items()}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    indicators_dict = {
        indicator["id"]: indicator["fields"] for indicator in results["indicators"]
    }
    datasets_dict = {
        dataset["id"]: dataset["fields"]["dataset_name"]
        for dataset in results["datasets"]
    }
    projects_dict = {
        project["id"]: project["fields"]["project_id"]
        for project in results["projects"]
    }

    indicators = []
    # Update data_sources_link and projects for each indicator
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get("data_sources_link", [])
        indicator["data_sources_link"] = [
            datasets_dict.get(data_source, data_source)
            for data_source in data_sources_link
        ]
        indicator_projects = indicator.get("projects", [])
        indicator["projects"] = [
            projects_dict.get(project, project) for project in indicator_projects
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
        theme_list = indicator["fields"].get("theme")
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
    query = (
        f"SELECT * FROM indicators WHERE indicator = '{indicator_id}' "
        f"AND indicators.geo_name=indicators.geo_parent_name"
    )
    indicator_df = read_carto(query)
    if indicator_df.empty:
        return []

    indicator_df["creation_date"] = indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    indicators = json.loads(indicator_df.to_json())
    indicators = [item["properties"] for item in indicators["features"]]

    return [
        {
            key: city_indicator[key]
            for key in INDICATORS_RESPONSE_KEYS
            if key in city_indicator
        }
        for city_indicator in indicators
    ]


def get_metadata_by_indicator_id(indicator_id: str) -> Dict:
    """
    Retrieve metadata for a specific indicator.

    Args:
        indicator_id (str): The ID of the indicator to retrieve metadata for.

    Returns:
        Dict: A dictionary containing metadata for the specified indicator.

    Raises:
        Exception: If the indicator is not found.
    """
    filter_formula = generate_search_query("indicator_id", indicator_id)
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

    Raises:
        Exception: If the city indicator is not found.
    """
    query = (
        f"SELECT * FROM indicators WHERE indicator = '{indicator_id}' "
        f"AND geo_name = '{city_id}'"
    )
    city_indicator_df = read_carto(query)
    if city_indicator_df.empty:
        return {}

    city_indicator_df["creation_date"] = city_indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    city_indicator = json.loads(city_indicator_df.to_json())
    city_indicator = city_indicator["features"][0]["properties"]

    return {
        key: city_indicator[key]
        for key in INDICATORS_RESPONSE_KEYS
        if key in city_indicator
    }
