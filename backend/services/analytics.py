import pandas as pd
from typing import Dict, Any

class AnalyticsEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def get_summary(self) -> Dict[str, Any]:
        """Returns total income, expenses, savings, and savings rate."""
        if self.df.empty:
            return {
                "total_income": 0,
                "total_expenses": 0,
                "net_savings": 0,
                "savings_rate": 0,
                "transaction_count": 0
            }
            
        income_df = self.df[self.df['type'] == 'income']
        expense_df = self.df[self.df['type'] == 'expense']
        
        total_income = float(income_df['amount'].sum())
        total_expenses = float(expense_df['amount'].sum())
        net_savings = total_income - total_expenses
        
        savings_rate = 0
        if total_income > 0:
            savings_rate = round((net_savings / total_income) * 100, 2)
            
        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate": savings_rate,
            "transaction_count": len(self.df)
        }
        
    def get_category_breakdown(self, type_filter: str = 'expense', days: int = 30) -> Dict[str, float]:
        """Returns spending or income by category over the last N days."""
        if self.df.empty:
            return {}
            
        filtered_df = self.df[self.df['type'] == type_filter].copy()
        
        if days:
            max_date = filtered_df['timestamp'].max()
            if pd.notna(max_date):
                cutoff = max_date - pd.Timedelta(days=days)
                filtered_df = filtered_df[filtered_df['timestamp'] >= cutoff]
                
        if filtered_df.empty:
            return {}
            
        breakdown = filtered_df.groupby('category')['amount'].sum().to_dict()
        # sort by amount descending
        breakdown = {k: round(v, 2) for k, v in sorted(breakdown.items(), key=lambda item: item[1], reverse=True)}
        
        return breakdown
        
    def get_monthly_trend(self) -> list:
        """Returns monthly aggregated income and expenses."""
        if self.df.empty:
            return []
            
        df = self.df.copy()
        df['month'] = df['timestamp'].dt.to_period('M').astype(str)
        
        monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
        
        if 'income' not in monthly.columns:
            monthly['income'] = 0
        if 'expense' not in monthly.columns:
            monthly['expense'] = 0
            
        result = []
        for _, row in monthly.iterrows():
            result.append({
                "month": row['month'],
                "income": round(row['income'], 2),
                "expense": round(row['expense'], 2)
            })
            
        return result

    def get_period_totals(self, days: int = 30, offset_days: int = 0) -> Dict[str, float]:
        """Returns total income and expenses for a specific period window."""
        if self.df.empty:
            return {"income": 0.0, "expense": 0.0}
            
        max_date = self.df['timestamp'].max()
        if pd.isna(max_date):
            return {"income": 0.0, "expense": 0.0}
            
        end_date = max_date - pd.Timedelta(days=offset_days)
        start_date = end_date - pd.Timedelta(days=days)
        
        mask = (self.df['timestamp'] >= start_date) & (self.df['timestamp'] <= end_date)
        period_df = self.df[mask]
        
        income = float(period_df[period_df['type'] == 'income']['amount'].sum())
        expense = float(period_df[period_df['type'] == 'expense']['amount'].sum())
        
        return {
            "income": round(income, 2),
            "expense": round(expense, 2)
        }
