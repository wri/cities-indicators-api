import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from cartoframes import read_carto
from cartoframes.auth import set_default_credentials

from app.const import (CARTO_API_KEY, CARTO_USERNAME,
                       INDICATORS_LIST_RESPONSE_KEYS,
                       INDICATORS_METADATA_RESPONSE_KEYS,
                       INDICATORS_RESPONSE_KEYS, indicators_table)
from app.dependencies import fetch_datasets, fetch_indicators, fetch_projects
from app.utils.filters import generate_search_query

set_default_credentials(username=CARTO_USERNAME, api_key=CARTO_API_KEY)

def list_indicators(project: Optional[str]) -> List[Dict]:
    filter_formula = generate_search_query("projects", project)

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_datasets): "datasets",
            executor.submit(fetch_projects): "projects",
            executor.submit(fetch_indicators, filter_formula): "indicators",
        }

        results = {
            name: future.result()
            for future in as_completed(futures)
            for name, future in futures.items()
        }

    datasets_list = results["datasets"]
    projects_list = results["projects"]
    indicators_filtered_list = results["indicators"]

    def extract_dicts(data_list: List[Dict], key: str, value: str) -> Dict[str, str]:
        return {item["id"]: item["fields"][value] for item in data_list}

    indicators_dict = extract_dicts(indicators_filtered_list, "id", "fields")
    datasets_dict = extract_dicts(datasets_list, "id", "dataset_name")
    projects_dict = extract_dicts(projects_list, "id", "project_id")

    def process_indicator(indicator: Dict) -> Dict:
        data_sources_link = indicator.get("data_sources_link", [])
        indicator_projects = indicator.get("projects", [])

        if not isinstance(data_sources_link, list):
            data_sources_link = [data_sources_link]
        if not isinstance(indicator_projects, list):
            indicator_projects = [indicator_projects]

        return {
            **indicator,
            "data_sources_link": [
                datasets_dict.get(data_source, data_source)
                for data_source in data_sources_link
            ],
            "projects": [
                projects_dict.get(project, project) for project in indicator_projects
            ]
        }

    indicators = [
        {
            key: processed_indicator[key]
            for key in INDICATORS_LIST_RESPONSE_KEYS
            if key in processed_indicator
        }
        for processed_indicator in (process_indicator(ind) for ind in indicators_dict.values())
    ]

    return indicators


def list_indicators_themes():
    indicators = fetch_indicators()
    themes_set = set()

    for indicator in indicators:
        theme = indicator["fields"].get("theme")
        if theme:
            themes_set.add(theme)

    return themes_set


def get_cities_by_indicator_id(indicator_id: str):
    indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_id}' and indicators.geo_name=indicators.geo_parent_name"
    )
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    indicator_df["creation_date"] = indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    indicator = json.loads(indicator_df.to_json())
    indicator = [item["properties"] for item in indicator["features"]]
    # Reorder and select indicators fields

    indicator = [
        {key: city_indicator[key] for key in INDICATORS_RESPONSE_KEYS}
        for city_indicator in indicator
    ]

    return indicator


def get_metadata_by_indicator_id(indicator_id: str):
    filter_formula = generate_search_query("indicator_id", indicator_id)
    filtered_indicator = indicators_table.first(view="api", formula=filter_formula)

    if filtered_indicator is None:
        return []

    indicator = filtered_indicator.get("fields", {})
    # Reorder indicators fields
    return {
        key: indicator[key]
        for key in INDICATORS_METADATA_RESPONSE_KEYS
        if key in indicator
    }


def get_city_indicator_by_indicator_id_and_city_id(indicator_id: str, city_id: str):
    city_indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_id}' and geo_name = '{city_id}'"
    )
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicator_df["creation_date"] = city_indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    city_indicator = json.loads(city_indicator_df.to_json())
    city_indicator = city_indicator["features"][0]["properties"]
    # Reorder and select city indicator fields
    city_indicator = {
        key: city_indicator[key]
        for key in INDICATORS_RESPONSE_KEYS
        if key in city_indicator
    }

    return city_indicator
