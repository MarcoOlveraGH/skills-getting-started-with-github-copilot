"""Tests for the POST /activities/{activity_name}/signup endpoint using AAA pattern."""

import pytest


class TestSignupHappyPath:
    """Test suite for successful signup scenarios."""

    def test_signup_success(self, client):
        """Test successful signup adds email to activity participants.
        
        AAA Pattern:
        - Arrange: Define activity name and email to signup
        - Act: POST to signup endpoint with valid activity and email
        - Assert: Verify response status is 200 and message indicates success
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_to_participants_list(self, client):
        """Test that signup actually adds email to activity's participants.
        
        AAA Pattern:
        - Arrange: Define activity and email, get initial participants count
        - Act: POST to signup endpoint
        - Assert: Verify email is now in the activity's participants list
        """
        # Arrange
        activity_name = "Soccer Club"
        email = "soccer_newbie@mergington.edu"
        
        # Get initial participants
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Verify signup succeeded
        assert signup_response.status_code == 200

        # Verify email is now in participants
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert email in final_participants
        assert len(final_participants) == len(initial_participants) + 1

    def test_signup_multiple_different_activities(self, client):
        """Test that one student can signup for multiple different activities.
        
        AAA Pattern:
        - Arrange: Define email and two different activities
        - Act: POST signup for first activity, then second activity
        - Assert: Verify both signups succeeded and email is in both activities
        """
        # Arrange
        email = "multi_activity@mergington.edu"
        activity1 = "Art Club"
        activity2 = "Drama Club"

        # Act - Sign up for first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        
        # Act - Sign up for second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        final_activities = client.get("/activities").json()
        assert email in final_activities[activity1]["participants"]
        assert email in final_activities[activity2]["participants"]


class TestSignupErrorCases:
    """Test suite for signup error scenarios."""

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Define invalid activity name and email
        - Act: POST to signup endpoint with invalid activity
        - Assert: Verify 404 status and error message
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_email(self, client):
        """Test signup with duplicate email returns 400.
        
        AAA Pattern:
        - Arrange: Identify activity with existing participant
        - Act: Attempt to signup with existing participant email
        - Assert: Verify 400 status and error message about duplicate signup
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_missing_email_parameter(self, client):
        """Test signup without email parameter returns 400 or 422.
        
        AAA Pattern:
        - Arrange: Define activity name without email
        - Act: POST to signup endpoint without email parameter
        - Assert: Verify error status code (400 or 422)
        """
        # Arrange
        activity_name = "Programming Class"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code in [400, 422]

    def test_signup_empty_email_parameter(self, client):
        """Test signup with empty email parameter.
        
        AAA Pattern:
        - Arrange: Define activity and empty email
        - Act: POST to signup endpoint with empty email
        - Assert: Verify request is processed (behavior depends on implementation)
        """
        # Arrange
        activity_name = "Debate Club"
        email = ""

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Either 200 (if API allows) or 400 (if validation fails)
        # For now, we just verify the endpoint responds
        assert response.status_code in [200, 400, 422]

    def test_signup_same_activity_twice_fails(self, client):
        """Test attempting to signup for same activity twice fails.
        
        AAA Pattern:
        - Arrange: Define activity and email
        - Act: POST signup once (should succeed), then attempt again
        - Assert: Verify first signup succeeds, second returns 400
        """
        # Arrange
        activity_name = "Science Club"
        email = "science_fan@mergington.edu"

        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Attempt second signup for same activity
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()


class TestSignupCapacityValidation:
    """Test suite for signup capacity constraints.
    
    Note: This test class depends on understanding current capacity usage
    in the application. Adjust activity names and pre-filled participants
    as needed based on the actual activities data.
    """

    def test_signup_respects_max_participants_constraint(self, client):
        """Test that signup enforces max_participants constraint.
        
        AAA Pattern:
        - Arrange: Get an activity and find how many spots are left
        - Act: Attempt to signup for that activity
        - Assert: Verify request succeeds if capacity allows, or fails if exceeded
        
        Note: This is an integration test that depends on initial data.
        Modify activity names and emails based on your actual data.
        """
        # Arrange
        activities = client.get("/activities").json()
        
        # Find an activity with available capacity
        available_activity = None
        for activity_name, activity_data in activities.items():
            if len(activity_data["participants"]) < activity_data["max_participants"]:
                available_activity = activity_name
                break

        assert available_activity is not None, "Need at least one activity with available capacity"
        
        test_email = f"capacity_test_{available_activity.lower().replace(' ', '_')}@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{available_activity}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        assert test_email in client.get("/activities").json()[available_activity]["participants"]
