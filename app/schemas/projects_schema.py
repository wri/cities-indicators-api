from pydantic import BaseModel
from typing import List


class ListProjectsResponse(BaseModel):
    projects: List[str]
