from app.const import COMMON_500_ERROR_RESPONSE
from app.schemas.projects import ListProjectsResponse

LIST_PROJECTS_RESPONSES={
    200: {
        "model": ListProjectsResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "projects": [
                        "urbanshift",
                        "dataforcoolcities",
                        "deepdive",
                        "cities4forests"
                    ]
                }
            }
        }
    },
    500: COMMON_500_ERROR_RESPONSE
}
