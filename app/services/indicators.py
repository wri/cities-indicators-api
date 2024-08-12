import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from cartoframes import read_carto
from cartoframes.auth import set_default_credentials

from app.const import (CARTO_API_KEY, CARTO_USERNAME,
                       INDICATORS_LIST_RESPONSE_KEYS,
                       INDICATORS_METADATA_RESPONSE_KEYS,
                       INDICATORS_RESPONSE_KEYS, indicators_table)
from app.dependencies import fetch_datasets, fetch_indicators, fetch_projects
from app.utils.filters import generate_search_query

set_default_credentials(username=CARTO_USERNAME, api_key=CARTO_API_KEY)


def list_indicators(project: Optional[str]):
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

    # Fetch indicators and datasets as dictionaries for quick lookup
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

    # Update data_sources_link for each indicator
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get("data_sources_link", [])
        indicator_projects = indicator.get("projects", [])
        indicator["data_sources_link"] = [
            datasets_dict.get(data_source, data_source)
            for data_source in data_sources_link
        ]
        indicator["projects"] = [
            projects_dict.get(project, project) for project in indicator_projects
        ]

    indicators = list(indicators_dict.values())

    indicators = [
        {
            key: indicator[key]
            for key in INDICATORS_LIST_RESPONSE_KEYS
            if key in indicator
        }
        for indicator in indicators
    ]

    return indicators


def list_indicators_themes():
    indicators = fetch_indicators()
    themes_set = set()

    for indicator in indicators:
        theme_list = indicator["fields"].get("theme")
        for theme in theme_list:
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
