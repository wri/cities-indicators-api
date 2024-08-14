from pydantic import ValidationError
import pytest
from fastapi.testclient import TestClient
from app.const import API_VERSION
from app.main import app
from app.schemas.cities import CityListResponse

client = TestClient(app)

# Mock data for tests
mock_city_id = "BRA-Florianopolis"
mock_admin_level = "ADM4"
mock_country_code_iso3 = "BRA"
mock_projects = []


def validate_cities_response(response_data):
    # Validate response against CityListResponse model
    try:
        CityListResponse(**response_data)
    except ValidationError as e:
        pytest.fail(f"Response did not match CityListResponse model: {e}")


def test_list_cities_no_filter():
    response = client.get(f"/{API_VERSION}/cities")
    assert response.status_code == 200

    # Parse the response JSON
    response_data = response.json()

    # Validate response against CityListResponse model
    try:
        city_list = CityListResponse(**response_data)
    except ValidationError as e:
        pytest.fail(f"Response did not match CityListResponse model: {e}")

    # Assuming CityListResponse has a field like "cities" that is a list
    cities = city_list.cities

    # Assert that the first item's "city_id" is a string
    assert isinstance(cities[0].city_id, str)


def test_list_cities_with_unknown_query_parameter():
    response = client.get(f"/{API_VERSION}/cities?something=true")

    # Check the status code
    assert response.status_code == 400

    # Parse the response JSON
    response_data = response.json()

    # Assert the response content
    assert response_data == {"detail": "Invalid query parameter: something"}


def test_list_cities_with_single_projects_filter():
    MOCK_PROJECTS = ["cities4forests"]
    response = client.get(f"/{API_VERSION}/cities?projects={MOCK_PROJECTS[0]}")
    # Ensure the response status code is 200
    assert response.status_code == 200

    # Parse the response JSON
    response_data = response.json()

    validate_cities_response(response_data)

    # Ensure all cities' projects contain at least one of the mock_projects
    for city in response_data["cities"]:
        assert any(
            project in MOCK_PROJECTS for project in city["projects"]
        ), f"City {city.city_id} does not contain any of the projects in {MOCK_PROJECTS}"


def test_list_cities_with_multiple_projects_filter():
    MOCK_PROJECTS = ["deepdive", "urbanshift"]
    response = client.get(
        f"/{API_VERSION}/cities?projects={MOCK_PROJECTS[0]}&projects={MOCK_PROJECTS[1]}"
    )
    # Ensure the response status code is 200
    assert response.status_code == 200

    validate_cities_response(response.json())

    # Parse the response JSON
    response_data = response.json()
    # Ensure all cities' projects contain at least one of the mock_projects
    for city in response_data["cities"]:
        assert any(
            project in MOCK_PROJECTS for project in city["projects"]
        ), f"City {city.city_id} does not contain any of the projects in {MOCK_PROJECTS}"


def test_list_cities_with_multiple_projects_and_country_code_filter():
    MOCK_PROJECTS = ["deepdive", "urbanshift"]
    COUNTRY_CODE_ISO3 = "MEX"
    response = client.get(
        f"/{API_VERSION}/cities?projects={MOCK_PROJECTS[0]}&projects={MOCK_PROJECTS[1]}&country_code_iso3={COUNTRY_CODE_ISO3}"
    )
    # Ensure the response status code is 200
    assert response.status_code == 200

    validate_cities_response(response.json())

    # Parse the response JSON
    response_data = response.json()
    # Ensure all cities' projects contain at least one of the mock_projects
    for city in response_data["cities"]:
        assert any(
            project in MOCK_PROJECTS for project in city["projects"]
        ), f"City {city.city_id} does not contain any of the projects in {MOCK_PROJECTS}"
        assert city["country_code_iso3"] == COUNTRY_CODE_ISO3


def test_list_cities_with_unknown_project_filter():
    pass


# def test_list_cities_with_country_filter():
#     response = client.get(f"/v1/cities?country_code_iso3={mock_country_code_iso3}")
#     assert response.status_code == 200
#     assert "cities" in response.json()

# def test_get_city_by_city_id():
#     response = client.get(f"/v1/cities/{mock_city_id}")
#     assert response.status_code == 200
#     assert "city_id" in response.json()

# def test_get_city_indicators():
#     response = client.get(f"/v1/cities/{mock_city_id}/{mock_admin_level}")
#     assert response.status_code == 200
#     assert "geo_id" in response.json()

# def test_get_city_geometry():
#     response = client.get(f"/v1/cities/{mock_city_id}/{mock_admin_level}/geojson")
#     assert response.status_code == 200
#     assert "features" in response.json()

# def test_get_city_geometry_with_indicators():
#     response = client.get(f"/v1/cities/{mock_city_id}/{mock_admin_level}/geojson/indicators")
#     assert response.status_code == 200
#     assert "features" in response.json()
