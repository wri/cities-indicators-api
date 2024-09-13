import pytest
from unittest.mock import patch

from app.services.datasets_service import list_datasets


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
def mock_datasets():
    return [
        {
            "id": "ds1",
            "fields": {
                "name": "Dataset 1",
                "indicators": ["ind1", "ind2"],
                "city_ids": ["city1"],
                "layers": ["layer1"],
            },
        },
        {
            "id": "ds2",
            "fields": {
                "name": "Dataset 2",
                "indicators": ["ind3"],
                "city_ids": ["city2"],
                "layers": ["layer1", "layer2"],
            },
        },
    ]


@pytest.fixture
def mock_cities():
    return [
        {
            "id": "city1",
            "fields": {
                "id": "city1",
            },
        },
        {
            "id": "city2",
            "fields": {
                "id": "city2",
            },
        },
    ]


@pytest.fixture
def mock_indicators():
    return [
        {
            "id": "0",
            "fields": {
                "id": "ind1",
                "name": "Indicator 1",
            },
        },
        {
            "id": "1",
            "fields": {
                "id": "ind2",
                "name": "Indicator 2",
            },
        },
        {
            "id": "2",
            "fields": {
                "id": "ind3",
                "name": "Indicator 3",
            },
        },
    ]


# Test Cases
@pytest.mark.unit
class TestListDatasets:
    @patch("app.services.datasets_service.fetch_datasets")
    @patch("app.services.datasets_service.fetch_cities")
    @patch("app.services.datasets_service.fetch_indicators")
    @patch("app.services.datasets_service.fetch_layers")
    def test_list_datasets(
        self,
        mock_fetch_layers,
        mock_fetch_indicators,
        mock_fetch_cities,
        mock_fetch_datasets,
        mock_datasets,
        mock_cities,
        mock_indicators,
        mock_layers,
    ):
        mock_fetch_datasets.return_value = mock_datasets
        mock_fetch_cities.return_value = mock_cities
        mock_fetch_indicators.return_value = mock_indicators
        mock_fetch_layers.return_value = mock_layers

        result = list_datasets(city_id=None)

        assert len(result) == 2
        assert result[0]["name"] == "Dataset 1"
        assert result[1]["name"] == "Dataset 2"

    @patch("app.services.datasets_service.fetch_datasets")
    @patch("app.services.datasets_service.fetch_cities")
    @patch("app.services.datasets_service.fetch_indicators")
    @patch("app.services.datasets_service.fetch_layers")
    def test_list_datasets_filtered_by_city(
        self,
        mock_fetch_layers,
        mock_fetch_indicators,
        mock_fetch_cities,
        mock_fetch_datasets,
        mock_datasets,
        mock_cities,
        mock_indicators,
        mock_layers,
    ):
        mock_fetch_datasets.return_value = mock_datasets
        mock_fetch_cities.return_value = mock_cities
        mock_fetch_indicators.return_value = mock_indicators
        mock_fetch_layers.return_value = mock_layers

        result = list_datasets(city_id=None)

        assert result[0]["name"] == "Dataset 1"
