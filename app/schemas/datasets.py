from pydantic import BaseModel, HttpUrl
from typing import List


class Dataset(BaseModel):
    city_ids: List[str]
    Data_source: str
    Data_source_website: HttpUrl
    dataset_id: str
    dataset_name: str
    Indicators: List[str]
    Provider: str
    Spatial_Coverage: str
    Spatial_resolution: str
    Storage: str
    Theme: List[str]

    model_config = {
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


class DatasetsResponse(BaseModel):
    datasets: List[Dataset]
