import pytest
import pandas as pd
from datetime import datetime, timedelta
import math

from services.planning_engine import PlanningEngine
from schemas.planning_schemas import PlanningScenarioRequest, AffordabilityRequest, GoalPlanningRequest

def test_baseline_and_scenario_savings():
    now = datetime.now()
    # Income: 5000, Expense: 2000 => Savings: 3000
    df = pd.DataFrame([
        {'transaction_id': '1', 'user_id': 'test', 'timestamp': now, 'amount': 5000, 'category': 'salary', 'merchant': 'Employer', 'type': 'income'},
        {'transaction_id': '2', 'user_id': 'test', 'timestamp': now, 'amount': 2000, 'category': 'shopping', 'merchant': 'Store', 'type': 'expense'}
    ])
    
    engine = PlanningEngine('test', df)
    
    # Scenario: Reduce shopping by 500, Increase income by 1000
    req = PlanningScenarioRequest(
        monthly_income_change=1000,
        category_changes={'shopping': -500}
    )
    
    res = engine.calculate_scenario(req)
    
    # Baseline
    assert res.baseline.monthly_income == 5000
    assert res.baseline.monthly_expenses == 2000
    assert res.baseline.monthly_savings == 3000
    
    # Scenario
    assert res.scenario.monthly_income == 6000
    assert res.scenario.monthly_expenses == 1500
    assert res.scenario.monthly_savings == 4500
    
    # Impact
    assert res.impact.monthly_savings_change == 1500
    
    # Category Impact
    cat_impact = next(c for c in res.category_impacts if c.category == 'shopping')
    assert cat_impact.current_spending == 2000
    assert cat_impact.scenario_spending == 1500
    assert cat_impact.reduction == 500

def test_future_projection_cumulative():
    now = datetime.now()
    df = pd.DataFrame([
        {'transaction_id': '1', 'user_id': 'test', 'timestamp': now, 'amount': 1000, 'category': 'salary', 'merchant': 'E', 'type': 'income'}
    ])
    engine = PlanningEngine('test', df)
    req = PlanningScenarioRequest(additional_monthly_savings=500, duration_months=3)
    res = engine.calculate_scenario(req)
    
    # Baseline savings: 1000
    # Scenario savings: 1500
    assert len(res.future_projection) == 3
    assert res.future_projection[0]['baseline_savings'] == 1000
    assert res.future_projection[0]['scenario_savings'] == 1500
    assert res.future_projection[2]['baseline_savings'] == 3000
    assert res.future_projection[2]['scenario_savings'] == 4500

def test_affordability():
    now = datetime.now()
    # Income 2000, Expense 1000 -> Savings 1000
    df = pd.DataFrame([
        {'transaction_id': '1', 'user_id': 'test', 'timestamp': now, 'amount': 2000, 'type': 'income'},
        {'transaction_id': '2', 'user_id': 'test', 'timestamp': now, 'amount': 1000, 'type': 'expense'}
    ])
    engine = PlanningEngine('test', df)
    
    # Can I afford 5000 in 4 months? (Requires 1250/mo, capacity is 1000, shortfall 250)
    # Shortfall is 250. 250 is > 10% of income (2000 * 0.1 = 200). So NOT_AFFORDABLE.
    res = engine.calculate_affordability(AffordabilityRequest(purchase_amount=5000, months=4))
    assert res.status == 'NOT_AFFORDABLE'
    assert res.shortfall == 250
    assert res.required_monthly_savings == 1250
    
    # Can I afford 4000 in 4 months? (Requires 1000/mo, capacity 1000, shortfall 0)
    res = engine.calculate_affordability(AffordabilityRequest(purchase_amount=4000, months=4))
    assert res.status == 'AFFORDABLE'
    assert res.shortfall == 0
