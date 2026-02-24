"""
Tests for the Mergington High School API.

Each test follows the Arrange-Act-Assert (AAA) pattern:
  - Arrange: set up data and preconditions
  - Act:     call the API endpoint
  - Assert:  verify the response
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict to its original state after every test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities():
    # Arrange - no setup required; activities are pre-populated at startup

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert activity_name in response.json()["message"]


def test_signup_already_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    email = "toleave@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert activity_name in response.json()["message"]


def test_unregister_not_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
