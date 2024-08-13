from typing import List

from app.dependencies import fetch_projects


def list_projects() -> List[str]:
    """
    Retrieve a list of unique project IDs from the projects table.

    Returns:
        List[str]: A list containing the unique project IDs.

    """
    projects = fetch_projects()
    projects_dict = {project["fields"]["project_id"] for project in projects}

    return projects_dict
