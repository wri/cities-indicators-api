from typing import Optional

from pyairtable import Api
from app.utils.settings import Settings

# Load settings
settings = Settings()

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
indicators_table = airtable_api.table(settings.airtable_base_id, "Indicators")


def fetch_indicators(filter_formula: Optional[str] = None):
    return indicators_table.all(view="api", formula=filter_formula)


def fetch_first_indicator(filter_formula: Optional[str] = None):
    return indicators_table.first(view="api", formula=filter_formula)
