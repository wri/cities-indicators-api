import os
from pyairtable import Api

from app.responses.common import ErrorResponse

# API
API_VERSION = "v1"

# Carto
CARTO_API_KEY = "default_public"
CARTO_USERNAME = "wri-cities"

# Airtable tables
AIRTABLE_API_KEY = os.getenv("CITIES_API_AIRTABLE_KEY")
AIRTABLE_BASE_ID = "appDWCVIQlVnLLaW2"
airtable_api = Api(AIRTABLE_API_KEY)
cities_table = airtable_api.table(AIRTABLE_BASE_ID, "Cities")
datasets_table = airtable_api.table(AIRTABLE_BASE_ID, "Datasets")
indicators_table = airtable_api.table(AIRTABLE_BASE_ID, "Indicators")
projects_table = airtable_api.table(AIRTABLE_BASE_ID, "Projects")

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
COMMON_500_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "example": {"detail": "An error occurred: <error_message>"}
        }
    },
}

COMMON_400_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Invalid query parameter:",
    "content": {
        "application/json": {
            "example": {"detail": "Invalid query parameter: <query_parameter>"}
        }
    },
}

COMMON_404_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Not found.",
    "content": {"application/json": {"example": {"detail": "No <entities> found."}}},
}
