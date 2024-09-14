from app.schemas.common_schema import ErrorResponse

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
    "id",
    "methods",
    "notebook_url",
    "projects",
    "themes",
    "layers",
    "unit",
]
DATASETS_LIST_RESPONSE_KEYS = [
    "id",
    "name",
    "city_ids",
    "data_sources",
    "indicators",
    "layers",
    "source",
    "spatial_coverage",
    "spatial_resolution",
    "storage",
    "theme",
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

COMMON_400_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Invalid query parameter",
    "content": {
        "application/json": {
            "example": {"detail": "Invalid query parameter: <query_parameter>"}
        }
    },
}

COMMON_404_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Not found",
}
