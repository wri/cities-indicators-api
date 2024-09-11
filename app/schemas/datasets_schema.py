from pydantic import BaseModel, HttpUrl
from typing import List


class Dataset(BaseModel):
    id: str
    name: str
    city_ids: List[str]
    data_sources: HttpUrl
    indicators: List[str]
    layers: List[str]
    source: str
    spatial_coverage: str
    spatial_resolution: str
    storage: str
    theme: List[str]


class DatasetsResponse(BaseModel):
    datasets: List[Dataset]
