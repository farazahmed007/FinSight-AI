import pytest
from fastapi.testclient import TestClient
import pandas as pd
from datetime import datetime, timedelta

from main import app
from database import init_db

# Mock authentication
from middleware.auth import VALID_TOKENS

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    token = list(VALID_TOKENS.keys())[0]
    return {"Authorization": f"Bearer {token}"}

def test_get_all_goals_empty(client, auth_headers):
    # Depending on test database state, might not be empty, so just check it runs
    response = client.get("/api/goals", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_and_get_goal(client, auth_headers):
    goal_data = {
        "name": "Test Emergency Fund",
        "description": "For emergencies",
        "target_amount": 50000,
        "current_amount": 10000,
        "target_date": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"),
        "category": "Emergency"
    }
    
    response = client.post("/api/goals", json=goal_data, headers=auth_headers)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Test Emergency Fund"
    assert created["remaining_amount"] == 40000
    assert created["progress_percentage"] == 20.0
    
    goal_id = created["id"]
    
    # Get by ID
    get_res = client.get(f"/api/goals/{goal_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Test Emergency Fund"

def test_update_goal(client, auth_headers):
    goal_data = {
        "name": "Test Update Goal",
        "target_amount": 10000,
        "current_amount": 0,
        "target_date": "2026-12-31"
    }
    
    create_res = client.post("/api/goals", json=goal_data, headers=auth_headers)
    goal_id = create_res.json()["id"]
    
    update_data = {
        "current_amount": 5000
    }
    
    update_res = client.put(f"/api/goals/{goal_id}", json=update_data, headers=auth_headers)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["current_amount"] == 5000
    assert updated["remaining_amount"] == 5000
    assert updated["progress_percentage"] == 50.0

def test_delete_goal(client, auth_headers):
    goal_data = {
        "name": "Test Delete Goal",
        "target_amount": 10000,
        "current_amount": 0,
        "target_date": "2026-12-31"
    }
    
    create_res = client.post("/api/goals", json=goal_data, headers=auth_headers)
    goal_id = create_res.json()["id"]
    
    del_res = client.delete(f"/api/goals/{goal_id}", headers=auth_headers)
    assert del_res.status_code == 204
    
    get_res = client.get(f"/api/goals/{goal_id}", headers=auth_headers)
    assert get_res.status_code == 404

def test_goal_summary(client, auth_headers):
    response = client.get("/api/goals/summary", headers=auth_headers)
    assert response.status_code == 200
    summary = response.json()
    assert "total_goals" in summary
    assert "active_goals" in summary
    assert "total_target" in summary

def test_nlp_intent_goals(client, auth_headers):
    # Test GOAL_SAVINGS_REQUIRED intent
    payload = {"query": "How much should I save each month?"}
    response = client.post("/api/query", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["intent"] == "GOAL_SAVINGS_REQUIRED"

def test_create_goal_validation_error(client, auth_headers):
    goal_data = {
        "name": "Invalid Goal",
        "target_amount": -100, # Invalid
        "target_date": "2026-12-31"
    }
    response = client.post("/api/goals", json=goal_data, headers=auth_headers)
    assert response.status_code == 400
