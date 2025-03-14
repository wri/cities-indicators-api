from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from app.const import SCENARIOS_INDICATOR_VALUES_RESPONSE_KEYS, SCENARIOS_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_first_city
from app.repositories.indicators_repository import fetch_indicators
from app.repositories.layers_repository import fetch_layers
from app.repositories.scenarios_repository import (
    fetch_indicator_values,
    fetch_scenarios,
)
from app.services import layers_service
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.settings import Settings

settings = Settings()


def get_scenario_by_city_id_aoi_id_intervention_id(
    city_id: str, aoi_id: str, intervention_id: str
) -> List:
    """
    Retrieve scenario data for a specific city ID.

    Args:
        city_id (str): The ID of the city to retrieve.
        aoi_id (str): The ID of the aoi to retrieve.
        intervention_id (str): The ID of the intervention to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of interventions for the specified city_id.
    """
    filters = {}

    if city_id:
        filters["cities"] = city_id
    if intervention_id and aoi_id:
        filters["Interventions"] = f"{intervention_id}__{city_id}__{aoi_id}"
    # Fetch all necessary data in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                lambda: fetch_scenarios(construct_filter_formula(filters))
            ): "scenarios",
            executor.submit(
                lambda: fetch_indicator_values(
                    construct_filter_formula({"cities": city_id} if city_id else {})
                )
            ): "indicator_values",
            executor.submit(
                lambda: fetch_indicators(
                    construct_filter_formula({"cities": city_id} if city_id else {})
                )
            ): "indicators",
            executor.submit(fetch_layers): "layers",
            executor.submit(
                lambda: fetch_first_city(generate_search_query("id", city_id))
            ): "city",
        }

        results = {}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()
    _layers_dict = {
        layer["id"]: layer["fields"]["layer_file_name"] for layer in results["layers"]
    }
    layers_dict = {layer["id"]: layer["fields"] for layer in results["layers"]}

    scenario_list = [
        {key: scenario["fields"].get(key) for key in SCENARIOS_RESPONSE_KEYS}
        for scenario in results["scenarios"]
    ]
    indicators_dict = {
        indicator["id"]: indicator["fields"].get("name")
        for indicator in results["indicators"]
    }
    scenario_indicator_dict = {}

    for indicator in results["indicator_values"]:
        data = indicator["fields"]
        name = (
            indicators_dict.get(data["indicators"][0], "")
            if isinstance(data["indicators"], list) and len(data["indicators"]) > 0
            else ""
        )
        scenario = data["scenarios_ids"]
        if scenario:
            scenario_id = scenario[0]
            if scenario_id in scenario_indicator_dict:
                existing_list = scenario_indicator_dict[scenario_id]
                if existing_list:
                    existing_list.append(
                        {
                            key: name if key == "name" else data.get(key)
                            for key in SCENARIOS_INDICATOR_VALUES_RESPONSE_KEYS
                        }
                    )
                    scenario_indicator_dict[scenario_id] = existing_list
            else:
                scenario_indicator_dict[scenario_id] = [
                    {
                        key: (name if key == "name" else data.get(key))
                        for key in SCENARIOS_INDICATOR_VALUES_RESPONSE_KEYS
                    }
                ]

    for scenario in scenario_list:
        layers = []
        for layer_id in scenario["layers"]:
            layer_fields = layers_dict.get(layer_id)
            if layer_fields:
                layers.append(
                    layers_service.generate_layer_response(
                        city_id=city_id,
                        aoi_id=aoi_id,
                        layer_fields=layer_fields,
                        city_fields=results["city"]["fields"],
                    )
                )
        scenario["layers"] = layers
        if scenario["id"] in scenario_indicator_dict:
            scenario["indicators"] = scenario_indicator_dict[scenario["id"]]
        else:
            scenario["indicators"] = []

    return scenario_list
