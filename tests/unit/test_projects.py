from unittest.mock import patch

import pytest

from app.services.projects_service import list_projects


# Fixtures
@pytest.fixture
def mock_projects():
    return [
        {
            "id": "proj1",
            "fields": {
                "id": "Project 1",
                "name": ["Project One"],
                "status": "Active",
            },
        },
        {
            "id": "proj2",
            "fields": {
                "id": "Project 2",
                "name": ["Project Two"],
                "status": "Inactive",
            },
        },
    ]


# Test Cases
@pytest.mark.unit
class TestListProjects:
    @patch("app.services.projects_service.fetch_projects")
    def test_list_projects(self, mock_fetch_projects, mock_projects):
        mock_fetch_projects.return_value = mock_projects

        result = list_projects("cid")

        assert result[0]["id"] == "Project 1"
        assert result[0]["name"] == "Project One"
