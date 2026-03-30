from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_for_activity_success():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Ensure cleanup for idempotence
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # cleanup
    activities[activity_name]["participants"].remove(email)


def test_signup_for_activity_already_signed_up():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    activity_name = "Programming Class"
    email = "testremove@mergington.edu"

    # Ensure participant exists before remove
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found():
    response = client.delete("/activities/Chess Club/participants", params={"email": "absent@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_activity_not_found():
    response = client.delete("/activities/Nonexistent/participants", params={"email": "absent@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"