import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_400_ERROR_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.cities_schema import City, CityList
from app.schemas.common_schema import ApplicationIdParam
from app.services import cities_service
from app.utils.dependencies import validate_query_params

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[
        Depends(
            validate_query_params("projects", "country_code_iso3", "application_id")
        )
    ],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityList},
        400: COMMON_400_ERROR_RESPONSE,
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_cities(
    application_id: ApplicationIdParam = Query(None),
    projects: Optional[List[str]] = Query(None),
    country_code_iso3: Optional[str] = Query(None),
):
    """
    Retrieve a list of cities filtered by project IDs and/or country code.

    ### Args:
    - **application_id** (`Optional[str]`): A WRI cities application ID used to filter the cities.
    - **projects** (`Optional[List[str]]`): A list of Project IDs used to filter the cities.
    - **country_code_iso3** (`Optional[str]`): An ISO 3166-1 alpha-3 country code used to filter the cities.

    ### Returns:
    - **CityListResponse**: A list of cities that match the provided filters.

    ### Raises:
    - **HTTPException**:
        - 404: If no cities are found for the given filters.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        cities_list = cities_service.list_cities(
            application_id, projects, country_code_iso3
        )
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving cities failed."
        ) from e

    if not cities_list:
        raise HTTPException(status_code=404, detail="No cities found")

    return {"cities": cities_list}


@router.get(
    "/{city_id}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": City},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {"application/json": {"example": {"detail": "No city found"}}},
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_by_city_id(
    application_id: ApplicationIdParam = Query(None),
    city_id: str = Path(),
):
    """
    Retrieve information about a specific city by its ID.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.

    ### Returns:
    - **CityDetail**: A Pydantic model containing the city's details.

    ### Raises:
    - **HTTPException**:
        - 404: If the city corresponding to the provided `city_id` is not found.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        city = cities_service.get_city_by_city_id(application_id, city_id)
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving city by city_id failed.",
        ) from e

    if not city:
        raise HTTPException(status_code=404, detail="No city found")

    return city
