import pandas as pd
import numpy as np

CATEGORY_ALIASES = {
    'groceries': 'food',
    'dining': 'food',
    'restaurant': 'food',
    'uber': 'transport',
    'ola': 'transport',
    'fuel': 'transport',
    'netflix': 'subscriptions',
    'spotify': 'subscriptions',
    'rent': 'housing',
    'emi': 'housing'
}

def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans transaction dataframe according to requirements:
    - Parse timestamps
    - Normalize category names (aliases and lowercase)
    - Handle missing values (uncategorized)
    - Remove invalid timestamps
    - Remove duplicates
    """
    if df.empty:
        return df

    # Remove duplicates
    df = df.drop_duplicates()

    # Parse timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Remove records with invalid/missing timestamps
    df = df.dropna(subset=['timestamp'])

    # Handle missing category
    df['category'] = df['category'].fillna('uncategorized').astype(str)
    
    # Normalize category names
    df['category'] = df['category'].str.lower().str.strip()
    df['category'] = df['category'].replace(CATEGORY_ALIASES)
    
    # Fill missing merchant
    df['merchant'] = df['merchant'].fillna('Unknown')
    
    # Ensure amount is numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])

    # Ensure type is valid
    df['type'] = df['type'].fillna('expense').str.lower()
    df.loc[~df['type'].isin(['income', 'expense']), 'type'] = 'expense'

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

def aggregate_daily_transactions(df: pd.DataFrame, category=None, txn_type='expense') -> pd.DataFrame:
    """
    Aggregates transactions into daily time series.
    Returns a dataframe with 'date' and 'amount' columns.
    If category is provided, filters by category.
    """
    if df.empty:
        return pd.DataFrame(columns=['date', 'amount'])
        
    filtered_df = df[df['type'] == txn_type].copy()
    if category:
        filtered_df = filtered_df[filtered_df['category'] == category]
        
    if filtered_df.empty:
        return pd.DataFrame(columns=['date', 'amount'])
        
    # Extract date
    filtered_df['date'] = filtered_df['timestamp'].dt.floor('D')
    
    # Aggregate
    daily_df = filtered_df.groupby('date')['amount'].sum().reset_index()
    
    return daily_df
