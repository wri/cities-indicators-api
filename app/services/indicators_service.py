import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set

from app.const import INDICATORS_LIST_RESPONSE_KEYS, INDICATORS_METADATA_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_cities
from app.repositories.datasets_repository import fetch_datasets
from app.repositories.indicators_repository import (
    fetch_first_indicator,
    fetch_indicators,
)
from app.repositories.layers_repository import fetch_layers
from app.repositories.projects_repository import fetch_projects
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.settings import Settings

settings = Settings()

SPECIAL_INDICATOR_TABLES = {
    "AQ_1_airPollution": "indicators_aq_1",
    "AQ_2_exceedancedays_atleastone": "indicators_aq_2",
    "GHG_1_ghg_emissions": "indicators_ghg_1",
}


def list_indicators(
    application_id: Optional[str] = None,
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
                "id": layers_dict[layer_id]["id"],
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

    if indicators:
        for indicator in indicators:
            theme_list = indicator["fields"].get("themes")
            if theme_list:
                for theme in theme_list:
                    themes_set.add(theme)

    return themes_set


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
