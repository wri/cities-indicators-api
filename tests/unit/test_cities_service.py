import pytest
from unittest.mock import patch

import pandas as pd
import geopandas as gpd
from shapely import MultiPolygon, Polygon

from app.services.cities_service import (
    list_cities,
    get_city_by_city_id,
    get_city_indicators,
    get_city_geometry,
    get_city_geometry_with_indicators,
)

# Constants for testing
POLYGON_GEOMETRY = [
    [
        [
            [0.0, 3.0],
            [100.0, 5.0],
            [73.0, 73.0],
            [42.0, 159.8],
            [17.0, 73.0],
            [0.0, 3.0],
        ]
    ]
]

# Fixtures


@pytest.fixture
def mock_cities_response():
    return [{"fields": {"city_id": "city1", "projects": ["proj1"]}}]


@pytest.fixture
def mock_projects_response():
    return [{"id": "proj1", "fields": {"project_id": "Project 1"}}]


@pytest.fixture
def mock_city_geometry_df():
    polygon = MultiPolygon([Polygon(coords[0]) for coords in POLYGON_GEOMETRY])
    return gpd.GeoDataFrame(
        {
            "geo_id": ["geo1"],
            "geo_level": ["ADM"],
            "geo_name": ["geoname1"],
            "geo_parent_name": ["geo1"],
            "geo_version": [0],
            "the_geom": [polygon],
        },
        geometry="the_geom",
        crs="EPSG:4326",
    )


@pytest.fixture
def mock_indicators():
    return [
        {
            "fields": {
                "indicator_legend": "legend",
                "unit": "hectares",
                "indicator_id": "IND_1",
                "indicator_label": "Indicator 1 label",
            }
        },
        {
            "fields": {
                "indicator_legend": "legend",
                "unit": "hectares",
                "indicator_id": "IND_2",
                "indicator_label": "Indicator 2 label",
            }
        },
    ]


@pytest.fixture
def mock_city_indicators_df():
    data = {"geo_id": ["123"], "indicator": ["IND_1"], "value": [10]}
    return pd.DataFrame(data)


# Test Cases


@patch("app.services.cities_service.fetch_cities")
@patch("app.services.cities_service.fetch_projects")
def test_list_cities(
    mock_fetch_projects, mock_fetch_cities, mock_cities_response, mock_projects_response
):
    """Test the list_cities function."""
    mock_fetch_cities.return_value = mock_cities_response
    mock_fetch_projects.return_value = mock_projects_response

    projects = ["proj1"]
    country_code_iso3 = "USA"
    response = list_cities(projects, country_code_iso3)

    assert isinstance(response, list)
    assert len(response) == 1
    assert response[0]["city_id"] == "city1"
    assert response[0]["projects"] == ["Project 1"]


@patch("app.services.cities_service.fetch_cities")
@patch("app.services.cities_service.fetch_projects")
def test_list_cities_empty(
    mock_fetch_projects, mock_fetch_cities, mock_cities_response, mock_projects_response
):
    """Test the list_cities function with no matching cities."""
    mock_fetch_cities.return_value = []
    mock_fetch_projects.return_value = mock_projects_response

    projects = ["proj1"]
    country_code_iso3 = "USA"
    response = list_cities(projects, country_code_iso3)

    assert isinstance(response, list)
    assert len(response) == 0


@patch("app.services.cities_service.fetch_cities")
@patch("app.services.cities_service.fetch_projects")
def test_get_city_by_city_id(
    mock_fetch_projects, mock_fetch_cities, mock_cities_response, mock_projects_response
):
    """Test the get_city_by_city_id function."""
    mock_fetch_cities.return_value = mock_cities_response
    mock_fetch_projects.return_value = mock_projects_response

    city_id = "city1"
    response = get_city_by_city_id(city_id)

    assert isinstance(response, dict)
    assert response["city_id"] == "city1"
    assert response["projects"] == ["Project 1"]


