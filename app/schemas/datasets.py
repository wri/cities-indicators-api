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


class ListDatasetsResponse(BaseModel):
    datasets: List[Dataset]
