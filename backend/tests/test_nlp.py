import pytest
from services.nlp_engine import NLPEngine

def test_nlp_engine_forecast():
    engine = NLPEngine()
    
    q1 = "How much will I spend on food next month?"
    res1 = engine.process_query(q1)
    
    assert res1['intent'] == 'FORECAST_REQUEST'
    assert res1['category'] == 'food'
    assert res1['time_range_days'] == 30
    
def test_nlp_engine_summary():
    engine = NLPEngine()
    
    q1 = "How much did I spend on transport last week?"
    res1 = engine.process_query(q1)
    
    assert res1['intent'] == 'SPENDING_SUMMARY'
    assert res1['category'] == 'transport'
    assert res1['time_range_days'] == 7

def test_nlp_engine_recommendation():
    engine = NLPEngine()
    
    q1 = "How can I save money on subscriptions?"
    res1 = engine.process_query(q1)
    
    assert res1['intent'] == 'RECOMMENDATION'
    assert res1['category'] == 'subscriptions'

def test_nlp_ambiguous_time():
    engine = NLPEngine()
    
    q1 = "What is my food summary?"
    res1 = engine.process_query(q1)
    
    assert res1['intent'] == 'SPENDING_SUMMARY'
    assert res1['category'] == 'food'
    assert res1['time_range_days'] == 30 # default
    
def test_nlp_missing_category():
    engine = NLPEngine()
    
    q1 = "How much will I spend next month?"
    res1 = engine.process_query(q1)
    
    assert res1['intent'] == 'FORECAST_REQUEST'
    assert res1['category'] is None
    assert res1['time_range_days'] == 30
