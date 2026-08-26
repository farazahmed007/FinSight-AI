import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta
from services.forecasting import ForecastingEngine

def generate_dummy_data(days=60, trend_factor=0.0):
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Base amount + trend + some noise
    amounts = [100.0 + (i * trend_factor) + (np.sin(i * (2 * np.pi / 7)) * 20) + np.random.normal(0, 5) for i in range(days)]
    # Ensure no negative amounts for safety
    amounts = [max(a, 0) for a in amounts]
    
    return pd.DataFrame({
        'date': dates,
        'amount': amounts
    })

def test_forecast_insufficient_history():
    # Less than 45 days
    df = generate_dummy_data(days=30)
    engine = ForecastingEngine(df)
    
    result = engine.forecast_category('food', horizon_days=7)
    
    assert result['category'] == 'food'
    assert result['horizon_days'] == 7
    assert len(result['forecast_values']) == 7
    assert result['method'] == 'average-fallback'

def test_forecast_sufficient_history():
    # More than 45 days
    df = generate_dummy_data(days=100)
    engine = ForecastingEngine(df)
    
    result = engine.forecast_category('food', horizon_days=30)
    
    assert result['method'] == 'holt-winters'
    assert len(result['forecast_values']) == 30
    # Values shouldn't be negative
    assert all(v >= 0 for v in result['forecast_values'])

def test_forecast_increasing_trend():
    # Significant increasing trend
    df = generate_dummy_data(days=60, trend_factor=5.0)
    engine = ForecastingEngine(df)
    
    result = engine.forecast_category('food', horizon_days=10)
    
    assert result['trend'] == 'increasing'

def test_forecast_decreasing_trend():
    # Significant decreasing trend
    df = generate_dummy_data(days=60, trend_factor=-2.0)
    engine = ForecastingEngine(df)
    
    result = engine.forecast_category('food', horizon_days=10)
    
    assert result['trend'] == 'decreasing'

def test_forecast_empty_dataframe():
    df = pd.DataFrame(columns=['date', 'amount'])
    engine = ForecastingEngine(df)
    
    result = engine.forecast_category('food', horizon_days=30)
    assert result['method'] == 'none'
    assert result['forecast_values'] == []
