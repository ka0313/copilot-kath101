"""
Integration tests for FastAPI Activities API using AAA (Arrange-Act-Assert) pattern.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Fresh activities data is ready via fixture
        Act: Make GET request to /activities
        Assert: Response should be 200 and contain all activities
        """
        # Arrange
        expected_activity_count = len(fresh_activities)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_returns_correct_structure(self, client, fresh_activities):
        """
        Test that each activity has required fields.
        
        Arrange: Fresh activities data is ready via fixture
        Act: Make GET request to /activities
        Assert: Each activity should have description, schedule, max_participants, participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields, \
                f"Activity '{activity_name}' missing or has extra fields"
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestRootRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client, fresh_activities):
        """
        Test that GET / redirects to /static/index.html.
        
        Arrange: Client is ready
        Act: Make GET request to / with follow_redirects=False
        Assert: Response should be 307 (temporary redirect)
        """
        # Arrange
        # (client fixture is ready)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, fresh_activities):
        """
        Test successful signup for an activity.
        
        Arrange: Valid activity name and new email address
        Act: Make POST request to signup
        Assert: Response should be 200 and email should be in participants
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        
        # Verify participant was added
        updated_activities = client.get("/activities").json()
        assert new_email in updated_activities[activity_name]["participants"]
        assert len(updated_activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_duplicate_returns_400(self, client, fresh_activities):
        """
        Test that duplicate signup returns 400 error.
        
        Arrange: Email that's already signed up for the activity
        Act: Make POST request to signup with duplicate email
        Assert: Response should be 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"
    
    def test_signup_invalid_activity_returns_404(self, client, fresh_activities):
        """
        Test that signup for non-existent activity returns 404.
        
        Arrange: Invalid activity name
        Act: Make POST request to signup with non-existent activity
        Assert: Response should be 404 with appropriate error message
        """
        # Arrange
        invalid_activity = "NonExistentClub"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, fresh_activities):
        """
        Test successful unregistration from an activity.
        
        Arrange: Valid activity name and email already signed up
        Act: Make DELETE request to unregister
        Assert: Response should be 200 and email should be removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
        
        # Verify participant was removed
        updated_activities = client.get("/activities").json()
        assert email_to_remove not in updated_activities[activity_name]["participants"]
        assert len(updated_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_not_signed_up_returns_400(self, client, fresh_activities):
        """
        Test that unregistration for non-participant returns 400.
        
        Arrange: Email not signed up for the activity
        Act: Make DELETE request to unregister non-participant
        Assert: Response should be 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email_not_signed_up = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_not_signed_up}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"
    
    def test_unregister_invalid_activity_returns_404(self, client, fresh_activities):
        """
        Test that unregistration from non-existent activity returns 404.
        
        Arrange: Invalid activity name
        Act: Make DELETE request to unregister from non-existent activity
        Assert: Response should be 404 with appropriate error message
        """
        # Arrange
        invalid_activity = "NonExistentClub"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""
    
    def test_signup_then_unregister_workflow(self, client, fresh_activities):
        """
        Test complete workflow: signup and then unregister.
        
        Arrange: Fresh activities, valid data
        Act: Signup a new participant, then unregister them
        Assert: Both operations succeed and state is consistent
        """
        # Arrange
        activity_name = "Programming Class"
        email = "workflow@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_after_signup = client.get("/activities").json()
        assert email in activities_after_signup[activity_name]["participants"]
        assert len(activities_after_signup[activity_name]["participants"]) == initial_count + 1
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Assert - Final state matches initial
        activities_after_unregister = client.get("/activities").json()
        assert email not in activities_after_unregister[activity_name]["participants"]
        assert len(activities_after_unregister[activity_name]["participants"]) == initial_count
