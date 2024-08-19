from pydantic import BaseModel
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city_id": "ARG-Buenos_Aires",
                    "city_name": "Buenos Aires",
                    "country_name": "Argentina",
                    "country_code_iso3": "ARG",
                    "admin_levels": ["ADM2union ", "ADM2"],
                    "aoi_boundary_level": "ADM2union",
                    "project": ["urbanshift", "dataforcoolcities"],
                }
            ]
        }
    }


# Response for listing cities
class CityListResponse(BaseModel):
    cities: List[CityDetail]


# Indicator Schema
class CityIndicatorsDetail(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "geo_id": "COD-Uvira_ADM3_1",
                    "geo_name": "Uvira",
                    "geo_level": "ADM3",
                    "geo_parent_name": "COD-Uvira",
                    "indicator_version": 0,
                    "ACC_1_OpenSpaceHectaresper1000people2022": 145.409455527,
                    "ACC_2_percentOpenSpaceinBuiltup2022": 0.0081307475,
                    "ACC_3_percentPopwOpenSpaceAccess2022": 0.1281915875,
                    "ACC_4_percentPopwTreeCoverAccess2022": 0.4531009647,
                    "AQ_3_percentWHOlimitPM25exposure2020": 650.117572054,
                    "BIO_1_percentNaturalArea": 0.8303408757,
                    "BIO_2_habitat_connectivity": 0.9996225035,
                    "BIO_3_percentBirdsinBuiltupAreas": -9999,
                    "BIO_4_numberPlantSpecies": -9999,
                    "BIO_5_numberBirdSpecies": -9999,
                    "BIO_6_numberArthropodSpecies": -9999,
                    "FLD_1_percentFloodProneinBuiltup2050": 0.0023108638,
                    "FLD_2_percentChangeinMaxDailyPrecip2020to2050": None,
                    "FLD_3_percentBuiltupWithin1mAboveDrainage": 0.0007730727,
                    "FLD_4_percentImperviousinBuiltup2018": 0.0040401583,
                    "FLD_5_percentBuiltupWOvegetationcover2020": 0.9975239912,
                    "FLD_6_percentRiparianZonewoVegorWatercover2020": 0.0171156996,
                    "FLD_7_percentSteepSlopesWOvegetationcover2020": 0.0036581294,
                    "GHG_2_meanannualTreeCarbonFluxMgcO2eperHA": -0.539006166,
                    "HEA_1_percentChangeinDaysAbove35C2020to2050": None,
                    "HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday": 0.014807287,
                    "HEA_3_percentBuiltwLowAlbedo": 0.8490105057,
                    "HEA_4_percentBuiltupWithoutTreeCover": 0.9988992926,
                    "LND_1_percentPermeableSurface": 0.9956248934,
                    "LND_2_percentTreeCover": 0.2891409452,
                    "LND_3_percentChangeinVegetation&WaterCover2019-2022": 0.0016699065,
                    "LND_4_percentof2000HabitatAreaRestoredby2020": 0.1078837856,
                    "LND_5_numberofHabitatTypesRestoredby2020": 0.5,
                    "LND_6_percentProtectedArea": 0.1902617786,
                    "LND_7_percentKBAsProtected": 0.9999838859,
                    "LND_8_percentKBAsBuiltup": 0.000011913,
                }
            ]
        },
        "extra": "allow",
    }

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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "0",
                    "type": "Feature",
                    "properties": {
                        "geo_id": "COD-Uvira_ADM3_1",
                        "geo_name": "Uvira",
                        "geo_level": "ADM3",
                        "geo_parent_name": "COD-Uvira",
                        "geo_version": 0,
                    },
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [
                                    [29.14637140071167, -3.27551291306084],
                                    [29.15899010337776, -3.32849459409734],
                                    [29.159295023075654, -3.34007959009418],
                                    [29.164027217145634, -3.349719854662924],
                                    [29.164747216528063, -3.351309561589972],
                                    [29.167414851796767, -3.350308442217524],
                                    [29.169720345780306, -3.349639614404152],
                                    [29.172976558699904, -3.348899125086321],
                                    [29.17530581941699, -3.348301956482154],
                                ]
                            ]
                        ],
                    },
                }
            ]
        }
    }


# GeoJSON Response
class GeoJSONFeatureCollection(BaseModel):
    type: str
    features: List[GeoFeature]
