from fastapi import APIRouter, HTTPException, Query

from app.responses.projects import LIST_PROJECTS_RESPONSES
from app.services import projects as projects_service

router = APIRouter()

@router.get("", responses=LIST_PROJECTS_RESPONSES)
# Return all cities metadata from Airtable
def list_projects():
    try:
        projects_list = projects_service.list_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return {"projects": projects_list}