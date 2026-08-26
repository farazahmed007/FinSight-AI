import { Card } from '../Card';
import type { BudgetCategorySummary } from '../../types/budget';
import { BudgetProgress } from './BudgetProgress';
import { Edit2, Trash2 } from 'lucide-react';
import {
  Coffee,
  Home,
  Bus,
  ShoppingCart,
  Film,
  Zap,
  Activity,
  CreditCard,
  MoreHorizontal
} from 'lucide-react';

interface BudgetCardProps {
  categorySummary: BudgetCategorySummary;
  onEdit: (category: string) => void;
  onDelete: (category: string) => void;
}

const CategoryIcon = ({ category }: { category: string }) => {
  const iconProps = { size: 20, className: 'text-gray-500 dark:text-gray-400' };
  switch (category.toLowerCase()) {
    case 'food': return <Coffee {...iconProps} />;
    case 'housing': return <Home {...iconProps} />;
    case 'transport': return <Bus {...iconProps} />;
    case 'shopping': return <ShoppingCart {...iconProps} />;
    case 'entertainment': return <Film {...iconProps} />;
    case 'utilities': return <Zap {...iconProps} />;
    case 'healthcare': return <Activity {...iconProps} />;
    case 'subscriptions': return <CreditCard {...iconProps} />;
    default: return <MoreHorizontal {...iconProps} />;
  }
};

export function BudgetCard({ categorySummary, onEdit, onDelete }: BudgetCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'OVER_BUDGET':
        return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded-full">Over Budget</span>;
      case 'NEAR_LIMIT':
        return <span className="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 rounded-full">Near Limit</span>;
      case 'WATCH':
        return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 rounded-full">Watch</span>;
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-full">On Track</span>;
    }
  };

  return (
    <Card className="p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <CategoryIcon category={categorySummary.category} />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white capitalize">
              {categorySummary.category}
            </h4>
            {getStatusBadge(categorySummary.status)}
          </div>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => onEdit(categorySummary.category)}
            className="p-1.5 text-gray-400 hover:text-blue-500 rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
          >
            <Edit2 size={16} />
          </button>
          <button 
            onClick={() => onDelete(categorySummary.category)}
            className="p-1.5 text-gray-400 hover:text-red-500 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Budget</span>
          <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(categorySummary.budget)}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Spent</span>
          <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(categorySummary.spent)}</span>
        </div>

        <BudgetProgress usagePercentage={categorySummary.usage_percentage} status={categorySummary.status} />
        
        <div className="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400 pt-1">
          <span>{categorySummary.usage_percentage.toFixed(1)}% Used</span>
          <span>{formatCurrency(categorySummary.remaining)} Remaining</span>
        </div>
      </div>
    </Card>
  );
}
