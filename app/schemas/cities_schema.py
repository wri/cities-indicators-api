from pydantic import BaseModel, ConfigDict
from typing import List, Optional


# City Schema
class City(BaseModel):  # More concise and clear
    """A single city."""

    city_id: str
    admin_levels: Optional[List[str]]
    aoi_boundary_level: Optional[str]
    city_name: str
    country_name: str
    country_code_iso3: str
    latitude: float
    longitude: float
    projects: List[str]


# Response for listing cities
class CityList(BaseModel):  # Removed "Response" for brevity
    """List of cities."""

    cities: List[City]


# Indicator Schema
class CityIndicatorBase(BaseModel):  # "Base" indicates it's a foundational schema
    """Basic city information for indicators."""

    bbox: List[float]
    geo_id: str
    geo_name: str
    geo_level: str
    geo_parent_name: str
    geo_version: int


class CityIndicatorAdmin(BaseModel):  # More descriptive and concise
    """City indicator details for a specific admin level."""

    city_name: str
    geo_id: str
    geo_level: str
    geo_parent_name: str
    indicator_version: int
    model_config = ConfigDict(extra="allow")


class CityIndicator(CityIndicatorBase):  # Clearer inheritance
    """Detailed city information for indicators."""

    indicator: str
    indicator_label: str
    indicator_unit: str
    value: float


# Geometry Schema
class Geometry(BaseModel):  # No change needed
    """GeoJSON geometry."""

    type: str
    coordinates: List[List[List[List[float]]]]


# Feature Schema with detailed indicators
class CityIndicatorFeature(BaseModel):  # No change needed
    """A GeoJSON feature with detailed city indicator information."""

    id: str
    type: str
    properties: CityIndicator
    geometry: Geometry


# GeoJSON Response with detailed indicators
class CityIndicatorGeoJSON(BaseModel):  # No change needed
    """A GeoJSON response with detailed city indicator information."""

    bbox: List[float]
    max: Optional[float]
    min: Optional[float]
    type: str
    features: List[CityIndicatorFeature]


# Feature Schema with basic city information
class CityBoundaryFeature(BaseModel):  # No change needed
    """A GeoJSON feature with basic city information."""

    id: str
    type: str
    properties: CityIndicatorBase
    geometry: Geometry


# GeoJSON Response with basic city information
class CityBoundaryGeoJSON(BaseModel):  # No change needed
    """A GeoJSON response with basic city information."""

    bbox: List[float]
    type: str
    features: List[CityBoundaryFeature]
