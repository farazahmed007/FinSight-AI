from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PlanningScenarioRequest(BaseModel):
    monthly_income_change: float = 0.0
    monthly_expense_change: float = 0.0
    category_changes: Dict[str, float] = Field(default_factory=dict)
    additional_monthly_savings: float = 0.0
    duration_months: int = Field(default=6, gt=0, le=120)

class GoalProjection(BaseModel):
    goal_id: int
    name: str
    target_amount: float
    current_amount: float
    remaining_amount: float
    current_required_monthly: float
    scenario_required_monthly: float
    current_projected_months: Optional[int]
    scenario_projected_months: Optional[int]
    months_improvement: Optional[int]

class BudgetImpact(BaseModel):
    category: str
    budget_amount: float
    current_spent: float
    current_usage_percentage: float
    current_status: str
    scenario_spent: float
    scenario_usage_percentage: float
    scenario_status: str

class FinancialHealthImpact(BaseModel):
    current_score: int
    scenario_score: int
    score_change: int
    current_breakdown: dict
    scenario_breakdown: dict

class CategoryDifference(BaseModel):
    category: str
    current_spending: float
    scenario_spending: float
    reduction: float
    percentage_change: float

class PlanningMetrics(BaseModel):
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    savings_rate: float
    financial_health_score: int

class ScenarioImpactSummary(BaseModel):
    monthly_savings_change: float
    savings_rate_change: float
    health_score_change: int

class PlanningScenarioResponse(BaseModel):
    baseline: PlanningMetrics
    scenario: PlanningMetrics
    impact: ScenarioImpactSummary
    category_impacts: List[CategoryDifference]
    goal_impacts: List[GoalProjection]
    budget_impacts: List[BudgetImpact]
    smart_insights: List[dict]
    future_projection: List[dict] # {month: "Month 1", baseline_savings: X, scenario_savings: Y}

class AffordabilityRequest(BaseModel):
    purchase_amount: float = Field(..., gt=0)
    months: int = Field(..., gt=0, le=120)

class AffordabilityResponse(BaseModel):
    purchase_amount: float
    months: int
    current_projected_capacity: float
    required_monthly_savings: float
    status: str # AFFORDABLE, TIGHT, NOT_AFFORDABLE
    shortfall: float

class GoalPlanningRequest(BaseModel):
    goal_id: int
    target_date: str

class GoalPlanningResponse(BaseModel):
    goal_id: int
    remaining_amount: float
    months_remaining: int
    required_monthly_saving: float
    current_monthly_saving: float
    additional_required: float
    feasible: bool
