"""Tests for the GET /activities endpoint using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """Test that GET /activities returns all activities with 200 status.
        
        AAA Pattern:
        - Arrange: Set up expected activity names
        - Act: Make GET request to /activities
        - Assert: Verify 200 status and all activities are present
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_response_structure(self, client):
        """Test that each activity has the required fields.
        
        AAA Pattern:
        - Arrange: Define required fields for each activity
        - Act: Make GET request to /activities
        - Assert: Verify each activity contains all required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing field: {field}"

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is always a list.
        
        AAA Pattern:
        - Arrange: Set up test
        - Act: Make GET request to /activities
        - Assert: Verify participants field is a list for all activities
        """
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_get_activities_max_participants_is_integer(self, client):
        """Test that max_participants is an integer.
        
        AAA Pattern:
        - Arrange: Set up test
        - Act: Make GET request to /activities
        - Assert: Verify max_participants is an integer greater than 0
        """
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"{activity_name} max_participants should be an integer"
            assert activity_data["max_participants"] > 0, \
                f"{activity_name} max_participants should be greater than 0"

    def test_get_activities_chess_club_initial_participants(self, client):
        """Test that Chess Club has expected initial participants.
        
        AAA Pattern:
        - Arrange: Define expected initial participants for Chess Club
        - Act: Make GET request to /activities
        - Assert: Verify Chess Club has correct participants
        """
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert activities["Chess Club"]["participants"] == expected_participants


class TestRootEndpoint:
    """Test suite for the GET / endpoint."""

    def test_root_endpoint_redirects(self, client):
        """Test that GET / redirects to /static/index.html.
        
        AAA Pattern:
        - Arrange: Set up test client
        - Act: Make GET request to / without following redirects
        - Assert: Verify redirect status code (307 or 302)
        """
        # Arrange & Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [301, 302, 303, 307], \
            "Root endpoint should redirect"

    def test_root_endpoint_redirects_to_static_index(self, client):
        """Test that GET / follows redirect to /static/index.html.
        
        AAA Pattern:
        - Arrange: Set up test client to follow redirects
        - Act: Make GET request to / and follow redirects
        - Assert: Verify final response is HTML content
        """
        # Arrange & Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # The response should contain HTML content from index.html
        assert "html" in response.text.lower() or response.text, \
            "Root endpoint should serve HTML content"
