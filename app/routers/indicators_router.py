import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.utils.dependencies import validate_query_params
from app.schemas.common_schema import ErrorResponse
from app.schemas.indicators_schema import (
    IndicatorValueResponse,
    IndicatorsThemesResponse,
    IndicatorsResponse,
    MetadataByIndicatorIdResponse,
    CitiesByIndicatorIdResponse,
)
from app.services import indicators_service as indicators_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(validate_query_params("project"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": IndicatorsResponse},
        400: {
            "model": ErrorResponse,
            "description": "Invalid query parameter",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid query parameter: <query_parameter>"}
                }
            },
        },
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No indicators found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_indicators(
    project: Optional[str] = Query(
        None, description="The project ID to filter indicators by"
    ),
):
    """
    Retrieve a list of indicators based on the provided project filter.
    """
    try:
        indicators_list = indicators_service.list_indicators(project)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving list of indicators failed.",
        ) from e

    if not indicators_list:
        raise HTTPException(status_code=404, detail="No indicators found.")

    return {"indicators": indicators_list}


@router.get(
    "/themes",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": IndicatorsThemesResponse},
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_indicators_themes():
    """
    Retrieve a set of unique themes from all indicators.
    """
    try:
        themes = indicators_service.list_indicators_themes()
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of indicators themes failed.",
        ) from e

    return {"themes": themes}


@router.get(
    "/{indicator_id}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CitiesByIndicatorIdResponse},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {"application/json": {"example": {"detail": "No cities found"}}},
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_cities_by_indicator_id(
    indicator_id: str = Path(description="The ID of the indicator to filter cities by"),
):
    """
    Retrieve a list of cities associated with a specific indicator.
    """
    try:
        indicators_list = indicators_service.get_cities_by_indicator_id(indicator_id)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving all the cities indicators specified by indicator_id failed.",
        ) from e

    if not indicators_list:
        raise HTTPException(status_code=404, detail="No cities found.")

    return {"cities": indicators_list}


@router.get(
    "/metadata/{indicator_id}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": MetadataByIndicatorIdResponse},
        400: {
            "model": ErrorResponse,
            "description": "Invalid query parameter",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid query parameter: <query_parameter>"}
                }
            },
        },
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No indicators found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_metadata_by_indicator_id(
    indicator_id: str = Path(
        description="The ID of the indicator to retrieve metadata for"
    ),
):
    """
    Retrieve metadata for a specific indicator.
    """
    try:
        indicators_metadata_list = indicators_service.get_metadata_by_indicator_id(
            indicator_id
        )
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving all metadata for a single indicator by indicator_id failed.",
        ) from e

    if not indicators_metadata_list:
        raise HTTPException(status_code=404, detail="No indicators metadata found.")

    return indicators_metadata_list


@router.get(
    "/{indicator_id}/{city_id}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": IndicatorValueResponse},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No indicator found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_indicator_by_indicator_id_and_city_id(
    indicator_id: str = Path(description="The ID of the indicator to filter by"),
    city_id: str = Path(description="The ID of the city to filter by"),
):
    """
    Retrieve indicator data for a specific city and indicator.
    """
    try:
        indicator = indicators_service.get_city_indicator_by_indicator_id_and_city_id(
            indicator_id, city_id
        )
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving a single city indicator specified by indicator_id and city_id failed.",
        ) from e

    if not indicator:
        raise HTTPException(status_code=404, detail="No indicator found.")

    return indicator
