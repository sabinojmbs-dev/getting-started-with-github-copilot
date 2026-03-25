"""
Tests for the Mergington High School Management System API
Using AAA (Arrange-Act-Assert) style.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Arrange: create a test client for FastAPI"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: reset activities to a stable baseline before each test"""
    state = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy(),
        }
        for name, activity in activities.items()
    }
    yield
    activities.clear()
    activities.update(state)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        payload = response.json()
        assert "Chess Club" in payload
        assert "Programming Class" in payload


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_rejected(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 409
        assert response.json()["detail"] == "Student already signed up"


class TestRemoveParticipant:
    def test_remove_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_delete_missing_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notpresent@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
