import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.unit
def test_get_cities():
    """Test /cities"""
    response = client.get("/cities")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_city_by_id():
    """Test /cities/{city_id}"""
    response = client.get("/cities/ARG-Buenos_Aires")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_city_by_id_and_admin_level():
    """Test /cities/{city_id}/{admin_level}"""
    response = client.get("/cities/ARG-Buenos_Aires/ADM2union")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_city_geometry_with_indicators_geojson():
    """
    Test /cities/{city_id}/indicators/geojson
    Test /cities/{city_id}/indicators/geojson?indicator_id={indicator_id}
    Test /cities/{city_id}/indicators/geojson?admin_level={admin_level}
    Test /cities/{city_id}/indicators/geojson?indicator_id={indicator_id}&admin_level={admin_level}
    """
    response = client.get("/cities/ARG-Buenos_Aires/indicators/geojson")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_city_geometry_with_indicators_csv():
    """
    Test /cities/{city_id}/indicators/csv
    Test /cities/{city_id}/indicators/csv?indicator_id={indicator_id}
    Test /cities/{city_id}/indicators/csv?admin_level={admin_level}
    Test /cities/{city_id}/indicators/csv?indicator_id={indicator_id}&admin_level={admin_level}
    """
    response = client.get("/cities/ARG-Buenos_Aires/indicators/csv")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_city_geometry_geojson():
    """Test /cities/{city_id}/{admin_level}/geojson"""
    response = client.get("/cities/ARG-Buenos_Aires/ADM2union/geojson")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_city_indicator_stats():
    """
    Test /cities/{city_id}/indicators/stats
    Test /cities/{city_id}/indicators/stats?indicator_id={indicator_id}
    Test /cities/{city_id}/indicators/stats?admin_level={admin_level}
    Test /cities/{city_id}/indicators/stats?indicator_id={indicator_id}&admin_level={admin_level}
    """
    response = client.get("/cities/ARG-Buenos_Aires/indicators/stats")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_datasets():
    """
    Test /datasets
    Test /datasets?city_id={city_id}
    Test /datasets?layer_id={layer_id}
    Test /datasets?layer_id={layer_id_1}&layer_id={layer_id_2}
    Test /datasets?city_id={city_id}&layer_id={layer_id_1}&layer_id={layer_id_2}
    """
    response = client.get("/datasets")
    assert response.status_code == 200
    response = client.get("/datasets?city_id=ARG-Buenos_Aires")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_indicators():
    """
    Test /indicators
    Test /indicators?project={project_id}
    Test /indicators?city_id={city_id}
    Test /indicators?city_id={city_id_1}&city_id={city_id_2}
    Test /indicators?project={project_id}&city_id={city_id_1}&city_id={city_id_2}
    """
    response = client.get("/indicators")
    assert response.status_code == 200
    response = client.get("/indicators?city_id=ARG-Buenos_Aires")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_indicator_themes():
    """Test /indicators/themes"""
    response = client.get("/indicators/themes")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_cities_with_indicator():
    """Test /indicators/{indicator_id}"""
    response = client.get("/indicators/ACC_1_OpenSpaceHectaresper1000people2022")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_indicator_metadata():
    """Test /indicators/metadata/{indicator_id}"""
    response = client.get(
        "/indicators/metadata/ACC_1_OpenSpaceHectaresper1000people2022"
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_get_indicator_data_for_city():
    """Test /indicators/{indicator_id}/{city_id}"""
    response = client.get(
        "/indicators/ACC_1_OpenSpaceHectaresper1000people2022/ARG-Buenos_Aires"
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_get_layer_for_city():
    """Test /layers/{layer_id}/{city_id}"""
    response = client.get("/layers/albedo/ARG-Buenos_Aires")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_projects():
    """Test /projects"""
    response = client.get("/projects")
    assert response.status_code == 200
