from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional


class City(BaseModel):
    """A single city."""

    id: str
    admin_levels: Optional[List[str]]
    city_admin_level: Optional[str]
    name: str
    country_name: str
    country_code_iso3: str
    latitude: float
    longitude: float
    projects: List[str]


class CityList(BaseModel):
    """List of cities."""

    cities: List[City]


class CityIndicatorBase(BaseModel):
    """Basic city information for indicators."""

    bbox: List[float]
    geo_id: str
    geo_name: str
    geo_level: str
    geo_parent_name: str
    geo_version: int


class CityIndicatorAdmin(BaseModel):
    """City indicator details for a specific admin level."""

    name: str
    geo_id: str
    geo_level: str
    geo_parent_name: str
    indicator_version: int
    model_config = ConfigDict(extra="allow")


class CityIndicator(CityIndicatorBase):
    """Detailed city information for indicators."""

    indicator: str
    indicator_label: str
    indicator_unit: str
    value: float


class Geometry(BaseModel):
    """GeoJSON geometry."""

    type: str
    coordinates: List[List[List[List[float]]]]


class CityIndicatorFeature(BaseModel):
    """A GeoJSON feature with detailed city indicator information."""

    id: str
    type: str
    properties: CityIndicator
    geometry: Geometry


class MinMaxIndicators(BaseModel):
    """Minimum and maximum values of each indicator for a city."""

    max: float
    min: float


class CityIndicatorStats(BaseModel):
    """Stats about an specific city."""

    indicators: Dict[str, MinMaxIndicators]


class CityIndicatorGeoJSON(BaseModel):
    """A GeoJSON response with detailed city indicator information."""

    bbox: List[float]
    type: str
    features: List[CityIndicatorFeature]


class CityBoundaryFeature(BaseModel):
    """A GeoJSON feature with basic city information."""

    id: str
    type: str
    properties: CityIndicatorBase
    geometry: Geometry


class CityBoundaryGeoJSON(BaseModel):
    """A GeoJSON response with basic city information."""

    bbox: List[float]
    type: str
    features: List[CityBoundaryFeature]
