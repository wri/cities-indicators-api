from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from app.const import SCENARIOS_RESPONSE_KEYS
from app.repositories.cities_repository import fetch_first_city
from app.repositories.layers_repository import fetch_layers
from app.repositories.scenarios_repository import fetch_scenarios
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
            executor.submit(lambda: fetch_layers()): "layers",
            executor.submit(
                lambda: fetch_first_city(generate_search_query("id", city_id))
            ): "city",
        }

        results = {}
        for future in as_completed(futures):
            func_name = futures[future]
            results[func_name] = future.result()
    layers_dict = {layer["id"]: layer["fields"] for layer in results["layers"]}

    scenario_list = [
        {key: scenario["fields"].get(key) for key in SCENARIOS_RESPONSE_KEYS}
        for scenario in results["scenarios"]
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

    return scenario_list
