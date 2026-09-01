"""
Pytest configuration and shared fixtures for API tests.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a FastAPI TestClient for making requests to the app.
    
    Yields a fresh test client for each test.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Provide a fresh activities database for each test.
    
    This fixture resets the activities to their initial state and resets
    participant lists to ensure test isolation. Each test gets a clean slate.
    
    Args:
        monkeypatch: pytest's monkeypatch fixture for patching module state
    """
    # Define initial test data
    test_activities = {
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
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and tournament preparation",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lucia@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performance and script analysis",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Public speaking and competitive debate",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alexander@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, research projects, and STEM exploration",
            "schedule": "Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu"]
        }
    }
    
    # Patch the app's activities dictionary with fresh test data
    monkeypatch.setattr("src.app.activities", test_activities)
    
    return test_activities
