import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.const import API_VERSION
from app.main import app
from app.schemas.indicators import (
    CitiesByIndicatorIdResponse,
    IndicatorsResponse,
    IndicatorsThemesResponse,
    IndicatorValueResponse,
    MetadataByIndicatorIdResponse,
)

client = TestClient(app)


@pytest.mark.e2e
class TestListIndicators:
    def test_list_indicators_no_filter(self):
        response = client.get(f"/{API_VERSION}/indicators")
        assert response.status_code == 200

        response_data = response.json()
        try:
            IndicatorsResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match IndicatorsResponse model: {e}")

        indicators = response_data.get("indicators", [])
        assert isinstance(indicators[0].get("indicator_id"), str)

    def test_list_indicators_with_unknown_query_parameter(self):
        response = client.get(f"/{API_VERSION}/indicators?hello=true")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid query parameter: hello"}

    def test_list_indicators_with_project_filter(self):
        MOCK_PROJECT = "urbanshift"
        response = client.get(f"/{API_VERSION}/indicators?project={MOCK_PROJECT}")
        assert response.status_code == 200

        response_data = response.json()
        try:
            IndicatorsResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match IndicatorsResponse model: {e}")

        indicators = response_data.get("projects", [])
        for indicator in indicators:
            assert any(MOCK_PROJECT in indicator.get("projects", []))

    def test_list_indicators_themes(self):
        response = client.get(f"/{API_VERSION}/indicators/themes")
        assert response.status_code == 200

        response_data = response.json()
        try:
            IndicatorsThemesResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match IndicatorsThemesResponse model: {e}")

        assert "Biodiversity" in response_data["themes"]

    def test_list_indicators_with_unknown_project_filter(self):
        response = client.get(f"/{API_VERSION}/indicators?project=unknownproject")
        assert response.status_code == 404
        assert response.json() == {"detail": "No indicators found"}


@pytest.mark.e2e
class TestGetIndicators:
    def test_get_cities_by_indicator_id(self):
        MOCK_INDICATOR_ID = "ACC_1_OpenSpaceHectaresper1000people2022"
        response = client.get(f"/{API_VERSION}/indicators/{MOCK_INDICATOR_ID}")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CitiesByIndicatorIdResponse(**response_data)
        except ValidationError as e:
            pytest.fail(
                f"Response did not match CitiesByIndicatorIdResponse model: {e}"
            )

        cities = response_data.get("cities", [])
        for city in cities:
            assert MOCK_INDICATOR_ID == city.get(
                "indicator"
            ), f"City {city.get('geo_parent_name')} does not contain the indicator {MOCK_INDICATOR_ID}"

    def test_get_metadata_by_indicator_id(self):
        MOCK_INDICATOR_ID = "ACC_1_OpenSpaceHectaresper1000people2022"
        response = client.get(f"/{API_VERSION}/indicators/metadata/{MOCK_INDICATOR_ID}")
        assert response.status_code == 200

        response_data = response.json()
        assert response_data.get("indicator_id") == MOCK_INDICATOR_ID

        try:
            MetadataByIndicatorIdResponse(**response_data)
        except ValidationError as e:
            pytest.fail(
                f"Response did not match MetadataByIndicatorIdResponse model: {e}"
            )

    def test_get_metadata_with_unknown_indicator_id(self):
        response = client.get(f"/{API_VERSION}/indicators/metadata/unknownindicatorid")
        assert response.status_code == 404
        assert response.json() == {"detail": "No indicators metadata found"}

    def test_get_city_indicator_by_indicator_id_and_city_id(self):
        MOCK_INDICATOR_ID = "ACC_1_OpenSpaceHectaresper1000people2022"
        MOCK_CITY_ID = "ARG-Mendoza"
        response = client.get(
            f"/{API_VERSION}/indicators/{MOCK_INDICATOR_ID}/{MOCK_CITY_ID}"
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data.get("indicator") == MOCK_INDICATOR_ID
        assert response_data.get("geo_parent_name") == MOCK_CITY_ID

        try:
            IndicatorValueResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match IndicatorValueResponse model: {e}")
