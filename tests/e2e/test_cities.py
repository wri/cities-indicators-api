from pydantic import ValidationError
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.cities_schema import (
    City,
    CityBoundaryGeoJSON,
    CityIndicatorAdmin,
    CityList,
)

client = TestClient(app)


@pytest.mark.e2e
class TestListCities:
    def test_list_cities_no_filter(self):
        response = client.get("/cities")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityList(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityList model: {e}")

    def test_list_cities_with_unknown_query_parameter(self):
        response = client.get("/cities?something=true")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid query parameter: something"}

    def test_list_cities_with_single_projects_filter(self):
        response = client.get("/cities?projects=cities4forests")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityList(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityList model: {e}")

    def test_list_cities_with_multiple_projects_filter(self):
        PROJECTS = ["deepdive", "urbanshift"]
        response = client.get(f"/cities?projects={PROJECTS[0]}&projects={PROJECTS[1]}")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityList(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityList model: {e}")

    def test_list_cities_with_multiple_projects_and_country_code_filter(self):
        PROJECTS = ["deepdive", "urbanshift"]
        COUNTRY_CODE_ISO3 = "MEX"
        response = client.get(
            f"/cities?projects={PROJECTS[0]}&projects={PROJECTS[1]}&country_code_iso3={COUNTRY_CODE_ISO3}"
        )
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityList(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityList model: {e}")

    def test_list_cities_with_unknown_projects_filter(self):
        response = client.get("/cities?projects=unknownproject")
        assert response.status_code == 404
        assert response.json() == {"detail": "No cities found"}


@pytest.mark.e2e
class TestGetCities:
    def test_get_city_by_city_id(self):
        CITY_ID = "COD-Uvira"
        response = client.get(f"/cities/{CITY_ID}")
        assert response.status_code == 200

        response_data = response.json()

        try:
            City(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match City model: {e}")

    def test_get_city_by_city_id_with_unknown_city_id(self):
        CITY_ID = "unknowncityid"
        response = client.get(f"/cities/{CITY_ID}")
        assert response.status_code == 404
        assert response.json() == {"detail": "No city found"}

    def test_get_city_indicators(self):
        CITY_ID = "COD-Uvira"
        ADM_LEVEL = "ADM3"
        response = client.get(f"/cities/{CITY_ID}/{ADM_LEVEL}")
        assert response.status_code == 200

        response_data = response.json()

        try:
            CityIndicatorAdmin(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityIndicatorAdmin model: {e}")

    def test_get_city_indicators_with_unknown_city_id_and_admin_level(self):
        CITY_ID = "unknowncityid"
        ADM_LEVEL = "unknownadminlevel"
        response = client.get(f"/cities/{CITY_ID}/{ADM_LEVEL}")
        assert response.status_code == 404
        assert response.json() == {"detail": "No indicators found"}
