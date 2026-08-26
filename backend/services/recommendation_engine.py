import pandas as pd
from typing import List, Dict, Any
from .preprocessing import aggregate_daily_transactions
from .forecasting import ForecastingEngine
from .budget_engine import BudgetEngine
from .goals_engine import GoalsEngine
from datetime import datetime

class RecommendationEngine:
    def __init__(self, df: pd.DataFrame, user_id: str = None):
        self.df = df
        self.user_id = user_id
        
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        if self.df.empty:
            return []
            
        recommendations = []
        
        # Inject budget checking logic if user_id is provided
        if self.user_id:
            current_month = datetime.now().strftime('%Y-%m')
            budget_engine = BudgetEngine(self.user_id, self.df)
            budget_summary = budget_engine.get_summary(current_month)
            
            for cat_summary in budget_summary['categories']:
                status = cat_summary['status']
                cat = cat_summary['category']
                variance = cat_summary['variance']
                usage = cat_summary['usage_percentage']
                
                if status == 'OVER_BUDGET':
                    recommendations.append({
                        "category": cat,
                        "type": "budget_alert",
                        "severity": "high",
                        "message": f"Your {cat.capitalize()} budget is overspent by ₹{variance:,.2f}.",
                        "reason": f"You have spent {usage}% of your {cat} budget.",
                        "suggested_action": f"Review {cat} expenses immediately."
                    })
                elif status == 'NEAR_LIMIT':
                    recommendations.append({
                        "category": cat,
                        "type": "budget_alert",
                        "severity": "medium",
                        "message": f"Your {cat.capitalize()} budget is almost exhausted.",
                        "reason": f"You have spent {usage}% of your {cat} budget.",
                        "suggested_action": f"Be careful with further {cat} spending this month."
                    })
                elif status == 'ON_TRACK' and usage < 50 and cat_summary['budget'] > 0 and datetime.now().day > 20:
                    recommendations.append({
                        "category": cat,
                        "type": "budget_alert",
                        "severity": "low",
                        "message": f"You are consistently spending below your {cat.capitalize()} budget.",
                        "reason": f"You have only spent {usage}% of your {cat} budget late in the month.",
                        "suggested_action": f"Consider reallocating some of your {cat} budget to savings."
                    })
                    
        # We'll analyze each major category's trend
        categories = self.df[self.df['type'] == 'expense']['category'].unique()
        
        for category in categories:
            if category == 'uncategorized':
                continue
                
            daily_df = aggregate_daily_transactions(self.df, category=category)
            if len(daily_df) < 14: # Need at least 2 weeks to make any sort of recommendation
                continue
                
            engine = ForecastingEngine(daily_df)
            forecast = engine.forecast_category(category, horizon_days=30)
            
            trend = forecast['trend']
            
            if trend == 'increasing':
                if category == 'food':
                    recommendations.append({
                        "category": category,
                        "type": "alert",
                        "severity": "medium",
                        "message": "Your food spending is trending upward.",
                        "reason": "Your food expenditure has increased consistently over recent weeks.",
                        "suggested_action": "Consider setting a weekly food budget and cooking more meals at home."
                    })
                elif category == 'subscriptions':
                    recommendations.append({
                        "category": category,
                        "type": "alert",
                        "severity": "high",
                        "message": "Your subscription spending is increasing.",
                        "reason": "You might have added new subscriptions recently.",
                        "suggested_action": "Review your active subscriptions and cancel unused ones."
                    })
                else:
                    recommendations.append({
                        "category": category,
                        "type": "alert",
                        "severity": "medium",
                        "message": f"Your {category} spending is trending upward.",
                        "reason": f"Historical data shows an increasing trend in {category} expenses.",
                        "suggested_action": f"Review your {category} expenses and identify areas to cut back."
                    })
                    
        # Inject goals checking logic if user_id is provided
        if self.user_id:
            goals_engine = GoalsEngine(self.user_id, self.df)
            active_goals = [g for g in goals_engine.get_all_goals() if g['status'] != 'COMPLETED']
            
            for goal in active_goals:
                status = goal['status']
                name = goal['name']
                remaining = goal['remaining_amount']
                req_savings = goal['required_monthly_savings']
                
                if status == 'BEHIND':
                    recommendations.append({
                        "category": goal.get('category') or "general",
                        "type": "goal_alert",
                        "severity": "high",
                        "message": f"You are falling behind on your goal: {name}.",
                        "reason": f"At your current savings pace, you will not reach the target date. You need to save approximately ₹{req_savings:,.2f} per month.",
                        "suggested_action": f"Increase your monthly savings by reviewing discretionary spending."
                    })
                elif status == 'AT_RISK':
                    recommendations.append({
                        "category": goal.get('category') or "general",
                        "type": "goal_alert",
                        "severity": "medium",
                        "message": f"Your goal '{name}' is at risk of missing the target date.",
                        "reason": f"Your savings pace is slightly below the required ₹{req_savings:,.2f}/month.",
                        "suggested_action": "Try to allocate a small extra amount to this goal this month."
                    })
                elif status == 'NEAR_TARGET':
                    recommendations.append({
                        "category": goal.get('category') or "general",
                        "type": "goal_alert",
                        "severity": "low",
                        "message": f"You are very close to achieving your goal: {name}!",
                        "reason": f"You only have ₹{remaining:,.2f} left to save.",
                        "suggested_action": "Keep up the great work! Consider pushing a little extra to finish it early."
                    })

        # Overall savings rate check
        income_df = self.df[self.df['type'] == 'income']
        expense_df = self.df[self.df['type'] == 'expense']
        
        # Check last 30 days
        max_date = self.df['timestamp'].max()
        cutoff = max_date - pd.Timedelta(days=30)
        
        recent_income = income_df[income_df['timestamp'] >= cutoff]['amount'].sum()
        recent_expense = expense_df[expense_df['timestamp'] >= cutoff]['amount'].sum()
        
        if recent_income > 0:
            savings_rate = (recent_income - recent_expense) / recent_income
            if savings_rate < 0.1:
                recommendations.append({
                    "category": "general",
                    "type": "warning",
                    "severity": "high",
                    "message": "Your recent savings rate is very low.",
                    "reason": "You have saved less than 10% of your income over the last 30 days.",
                    "suggested_action": "Try to follow the 50/30/20 budgeting rule to increase your savings."
                })
            elif savings_rate > 0.4:
                recommendations.append({
                    "category": "general",
                    "type": "success",
                    "severity": "low",
                    "message": "Excellent savings rate!",
                    "reason": f"You saved {round(savings_rate*100)}% of your income in the last 30 days.",
                    "suggested_action": "Consider investing your surplus savings."
                })
                
        # Sort recommendations by severity (high -> medium -> low -> success)
        severity_map = {"high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: severity_map.get(x['severity'], 99))
        
        return recommendations
