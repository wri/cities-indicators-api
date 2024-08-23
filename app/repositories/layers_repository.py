from typing import Optional

from pyairtable import Api
from app.utils.settings import Settings

# Load settings
settings = Settings()

# Airtable tables
airtable_api = Api(settings.cities_api_airtable_key)
layers_table = airtable_api.table(settings.airtable_base_id, "Layers")


def fetch_layers(filter_formula: Optional[str] = None):
    return layers_table.all(view="api", formula=filter_formula)


def fetch_first_layer(filter_formula: Optional[str] = None):
    return layers_table.first(view="api", formula=filter_formula)
