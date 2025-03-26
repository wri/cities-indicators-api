from unittest.mock import patch

import geopandas as gpd
import pandas as pd
import pytest

from app.services.indicators_service import (
    get_cities_by_indicator_id,
    get_city_indicator_by_indicator_id_and_city_id,
    get_metadata_by_indicator_id,
    list_indicators,
    list_indicators_themes,
)

# Fixtures


@pytest.fixture
def mock_layers():
    return [
        {
            "id": "layer1",
            "fields": {
                "id": "layer_1",
            },
        },
        {
            "id": "layer2",
            "fields": {
                "id": "layer_2",
            },
        },
    ]


@pytest.fixture
def mock_indicators():
    return [
        {
            "id": "ind1",
            "fields": {
                "data_sources_link": ["ds1"],
                "projects": ["proj1"],
                "themes": ["Theme 1", "Theme 2"],
                "id": "IND_1",
                "name": "Indicator 1",
                "unit": "unit1",
            },
        },
        {
            "id": "ind2",
            "fields": {
                "data_sources_link": ["ds2"],
                "projects": ["proj2"],
                "themes": ["Theme 2", "Theme 3"],
                "id": "IND_2",
                "name": "Indicator 2",
                "unit": "unit2",
            },
        },
    ]


@pytest.fixture
def mock_datasets():
    return [
        {"id": "ds1", "fields": {"name": "Dataset 1"}},
        {"id": "ds2", "fields": {"name": "Dataset 2"}},
    ]


@pytest.fixture
def mock_projects():
    return [
        {"id": "pr1", "fields": {"id": "project1"}},
        {"id": "pr2", "fields": {"id": "project2"}},
    ]


@pytest.fixture
def mock_cities():
    return [
        {
            "id": "ct1",
            "fields": {
                "id": "city1",
                "name": "City 1",
            },
        },
        {
            "id": "ct2",
            "fields": {
                "id": "city2",
                "name": "City 2",
            },
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
    @patch("app.services.indicators_service.fetch_layers")
    @patch("app.services.indicators_service.fetch_cities")
    def test_list_indicators(
        self,
        mock_fetch_cities,
        mock_fetch_layers,
        mock_fetch_projects,
        mock_fetch_datasets,
        mock_fetch_indicators,
        mock_indicators,
        mock_datasets,
        mock_projects,
        mock_layers,
        mock_cities,
    ):
        mock_fetch_indicators.return_value = mock_indicators
        mock_fetch_datasets.return_value = mock_datasets
        mock_fetch_projects.return_value = mock_projects
        mock_fetch_layers.return_value = mock_layers
        mock_fetch_cities.return_value = mock_cities

        result = list_indicators("cid")
        assert len(result) == 2
        assert result[0]["id"] == "IND_1"
        assert result[0]["data_sources_link"] == ["Dataset 1"]
        # assert result[0]["projects"] == ["proj1"]
        assert result[1]["id"] == "IND_2"
        assert result[1]["data_sources_link"] == ["Dataset 2"]
        # assert result[1]["projects"] == ["proj2"]


@pytest.mark.unit
class TestListIndicatorThemes:
    @patch("app.services.indicators_service.fetch_indicators")
    def test_list_indicators_themes(self, mock_fetch_indicators, mock_indicators):
        mock_fetch_indicators.return_value = mock_indicators
        result = list_indicators_themes()
        assert result == {"Theme 1", "Theme 2", "Theme 3"}


@pytest.mark.unit
class TestGetCitiesByIndicatorId:
    @patch("app.services.indicators_service.query_carto")
    @patch("app.services.indicators_service.fetch_cities")
    @patch("app.services.indicators_service.fetch_indicators")
    def test_get_cities_by_indicator_id_empty(
        self,
        mock_fetch_indicators,
        mock_fetch_cities,
        mock_query_carto,
        mock_cities,
        mock_indicators,
    ):
        mock_query_carto.return_value = pd.DataFrame()
        mock_fetch_cities.return_value = mock_cities
        mock_fetch_indicators.return_value = mock_indicators

        result = get_cities_by_indicator_id("IND_1")

        assert result == []


@pytest.mark.unit
class TestGetMetadataByIndicatorId:
    @patch("app.services.indicators_service.fetch_first_indicator")
    def test_get_metadata_by_indicator_id_not_found(self, mock_fetch_first_indicator):
        mock_fetch_first_indicator.return_value = None
        result = get_metadata_by_indicator_id("nonexistent_indicator")
        assert result == {}


@pytest.mark.unit
class TestGetCityIndicatorByIds:
    @patch("app.services.indicators_service.query_carto")
    @patch("app.services.indicators_service.fetch_cities")
    @patch("app.services.indicators_service.fetch_indicators")
    def test_get_city_indicator_by_indicator_id_and_city_id_not_found(
        self,
        mock_fetch_indicators,
        mock_fetch_cities,
        mock_query_carto,
        mock_cities,
        mock_indicators,
    ):
        mock_query_carto.return_value = pd.DataFrame()
        mock_fetch_cities.return_value = mock_cities
        mock_fetch_indicators.return_value = mock_indicators

        result = get_city_indicator_by_indicator_id_and_city_id(
            "nonexistent_indicator", "nonexistent_city"
        )

        assert result == {}
