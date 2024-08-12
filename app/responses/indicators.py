from app.const import (
    COMMON_400_ERROR_RESPONSE,
    COMMON_404_ERROR_RESPONSE,
    COMMON_500_ERROR_RESPONSE,
)
from app.schemas.indicators import (
    CityResponse,
    IndicatorResponse,
    ListCitiesResponse,
    ListIndicatorsResponse,
    ListThemesResponse,
)

LIST_INDICATORS_RESPONSES = {
    200: {
        "model": ListIndicatorsResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "indicators": [
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
                            "indicator_legend": "Key Biodiversity Area land <br> within built-up areas (%)",
                            "methods": "The recreational services indicator is calculated as (total area of recreational space within the boundary) / (population within the boundary / 1000). Data on recreational areas were taken from the crowdsourced data initiative OpenStreetMap. Population data are 2020 estimates from WorldPop.  There are limitations to these methods and uncertainty regarding the resulting indicator values. There is uncertainty in the population estimates, especially the distribution of population within enumeration areas.",
                            "Notebook": "https://github.com/wri/cities-indicators/blob/emackres-patch-1/notebooks/compute-indicators/compute-indicator-ACC-1-openspace-per-capita.ipynb",
                            "projects": ["urbanshift", "cities4forests", "deepdive"],
                            "theme": "Greenspace access",
                        }
                    ]
                }
            }
        },
    },
    400: COMMON_400_ERROR_RESPONSE,
    404: COMMON_404_ERROR_RESPONSE,
    500: COMMON_500_ERROR_RESPONSE,
}

LIST_INDICATORS_THEMES_RESPONSES = {
    200: {
        "model": ListThemesResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
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
        },
    },
    400: COMMON_400_ERROR_RESPONSE,
    404: COMMON_404_ERROR_RESPONSE,
    500: COMMON_500_ERROR_RESPONSE,
}

