import os

os.environ["CITIES_API_AIRTABLE_KEY"] = "your_test_api_key"

from unittest.mock import patch

import geopandas as gpd
import pandas as pd
import pytest
from shapely import MultiPolygon, Polygon

from app.services.cities_service import (
    get_city_by_city_id,
    get_city_geometry,
    get_city_indicators,
    list_cities,
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
    return [{"fields": {"id": "city1", "projects": ["proj1"]}}]


@pytest.fixture
def mock_projects_response():
    return [{"id": "proj1", "fields": {"id": "Project 1"}}]


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
def mock_city_indicators_df():
    data = {"geo_id": ["123"], "indicator": ["IND_1"], "value": [10]}
    return pd.DataFrame(data)


# Test Cases


class TestListCities:
    @pytest.mark.unit
    @patch("app.services.cities_service.fetch_cities")
    @patch("app.services.cities_service.fetch_projects")
    def test_list_cities(
        self,
        mock_fetch_projects,
        mock_fetch_cities,
        mock_cities_response,
        mock_projects_response,
    ):
        """Test the list_cities function."""
        mock_fetch_cities.return_value = mock_cities_response
        mock_fetch_projects.return_value = mock_projects_response

        projects = ["proj1"]
        country_code_iso3 = "USA"
        response = list_cities("cid", projects, country_code_iso3)

        assert isinstance(response, list)
        assert len(response) == 1
        assert response[0]["id"] == "city1"
        assert response[0]["projects"] == ["Project 1"]

    @patch("app.services.cities_service.fetch_cities")
    @patch("app.services.cities_service.fetch_projects")
    def test_list_cities_empty(
        self,
        mock_fetch_projects,
        mock_fetch_cities,
        mock_projects_response,
    ):
        """Test the list_cities function with no matching cities."""
        mock_fetch_cities.return_value = []
        mock_fetch_projects.return_value = mock_projects_response

        projects = ["proj1"]
        country_code_iso3 = "USA"
        response = list_cities("cid", projects, country_code_iso3)

        assert isinstance(response, list)
        assert len(response) == 0


class TestGetCity:
    @patch("app.services.cities_service.fetch_cities")
    @patch("app.services.cities_service.fetch_projects")
    def test_get_city_by_city_id(
        self,
        mock_fetch_projects,
        mock_fetch_cities,
        mock_cities_response,
        mock_projects_response,
    ):
        """Test the get_city_by_city_id function."""
        mock_fetch_cities.return_value = mock_cities_response
        mock_fetch_projects.return_value = mock_projects_response

        city_id = "city1"
        response = get_city_by_city_id(city_id)

        assert isinstance(response, dict)
        assert response["id"] == "city1"
        assert response["projects"] == ["Project 1"]

    @patch("app.services.cities_service.fetch_cities")
    @patch("app.services.cities_service.fetch_projects")
    def test_get_city_by_city_id_not_found(
        self, mock_fetch_projects, mock_fetch_cities, mock_projects_response
    ):
        """Test the get_city_by_city_id function when city is not found."""
        mock_fetch_cities.return_value = []
        mock_fetch_projects.return_value = mock_projects_response

        city_id = "nonexistent_city"
        response = get_city_by_city_id(city_id)

        assert response is None


class TestGetCityIndicators:
    @patch("app.services.cities_service.query_carto")
    def test_get_city_indicators(self, mock_query_carto):
        """Test the get_city_indicators function."""
        mock_query_carto.return_value = pd.DataFrame(
            {
                "name": ["City_1"],
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

    @patch("app.services.cities_service.query_carto")
    def test_get_city_indicators_empty(self, mock_query_carto):
        """Test the get_city_indicators function with no matching indicators."""
        mock_query_carto.return_value = pd.DataFrame()
        city_id = "anything"
        admin_level = "unknown"

        response = get_city_indicators(city_id, admin_level)

        assert response is None


class TestGetCityGeometry:
    @patch("app.services.cities_service.query_carto")
    def test_get_city_geometry(self, mock_query_carto, mock_city_geometry_df):
        """Test the get_city_geometry function."""
        mock_query_carto.return_value = mock_city_geometry_df

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

    @patch("app.services.cities_service.query_carto")
    def test_get_city_geometry_empty(self, mock_query_carto):
        """Test the get_city_geometry function with no matching geometry."""
        mock_query_carto.return_value = pd.DataFrame()

        city_id = "unknown"
        admin_level = "unknown"

        response = get_city_geometry(city_id, admin_level)

        assert response is None
