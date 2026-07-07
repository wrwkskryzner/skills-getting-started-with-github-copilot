import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


BASE_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(BASE_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(BASE_ACTIVITIES))


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant_to_activity(client):
    response = client.post(
        "/activities/Chess Club/signup?email=student@example.com"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@example.com for Chess Club"
    assert "student@example.com" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity(client):
    email = "student@example.com"
    app_module.activities["Chess Club"]["participants"].append(email)

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Removed {email} from Chess Club"


def test_remove_participant_returns_404_when_activity_missing(client):
    response = client.delete("/activities/Unknown Activity/participants/student@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_returns_404_when_participant_missing(client):
    response = client.delete("/activities/Chess Club/participants/not-a-member@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
