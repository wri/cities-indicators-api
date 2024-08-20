import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.const import COMMON_200_SUCCESSFUL_RESPONSE, COMMON_500_ERROR_RESPONSE
from app.utils.dependencies import validate_query_params
from app.schemas.common_schema import ErrorResponse
from app.schemas.datasets_schema import DatasetsResponse
from app.services import datasets_service as datasets_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(validate_query_params("city_id"))],
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
    city_id: Optional[str] = Query(None, description="The ID of the city to filter by"),
):
    """
    Retrieve the list of datasets
    """
    try:
        datasets = datasets_service.list_datasets(city_id)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of datasets failed.",
        ) from e
    return {"datasets": datasets}
