from typing import Optional
from app.const import projects_table


def fetch_projects(filter_formula: Optional[str] = None):
    return projects_table.all(view="api", formula=filter_formula)
