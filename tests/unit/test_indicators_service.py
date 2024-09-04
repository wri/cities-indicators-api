import pytest
from unittest.mock import patch
import geopandas as gpd
import pandas as pd

from app.services.indicators_service import (
    list_indicators,
    list_indicators_themes,
    get_cities_by_indicator_id,
    get_metadata_by_indicator_id,
    get_city_indicator_by_indicator_id_and_city_id,
)
from app.repositories.indicators_repository import fetch_indicators, fetch_first_indicator


# Fixtures


@pytest.fixture
def mock_indicators():
    return [
        {
            "id": "ind1",
            "fields": {
                "data_sources_link": ["ds1"],
                "projects": ["proj1"],
                "theme": ["Theme 1", "Theme 2"],
                "indicator_id": "IND_1",
                "indicator_label": "Indicator 1",
                "unit": "unit1",
            },
        },
        {
            "id": "ind2",
            "fields": {
                "data_sources_link": ["ds2"],
                "projects": ["proj2"],
                "theme": ["Theme 2", "Theme 3"],
                "indicator_id": "IND_2",
                "indicator_label": "Indicator 2",
                "unit": "unit2",
            },
        },
    ]


@pytest.fixture
def mock_datasets():
    return [
        {"id": "ds1", "fields": {"dataset_name": "Dataset 1"}},
        {"id": "ds2", "fields": {"dataset_name": "Dataset 2"}},
    ]


@pytest.fixture
def mock_projects():
    return [
        {"id": "proj1", "fields": {"project_id": "Project 1"}},
        {"id": "proj2", "fields": {"project_id": "Project 2"}},
    ]


@pytest.fixture
def mock_cities():
    return [
        {
            "fields": {
                "city_id": "city1",
                "city_name": "City 1",
                "country_name": "Country 1",
                "country_code_iso3": "CO1",
            }
        },
        {
            "fields": {
                "city_id": "city2",
                "city_name": "City 2",
                "country_name": "Country 2",
                "country_code_iso3": "CO2",
            }
        },
    ]


@pytest.fixture
def mock_indicator_df():
    df = gpd.GeoDataFrame(
        {
            "the_geom": [None],
            "geo_id": ["geo1"],
            "geo_level": ["ADM"],
            "value": [10.0],
            "indicator_version": [0],
            "creation_date": ["2023-01-01 23:00:00"],
            "city_id": ["city1"],
        },
        geometry="the_geom",
        crs="EPSG:4326",
    )
    df["creation_date"] = pd.to_datetime(df["creation_date"])
    return df


# Test Cases


@pytest.mark.unit
class TestListIndicators:
    @patch("app.services.indicators_service.fetch_indicators")
    @patch("app.services.indicators_service.fetch_datasets")
    @patch("app.services.indicators_service.fetch_projects")
    def test_list_indicators(
        self,
        mock_fetch_projects,
        mock_fetch_datasets,
        mock_fetch_indicators,
        mock_indicators,
        mock_datasets,
        mock_projects,
    ):
        mock_fetch_indicators.return_value = mock_indicators
        mock_fetch_datasets.return_value = mock_datasets
        mock_fetch_projects.return_value = mock_projects

        result = list_indicators()
        assert len(result) == 2
        assert result[0]["indicator_id"] == "IND_1"
        assert result[0]["data_sources_link"] == ["Dataset 1"]
        assert result[0]["projects"] == ["Project 1"]
        assert result[1]["indicator_id"] == "IND_2"
        assert result[1]["data_sources_link"] == ["Dataset 2"]
        assert result[1]["projects"] == ["Project 2"]


@pytest.mark.unit
class TestListIndicatorThemes:
    @patch("app.services.indicators_service.fetch_indicators")
    def test_list_indicators_themes(self, mock_fetch_indicators, mock_indicators):
        mock_fetch_indicators.return_value = mock_indicators
        result = list_indicators_themes()
        assert result == {"Theme 1", "Theme 2", "Theme 3"}


@pytest.mark.unit
class TestGetCitiesByIndicatorId:
    @patch("app.services.indicators_service.read_carto")
    @patch("app.services.indicators_service.fetch_cities")
    @patch("app.services.indicators_service.fetch_indicators")
    def test_get_cities_by_indicator_id_empty(
        self,
        mock_fetch_indicators,
        mock_fetch_cities,
        mock_read_carto,
        mock_cities,
        mock_indicators,
    ):
        mock_read_carto.return_value = pd.DataFrame()
        mock_fetch_cities.return_value = mock_cities
        mock_fetch_indicators.return_value = mock_indicators

        result = get_cities_by_indicator_id("IND_1")

        assert result == []


@pytest.mark.unit
class TestGetMetadataByIndicatorId:
    @patch("app.services.indicators_service.fetch_first_indicator")
    def test_get_metadata_by_indicator_id_not_found(
        self, mock_fetch_first_indicator
    ):
        mock_fetch_first_indicator.return_value = None
        result = get_metadata_by_indicator_id("nonexistent_indicator")
        assert result == {}


@pytest.mark.unit
class TestGetCityIndicatorByIds:
    @patch("app.services.indicators_service.read_carto")
    @patch("app.services.indicators_service.fetch_cities")
    @patch("app.services.indicators_service.fetch_indicators")
    def test_get_city_indicator_by_indicator_id_and_city_id_not_found(
        self,
        mock_fetch_indicators,
        mock_fetch_cities,
        mock_read_carto,
        mock_cities,
        mock_indicators,
    ):
        mock_read_carto.return_value = pd.DataFrame()
        mock_fetch_cities.return_value = mock_cities
        mock_fetch_indicators.return_value = mock_indicators

        result = get_city_indicator_by_indicator_id_and_city_id(
            "nonexistent_indicator", "nonexistent_city"
        )

        assert result == {}
