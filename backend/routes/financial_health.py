from fastapi import APIRouter, Depends
from middleware.auth import require_auth
from schemas.api_schemas import FinancialHealthScore, FinancialHealthSnapshot
from database import get_all_transactions
from services.financial_health_engine import FinancialHealthEngine
from services.financial_insights_engine import FinancialInsightsEngine
from typing import List

financial_health_bp = APIRouter()

def get_df(user_id):
    return get_all_transactions(user_id)

@financial_health_bp.get('/', response_model=FinancialHealthScore, tags=["Financial Health"])
def get_financial_health(user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    
    # Initialize Engine
    health_engine = FinancialHealthEngine(user_id, df)
    health_data = health_engine.calculate_overall_health()
    
    insights_engine = FinancialInsightsEngine(user_id, df, health_data)
    insights_data = insights_engine.generate_insights()
    
    return {
        "score": health_data["score"],
        "status": health_data["status"],
        "breakdown": health_data["breakdown"],
        "summary": insights_data["summary"],
        "insights": insights_data["insights"],
        "strengths": insights_data["strengths"],
        "weaknesses": insights_data["weaknesses"],
        "improvement_opportunities": insights_data["improvement_opportunities"]
    }

@financial_health_bp.get('/history', response_model=List[FinancialHealthSnapshot], tags=["Financial Health"])
def get_financial_health_history(user_id: str = Depends(require_auth)):
    df = get_df(user_id)
    health_engine = FinancialHealthEngine(user_id, df)
    history = health_engine.get_history()
    return history
