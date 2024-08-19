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
    Notebook: HttpUrl
    projects: List[str]
    theme: List[str]
    unit: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data_sources": '<a href="https://www.openstreetmap.org">OpenStreetMap</a>, <a href="https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex_cons_unadj">WorldPop</a> ',
                    "data_sources_link": [
                        "Open spaces for public use",
                        "Population density",
                    ],
                    "importance": "Parks, natural areas and other green spaces provide city residents with invaluable recreational, spiritual, cultural, and educational services. They have been shown to improve human physical and psychological health. ",
                    "indicator_id": "ACC_1_OpenSpaceHectaresper1000people2022",
                    "indicator_definition": "Hectares of recreational space (open space for public use) per 1000 people",
                    "indicator_label": "Recreational space per capita",
                    "indicator_legend": "Key Biodiversity Area land within built-up areas (%)",
                    "methods": "The recreational services indicator is calculated as (total area of recreational space within the boundary) / (population within the boundary / 1000). Data on recreational areas were taken from the crowdsourced data initiative OpenStreetMap. Population data are 2020 estimates from WorldPop.  There are limitations to these methods and uncertainty regarding the resulting indicator values. There is uncertainty in the population estimates, especially the distribution of population within enumeration areas.",
                    "Notebook": "https://github.com/wri/cities-indicators/blob/emackres-patch-1/notebooks/compute-indicators/compute-indicator-ACC-1-openspace-per-capita.ipynb",
                    "projects": ["urbanshift", "cities4forests", "deepdive"],
                    "theme": ["Greenspace access"],
                    "unit": "%",
                }
            ]
        }
    }


class IndicatorsResponse(BaseModel):
    indicators: List[Indicator]


class IndicatorsThemesResponse(BaseModel):
    themes: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": {
                "themes": [
                    "Biodiversity",
                    "Climate mitigation",
                    "Flooding",
                    "Greenspace access",
                    "Health - Air Quality",
                    "Health - Heat",
                    "Land protection and restoration",
                ]
            }
        }
    }


class IndicatorValueResponse(BaseModel):
    geo_id: str
    geo_name: str
    geo_level: str
    geo_parent_name: str
    indicator: str
    value: float
    indicator_version: Optional[int] = 0

    model_config = {
        "json_schema_extra": {
            "examples": {
                "geo_id": "BRA-Florianopolis_ADM-4-union_1",
                "geo_name": "BRA-Florianopolis",
                "geo_level": "ADM4union",
                "geo_parent_name": "BRA-Florianopolis",
                "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                "value": 13.008957821430275,
                "indicator_version": 0,
            }
        }
    }


class CitiesByIndicatorIdResponse(BaseModel):
    cities: List[IndicatorValueResponse]


class MetadataByIndicatorIdResponse(BaseModel):
    indicator_id: str
    indicator_definition: str
    methods: str
    importance: str
    data_sources: str

    model_config = {
        "json_schema_extra": {
            "examples": {
                "indicator_id": "ACC_1_OpenSpaceHectaresper1000people2022",
                "indicator_definition": "Hectares of recreational space (open space for public use) per 1000 people",
                "methods": "The recreational services indicator is calculated as (total area of recreational space within the boundary) / (population within the boundary / 1000). Data on recreational areas were taken from the crowdsourced data initiative OpenStreetMap. Population data are 2020 estimates from WorldPop.  There are limitations to these methods and uncertainty regarding the resulting indicator values. There is uncertainty in the population estimates, especially the distribution of population within enumeration areas.",
                "importance": "Parks, natural areas and other green spaces provide city residents with invaluable recreational, spiritual, cultural, and educational services. They have been shown to improve human physical and psychological health. ",
                "data_sources": '<a href="https://www.openstreetmap.org">OpenStreetMap</a>, <a href="https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex_cons_unadj">WorldPop</a> ',
            }
        }
    }
