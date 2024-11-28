import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.repositories.cities_repository import fetch_first_city
from app.repositories.layers_repository import fetch_first_layer
from app.utils.filters import generate_search_query


def get_city_layer(city_id: str, layer_id: str):
    """
    Retrieve layer and city information, then construct a URL path
    for the layer file stored on S3.

    Args:
    - city_id (str): The unique identifier of the city.
    - layer_id (str): The unique identifier of the layer.

    Returns:
        - Dict[str, str]: A dictionary containing:
            - "city_id": The city ID.
            - "layer_id": The layer ID.
            - "layer_url": The full URL path to the layer file on S3.
            - "file_type": The file type of the layer.
            - "styling": The styling parameters associated with the layer, if available, as a JSON object.
    """
    layer_filter = generate_search_query("id", layer_id)
    city_filter = generate_search_query("id", city_id)

    tasks = {
        "layer": lambda: fetch_first_layer(layer_filter),
        "city": lambda: fetch_first_city(city_filter),
    }

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(func): name for name, func in tasks.items()}
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    # Extract necessary fields from the results
    if not results["layer"] or not results["city"]:
        return None

    layer_fields = results["layer"]["fields"]
    city_fields = results["city"]["fields"]

    # Construct the S3 file path
    s3_base_url = "https://cities-indicators.s3.amazonaws.com/"
    s3_path = layer_fields["layer_url"].replace("s3://cities-indicators/", "")
    layer_url = (
        f"{s3_base_url}{s3_path}{city_id}-"
        f"{city_fields['city_admin_level']}-"
        f"{layer_fields['layer_file_name']}"
        f"{'-' + layer_fields['version'] if 'version' in layer_fields else ''}"
        f".{layer_fields['file_type']}"
    )
    try:
        map_styling = json.loads(layer_fields["map_styling"])
        legend_styling = json.loads(layer_fields.get("legend_styling", "{}"))
    except json.JSONDecodeError:
        map_styling = {}
        legend_styling = {}
    return_dict = {
        "city_id": city_id,
        "layer_id": layer_id,
        "layer_url": layer_url,
        "class_name": layer_fields["cif_class_name"],
        "file_type": layer_fields["file_type"],
        "map_styling": map_styling,
        "legend_styling": legend_styling,
    }
    if layer_fields["layer_type"] == "vector":
        return_dict["pmtiles_layer_url"] = f"{os.path.splitext(layer_url)[0]}.pmtiles"
    return return_dict
