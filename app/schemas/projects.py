from pydantic import BaseModel
from typing import List, Optional, Union

# Response for listing projects
class ListProjectsResponse(BaseModel):
    projects: List[str]