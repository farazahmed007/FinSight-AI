import pandas as pd
from datetime import datetime
from database import get_db_connection

class BudgetEngine:
    def __init__(self, user_id: str, transactions_df: pd.DataFrame):
        self.user_id = user_id
        self.transactions_df = transactions_df
        # Ensure timestamp is datetime
        if not self.transactions_df.empty and not pd.api.types.is_datetime64_any_dtype(self.transactions_df['timestamp']):
            self.transactions_df['timestamp'] = pd.to_datetime(self.transactions_df['timestamp'])

    def _get_status(self, usage_percentage: float) -> str:
        if usage_percentage >= 100:
            return "OVER_BUDGET"
        elif usage_percentage >= 90:
            return "NEAR_LIMIT"
        elif usage_percentage >= 70:
            return "WATCH"
        return "ON_TRACK"

    def get_budgets_for_month(self, month: str):
        conn = get_db_connection()
        # Ensure budgets table is initialized for query
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='budgets'")
        if not cursor.fetchone():
            conn.close()
            return []
            
        cursor.execute(
            "SELECT * FROM budgets WHERE month = ? AND user_id = ?",
            (month, self.user_id)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_summary(self, month: str):
        budgets = self.get_budgets_for_month(month)
        
        # Filter transactions for the given month
        # month format is YYYY-MM
        year, m = month.split('-')
        
        month_transactions = pd.DataFrame()
        if not self.transactions_df.empty:
            month_transactions = self.transactions_df[
                (self.transactions_df['timestamp'].dt.year == int(year)) & 
                (self.transactions_df['timestamp'].dt.month == int(m))
            ]

        total_budget = sum(b['amount'] for b in budgets)
        
        category_summaries = []
        alerts = []
        total_spent = 0
        
        for budget in budgets:
            cat = budget['category']
            budget_amount = budget['amount']
            
            spent = 0.0
            if not month_transactions.empty:
                cat_txs = month_transactions[month_transactions['category'] == cat]
                spent = float(cat_txs['amount'].sum())
            
            total_spent += spent
            remaining = max(0, budget_amount - spent)
            variance = spent - budget_amount
            usage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            status = self._get_status(usage)
            
            category_summaries.append({
                "category": cat,
                "budget": budget_amount,
                "spent": spent,
                "remaining": remaining,
                "usage_percentage": round(usage, 2),
                "status": status,
                "variance": variance
            })
            
            # Generate Alerts
            if status == "OVER_BUDGET":
                alerts.append({
                    "type": "OVER_BUDGET",
                    "message": f"You have exceeded your {cat.capitalize()} budget by ₹{variance:,.2f}."
                })
            elif status == "NEAR_LIMIT":
                alerts.append({
                    "type": "NEAR_LIMIT",
                    "message": f"{cat.capitalize()} spending has reached {round(usage)}% of your monthly budget."
                })

        overall_usage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        return {
            "month": month,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining_budget": max(0, total_budget - total_spent),
            "usage_percentage": round(overall_usage, 2),
            "categories": category_summaries,
            "alerts": alerts
        }

    def create_budget(self, category: str, amount: float, month: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO budgets (user_id, category, amount, month) 
                VALUES (?, ?, ?, ?)
                """,
                (self.user_id, category, amount, month)
            )
            conn.commit()
            budget_id = cursor.lastrowid
        except Exception as e:
            conn.close()
            raise e
        
        cursor.execute("SELECT * FROM budgets WHERE id = ? AND user_id = ?", (budget_id, self.user_id))
        budget = dict(cursor.fetchone())
        conn.close()
        return budget

    def update_budget(self, budget_id: int, amount: float):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE budgets 
            SET amount = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
            """,
            (amount, budget_id, self.user_id)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM budgets WHERE id = ? AND user_id = ?", (budget_id, self.user_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    def delete_budget(self, budget_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, self.user_id))
        conn.commit()
        conn.close()
        return True

    def get_budget(self, budget_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets WHERE id = ? AND user_id = ?", (budget_id, self.user_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
