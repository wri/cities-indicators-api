from app.const import COMMON_500_ERROR_RESPONSE
from app.schemas.projects import ListProjectsResponse

LIST_INDICATORS_RESPONSES={
    200: {
        "model": ListProjectsResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "indicators": [
                        {
                            "code": "ACC-1",
                            "data_sources": "<a href=\"https://www.openstreetmap.org\">OpenStreetMap</a>, <a href=\"https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex_cons_unadj\">WorldPop</a> ",
                            "data_sources_link": [
                                "Open spaces for public use",
                                "Population density"
                            ],
                            "importance": "Parks, natural areas and other green spaces provide city residents with invaluable recreational, spiritual, cultural, and educational services. They have been shown to improve human physical and psychological health. ",
                            "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                            "indicator_definition": "Hectares of recreational space (open space for public use) per 1000 people",
                            "indicator_label": "Recreational space per capita",
                            "indicator_legend": "Key Biodiversity Area land <br> within built-up areas (%)",
                            "methods": "The recreational services indicator is calculated as (total area of recreational space within the boundary) / (population within the boundary / 1000). Data on recreational areas were taken from the crowdsourced data initiative OpenStreetMap. Population data are 2020 estimates from WorldPop.  There are limitations to these methods and uncertainty regarding the resulting indicator values. There is uncertainty in the population estimates, especially the distribution of population within enumeration areas.",
                            "Notebook": "https://github.com/wri/cities-indicators/blob/emackres-patch-1/notebooks/compute-indicators/compute-indicator-ACC-1-openspace-per-capita.ipynb",
                            "projects": [
                                "urbanshift",
                                "cities4forests",
                                "deepdive"
                            ],
                            "theme": "Greenspace access"
                        }
                    ]
                }
            }
        }
    },
    404: {
        "description": "No indicators found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "No indicators found."
                }
            }
        }
    },
    500: COMMON_500_ERROR_RESPONSE
}
