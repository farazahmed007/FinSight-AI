import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'finance.db')

def migrate_database():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. USERS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Ensured users table exists.")

    # Insert default prototype user if not exists
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES ('user_123', 'prototype_user')")
    print("Ensured default prototype user_123 exists.")

    # 2. BUDGETS MIGRATION
    # Check if user_id exists in budgets
    cursor.execute("PRAGMA table_info(budgets)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'user_id' not in columns:
        print("Migrating budgets table...")
        # Create temp table
        cursor.execute('''
        CREATE TABLE budgets_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'user_123',
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, category, month)
        )
        ''')
        
        # Copy data
        cursor.execute('''
        INSERT INTO budgets_new (id, user_id, category, amount, month, created_at, updated_at)
        SELECT id, 'user_123', category, amount, month, created_at, updated_at FROM budgets
        ''')
        
        # Drop old and rename
        cursor.execute("DROP TABLE budgets")
        cursor.execute("ALTER TABLE budgets_new RENAME TO budgets")
        print("Migrated budgets table successfully.")
    else:
        print("budgets table already has user_id.")

    # 3. FINANCIAL GOALS MIGRATION
    cursor.execute("PRAGMA table_info(financial_goals)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'user_id' not in columns:
        print("Migrating financial_goals table...")
        cursor.execute('''
        CREATE TABLE financial_goals_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'user_123',
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
        INSERT INTO financial_goals_new (id, user_id, name, description, target_amount, current_amount, target_date, category, created_at, updated_at)
        SELECT id, 'user_123', name, description, target_amount, current_amount, target_date, category, created_at, updated_at FROM financial_goals
        ''')
        
        cursor.execute("DROP TABLE financial_goals")
        cursor.execute("ALTER TABLE financial_goals_new RENAME TO financial_goals")
        print("Migrated financial_goals table successfully.")
    else:
        print("financial_goals table already has user_id.")

    conn.commit()
    conn.close()
    print("Database migration complete.")

if __name__ == "__main__":
    migrate_database()
