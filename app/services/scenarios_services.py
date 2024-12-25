import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from app.const import SCENARIOS_RESPONSE_KEYS
from app.repositories.scenarios_repository import (
    fetch_scenarios,
    fetch_first_scenario,
)
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.settings import Settings

settings = Settings()


def list_scenarios() -> List[Dict[str, Any]]:
    """
    Retrieve a list of all scenarios.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the scenarios' data.
    """

    scenarios_list = fetch_scenarios()

    # Return empty list if none found
    if not scenarios_list:
        return []

    return [
        {key: scenario["fields"].get(key) for key in SCENARIOS_RESPONSE_KEYS}
        for scenario in scenarios_list
    ]
