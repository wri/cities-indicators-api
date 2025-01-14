from pydantic import BaseModel
from typing import List, Optional


class Scenario(BaseModel):
    """A single scenario."""

    id: str
    name: Optional[str]
    description: Optional[str]
    layers: Optional[List[str]]
    cities: Optional[List[str]]
    interventions: Optional[List[str]]


class ScenarioList(BaseModel):
    """A list of scenarios"""

    scenarios: List[Scenario]
