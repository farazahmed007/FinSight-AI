import pandas as pd
from typing import List, Dict, Any
from .preprocessing import aggregate_daily_transactions
from .forecasting import ForecastingEngine
from .budget_engine import BudgetEngine
from .goals_engine import GoalsEngine
from .analytics import AnalyticsEngine
from .financial_health_engine import FinancialHealthEngine
from datetime import datetime

class RecommendationEngine:
    def __init__(self, df: pd.DataFrame, user_id: str = None):
        self.df = df
        self.user_id = user_id
        
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        if self.df.empty:
            return []
            
        recommendations = []
        
        # 1. Budget Alerts
        if self.user_id:
            current_month = datetime.now().strftime('%Y-%m')
            budget_engine = BudgetEngine(self.user_id, self.df)
            budget_summary = budget_engine.get_summary(current_month)
            
            for cat_summary in budget_summary['categories']:
                status = cat_summary['status']
                cat = cat_summary['category']
                variance = cat_summary['variance']
                usage = cat_summary['usage_percentage']
                budget_amt = cat_summary['budget']
                
                if status == 'OVER_BUDGET':
                    recommendations.append({
                        "category": cat,
                        "type": "budget_alert",
                        "severity": "high",
                        "message": f"Your {cat.capitalize()} budget is overspent.",
                        "reason": f"You have spent {usage}% of your ₹{budget_amt:,.0f} {cat} budget.",
                        "suggested_action": f"Reduce {cat} expenses by at least ₹{variance:,.0f} next month to recover."
                    })
                elif status == 'NEAR_LIMIT':
                    recommendations.append({
                        "category": cat,
                        "type": "budget_alert",
                        "severity": "medium",
                        "message": f"Your {cat.capitalize()} budget is almost exhausted.",
                        "reason": f"You have spent {usage}% of your {cat} budget.",
                        "suggested_action": f"Limit further {cat} spending this month."
                    })
                elif status == 'ON_TRACK' and usage < 50 and budget_amt > 0 and datetime.now().day > 20:
                    surplus = budget_amt - cat_summary['spent']
                    recommendations.append({
                        "category": cat,
                        "type": "budget_alert",
                        "severity": "low",
                        "message": f"You are consistently spending below your {cat.capitalize()} budget.",
                        "reason": f"You have ₹{surplus:,.0f} remaining late in the month.",
                        "suggested_action": f"Consider reallocating ₹{surplus:,.0f} to savings or a financial goal."
                    })
                    
        # 2. Spending Trend Alerts
        categories = self.df[self.df['type'] == 'expense']['category'].unique()
        for category in categories:
            if category == 'uncategorized':
                continue
                
            daily_df = aggregate_daily_transactions(self.df, category=category)
            if len(daily_df) < 14:
                continue
                
            engine = ForecastingEngine(daily_df)
            forecast = engine.forecast_category(category, horizon_days=30)
            
            trend = forecast['trend']
            if trend == 'increasing':
                severity = 'high' if category == 'subscriptions' else 'medium'
                recommendations.append({
                    "category": category,
                    "type": "alert",
                    "severity": severity,
                    "message": f"Your {category} spending is trending upward.",
                    "reason": f"Based on recent data, {category} expenses are accelerating.",
                    "suggested_action": f"Review {category} and simulate a reduction in the What-If planner."
                })
                    
        # 3. Goal Alerts
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
                        "reason": f"You need to save ₹{req_savings:,.0f} per month to hit your target date.",
                        "suggested_action": f"Use the What-If simulator to find ₹{req_savings:,.0f} in savings."
                    })
                elif status == 'AT_RISK':
                    recommendations.append({
                        "category": goal.get('category') or "general",
                        "type": "goal_alert",
                        "severity": "medium",
                        "message": f"Your goal '{name}' is at risk.",
                        "reason": f"Your savings pace is slightly below the required ₹{req_savings:,.0f}/month.",
                        "suggested_action": "Try to allocate a small extra amount this month."
                    })
                elif status == 'NEAR_TARGET':
                    recommendations.append({
                        "category": goal.get('category') or "general",
                        "type": "goal_alert",
                        "severity": "low",
                        "message": f"You are very close to achieving your goal: {name}!",
                        "reason": f"You only have ₹{remaining:,.0f} left to save.",
                        "suggested_action": "Keep up the great work to finish it early."
                    })

        # 4. Savings Rate Check (using AnalyticsEngine)
        analytics = AnalyticsEngine(self.df)
        totals = analytics.get_period_totals(days=30)
        recent_income = totals['income']
        recent_expense = totals['expense']
        
        if recent_income > 0:
            savings_rate = (recent_income - recent_expense) / recent_income
            if savings_rate < 0.1:
                recommendations.append({
                    "category": "general",
                    "type": "warning",
                    "severity": "high",
                    "message": "Your recent savings rate is very low.",
                    "reason": f"You saved {round(savings_rate*100)}% of your income over the last 30 days.",
                    "suggested_action": "Use the What-If planner to target a 20% savings rate."
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
                
        # 5. Financial Health Alerts
        if self.user_id:
            health_engine = FinancialHealthEngine(self.user_id, self.df)
            health_data = health_engine.calculate_overall_health()
            if health_data['status'] in ['Needs Attention', 'Critical']:
                # Find the weakest component
                components = health_data['breakdown']
                weakest = min(components.items(), key=lambda x: x[1]['score'])
                weak_name, weak_data = weakest
                
                recommendations.append({
                    "category": "health",
                    "type": "health_alert",
                    "severity": "high",
                    "message": f"Your {weak_name.replace('_', ' ').capitalize()} needs attention.",
                    "reason": f"This is pulling down your overall financial health score.",
                    "suggested_action": weak_data.get('insight', "Review this area of your finances.")
                })

        # Resolve Conflicts
        recommendations = self._resolve_conflicts(recommendations)
        
        # Sort recommendations by severity (high -> medium -> low -> success)
        severity_map = {"high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: severity_map.get(x['severity'], 99))
        
        return recommendations
        
    def _resolve_conflicts(self, recs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Suppresses contradictory recommendations.
        - If the user has a high-severity goal alert (BEHIND), suppress "invest surplus" success messages.
        - If the user has a low savings rate (<10%), suppress "reallocate surplus budget" messages.
        """
        has_behind_goal = any(r for r in recs if r['type'] == 'goal_alert' and r['severity'] == 'high')
        has_low_savings = any(r for r in recs if r['type'] == 'warning' and 'savings rate' in r['message'].lower())
        
        filtered = []
        for r in recs:
            # Suppress "invest surplus savings" if they are behind on a goal
            if r['type'] == 'success' and 'investing your surplus' in r['suggested_action'].lower() and has_behind_goal:
                continue
                
            # Suppress "reallocate surplus budget" if they have an objectively terrible savings rate overall
            if r['type'] == 'budget_alert' and r['severity'] == 'low' and 'reallocating' in r['suggested_action'].lower() and has_low_savings:
                continue
                
            filtered.append(r)
            
        return filtered
