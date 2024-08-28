from pydantic import BaseModel, ConfigDict
from typing import List, Optional


# City Schema
class CityDetail(BaseModel):
    city_id: str
    city_name: str
    country_name: str
    country_code_iso3: str
    admin_levels: Optional[List[str]]
    aoi_boundary_level: Optional[str]
    projects: List[str]


# Response for listing cities
class CityListResponse(BaseModel):
    cities: List[CityDetail]


# Indicator Schema
class CityIndicatorsDetailBase(BaseModel):
    model_config = ConfigDict(extra="allow")
    bbox: List[float]
    city_name: str
    geo_id: str
    geo_level: str
    geo_parent_name: str


class CityIndicatorsDetail(CityIndicatorsDetailBase):
    bbox: List[float]
    geo_version: int
    indicator: str
    indicator_name: str
    indicator_unit: str
    value: float


# Geometry Schema
class Geometry(BaseModel):
    type: str
    coordinates: List[List[List[List[float]]]]


# Feature Schema with detailed indicators
class CityIndicatorFeature(BaseModel):
    id: str
    type: str
    properties: CityIndicatorsDetail
    geometry: Geometry


# GeoJSON Response with detailed indicators
class CityIndicatorGeoJSON(BaseModel):
    type: str
    features: List[CityIndicatorFeature]


# Feature Schema with basic city information
class CityBoundaryFeature(BaseModel):
    id: str
    type: str
    properties: CityIndicatorsDetailBase
    geometry: Geometry


# GeoJSON Response with basic city information
class CityBoundaryGeoJSON(BaseModel):
    type: str
    features: List[CityBoundaryFeature]
