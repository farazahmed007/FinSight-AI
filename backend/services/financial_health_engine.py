import pandas as pd
from datetime import datetime, timedelta
from .budget_engine import BudgetEngine
from .goals_engine import GoalsEngine
from .analytics import AnalyticsEngine
from database import get_db_connection

class FinancialHealthEngine:
    def __init__(self, user_id: str, transactions_df: pd.DataFrame):
        self.user_id = user_id
        self.transactions_df = transactions_df
        if not self.transactions_df.empty and not pd.api.types.is_datetime64_any_dtype(self.transactions_df['timestamp']):
            self.transactions_df['timestamp'] = pd.to_datetime(self.transactions_df['timestamp'])

    def calculate_savings_score(self) -> float:
        if self.transactions_df.empty:
            return 50.0

        analytics_engine = AnalyticsEngine(self.transactions_df)
        totals = analytics_engine.get_period_totals(days=90, offset_days=0)
        
        income = totals['income']
        expense = totals['expense']
        
        if income == 0:
            if expense > 0:
                return 20.0
            return 50.0

        savings_rate = (income - expense) / income * 100

        # Score mapping:
        # > 30% savings rate = 100
        # 20% = 80
        # 10% = 60
        # 0% = 40
        # < 0 = max(0, 40 + savings_rate * 2)
        if savings_rate >= 30:
            return 100.0
        elif savings_rate > 0:
            return 40.0 + (savings_rate * 2)
        else:
            return max(0.0, 40.0 + (savings_rate * 2))

    def calculate_budget_discipline_score(self) -> float:
        current_month = datetime.now().strftime('%Y-%m')
        budget_engine = BudgetEngine(self.user_id, self.transactions_df)
        summary = budget_engine.get_summary(current_month)
        
        if not summary['categories']:
            return 60.0 # Neutral score if no budgets

        total_categories = len(summary['categories'])
        score_sum = 0
        
        for cat in summary['categories']:
            usage = cat['usage_percentage']
            if usage <= 80:
                score_sum += 100
            elif usage <= 100:
                score_sum += 100 - ((usage - 80) * 2.5) # scales down to 50 at 100%
            elif usage <= 150:
                score_sum += max(0, 50 - ((usage - 100) * 1.0))
            else:
                score_sum += 0

        return score_sum / total_categories

    def calculate_goal_progress_score(self) -> float:
        goals_engine = GoalsEngine(self.user_id, self.transactions_df)
        goals = [g for g in goals_engine.get_all_goals() if g['status'] != 'COMPLETED']
        
        if not goals:
            return 60.0

        total_goals = len(goals)
        score_sum = 0
        
        for goal in goals:
            status = goal['status']
            if status == 'ON_TRACK' or status == 'NEAR_TARGET':
                score_sum += 100
            elif status == 'AT_RISK':
                score_sum += 60
            elif status == 'BEHIND':
                score_sum += 30
            else:
                score_sum += 50
                
        return score_sum / total_goals

    def calculate_spending_control_score(self) -> float:
        if self.transactions_df.empty:
            return 60.0

        analytics_engine = AnalyticsEngine(self.transactions_df)
        
        last_30_totals = analytics_engine.get_period_totals(days=30, offset_days=0)
        prev_30_totals = analytics_engine.get_period_totals(days=30, offset_days=30)
        
        last_30 = last_30_totals['expense']
        prev_30 = prev_30_totals['expense']

        base_score = 70.0
        
        if prev_30 > 0:
            change = (last_30 - prev_30) / prev_30 * 100
            if change <= -10:
                base_score += 20 # improved spending
            elif change <= 5:
                base_score += 10 # stable spending
            elif change > 20:
                base_score -= 30 # increased significantly
            elif change > 5:
                base_score -= 15 # increased slightly
                
        # Cap at 100
        return min(100.0, max(0.0, base_score))

    def calculate_stability_score(self) -> float:
        if self.transactions_df.empty:
            return 60.0

        # Group by month and look at variance in income and expenses
        df = self.transactions_df.copy()
        df['month'] = df['timestamp'].dt.to_period('M')
        monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        
        if len(monthly) < 2:
            return 65.0
            
        if 'income' in monthly:
            inc_var = monthly['income'].std() / (monthly['income'].mean() + 1)
        else:
            inc_var = 1.0
            
        if 'expense' in monthly:
            exp_var = monthly['expense'].std() / (monthly['expense'].mean() + 1)
        else:
            exp_var = 1.0

        score = 100.0
        # Higher variance -> lower score
        if pd.notna(inc_var):
            score -= min(30, inc_var * 30)
        if pd.notna(exp_var):
            score -= min(30, exp_var * 30)

        return min(100.0, max(0.0, score))

    def calculate_overall_health(self) -> dict:
        savings_score = self.calculate_savings_score()
        budget_score = self.calculate_budget_discipline_score()
        goal_score = self.calculate_goal_progress_score()
        spending_score = self.calculate_spending_control_score()
        stability_score = self.calculate_stability_score()

        # Weights based on spec
        overall = (
            savings_score * 0.25 +
            budget_score * 0.20 +
            goal_score * 0.20 +
            spending_score * 0.20 +
            stability_score * 0.15
        )

        overall = round(overall)
        
        status = self._get_status(overall)

        breakdown = {
            "savings": round(savings_score),
            "budget_discipline": round(budget_score),
            "goal_progress": round(goal_score),
            "spending_control": round(spending_score),
            "financial_stability": round(stability_score)
        }

        self._save_snapshot(overall, breakdown)

        return {
            "score": overall,
            "status": status,
            "breakdown": breakdown
        }

    def _get_status(self, score: float) -> str:
        if score < 40:
            return "CRITICAL"
        elif score < 60:
            return "NEEDS IMPROVEMENT"
        elif score < 75:
            return "FAIR"
        elif score < 90:
            return "GOOD"
        else:
            return "EXCELLENT"

    def _save_snapshot(self, overall: int, breakdown: dict):
        # Save snapshot if last snapshot was more than 1 day ago to prevent spam
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_health_snapshots'")
        if not cursor.fetchone():
            conn.close()
            return
            
        cursor.execute(
            "SELECT created_at FROM financial_health_snapshots WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (self.user_id,)
        )
        row = cursor.fetchone()
        
        should_save = True
        if row:
            last_created = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
            if (datetime.now() - last_created).days < 1:
                should_save = False
                
        if should_save:
            cursor.execute(
                """
                INSERT INTO financial_health_snapshots 
                (user_id, score, savings_score, budget_score, goal_score, spending_score, stability_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self.user_id, overall, breakdown['savings'], breakdown['budget_discipline'], 
                 breakdown['goal_progress'], breakdown['spending_control'], breakdown['financial_stability'])
            )
            conn.commit()
            
        conn.close()

    def get_history(self) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_health_snapshots'")
        if not cursor.fetchone():
            conn.close()
            return []
            
        cursor.execute(
            "SELECT * FROM financial_health_snapshots WHERE user_id = ? ORDER BY created_at ASC",
            (self.user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
