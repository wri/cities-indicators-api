import json
import logging
import os

import pandas as pd
import requests
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pyairtable import Table

from utils.filters import generate_search_query

# Authentication
## Airtable
airtable_api_key = os.getenv("CITIES_API_AIRTABLE_KEY")
cities_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Cities")
datasets_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Datasets")
indicators_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Indicators")
projects_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Projects")

## Carto
set_default_credentials(username="wri-cities", api_key="default_public")

# Get Airtable tables using formula to exclude rows where the key field is empty
datasets_list = datasets_table.all(view="api", formula="")
indicators_list = indicators_table.all(view="api", formula="")
projects_list = projects_table.all(view="api", formula="")

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


# Cities
# Define the desired keys to extract from each city's data
city_keys = [
    "city_id",
    "city_name",
    "country_name",
    "country_code_iso3",
    "admin_levels",
    "aoi_boundary_level",
    "project",
]


@app.get(
    "/cities",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "cities": [
                            {
                                "city_id": "ARG-Buenos_Aires",
                                "city_name": "Buenos Aires",
                                "country_name": "Argentina",
                                "country_code_iso3": "ARG",
                                "admin_levels": ["ADM2union ", "ADM2"],
                                "aoi_boundary_level": "ADM2union",
                                "project": ["urbanshift", "data4coolcities"],
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "An error occurred: <error_message>"}
                }
            },
        },
    },
)
# Return all cities metadata from Airtable
def list_cities(
    project: str = Query(None, description="Project ID"),
    country_code_iso3: str = Query(None, description="ISO 3166-1 alpha-3 country code"),
):
    print(generate_search_query("project", project))
    filters = []
    if project:
        filters.append(generate_search_query("project", project))
    if country_code_iso3:
        filters.append(f"{{country_code_iso3}} = '{country_code_iso3}'")

    filter_formula = f"AND({', '.join(filters)})" if filters else ""

    try:
        cities_list = cities_table.all(view="api", formula=filter_formula)
    except Exception as e:
        logger.error(f"An Airtable error occurred: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred: Retrieving cities failed."
        ) from e

    cities = [
        {key: city["fields"].get(key) for key in city_keys} for city in cities_list
    ]

    return {"cities": cities}


@app.get("/cities/{city_id}")
# Return one city metadata from Airtable
def get_city(city_id: str):
    formula = f'"{city_id}" = {{city_id}}'
    city_data = cities_table.all(view="api", formula=formula)
    city = city_data[0]["fields"]
    # Define the desired keys to extract from the city's data
    city = {key: city[key] for key in city_keys if key in city}

    return {"cities": city}


@app.get("/cities/{city_id}/{admin_level}")
# Return one city all indicators values from Carto
def get_city_indicators(city_id: str, admin_level: str):
    city_indicators_df = read_carto(
        f"SELECT * FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}'"
    )
    # Reorder and select city geometry properties fields
    city_indicators_df = city_indicators_df[
        [
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "indicator",
            "value",
            "indicator_version",
        ]
    ]
    city_indicators_df = city_indicators_df.pivot(
        index=[
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "indicator_version",
        ],
        columns="indicator",
        values="value",
    )
    city_indicators_df.reset_index(inplace=True)

    city_indicators = json.loads(city_indicators_df.to_json(orient="records"))

    return {"city_indicators": city_indicators}


@app.get("/cities/{city_id}/{admin_level}/geojson")
# Return one city's geometry from Carto
def get_city_geometry(city_id: str, admin_level: str):
    city_geometry_df = read_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    )
    # Reorder and select city geometry properties fields
    city_geometry_df = city_geometry_df[
        [
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "geo_version",
            "the_geom",
        ]
    ]

    city_indicators_df = read_carto(
        f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}' and indicator_version=0"
    )
    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="value"
    )

    city_geojson = json.loads(city_geometry_df.to_json())

    return city_geojson


