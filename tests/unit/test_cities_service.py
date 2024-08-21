import pytest
from unittest.mock import patch, MagicMock
from app.services.cities_service import (
    list_cities,
    get_city_by_city_id,
    get_city_indicators,
    get_city_geometry,
    get_city_geometry_with_indicators
)
from app.schemas.cities_schema import CityListResponse, GeoJSONFeatureCollection
import pandas as pd


@pytest.fixture
def mock_cities_response():
    return [{"fields": {"city_id": "city1", "projects": ["proj1"]}}]


@pytest.fixture
def mock_projects_response():
    return [{"id": "proj1", "fields": {"project_id": "Project 1"}}]


@patch('app.services.cities_service.fetch_cities')
@patch('app.services.cities_service.fetch_projects')
def test_list_cities(mock_fetch_projects, mock_fetch_cities, mock_cities_response, mock_projects_response):
    mock_fetch_cities.return_value = mock_cities_response
    mock_fetch_projects.return_value = mock_projects_response

    projects = ["proj1"]
    country_code_iso3 = "USA"
    response = list_cities(projects, country_code_iso3)

    assert isinstance(response, list)
    assert len(response) == 1
    assert response[0]['city_id'] == "city1"
    assert response[0]['projects'] == ["Project 1"]


@patch('app.services.cities_service.fetch_cities')
@patch('app.services.cities_service.fetch_projects')
def test_get_city_by_city_id(mock_fetch_projects, mock_fetch_cities, mock_cities_response, mock_projects_response):
    mock_fetch_cities.return_value = mock_cities_response
    mock_fetch_projects.return_value = mock_projects_response

    city_id = "city1"
    response = get_city_by_city_id(city_id)

    assert isinstance(response, dict)
    assert response['city_id'] == "city1"
    assert response['projects'] == ["Project 1"]


@patch('app.services.cities_service.read_carto')
def test_get_city_indicators(mock_read_carto):
    mock_read_carto.return_value = pd.DataFrame({
        "geo_id": ["geo1"],
        "geo_name": ["City 1"],
        "geo_level": ["admin"],
        "geo_parent_name": ["city1"],
        "indicator": ["Population"],
        "indicator_version": 0,
        "value": [1000]
    })

    city_id = "city1"
    admin_level = "admin"
    response = get_city_indicators(city_id, admin_level)

    assert isinstance(response, list)
    assert response[0]["geo_id"] == "geo1"
    assert response[0]["Population"] == 1000


@patch('app.services.cities_service.read_carto')
def test_get_city_geometry(mock_read_carto):
    mock_read_carto.return_value = pd.DataFrame({
        "geo_id": ["geo1"],
        "geo_name": ["City 1"],
        "geo_level": ["admin"],
        "geo_parent_name": ["city1"],
        "geo_version": [1],
        "indicator": ["Population"],
        "the_geom": [{}],
        "value": [1000]
    })

    city_id = "city1"
    admin_level = "admin"
    response = get_city_geometry(city_id, admin_level)

    assert isinstance(response, dict)
    # assert "features" in response


@patch('app.services.cities_service.read_carto')
def test_get_city_geometry_with_indicators(mock_read_carto):
    mock_read_carto.side_effect = [
        pd.DataFrame({
            "geo_id": ["geo1"],
            "geo_name": ["City 1"],
            "geo_level": ["admin"],
            "geo_parent_name": ["city1"],
            "geo_version": [1],
            "the_geom": [{}]
        }),
        pd.DataFrame({
            "geo_id": ["geo1"],
            "indicator": ["Population"],
            "value": [1000]
        })
    ]

    city_id = "city1"
    admin_level = "admin"
    response = get_city_geometry_with_indicators(city_id, admin_level)

    assert isinstance(response, dict)
    # assert "features" in response
    # assert len(response["features"]) > 0
    # assert response["features"][0]["properties"]["geo_id"] == "geo1"
    # assert response["features"][0]["properties"]["Population"] == 1000
