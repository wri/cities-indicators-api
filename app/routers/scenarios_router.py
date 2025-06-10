import logging

from fastapi import APIRouter, HTTPException, Path

from app.services import scenarios_service
from app.utils.utilities import cleanup_spaces_in_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{city_id}/{aoi_id}/{intervention_category}",
)
def get_scenario_by_city_id_aoi_id_intervention_category(
    city_id: str = Path(),
    aoi_id: str = Path(),
    intervention_category: str = Path(),
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
            scenarios_service.get_scenario_by_city_id_aoi_id_intervention_category(
                city_id, aoi_id, intervention_category
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

    return_dict = cleanup_spaces_in_response(scenarios_list)
    return return_dict
