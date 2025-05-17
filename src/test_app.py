import pytest
from pymongo import MongoClient
from app import app, init_db, activities_collection
from fastapi.testclient import TestClient

# Test client setup
client = TestClient(app)

def clear_test_db():
    """Clear the test database before each test"""
    activities_collection.delete_many({})

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    clear_test_db()
    init_db()  # Initialize with test data
    yield
    clear_test_db()

def test_initial_data_loaded():
    """Test that initial data is properly loaded into MongoDB"""
    # Get all activities from the database
    activities = list(activities_collection.find())
    
    # Verify we have the correct number of activities
    assert len(activities) == 9, "Should have 9 initial activities"
    
    # Check for specific activities
    chess_club = activities_collection.find_one({"_id": "Chess Club"})
    assert chess_club is not None, "Chess Club should exist"
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert len(chess_club["participants"]) == 2, "Chess Club should have 2 participants"
    
    programming_class = activities_collection.find_one({"_id": "Programming Class"})
    assert programming_class is not None, "Programming Class should exist"
    assert "emma@mergington.edu" in programming_class["participants"]

def test_signup_for_activity():
    """Test signing up for an activity updates MongoDB"""
    new_email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={new_email}")
    assert response.status_code == 200
    
    # Verify the database was updated
    chess_club = activities_collection.find_one({"_id": "Chess Club"})
    assert new_email in chess_club["participants"]
    assert len(chess_club["participants"]) == 3

def test_unregister_from_activity():
    """Test unregistering from an activity updates MongoDB"""
    # First ensure we know an existing participant
    chess_club = activities_collection.find_one({"_id": "Chess Club"})
    existing_email = chess_club["participants"][0]
    
    # Unregister the participant
    response = client.delete(f"/activities/Chess Club/unregister?email={existing_email}")
    assert response.status_code == 200
    
    # Verify the database was updated
    updated_chess_club = activities_collection.find_one({"_id": "Chess Club"})
    assert existing_email not in updated_chess_club["participants"]
    assert len(updated_chess_club["participants"]) == len(chess_club["participants"]) - 1
