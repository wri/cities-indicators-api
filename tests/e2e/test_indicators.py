import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError


from app.main import app
from app.schemas.indicators_schema import (
    CitiesByIndicatorIdResponse,
    IndicatorsResponse,
    IndicatorsThemesResponse,
    IndicatorValueResponse,
    MetadataByIndicatorIdResponse,
)

client = TestClient(app)


@pytest.mark.e2e
class TestListIndicators:
    def test_list_indicators_themes(self):
        response = client.get("/indicators/themes")
        assert response.status_code == 200

        response_data = response.json()
        try:
            IndicatorsThemesResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match IndicatorsThemesResponse model: {e}")

        assert "Biodiversity" in response_data["themes"]

    def test_list_indicators_with_unknown_project_filter(self):
        PROJECT = "unknownproject"
        response = client.get(f"/indicators?project={PROJECT}")
        assert response.status_code == 404
        assert response.json() == {"detail": "No indicators found"}


@pytest.mark.e2e
class TestGetIndicators:
    def test_get_cities_by_indicator_id(self):
        INDICATOR_ID = "ACC_1_OpenSpaceHectaresper1000people2022"
        response = client.get(f"/indicators/{INDICATOR_ID}")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CitiesByIndicatorIdResponse(**response_data)
        except ValidationError as e:
            pytest.fail(
                f"Response did not match CitiesByIndicatorIdResponse model: {e}"
            )

    def test_get_metadata_by_indicator_id(self):
        INDICATOR_ID = "ACC_1_OpenSpaceHectaresper1000people2022"
        response = client.get(f"/indicators/metadata/{INDICATOR_ID}")
        assert response.status_code == 200

        response_data = response.json()

        try:
            MetadataByIndicatorIdResponse(**response_data)
        except ValidationError as e:
            pytest.fail(
                f"Response did not match MetadataByIndicatorIdResponse model: {e}"
            )

    def test_get_metadata_with_unknown_indicator_id(self):
        INDICATOR_ID = "unknownindicatorid"
        response = client.get(f"/indicators/metadata/{INDICATOR_ID}")
        assert response.status_code == 404
        assert response.json() == {"detail": "No indicators metadata found"}

    def test_get_city_indicator_by_indicator_id_and_city_id(self):
        INDICATOR_ID = "ACC_1_OpenSpaceHectaresper1000people2022"
        CITY_ID = "ARG-Mendoza"
        response = client.get(f"/indicators/{INDICATOR_ID}/{CITY_ID}")
        assert response.status_code == 200

        response_data = response.json()

        try:
            IndicatorValueResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match IndicatorValueResponse model: {e}")
