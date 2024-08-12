import json
import logging
import os
from typing import Optional

import pandas as pd
import requests
from cartoframes import read_carto
from cartoframes.auth import set_default_credentials
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pyairtable import Table
from starlette.middleware.base import BaseHTTPMiddleware

from utils.filters import construct_filter_formula, generate_search_query

# Authentication
## Airtable
airtable_api_key = os.getenv("CITIES_API_AIRTABLE_KEY")
cities_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Cities")
datasets_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Datasets")
indicators_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Indicators")
projects_table = Table(airtable_api_key, "appDWCVIQlVnLLaW2", "Projects")

# Get Airtable tables using formula to exclude rows where the key field is empty
datasets_list = datasets_table.all(view="api", formula="")
indicators_list = indicators_table.all(view="api", formula="")
projects_list = projects_table.all(view="api", formula="")

## Carto
set_default_credentials(username="wri-cities", api_key="default_public")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Middlewares
class StripApiPrefixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            request.scope["path"] = request.url.path[4:]
        response = await call_next(request)
        return response


DESCRIPTION = """
You can use this API to get the value of various indicators for a number of cities at multiple admin levels.
"""

app = FastAPI(
    title="WRI Cities Indicators API",
    description=DESCRIPTION,
    summary="An indicators API",
    version="v0",
    terms_of_service="TBD",
    contact={
        "name": "WRI Cities Data Team",
        "url": "https://citiesindicators.wri.org/",
        "email": "citiesdata@wri.org",
    },
    license_info={
        "name": "License TBD",
        "url": "https://opensource.org/licenses/",
    },
)
app.add_middleware(StripApiPrefixMiddleware)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS")

if cors_origins:
    cors_origins = cors_origins.split(",")
else:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
)

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


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")



@app.get("/health")
def health_check():
    return {"status": "ok"}


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
def list_cities(
    project_in: Optional[str] = Query(
        None,
        description="Filter by a specific Project ID in a multiple selection field",
    ),
    country_code_iso3: Optional[str] = Query(
        None, description="Filter by ISO 3166-1 alpha-3 country code"
    ),
):
    """
    Retrieve a list of cities based on provided filter parameters.
    """
    filters = {}

    if project_in:
        filters["project_in"] = project_in
    if country_code_iso3:
        filters["country_code_iso3"] = country_code_iso3

    filter_formula = construct_filter_formula(filters)

    try:
        cities_list = cities_table.all(view="api", formula=filter_formula)
    except Exception as e:
        logger.error("An Airtable error occurred: %s", e)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving cities failed."
        ) from e

    cities = [
        {key: city["fields"].get(key) for key in city_keys} for city in cities_list
    ]

    return {"cities": cities}


@app.get(
    "/cities/{city_id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "cities": {
                            "city_id": "BRA-Florianopolis",
                            "city_name": "Florianopolis",
                            "country_name": "Brazil",
                            "country_code_iso3": "BRA",
                            "admin_levels": ["ADM4union", "ADM4"],
                            "aoi_boundary_level": "ADM4union",
                            "project": ["urbanshift"],
                        }
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
def get_city(city_id: str):
    """
    Retrieve a single city by its ID.
    """
    formula = f'"{city_id}" = {{city_id}}'
    city_data = cities_table.all(view="api", formula=formula)
    city = city_data[0]["fields"]
    # Define the desired keys to extract from the city's data
    city = {key: city[key] for key in city_keys if key in city}

    return {"cities": city}


@app.get("/cities/{city_id}/{admin_level}")
def get_city_indicators(city_id: str, admin_level: str):
    """
    Retrieve all indicators for a single city and admin level.
    """
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
def get_city_geometry(city_id: str, admin_level: str):
    """
    Retrieve the geometry of a single city and admin level.
    """
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
    """
    Retrieve the indicators and geometry of a single city and admin level.
    """
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
def list_projects():
    """
    Retrieve the list of projects.
    """
    try:
        projects = projects_table.all(view="api", formula="{project_id}")
        projects_dict = {project["fields"]["project_id"] for project in projects}
        return {"projects": projects_dict}
    except Exception as e:
        logger.error("An Airtable error occurred: %s", e)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving projects failed."
        ) from e


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
                                "indicator_id": "ACC_1_OpenSpaceHectaresper1000people2022",
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
                                "unit": "%",
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
def list_indicators(
    project_in: Optional[str] = Query(
        None,
        description="Filter by a specific Project ID in a multiple selection field",
    )
):
    """
    Retrieve a list of indicators based on provided filter parameters.
    """
    filter_formula = generate_search_query("projects", project_in)

    try:
        indicators_filtered_list = indicators_table.all(
            view="api", formula=filter_formula
        )
    except Exception as e:
        logger.error("An Airtable error occurred: %s", e)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving indicators failed."
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
        "indicator_id",
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


