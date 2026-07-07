from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_remove_participant_from_activity():
    activity_name = "Chess Club"
    email = "student@example.com"

    activities[activity_name]["participants"].append(email)

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_remove_participant_returns_404_when_activity_missing():
    response = client.delete("/activities/Unknown Activity/participants/student@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
