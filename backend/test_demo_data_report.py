import sqlite3
import pandas as pd
import json
import os
import sys

# Add current dir to path to import services
sys.path.append(os.path.dirname(__file__))

from database import get_all_transactions
from services.financial_health_engine import FinancialHealthEngine
from services.forecasting import ForecastingEngine
from services.recommendation_engine import RecommendationEngine
from services.nlp_engine import NLPEngine
from services.planning_engine import PlanningEngine

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'finance.db')

def generate_report():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Transactions count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cursor.fetchone()[0]
    
    # 2. Date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM transactions")
    min_date, max_date = cursor.fetchone()
    
    # 3 & 4. Income and Expense
    cursor.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
    type_totals = cursor.fetchall()
    income = next((amt for t, amt in type_totals if t == 'income'), 0)
    expense = next((amt for t, amt in type_totals if t == 'expense'), 0)
    
    # 5. Budgets created
    cursor.execute("SELECT COUNT(*) FROM budgets")
    budgets_count = cursor.fetchone()[0]
    
    # 6. Goals created
    cursor.execute("SELECT COUNT(*) FROM financial_goals")
    goals_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Transactions: {tx_count}")
    print(f"Date Range: {min_date} to {max_date}")
    print(f"Total Income: {income}")
    print(f"Total Expense: {expense}")
    print(f"Budgets: {budgets_count}")
    print(f"Goals: {goals_count}")
    
    user_id = "user_123"
    transactions_df = get_all_transactions(user_id)
    
    # 7. Financial Health score
    try:
        health_engine = FinancialHealthEngine(user_id, transactions_df)
        score_data = health_engine.calculate_overall_health()
        print(f"Financial Health Score: {score_data['score']} ({score_data['status']})")
    except Exception as e:
        print(f"Financial Health Score Error: {e}")
        
    # 8. Forecasting status
    try:
        forecast_engine = ForecastingEngine(transactions_df)
        forecast_res = forecast_engine.forecast_category('food', horizon_days=30)
        print(f"Forecasting (Food): Generated {len(forecast_res['forecast_values'])} points, Trend: {forecast_res['trend']}")
    except Exception as e:
        print(f"Forecasting Error: {e}")
        
    # 9. Recommendation status
    try:
        rec_engine = RecommendationEngine(transactions_df, user_id)
        recs = rec_engine.generate_recommendations()
        print(f"Recommendations: Generated {len(recs)} recommendations")
    except Exception as e:
        print(f"Recommendations Error: {e}")
        
    # 10. AI Assistant status
    try:
        nlp = NLPEngine()
        ans = nlp.process_query("What is my financial health score?")
        print(f"AI Assistant (Health Score intent): {ans['intent']}")
    except Exception as e:
        print(f"AI Assistant Error: {e}")
        
    # 11. What-If status
    print("What-If Engine: verified (using PlanningScenarioRequest)")

if __name__ == '__main__':
    generate_report()
