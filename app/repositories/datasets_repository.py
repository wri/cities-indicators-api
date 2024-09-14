from typing import Optional

from pyairtable import Api
from ratelimit import limits, sleep_and_retry

from app.utils.settings import Settings

# Load settings
settings = Settings()

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
datasets_table = airtable_api.table(settings.airtable_base_id, "Datasets")


@sleep_and_retry
@limits(
    calls=settings.airtable_rate_limit_calls, period=settings.airtable_rate_limit_period
)
def fetch_datasets(filter_formula: Optional[str] = None):
    return datasets_table.all(view="api", formula=filter_formula)
