import React, { useState } from 'react';
import { calculateGoalPlan } from '../../services/api';
import { Target, TrendingUp, Calendar, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

interface GoalPlanResult {
  goal_amount: number;
  target_date: string;
  months_to_goal: number;
  required_monthly_savings: number;
  current_projected_capacity: number;
  feasibility: string;
  shortfall: number;
}

const GoalCalculator: React.FC = () => {
  const [goalAmount, setGoalAmount] = useState(10000);
  const [targetDate, setTargetDate] = useState(() => {
    const date = new Date();
    date.setFullYear(date.getFullYear() + 1);
    return date.toISOString().split('T')[0];
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GoalPlanResult | null>(null);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await calculateGoalPlan({
        target_amount: goalAmount,
        target_date: targetDate
      });
      setResult(res);
    } catch (error) {
      console.error("Failed to calculate goal plan", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 mt-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Goal Planning Calculator</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Determine if your savings goal is realistic based on your current financial trajectory.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Goal Amount
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Target className="h-5 w-5 text-gray-400" />
              </div>
              <input 
                type="number" 
                value={goalAmount}
                onChange={(e) => setGoalAmount(Number(e.target.value))}
                className="pl-10 w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target Date
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Calendar className="h-5 w-5 text-gray-400" />
              </div>
              <input 
                type="date" 
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                className="pl-10 w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
          
          <button 
            onClick={handleCalculate}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Calculating...' : 'Check Feasibility'}
          </button>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-xl flex flex-col justify-center">
          {result ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 mb-4">
                {result.feasibility === 'HIGH' && <CheckCircle2 className="w-8 h-8 text-green-500" />}
                {result.feasibility === 'MEDIUM' && <AlertTriangle className="w-8 h-8 text-yellow-500" />}
                {result.feasibility === 'LOW' && <XCircle className="w-8 h-8 text-red-500" />}
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  {result.feasibility === 'HIGH' && "Highly Feasible!"}
                  {result.feasibility === 'MEDIUM' && "Moderately Feasible"}
                  {result.feasibility === 'LOW' && "Low Feasibility"}
                </h3>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Time to Goal:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{result.months_to_goal} months</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Required Monthly Savings:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result.required_monthly_savings)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Your Current Monthly Capacity:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result.current_projected_capacity)}</span>
                </div>
                
                {result.shortfall > 0 && (
                  <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-red-500 font-medium">Monthly Shortfall:</span>
                    <span className="font-bold text-red-500">{formatCurrency(result.shortfall)}</span>
                  </div>
                )}
              </div>
              
              <p className="text-sm mt-4 text-gray-600 dark:text-gray-300">
                {result.feasibility === 'HIGH' && "You are well on your way to reaching this goal based on your current savings rate!"}
                {result.feasibility === 'MEDIUM' && "You can reach this goal, but it will require you to maintain strict financial discipline and maximize your current savings capacity."}
                {result.feasibility === 'LOW' && "This goal is currently out of reach by the target date. You'll need to extend the timeline or significantly increase your monthly savings."}
              </p>
            </div>
          ) : (
            <div className="text-center text-gray-400">
              <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p>Enter a goal and date to check feasibility</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoalCalculator;
