import pandas as pd
from datetime import datetime, timedelta
from .budget_engine import BudgetEngine
from .goals_engine import GoalsEngine
from .forecasting import ForecastingEngine
from .recommendation_engine import RecommendationEngine
from .preprocessing import aggregate_daily_transactions

class FinancialInsightsEngine:
    def __init__(self, user_id: str, transactions_df: pd.DataFrame, health_data: dict):
        self.user_id = user_id
        self.transactions_df = transactions_df
        self.health_data = health_data
        if not self.transactions_df.empty and not pd.api.types.is_datetime64_any_dtype(self.transactions_df['timestamp']):
            self.transactions_df['timestamp'] = pd.to_datetime(self.transactions_df['timestamp'])

    def generate_insights(self) -> dict:
        insights = []
        strengths = []
        weaknesses = []
        improvements = []

        breakdown = self.health_data['breakdown']
        
        # 1. Savings Insights
        savings_score = breakdown['savings']
        if savings_score >= 80:
            strengths.append("High savings rate")
            insights.append({
                "type": "savings",
                "severity": "success",
                "title": "Excellent Savings Habits",
                "message": "Your savings rate is very healthy.",
                "reason": "You are saving a significant portion of your income.",
                "category": "general",
                "suggested_action": "Consider investing excess savings to accelerate wealth building."
            })
        elif savings_score < 50:
            weaknesses.append("Low savings rate")
            insights.append({
                "type": "savings",
                "severity": "warning",
                "title": "Savings Opportunity",
                "message": "Your savings rate has room for improvement.",
                "reason": "Your expenses are consuming most of your income.",
                "category": "general",
                "suggested_action": "Try to reduce discretionary spending to increase your monthly savings."
            })
            improvements.append({
                "action": "Improve savings rate to at least 20%",
                "estimated_points": 5
            })

        # 2. Budget Insights
        budget_score = breakdown['budget_discipline']
        if budget_score >= 80:
            strengths.append("Strong budget adherence")
            insights.append({
                "type": "budget",
                "severity": "success",
                "title": "Budget Discipline",
                "message": "You're staying within most of your monthly budgets.",
                "reason": "Most of your categories are under their set limits.",
                "category": "general",
                "suggested_action": "Keep tracking your expenses to maintain this discipline."
            })
        elif budget_score < 60:
            weaknesses.append("Budget overspending")
            insights.append({
                "type": "budget",
                "severity": "warning",
                "title": "Budget Warning",
                "message": "Multiple categories have exceeded their monthly budgets.",
                "reason": "Budget discipline is currently one of the main factors affecting your score.",
                "category": "general",
                "suggested_action": "Review your highest spending categories and adjust your budget or spending."
            })
            improvements.append({
                "action": "Stay within monthly budget limits",
                "estimated_points": 4
            })

        # 3. Goals Insights
        goal_score = breakdown['goal_progress']
        if goal_score >= 80:
            strengths.append("Consistent goal progress")
            insights.append({
                "type": "goals",
                "severity": "success",
                "title": "Goals on Track",
                "message": "Your savings goals are progressing well.",
                "reason": "Your current savings pace matches or exceeds the required pace.",
                "category": "general",
                "suggested_action": "Maintain your current savings contributions."
            })
        elif goal_score < 60:
            weaknesses.append("Goals falling behind")
            insights.append({
                "type": "goals",
                "severity": "warning",
                "title": "Goal Progress Risk",
                "message": "Goal progress is currently reducing your financial health score.",
                "reason": "Some of your active goals are falling behind schedule.",
                "category": "general",
                "suggested_action": "Consider reallocating funds to get back on track."
            })
            improvements.append({
                "action": "Increase monthly contributions to goals",
                "estimated_points": 4
            })

        # 4. Spending Control Insights
        spending_score = breakdown['spending_control']
        if spending_score >= 80:
            strengths.append("Stable spending habits")
        elif spending_score < 60:
            weaknesses.append("Increasing spending trends")
            improvements.append({
                "action": "Reduce overall monthly spending by 10%",
                "estimated_points": 3
            })

        # Specific category checks for spending
        if not self.transactions_df.empty:
            expense_df = self.transactions_df[self.transactions_df['type'] == 'expense']
            now = datetime.now()
            last_30 = expense_df[expense_df['timestamp'] >= now - timedelta(days=30)]
            prev_30 = expense_df[(expense_df['timestamp'] >= now - timedelta(days=60)) & (expense_df['timestamp'] < now - timedelta(days=30))]
            
            for cat in ['shopping', 'subscriptions', 'food']:
                last_cat = last_30[last_30['category'] == cat]['amount'].sum()
                prev_cat = prev_30[prev_30['category'] == cat]['amount'].sum()
                
                if prev_cat > 0 and last_cat > prev_cat * 1.2:
                    insights.append({
                        "type": "spending",
                        "severity": "warning",
                        "title": f"{cat.capitalize()} spending is increasing",
                        "message": f"Your {cat} expenses are trending above your recent average.",
                        "reason": f"You spent ₹{last_cat:,.2f} recently compared to ₹{prev_cat:,.2f} previously.",
                        "category": cat,
                        "suggested_action": f"Review recent {cat} transactions and reduce discretionary purchases."
                    })
                    if cat == 'shopping':
                        weaknesses.append("High shopping spending")
                        improvements.append({
                            "action": "Reduce shopping spending",
                            "estimated_points": 2
                        })

        # 5. Recommendation Engine Integration
        rec_engine = RecommendationEngine(self.transactions_df, self.user_id)
        recommendations = rec_engine.generate_recommendations()
        
        for rec in recommendations:
            # Map severity to insights severity
            mapped_severity = "warning" if rec["severity"] in ["high", "medium"] else "info"
            if rec["type"] == "success":
                mapped_severity = "success"
                
            insights.append({
                "type": rec["type"],
                "severity": mapped_severity,
                "title": f"Recommendation: {rec['category'].capitalize()}",
                "message": rec["message"],
                "reason": rec["reason"],
                "category": rec["category"],
                "suggested_action": rec["suggested_action"]
            })
            
            # Map to strengths/weaknesses
            if rec["severity"] == "high":
                weaknesses.append(rec["message"])
                improvements.append({
                    "action": rec["suggested_action"],
                    "estimated_points": 3
                })
            elif rec["severity"] == "low" or rec["type"] == "success":
                strengths.append(rec["message"])

        # 6. Forecasting vs Budget checks
        if self.user_id and not self.transactions_df.empty:
            budget_engine = BudgetEngine(self.user_id, self.transactions_df)
            current_month = datetime.now().strftime('%Y-%m')
            budget_summary = budget_engine.get_summary(current_month)
            
            for cat_summary in budget_summary['categories']:
                cat = cat_summary['category']
                budget_limit = cat_summary['budget']
                
                if budget_limit > 0:
                    daily_df = aggregate_daily_transactions(self.transactions_df, category=cat)
                    if len(daily_df) >= 14:
                        engine = ForecastingEngine(daily_df)
                        forecast = engine.forecast_category(cat, horizon_days=30)
                        
                        # Compare 30-day forecast total with the budget
                        projected_total = sum(forecast['forecast_values'])
                        if projected_total > budget_limit:
                            insights.append({
                                "type": "forecast_warning",
                                "severity": "warning",
                                "title": f"{cat.capitalize()} spending projected to exceed budget",
                                "message": f"{cat.capitalize()} spending is projected to reach ₹{projected_total:,.2f}, exceeding your budget of ₹{budget_limit:,.2f}.",
                                "reason": f"Based on your current {cat} spending habits.",
                                "category": cat,
                                "suggested_action": f"Slow down your {cat} spending to avoid going over budget."
                            })
                            weaknesses.append(f"Projected overspending in {cat}")

        # Sort insights: warnings first
        severity_map = {"warning": 1, "info": 2, "success": 3}
        insights.sort(key=lambda x: severity_map.get(x['severity'], 99))

        # Deduplicate strengths/weaknesses
        strengths = list(dict.fromkeys(strengths))
        weaknesses = list(dict.fromkeys(weaknesses))

        # Calculate a summary string
        summary = ""
        if self.health_data['score'] >= 75:
            summary = "Your financial health is strong, indicating excellent money management."
        elif self.health_data['score'] >= 60:
            summary = "Your financial health is fair, with opportunities to improve spending control."
        else:
            summary = "Your financial health needs attention. Focus on budget adherence and savings."

        return {
            "insights": insights[:10], # Return up to 10 insights since we have more now
            "strengths": strengths[:4],
            "weaknesses": weaknesses[:4],
            "improvement_opportunities": improvements[:4],
            "summary": summary
        }
