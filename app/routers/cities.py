import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_expected_params
from app.responses.cities import (
    GET_CITY_BY_CITY_ID_RESPONSES,
    GET_CITY_GEOMETRY_RESPONSES,
    GET_CITY_GEOMETRY_WITH_INDICATORS_RESPONSES,
    GET_CITY_INDICATORS_RESPONSES,
    LIST_CITIES_RESPONSES,
)
from app.services import cities as cities_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(get_expected_params("projects", "country_code_iso3"))],
    responses=LIST_CITIES_RESPONSES,
)
def list_cities(
    projects: List[str] = Query(
        None,
        description="Filter by multiple Project IDs",
    ),
    country_code_iso3: Optional[str] = Query(
        None, description="Filter by ISO 3166-1 alpha-3 country code"
    ),
):
    """
    Retrieve a list of cities based on provided filter parameters.
    """
    try:
        cities_list = cities_service.get_cities(projects, country_code_iso3)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving cities failed."
        ) from e

    if not cities_list:
        raise HTTPException(status_code=404, detail="No cities found.")

    return {"cities": cities_list}


@router.get("/{city_id}", responses=GET_CITY_BY_CITY_ID_RESPONSES)
def get_city_by_city_id(city_id: str):
    """
    Retrieve a single city by its ID.
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
        raise HTTPException(status_code=404, detail="No city found.")

    return city


@router.get("/{city_id}/{admin_level}", responses=GET_CITY_INDICATORS_RESPONSES)
def get_city_indicators(city_id: str, admin_level: str):
    """
    Retrieve all indicators for a single city and admin level.
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
        raise HTTPException(status_code=404, detail="No indicators found.")

    return city_indicators


@router.get("/{city_id}/{admin_level}/geojson", responses=GET_CITY_GEOMETRY_RESPONSES)
def get_city_geometry(city_id: str, admin_level: str):
    """
    Retrieve the geometry of a single city and admin level.
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
        raise HTTPException(status_code=404, detail="No geometry found.")

    return city_geojson


@router.get(
    "/{city_id}/{admin_level}/geojson/indicators",
    responses=GET_CITY_GEOMETRY_WITH_INDICATORS_RESPONSES,
)
def get_city_geometry_with_indicators(city_id: str, admin_level: str):
    """
    Retrieve the indicators and geometry of a single city and admin level.
    """
    try:
        city_indicators = cities_service.get_city_geometry_with_indicators(
            city_id, admin_level
        )
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the indicators and geometry of a single city and admin level failed.",
        ) from e

    if not city_indicators["features"]:
        raise HTTPException(status_code=404, detail="No indicators found.")

    return city_indicators
