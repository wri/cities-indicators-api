from pyairtable import Api

from app.schemas.common import ErrorResponse
from app.utils.settings import Settings

# Load settings
settings = Settings()

# API Version
API_VERSION = settings.api_version

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
cities_table = airtable_api.table(settings.airtable_base_id, "Cities")
datasets_table = airtable_api.table(settings.airtable_base_id, "Datasets")
indicators_table = airtable_api.table(settings.airtable_base_id, "Indicators")
projects_table = airtable_api.table(settings.airtable_base_id, "Projects")

# Response keys
CITY_RESPONSE_KEYS = [
    "city_id",
    "admin_levels",
    "aoi_boundary_level",
    "city_name",
    "country_name",
    "country_code_iso3",
    "latitude",
    "longitude",
    "projects",
]
INDICATORS_LIST_RESPONSE_KEYS = [
    "indicator_id",
    "data_sources",
    "data_sources_link",
    "data_views",
    "importance",
    "indicator_definition",
    "indicator_label",
    "indicator_legend",
    "layer_id",
    "methods",
    "Notebook",
    "projects",
    "theme",
    "unit",
]
DATASETS_LIST_RESPONSE_KEYS = [
    "city_ids",
    "Data source",
    "Data source website",
    "dataset_id",
    "dataset_name",
    "Indicators",
    "Provider",
    "Spatial Coverage",
    "Spatial resolution",
    "Storage",
    "Theme",
    "visualization_endpoint",
]
INDICATORS_RESPONSE_KEYS = [
    "geo_id",
    "geo_name",
    "geo_level",
    "geo_parent_name",
    "indicator",
    "value",
    "indicator_version",
]
INDICATORS_METADATA_RESPONSE_KEYS = [
    "indicator_id",
    "indicator_definition",
    "methods",
    "importance",
    "data_sources",
]

# Common HTTP responses
COMMON_200_SUCCESSFUL_RESPONSE = {
    "description": "Successful Response",
}

COMMON_500_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "example": {"detail": "An error occurred: <error_message>"}
        }
    },
}

COMMON_404_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Not found.",
}
