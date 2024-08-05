from pydantic import BaseModel
from typing import List

# Response for listing projects
class ListProjectsResponse(BaseModel):
    projects: List[str]
