import pytest
from fastapi.testclient import TestClient
from main import app
from middleware.auth import VALID_TOKENS

client = TestClient(app)

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
    assert "Invalid or expired token" in response.json()["message"]

def test_valid_token():
    # Use the default dev token
    token = list(VALID_TOKENS.keys())[0]
    response = client.get('/api/analytics/summary', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