GET_CITIES_BY_INDICATOR_ID_RESPONSES = {
    200: {
        "model": ListCitiesResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "cities": [
                        {
                            "geo_id": "ARG-Mendoza_ADM-3-union_1",
                            "geo_name": "ARG-Mendoza",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "ARG-Mendoza",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 350.8144437969639,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "ARG-Mar_del_Plata_ADM-3_1",
                            "geo_name": "ARG-Mar_del_Plata",
                            "geo_level": "ADM3",
                            "geo_parent_name": "ARG-Mar_del_Plata",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 1.3852092082783116,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "ARG-Ushuaia_ADM-4_1",
                            "geo_name": "ARG-Ushuaia",
                            "geo_level": "ADM4",
                            "geo_parent_name": "ARG-Ushuaia",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 1.2475371833207298,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "ARG-Salta_ADM-2-union_1",
                            "geo_name": "ARG-Salta",
                            "geo_level": "ADM2union",
                            "geo_parent_name": "ARG-Salta",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 19.63239594980549,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "ARG-Buenos_Aires_ADM-2-union_1",
                            "geo_name": "ARG-Buenos_Aires",
                            "geo_level": "ADM2union",
                            "geo_parent_name": "ARG-Buenos_Aires",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 7.642268266093797,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "BRA-Teresina_ADM-4-union_1",
                            "geo_name": "BRA-Teresina",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "BRA-Teresina",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.403441090932263,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "BRA-Florianopolis_ADM-4-union_1",
                            "geo_name": "BRA-Florianopolis",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "BRA-Florianopolis",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 13.008957821430275,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "BRA-Belem_ADM-4-union_1",
                            "geo_name": "BRA-Belem",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "BRA-Belem",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 1.0148481249001715,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "CRI-San_Jose_ADM-2-union_1",
                            "geo_name": "CRI-San_Jose",
                            "geo_level": "ADM2union",
                            "geo_parent_name": "CRI-San_Jose",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 37.78838201026343,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "RWA-Kigali_ADM-4-union_1",
                            "geo_name": "RWA-Kigali",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "RWA-Kigali",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0754697924360913,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "SLE-Freetown_city_ADM-4-union_1",
                            "geo_name": "SLE-Freetown_city",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "SLE-Freetown_city",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0462100641743985,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "MAR-Marrakech_ADM-2_1",
                            "geo_name": "MAR-Marrakech",
                            "geo_level": "ADM2",
                            "geo_parent_name": "MAR-Marrakech",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.6802144267904426,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IND-Chennai_ADM-4-union_1",
                            "geo_name": "IND-Chennai",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "IND-Chennai",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.516070705574197,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IND-Pune_ADM-4-union_1",
                            "geo_name": "IND-Pune",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "IND-Pune",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 2.1930325031635807,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IND-Surat_ADM-4-union_1",
                            "geo_name": "IND-Surat",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "IND-Surat",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0160810403317918,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "CHN-Chengdu_ADM-3-union_1",
                            "geo_name": "CHN-Chengdu",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "CHN-Chengdu",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 1.114241281301012,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "CHN-Chongqing_ADM-1_1",
                            "geo_name": "CHN-Chongqing",
                            "geo_level": "ADM1",
                            "geo_parent_name": "CHN-Chongqing",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 2.077855885131513,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "CHN-Ningbo_ADM-3-union_1",
                            "geo_name": "CHN-Ningbo",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "CHN-Ningbo",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 1.0329188010879662,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IDN-Jakarta_ADM-4-union_1",
                            "geo_name": "IDN-Jakarta",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "IDN-Jakarta",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.1099455217073177,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IDN-Bitung_ADM-2_1",
                            "geo_name": "IDN-Bitung",
                            "geo_level": "ADM2",
                            "geo_parent_name": "IDN-Bitung",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 4.703844034678236,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IDN-Semarang_ADM-1_1",
                            "geo_name": "IDN-Semarang",
                            "geo_level": "ADM1",
                            "geo_parent_name": "IDN-Semarang",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.1052835287455369,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IDN-Balikpapan_ADM-4-union_1",
                            "geo_name": "IDN-Balikpapan",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "IDN-Balikpapan",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.040765480106916,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "IDN-Palembang_ADM-2-union_1",
                            "geo_name": "IDN-Palembang",
                            "geo_level": "ADM2union",
                            "geo_parent_name": "IDN-Palembang",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.10421152250283,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "BRA-Salvador_ADM4-union_1",
                            "geo_name": "BRA-Salvador",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "BRA-Salvador",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.6465401163971166,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "COD-Bukavu_ADM3-union_1",
                            "geo_name": "COD-Bukavu",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "COD-Bukavu",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0193109778053582,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "COD-Uvira_ADM3-union_1",
                            "geo_name": "COD-Uvira",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "COD-Uvira",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 145.40945552697562,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "COG-Brazzaville_ADM4-union_1",
                            "geo_name": "COG-Brazzaville",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "COG-Brazzaville",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0306415580712776,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "COL-Barranquilla_ADM4-union_1",
                            "geo_name": "COL-Barranquilla",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "COL-Barranquilla",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.1314054626259484,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "ETH-Addis_Ababa_ADM4-union_1",
                            "geo_name": "ETH-Addis_Ababa",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "ETH-Addis_Ababa",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0490801713579191,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "ETH-Dire_Dawa_ADM3-union_1",
                            "geo_name": "ETH-Dire_Dawa",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "ETH-Dire_Dawa",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0129539803177783,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "KEN-Nairobi_ADM3-union_1",
                            "geo_name": "KEN-Nairobi",
                            "geo_level": "ADM3union",
                            "geo_parent_name": "KEN-Nairobi",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 2.2553409353771654,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "MDG-Antananarivo_ADM4-union_1",
                            "geo_name": "MDG-Antananarivo",
                            "geo_level": "ADM4union",
                            "geo_parent_name": "MDG-Antananarivo",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0848658525492981,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "MEX-Mexico_City_ADM2-union_1",
                            "geo_name": "MEX-Mexico_City",
                            "geo_level": "ADM2union",
                            "geo_parent_name": "MEX-Mexico_City",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 5.743557356789653,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "MEX-Monterrey_ADM2-union_1",
                            "geo_name": "MEX-Monterrey",
                            "geo_level": "ADM2union",
                            "geo_parent_name": "MEX-Monterrey",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 19.51940516170509,
                            "indicator_version": 0,
                        },
                        {
                            "geo_id": "RWA-Musanze_ADM5-union_1",
                            "geo_name": "RWA-Musanze",
                            "geo_level": "ADM5union",
                            "geo_parent_name": "RWA-Musanze",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "value": 0.0199162453650737,
                            "indicator_version": 0,
                        },
                    ]
                }
            }
        },
    },
    404: COMMON_404_ERROR_RESPONSE,
    500: COMMON_500_ERROR_RESPONSE,
}

GET_METADATA_BY_INDICATOR_ID_RESPONSES = {
    200: {
        "model": IndicatorResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "indicator_id": "ACC_1_OpenSpaceHectaresper1000people2022",
                    "indicator_definition": "Hectares of recreational space (open space for public use) per 1000 people",
                    "methods": "The recreational services indicator is calculated as (total area of recreational space within the boundary) / (population within the boundary / 1000). Data on recreational areas were taken from the crowdsourced data initiative OpenStreetMap. Population data are 2020 estimates from WorldPop.  There are limitations to these methods and uncertainty regarding the resulting indicator values. There is uncertainty in the population estimates, especially the distribution of population within enumeration areas.",
                    "importance": "Parks, natural areas and other green spaces provide city residents with invaluable recreational, spiritual, cultural, and educational services. They have been shown to improve human physical and psychological health. ",
                    "data_sources": '<a href="https://www.openstreetmap.org">OpenStreetMap</a>, <a href="https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex_cons_unadj">WorldPop</a> ',
                }
            }
        },
    },
    404: COMMON_404_ERROR_RESPONSE,
    500: COMMON_500_ERROR_RESPONSE,
}

GET_INDICATOR_BY_INDICATOR_ID_CITY_ID_RESPONSES = {
    200: {
        "model": CityResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "geo_id": "BRA-Florianopolis_ADM-4-union_1",
                    "geo_name": "BRA-Florianopolis",
                    "geo_level": "ADM4union",
                    "geo_parent_name": "BRA-Florianopolis",
                    "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                    "value": 13.008957821430275,
                    "indicator_version": 0,
                }
            }
        },
    },
    404: COMMON_404_ERROR_RESPONSE,
    500: COMMON_500_ERROR_RESPONSE,
}
