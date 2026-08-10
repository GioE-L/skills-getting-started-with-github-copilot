from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "teststudent@mergington.edu"
    activity = quote("Chess Club", safe="")
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate_returns_400():
    email = "duplicate@mergington.edu"
    activity = quote("Chess Club", safe="")

    first_response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert first_response.status_code == 200

    duplicate_response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_delete_participant_removes_participant():
    participant_email = "michael@mergington.edu"
    activity = quote("Chess Club", safe="")
    participant = quote(participant_email, safe="")

    response = client.delete(f"/activities/{activity}/participants/{participant}")

    assert response.status_code == 200
    assert participant_email not in activities["Chess Club"]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_delete_nonexistent_participant_returns_404():
    participant_email = "notfound@mergington.edu"
    activity = quote("Chess Club", safe="")
    participant = quote(participant_email, safe="")

    response = client.delete(f"/activities/{activity}/participants/{participant}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
