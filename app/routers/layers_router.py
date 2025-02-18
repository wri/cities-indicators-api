import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Path, Query, Depends

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.layers_schema import LayerResponse
from app.services import layers_service
from app.utils.dependencies import validate_query_params

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{layer_id}/{city_id}",
    dependencies=[Depends(validate_query_params("aoi_id"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": LayerResponse},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {"application/json": {"example": {"detail": "No layer found"}}},
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_layer(
    city_id: str = Path(), layer_id: str = Path(), aoi_id: Optional[str] = Query(None)
):
    """
    Retrieve information about a specific layer for a given city.

    This endpoint fetches details about a layer associated with a city,
    identified by their respective `city_id` and `layer_id`. The retrieved
    layer information may include file paths, styling, and other metadata
    necessary for accessing the layer's data.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city. This ID is used to
        locate the city's data within the database.
    - **layer_id** (`str`): The unique identifier of the layer. This ID corresponds
        to a specific layer associated with the city, used to retrieve
        the layer's metadata.
    - **aoi_id** (`Optional[str]`): The unique ID associated with the area of interest
        for which the layer is required.

    ### Returns:
    - **LayerResponse**: A Pydantic model containing the layer's details. If
        successful, the response will include metadata such as file paths,
        versioning, and styling.

    ### Raises:
    - **HTTPException**:
        - 404: If the layer corresponding to the provided `city_id` or
            `layer_id` is not found.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        layer = layers_service.get_city_layer(city_id, layer_id, aoi_id)
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving layer failed.",
        ) from e

    if not layer:
        raise HTTPException(status_code=404, detail="No layer found")

    return layer
