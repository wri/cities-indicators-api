import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)

from app.utils.dependencies import validate_query_params
from app.schemas.common_schema import ErrorResponse
from app.schemas.cities_schema import (
    CityBoundaryGeoJSON,
    City,
    CityIndicatorAdmin,
    CityIndicatorGeoJSON,
    CityList,
)
from app.services import cities_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(validate_query_params("projects", "country_code_iso3"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityList},
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
def list_cities(
    projects: Optional[List[str]] = Query(None),
    country_code_iso3: Optional[str] = Query(None),
):
    """
    Retrieve a list of cities filtered by project IDs and/or country code.

    ### Args:
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
        cities_list = cities_service.list_cities(projects, country_code_iso3)
    except Exception as e:
        logger.error("An error occurred: %s", e)
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
        city = cities_service.get_city_by_city_id(city_id)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving city by city_id failed.",
        ) from e

    if not city:
        raise HTTPException(status_code=404, detail="No city found")

    return city


@router.get(
    "/{city_id}/{admin_level}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityIndicatorAdmin},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No indicators found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_indicators(
    city_id: str = Path(),
    admin_level: str = Path(),
):
    """
    Retrieve all indicators for a specific city and administrative level.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.
    - **admin_level** (`str`): The administrative level to filter the indicators by.

    ### Returns:
    - **CityIndicatorsDetail**: A Pydantic model containing the city's indicators details.

    ### Raises:
    - **HTTPException**:
        - 404: If no indicators are found for the given city and administrative level.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        city_indicators = cities_service.get_city_indicators(city_id, admin_level)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving all indicators for a single city and admin level failed.",
        ) from e

    if not city_indicators:
        raise HTTPException(status_code=404, detail="No indicators found")

    return city_indicators[0]


@router.get(
    "/{city_id}/{admin_level}/geojson",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityBoundaryGeoJSON},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No geometry found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_geometry(
    city_id: str = Path(),
    admin_level: str = Path(),
):
    """
    Retrieve the geometry of a specific city and administrative level in GeoJSON format.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.
    - **admin_level** (`str`): The administrative level to filter the geometry by.

    ### Returns:
    - **GeoJSONFeatureCollection**: A GeoJSON feature collection representing the city's geometry.

    ### Raises:
    - **HTTPException**:
        - 404: If no geometry is found for the given city and administrative level.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        city_geojson = cities_service.get_city_geometry(city_id, admin_level)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the geometry of a single city and admin level failed.",
        ) from e

    if not city_geojson["features"]:
        raise HTTPException(status_code=404, detail="No geometry found")

    return city_geojson


@router.get(
    "/{city_id}/indicators/{indicator_id}/geojson",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityIndicatorGeoJSON},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No indicators found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_geometry_with_indicators(
    city_id: str = Path(),
    indicator_id: str = Path(),
    admin_level: Optional[str] = Query(None),
):
    """
    Retrieve the geometry and indicators of a specific city and administrative level in GeoJSON format.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.
    - **indicator_id** (`str`): The unique identifier of the indicator.
    - **admin_level** (`Optional[str]`): The administrative level to filter the geometry and indicators by, if provided.

    ### Returns:
    - **GeoJSONFeatureCollection**: A GeoJSON feature collection representing the city's geometry and indicators.

    ### Raises:
    - **HTTPException**:
        - 404: If no indicators or geometry are found for the given city and administrative level.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        city_indicators = cities_service.get_city_geometry_with_indicators(
            city_id, indicator_id, admin_level
        )
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the indicators and geometry of the city failed.",
        ) from e

    if not city_indicators["features"]:
        raise HTTPException(status_code=404, detail="No geometry found.")

    return city_indicators
