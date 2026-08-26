import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set seed for deterministic data generation
np.random.seed(42)
random.seed(42)

def generate_transactions(num_days=365):
    transactions = []
    
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=num_days)
    
    user_id = "user_123"
    
    # Categories and base probabilities
    expense_categories = {
        'food': 0.35,          # frequent
        'housing': 0.05,       # once a month
        'transport': 0.20,     # frequent
        'subscriptions': 0.05, # monthly
        'shopping': 0.15,      # occasional
        'healthcare': 0.05,    # rare
        'utilities': 0.05,     # monthly
        'entertainment': 0.10  # weekend mostly
    }
    
    # Merchants for categories
    merchants = {
        'food': ['Swiggy', 'Zomato', 'Local Grocery', 'Starbucks', 'McDonalds', 'Domino\'s'],
        'housing': ['Landlord', 'Maintenance'],
        'transport': ['Uber', 'Ola', 'Metro', 'Indian Oil', 'HP Petrol'],
        'subscriptions': ['Netflix', 'Spotify', 'Amazon Prime', 'Gym'],
        'shopping': ['Amazon', 'Flipkart', 'Myntra', 'H&M'],
        'healthcare': ['Apollo Pharmacy', 'Practo', 'Local Clinic'],
        'utilities': ['Electricity Board', 'Jio Fiber', 'Water Bill'],
        'entertainment': ['BookMyShow', 'PVR Cinemas', 'Pub/Bar']
    }
    
    current_date = start_date
    transaction_id = 1000
    
    # Monthly fixed transactions
    rent_day = 5
    salary_day = 1
    utility_day = 10
    
    while current_date <= end_date:
        # Salary Income (once a month)
        if current_date.day == salary_day:
            transactions.append({
                'transaction_id': f"TXN{transaction_id}",
                'user_id': user_id,
                'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': 85000.0,
                'category': 'salary',
                'merchant': 'Employer Inc',
                'type': 'income'
            })
            transaction_id += 1
            
        # Rent Expense (once a month)
        if current_date.day == rent_day:
            transactions.append({
                'transaction_id': f"TXN{transaction_id}",
                'user_id': user_id,
                'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': 25000.0,
                'category': 'housing',
                'merchant': 'Landlord',
                'type': 'expense'
            })
            transaction_id += 1
            
        # Utilities (once a month)
        if current_date.day == utility_day:
            transactions.append({
                'transaction_id': f"TXN{transaction_id}",
                'user_id': user_id,
                'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': random.uniform(1500, 3000),
                'category': 'utilities',
                'merchant': random.choice(merchants['utilities']),
                'type': 'expense'
            })
            transaction_id += 1
            
        # Subscriptions (scattered monthly)
        if current_date.day in [12, 15, 20, 25]:
            transactions.append({
                'transaction_id': f"TXN{transaction_id}",
                'user_id': user_id,
                'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': random.choice([199.0, 499.0, 999.0]),
                'category': 'subscriptions',
                'merchant': random.choice(merchants['subscriptions']),
                'type': 'expense'
            })
            transaction_id += 1
            
        # Daily variable expenses
        # 1-3 transactions per day
        num_daily_txns = random.randint(1, 3)
        for _ in range(num_daily_txns):
            # Pick a category based on weights
            cats = list(expense_categories.keys())
            weights = list(expense_categories.values())
            
            # Weekend bias for entertainment & shopping
            is_weekend = current_date.weekday() >= 5
            if is_weekend:
                idx = cats.index('entertainment')
                weights[idx] *= 3
                idx2 = cats.index('shopping')
                weights[idx2] *= 2
                idx3 = cats.index('food')
                weights[idx3] *= 1.5
                
            cat = random.choices(cats, weights=weights)[0]
            
            # Amount ranges based on category
            amount_ranges = {
                'food': (100, 1500),
                'housing': (500, 5000), # miscellaneous maintenance
                'transport': (50, 800),
                'subscriptions': (100, 1000),
                'shopping': (500, 5000),
                'healthcare': (200, 2500),
                'utilities': (100, 1000),
                'entertainment': (300, 3000)
            }
            
            # Trend simulation (e.g., food spending slowly increasing over the year)
            days_passed = (current_date - start_date).days
            trend_multiplier = 1.0
            if cat == 'food':
                trend_multiplier = 1.0 + (days_passed / num_days) * 0.2  # 20% increase over year
            
            min_amt, max_amt = amount_ranges[cat]
            amount = random.uniform(min_amt, max_amt) * trend_multiplier
            
            # Format time randomly during the day
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            txn_time = current_date.replace(hour=hour, minute=minute, second=second)
            
            transactions.append({
                'transaction_id': f"TXN{transaction_id}",
                'user_id': user_id,
                'timestamp': txn_time.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': round(amount, 2),
                'category': cat,
                'merchant': random.choice(merchants[cat]),
                'type': 'expense'
            })
            transaction_id += 1
            
        # Move to next day
        current_date += timedelta(days=1)
        
    df = pd.DataFrame(transactions)
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/transactions.csv', index=False)
    print(f"Generated {len(df)} transactions and saved to data/transactions.csv")

if __name__ == "__main__":
    generate_transactions(365)
