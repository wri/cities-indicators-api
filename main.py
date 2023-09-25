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
    cities_data = cities_table.all(view="api")
    # Define the desired keys to extract from each city's data
    desired_keys = ["id", "country_name", "country_code_iso3", "name", "admin_levels", "project",
                    "aoi_boundary_level", "aoi_boundary_file", "units_boundary_level", "unit_boundary_file"]
    cities = [{key: city['fields'][key] for key in desired_keys if key in city['fields']} for city in cities_data]

    return {"cities": cities}

@app.get("/cities/{city_id}")
# Return one city metadata from Airtable
def get_city(city_id: str):
    formula = f'"{city_id}" = {{id}}'
    city_data = cities_table.all(view="api", formula=formula)
    city = city_data[0]['fields']
    # Define the desired keys to extract from the city's data
    desired_keys = ["id", "country_name", "country_code_iso3", "name", "admin_levels", "project",
                    "aoi_boundary_level", "aoi_boundary_file", "units_boundary_level", "unit_boundary_file"]
    city = {key: city[key] for key in desired_keys if key in city}
    
    return {"cities": city}

@app.get("/cities/{city_id}/{admin_level}")
# Return one city all indicators values from Carto
def get_city_indicators(city_id: str, admin_level: str):
    city_indicators_df = read_carto(f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicators_df['creation_date'] = city_indicators_df['creation_date'].dt.strftime('%Y-%m-%d')
    city_indicators = json.loads(city_indicators_df.to_json())
    city_indicators = [item['properties'] for item in city_indicators['features']]
    # Select and reorder the desired keys
    desired_keys = ["geo_id", "geo_level", "geo_name", "geo_parent_name", "indicator", "value", "indicator_version"]
    city_indicators = [{key: city_indicator[key] for key in desired_keys if key in city_indicator} for city_indicator in city_indicators]

    return {"city_indicators": city_indicators}

@app.get("/cities/{city_id}/{admin_level}/geojson")
# Return one city all indicators values and geometry from Carto
def get_city_indicators_geometry(city_id: str, admin_level: str):
    city_geometry_df = read_carto(f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'")
    # Reorder and select city geometry properties fields
    city_geometry_df = city_geometry_df[["geo_id", "geo_level", "geo_name", "geo_parent_name", "geo_version", "the_geom"]]
    city_geometry = json.loads(city_geometry_df.to_json())
    city_geometry = [{'properties': item['properties'],
                      'geometry': item['geometry']} for item in city_geometry['features']]

    city_indicators_df = read_carto(f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicators_df['creation_date'] = city_indicators_df['creation_date'].dt.strftime('%Y-%m-%d')
    city_indicators = json.loads(city_indicators_df.to_json())
    city_indicators = [item['properties'] for item in city_indicators['features']]
    # Reorder and select city indicators fields
    desired_keys = ["geo_id", "geo_level", "geo_name", "geo_parent_name", "indicator", "value", "indicator_version"]
    city_indicators = [{key: city_indicator[key] for key in desired_keys if key in city_indicator} for city_indicator in city_indicators]

    return {"city_indicators": city_indicators, "city_geometry": city_geometry}


# Indicators
@app.get("/indicators")
# Return all indicators metadata from Airtable
def list_indicators():
    # Fetch indicators and datasets as dictionaries for quick lookup
    indicators_dict = {indicator['id']: indicator['fields'] for indicator in indicators_table.all(view="api")}
    datasets_dict = {dataset['id']: dataset['fields']['Name'] for dataset in datasets_table.all(view="api")}

    # Update data_sources_link for each indicator
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get('data_sources_link', [])
        indicator['data_sources_link'] = [datasets_dict.get(data_source, data_source) for data_source in data_sources_link]

    indicators = list(indicators_dict.values())
    # Reorder indicators fields
    desired_keys = ["indicator", "indicator_label", "code", "indicator_definition", "importance",
                    "methods", "data_sources", "data_sources_link", "indicator_legend", "theme", "Notebook"]
    indicators = [{key: indicator[key] for key in desired_keys if key in indicator} for indicator in indicators]
    
    return {"indicators": indicators}

@app.get("/indicators/{indicator_name}")
# Return one indicator values for all cities top admin level from Carto
def get_indicator(indicator_name: str):
    indicator_df = read_carto(f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and indicators.geo_name=indicators.geo_parent_name")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    indicator_df['creation_date'] = indicator_df['creation_date'].dt.strftime('%Y-%m-%d')
    indicator = json.loads(indicator_df.to_json())
    indicator = [item['properties'] for item in indicator['features']]
    # Reorder and select indicators fields
    desired_keys = ["geo_id", "geo_level", "geo_name","geo_parent_name", "indicator", "value", "indicator_version"]
    indicator = [{key: city_indicator[key] for key in desired_keys} for city_indicator in indicator]

    return {"indicator_values": indicator}

@app.get("/indicators/{indicator_name}/{city_id}")
# Return one indicator value for one city top admin level from Carto
def get_city_indicator(indicator_name: str, city_id: str):
    city_indicator_df = read_carto(f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and geo_name = '{city_id}'")
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicator_df['creation_date'] = city_indicator_df['creation_date'].dt.strftime('%Y-%m-%d')
    city_indicator = json.loads(city_indicator_df.to_json())
    city_indicator = city_indicator['features'][0]['properties']
    # Reorder and select city indicator fields
    desired_keys = ["geo_id", "geo_level", "geo_name","geo_parent_name", "indicator", "value", "indicator_version"]
    city_indicator = {key: city_indicator[key] for key in desired_keys if key in city_indicator}

    return {"indicator_values": city_indicator}


# Datasets
@app.get("/datasets")
def list_datasets():
    # Fetch datasets and indicators as dictionaries for quick lookup
    datasets_dict = {dataset['id']: dataset['fields'] for dataset in datasets_table.all(view="api")}
    indicators_dict = {indicator['id']: indicator['fields']['indicator_label'] for indicator in indicators_table.all(view="api")}

    # Update Indicators for each dataset
    for dataset in datasets_dict.values():
        indicator_ids = dataset.get('Indicators', [])
        dataset['Indicators'] = [indicators_dict.get(indicator_id, indicator_id) for indicator_id in indicator_ids]

    datasets = list(datasets_dict.values())
    # Reorder and select indicators fields
    desired_keys = ["Name", "Spatial resolution", "Spatial Coverage", "Provider", "Data source",
                    "Data source website", "Storage", "Theme", "visualization_endpoint", "Indicators"]
    datasets = [{key: dataset[key] for key in desired_keys if key in dataset} for dataset in datasets]

    return {"datasets": datasets}


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
