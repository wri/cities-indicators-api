import logging

from fastapi import APIRouter, HTTPException, Path

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_400_ERROR_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.interventions_schema import InterventionList
from app.services import interventions_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": InterventionList},
        400: COMMON_400_ERROR_RESPONSE,
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_interventions():
    """
    Retrieve a list of all interventions.

    ### Returns:
    - **InterventionsListResponse**: A list of all interventions.

    ### Raises:
    - **HTTPException**:
        - 404: If no interventions are found.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        interventions_list = interventions_service.list_interventions()
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving interventions failed.",
        ) from e

    if not interventions_list:
        raise HTTPException(status_code=404, detail="No interventions found")

    return {"interventions": interventions_list}


@router.get(
    "/{city_id}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": InterventionList},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {"application/json": {"example": {"detail": "No city found"}}},
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_by_city_id(
    city_id: str = Path(),
):
    """
    Retrieve all interventions that correspond to a specific city by its ID.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.

    ### Returns:
    - **InterventionList**: A Pydantic model containing a list of interventions details.

    ### Raises:
    - **HTTPException**:
        - 404: If no intervention corresponding to the provided `city_id` is not found.
        - 500: If an error occurs during the retrieval process.
    """

    try:
        interventions_list = interventions_service.get_intervention_by_city_id(city_id)
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving interventions failed.",
        ) from e

    if not interventions_list:
        raise HTTPException(status_code=404, detail="No interventions found")

    return {"interventions": interventions_list}
