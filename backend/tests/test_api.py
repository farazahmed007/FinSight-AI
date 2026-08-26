import os
os.environ['DEV_API_TOKEN'] = 'test-token'

import pytest
from fastapi.testclient import TestClient
from main import app
import json

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

def get_headers():
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

def test_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'healthy'

def test_query_forecast(client):
    res = client.post('/api/query', headers=get_headers(), content=json.dumps({
        'query': 'How much will I spend on food next month?'
    }))
    assert res.status_code == 200
    assert res.json()['intent'] == 'FORECAST_REQUEST'
    assert res.json()['category'] == 'food'
    assert 'forecast_amount' in res.json()
    
def test_query_summary(client):
    res = client.post('/api/query', headers=get_headers(), content=json.dumps({
        'query': 'What is my total summary last month?'
    }))
    assert res.status_code == 200
    assert res.json()['intent'] == 'SPENDING_SUMMARY'
    
def test_query_recommendation(client):
    res = client.post('/api/query', headers=get_headers(), content=json.dumps({
        'query': 'How can I save money?'
    }))
    assert res.status_code == 200
    assert res.json()['intent'] == 'RECOMMENDATION'

def test_query_missing_text(client):
    res = client.post('/api/query', headers=get_headers(), content=json.dumps({}))
    assert res.status_code == 400
    
def test_get_transactions(client):
    res = client.get('/api/transactions', headers=get_headers())
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_analytics_summary(client):
    res = client.get('/api/analytics/summary', headers=get_headers())
    assert res.status_code == 200
    assert 'net_savings' in res.json()
