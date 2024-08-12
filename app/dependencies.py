from typing import Optional
from fastapi import HTTPException, Request

from app.const import datasets_table, indicators_table, projects_table, cities_table


def fetch_cities(filter_formula: Optional[str] = None):
    return cities_table.all(view="api", formula=filter_formula)


def fetch_datasets(filter_formula: Optional[str] = None):
    return datasets_table.all(view="api", formula=filter_formula)


def fetch_projects(filter_formula: Optional[str] = None):
    return projects_table.all(view="api", formula=filter_formula)


def fetch_indicators(filter_formula: Optional[str] = None):
    return indicators_table.all(view="api", formula=filter_formula)


def validate_query_params(request: Request, expected_params: list[str]):
    query_params = request.query_params
    for param in query_params:
        if param not in expected_params:
            raise HTTPException(
                status_code=400, detail=f"Invalid query parameter: {param}"
            )


def get_expected_params(*params: str):
    def dependency(request: Request):
        validate_query_params(request, params)

    return dependency
