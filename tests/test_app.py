import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = {
        name: {
            key: value[:] if isinstance(value, list) else value
            for key, value in activity.items()
        }
        for name, activity in activities.items()
    }
    yield
    activities.clear()
    activities.update({
        name: {
            key: value[:] if isinstance(value, list) else value
            for key, value in activity.items()
        }
        for name, activity in original_state.items()
    })


def test_get_activities_returns_seed_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["description"].startswith("Learn strategies")


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )

    assert response.status_code == 200
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email_from_activity(client):
    response = client.delete(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"


def test_unregister_unknown_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/signup?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unknown_activity_returns_404(client):
    response = client.get("/activities/Unknown%20Activity")

    assert response.status_code == 404
