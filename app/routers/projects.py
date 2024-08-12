import logging
from fastapi import APIRouter, HTTPException

from app.responses.projects import LIST_PROJECTS_RESPONSES
from app.schemas.projects import ListProjectsResponse
from app.services import projects as projects_service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", responses=LIST_PROJECTS_RESPONSES)
def list_projects() -> ListProjectsResponse:
    """
    Retrieve the list of projects.
    """
    try:
        projects_list = projects_service.list_projects()
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of projects failed.",
        ) from e

    return {"projects": projects_list}
