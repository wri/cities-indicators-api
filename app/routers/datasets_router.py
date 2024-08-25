import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.const import COMMON_200_SUCCESSFUL_RESPONSE, COMMON_500_ERROR_RESPONSE
from app.utils.dependencies import validate_query_params
from app.schemas.common_schema import ErrorResponse
from app.schemas.datasets_schema import DatasetsResponse
from app.services import datasets_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(validate_query_params("city_id", "layer_id"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": DatasetsResponse},
        400: {
            "model": ErrorResponse,
            "description": "Invalid query parameter",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid query parameter: <query_parameter>"}
                }
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_datasets(
    city_id: Optional[str] = Query(None),
    layer_id: Optional[List[str]] = Query(None),
):
    """
    Retrieve a list of datasets, optionally filtered by a specific city and/or layer.

    This endpoint fetches a list of datasets, with options to filter the results by
    a specific city's ID and/or one or more layer IDs.

    ### Args:
    - **city_id** (`Optional[str]`): The unique identifier of the city to filter the datasets by.
    - **layer_id** (`Optional[List[str]]`): A list of unique layer identifiers to filter the datasets by.

    ### Returns:
    - **DatasetsResponse**: A Pydantic model containing the list of datasets. The response
        will include metadata such as dataset IDs, names, and associated cities.

    ### Raises:
    - **HTTPException**:
        - 400: If there is an invalid query parameter.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        datasets = datasets_service.list_datasets(city_id, layer_id)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of datasets failed.",
        ) from e

    return {"datasets": datasets}
