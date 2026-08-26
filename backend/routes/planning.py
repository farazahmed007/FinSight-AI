from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from typing import Dict, Any

from middleware.auth import require_auth
from database import get_db_connection
from schemas.planning_schemas import (
    PlanningScenarioRequest, PlanningScenarioResponse,
    AffordabilityRequest, AffordabilityResponse,
    GoalPlanningRequest, GoalPlanningResponse
)
from services.planning_engine import PlanningEngine

planning_bp = APIRouter()

def get_transactions_df(user_id: str) -> pd.DataFrame:
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df

@planning_bp.post("/simulate", response_model=PlanningScenarioResponse)
async def simulate_scenario(request: PlanningScenarioRequest, user_id: str = Depends(require_auth)):
    df = get_transactions_df(user_id)
    
    engine = PlanningEngine(user_id, df)
    result = engine.calculate_scenario(request)
    return result

@planning_bp.post("/affordability", response_model=AffordabilityResponse)
async def check_affordability(request: AffordabilityRequest, user_id: str = Depends(require_auth)):
    df = get_transactions_df(user_id)
    
    engine = PlanningEngine(user_id, df)
    result = engine.calculate_affordability(request)
    return result

@planning_bp.post("/goal-calculator", response_model=GoalPlanningResponse)
async def calculate_goal_plan(request: GoalPlanningRequest, user_id: str = Depends(require_auth)):
    df = get_transactions_df(user_id)
    
    engine = PlanningEngine(user_id, df)
    try:
        result = engine.calculate_goal_plan(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
