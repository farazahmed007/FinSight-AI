import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app
from database import init_db, load_seed_data
import os
from middleware.auth import VALID_TOKENS

client = TestClient(app)

token = list(VALID_TOKENS.keys())[0]
HEADERS = {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_database():
    # Ensure test database is initialized
    init_db()
    load_seed_data()
    yield
    # Cleanup logic if necessary (though using the same dev db for now)

def test_get_financial_health_no_auth():
    response = client.get("/api/financial-health/")
    assert response.status_code == 401

def test_get_financial_health():
    # Note: Requires auth token. The current auth mock just checks for Bearer token.
    response = client.get(
        "/api/financial-health/",
        headers=HEADERS
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "status" in data
    assert "breakdown" in data
    assert "insights" in data
    assert "summary" in data

    breakdown = data["breakdown"]
    assert "savings" in breakdown
    assert "budget_discipline" in breakdown
    assert "goal_progress" in breakdown
    assert "spending_control" in breakdown
    assert "financial_stability" in breakdown

def test_get_financial_health_history():
    response = client.get(
        "/api/financial-health/history",
        headers=HEADERS
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_ai_assistant_financial_health_intent():
    response = client.post(
        "/api/query",
        json={"query": "what is my financial health score?"},
        headers=HEADERS
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "FINANCIAL_HEALTH_SCORE"
    assert "score" in data
    assert "breakdown" in data

# --- Unit Tests for FinancialHealthEngine ---
import pandas as pd
from services.financial_health_engine import FinancialHealthEngine
from datetime import datetime, timedelta

def test_savings_score():
    now = datetime.now()
    df = pd.DataFrame([
        {'timestamp': now, 'type': 'income', 'amount': 1000},
        {'timestamp': now, 'type': 'expense', 'amount': 800} # 20% savings
    ])
    engine = FinancialHealthEngine("test_user", df)
    score = engine.calculate_savings_score()
    assert score == 80.0

def test_savings_score_no_income():
    now = datetime.now()
    df = pd.DataFrame([
        {'timestamp': now, 'type': 'expense', 'amount': 800} 
    ])
    engine = FinancialHealthEngine("test_user", df)
    score = engine.calculate_savings_score()
    assert score == 20.0 # From logic: expense > 0 and income = 0

def test_spending_control_score():
    now = datetime.now()
    df = pd.DataFrame([
        {'timestamp': now, 'type': 'expense', 'amount': 1000}, # last 30
        {'timestamp': now - timedelta(days=45), 'type': 'expense', 'amount': 500} # prev 30
    ])
    engine = FinancialHealthEngine("test_user", df)
    score = engine.calculate_spending_control_score()
    # base 70. 1000 is 100% higher than 500. So ratio 1.0. Deduct 30. Final 40.
    assert score == 40.0

def test_stability_score():
    now = datetime.now()
    df = pd.DataFrame([
        {'timestamp': datetime(2026, 8, 15), 'type': 'income', 'amount': 1000},
        {'timestamp': datetime(2026, 7, 15), 'type': 'income', 'amount': 1000},
        {'timestamp': datetime(2026, 6, 15), 'type': 'income', 'amount': 1000},
        {'timestamp': datetime(2026, 8, 15), 'type': 'expense', 'amount': 500},
        {'timestamp': datetime(2026, 7, 15), 'type': 'expense', 'amount': 500},
        {'timestamp': datetime(2026, 6, 15), 'type': 'expense', 'amount': 500},
    ])
    engine = FinancialHealthEngine("test_user", df)
    score = engine.calculate_stability_score()
    assert score == 100.0 # 0 variance

def test_aggregation():
    engine = FinancialHealthEngine("test_user", pd.DataFrame())
    # Override for testing weights
    engine.calculate_savings_score = lambda: 100.0 # 25%
    engine.calculate_budget_discipline_score = lambda: 100.0 # 20%
    engine.calculate_goal_progress_score = lambda: 50.0 # 20% => 10 points
    engine.calculate_spending_control_score = lambda: 50.0 # 20% => 10 points
    engine.calculate_stability_score = lambda: 50.0 # 15% => 7.5 points
    
    # 25 + 20 + 10 + 10 + 7.5 = 72.5
    data = engine.calculate_overall_health()
    assert data['score'] == 72 # rounded

# --- Unit Tests for FinancialInsightsEngine ---
from services.financial_insights_engine import FinancialInsightsEngine

def test_insights_generation_with_forecast_and_recommendation():
    # Mock some basic transaction data to trigger both systems
    now = datetime.now()
    # Generate 15 days of food spending to trigger forecast
    data = []
    for i in range(15):
        data.append({'id': i, 'timestamp': now - timedelta(days=i), 'type': 'expense', 'amount': 100, 'category': 'food'})
    
    df = pd.DataFrame(data)
    
    health_data = {
        'score': 50,
        'breakdown': {
            'savings': 50,
            'budget_discipline': 50,
            'goal_progress': 50,
            'spending_control': 50,
            'financial_stability': 50
        }
    }
    
    # Need to override BudgetEngine briefly to ensure it returns a budget for food
    import services.budget_engine
    original_get_summary = services.budget_engine.BudgetEngine.get_summary
    
    def mock_get_summary(self, month):
        return {
            'categories': [
                {'category': 'food', 'budget': 500, 'spent': 1500, 'variance': -1000, 'usage_percentage': 300, 'status': 'OVER_BUDGET'}
            ]
        }
        
    services.budget_engine.BudgetEngine.get_summary = mock_get_summary

    import services.goals_engine
    original_get_all_goals = services.goals_engine.GoalsEngine.get_all_goals
    def mock_get_all_goals(self):
        return []
    services.goals_engine.GoalsEngine.get_all_goals = mock_get_all_goals
    
    try:
        engine = FinancialInsightsEngine("test_user", df, health_data)
        result = engine.generate_insights()
        
        # Should have forecast warning (projected > 500)
        assert any(i['type'] == 'forecast_warning' for i in result['insights'])
        
        # Should have budget alert from RecommendationEngine
        assert any(i['type'] == 'budget_alert' for i in result['insights'])
        
    finally:
        # Restore
        services.budget_engine.BudgetEngine.get_summary = original_get_summary
        services.goals_engine.GoalsEngine.get_all_goals = original_get_all_goals
