import os

from pyairtable import Api

from app.schemas.common_schema import ErrorResponse

# Carto
CARTO_API_KEY = "default_public"
CARTO_USERNAME = "wri-cities"

# Airtable tables
AIRTABLE_API_KEY = os.getenv("CITIES_API_AIRTABLE_KEY")
AIRTABLE_BASE_ID = os.getenv("CITIES_API_AIRTABLE_BASE_ID")
airtable_api = Api(AIRTABLE_API_KEY)
cities_table = airtable_api.table(AIRTABLE_BASE_ID, "Cities")
datasets_table = airtable_api.table(AIRTABLE_BASE_ID, "Datasets")
indicators_table = airtable_api.table(AIRTABLE_BASE_ID, "Indicators")
projects_table = airtable_api.table(AIRTABLE_BASE_ID, "Projects")

# Response keys
CITY_RESPONSE_KEYS = [
    "id",
    "admin_levels",
    "city_admin_level",
    "name",
    "country_name",
    "country_code_iso3",
    "latitude",
    "longitude",
    "projects",
]
INDICATORS_LIST_RESPONSE_KEYS = [
    "id",
    "data_sources",
    "data_sources_link",
    "data_views",
    "importance",
    "definition",
    "name",
    "legend",
    "layer_id",
    "methods",
    "notebook_url",
    "projects",
    "themes",
    "unit",
]
DATASETS_LIST_RESPONSE_KEYS = [
    "city_id",
    "source",
    "data_sources",
    "id",
    "name",
    "indicators",
    "spatial_coverage",
    "spatial_resolution",
    "storage",
    "theme",
    "visualization_endpoint",
]
CITY_INDICATORS_RESPONSE_KEYS = [
    "city_id",
    "city_name",
    "country_name",
    "country_code_iso3",
    "geo_id",
    "geo_level",
    "geo_parent_name",
    "indicator",
    "indicator_version",
    "unit",
    "value",
]
INDICATORS_RESPONSE_KEYS = [
    "city_id",
    "city_name",
    "country_name",
    "country_code_iso3",
    "geo_id",
    "geo_level",
    "geo_parent_name",
    "unit",
    "value",
]
INDICATORS_METADATA_RESPONSE_KEYS = [
    "id",
    "definition",
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
