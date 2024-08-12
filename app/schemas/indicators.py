from pydantic import BaseModel, HttpUrl
from typing import List


class ListIndicatorsResponse(BaseModel):
    code: str
    data_sources: str
    data_sources_link: List[str]
    importance: str
    indicator: str
    indicator_definition: str
    indicator_label: str
    indicator_legend: str
    methods: str
    Notebook: HttpUrl
    projects: List[str]
    theme: str


class ListThemesResponse(BaseModel):
    themes: List[str]
