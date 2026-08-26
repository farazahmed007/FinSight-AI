import pandas as pd
import pytest
from services.preprocessing import clean_transactions, aggregate_daily_transactions

def test_clean_transactions():
    data = {
        'transaction_id': ['1', '2', '2', '3', '4'],
        'timestamp': ['2023-01-01 10:00:00', '2023-01-02 12:00:00', '2023-01-02 12:00:00', 'invalid_date', '2023-01-04 09:00:00'],
        'amount': [100.0, 200.0, 200.0, 300.0, 'abc'],
        'category': [' Groceries ', 'RENT', 'RENT', 'food', None],
        'merchant': ['Store A', 'Landlord', 'Landlord', None, 'Store B'],
        'type': ['expense', 'Expense', 'Expense', 'income', None]
    }
    df = pd.DataFrame(data)
    
    cleaned = clean_transactions(df)
    
    # Check length: one duplicate removed, one invalid date removed, one invalid amount removed
    # original: 5 rows
    # - 1 duplicate = 4 rows (1, 2, 3, 4)
    # - 1 invalid date (row 3) = 3 rows (1, 2, 4)
    # - 1 invalid amount (row 4) = 2 rows (1, 2)
    assert len(cleaned) == 2
    
    # Check category normalization and aliases
    assert cleaned.iloc[0]['category'] == 'food' # Groceries -> food
    assert cleaned.iloc[1]['category'] == 'housing' # RENT -> housing
    
    # Check type normalization
    assert cleaned.iloc[0]['type'] == 'expense'

def test_aggregate_daily_transactions():
    data = {
        'timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 15:00:00', '2023-01-02 09:00:00', '2023-01-02 10:00:00']),
        'amount': [100.0, 50.0, 200.0, 300.0],
        'category': ['food', 'food', 'housing', 'food'],
        'type': ['expense', 'expense', 'expense', 'expense']
    }
    df = pd.DataFrame(data)
    
    daily_food = aggregate_daily_transactions(df, category='food', txn_type='expense')
    
    assert len(daily_food) == 2
    assert daily_food.iloc[0]['amount'] == 150.0 # 100 + 50
    assert daily_food.iloc[1]['amount'] == 300.0 # 300 (housing is filtered out)