@app.get("/cities/{city_id}/{admin_level}/geojson/indicators")
# Return one city’s geometry and indicator values from Carto
def get_city_geometry_with_indicators(city_id: str, admin_level: str):
    city_geometry_df = read_carto(
        f"SELECT * FROM boundaries WHERE geo_parent_name = '{city_id}' AND geo_level = '{admin_level}'"
    )
    # Reorder and select city geometry properties fields
    city_geometry_df = city_geometry_df[
        [
            "geo_id",
            "geo_name",
            "geo_level",
            "geo_parent_name",
            "geo_version",
            "the_geom",
        ]
    ]

    city_indicators_df = read_carto(
        f"SELECT geo_id, indicator, value FROM indicators WHERE geo_parent_name = '{city_id}' and geo_level = '{admin_level}' and indicator_version=0"
    )
    city_indicators_df = city_indicators_df.pivot(
        index="geo_id", columns="indicator", values="value"
    )

    city_gdf = pd.merge(city_geometry_df, city_indicators_df, on="geo_id")

    city_geojson = json.loads(city_gdf.to_json())

    return city_geojson


@app.get("/projects")
# Return all projects metadata from Airtable
def list_projects():
    try:
        projects = projects_table.all(view="api", formula="{project_id}")
        projects_dict = {project["fields"]["project_id"] for project in projects}
        return {"projects": projects_dict}
    except Exception as e:
        logger.error(f"An Airtable error occurred: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred: Retrieving projects failed."
        ) from e


# Indicators
@app.get(
    "/indicators",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "indicators": [
                            {
                                "code": "ACC-1",
                                "data_sources": '<a href="https://www.openstreetmap.org">OpenStreetMap</a>, <a href="https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex_cons_unadj">WorldPop</a> ',
                                "data_sources_link": [
                                    "Open spaces for public use",
                                    "Population density",
                                ],
                                "importance": "Parks, natural areas and other green spaces provide city residents with invaluable recreational, spiritual, cultural, and educational services. They have been shown to improve human physical and psychological health. ",
                                "indicator": "ACC_1_OpenSpaceHectaresper1000people2022",
                                "indicator_definition": "Hectares of recreational space (open space for public use) per 1000 people",
                                "indicator_label": "Recreational space per capita",
                                "indicator_legend": "Key Biodiversity Area land <br> within built-up areas (%)",
                                "methods": "The recreational services indicator is calculated as (total area of recreational space within the boundary) / (population within the boundary / 1000). Data on recreational areas were taken from the crowdsourced data initiative OpenStreetMap. Population data are 2020 estimates from WorldPop.  There are limitations to these methods and uncertainty regarding the resulting indicator values. There is uncertainty in the population estimates, especially the distribution of population within enumeration areas.",
                                "Notebook": "https://github.com/wri/cities-indicators/blob/emackres-patch-1/notebooks/compute-indicators/compute-indicator-ACC-1-openspace-per-capita.ipynb",
                                "projects": [
                                    "urbanshift",
                                    "cities4forests",
                                    "deepdive",
                                ],
                                "theme": "Greenspace access",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "An error occurred: <error_message>"}
                }
            },
        },
    },
)
# Return all indicators metadata from Airtable
def list_indicators(project: str = Query(None, description="Project ID")):
    filter_formula = generate_search_query("projects", project)

    try:
        indicators_filtered_list = indicators_table.all(
            view="api", formula=filter_formula
        )
    except Exception as e:
        logger.error(f"An Airtable error occurred: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred: Retrieving indicators failed."
        ) from e

    # Fetch indicators and datasets as dictionaries for quick lookup
    indicators_dict = {
        indicator["id"]: indicator["fields"] for indicator in indicators_filtered_list
    }
    datasets_dict = {
        dataset["id"]: dataset["fields"]["dataset_name"] for dataset in datasets_list
    }
    projects_dict = {
        project["id"]: project["fields"]["project_id"] for project in projects_list
    }

    # Update data_sources_link for each indicator
    for indicator in indicators_dict.values():
        data_sources_link = indicator.get("data_sources_link", [])
        indicator_projects = indicator.get("projects", [])
        indicator["data_sources_link"] = [
            datasets_dict.get(data_source, data_source)
            for data_source in data_sources_link
        ]
        indicator["projects"] = [
            projects_dict.get(project, project) for project in indicator_projects
        ]

    indicators = list(indicators_dict.values())
    # Reorder indicators fields
    desired_keys = [
        "code",
        "data_sources",
        "data_sources_link",
        "importance",
        "indicator",
        "indicator_definition",
        "indicator_label",
        "indicator_legend",
        "methods",
        "Notebook",
        "projects",
        "theme",
        "unit",
    ]
    indicators = [
        {key: indicator[key] for key in desired_keys if key in indicator}
        for indicator in indicators
    ]

    return {"indicators": indicators}


