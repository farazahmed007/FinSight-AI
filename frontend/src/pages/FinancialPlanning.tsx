import React, { useState, useEffect } from 'react';
import { 
  Calculator, TrendingUp, Target, Activity, DollarSign, CheckCircle2, ChevronRight
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { simulateScenario } from '../services/api';

interface ScenarioResponse {
  baseline: {
    monthly_income: number;
    monthly_expenses: number;
    monthly_savings: number;
    savings_rate: number;
    financial_health_score: number;
  };
  scenario: {
    monthly_income: number;
    monthly_expenses: number;
    monthly_savings: number;
    savings_rate: number;
    financial_health_score: number;
  };
  impact: {
    monthly_savings_change: number;
    savings_rate_change: number;
    health_score_change: number;
  };
  smart_insights: Array<{
    type: string;
    message: string;
  }>;
  goal_impacts: Array<{
    name: string;
    target_amount: number;
    remaining_amount: number;
    months_improvement: number | null;
    scenario_projected_months: number | null;
  }>;
  budget_impacts: Array<{
    category: string;
    current_status: string;
    scenario_status: string;
  }>;
  future_projection: Array<{
    month: string;
    baseline_savings: number;
    scenario_savings: number;
  }>;
}

const FinancialPlanning: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScenarioResponse | null>(null);
  
  const [incomeChange, setIncomeChange] = useState(0);
  const [expenseChange, setExpenseChange] = useState(0);
  const [duration, setDuration] = useState(12);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await simulateScenario({
        monthly_income_change: incomeChange,
        monthly_expense_change: expenseChange,
        category_changes: {},
        additional_monthly_savings: 0,
        duration_months: duration
      });
      setResult(res);
    } catch (error) {
      console.error("Failed to run scenario", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSimulate();
  }, []);

  const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <Calculator className="w-6 h-6 mr-2 text-indigo-500" />
            What-If Simulator
          </h1>
          <p className="text-gray-500 dark:text-gray-400">Model how financial changes impact your future.</p>
        </div>
        <button 
          onClick={handleSimulate}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Builder Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Scenario Builder</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Monthly Income Change
              </label>
              <div className="flex items-center space-x-4">
                <input 
                  type="range" 
                  min="-5000" 
                  max="5000" 
                  step="100"
                  value={incomeChange}
                  onChange={(e) => setIncomeChange(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" 
                />
                <span className={`font-semibold min-w-[80px] text-right ${incomeChange > 0 ? 'text-green-500' : incomeChange < 0 ? 'text-red-500' : 'text-gray-500'}`}>
                  {incomeChange > 0 ? '+' : ''}{formatCurrency(incomeChange)}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Monthly Expenses Change
              </label>
              <div className="flex items-center space-x-4">
                <input 
                  type="range" 
                  min="-5000" 
                  max="5000" 
                  step="100"
                  value={expenseChange}
                  onChange={(e) => setExpenseChange(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" 
                />
                <span className={`font-semibold min-w-[80px] text-right ${expenseChange < 0 ? 'text-green-500' : expenseChange > 0 ? 'text-red-500' : 'text-gray-500'}`}>
                  {expenseChange > 0 ? '+' : ''}{formatCurrency(expenseChange)}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Projection Horizon ({duration} Months)
              </label>
              <input 
                type="range" 
                min="1" 
                max="60" 
                step="1"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" 
              />
            </div>
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {result && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Monthly Savings</p>
                      <div className="flex items-end mt-1">
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                          {formatCurrency(result.scenario.monthly_savings)}
                        </p>
                        {result.impact.monthly_savings_change !== 0 && (
                          <span className={`ml-2 text-sm font-medium ${result.impact.monthly_savings_change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {result.impact.monthly_savings_change > 0 ? '+' : ''}{formatCurrency(result.impact.monthly_savings_change)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-full">
                      <DollarSign className="w-5 h-5 text-indigo-500" />
                    </div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Savings Rate</p>
                      <div className="flex items-end mt-1">
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                          {result.scenario.savings_rate.toFixed(1)}%
                        </p>
                        {result.impact.savings_rate_change !== 0 && (
                          <span className={`ml-2 text-sm font-medium ${result.impact.savings_rate_change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {result.impact.savings_rate_change > 0 ? '+' : ''}{result.impact.savings_rate_change.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-full">
                      <TrendingUp className="w-5 h-5 text-emerald-500" />
                    </div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Financial Health</p>
                      <div className="flex items-end mt-1">
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                          {result.scenario.financial_health_score.toFixed(0)}
                        </p>
                        {result.impact.health_score_change !== 0 && (
                          <span className={`ml-2 text-sm font-medium ${result.impact.health_score_change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {result.impact.health_score_change > 0 ? '+' : ''}{result.impact.health_score_change.toFixed(0)} pts
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="p-3 bg-purple-50 dark:bg-purple-900/30 rounded-full">
                      <Activity className="w-5 h-5 text-purple-500" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Chart */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Cumulative Savings Projection</h3>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={result.future_projection}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" opacity={0.2} />
                      <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis 
                        stroke="#9CA3AF" 
                        fontSize={12} 
                        tickLine={false} 
                        axisLine={false}
                        tickFormatter={(value) => `$${value/1000}k`}
                      />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }}
                        formatter={(value: any) => formatCurrency(Number(value))}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        name="Baseline Savings"
                        dataKey="baseline_savings" 
                        stroke="#9CA3AF" 
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                      <Line 
                        type="monotone" 
                        name="Scenario Savings"
                        dataKey="scenario_savings" 
                        stroke="#6366F1" 
                        strokeWidth={3}
                        dot={false}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Insights & Goals */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <Target className="w-5 h-5 mr-2 text-rose-500" />
                    Goal Acceleration
                  </h3>
                  <div className="space-y-4">
                    {result.goal_impacts.length === 0 ? (
                      <p className="text-gray-500 dark:text-gray-400">No active goals to track.</p>
                    ) : (
                      result.goal_impacts.map((g, idx) => (
                        <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">{g.name}</p>
                            <p className="text-sm text-gray-500">
                              {g.months_improvement && g.months_improvement > 0 ? (
                                <span className="text-green-500 font-medium">{g.months_improvement} months faster</span>
                              ) : (
                                "No change"
                              )}
                            </p>
                          </div>
                          <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-700">
                            {g.scenario_projected_months ? `${g.scenario_projected_months} mo` : 'N/A'}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white shadow-md">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <CheckCircle2 className="w-5 h-5 mr-2" />
                    Smart Insights
                  </h3>
                  <div className="space-y-3">
                    {result.smart_insights.length === 0 ? (
                      <p className="text-indigo-100">No major insights for this scenario.</p>
                    ) : (
                      result.smart_insights.map((insight, idx) => (
                        <div key={idx} className="flex items-start">
                          <ChevronRight className="w-5 h-5 mr-1 flex-shrink-0 text-indigo-200 mt-0.5" />
                          <p className="text-indigo-50 leading-relaxed">{insight.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinancialPlanning;
