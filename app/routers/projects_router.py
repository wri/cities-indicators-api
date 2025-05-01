import logging

from fastapi import APIRouter, HTTPException, Query

from app.const import (
    COMMON_200_SUCCESSFUL_RESPONSE,
    COMMON_400_ERROR_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.common_schema import ApplicationIdParam
from app.schemas.projects_schema import ListProjectsResponse
from app.services import projects_service
from app.utils.utilities import cleanup_spaces_in_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    responses={
        200: {**COMMON_200_SUCCESSFUL_RESPONSE, "model": ListProjectsResponse},
        400: COMMON_400_ERROR_RESPONSE,
        404: {
            **COMMON_404_ERROR_RESPONSE,
            "content": {
                "application/json": {"example": {"detail": "No projects found"}}
            },
        },
        500: COMMON_500_ERROR_RESPONSE,
    },
)
def list_projects(
    application_id: ApplicationIdParam = Query(None),
):
    """
    Retrieve the list of projects.

    ### Returns:
    - **ListProjectsResponse**: A Pydantic model containing the list of projects. The response
      includes metadata such as project IDs, names, and descriptions.

    ### Raises:
    - **HTTPException**:
        - 404: If no projects are found (handled by the service layer, should be rare).
        - 500: If an error occurs during the retrieval process.
    """
    try:
        projects_list = projects_service.list_projects(application_id)
    except Exception as e:
        logger.exception("An error occurred: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of projects failed.",
        ) from e

    if not projects_list:
        raise HTTPException(status_code=404, detail="No projects found")

    return_dict = cleanup_spaces_in_response({"projects": projects_list})
    return return_dict