@patch("app.services.cities_service.fetch_cities")
@patch("app.services.cities_service.fetch_projects")
def test_get_city_by_city_id_not_found(
    mock_fetch_projects, mock_fetch_cities, mock_projects_response
):
    """Test the get_city_by_city_id function when city is not found."""
    mock_fetch_cities.return_value = []
    mock_fetch_projects.return_value = mock_projects_response

    city_id = "nonexistent_city"
    response = get_city_by_city_id(city_id)

    assert response == {}


@patch("app.services.cities_service.read_carto")
def test_get_city_indicators(mock_read_carto):
    """Test the get_city_indicators function."""
    mock_read_carto.return_value = pd.DataFrame(
        {
            "city_name": ["City_1"],
            "geo_id": ["city1"],
            "geo_level": ["ADM"],
            "geo_parent_name": ["city1"],
            "indicator_version": 0,
            "indicator": ["Indicator_Test"],
            "value": [1000],
        }
    )

    city_id = "city1"
    admin_level = "ADM"
    response = get_city_indicators(city_id, admin_level)

    assert isinstance(response, list)
    assert response[0]["geo_id"] == "city1"
    assert response[0]["Indicator_Test"] == 1000


def test_get_city_indicators_empty():
    """Test the get_city_indicators function with no matching indicators."""
    city_id = "anything"
    admin_level = "unknown"
    response = get_city_indicators(city_id, admin_level)

    assert response == []


@patch("app.services.cities_service.read_carto")
def test_get_city_geometry(mock_read_carto, mock_city_geometry_df):
    """Test the get_city_geometry function."""
    mock_read_carto.return_value = mock_city_geometry_df

    city_id = "city1"
    admin_level = "ADM"

    response = get_city_geometry(city_id, admin_level)

    assert isinstance(response, dict)
    assert response["type"] == "FeatureCollection"
    assert response["bbox"] == [0.0, 3.0, 100.0, 159.8]
    assert len(response["features"]) == 1

    feature = response["features"][0]
    assert feature["type"] == "Feature"
    assert feature["geometry"]["type"] == "MultiPolygon"
    assert feature["geometry"]["coordinates"] == POLYGON_GEOMETRY

    properties = feature["properties"]
    assert properties["geo_id"] == "geo1"
    assert properties["geo_level"] == "ADM"
    assert properties["geo_name"] == "geoname1"
    assert properties["geo_parent_name"] == "geo1"
    assert properties["geo_version"] == 0
    assert properties["bbox"] == (0.0, 3.0, 100.0, 159.8)


def test_get_city_geometry_empty():
    """Test the get_city_geometry function with no matching geometry."""
    city_id = "anything"
    admin_level = "unknown"

    response = get_city_geometry(city_id, admin_level)

    assert response == None


@patch("app.services.cities_service.read_carto")
@patch("app.services.cities_service.fetch_indicators")
def test_get_city_geometry_with_indicators(
    mock_fetch_indicators,
    mock_read_carto,
    mock_city_geometry_df,
    mock_city_indicators_df,
    mock_indicators,
):
    """Test the get_city_geometry_with_indicators function."""

    def side_effect(query):
        if "boundaries" in query:
            return mock_city_geometry_df
        elif "indicators" in query:
            return mock_city_indicators_df

    mock_read_carto.side_effect = side_effect
    mock_fetch_indicators.return_value = mock_indicators

    city_id = "CityID"
    indicator_id = "IND_1"
    admin_level = "admin_level_1"

    result = get_city_geometry_with_indicators(city_id, indicator_id, admin_level)

    assert "bbox" in result
    assert "features" in result
    assert result["features"][0]["properties"]["geo_name"] == "geoname1"
    assert result["features"][0]["properties"]["indicator_label"] == "Indicator 1 label"
    assert result["bbox"] == [0.0, 3.0, 100.0, 159.8]
