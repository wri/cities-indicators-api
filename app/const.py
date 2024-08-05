import os
from pyairtable import Table

from app.schemas.cities import ErrorResponse

# Carto
CARTO_API_KEY = os.getenv('CARTO_API_KEY')
CARTO_USERNAME = os.getenv('CARTO_USERNAME')

# Airtable tables
AIRTABLE_API_KEY = os.getenv('CITIES_API_AIRTABLE_KEY')
AIRTABLE_BASE_ID = os.getenv('CITIES_API_AIRTABLE_BASE_ID')
cities_table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, 'Cities')
datasets_table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, 'Datasets')
indicators_table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, 'Indicators')
projects_table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, 'Projects')

# Response keys
CITY_RESPONSE_KEYS = ["city_id", 
            "city_name", 
            "country_name", 
            "country_code_iso3", 
            "admin_levels", 
            "aoi_boundary_level", 
            "project"]

COMMON_500_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "example": {
                "detail": "An error occurred: <error_message>"
            }
        }
    }
}