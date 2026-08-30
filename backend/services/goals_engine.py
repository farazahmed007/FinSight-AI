import pandas as pd
from datetime import datetime, timedelta
import math
from database import get_db_connection

class GoalsEngine:
    def __init__(self, user_id: str, transactions_df: pd.DataFrame = None):
        self.user_id = user_id
        self.transactions_df = transactions_df
        if self.transactions_df is not None and not self.transactions_df.empty:
            if not pd.api.types.is_datetime64_any_dtype(self.transactions_df['timestamp']):
                self.transactions_df['timestamp'] = pd.to_datetime(self.transactions_df['timestamp'])

    def _calculate_metrics(self, goal: dict, active_goals_count: int = 1) -> dict:
        target_amount = float(goal['target_amount'])
        current_amount = float(goal['current_amount'])
        target_date_str = goal['target_date']
        
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        now = datetime.now()
        
        remaining_amount = max(0.0, target_amount - current_amount)
        progress_percentage = min(100.0, (current_amount / target_amount) * 100) if target_amount > 0 else 0.0
        
        # Calculate remaining days (minimum 1 day to avoid division by zero)
        remaining_days = max(1, (target_date - now).days)
        remaining_months = remaining_days / 30.44
        
        required_monthly_savings = remaining_amount / remaining_months if remaining_months > 0 else remaining_amount
        
        # Calculate actual savings pace
        actual_monthly_savings = 0.0
        if self.transactions_df is not None and not self.transactions_df.empty:
            # Last 90 days to determine pace
            cutoff = now - timedelta(days=90)
            recent_df = self.transactions_df[self.transactions_df['timestamp'] >= cutoff]
            income = recent_df[recent_df['type'] == 'income']['amount'].sum()
            expense = recent_df[recent_df['type'] == 'expense']['amount'].sum()
            net_savings = max(0.0, float(income - expense))
            
            # Average per month over the last 3 months
            total_monthly_savings = net_savings / 3.0
            
            # Divide savings evenly among active goals
            if active_goals_count > 0:
                actual_monthly_savings = total_monthly_savings / active_goals_count
            else:
                actual_monthly_savings = total_monthly_savings
            
        # Projected completion date
        projected_completion_date = None
        if remaining_amount == 0:
            status = "COMPLETED"
        else:
            if actual_monthly_savings > 0:
                months_needed = remaining_amount / actual_monthly_savings
                projected_completion = now + timedelta(days=months_needed * 30.44)
                projected_completion_date = projected_completion.strftime("%Y-%m-%d")
                
                # Determine status
                if projected_completion <= target_date:
                    status = "ON_TRACK"
                elif (projected_completion - target_date).days <= 30:
                    status = "AT_RISK"
                else:
                    status = "BEHIND"
            else:
                status = "BEHIND"
                
            if progress_percentage >= 90 and status != "BEHIND":
                status = "NEAR_TARGET"

        goal['progress_percentage'] = round(progress_percentage, 2)
        goal['remaining_amount'] = round(remaining_amount, 2)
        goal['status'] = status
        goal['required_monthly_savings'] = round(required_monthly_savings, 2)
        goal['projected_completion_date'] = projected_completion_date
        
        return goal

    def get_all_goals(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_goals'")
        if not cursor.fetchone():
            conn.close()
            return []
            
        cursor.execute("SELECT * FROM financial_goals WHERE user_id = ? ORDER BY target_date ASC", (self.user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        goals = [dict(row) for row in rows]
        
        # Determine number of active (non-completed) goals
        active_count = sum(1 for g in goals if max(0.0, float(g['target_amount']) - float(g['current_amount'])) > 0)
        
        for g in goals:
            self._calculate_metrics(g, active_goals_count=active_count)
            
        return goals

    def get_goal(self, goal_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financial_goals WHERE id = ? AND user_id = ?", (goal_id, self.user_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            goal = dict(row)
            
            # We need to know total active goals to calculate pace for this single goal
            conn_temp = get_db_connection()
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute("SELECT target_amount, current_amount FROM financial_goals WHERE user_id = ?", (self.user_id,))
            all_rows = cursor_temp.fetchall()
            active_count = sum(1 for r in all_rows if max(0.0, float(r['target_amount']) - float(r['current_amount'])) > 0)
            conn_temp.close()
            
            self._calculate_metrics(goal, active_goals_count=active_count)
            return goal
        return None

    def create_goal(self, data: dict):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO financial_goals (user_id, name, description, target_amount, current_amount, target_date, category) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.user_id,
                data['name'], 
                data.get('description'), 
                data['target_amount'], 
                data.get('current_amount', 0.0), 
                data['target_date'], 
                data.get('category')
            )
        )
        conn.commit()
        goal_id = cursor.lastrowid
        conn.close()
        
        return self.get_goal(goal_id)

    def update_goal(self, goal_id: int, data: dict):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        params = []
        for key, value in data.items():
            if value is not None:
                update_fields.append(f"{key} = ?")
                params.append(value)
                
        if not update_fields:
            conn.close()
            return self.get_goal(goal_id)
            
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(goal_id)
        params.append(self.user_id)
        
        query = f"UPDATE financial_goals SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return self.get_goal(goal_id)

    def delete_goal(self, goal_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financial_goals WHERE id = ? AND user_id = ?", (goal_id, self.user_id))
        conn.commit()
        conn.close()
        return True

    def get_summary(self):
        goals = self.get_all_goals()
        
        total_goals = len(goals)
        active_goals = sum(1 for g in goals if g['status'] != 'COMPLETED')
        completed_goals = total_goals - active_goals
        
        total_target = sum(g['target_amount'] for g in goals)
        total_saved = sum(g['current_amount'] for g in goals)
        total_remaining = sum(g['remaining_amount'] for g in goals)
        total_required_monthly_savings = sum(g['required_monthly_savings'] for g in goals if g['status'] != 'COMPLETED')
        
        overall_progress = (total_saved / total_target * 100) if total_target > 0 else 0.0
        
        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "total_target": round(total_target, 2),
            "total_saved": round(total_saved, 2),
            "total_remaining": round(total_remaining, 2),
            "overall_progress": round(overall_progress, 2),
            "total_required_monthly_savings": round(total_required_monthly_savings, 2)
        }
