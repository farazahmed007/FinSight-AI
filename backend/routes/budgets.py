from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from middleware.auth import require_auth
from schemas.api_schemas import (
    BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummary
)
from database import get_all_transactions
from services.budget_engine import BudgetEngine
import pandas as pd

budgets_bp = APIRouter()

def get_budget_engine(user_id: str):
    df = get_all_transactions(user_id)
    return BudgetEngine(user_id, df)

@budgets_bp.get('', response_model=List[BudgetResponse], tags=["Budgets"])
def get_budgets(month: Optional[str] = None, user_id: str = Depends(require_auth)):
    if not month:
        month = datetime.now().strftime('%Y-%m')
    
    engine = get_budget_engine(user_id)
    return engine.get_budgets_for_month(month)

@budgets_bp.get('/summary', response_model=BudgetSummary, tags=["Budgets"])
def get_budget_summary(month: Optional[str] = None, user_id: str = Depends(require_auth)):
    if not month:
        month = datetime.now().strftime('%Y-%m')
        
    engine = get_budget_engine(user_id)
    return engine.get_summary(month)

@budgets_bp.get('/{budget_id}', response_model=BudgetResponse, tags=["Budgets"])
def get_budget(budget_id: int, user_id: str = Depends(require_auth)):
    engine = get_budget_engine(user_id)
    budget = engine.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@budgets_bp.post('', response_model=BudgetResponse, tags=["Budgets"])
def create_budget(budget_data: BudgetCreate, user_id: str = Depends(require_auth)):
    engine = get_budget_engine(user_id)
    # Check if budget already exists for this category and month
    existing_budgets = engine.get_budgets_for_month(budget_data.month)
    if any(b['category'] == budget_data.category for b in existing_budgets):
        raise HTTPException(status_code=400, detail=f"Budget for {budget_data.category} already exists in {budget_data.month}")
        
    try:
        new_budget = engine.create_budget(budget_data.category, budget_data.amount, budget_data.month)
        return new_budget
    except Exception as e:
        # Most likely unique constraint failure
        raise HTTPException(status_code=400, detail="Failed to create budget. It may already exist.")

@budgets_bp.put('/{budget_id}', response_model=BudgetResponse, tags=["Budgets"])
def update_budget(budget_id: int, budget_data: BudgetUpdate, user_id: str = Depends(require_auth)):
    engine = get_budget_engine(user_id)
    budget = engine.update_budget(budget_id, budget_data.amount)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@budgets_bp.delete('/{budget_id}', tags=["Budgets"])
def delete_budget(budget_id: int, user_id: str = Depends(require_auth)):
    engine = get_budget_engine(user_id)
    budget = engine.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
        
    engine.delete_budget(budget_id)
    return {"success": True, "message": "Budget deleted successfully"}
