import sqlite3
import pandas as pd
import os
from services.preprocessing import clean_transactions

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'finance.db')
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'transactions.csv')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        user_id TEXT,
        timestamp DATETIME,
        amount REAL,
        category TEXT,
        merchant TEXT,
        type TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        month TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(category, month)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        target_amount REAL NOT NULL CHECK(target_amount > 0),
        current_amount REAL NOT NULL DEFAULT 0 CHECK(current_amount >= 0),
        target_date TEXT NOT NULL,
        category TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_health_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        score INTEGER NOT NULL,
        savings_score INTEGER NOT NULL,
        budget_score INTEGER NOT NULL,
        goal_score INTEGER NOT NULL,
        spending_score INTEGER NOT NULL,
        stability_score INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def load_seed_data():
    if not os.path.exists(CSV_PATH):
        print(f"Seed data {CSV_PATH} not found.")
        return
        
    df = pd.read_csv(CSV_PATH)
    cleaned_df = clean_transactions(df)
    
    # Store string formatted timestamp
    cleaned_df['timestamp'] = cleaned_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    # Use to_sql to insert data, replacing if exists
    cleaned_df.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()
    print("Database initialized with seed data.")

def get_all_transactions(user_id="user_123"):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    # Convert timestamp back to datetime for internal usage
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

if __name__ == "__main__":
    init_db()
    load_seed_data()
