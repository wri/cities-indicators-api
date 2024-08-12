from app.const import COMMON_500_ERROR_RESPONSE
from app.schemas.datasets import ListDatasetsResponse


LIST_DATASETS_RESPONSES = {
    200: {
        "model": ListDatasetsResponse,
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "datasets": [
                        {
                            "city_ids": ["ARG-Buenos_Aires"],
                            "Data source": "ESA World Cover",
                            "Data source website": "https://esa-worldcover.org/en",
                            "dataset_id": "esa_land_cover_2020",
                            "dataset_name": "ESA Land Cover",
                            "Indicators": [
                                "Natural Areas",
                                "Connectivity of natural lands",
                                "Biodiversity in built-up areas (birds)",
                                "Built-up Key Biodiversity Areas",
                                "Urban open space for public use",
                                "Surface reflectivity",
                                "Built land without tree cover",
                                "Exposure to coastal and river flooding",
                                "Land near natural drainage",
                                "Impervious surfaces",
                                "Vegetation cover in built areas",
                            ],
                            "Provider": "ESA",
                            "Spatial Coverage": "Global",
                            "Spatial resolution": "10m",
                            "Storage": "s3://cities-indicators/data/land_use/esa_world_cover/",
                            "Theme": ["Land use"],
                        }
                    ]
                }
            }
        },
    },
    500: COMMON_500_ERROR_RESPONSE,
}
