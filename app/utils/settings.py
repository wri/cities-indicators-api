from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Basic
    cors_origins: List[str] = ["*"]

    # Carto
    carto_api_key: str = "default_public"
    carto_username: str = "wri-cities"

    # Airtable
    cities_api_airtable_key: str
    airtable_base_id: str = "appDWCVIQlVnLLaW2"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.cities_api_airtable_key:
            raise ValueError("cities_api_airtable_key must be set")
