from pydantic import ValidationError
import pytest
from fastapi.testclient import TestClient
from app.const import API_VERSION
from app.main import app
from app.schemas.cities import (
    CityDetail,
    CityIndicatorsDetail,
    CityListResponse,
    GeoJSONFeatureCollection,
)

client = TestClient(app)


@pytest.mark.e2e
class TestListCities:
    def test_list_cities_no_filter(self):
        response = client.get(f"/{API_VERSION}/cities")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityListResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityListResponse model: {e}")

        cities = response_data.get("cities", [])
        assert isinstance(cities[0].get("city_id"), str)

    def test_list_cities_with_unknown_query_parameter(self):
        response = client.get(f"/{API_VERSION}/cities?something=true")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid query parameter: something"}

    def test_list_cities_with_single_projects_filter(self):
        MOCK_PROJECTS = ["cities4forests"]
        response = client.get(f"/{API_VERSION}/cities?projects={MOCK_PROJECTS[0]}")
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityListResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityListResponse model: {e}")

        cities = response_data.get("cities", [])
        for city in cities:
            assert any(
                project in MOCK_PROJECTS for project in city.get("projects", [])
            ), f"City {city.get('city_id')} does not contain any of the projects in {MOCK_PROJECTS}"

    def test_list_cities_with_multiple_projects_filter(self):
        MOCK_PROJECTS = ["deepdive", "urbanshift"]
        response = client.get(
            f"/{API_VERSION}/cities?projects={MOCK_PROJECTS[0]}&projects={MOCK_PROJECTS[1]}"
        )
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityListResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityListResponse model: {e}")

        cities = response_data.get("cities", [])
        for city in cities:
            assert any(
                project in MOCK_PROJECTS for project in city.get("projects", [])
            ), f"City {city.get('city_id')} does not contain any of the projects in {MOCK_PROJECTS}"

    def test_list_cities_with_multiple_projects_and_country_code_filter(self):
        MOCK_PROJECTS = ["deepdive", "urbanshift"]
        MOCK_COUNTRY_CODE_ISO3 = "MEX"
        response = client.get(
            f"/{API_VERSION}/cities?projects={MOCK_PROJECTS[0]}&projects={MOCK_PROJECTS[1]}&country_code_iso3={MOCK_COUNTRY_CODE_ISO3}"
        )
        assert response.status_code == 200

        response_data = response.json()
        try:
            CityListResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityListResponse model: {e}")

        cities = response_data.get("cities", [])
        for city in cities:
            assert any(
                project in MOCK_PROJECTS for project in city.get("projects", [])
            ), f"City {city.get('city_id')} does not include any of the projects: {MOCK_PROJECTS}"
            assert city.get("country_code_iso3") == MOCK_COUNTRY_CODE_ISO3

    def test_list_cities_with_unknown_projects_filter(self):
        response = client.get(f"/{API_VERSION}/cities?projects=unknownproject")
        assert response.status_code == 404
        assert response.json() == {"detail": "No cities found"}


@pytest.mark.e2e
class TestGetCities:
    def test_get_city_by_city_id(self):
        MOCK_CITY_ID = "COD-Uvira"
        response = client.get(f"/{API_VERSION}/cities/{MOCK_CITY_ID}")
        assert response.status_code == 200

        response_data = response.json()
        assert response_data.get("city_id") == MOCK_CITY_ID

        try:
            CityDetail(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityDetail model: {e}")

    def test_get_city_by_city_id_with_unknown_city_id(self):
        MOCK_CITY_ID = "unknowncityid"
        response = client.get(f"/{API_VERSION}/cities/{MOCK_CITY_ID}")
        assert response.status_code == 404

    def test_get_city_indicators(self):
        MOCK_CITY_ID = "COD-Uvira"
        MOCK_ADM_LEVEL = "ADM3"
        response = client.get(f"/{API_VERSION}/cities/{MOCK_CITY_ID}/{MOCK_ADM_LEVEL}")
        assert response.status_code == 200

        response_data = response.json()
        assert response_data.get("geo_parent_name") == MOCK_CITY_ID

        try:
            CityIndicatorsDetail(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match CityIndicatorsDetail model: {e}")

    def test_get_city_indicators_with_unknown_city_id_and_admin_level(self):
        response = client.get(f"/{API_VERSION}/cities/unknowncityid/unknownadminlevel")
        assert response.status_code == 404

    def test_get_city_geometry(self):
        MOCK_CITY_ID = "COD-Uvira"
        MOCK_ADM_LEVEL = "ADM3"
        response = client.get(
            f"/{API_VERSION}/cities/{MOCK_CITY_ID}/{MOCK_ADM_LEVEL}/geojson"
        )
        assert response.status_code == 200

        response_data = response.json()
        assert (
            response_data.get("features", [{}])[0]
            .get("properties", {})
            .get("geo_parent_name")
            == MOCK_CITY_ID
        )

        try:
            GeoJSONFeatureCollection(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match GeoJSONFeatureCollection model: {e}")

    def test_get_city_geometry_with_unknown_city_id_and_admin_level(self):
        response = client.get(
            f"/{API_VERSION}/cities/unknowncityid/unknownadminlevel/geojson"
        )
        assert response.status_code == 404

    def test_get_city_geometry(self):
        MOCK_CITY_ID = "COD-Uvira"
        MOCK_ADM_LEVEL = "ADM3"
        response = client.get(
            f"/{API_VERSION}/cities/{MOCK_CITY_ID}/{MOCK_ADM_LEVEL}/geojson/indicators"
        )
        assert response.status_code == 200

        response_data = response.json()
        assert (
            response_data.get("features", [{}])[0]
            .get("properties", {})
            .get("geo_parent_name")
            == MOCK_CITY_ID
        )

        try:
            GeoJSONFeatureCollection(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match GeoJSONFeatureCollection model: {e}")

    def test_get_city_geometry_with_indicators_with_unknown_city_id_and_admin_level(
        self,
    ):
        response = client.get(
            f"/{API_VERSION}/cities/unknowncityid/unknownadminlevel/geojson/indicators"
        )
        assert response.status_code == 404
