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

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(get_expected_params("project", "country_code_iso3"))],
    responses=LIST_CITIES_RESPONSES,
)
# Return all cities metadata from Airtable
def list_cities(
    project: str = Query(None, description="Project ID"),
    country_code_iso3: str = Query(None, description="ISO 3166-1 alpha-3 country code"),
):
    try:
        cities_list = cities_service.get_cities(
            project=project, country_code_iso3=country_code_iso3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not cities_list:
        raise HTTPException(status_code=404, detail="No cities found.")

    return {"cities": cities_list}


@router.get("/{city_id}", responses=GET_CITY_BY_CITY_ID_RESPONSES)
# Return one city metadata from Airtable
def get_city_by_city_id(city_id: str):
    try:
        city = cities_service.get_city_by_city_id(city_id=city_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not city:
        raise HTTPException(status_code=404, detail="No city found.")

    return city


@router.get("/{city_id}/{admin_level}", responses=GET_CITY_INDICATORS_RESPONSES)
# Return one city all indicators values from Carto
def get_city_indicators(city_id: str, admin_level: str):
    try:
        city_indicators = cities_service.get_city_indicators(
            city_id=city_id, admin_level=admin_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return {"city_indicators": city_indicators}


@router.get("/{city_id}/{admin_level}/geojson", responses=GET_CITY_GEOMETRY_RESPONSES)
# Return one city's geometry from Carto
def get_city_geometry(city_id: str, admin_level: str):
    try:
        city_geojson = cities_service.get_city_geometry(
            city_id=city_id, admin_level=admin_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return city_geojson


@router.get(
    "/{city_id}/{admin_level}/geojson/indicators",
    responses=GET_CITY_GEOMETRY_WITH_INDICATORS_RESPONSES,
)
# Return one city’s geometry and indicator values from Carto
def get_city_geometry_with_indicators(city_id: str, admin_level: str):
    try:
        city_indicators = cities_service.get_city_geometry_with_indicators(
            city_id=city_id, admin_level=admin_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return city_indicators
