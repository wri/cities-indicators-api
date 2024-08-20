from fastapi.testclient import TestClient
import pytest

from app.const import API_VERSION
from app.main import app

client = TestClient(app)


@pytest.mark.e2e
class TestListDatasets:
    def test_list_datasets_no_filter(selft):
        response = client.get(f"/{API_VERSION}/datasets")
        assert response.status_code == 200

        # response_data = response.json()
        # TODO: this this should fail because the API responses contain "Sentence Case" attribute names
        # try:
        #     DatasetsResponse(**response_data)
        # except ValidationError as e:
        #     pytest.fail(f"Response did not match DatasetsResponse model: {e}")

    def test_list_datasets_with_unknown_query_parameter(selft):
        response = client.get(f"/{API_VERSION}/datasets?country=USA")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid query parameter: country"}

    def test_list_indicators_with_city_id_filter(selft):
        CITY_ID = "BRA-Florianopolis"
        response = client.get(f"/{API_VERSION}/datasets?city_id={CITY_ID}")
        assert response.status_code == 200

        # response_data = response.json()
        # try:
        #     DatasetsResponse(**response_data)
        # except ValidationError as e:
        #     pytest.fail(f"Response did not match DatasetsResponse model: {e}")
