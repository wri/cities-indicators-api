from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from app.const import INTERVENTIONS_RESPONSE_KEYS
from app.repositories.interventions_repository import (
    fetch_interventions,
)
from app.repositories.scenarios_repository import fetch_scenarios
from app.repositories.cities_repository import fetch_cities
from app.utils.settings import Settings

settings = Settings()


def list_interventions() -> List[Dict[str, Any]]:
    """
    Retrieve a list of all interventios.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the interventions' data.
    """

    # Fetch all necessary data in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_scenarios): "scenarios",
            executor.submit(fetch_interventions): "interventions",
            executor.submit(fetch_cities): "cities",
        }

        results = {}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    scenarios_dict = {
        scenario["id"]: scenario["fields"]["id"] for scenario in results["scenarios"]
    }
    interventions_dict = {
        intervention["id"]: intervention["fields"]
        for intervention in results["interventions"]
    }
    cities_dict = {city["id"]: city["fields"]["id"] for city in results["cities"]}
    interventions = []
    for intervention in interventions_dict.values():
        intervention["cities"] = [
            cities_dict[city_id]
            for city_id in cities_dict.keys()
            if city_id in intervention.get("cities", [])
        ]
        intervention["scenarios"] = [
            scenarios_dict[scenario_id]
            for scenario_id in scenarios_dict.keys()
            if scenario_id in intervention.get("scenarios", [])
        ]
        interventions.append(
            {
                key: intervention[key]
                for key in INTERVENTIONS_RESPONSE_KEYS
                if key in intervention
            }
        )
    return interventions


def get_intervention_by_city_id(city_id: str) -> Optional[Dict]:
    """
    Retrieve intervention data for a specific city ID.

    Args:
        city_id (str): The ID of the city to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of interventions for the specified city_id.
    """

    # Fetch all necessary data in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_scenarios): "scenarios",
            executor.submit(fetch_interventions): "interventions",
            executor.submit(fetch_cities): "cities",
        }

        results = {}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()

    scenarios_dict = {
        scenario["id"]: scenario["fields"]["id"] for scenario in results["scenarios"]
    }
    interventions_dict = {
        intervention["id"]: intervention["fields"]
        for intervention in results["interventions"]
    }
    cities_dict = {city["id"]: city["fields"]["id"] for city in results["cities"]}
    interventions = []
    for intervention in interventions_dict.values():
        intervention["cities"] = [
            cities_dict[city_id]
            for city_id in cities_dict.keys()
            if city_id in intervention.get("cities", [])
        ]

        # Continue to the next intervention if the requested city_id is not present in this intervention
        if city_id not in intervention["cities"]:
            continue

        intervention["scenarios"] = [
            scenarios_dict[scenario_id]
            for scenario_id in scenarios_dict.keys()
            if scenario_id in intervention.get("scenarios", [])
        ]
        interventions.append(
            {
                key: intervention[key]
                for key in INTERVENTIONS_RESPONSE_KEYS
                if key in intervention
            }
        )
    return interventions
