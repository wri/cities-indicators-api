from app.schemas.common_schema import ErrorResponse

# Response keys
CITY_RESPONSE_KEYS = [
    "id",
    "admin_levels",
    "city_admin_level",
    "subcity_admin_level",
    "name",
    "country_name",
    "country_code_iso3",
    "latitude",
    "longitude",
    "projects",
    "s3_base_path",
]
INTERVENTIONS_RESPONSE_KEYS = [
    "id",
    "name",
    "areas_id",
    "areas_name",
    "filter_solution_type",
    "filter_impact_timescale",
    "filter_solution_area",
    "card_intervention_short_description",
    "card_intervention_long_description",
    "card_cooling_impact_estimation",
    "card_timescale_impact",
    "card_investment",
    "card_intervention_photo",
    "cities",
    "scenarios",
    "category",
]
SCENARIOS_RESPONSE_KEYS = [
    "id",
    "name",
    "description",
    "layers",
]
SCENARIOS_INDICATOR_VALUES_RESPONSE_KEYS = [
    "id",
    "name",
    "time",
    "value",
]
INDICATORS_LIST_RESPONSE_KEYS = [
    "id",
    "city_ids",
    "data_sources",
    "data_sources_link",
    "data_views",
    "importance",
    "definition",
    "name",
    "legend",
    "id",
    "source_metric_id",
    "population_category",
    "year",
    "methods",
    "notebook_url",
    "projects",
    "themes",
    "layers",
    "unit",
    "map_styling",
    "legend_styling",
]
DATASETS_LIST_RESPONSE_KEYS = [
    "id",
    "name",
    "description",
    "source",
    "data_sources",
    "theme",
    "spatial_resolution",
    "temporal_resolution",
    "spatial_coverage",
    "temporal_coverage",
    "cautions",
    "license",
    "image",
    "city_ids",
    "indicators",
    "layers",
    "storage",
    "function",
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
    "cif_metric_name",
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
