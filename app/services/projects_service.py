from typing import Dict, List

from app.repositories.projects_repository import fetch_projects
from app.utils.filters import generate_search_query


def list_projects(application_id) -> List[Dict]:
    """
    Retrieve a list of unique project IDs from the projects table.

    Returns:
        List[str]: A list containing the unique project IDs.

    """
    filter_formula = (
        generate_search_query("application_id", application_id.value)
        if application_id
        else {}
    )
    projects = fetch_projects(filter_formula)
    projects_list = [
        {
            "id": project["fields"]["id"],
            "name": project["fields"].get("name", [""])[0],
        }
        for project in projects
    ]

    return projects_list
