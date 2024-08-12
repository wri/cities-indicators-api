from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Indicator(BaseModel):
    code: str
    data_sources: str
    data_sources_link: List[str]
    importance: str
    indicator: str
    indicator_definition: str
    indicator_label: str
    indicator_legend: str
    methods: str
    Notebook: HttpUrl
    projects: List[str]
    theme: str


class ListIndicatorsResponse(BaseModel):
    List[str]


class ListThemesResponse(BaseModel):
    themes: List[str]


class CityResponse(BaseModel):
    geo_id: str
    geo_name: str
    geo_level: str
    geo_parent_name: str
    indicator: str
    value: float
    indicator_version: Optional[int] = 0


class ListCitiesResponse(BaseModel):
    cities: List[CityResponse]


class IndicatorResponse(BaseModel):
    indicator_id: str
    indicator_definition: str
    methods: str
    importance: str
    data_sources: str
