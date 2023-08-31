from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import os

from pyairtable import Table
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
import requests

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

@app.get("/cities")
def list_cities():
    cities = cities_table.all(view="api")
    return {"cities": cities}


# Boundaries
@app.get("/boundaries")
def list_boundaries():
    api_url = "https://wri-cities.carto.com/api/v2/sql?q=select geo_id from boundaries"
    response = requests.get(api_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
    # The response should contain JSON data
        json_data = response.json()
    else:
        print("Failed to fetch data from the API.")
    return json_data

@app.get("/boundaries/{geography}")
def get_geography_boundary(geography: str):
    geography_boundary = read_carto('SELECT * FROM boundaries WHERE geo_id = {geography}').to_json()
    return geography_boundary

@app.get("/boundaries/geojson")
def list_boundaries():
    boundaries = read_carto('SELECT cartodb_id,ST_AsGeoJSON(the_geom) as the_geom FROM boundaries LIMIT 1').to_json()
    return boundaries




# Indicators
@app.get("/indicators")
def list_indicators():
    indicators = read_carto('indicators').to_json()
    return indicators


# Datasets
@app.get("/datasets")
def list_datasets():
    datasets = datasets_table.all(view="api")
    return {"datasets": datasets}
