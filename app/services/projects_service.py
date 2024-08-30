from typing import Dict, List

from app.repositories.projects_repository import fetch_projects
from app.utils.filters import generate_search_query


def list_projects() -> List[Dict]:
    """
    Retrieve a list of unique project IDs from the projects table.

    Returns:
        List[str]: A list containing the unique project IDs.

    """
    filter_formula = generate_search_query("status", "Active")
    projects = fetch_projects(filter_formula)
    projects_list = [
        {
            "id": project["fields"]["project_id"],
            "name": project["fields"]["project_name"][0],
        }
        for project in projects
    ]

    return projects_list
