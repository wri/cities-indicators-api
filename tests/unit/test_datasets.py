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
                "layer_id": "layer_1",
            },
        },
        {
            "id": "layer2",
            "fields": {
                "layer_id": "layer_2",
            },
        },
    ]


@pytest.fixture
def mock_datasets():
    return [
        {
            "id": "ds1",
            "fields": {
                "dataset_name": "Dataset 1",
                "Indicators": ["ind1", "ind2"],
                "city_id": ["city1"],
                "Layer": ["layer1"],
            },
        },
        {
            "id": "ds2",
            "fields": {
                "dataset_name": "Dataset 2",
                "Indicators": ["ind3"],
                "city_id": ["city2"],
                "Layer": ["layer1", "layer2"],
            },
        },
    ]


@pytest.fixture
def mock_cities():
    return [
        {
            "id": "city1",
            "fields": {
                "city_id": "city1",
            },
        },
        {
            "id": "city2",
            "fields": {
                "city_id": "city2",
            },
        },
    ]


@pytest.fixture
def mock_indicators():
    return [
        {
            "id": "ind1",
            "fields": {
                "indicator_label": "Indicator 1",
            },
        },
        {
            "id": "ind2",
            "fields": {
                "indicator_label": "Indicator 2",
            },
        },
        {
            "id": "ind3",
            "fields": {
                "indicator_label": "Indicator 3",
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
        assert result[0]["dataset_name"] == "Dataset 1"
        assert result[0]["Indicators"] == ["Indicator 1", "Indicator 2"]
        assert result[0]["city_ids"] == ["city1"]
        assert result[1]["dataset_name"] == "Dataset 2"
        assert result[1]["Indicators"] == ["Indicator 3"]
        assert result[1]["city_ids"] == ["city2"]

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

        assert result[0]["dataset_name"] == "Dataset 1"
        assert result[0]["Indicators"] == ["Indicator 1", "Indicator 2"]
        assert result[0]["city_ids"] == ["city1"]
