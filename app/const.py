from app.schemas.common_schema import ErrorResponse

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
    "layers",
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
    "Layers",
    "Provider",
    "Spatial Coverage",
    "Spatial resolution",
    "Storage",
    "Theme",
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
    "description": "Not found",
}
