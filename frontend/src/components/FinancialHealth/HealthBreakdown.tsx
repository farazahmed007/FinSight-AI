import React from 'react';
import { PiggyBank, PieChart, Target, CreditCard, Shield } from 'lucide-react';

interface HealthBreakdownProps {
  breakdown: {
    savings: number;
    budget_discipline: number;
    goal_progress: number;
    spending_control: number;
    financial_stability: number;
  };
}

const HealthBreakdown: React.FC<HealthBreakdownProps> = ({ breakdown }) => {
  const categories = [
    { key: 'savings', label: 'Savings Rate', icon: PiggyBank, color: 'bg-emerald-500', value: breakdown.savings },
    { key: 'budget_discipline', label: 'Budget Discipline', icon: PieChart, color: 'bg-blue-500', value: breakdown.budget_discipline },
    { key: 'goal_progress', label: 'Goal Progress', icon: Target, color: 'bg-purple-500', value: breakdown.goal_progress },
    { key: 'spending_control', label: 'Spending Control', icon: CreditCard, color: 'bg-amber-500', value: breakdown.spending_control },
    { key: 'financial_stability', label: 'Financial Stability', icon: Shield, color: 'bg-rose-500', value: breakdown.financial_stability }
  ];

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-lg font-medium text-gray-400 mb-6">Score Breakdown</h3>
      
      <div className="space-y-6">
        {categories.map((category) => {
          const Icon = category.icon;
          return (
            <div key={category.key}>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-3 text-gray-300">
                  <div className={`p-2 rounded-lg ${category.color} bg-opacity-20`}>
                    <Icon size={18} className={`text-${category.color.split('-')[1]}-400`} />
                  </div>
                  <span className="font-medium">{category.label}</span>
                </div>
                <span className="font-bold text-white">{category.value}/100</span>
              </div>
              
              <div className="w-full bg-gray-800 rounded-full h-2.5">
                <div 
                  className={`h-2.5 rounded-full ${category.color}`} 
                  style={{ width: `${category.value}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HealthBreakdown;
