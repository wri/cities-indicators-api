from pydantic import BaseModel
from typing import List, Optional


class Intervention(BaseModel):
    """A single intervention."""

    id: str
    name: str
    areas_id: Optional[str]
    areas_name: Optional[str]
    filter_solution_type: Optional[str]
    filter_impact_timescale: Optional[str]
    filter_solution_area: Optional[List[str]]
    card_intervention_short_description: Optional[str]
    card_intervention_long_description: Optional[str]
    card_cooling_impact_estimation: Optional[str]
    card_timescale_impact: Optional[str]
    card_investment: Optional[str]
    card_intervention_photo: Optional[str]
    cities: Optional[List[str]]
    scenarios: Optional[List[str]]


class InterventionList(BaseModel):
    """A list of interventions"""

    interventions: List[Intervention]
