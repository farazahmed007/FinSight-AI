from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    intent: str
    error: Optional[bool] = None
    message: str
    category: Optional[str] = None
    horizon_days: Optional[int] = None
    forecast_amount: Optional[float] = None
    trend: Optional[str] = None
    period_days: Optional[int] = None
    total_spent: Optional[float] = None
    recommendations: Optional[List[dict]] = None
    goal: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    remaining_amount: Optional[float] = None
    required_monthly_savings: Optional[float] = None
    target_date: Optional[str] = None
    
    # Financial Health specific
    score: Optional[int] = None
    status: Optional[str] = None
    breakdown: Optional[dict] = None
    summary: Optional[str] = None
    insights: Optional[List[dict]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    improvement_opportunities: Optional[List[dict]] = None

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    timestamp: str
    amount: float
    category: str
    merchant: str
    type: str

class ForecastResponse(BaseModel):
    forecast_values: List[float]
    forecast_dates: List[str]
    category: str
    horizon_days: int
    trend: str
    confidence_intervals: Optional[List[dict]] = None

class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    transaction_count: int

class Recommendation(BaseModel):
    category: Optional[str] = None
    type: str
    severity: str
    message: str
    reason: str
    suggested_action: str

class BudgetCreate(BaseModel):
    category: str
    amount: float = Field(..., gt=0, description="Budget amount must be greater than zero")
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Month must be in YYYY-MM format")

class BudgetUpdate(BaseModel):
    amount: float = Field(..., gt=0, description="Budget amount must be greater than zero")

class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: float
    month: str
    created_at: str
    updated_at: str

class BudgetAlert(BaseModel):
    type: str
    message: str

class BudgetCategorySummary(BaseModel):
    category: str
    budget: float
    spent: float
    remaining: float
    usage_percentage: float
    status: str
    variance: float

class BudgetSummary(BaseModel):
    month: str
    total_budget: float
    total_spent: float
    remaining_budget: float
    usage_percentage: float
    categories: List[BudgetCategorySummary]
    alerts: List[BudgetAlert]

class GoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(0.0, ge=0)
    target_date: str
    category: Optional[str] = None

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    target_date: Optional[str] = None
    category: Optional[str] = None

class GoalResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float
    target_date: str
    category: Optional[str] = None
    created_at: str
    updated_at: str
    # Computed properties
    progress_percentage: float
    remaining_amount: float
    status: str
    required_monthly_savings: float
    projected_completion_date: Optional[str] = None

class GoalSummary(BaseModel):
    total_goals: int
    active_goals: int
    completed_goals: int
    total_target: float
    total_saved: float
    total_remaining: float
    overall_progress: float
    total_required_monthly_savings: float

class GoalRecommendation(BaseModel):
    type: str
    severity: str
    message: str
    reason: str
    suggested_action: str

# Financial Health Schemas
class FinancialHealthBreakdown(BaseModel):
    savings: int
    budget_discipline: int
    goal_progress: int
    spending_control: int
    financial_stability: int

class FinancialHealthInsight(BaseModel):
    type: str
    severity: str
    title: str
    message: str
    reason: str
    category: Optional[str] = None
    suggested_action: str

class FinancialHealthImprovement(BaseModel):
    action: str
    estimated_points: int

class FinancialHealthScore(BaseModel):
    score: int
    status: str
    breakdown: FinancialHealthBreakdown
    summary: str
    insights: List[FinancialHealthInsight]
    strengths: List[str]
    weaknesses: List[str]
    improvement_opportunities: List[FinancialHealthImprovement]

class FinancialHealthSnapshot(BaseModel):
    id: int
    user_id: str
    score: int
    savings_score: int
    budget_score: int
    goal_score: int
    spending_score: int
    stability_score: int
    created_at: str
