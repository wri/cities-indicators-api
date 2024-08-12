from pydantic import BaseModel
from typing import List, Optional, Union


# City Schema
class CityResponse(BaseModel):
    city_id: str
    city_name: str
    country_name: str
    country_code_iso3: str
    admin_levels: List[str]
    aoi_boundary_level: str
    project: List[str]


# Response for listing cities
class ListCitiesResponse(BaseModel):
    cities: List[CityResponse]


# Indicator Schema
class CityIndicatorsResponse(BaseModel):
    geo_id: str
    geo_name: str
    geo_level: str
    geo_parent_name: str
    indicator_version: int
    ACC_1_OpenSpaceHectaresper1000people2022: Optional[float]
    ACC_2_percentOpenSpaceinBuiltup2022: Optional[float]
    ACC_3_percentPopwOpenSpaceAccess2022: Optional[float]
    ACC_4_percentPopwTreeCoverAccess2022: Optional[float]
    AQ_3_percentWHOlimitPM25exposure2020: Optional[float]
    BIO_1_percentNaturalArea: Optional[float]
    BIO_2_habitat_connectivity: Optional[float]
    BIO_3_percentBirdsinBuiltupAreas: Optional[Union[float, int]]
    BIO_4_numberPlantSpecies: Optional[Union[float, int]]
    BIO_5_numberBirdSpecies: Optional[Union[float, int]]
    BIO_6_numberArthropodSpecies: Optional[Union[float, int]]
    FLD_1_percentFloodProneinBuiltup2050: Optional[float]
    FLD_2_percentChangeinMaxDailyPrecip2020to2050: Optional[float]
    FLD_3_percentBuiltupWithin1mAboveDrainage: Optional[float]
    FLD_4_percentImperviousinBuiltup2018: Optional[float]
    FLD_5_percentBuiltupWOvegetationcover2020: Optional[float]
    FLD_6_percentRiparianZonewoVegorWatercover2020: Optional[float]
    FLD_7_percentSteepSlopesWOvegetationcover2020: Optional[float]
    GHG_2_meanannualTreeCarbonFluxMgcO2eperHA: Optional[float]
    HEA_1_percentChangeinDaysAbove35C2020to2050: Optional[float]
    HEA_2_percentBuiltupwHighLST_2013to2022meanofmonthwhottestday: Optional[float]
    HEA_3_percentBuiltwLowAlbedo: Optional[float]
    HEA_4_percentBuiltupWithoutTreeCover: Optional[float]
    LND_1_percentPermeableSurface: Optional[float]
    LND_2_percentTreeCover: Optional[float]
    LND_3_percentChangeinVegetation_WaterCover2019_2022: Optional[float]
    LND_4_percentof2000HabitatAreaRestoredby2020: Optional[float]
    LND_5_numberofHabitatTypesRestoredby2020: Optional[float]
    LND_6_percentProtectedArea: Optional[float]
    LND_7_percentKBAsProtected: Optional[float]
    LND_8_percentKBAsBuiltup: Optional[float]

# Geometry Schema
class GeometryResponse(BaseModel):
    type: str
    coordinates: List[List[List[List[float]]]]


# Feature Schema
class FeatureResponse(BaseModel):
    id: str
    type: str
    properties: CityIndicatorsResponse
    geometry: GeometryResponse


# GeoJSON Response
class GeoJSONResponse(BaseModel):
    type: str
    features: List[FeatureResponse]
