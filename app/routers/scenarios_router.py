import logging

from fastapi import APIRouter, HTTPException, Path

from app.schemas.common_schema import ApplicationIdParam
from app.services import scenarios_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{city_id}/{aoi_id}/{intervention_id}",
)
def get_scenario_by_city_id_aoi_id_intervention_id(
    application_id: ApplicationIdParam = Path(),
    city_id: str = Path(),
    aoi_id: str = Path(),
    intervention_id: str = Path(),
):
    """
    Retrieve all scenarios that correspond to a specific city by its ID.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.

    ### Returns:
    - **ScenarioList**: A Pydantic model containing a list of scenarios details.

    ### Raises:
    - **HTTPException**:
        - 404: If no intervention corresponding to the provided `city_id` is not found.
        - 500: If an error occurs during the retrieval process.
    """

    try:
        scenarios_list = (
            scenarios_service.get_scenario_by_city_id_aoi_id_intervention_id(
                city_id, aoi_id, intervention_id
            )
        )
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving scenarios failed.",
        ) from e

    if not scenarios_list:
        raise HTTPException(status_code=404, detail="No scenarios found")

    return scenarios_list
