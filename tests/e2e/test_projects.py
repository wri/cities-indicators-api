import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError


from app.main import app
from app.schemas.projects_schema import ListProjectsResponse

client = TestClient(app)


@pytest.mark.e2e
class TestListProjects:
    def test_list_projects_no_filter(self):
        response = client.get("/projects")
        assert response.status_code == 200

        response_data = response.json()
        try:
            ListProjectsResponse(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response did not match ListProjectsResponse model: {e}")
