from typing import Optional

from pyairtable import Api
from ratelimit import limits, sleep_and_retry

from app.utils.settings import Settings
from app.utils.telemetry import timed

# Load settings
settings = Settings()

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
indicators_table = airtable_api.table(settings.airtable_base_id, "Indicators")


@sleep_and_retry
@limits(
    calls=settings.airtable_rate_limit_calls, period=settings.airtable_rate_limit_period
)
@timed
def fetch_indicators(filter_formula: Optional[str] = None):
    return indicators_table.all(view="all", formula=filter_formula)


@sleep_and_retry
@limits(
    calls=settings.airtable_rate_limit_calls, period=settings.airtable_rate_limit_period
)
@timed
def fetch_first_indicator(filter_formula: Optional[str] = None):
    return indicators_table.first(view="all", formula=filter_formula)
