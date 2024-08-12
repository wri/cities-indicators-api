from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_expected_params
from app.responses.indicators import (
    GET_CITIES_BY_INDICATOR_ID_RESPONSES,
    GET_INDICATOR_BY_INDICATOR_ID_CITY_ID_RESPONSES,
    GET_METADATA_BY_INDICATOR_ID_RESPONSES,
    LIST_INDICATORS_RESPONSES,
    LIST_INDICATORS_THEMES_RESPONSES,
)
from app.services import indicators as indicators_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(get_expected_params("project"))],
    responses=LIST_INDICATORS_RESPONSES,
)
def list_indicators(project: Optional[str] = Query(None, description="Project ID")):
    """
    Retrieve a list of indicators.
    """
    try:
        indicators_list = indicators_service.list_indicators(project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not indicators_list:
        raise HTTPException(status_code=404, detail="No indicators found.")

    return {"indicators": indicators_list}


@router.get(
    "/themes",
    responses=LIST_INDICATORS_THEMES_RESPONSES,
)
def list_indicators_themes():
    """
    Retrieve the list of indicators themes.
    """
    try:
        themes = indicators_service.list_indicators_themes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return {"themes": themes}


@router.get(
    "/{indicator_id}",
    responses=GET_CITIES_BY_INDICATOR_ID_RESPONSES,
)
def get_cities_by_indicator_id(indicator_id: str):
    """
    Retrieve all the cities indicators specified by indicator_id.
    """
    try:
        indicators_list = indicators_service.get_cities_by_indicator_id(indicator_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not indicators_list:
        raise HTTPException(status_code=404, detail="No cities found.")

    return {"cities": indicators_list}


@router.get(
    "/metadata/{indicator_id}",
    responses=GET_METADATA_BY_INDICATOR_ID_RESPONSES,
)
def get_metadata_by_indicator_id(indicator_id: str):
    """
    Retrieve all metadata for a single indicator by indicator_id.
    """
    try:
        indicators_metadata_list = indicators_service.get_metadata_by_indicator_id(
            indicator_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not indicators_metadata_list:
        raise HTTPException(status_code=404, detail="No indicators metadata found.")

    return indicators_metadata_list


@router.get(
    "/{indicator_id}/{city_id}",
    responses=GET_INDICATOR_BY_INDICATOR_ID_CITY_ID_RESPONSES,
)
def get_city_indicator_by_indicator_id_and_city_id(indicator_id: str, city_id: str):
    """
    Retrieve a single city indicator specified by indicator_id and city_id.
    """
    try:
        indicator = indicators_service.get_city_indicator_by_indicator_id_and_city_id(
            indicator_id, city_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not indicator:
        raise HTTPException(status_code=404, detail="No indicator found.")

    return indicator
