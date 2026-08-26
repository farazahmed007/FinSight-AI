

interface BudgetProgressProps {
  usagePercentage: number;
  status: 'ON_TRACK' | 'WATCH' | 'NEAR_LIMIT' | 'OVER_BUDGET';
}

export function BudgetProgress({ usagePercentage, status }: BudgetProgressProps) {
  let colorClass = 'bg-blue-500';
  
  if (status === 'OVER_BUDGET') {
    colorClass = 'bg-red-500';
  } else if (status === 'NEAR_LIMIT') {
    colorClass = 'bg-orange-500';
  } else if (status === 'WATCH') {
    colorClass = 'bg-yellow-500';
  } else {
    colorClass = 'bg-green-500';
  }

  // Cap width at 100% so it doesn't overflow
  const width = Math.min(100, Math.max(0, usagePercentage));

  return (
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mt-2 overflow-hidden">
      <div 
        className={`${colorClass} h-2.5 rounded-full transition-all duration-500`}
        style={{ width: `${width}%` }}
      ></div>
    </div>
  );
}
