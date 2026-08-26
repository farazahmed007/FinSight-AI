import { Card } from '../Card';
import { AlertTriangle, AlertCircle, Info, Bell } from 'lucide-react';
import type { BudgetAlert } from '../../types/budget';

interface BudgetAlertsProps {
  alerts: BudgetAlert[];
}

export function BudgetAlerts({ alerts }: BudgetAlertsProps) {
  if (!alerts || alerts.length === 0) {
    return (
      <Card className="p-6 h-full flex flex-col justify-center items-center text-center">
        <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 mb-3">
          <Bell size={24} />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
          All Good!
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          You have no budget alerts for this month. You're staying well within your limits.
        </p>
      </Card>
    );
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'OVER_BUDGET':
        return <AlertTriangle size={20} className="text-red-500" />;
      case 'NEAR_LIMIT':
        return <AlertCircle size={20} className="text-orange-500" />;
      default:
        return <Info size={20} className="text-blue-500" />;
    }
  };

  const getAlertBgClass = (type: string) => {
    switch (type) {
      case 'OVER_BUDGET':
        return 'bg-red-50 dark:bg-red-900/10 border-red-100 dark:border-red-900/30';
      case 'NEAR_LIMIT':
        return 'bg-orange-50 dark:bg-orange-900/10 border-orange-100 dark:border-orange-900/30';
      default:
        return 'bg-blue-50 dark:bg-blue-900/10 border-blue-100 dark:border-blue-900/30';
    }
  };

  return (
    <Card className="p-6 h-full">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <Bell className="mr-2 h-5 w-5 text-gray-500" />
        Budget Alerts
      </h3>
      <div className="space-y-3 overflow-y-auto max-h-[250px] pr-2 custom-scrollbar">
        {alerts.map((alert, index) => (
          <div 
            key={index} 
            className={`p-3 rounded-lg border flex items-start space-x-3 ${getAlertBgClass(alert.type)}`}
          >
            <div className="mt-0.5">{getAlertIcon(alert.type)}</div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {alert.message}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
