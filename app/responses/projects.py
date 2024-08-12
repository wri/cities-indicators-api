from app.const import COMMON_500_ERROR_RESPONSE

LIST_PROJECTS_RESPONSES = {
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "projects": [
                        "urbanshift",
                        "dataforcoolcities",
                        "deepdive",
                        "cities4forests",
                    ]
                }
            }
        },
    },
    500: COMMON_500_ERROR_RESPONSE,
}
