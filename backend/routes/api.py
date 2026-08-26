from fastapi import APIRouter, Depends, Request
from middleware.auth import require_auth, AuthException
from schemas.api_schemas import (
    QueryRequest, QueryResponse, Transaction, ForecastResponse, 
    AnalyticsSummary, Recommendation
)
from database import get_all_transactions
from services.preprocessing import aggregate_daily_transactions
from services.forecasting import ForecastingEngine
from services.nlp_engine import NLPEngine
from services.recommendation_engine import RecommendationEngine
from services.analytics import AnalyticsEngine
from typing import List

api_bp = APIRouter()
nlp_engine = NLPEngine()

def get_df(user_id):
    return get_all_transactions(user_id)

@api_bp.get('/health', tags=["Health"])
def health_check():
    return {"status": "healthy"}

@api_bp.post('/query', response_model=QueryResponse, tags=["AI Assistant"])
def handle_query(data: dict, user_id: str = Depends(require_auth)):
    if not data or 'query' not in data or not str(data['query']).strip():
        raise AuthException(status_code=400, message="Query text is required")
        
    query_text = data['query']
    parsed = nlp_engine.process_query(query_text)
    
    intent = parsed['intent']
    category = parsed['category']
    time_range = parsed['time_range_days']
    
    df = get_df(user_id)
    
    if intent == 'FORECAST_REQUEST':
        if not category:
            return {
                "intent": intent,
                "error": True,
                "message": "I couldn't identify a specific category to forecast. Please specify one (e.g., food, transport)."
            }
            
        daily_df = aggregate_daily_transactions(df, category=category)
        engine = ForecastingEngine(daily_df)
        forecast = engine.forecast_category(category, horizon_days=time_range)
        
        amount = sum(forecast['forecast_values'])
        return {
            "intent": intent,
            "category": category,
            "horizon_days": time_range,
            "forecast_amount": round(amount, 2),
            "trend": forecast['trend'],
            "message": f"You are projected to spend approximately ₹{round(amount):,} on {category} over the next {time_range} days."
        }
        
    elif intent == 'SPENDING_SUMMARY':
        if not category:
            # Overall summary
            analytics = AnalyticsEngine(df)
            breakdown = analytics.get_category_breakdown(days=time_range)
            total = sum(breakdown.values())
            return {
                "intent": intent,
                "period_days": time_range,
                "total_spent": round(total, 2),
                "message": f"You spent approximately ₹{round(total):,} in total over the last {time_range} days."
            }
        else:
            analytics = AnalyticsEngine(df)
            breakdown = analytics.get_category_breakdown(days=time_range)
            total = breakdown.get(category, 0)
            return {
                "intent": intent,
                "category": category,
                "period_days": time_range,
                "total_spent": round(total, 2),
                "message": f"You spent approximately ₹{round(total):,} on {category} over the last {time_range} days."
            }
            
    elif intent in ['BUDGET_SUMMARY', 'BUDGET_STATUS', 'BUDGET_REMAINING']:
        from services.budget_engine import BudgetEngine
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        
        budget_engine = BudgetEngine(user_id, df)
        budget_summary = budget_engine.get_summary(current_month)
        
        if not category:
            return {
                "intent": intent,
                "budget": budget_summary['total_budget'],
                "spent": budget_summary['total_spent'],
                "remaining": budget_summary['remaining_budget'],
                "usage_percentage": budget_summary['usage_percentage'],
                "status": budget_engine._get_status(budget_summary['usage_percentage']),
                "message": f"Your total budget for this month is ₹{budget_summary['total_budget']:,.2f}. You have spent ₹{budget_summary['total_spent']:,.2f}, leaving ₹{budget_summary['remaining_budget']:,.2f}."
            }
        else:
            cat_summary = next((c for c in budget_summary['categories'] if c['category'] == category), None)
            if not cat_summary:
                return {
                    "intent": intent,
                    "category": category,
                    "error": True,
                    "message": f"You haven't set up a budget for {category} this month."
                }
                
            return {
                "intent": intent,
                "category": category,
                "budget": cat_summary['budget'],
                "spent": cat_summary['spent'],
                "remaining": cat_summary['remaining'],
                "usage_percentage": cat_summary['usage_percentage'],
                "status": cat_summary['status'],
                "message": f"For {category}, you have spent ₹{cat_summary['spent']:,.2f} out of your ₹{cat_summary['budget']:,.2f} budget."
            }
            
    elif intent == 'RECOMMENDATION':
        recommender = RecommendationEngine(df, user_id=user_id)
        recs = recommender.generate_recommendations()
        if category:
            recs = [r for r in recs if r.get('category') == category]
            
        return {
            "intent": intent,
            "category": category,
            "recommendations": recs,
            "message": f"Here are your recommendations{' for ' + category if category else ''}."
        }
        
    elif intent in ['GOAL_SUMMARY', 'GOAL_PROGRESS', 'GOAL_REMAINING', 'GOAL_SAVINGS_REQUIRED', 'GOAL_STATUS', 'GOAL_COMPLETION', 'GOAL_RECOMMENDATION']:
        from services.goals_engine import GoalsEngine
        goals_engine = GoalsEngine(user_id, df)
        
        if intent == 'GOAL_SUMMARY':
            summary = goals_engine.get_summary()
            return {
                "intent": intent,
                "message": f"You have {summary['active_goals']} active goals out of {summary['total_goals']} total goals. You've saved ₹{summary['total_saved']:,.2f} against a target of ₹{summary['total_target']:,.2f}."
            }
            
        elif intent == 'GOAL_SAVINGS_REQUIRED':
            summary = goals_engine.get_summary()
            if summary['active_goals'] == 0:
                return {
                    "intent": intent,
                    "message": "You don't have any active goals right now."
                }
            return {
                "intent": intent,
                "message": f"To stay on track for all your active goals, you need to save a total of ₹{summary['total_required_monthly_savings']:,.2f} per month."
            }
            
        else:
            return {
                "intent": intent,
                "message": "I found your goals! Check the Goals dashboard for detailed progress and status."
            }
            
    elif intent in ['FINANCIAL_HEALTH_SCORE', 'FINANCIAL_HEALTH_STATUS', 'FINANCIAL_HEALTH_BREAKDOWN', 'FINANCIAL_HEALTH_INSIGHTS', 'FINANCIAL_HEALTH_IMPROVEMENT', 'FINANCIAL_HEALTH_HISTORY']:
        from services.financial_health_engine import FinancialHealthEngine
        from services.financial_insights_engine import FinancialInsightsEngine
        
        health_engine = FinancialHealthEngine(user_id, df)
        health_data = health_engine.calculate_overall_health()
        
        insights_engine = FinancialInsightsEngine(user_id, df, health_data)
        insights_data = insights_engine.generate_insights()
        
        return {
            "intent": intent,
            "score": health_data["score"],
            "status": health_data["status"],
            "breakdown": health_data["breakdown"],
            "summary": insights_data["summary"],
            "insights": insights_data["insights"],
            "strengths": insights_data["strengths"],
            "weaknesses": insights_data["weaknesses"],
            "improvement_opportunities": insights_data["improvement_opportunities"],
            "message": "Here is your latest financial health breakdown."
        }
            
    raise AuthException(status_code=400, message="Unknown intent")

