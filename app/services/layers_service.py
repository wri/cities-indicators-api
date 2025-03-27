import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
from urllib.parse import urljoin

from app.repositories.cities_repository import fetch_first_city
from app.repositories.layers_repository import fetch_first_layer
from app.utils.filters import generate_search_query


def generate_layer_response(
    city_id: str, aoi_id: str | None, layer_fields: dict, city_fields: dict
):

    s3_path = layer_fields.get("s3_path", "")
    if aoi_id:
        layer_file_name = (
            f"{city_id}__{aoi_id}__"
            f"{layer_fields.get('layer_file_name')}__"
            f"{layer_fields['version'] if 'version' in layer_fields else ''}"
            f".{layer_fields.get('file_type')}"
        )
    else:
        layer_file_name = (
            f"{city_id}-"
            f"{city_fields.get('city_admin_level')}-"
            f"{layer_fields.get('layer_file_name')}"
            f"{'-' + layer_fields['version'] if 'version' in layer_fields else ''}"
            f".{layer_fields.get('file_type')}"
        )

    try:
        map_styling = json.loads(layer_fields.get("map_styling", "{}"))
        legend_styling = json.loads(layer_fields.get("legend_styling", "{}"))
    except json.JSONDecodeError:
        map_styling = {}
        legend_styling = {}
    return_dict = {
        "city_id": city_id,
        "layer_id": layer_fields.get("id"),
        "class_name": layer_fields.get("cif_class_name"),
        "file_type": layer_fields.get("file_type"),
        "source_layer_id": layer_fields.get("source_layer_id"),
        "map_styling": map_styling,
        "legend_styling": legend_styling,
    }
    if layer_fields.get("layer_type") == "vector":
        geojson_sub_url = urljoin(s3_path, "geojson/")
        geojson_layer_url = urljoin(geojson_sub_url, layer_file_name)
        pmtiles_sub_url = urljoin(s3_path, "pmtiles/")
        pmtiles_layer_url = (
            f"{os.path.splitext(urljoin(pmtiles_sub_url, layer_file_name))[0]}.pmtiles"
        )
        return_dict["layers_url"] = {
            "geojson": geojson_layer_url,
            "pmtiles": pmtiles_layer_url,
        }
    else:
        cog_sub_url = urljoin(s3_path, "cog/")
        cog_layer_url = urljoin(cog_sub_url, layer_file_name)
        return_dict["layers_url"] = {"cog": cog_layer_url}

    return return_dict


def get_city_layer(city_id: str, layer_id: str, aoi_id: Union[str, None] = None):
    """
    Retrieve layer and city information, then construct a URL path
    for the layer file stored on S3.

    Args:
    - city_id (str): The unique identifier of the city.
    - layer_id (str): The unique identifier of the layer.
    - aoi_id (str, optional): The unique identifier for the area of interest

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
    return generate_layer_response(
        city_id=city_id,
        aoi_id=aoi_id,
        layer_fields=layer_fields,
        city_fields=city_fields,
    )
