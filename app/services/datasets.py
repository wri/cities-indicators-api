from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any, List

from app.const import DATASETS_LIST_RESPONSE_KEYS
from app.dependencies import fetch_cities, fetch_datasets, fetch_indicators
from app.utils.filters import generate_search_query


def list_datasets(city_id: Optional[str]) -> List[Dict[str, Any]]:
    filter_formula = generate_search_query("city_id", city_id)
    future_to_func = {
        fetch_cities: "cities",
        fetch_indicators: "indicators",
        lambda: fetch_datasets(filter_formula): "datasets",
    }

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for func, name in future_to_func.items()}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    # Create dictionaries for quick lookup
    cities_dict = {city["id"]: city["fields"] for city in results["cities"]}
    datasets_dict = {
        dataset["id"]: dataset["fields"] for dataset in results["datasets"]
    }
    indicators_dict = {
        indicator["id"]: indicator["fields"]["indicator_label"]
        for indicator in results["indicators"]
    }

    # Update indicators and cities for each dataset
    for dataset in datasets_dict.values():
        dataset["Indicators"] = [
            indicators_dict.get(indicator_id, indicator_id)
            for indicator_id in dataset.get("Indicators", [])
        ]
        dataset["city_ids"] = [
            cities_dict[city_id]["city_id"] for city_id in dataset.get("city_id", [])
        ]

    # Reorder and select dataset fields
    return [
        {key: dataset[key] for key in DATASETS_LIST_RESPONSE_KEYS if key in dataset}
        for dataset in datasets_dict.values()
    ]
