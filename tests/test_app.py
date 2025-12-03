import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer training and matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill development and intramural basketball games",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "william@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and school play productions",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking, argumentation, and tournament prep",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for competitions",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 12,
            "participants": ["eli@mergington.edu", "zoe@mergington.edu"]
        }
    })
    yield


class TestRoot:
    def test_root_redirects_to_static(self):
        """Test that the root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_get_activities_returns_all_activities(self):
        """Test that /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)

    def test_get_activities_contains_initial_participants(self):
        """Test that activities have the expected initial participants."""
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    def test_signup_new_participant(self):
        """Test signing up a new participant for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_participant(self):
        """Test that signing up a duplicate participant fails."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_multiple_different_activities(self):
        """Test that a student can sign up for multiple activities."""
        student = "alice@mergington.edu"
        response1 = client.post(
            f"/activities/Chess Club/signup?email={student}"
        )
        assert response1.status_code == 200
        response2 = client.post(
            f"/activities/Programming Class/signup?email={student}"
        )
        assert response2.status_code == 200
        assert student in activities["Chess Club"]["participants"]
        assert student in activities["Programming Class"]["participants"]


class TestUnregister:
    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a non-existent participant fails."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_from_nonexistent_activity(self):
        """Test unregistering from a non-existent activity fails."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_all_participants(self):
        """Test unregistering all participants from an activity."""
        participants = activities["Chess Club"]["participants"].copy()
        for email in participants:
            response = client.delete(
                f"/activities/Chess Club/unregister?email={email}"
            )
            assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == 0

    def test_signup_after_unregister(self):
        """Test that a participant can sign up again after unregistering."""
        email = "michael@mergington.edu"
        # Unregister
        response1 = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        # Re-signup
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 200
        assert email in activities["Chess Club"]["participants"]


class TestIntegration:
    def test_full_signup_and_unregister_flow(self):
        """Test the complete flow of signup and unregister."""
        email = "bob@mergington.edu"
        activity = "Programming Class"
        
        # Verify not registered initially
        assert email not in activities[activity]["participants"]
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        assert email not in activities[activity]["participants"]

    def test_activity_availability_after_operations(self):
        """Test that availability calculation is correct after signup/unregister."""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        initial_spots = chess_club["max_participants"] - len(chess_club["participants"])
        
        # Sign up
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        new_spots = data["Chess Club"]["max_participants"] - len(data["Chess Club"]["participants"])
        assert new_spots == initial_spots - 1
        
        # Unregister
        client.delete("/activities/Chess Club/unregister?email=test@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        final_spots = data["Chess Club"]["max_participants"] - len(data["Chess Club"]["participants"])
        assert final_spots == initial_spots
