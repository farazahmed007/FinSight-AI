import pytest
from fastapi.testclient import TestClient
import sqlite3
import os

from main import app
from database import DB_PATH
from services.auth_service import AuthService

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Setup
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Ensure users exist
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES ('user_123', 'prototype_user')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES ('user_456', 'test_user_2')")
    # Clean tables
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM financial_goals")
    conn.commit()
    conn.close()
    
    yield
    
    # Teardown
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM financial_goals")
    conn.commit()
    conn.close()

def test_budget_isolation():
    # User 123 creates a budget
    token_123 = AuthService.create_access_token(data={"sub": "user_123"})
    token_456 = AuthService.create_access_token(data={"sub": "user_456"})
    
    response1 = client.post("/api/budgets", json={
        "category": "Groceries",
        "amount": 500.0,
        "month": "2024-01"
    }, headers={"Authorization": f"Bearer {token_123}"})
    assert response1.status_code == 200
    b1_id = response1.json()["id"]
    
    # User 456 shouldn't see User 123's budgets
    response2 = client.get("/api/budgets?month=2024-01", headers={"Authorization": f"Bearer {token_456}"})
    assert response2.status_code == 200
    assert len(response2.json()) == 0
    
    # User 456 should not be able to fetch User 123's budget
    response3 = client.get(f"/api/budgets/{b1_id}", headers={"Authorization": f"Bearer {token_456}"})
    assert response3.status_code == 404
    
    # User 456 should not be able to update User 123's budget
    response4 = client.put(f"/api/budgets/{b1_id}", json={"amount": 900.0}, headers={"Authorization": f"Bearer {token_456}"})
    assert response4.status_code == 404
    
    # User 456 creates their own budget
    response5 = client.post("/api/budgets", json={
        "category": "Groceries",
        "amount": 300.0,
        "month": "2024-01"
    }, headers={"Authorization": f"Bearer {token_456}"})
    assert response5.status_code == 200

def test_goal_isolation():
    token_123 = AuthService.create_access_token(data={"sub": "user_123"})
    token_456 = AuthService.create_access_token(data={"sub": "user_456"})
    
    # User 123 creates a goal
    response1 = client.post("/api/goals", json={
        "name": "Vacation 123",
        "target_amount": 5000.0,
        "target_date": "2025-01-01"
    }, headers={"Authorization": f"Bearer {token_123}"})
    assert response1.status_code == 201
    g1_id = response1.json()["id"]
    
    # User 456 should not see it
    response2 = client.get("/api/goals", headers={"Authorization": f"Bearer {token_456}"})
    assert response2.status_code == 200
    assert len(response2.json()) == 0
    
    # User 456 should not be able to fetch it
    response3 = client.get(f"/api/goals/{g1_id}", headers={"Authorization": f"Bearer {token_456}"})
    assert response3.status_code == 404
