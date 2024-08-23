from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any, List

from app.const import DATASETS_LIST_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_cities
from app.repositories.datasets_repository import fetch_datasets
from app.repositories.indicators_repository import fetch_indicators
from app.repositories.layers_repository import fetch_layers
from app.utils.filters import construct_filter_formula, generate_search_query


def list_datasets(city_id: Optional[str], layer_id: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Retrieve a list of datasets, optionally filtered by city ID and/or layer IDs.

    This function fetches datasets from various sources, filters them based on the provided 
    city ID and/or layer IDs, and enriches the datasets with additional information like 
    indicators and city details.

    Args:
        city_id (Optional[str]): The unique identifier of the city to filter datasets by. 
            If None, datasets from all cities are retrieved.
        layer_id (Optional[List[str]]): A list of unique layer identifiers to filter datasets by. 
            If None, datasets from all layers are retrieved.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the filtered datasets, 
            each enriched with selected fields like indicators, city IDs, and layers.
    """
    filters = {}

    if layer_id:
        filters["Layers"] = layer_id
    if city_id:
        filters["city_id"] = city_id

    formula = construct_filter_formula(filters)
    
    future_to_func = {
        fetch_layers: "layers",
        fetch_cities: "cities",
        fetch_indicators: "indicators",
        lambda: fetch_datasets(filter_formula=formula): "datasets",
    }

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for func, name in future_to_func.items()}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    # Create dictionaries for quick lookup
    layers_dict = {layer["id"]: layer["fields"] for layer in results["layers"]}
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
        dataset["Layers"] = [
            layers_dict[layer_id]["layer_id"]
            for layer_id in dataset.get("Layers", [])
            if layer_id in layers_dict and "layer_id" in layers_dict[layer_id]
        ]

    # Reorder and select dataset fields
    return [
        {key: dataset[key] for key in DATASETS_LIST_RESPONSE_KEYS if key in dataset}
        for dataset in datasets_dict.values()
    ]
