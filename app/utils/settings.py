from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic
    cors_origins: List[str] = ["*"]

    # Carto
    carto_api_key: str = "default_public"
    carto_username: str = "wri-cities"

    # Airtable
    cities_api_airtable_key: str
    airtable_base_id: str = "appDWCVIQlVnLLaW2"

    model_config = ConfigDict(extra="ignore")
