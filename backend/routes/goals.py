from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from middleware.auth import require_auth, AuthException
from schemas.api_schemas import GoalCreate, GoalUpdate, GoalResponse, GoalSummary
from services.goals_engine import GoalsEngine
from database import get_all_transactions

goals_bp = APIRouter()

def get_engine(user_id: str) -> GoalsEngine:
    df = get_all_transactions(user_id)
    return GoalsEngine(user_id, df)

@goals_bp.get("/summary", response_model=GoalSummary, tags=["Goals"])
def get_goal_summary(user_id: str = Depends(require_auth)):
    engine = get_engine(user_id)
    return engine.get_summary()

@goals_bp.get("", response_model=List[GoalResponse], tags=["Goals"])
def get_all_goals(user_id: str = Depends(require_auth)):
    engine = get_engine(user_id)
    return engine.get_all_goals()

@goals_bp.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED, tags=["Goals"])
def create_goal(goal: GoalCreate, user_id: str = Depends(require_auth)):
    engine = get_engine(user_id)
    new_goal = engine.create_goal(goal.model_dump(exclude_unset=True))
    if not new_goal:
        raise HTTPException(status_code=400, detail="Could not create goal")
    return new_goal

@goals_bp.get("/{goal_id}", response_model=GoalResponse, tags=["Goals"])
def get_goal(goal_id: int, user_id: str = Depends(require_auth)):
    engine = get_engine(user_id)
    goal = engine.get_goal(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@goals_bp.put("/{goal_id}", response_model=GoalResponse, tags=["Goals"])
def update_goal(goal_id: int, goal: GoalUpdate, user_id: str = Depends(require_auth)):
    engine = get_engine(user_id)
    
    # Check if goal exists
    existing = engine.get_goal(goal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    updated = engine.update_goal(goal_id, goal.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update goal")
    return updated

@goals_bp.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Goals"])
def delete_goal(goal_id: int, user_id: str = Depends(require_auth)):
    engine = get_engine(user_id)
    
    # Check if goal exists
    existing = engine.get_goal(goal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    engine.delete_goal(goal_id)
    return None
