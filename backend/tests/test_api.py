import os
os.environ['DEV_API_TOKEN'] = 'test-token'

import pytest
import sqlite3
from fastapi.testclient import TestClient
from main import app
from database import DB_PATH
from services.auth_service import AuthService
import json

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

@pytest.fixture
def auth_headers():
    token = AuthService.create_access_token(data={"sub": "user_123"})
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def test_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'healthy'

def test_query_forecast(client, auth_headers):
    res = client.post('/api/query', headers=auth_headers, content=json.dumps({
        'query': 'How much will I spend on food next month?'
    }))
    assert res.status_code == 200
    assert res.json()['intent'] == 'FORECAST_REQUEST'
    assert res.json()['category'] == 'food'
    assert 'forecast_amount' in res.json()
    
def test_query_summary(client, auth_headers):
    res = client.post('/api/query', headers=auth_headers, content=json.dumps({
        'query': 'What is my total summary last month?'
    }))
    assert res.status_code == 200
    assert res.json()['intent'] == 'SPENDING_SUMMARY'
    
def test_query_recommendation(client, auth_headers):
    res = client.post('/api/query', headers=auth_headers, content=json.dumps({
        'query': 'How can I save money?'
    }))
    assert res.status_code == 200
    assert res.json()['intent'] == 'RECOMMENDATION'

def test_query_missing_text(client, auth_headers):
    res = client.post('/api/query', headers=auth_headers, content=json.dumps({}))
    assert res.status_code == 400
    
def test_get_transactions(client, auth_headers):
    res = client.get('/api/transactions', headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_analytics_summary(client, auth_headers):
    res = client.get('/api/analytics/summary', headers=auth_headers)
    assert res.status_code == 200
    assert 'net_savings' in res.json()
