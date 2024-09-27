import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
import csv
import io

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_400_ERROR_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.cities_schema import (
    City,
    CityBoundaryGeoJSON,
    CityIndicatorAdmin,
    CityIndicatorGeoJSON,
    CityIndicatorStats,
    CityList,
)
from app.services import cities_service
from app.utils.dependencies import validate_query_params

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(validate_query_params("projects", "country_code_iso3"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityList},
        400: COMMON_400_ERROR_RESPONSE,
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
        logger.exception("An error occurred: %s", e, exc_info=True)
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
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving all indicators for a single city and admin level failed.",
        ) from e

    if not city_indicators:
        raise HTTPException(status_code=404, detail="No indicators found")

    return city_indicators[0]


@router.get(
    "/{city_id}/indicators/geojson",
    dependencies=[Depends(validate_query_params("indicator_id", "admin_level"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityIndicatorGeoJSON},
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
def get_city_geometry_with_indicators(
    city_id: str = Path(),
    indicator_id: Optional[str] = Query(None),
    admin_level: Optional[str] = Query(None),
):
    """
    Retrieve the geometry and indicators of a specific city and administrative level in GeoJSON format.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.
    - **indicator_id** (`Optional[str]`): The unique identifier of the indicator.
    - **admin_level** (`Optional[str]`): The administrative level to filter the geometry and indicators.
        - Possible values are **"subcity_admin_level"**, **"city_admin_level"**, or any valid administrative level.
        - If no value is provided, **"subcity_admin_level"** value will be used as the default.

    ### Returns:
    - **GeoJSONFeatureCollection**: A GeoJSON feature collection representing the city's geometry and indicators.

    ### Raises:
    - **HTTPException**:
        - 400: If there is an invalid query parameter.
        - 404: If no indicators or geometry are found for the given city and administrative level.
        - 500: If an error occurs during the retrieval process.
    """
    if admin_level is None:
        admin_level = "subcity_admin_level"

    try:
        city_indicators = cities_service.get_city_geometry_with_indicators(
            city_id, admin_level, indicator_id
        )
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the indicators and geometry of the city failed.",
        ) from e

    if not city_indicators or not city_indicators["features"]:
        raise HTTPException(status_code=404, detail="No geometry found.")

    return city_indicators


@router.get(
    "/{city_id}/indicators/csv",
    dependencies=[Depends(validate_query_params("indicator_id", "admin_level"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityIndicatorGeoJSON},
        400: COMMON_400_ERROR_RESPONSE,
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No indicators found"}},
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_geometry_with_indicators_csv(
    city_id: str = Path(),
    indicator_id: Optional[str] = Query(None),
    admin_level: Optional[str] = Query(None),
):
    """
    Retrieve the geometry and indicators of a specific city and administrative level in CSV format.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.
    - **indicator_id** (`Optional[str]`): The unique identifier of the indicator to filter.
    - **admin_level** (`Optional[str]`): The administrative level to filter the geometry and indicators.
        - Possible values include **"subcity_admin_level"**, **"city_admin_level"**, or any valid administrative level.
        - If no value is provided, **"subcity_admin_level"** will be used as the default.

    ### Returns:
    - **StreamingResponse**: A streaming response containing the CSV representation of the city's geometry and indicators.

    ### Raises:
    - **HTTPException**:
        - 400: If there are invalid query parameters.
        - 404: If no indicators or geometry are found for the given city and administrative level.
        - 500: If an error occurs during the retrieval process.
    """
    if admin_level is None:
        admin_level = "subcity_admin_level"

    try:
        data = cities_service.get_city_geometry_with_indicators_csv(
            city_id, admin_level, indicator_id
        )

        if not data:
            # Raise a 404 error if no data is found
            raise HTTPException(status_code=404, detail="No geometry found.")

        # Create an in-memory stream for the CSV data
        csv_file = io.StringIO()
        fieldnames = data[0].keys()

        # Create a CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header (field names)

        # Write data rows
        for row in data:
            writer.writerow(row)

        # Move the cursor to the start of the stream
        csv_file.seek(0)

        # Create a StreamingResponse with the CSV file
        response = StreamingResponse(csv_file, media_type="text/csv")

        # Define the filename for the CSV download
        response.headers["Content-Disposition"] = (
            "attachment; filename=cities_indicators.csv"
        )

        return response

    except HTTPException as http_exc:
        # Re-raise the HTTPException to return the 404 response
        raise http_exc
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the indicators and geometry of the city failed.",
        ) from e


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
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the geometry of a single city and admin level failed.",
        ) from e

    if not city_geojson or not city_geojson["features"]:
        raise HTTPException(status_code=404, detail="No geometry found")

    return city_geojson


@router.get(
    "/{city_id}/indicators/stats",
    dependencies=[Depends(validate_query_params("indicator_id", "admin_level"))],
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": CityIndicatorStats},
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {"application/json": {"example": {"detail": "No stats found"}}},
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def get_city_stats(
    city_id: str = Path(),
    indicator_id: Optional[str] = Query(None),
    admin_level: Optional[str] = Query(None),
):
    """
    Retrieve stats for an specific city, administrative level, and indicator.

    ### Args:
    - **city_id** (`str`): The unique identifier of the city.
    - **indicator_id** (`Optional[str]`): The unique identifier of the indicator.
    - **admin_level** (`Optional[str]`): The administrative level to filter the geometry and indicators.
        - Possible values are **"subcity_admin_level"**, **"city_admin_level"**, or any valid administrative level.
        - If no value is provided, **"subcity_admin_level"** value will be used as the default.

    ### Returns:
    - **Dict**: A dictionary containing:
        - **indicators**: A dictionary of indicator statistics, where each key is an indicator ID and the value is a dictionary containing "min" and "max" values for that indicator.

    ### Raises:
    - **HTTPException**:
        - 400: If there is an invalid query parameter.
        - 404: If no stats are found for the given city and administrative level.
        - 500: If an error occurs during the retrieval process.
    """
    if admin_level is None:
        admin_level = "subcity_admin_level"

    try:
        stats = cities_service.get_city_stats(city_id, admin_level, indicator_id)
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving city stats failed.",
        ) from e

    if not stats:
        raise HTTPException(status_code=404, detail="No stats found.")

    return stats
