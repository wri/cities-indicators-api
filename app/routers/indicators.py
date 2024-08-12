from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_expected_params
from app.responses.indicators import (
    GET_CITIES_BY_INDICATOR_ID_RESPONSES,
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
