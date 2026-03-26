import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: snapshot in-memory state before each test
    original = copy.deepcopy(activities)
    yield
    # Restore state so mutations don't bleed between tests
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    # Arrange: no preconditions needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all():
    # Arrange: expected activity names from seed data
    expected_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Music Band",
        "Debate Team",
        "Science Olympiad",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.json().keys() == expected_names


def test_get_activities_structure():
    # Arrange: required fields for each activity
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert required_fields.issubset(activity.keys())


# ---------------------------------------------------------------------------
# POST /activities/{name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants


def test_signup_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_signup_duplicate():
    # Arrange: michael is already in Chess Club seed data
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange: michael is enrolled in Chess Club in seed data
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_unregister_not_enrolled():
    # Arrange: this email is not in Chess Club
    activity_name = "Chess Club"
    email = "notenrolled@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root_redirect():
    # Arrange: disable redirect following so we can inspect the redirect itself
    no_redirect_client = TestClient(app, follow_redirects=False)

    # Act
    response = no_redirect_client.get("/")

    # Assert
    assert response.status_code in (301, 302, 307, 308)
    assert "/static/index.html" in response.headers["location"]
