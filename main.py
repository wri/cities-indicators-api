from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import os
import json
import datetime as dt

from pyairtable import Table
from pyairtable.formulas import match
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
import requests

# Authentication
## Airtable 
airtable_api_key = os.getenv('CITIES_API_AIRTABLE_KEY')
cities_table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Cities')
datasets_table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Datasets')
indicators_table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Indicators')

## Carto
set_default_credentials(username='wri-cities', api_key='default_public')


app = FastAPI()

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


# Cities
@app.get("/cities")
# Return all cities metadata from Airtable
def list_cities():
    cities = cities_table.all(view="api")
    cities = [city['fields'] for city in cities]
    return {"cities": cities}

@app.get("/cities/{city_id}")
# Return one city metadata from Airtable
def get_city(city_id: str):
    formula = f'SEARCH("{city_id}",{{id}})'
    city = cities_table.all(view="api", formula=formula)
    city = city[0]['fields']
    return city

@app.get("/cities/{city_id}/{admin_level}")
# Return one city all indicators values from Carto
def get_city_indicators(city_id: str, admin_level: str):
    city_indicators_df = read_carto(f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicators_df['creation_date'] = city_indicators_df['creation_date'].dt.strftime('%Y-%m-%d')
    city_indicators =  json.loads(city_indicators_df.to_json())
    city_indicators = {"city_indicators": city_indicators['features']}
    return city_indicators

@app.get("/cities/{city_id}/{admin_level}/geojson")
# Return one city all indicators values and geometry from Carto
def get_city_indicators_geometry(city_id: str, admin_level: str):
    city_geometry_df = read_carto(f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'")
    city_geometry =  json.loads(city_geometry_df.to_json())

    city_indicators_df = read_carto(f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicators_df['creation_date'] = city_indicators_df['creation_date'].dt.strftime('%Y-%m-%d')
    city_indicators = json.loads(city_indicators_df.to_json())

    city_indicators_geometry = {"city_indicators": city_indicators['features'], "city_geometry":city_geometry['features']}

    #TODO: add indicators dataframe from Carto and combine with city before jsonifying
    return city_indicators_geometry


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
    geography_boundary = json.loads(read_carto(f"SELECT * FROM boundaries WHERE geo_id = '{geography}'").to_json())
    return geography_boundary

@app.get("/boundaries/geojson")
def list_boundaries():
    boundaries = read_carto('SELECT cartodb_id,ST_AsGeoJSON(the_geom) as the_geom FROM boundaries LIMIT 1').to_json()
    return boundaries


# Indicators
@app.get("/indicators")
# Return all indicators metadata from Airtable
def list_indicators():
    indicators = indicators_table.all(view="api")
    indicators = [indicator['fields'] for indicator in indicators]
    # Convert data_sources_link from Airtable ID to dataset Name
    datasets = datasets_table.all(view="api")
    for indicator in indicators:
        data_sources_link = []
        if 'data_sources_link' in indicator:
            for data_source in indicator['data_sources_link']:
                for item in datasets:
                    if item['id'] == data_source:
                        data_sources_link.append(item['fields']['Name'])
        indicator['data_sources_link'] = data_sources_link
    return {"indicators": indicators}

@app.get("/indicators/{indicator_name}")
# Return one indicator values for all cities top admin level from Carto
def get_indicator(indicator_name: str):
    indicator_df = read_carto(f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and indicators.geo_name=indicators.geo_parent_name")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    indicator_df['creation_date'] = indicator_df['creation_date'].dt.strftime('%Y-%m-%d')
    indicator = json.loads(indicator_df.to_json())
    indicator = indicator['features']
    return {"indicator_values": indicator}

@app.get("/indicators/{indicator_name}/{city_id}")
# Return one indicator value for one city top admin level from Carto
def get_indicator(indicator_name: str, city_id: str):
    indicator_df = read_carto(f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and geo_name = '{city_id}'")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    indicator_df['creation_date'] = indicator_df['creation_date'].dt.strftime('%Y-%m-%d')
    indicator = json.loads(indicator_df.to_json())
    indicator = indicator['features'][0]
    return indicator


# Datasets
@app.get("/datasets")
def list_datasets():
    datasets = datasets_table.all(view="api")
    datasets = [dataset['fields'] for dataset in datasets]
    # Convert indicators from Airtable ID to indicator_label
    indicators = indicators_table.all(view="api")
    for dataset in datasets:
        Indicators = []
        if 'Indicators' in dataset:
            for indicator in dataset['Indicators']:
                for item in indicators:
                    if item['id'] == indicator:
                        Indicators.append(item['fields']['indicator_label'])
        dataset['Indicators'] = Indicators
    return {"datasets": datasets}
