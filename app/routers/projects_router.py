import logging
from fastapi import APIRouter, HTTPException

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.common_schema import ErrorResponse
from app.services import projects_service
from app.schemas.projects_schema import ListProjectsResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": ListProjectsResponse},
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
                "application/json": {"example": {"detail": "No projects found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_projects():
    """
    Retrieve the list of projects.

    ### Returns:
    - ListProjectsResponse: A Pydantic model containing the list of projects. The response 
      includes metadata such as project IDs, names, and descriptions.

    ### Raises:
    - HTTPException:
        - 404: If no projects are found (handled by the service layer, should be rare).
        - 500: If an error occurs during the retrieval process.
    """
    try:
        projects_list = projects_service.list_projects()
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of projects failed.",
        ) from e

    if not projects_list:
        raise HTTPException(status_code=404, detail="No projects found")

    return {"projects": projects_list}
