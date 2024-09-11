from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Indicator(BaseModel):
    data_sources: str
    data_sources_link: List[str]
    importance: str
    indicator_id: str
    indicator_definition: str
    indicator_label: str
    indicator_legend: str
    methods: str
    layers: List[str]
    Notebook: HttpUrl
    projects: List[str]
    theme: List[str]
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