@api_bp.get('/forecast/{category}', response_model=ForecastResponse, tags=["Forecasting"])
def get_forecast(category: str, horizon: int = 30, user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    daily_df = aggregate_daily_transactions(df, category=category)
    
    engine = ForecastingEngine(daily_df)
    forecast = engine.forecast_category(category, horizon_days=horizon)
    return forecast

@api_bp.get('/recommendations', response_model=List[Recommendation], tags=["Recommendations"])
def get_recommendations(user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    recommender = RecommendationEngine(df, user_id=user_id)
    recs = recommender.generate_recommendations()
    return recs

@api_bp.get('/transactions', response_model=List[Transaction], tags=["Transactions"])
def get_transactions(user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    # limit for prototype
    df = df.sort_values('timestamp', ascending=False).head(100)
    # format timestamp as string
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.to_dict(orient='records')

@api_bp.get('/analytics/summary', response_model=AnalyticsSummary, tags=["Analytics"])
def get_analytics_summary(user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    analytics = AnalyticsEngine(df)
    return analytics.get_summary()

@api_bp.get('/analytics/categories', response_model=dict, tags=["Analytics"])
def get_analytics_categories(days: int = 30, user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    analytics = AnalyticsEngine(df)
    return analytics.get_category_breakdown(days=days)

@api_bp.get('/analytics/monthly', response_model=List[dict], tags=["Analytics"])
def get_analytics_monthly(user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    analytics = AnalyticsEngine(df)
    return analytics.get_monthly_trend()
