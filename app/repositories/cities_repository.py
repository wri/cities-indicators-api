from typing import Optional

from pyairtable import Api
from app.const import cities_table
from app.utils.settings import Settings

# Load settings
settings = Settings()

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
cities_table = airtable_api.table(settings.airtable_base_id, "Cities")


def fetch_cities(filter_formula: Optional[str] = None):
    return cities_table.all(view="api", formula=filter_formula)
