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
class CityIndicatorsDetail(BaseModel):
    model_config = ConfigDict(extra='allow')

    geo_id: str
    geo_name: str
    geo_level: str
    geo_parent_name: str


# Geometry Schema
class Geometry(BaseModel):
    type: str
    coordinates: List[List[List[List[float]]]]


# Feature Schema
class GeoFeature(BaseModel):
    id: str
    type: str
    properties: CityIndicatorsDetail
    geometry: Geometry


# GeoJSON Response
class GeoJSONFeatureCollection(BaseModel):
    type: str
    features: List[GeoFeature]
