from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import HTTPException

from app.const import INDICATORS_LIST_RESPONSE_KEYS
from app.dependencies import fetch_datasets, fetch_indicators, fetch_projects
from app.utils.filters import generate_search_query


def list_indicators(project: str = None):
    filter_formula = generate_search_query("projects", project)

    with ThreadPoolExecutor() as executor:
        future_to_func = {
            executor.submit(fetch_datasets): "datasets",
            executor.submit(fetch_projects): "projects",
            executor.submit(fetch_indicators, filter_formula): "indicators",
        }

        results = {}
        for future in as_completed(future_to_func):
            func_name = future_to_func[future]
            try:
                result = future.result()
                results[func_name] = result
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"An error occurred: {e}"
                ) from e

    datasets_list = results["datasets"]
    projects_list = results["projects"]
    indicators_filtered_list = results["indicators"]

    # Fetch indicators and datasets as dictionaries for quick lookup
    indicators_dict = {
        indicator["id"]: indicator["fields"] for indicator in indicators_filtered_list
    }
    datasets_dict = {
        dataset["id"]: dataset["fields"]["dataset_name"] for dataset in datasets_list
    }
    projects_dict = {
        project["id"]: project["fields"]["project_id"] for project in projects_list
    }

    # Update data_sources_link for each indicator
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get("data_sources_link", [])
        indicator_projects = indicator.get("projects", [])

        # Ensure data_sources_link and projects are lists
        if not isinstance(data_sources_link, list):
            data_sources_link = [data_sources_link]
        if not isinstance(indicator_projects, list):
            indicator_projects = [indicator_projects]

        indicator["data_sources_link"] = [
            datasets_dict.get(data_source, data_source)
            for data_source in data_sources_link
        ]
        indicator["projects"] = [
            projects_dict.get(project, project) for project in indicator_projects
        ]

    indicators = list(indicators_dict.values())
    # Reorder indicators fields
    indicators = [
        {
            key: indicator[key]
            for key in INDICATORS_LIST_RESPONSE_KEYS
            if key in indicator
        }
        for indicator in indicators
    ]

    return indicators


def get_indicator(indicator_name: str):
    indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and indicators.geo_name=indicators.geo_parent_name"
    )
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    indicator_df["creation_date"] = indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    indicator = json.loads(indicator_df.to_json())
    indicator = [item["properties"] for item in indicator["features"]]
    # Reorder and select indicators fields
    desired_keys = [
        "geo_id",
        "geo_name",
        "geo_level",
        "geo_parent_name",
        "indicator",
        "value",
        "indicator_version",
    ]
    indicator = [
        {key: city_indicator[key] for key in desired_keys}
        for city_indicator in indicator
    ]

    return {"indicator_values": indicator}
