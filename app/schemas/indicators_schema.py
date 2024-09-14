from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Layers(BaseModel):
    id: str
    legend: str
    name: str


class Indicator(BaseModel):
    id: str
    data_sources: str
    data_sources_link: List[str]
    data_views: List[str]
    importance: str
    definition: str
    name: str
    legend: str
    methods: str
    layers: List[Layers]
    notebook_url: HttpUrl
    projects: List[str]
    themes: List[str]
    unit: Optional[str] = None


class IndicatorsResponse(BaseModel):
    indicators: List[Indicator]


class IndicatorsThemesResponse(BaseModel):
    themes: List[str]


class IndicatorValueResponse(BaseModel):
    city_id: str
    city_name: str
    country_name: str
    country_code_iso3: str
    geo_id: str
    geo_level: str
    geo_parent_name: str
    value: float


class CityIndicatorValueResponse(IndicatorValueResponse):
    indicator: str
    indicator_version: int
    unit: str


class CitiesByIndicatorIdResponse(BaseModel):
    indicator: str
    indicator_version: Optional[int] = 0
    unit: str
    cities: List[IndicatorValueResponse]


class MetadataByIndicatorIdResponse(BaseModel):
    indicator_id: str
    indicator_definition: str
    methods: str
    importance: str
    data_sources: str
