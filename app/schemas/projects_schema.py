from pydantic import BaseModel
from typing import List


class Project(BaseModel):
    id: str
    name: str


class ListProjectsResponse(BaseModel):
    projects: List[Project]