@app.get(
    "/indicators/themes",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "themes": [
                            "Biodiversity",
                            "Climate mitigation",
                            "Flooding",
                            "Greenspace access",
                            "Health - Air Quality",
                            "Health - Heat",
                            "Land protection and restoration",
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
def list_indicators_themes():
    """
    Retrieve the list of themes.
    """
    indicators = indicators_table.all(view="api", formula="")
    themes_set = set()

    for indicator in indicators:
        theme = indicator["fields"].get("theme")
        if theme:
            themes_set.add(theme)

    return {"themes": sorted(list(themes_set))}


@app.get("/indicators/{indicator_id}")
def get_indicator(indicator_id: str):
    """
    Retrieve all the cities indicators specified by indicator_id.
    """
    indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_id}' and indicators.geo_name=indicators.geo_parent_name"
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


@app.get("/indicators/metadata/{indicator_id}")
def get_indicator_metadata(indicator_id: str):
    """
    Retrieve all metadata for a single indicator by indicator_id.
    """
    filter_formula = generate_search_query("indicator_id", indicator_id)
    try:
        filtered_indicator = indicators_table.first(view="api", formula=filter_formula)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not filtered_indicator:
        raise HTTPException(status_code=404, detail="No indicator found.")

    indicator = filtered_indicator["fields"]
    # Reorder indicators fields
    desired_keys = [
        "indicator_id",
        "indicator_definition",
        "methods",
        "importance",
        "data_sources",
    ]
    return {key: indicator[key] for key in desired_keys if key in indicator}


@app.get("/indicators/{indicator_id}/{city_id}")
def get_city_indicator(indicator_id: str, city_id: str):
    """
    Retrieve a single city indicator specified by indicator_id and city_id.
    """
    city_indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_id}' and geo_name = '{city_id}'"
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


@app.get(
    "/datasets",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "datasets": [
                            {
                                "city_ids": ["ARG-Buenos_Aires"],
                                "Data source": "ESA World Cover",
                                "Data source website": "https://esa-worldcover.org/en",
                                "dataset_id": "esa_land_cover_2020",
                                "dataset_name": "ESA Land Cover",
                                "Indicators": [
                                    "Natural Areas",
                                    "Connectivity of natural lands",
                                    "Biodiversity in built-up areas (birds)",
                                    "Built-up Key Biodiversity Areas",
                                    "Urban open space for public use",
                                    "Surface reflectivity",
                                    "Built land without tree cover",
                                    "Exposure to coastal and river flooding",
                                    "Land near natural drainage",
                                    "Impervious surfaces",
                                    "Vegetation cover in built areas",
                                ],
                                "Provider": "ESA",
                                "Spatial Coverage": "Global",
                                "Spatial resolution": "10m",
                                "Storage": "s3://cities-indicators/data/land_use/esa_world_cover/",
                                "Theme": ["Land use"],
                            }
                        ]
                    }
                }
            },
        },
        400: {
            "description": "Bad Request - No datasets found",
            "content": {
                "application/json": {"example": {"detail": "No datasets found."}}
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
def list_datasets(
    city_id: str = Query(None, description="City ID"),
):
    """
    Retrieve the list of datasets
    """
    filter_formula = generate_search_query("city_id", city_id)

    try:
        cities_list = cities_table.all(view="api", formula="{city_id}")
        datasets_filter_list = datasets_table.all(view="api", formula=filter_formula)
    except Exception as e:
        logger.error("An Airtable error occurred: %s", e)
        raise HTTPException(
            status_code=500, detail="An error occurred: Retrieving indicators failed."
        ) from e

    # Fetch cities, datasets and indicators as dictionaries for quick lookup
    cities_dict = {city["id"]: city["fields"] for city in cities_list}
    datasets_dict = {
        dataset["id"]: dataset["fields"] for dataset in datasets_filter_list
    }
    indicators_dict = {
        indicator["id"]: indicator["fields"]["indicator_label"]
        for indicator in indicators_list
    }

    # Update Indicators for each dataset
    for dataset in datasets_dict.values():
        indicator_ids = dataset.get("Indicators", [])
        cities_ids = dataset.get("city_id", [])
        dataset["Indicators"] = [
            indicators_dict.get(indicator_id, indicator_id)
            for indicator_id in indicator_ids
        ]
        dataset["city_ids"] = [
            cities_dict[city_id]["city_id"] for city_id in cities_ids
        ]

    datasets = list(datasets_dict.values())
    # Reorder and select indicators fields
    desired_keys = [
        "city_ids",
        "Data source",
        "Data source website",
        "dataset_id",
        "dataset_name",
        "Indicators",
        "Provider",
        "Spatial Coverage",
        "Spatial resolution",
        "Storage",
        "Theme",
        "visualization_endpoint",
    ]
    datasets = [
        {key: dataset[key] for key in desired_keys if key in dataset}
        for dataset in datasets
    ]

    return {"datasets": datasets}


@app.get("/boundaries")
def list_boundaries():
    """
    Retrieve the list of boundaries
    """
    api_url = "https://wri-cities.carto.com/api/v2/sql?q=select geo_id from boundaries"
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred: %s", e)
        return {"error": "An error occurred: Retrieving boundaries failed."}



@app.get("/boundaries/{geography}")
def get_geography_boundary(geography: str):
    """
    Retrieve a single boundary by geography.
    """
    geography_boundary = json.loads(
        read_carto(f"SELECT * FROM boundaries WHERE geo_id = '{geography}'").to_json()
    )

    return geography_boundary


@app.get("/boundaries/geojson")
def list_boundaries_geojson():
    """
    Retrieve the geometry from the boundaries.
    """
    boundaries = read_carto(
        "SELECT cartodb_id,ST_AsGeoJSON(the_geom) as the_geom FROM boundaries LIMIT 1"
    ).to_json()

    return boundaries
