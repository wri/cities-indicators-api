import logging
import time

from carto import exceptions
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
from ratelimit import limits, sleep_and_retry

from app.utils.settings import Settings

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

# Carto settings
set_default_credentials(
    username=settings.carto_username, api_key=settings.carto_api_key
)


@sleep_and_retry
@limits(calls=10, period=1)
def query_carto(query: str, retries=6, backoff_factor=2):
    last_exception = None
    for attempt in range(retries):
        try:
            return read_carto(query)
        except exceptions.CartoRateLimitException as e:
            last_exception = e
            if attempt == retries - 1:
                raise last_exception from e
            sleep_time = backoff_factor**attempt
            logger.exception(
                "Rate limit hit. Retrying in %d seconds...", sleep_time, exc_info=True
            )
            time.sleep(sleep_time)

    return None
