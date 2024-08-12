import logging
from typing import Optional

from fastapi import HTTPException
from app.const import DATASETS_LIST_RESPONSE_KEYS, datasets_table, cities_table
from app.dependencies import fetch_indicators
from app.utils.filters import generate_search_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_datasets(city_id: Optional[str]):
    filter_formula = generate_search_query("city_id", city_id)

    try:
        indicators_list = fetch_indicators()
        cities_list = cities_table.all(view="api", formula="{city_id}")
        datasets_filter_list = datasets_table.all(view="api", formula=filter_formula)
    except Exception as e:
        logger.error("An Airtable error occurred: %s", e)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving indicators failed."
        ) from e

    # Fetch cities, datasets and indicators as dictionaries for quick lookup
    cities_dict = {city["id"]: city["fields"] for city in cities_list}
    datasets_dict = {
        dataset["id"]: dataset["fields"] for dataset in datasets_filter_list
    }
    indicators_dict = {
        indicator["id"]: indicator["fields"]["indicator_label"]
        for indicator in indicators_list
    }

    # Update Indicators for each dataset
    for dataset in datasets_dict.values():
        indicator_ids = dataset.get("Indicators", [])
        cities_ids = dataset.get("city_id", [])
        dataset["Indicators"] = [
            indicators_dict.get(indicator_id, indicator_id)
            for indicator_id in indicator_ids
        ]
        dataset["city_ids"] = [
            cities_dict[city_id]["city_id"] for city_id in cities_ids
        ]

    datasets = list(datasets_dict.values())
    # Reorder and select indicators fields

    datasets = [
        {key: dataset[key] for key in DATASETS_LIST_RESPONSE_KEYS if key in dataset}
        for dataset in datasets
    ]

    return datasets
