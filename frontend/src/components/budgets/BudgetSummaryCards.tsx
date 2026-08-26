import { Card } from '../Card';
import { IndianRupee, Wallet, PiggyBank, Target } from 'lucide-react';
import type { BudgetSummary } from '../../types/budget';

interface BudgetSummaryCardsProps {
  summary: BudgetSummary;
}

export function BudgetSummaryCards({ summary }: BudgetSummaryCardsProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <Card className="flex items-center p-6 space-x-4">
        <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl">
          <Target size={24} />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Budget</p>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(summary.total_budget)}
          </h3>
        </div>
      </Card>

      <Card className="flex items-center p-6 space-x-4">
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-2xl">
          <Wallet size={24} />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Spent</p>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(summary.total_spent)}
          </h3>
        </div>
      </Card>

      <Card className="flex items-center p-6 space-x-4">
        <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-2xl">
          <PiggyBank size={24} />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Remaining</p>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(summary.remaining_budget)}
          </h3>
        </div>
      </Card>

      <Card className="flex items-center p-6 space-x-4">
        <div className="p-3 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-2xl">
          <IndianRupee size={24} />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Usage</p>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
            {summary.usage_percentage.toFixed(1)}%
          </h3>
        </div>
      </Card>
    </div>
  );
}