@app.get("/indicators/{indicator_name}")
# Return one indicator values for all cities top admin level from Carto
def get_indicator(indicator_name: str):
    indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and indicators.geo_name=indicators.geo_parent_name"
    )
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    indicator_df["creation_date"] = indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    indicator = json.loads(indicator_df.to_json())
    indicator = [item["properties"] for item in indicator["features"]]
    # Reorder and select indicators fields
    desired_keys = [
        "geo_id",
        "geo_name",
        "geo_level",
        "geo_parent_name",
        "indicator",
        "value",
        "indicator_version",
    ]
    indicator = [
        {key: city_indicator[key] for key in desired_keys}
        for city_indicator in indicator
    ]

    return {"indicator_values": indicator}


@app.get("/indicators/{indicator_name}/{city_id}")
# Return one indicator value for one city top admin level from Carto
def get_city_indicator(indicator_name: str, city_id: str):
    city_indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and geo_name = '{city_id}'"
    )
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicator_df["creation_date"] = city_indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    city_indicator = json.loads(city_indicator_df.to_json())
    city_indicator = city_indicator["features"][0]["properties"]
    # Reorder and select city indicator fields
    desired_keys = [
        "geo_id",
        "geo_name",
        "geo_level",
        "geo_parent_name",
        "indicator",
        "value",
        "indicator_version",
    ]
    city_indicator = {
        key: city_indicator[key] for key in desired_keys if key in city_indicator
    }

    return {"indicator_values": city_indicator}


# Datasets
@app.get("/datasets")
def list_datasets():
    # Fetch datasets and indicators as dictionaries for quick lookup
    datasets_dict = {dataset["id"]: dataset["fields"] for dataset in datasets_list}
    indicators_dict = {
        indicator["id"]: indicator["fields"]["indicator_label"]
        for indicator in indicators_list
    }

    # Update Indicators for each dataset
    for dataset in datasets_dict.values():
        indicator_ids = dataset.get("Indicators", [])
        dataset["Indicators"] = [
            indicators_dict.get(indicator_id, indicator_id)
            for indicator_id in indicator_ids
        ]

    datasets = list(datasets_dict.values())
    # Reorder and select indicators fields
    desired_keys = [
        "Name",
        "Provider",
        "Data source",
        "Data source website",
        "Spatial resolution",
        "Spatial Coverage",
        "Storage",
        "visualization_endpoint",
        "Theme",
        "Indicators",
    ]
    datasets = [
        {key: dataset[key] for key in desired_keys if key in dataset}
        for dataset in datasets
    ]

    return {"datasets": datasets}


# Boundaries
@app.get("/boundaries")
def list_boundaries():
    api_url = "https://wri-cities.carto.com/api/v2/sql?q=select geo_id from boundaries"
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {"error": "Failed to fetch data from the API."}


@app.get("/boundaries/{geography}")
def get_geography_boundary(geography: str):
    geography_boundary = json.loads(
        read_carto(f"SELECT * FROM boundaries WHERE geo_id = '{geography}'").to_json()
    )

    return geography_boundary


@app.get("/boundaries/geojson")
def list_boundaries_geojson():
    boundaries = read_carto(
        "SELECT cartodb_id,ST_AsGeoJSON(the_geom) as the_geom FROM boundaries LIMIT 1"
    ).to_json()

    return boundaries
