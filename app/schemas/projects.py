from pydantic import BaseModel
from typing import List


class ListProjectsResponse(BaseModel):
    projects: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": {
                "projects": [
                    "urbanshift",
                    "dataforcoolcities",
                    "deepdive",
                    "cities4forests",
                ]
            }
        }
    }
