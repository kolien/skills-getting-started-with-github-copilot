"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Join the school soccer team and compete in inter-school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and participate in friendly games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Explore acting, theater production, and perform in school plays",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["emily@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Paint, draw, and create various art projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "charlotte@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["benjamin@mergington.edu", "amelia@mergington.edu"]
        },
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
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are returned
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Drama Club" in data
        assert len(data) == 9
        
    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        soccer = data["Soccer Team"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)
        
    def test_activity_has_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        soccer = data["Soccer Team"]
        assert len(soccer["participants"]) == 2
        assert "lucas@mergington.edu" in soccer["participants"]
        assert "mia@mergington.edu" in soccer["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Soccer Team"]["participants"]
        
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
        
    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        email = "lucas@mergington.edu"
        response = client.post(
            f"/activities/Soccer Team/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
        
    def test_signup_with_special_characters(self, client):
        """Test signup with email containing special characters"""
        from urllib.parse import quote
        email = "test+special@mergington.edu"
        response = client.post(
            f"/activities/Drama Club/signup?email={quote(email)}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Drama Club"]["participants"]
        
    def test_signup_multiple_students(self, client):
        """Test signup for multiple students"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Chess Club/signup?email={email}"
            )
            assert response.status_code == 200
            
        # Verify all participants were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "lucas@mergington.edu"
        
        # Verify participant is registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Soccer Team"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Soccer Team/signup?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Soccer Team"]["participants"]
        
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
        
    def test_unregister_not_registered(self, client):
        """Test unregistration when student is not registered"""
        email = "notregistered@mergington.edu"
        response = client.delete(
            f"/activities/Soccer Team/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
        
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signup and unregister"""
        email = "workflow@mergington.edu"
        activity = "Art Studio"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify registration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
        
    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple participants"""
        activity = "Basketball Club"
        
        # Get original participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        original_participants = activities_data[activity]["participants"].copy()
        
        # Unregister all original participants
        for email in original_participants:
            response = client.delete(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
            
        # Verify all were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in original_participants:
            assert email not in activities_data[activity]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity limits"""
    
    def test_activities_have_max_participants(self, client):
        """Test that all activities have max_participants defined"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "max_participants" in activity_details
            assert activity_details["max_participants"] > 0
            
    def test_participant_count(self, client):
        """Test that participant count is tracked correctly"""
        response = client.get("/activities")
        data = response.json()
        
        initial_count = len(data["Science Club"]["participants"])
        
        # Add a participant
        client.post("/activities/Science Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        new_count = len(data["Science Club"]["participants"])
        
        assert new_count == initial_count + 1
