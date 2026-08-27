import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import sys
import shutil
import argparse

# Set seed for deterministic data generation
np.random.seed(42)
random.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'finance.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def backup_db():
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.bak"
        shutil.copy2(DB_PATH, backup_path)
        print(f"Created database backup at: {backup_path}")

def clear_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM financial_goals")
    cursor.execute("DELETE FROM financial_health_snapshots")
    conn.commit()
    conn.close()
    print("Cleared existing demonstration data.")

def insert_demo_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ---------------------------------------------------------
    # 1. TRANSACTIONS
    # ---------------------------------------------------------
    num_days = 180  # ~6 months
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=num_days)
    user_id = "user_123"
    
    expense_categories = {
        'food': 0.35,
        'transport': 0.20,
        'shopping': 0.15,
        'entertainment': 0.10,
        'healthcare': 0.05,
        'utilities': 0.05,
        'subscriptions': 0.05,
        'housing': 0.05 # Monthly rent will be handled separately
    }
    
    merchants = {
        'food': ['Swiggy', 'Zomato', 'Local Grocery', 'Starbucks', 'McDonalds', 'Domino\'s', 'Burger King', 'FreshMenu'],
        'transport': ['Uber', 'Ola', 'Metro', 'Indian Oil', 'HP Petrol', 'Shell'],
        'shopping': ['Amazon', 'Flipkart', 'Myntra', 'H&M', 'Zara', 'Reliance Digital'],
        'entertainment': ['BookMyShow', 'PVR Cinemas', 'Pub/Bar', 'Bowling', 'Concert'],
        'healthcare': ['Apollo Pharmacy', 'Practo', 'Local Clinic', '1mg'],
        'utilities': ['Electricity Board', 'Jio Fiber', 'Water Bill', 'Gas Provider'],
        'subscriptions': ['Netflix', 'Spotify', 'Amazon Prime', 'Gym', 'Hotstar'],
        'housing': ['Maintenance', 'Plumber', 'Electrician']
    }
    
    amount_ranges = {
        'food': (150, 1500),
        'transport': (100, 900),
        'shopping': (1000, 6000),
        'entertainment': (500, 3500),
        'healthcare': (300, 2500),
        'utilities': (100, 1000),
        'subscriptions': (199, 999),
        'housing': (500, 2000)
    }

    current_date = start_date
    transaction_id = 1000
    transactions = []
    
    salary_day = 1
    rent_day = 5
    utility_day = 10

    while current_date <= end_date:
        # Salary Income
        if current_date.day == salary_day:
            transactions.append((
                f"TXN{transaction_id}", user_id, current_date.strftime('%Y-%m-%d 10:00:00'),
                75000.0, 'salary', 'Tech Corp', 'income'
            ))
            transaction_id += 1
            
        # Rent Expense
        if current_date.day == rent_day:
            transactions.append((
                f"TXN{transaction_id}", user_id, current_date.strftime('%Y-%m-%d 11:30:00'),
                15000.0, 'housing', 'Landlord', 'expense'
            ))
            transaction_id += 1
            
        # Utilities
        if current_date.day == utility_day:
            transactions.append((
                f"TXN{transaction_id}", user_id, current_date.strftime('%Y-%m-%d 14:15:00'),
                random.uniform(1500, 3000), 'utilities', random.choice(merchants['utilities']), 'expense'
            ))
            transaction_id += 1

        # Daily variable expenses
        num_daily_txns = random.randint(1, 4)
        for _ in range(num_daily_txns):
            cats = list(expense_categories.keys())
            weights = list(expense_categories.values())
            
            # Weekend bias
            if current_date.weekday() >= 5:
                weights[cats.index('entertainment')] *= 3
                weights[cats.index('shopping')] *= 2
                weights[cats.index('food')] *= 1.5
                
            cat = random.choices(cats, weights=weights)[0]
            if cat == 'housing' and random.random() > 0.1: 
                # Avoid too many housing maintenance expenses
                cat = 'food'
                
            min_amt, max_amt = amount_ranges[cat]
            amount = random.uniform(min_amt, max_amt)
            
            # Subscriptions tend to be fixed specific amounts
            if cat == 'subscriptions':
                amount = random.choice([199.0, 499.0, 999.0, 149.0])
                
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            txn_time = current_date.replace(hour=hour, minute=minute, second=second)
            
            transactions.append((
                f"TXN{transaction_id}", user_id, txn_time.strftime('%Y-%m-%d %H:%M:%S'),
                round(amount, 2), cat, random.choice(merchants[cat]), 'expense'
            ))
            transaction_id += 1
            
        current_date += timedelta(days=1)

    cursor.executemany('''
        INSERT INTO transactions (transaction_id, user_id, timestamp, amount, category, merchant, type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', transactions)
    
    print(f"Inserted {len(transactions)} transactions.")

    # ---------------------------------------------------------
    # 2. BUDGETS
    # ---------------------------------------------------------
    current_month = datetime.now().strftime('%Y-%m')
    budgets = [
        ('food', 10000.0, current_month),
        ('housing', 15000.0, current_month),
        ('transport', 6000.0, current_month),
        ('shopping', 7000.0, current_month),
        ('utilities', 5000.0, current_month),
        ('entertainment', 4000.0, current_month),
        ('healthcare', 3000.0, current_month),
        ('subscriptions', 2500.0, current_month)
    ]
    
    cursor.executemany('''
        INSERT INTO budgets (category, amount, month)
        VALUES (?, ?, ?)
    ''', budgets)
    
    print(f"Inserted {len(budgets)} budgets for month {current_month}.")

    # ---------------------------------------------------------
    # 3. FINANCIAL GOALS
    # ---------------------------------------------------------
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    goals = [
        ('Emergency Fund', '6 months of living expenses', 100000.0, 35000.0, '2026-12-28', 'savings'),
        ('Travel Fund', 'Trip to Europe', 60000.0, 25000.0, '2026-11-16', 'travel'),
        ('Laptop Upgrade', 'New Macbook Pro', 80000.0, 50000.0, '2027-02-15', 'shopping'),
        ('Education Fund', 'Course certifications', 120000.0, 30000.0, '2027-06-30', 'education')
    ]
    
    for goal in goals:
        cursor.execute('''
            INSERT INTO financial_goals (name, description, target_amount, current_amount, target_date, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*goal, now_str, now_str))

    print(f"Inserted {len(goals)} financial goals.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed FinSight database with demonstration data.")
    parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()

    if args.reset:
        backup_db()
        clear_db()
        
    insert_demo_data()
    print("Seeding completed successfully.")
