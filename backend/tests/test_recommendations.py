import pytest
import pandas as pd
from datetime import datetime, timedelta
from services.recommendation_engine import RecommendationEngine

def test_empty_df():
    df = pd.DataFrame()
    engine = RecommendationEngine(df, 'test_user')
    recs = engine.generate_recommendations()
    assert len(recs) == 0

def test_savings_rate_warning():
    # Setup df with very low savings rate (<10%) over last 30 days
    now = datetime.now()
    df = pd.DataFrame([
        {'transaction_id': '1', 'user_id': 'test', 'timestamp': now, 'amount': 10000, 'category': 'salary', 'type': 'income'},
        {'transaction_id': '2', 'user_id': 'test', 'timestamp': now, 'amount': 9500, 'category': 'shopping', 'type': 'expense'}
    ])
    
    engine = RecommendationEngine(df, user_id=None)
    recs = engine.generate_recommendations()
    
    # Should contain a warning about low savings rate
    savings_warnings = [r for r in recs if r['type'] == 'warning' and 'savings rate' in r['message'].lower()]
    assert len(savings_warnings) == 1
    assert savings_warnings[0]['severity'] == 'high'

def test_savings_rate_success():
    # Setup df with high savings rate (>40%)
    now = datetime.now()
    df = pd.DataFrame([
        {'transaction_id': '1', 'user_id': 'test', 'timestamp': now, 'amount': 10000, 'category': 'salary', 'type': 'income'},
        {'transaction_id': '2', 'user_id': 'test', 'timestamp': now, 'amount': 4000, 'category': 'shopping', 'type': 'expense'}
    ])
    
    engine = RecommendationEngine(df, user_id=None)
    recs = engine.generate_recommendations()
    
    savings_success = [r for r in recs if r['type'] == 'success' and 'savings rate' in r['message'].lower()]
    assert len(savings_success) == 1
    assert savings_success[0]['severity'] == 'low'

def test_conflict_resolution(monkeypatch):
    # Setup df with high savings rate (>40%)
    now = datetime.now()
    df = pd.DataFrame([
        {'transaction_id': '1', 'user_id': 'test', 'timestamp': now, 'amount': 10000, 'category': 'salary', 'type': 'income'},
        {'transaction_id': '2', 'user_id': 'test', 'timestamp': now, 'amount': 4000, 'category': 'shopping', 'type': 'expense'}
    ])
    
    # Mock GoalsEngine to return a 'BEHIND' goal
    from services.goals_engine import GoalsEngine
    def mock_get_all_goals(self):
        return [{
            'id': 'g1',
            'name': 'House Downpayment',
            'target_amount': 500000,
            'current_amount': 100000,
            'target_date': (now + timedelta(days=365)).strftime('%Y-%m-%d'),
            'category': 'housing',
            'status': 'BEHIND',
            'remaining_amount': 400000,
            'required_monthly_savings': 400000 / 12
        }]
    monkeypatch.setattr(GoalsEngine, 'get_all_goals', mock_get_all_goals)
    
    engine = RecommendationEngine(df, 'test_user')
    recs = engine.generate_recommendations()
    
    # Verify that the BEHIND goal alert is present
    goal_alerts = [r for r in recs if r['type'] == 'goal_alert' and r['severity'] == 'high']
    assert len(goal_alerts) == 1
    
    # Verify that the "invest surplus" success recommendation is SUPPRESSED because of the high severity goal alert
    savings_success = [r for r in recs if r['type'] == 'success' and 'savings rate' in r['message'].lower()]
    assert len(savings_success) == 0  # Should be suppressed
