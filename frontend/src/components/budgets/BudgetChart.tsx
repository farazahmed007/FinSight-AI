import { Card } from '../Card';
import type { BudgetCategorySummary } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, Cell } from 'recharts';

interface BudgetChartProps {
  categories: BudgetCategorySummary[];
}

export function BudgetChart({ categories }: BudgetChartProps) {
  const data = categories.map(c => ({
    name: c.category.charAt(0).toUpperCase() + c.category.slice(1),
    budget: c.budget,
    spent: c.spent,
    status: c.status
  }));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OVER_BUDGET': return '#ef4444'; // red-500
      case 'NEAR_LIMIT': return '#f97316'; // orange-500
      case 'WATCH': return '#eab308';      // yellow-500
      default: return '#3b82f6';           // blue-500 (we'll use blue for spent, but highlight if over)
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
        Budget vs. Spending
      </h3>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" opacity={0.2} />
            <XAxis 
              dataKey="name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#6B7280' }} 
              dy={10} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#6B7280' }}
              tickFormatter={(value) => `₹${value / 1000}k`}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(107, 114, 128, 0.1)' }}
              contentStyle={{ 
                backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                border: 'none',
                borderRadius: '8px',
                color: '#fff'
              }}
              formatter={(value: any) => [`${formatCurrency(value)}`, '']}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="budget" name="Budget" fill="#e5e7eb" radius={[4, 4, 0, 0]} />
            <Bar dataKey="spent" name="Spent" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getStatusColor(entry.status)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
