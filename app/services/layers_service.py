import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
from urllib.parse import urljoin

from app.repositories.cities_repository import fetch_first_city
from app.repositories.layers_repository import fetch_first_layer
from app.utils.filters import construct_filter_formula, generate_search_query
from app.utils.settings import Settings

settings = Settings()


def generate_layer_response(
    city_id: str,
    aoi_id: str | None,
    layer_fields: dict,
    city_fields: dict,
):

    s3_path = layer_fields.get("s3_path", "")
    s3_path = s3_path.replace("/prd/", f"/{settings.env}/")
    if aoi_id:
        layer_file_name = (
            f"{city_id}__{aoi_id}__"
            f"{layer_fields.get('layer_file_name')}__"
            f"{layer_fields['version'] if 'version' in layer_fields else ''}"
            f".{layer_fields.get('file_type')}"
        )
    else:
        layer_file_name = (
            f"{city_id}__"
            f"{city_fields.get('city_admin_level')}__"
            f"{layer_fields.get('layer_file_name')}__"
            f"{layer_fields['version'] if 'version' in layer_fields else ''}"
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
        "datasets_id": layer_fields.get("datasets_id"),
        "file_type": layer_fields.get("file_type"),
        "source_layer_id": layer_fields.get("source_layer_id"),
        "layers_group_mask": layer_fields.get("layers_group_mask"),
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


def get_city_layer(
    city_id: str,
    layer_id: str,
    aoi_id: Union[str, None] = None,
    year: Union[str, None] = None,
):
    """
    Retrieve layer and city information, then construct a URL path
    for the layer file stored on S3.

    Args:
    - city_id (str): The unique identifier of the city.
    - layer_id (str): The unique identifier of the layer.
    - aoi_id (str, optional): The unique identifier for the area of interest
    - year (str, optional): The version of the layer corresponding to the year specified

    Returns:
        - Dict[str, str]: A dictionary containing:
            - "city_id": The city ID.
            - "layer_id": The layer ID.
            - "layer_url": The full URL path to the layer file on S3.
            - "file_type": The file type of the layer.
            - "styling": The styling parameters associated with the layer, if available, as a JSON object.
    """
    layer_filters = {"id": layer_id}
    if year:
        layer_filters["version"] = year
    layers_filter_formula = construct_filter_formula(layer_filters)
    city_filter = generate_search_query("id", city_id)

    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(lambda: fetch_first_layer(layers_filter_formula)): "layer",
            executor.submit(lambda: fetch_first_city(city_filter)): "city",
        }
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
