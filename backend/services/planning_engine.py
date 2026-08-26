import pandas as pd
from datetime import datetime
import math
from typing import List, Dict

from schemas.planning_schemas import (
    PlanningScenarioRequest, PlanningScenarioResponse,
    PlanningMetrics, ScenarioImpactSummary,
    CategoryDifference, GoalProjection, BudgetImpact,
    AffordabilityRequest, AffordabilityResponse,
    GoalPlanningRequest, GoalPlanningResponse
)
from services.analytics import AnalyticsEngine
from services.budget_engine import BudgetEngine
from services.goals_engine import GoalsEngine
from services.financial_health_engine import FinancialHealthEngine

class PlanningEngine:
    def __init__(self, user_id: str, transactions_df: pd.DataFrame):
        self.user_id = user_id
        self.transactions_df = transactions_df.copy()
        
    def calculate_scenario(self, request: PlanningScenarioRequest) -> PlanningScenarioResponse:
        analytics = AnalyticsEngine(self.transactions_df)
        totals = analytics.get_period_totals(days=30, offset_days=0)
        
        current_health_engine = FinancialHealthEngine(self.user_id, self.transactions_df)
        current_health = current_health_engine.calculate_overall_health()
        
        baseline_metrics = PlanningMetrics(
            monthly_income=totals['income'],
            monthly_expenses=totals['expense'],
            monthly_savings=totals['income'] - totals['expense'],
            savings_rate=(totals['income'] - totals['expense']) / totals['income'] * 100 if totals['income'] > 0 else 0,
            financial_health_score=current_health['score']
        )
        
        scenario_df = self.transactions_df.copy()
        if scenario_df.empty:
            now = pd.Timestamp.now()
        else:
            now = scenario_df['timestamp'].max()
            if pd.isna(now):
                now = pd.Timestamp.now()
                
        scenario_records = []
        
        if request.monthly_income_change != 0:
            scenario_records.append({
                'transaction_id': 'scen_inc_1',
                'user_id': self.user_id,
                'timestamp': now,
                'amount': request.monthly_income_change,
                'category': 'salary',
                'merchant': 'Scenario Adjustment',
                'type': 'income'
            })
            
        if request.monthly_expense_change != 0:
            scenario_records.append({
                'transaction_id': 'scen_exp_1',
                'user_id': self.user_id,
                'timestamp': now,
                'amount': request.monthly_expense_change,
                'category': 'uncategorized',
                'merchant': 'Scenario Adjustment',
                'type': 'expense'
            })
            
        category_impacts = []
        category_breakdown = analytics.get_category_breakdown(type_filter='expense', days=30)
        
        for cat, change in request.category_changes.items():
            scenario_records.append({
                'transaction_id': f'scen_cat_{cat}',
                'user_id': self.user_id,
                'timestamp': now,
                'amount': change,
                'category': cat,
                'merchant': 'Scenario Adjustment',
                'type': 'expense'
            })
            current_spend = category_breakdown.get(cat, 0.0)
            scen_spend = max(0, current_spend + change)
            reduction = current_spend - scen_spend
            pct = (reduction / current_spend * 100) if current_spend > 0 else 0
            category_impacts.append(CategoryDifference(
                category=cat,
                current_spending=current_spend,
                scenario_spending=scen_spend,
                reduction=reduction,
                percentage_change=pct
            ))
            
        if scenario_records:
            scenario_df = pd.concat([scenario_df, pd.DataFrame(scenario_records)], ignore_index=True)
            
        scen_analytics = AnalyticsEngine(scenario_df)
        scen_totals = scen_analytics.get_period_totals(days=30, offset_days=0)
        
        scen_income = max(0.0, float(scen_totals['income']))
        scen_expense = max(0.0, float(scen_totals['expense']))
        
        scenario_savings = scen_income - scen_expense + request.additional_monthly_savings
        
        scen_health_engine = FinancialHealthEngine(self.user_id, scenario_df)
        scen_health_engine._save_snapshot = lambda overall, breakdown: None
        scen_health = scen_health_engine.calculate_overall_health()
        
        scenario_metrics = PlanningMetrics(
            monthly_income=scen_income,
            monthly_expenses=scen_expense,
            monthly_savings=scenario_savings,
            savings_rate=(scenario_savings / scen_income * 100) if scen_income > 0 else 0,
            financial_health_score=scen_health['score']
        )
        
        impact = ScenarioImpactSummary(
            monthly_savings_change=scenario_metrics.monthly_savings - baseline_metrics.monthly_savings,
            savings_rate_change=scenario_metrics.savings_rate - baseline_metrics.savings_rate,
            health_score_change=scenario_metrics.financial_health_score - baseline_metrics.financial_health_score
        )
        
        goal_impacts = self._calculate_goals_impact(baseline_metrics.monthly_savings, scenario_metrics.monthly_savings)
        budget_impacts = self._calculate_budget_impacts(scenario_df, request.category_changes)
        smart_insights = self._generate_smart_insights(baseline_metrics, scenario_metrics, goal_impacts, budget_impacts)
        future_projection = self._calculate_future_projections(baseline_metrics.monthly_savings, scenario_metrics.monthly_savings, request.duration_months)
        
        return PlanningScenarioResponse(
            baseline=baseline_metrics,
            scenario=scenario_metrics,
            impact=impact,
            category_impacts=category_impacts,
            goal_impacts=goal_impacts,
            budget_impacts=budget_impacts,
            smart_insights=smart_insights,
            future_projection=future_projection
        )

    def _calculate_goals_impact(self, current_monthly_savings: float, scenario_monthly_savings: float) -> List[GoalProjection]:
        goals_engine = GoalsEngine(self.user_id, self.transactions_df)
        goals = [g for g in goals_engine.get_all_goals() if g['status'] != 'COMPLETED']
        
        projections = []
        for g in goals:
            target = g['target_amount']
            current = g['current_amount']
            remaining = target - current
            
            curr_months = math.ceil(remaining / current_monthly_savings) if current_monthly_savings > 0 else None
            scen_months = math.ceil(remaining / scenario_monthly_savings) if scenario_monthly_savings > 0 else None
                
            improvement = None
            if curr_months is not None and scen_months is not None:
                improvement = curr_months - scen_months
                
            projections.append(GoalProjection(
                goal_id=g['id'],
                name=g['name'],
                target_amount=target,
                current_amount=current,
                remaining_amount=remaining,
                current_required_monthly=g['required_monthly_savings'],
                scenario_required_monthly=max(0, g['required_monthly_savings'] - (scenario_monthly_savings - current_monthly_savings)),
                current_projected_months=curr_months,
                scenario_projected_months=scen_months,
                months_improvement=improvement
            ))
        return projections

    def _calculate_budget_impacts(self, scenario_df: pd.DataFrame, category_changes: dict) -> List[BudgetImpact]:
        if not category_changes:
            return []
            
        current_month = datetime.now().strftime('%Y-%m')
        
        budget_engine = BudgetEngine(self.user_id, self.transactions_df)
        current_summary = budget_engine.get_summary(current_month)
        
        scen_budget_engine = BudgetEngine(self.user_id, scenario_df)
        scen_summary = scen_budget_engine.get_summary(current_month)
        
        impacts = []
        for curr_cat in current_summary['categories']:
            cat_name = curr_cat['category']
            if cat_name in category_changes:
                scen_cat = next((c for c in scen_summary['categories'] if c['category'] == cat_name), None)
                if scen_cat:
                    impacts.append(BudgetImpact(
                        category=cat_name,
                        budget_amount=curr_cat['budget'],
                        current_spent=curr_cat['spent'],
                        current_usage_percentage=curr_cat['usage_percentage'],
                        current_status=curr_cat['status'],
                        scenario_spent=scen_cat['spent'],
                        scenario_usage_percentage=scen_cat['usage_percentage'],
                        scenario_status=scen_cat['status']
                    ))
        return impacts

    def _generate_smart_insights(self, baseline: PlanningMetrics, scenario: PlanningMetrics, goal_impacts: List[GoalProjection], budget_impacts: List[BudgetImpact]) -> List[dict]:
        insights = []
        
        if scenario.savings_rate > baseline.savings_rate:
            insights.append({
                "type": "savings_improvement",
                "message": f"This scenario could increase your savings rate from {baseline.savings_rate:.1f}% to {scenario.savings_rate:.1f}%."
            })
            
        for g in goal_impacts:
            if g.months_improvement and g.months_improvement > 0:
                insights.append({
                    "type": "goal_acceleration",
                    "message": f"You could reach your '{g.name}' goal approximately {g.months_improvement} months earlier."
                })
                
        for b in budget_impacts:
            if b.current_status == 'OVER_BUDGET' and b.scenario_status != 'OVER_BUDGET':
                insights.append({
                    "type": "budget_recovery",
                    "message": f"Reducing {b.category} spending would bring you back under budget."
                })
                
        return insights

    def _calculate_future_projections(self, baseline_savings: float, scenario_savings: float, duration_months: int) -> List[dict]:
        projections = []
        base_accum = 0.0
        scen_accum = 0.0
        
        for i in range(1, duration_months + 1):
            base_accum += max(0, baseline_savings)
            scen_accum += max(0, scenario_savings)
            projections.append({
                "month": f"Month {i}",
                "baseline_savings": base_accum,
                "scenario_savings": scen_accum
            })
            
        return projections

    def calculate_affordability(self, request: AffordabilityRequest) -> AffordabilityResponse:
        analytics = AnalyticsEngine(self.transactions_df)
        totals = analytics.get_period_totals(days=30, offset_days=0)
        current_savings = totals['income'] - totals['expense']
        
        req_monthly = request.purchase_amount / request.months
        shortfall = req_monthly - current_savings
        
        if shortfall <= 0:
            status = "AFFORDABLE"
        elif shortfall < (totals['income'] * 0.1):
            status = "TIGHT"
        else:
            status = "NOT_AFFORDABLE"
            
        return AffordabilityResponse(
            purchase_amount=request.purchase_amount,
            months=request.months,
            current_projected_capacity=current_savings,
            required_monthly_savings=req_monthly,
            status=status,
            shortfall=max(0, shortfall)
        )

    def calculate_goal_plan(self, request: GoalPlanningRequest) -> GoalPlanningResponse:
        goals_engine = GoalsEngine(self.user_id, self.transactions_df)
        goals = goals_engine.get_all_goals()
        target_goal = next((g for g in goals if g['id'] == request.goal_id), None)
        
        if not target_goal:
            raise ValueError(f"Goal {request.goal_id} not found")
            
        remaining = target_goal['target_amount'] - target_goal['current_amount']
        
        target_dt = datetime.strptime(request.target_date, '%Y-%m-%d')
        now = datetime.now()
        months = (target_dt.year - now.year) * 12 + target_dt.month - now.month
        months = max(1, months)
        
        req_monthly = remaining / months
        
        analytics = AnalyticsEngine(self.transactions_df)
        totals = analytics.get_period_totals(days=30, offset_days=0)
        current_savings = totals['income'] - totals['expense']
        
        additional = req_monthly - current_savings
        feasible = additional <= 0 or (additional < totals['income'] * 0.2)
        
        return GoalPlanningResponse(
            goal_id=request.goal_id,
            remaining_amount=remaining,
            months_remaining=months,
            required_monthly_saving=req_monthly,
            current_monthly_saving=current_savings,
            additional_required=max(0, additional),
            feasible=feasible
        )
