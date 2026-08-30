import pytest
from fastapi.testclient import TestClient
from main import app
from services.auth_service import AuthService
import sqlite3
from database import DB_PATH
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM users WHERE username = 'test_jwt_user'")
    conn.commit()
    conn.close()
    yield
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM users WHERE username = 'test_jwt_user'")
    conn.commit()
    conn.close()

def test_missing_auth():
    response = client.get('/api/analytics/summary')
    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["message"]

def test_invalid_auth_format():
    response = client.get('/api/analytics/summary', headers={'Authorization': 'test-token'})
    assert response.status_code == 401
    assert "Invalid Authorization header format" in response.json()["message"]

def test_invalid_token():
    response = client.get('/api/analytics/summary', headers={'Authorization': 'Bearer wrong-token'})
    assert response.status_code == 401
    assert "Invalid token" in response.json()["message"]

def test_register_and_login():
    # Register
    res_reg = client.post("/api/auth/register", json={
        "username": "test_jwt_user",
        "password": "password123"
    })
    assert res_reg.status_code == 201
    assert res_reg.json()["username"] == "test_jwt_user"

    # Login
    res_login = client.post("/api/auth/login", json={
        "username": "test_jwt_user",
        "password": "password123"
    })
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]

    # Verify access to protected route
    res_auth = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200
    assert res_auth.json()["username"] == "test_jwt_user"

def test_login_invalid():
    res = client.post("/api/auth/login", json={
        "username": "non_existent_user",
        "password": "password"
    })
    assert res.status_code == 401
