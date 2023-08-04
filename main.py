from fastapi import FastAPI
from pyairtable import Table

import os
airtable_api_key = os.getenv('CITIES_API_AIRTABLE_KEY')
from fastapi.responses import RedirectResponse
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
# Authentication
## Airtable 
airtable_api_key = os.getenv('CITIES_API_AIRTABLE_KEY')
cities_table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Cities')
datasets_table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Datasets')

## Carto
set_default_credentials(username='wri-cities', api_key='default_public')


app = FastAPI()

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

# Indicators
@app.get("/indicators")
def list_indicators():
    indicators = read_carto('indicators')
    return indicators


@app.get("/cities")
def list_cities():
    table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Cities')
    cities = table.all(view="api")
    return {"cities": cities}
# Datasets
@app.get("/datasets")
def list_datasets():
    datasets = datasets_table.all(view="api")
    return {"datasets": datasets}
