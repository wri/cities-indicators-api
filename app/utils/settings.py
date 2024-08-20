from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic
    api_version: str = "v1"
    cors_origins: List[str] = ["*"]

    # Carto
    carto_api_key: str = "default_public"
    carto_username: str = "wri-cities"

    # Airtable
    cities_api_airtable_key: str
    airtable_base_id: str = "appDWCVIQlVnLLaW2"

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
