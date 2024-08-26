import pytest
from unittest.mock import patch
from app.services.cities_service import (
    list_cities,
    get_city_by_city_id,
    get_city_indicators
)
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
        "geo_id": ["city1"],
        "geo_name": ["City_1"],
        "geo_level": ["ADM"],
        "geo_parent_name": ["city1"],
        "indicator": ["Indicator_Test"],
        "indicator_version": 0,
        "value": [1000]
    })

    city_id = "city1"
    admin_level = "ADM"
    response = get_city_indicators(city_id, admin_level)

    assert isinstance(response, list)
    assert response[0]["geo_id"] == "city1"
    assert response[0]["Indicator_Test"] == 1000

# TODO: get_city_geometry
# TODO: get_city_geometry_with_indicators