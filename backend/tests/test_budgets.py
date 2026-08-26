import pytest
from fastapi.testclient import TestClient
from main import app
import os
import sqlite3
from database import DB_PATH, init_db
from middleware.auth import VALID_TOKENS

client = TestClient(app)

# Use existing auth mechanism
token = list(VALID_TOKENS.keys())[0]
HEADERS = {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup test DB (which uses the same DB_PATH in prototype, but we can clean budgets)
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets")
    conn.commit()
    conn.close()
    yield
    # Teardown
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets")
    conn.commit()
    conn.close()

def test_create_budget():
    response = client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 15000, "month": "2026-08"},
        headers=HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "food"
    assert data["amount"] == 15000
    assert data["month"] == "2026-08"

def test_create_duplicate_budget():
    client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 15000, "month": "2026-08"},
        headers=HEADERS
    )
    response = client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 20000, "month": "2026-08"},
        headers=HEADERS
    )
    assert response.status_code == 400

def test_get_budgets():
    client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 15000, "month": "2026-08"},
        headers=HEADERS
    )
    response = client.get("/api/budgets?month=2026-08", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "food"

def test_get_budget_summary():
    client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 15000, "month": "2026-08"},
        headers=HEADERS
    )
    response = client.get("/api/budgets/summary?month=2026-08", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["total_budget"] == 15000
    assert len(data["categories"]) == 1
    assert data["categories"][0]["category"] == "food"
    assert data["categories"][0]["budget"] == 15000

def test_update_budget():
    create_resp = client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 15000, "month": "2026-08"},
        headers=HEADERS
    )
    budget_id = create_resp.json()["id"]
    
    update_resp = client.put(
        f"/api/budgets/{budget_id}",
        json={"amount": 18000},
        headers=HEADERS
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["amount"] == 18000

def test_delete_budget():
    create_resp = client.post(
        "/api/budgets", 
        json={"category": "food", "amount": 15000, "month": "2026-08"},
        headers=HEADERS
    )
    budget_id = create_resp.json()["id"]
    
    del_resp = client.delete(f"/api/budgets/{budget_id}", headers=HEADERS)
    assert del_resp.status_code == 200
    
    get_resp = client.get(f"/api/budgets/{budget_id}", headers=HEADERS)
    assert get_resp.status_code == 404

def test_nlp_budget_intent():
    # Test intent parsing in API
    response = client.post(
        "/api/query",
        json={"query": "what is my food budget status?"},
        headers=HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "BUDGET_STATUS"
    assert data["category"] == "food"
