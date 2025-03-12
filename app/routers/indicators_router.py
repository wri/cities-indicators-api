import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_400_ERROR_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.indicators_schema import (
    IndicatorsResponse,
    IndicatorsThemesResponse,
    MetadataByIndicatorIdResponse,
)
from app.services import indicators_service
from app.utils.dependencies import validate_query_params

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[
        Depends(validate_query_params("project", "city_id", "application_id"))
    ],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": IndicatorsResponse},
        400: COMMON_400_ERROR_RESPONSE,
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
    application_id: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    city_id: Optional[List[str]] = Query(None),
):
    """
    Retrieve a list of indicators based on the provided project filter.

    ### Args:
    - **project** (`Optional[str]`): The unique identifier of the project to filter the
      indicators by.
    - **city_id** (`Optional[List[str]]`): A list of unique city identifiers to filter the
      indicators by.


    ### Returns:
    - **IndicatorsResponse**: A Pydantic model containing the list of indicators. The response
      includes metadata such as indicator IDs, labels, and associated projects, and themes.

    ### Raises:
    - **HTTPException**:
        - 400: If there is an invalid query parameter.
        - 404: If no indicators are found for the given filter.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        indicators_list = indicators_service.list_indicators(
            application_id, project, city_id
        )
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving list of indicators failed.",
        ) from e

    if not indicators_list:
        raise HTTPException(status_code=404, detail="No indicators found")

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

    ### Returns:
    - **IndicatorsThemesResponse**: A Pydantic model containing a set of unique indicator
      themes.

    ### Raises:
    - **HTTPException**:
        - 500: If an error occurs during the retrieval process.
    """
    try:
        themes = indicators_service.list_indicators_themes()
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of indicator themes failed.",
        ) from e

    return {"themes": themes}


@router.get(
    "/metadata/{indicator_id}",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": MetadataByIndicatorIdResponse},
        400: COMMON_400_ERROR_RESPONSE,
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
    indicator_id: str = Path(),
):
    """
    Retrieve metadata for a specific indicator.

    ### Args:
    - **indicator_id** (`str`): The unique identifier of the indicator to retrieve metadata for.

    ### Returns:
    - **MetadataByIndicatorIdResponse**: A Pydantic model containing metadata for the
      specified indicator.

    ### Raises:
    - **HTTPException**:
        - 400: If there is an invalid query parameter.
        - 404: If no metadata is found for the given indicator.
        - 500: If an error occurs during the retrieval process.
    """
    try:
        indicators_metadata_list = indicators_service.get_metadata_by_indicator_id(
            indicator_id
        )
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving metadata for the specified indicator failed.",
        ) from e

    if not indicators_metadata_list:
        raise HTTPException(status_code=404, detail="No indicators metadata found")

    return indicators_metadata_list
