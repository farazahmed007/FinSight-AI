export interface Budget {
    id: number;
    category: string;
    amount: number;
    month: string;
    created_at: string;
    updated_at: string;
}

export interface BudgetAlert {
    type: string;
    message: string;
}

export interface BudgetCategorySummary {
    category: string;
    budget: number;
    spent: number;
    remaining: number;
    usage_percentage: number;
    status: 'ON_TRACK' | 'WATCH' | 'NEAR_LIMIT' | 'OVER_BUDGET';
    variance: number;
}

export interface BudgetSummary {
    month: string;
    total_budget: number;
    total_spent: number;
    remaining_budget: number;
    usage_percentage: number;
    categories: BudgetCategorySummary[];
    alerts: BudgetAlert[];
}

export interface BudgetCreate {
    category: string;
    amount: number;
    month: string;
}

export interface BudgetUpdate {
    amount: number;
}
