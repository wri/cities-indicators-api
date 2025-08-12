from typing import Optional

from pyairtable import Api
from ratelimit import limits, sleep_and_retry

from app.utils.settings import Settings
from app.utils.telemetry import timed

# Load settings
settings = Settings()

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
projects_table = airtable_api.table(settings.airtable_base_id, "Projects")


@sleep_and_retry
@limits(
    calls=settings.airtable_rate_limit_calls, period=settings.airtable_rate_limit_period
)
@timed
def fetch_projects(filter_formula: Optional[str] = None):
    return projects_table.all(view="all", formula=filter_formula)
