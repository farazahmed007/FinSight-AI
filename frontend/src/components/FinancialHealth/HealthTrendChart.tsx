import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HealthSnapshot {
  id: number;
  score: number;
  created_at: string;
}

interface HealthTrendChartProps {
  history: HealthSnapshot[];
}

const HealthTrendChart: React.FC<HealthTrendChartProps> = ({ history }) => {
  // Format data for chart
  const data = history.map(snapshot => ({
    date: new Date(snapshot.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    score: snapshot.score
  }));

  if (data.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-64 flex flex-col items-center justify-center">
        <p className="text-gray-400">Not enough history to show trend.</p>
        <p className="text-sm text-gray-500 mt-2">Check back later as you use Finsight!</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-lg font-medium text-gray-400 mb-6">Health Score Trend</h3>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              left: -20,
              bottom: 0,
            }}
          >
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af" 
              tick={{fill: '#9ca3af', fontSize: 12}} 
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#9ca3af" 
              tick={{fill: '#9ca3af', fontSize: 12}}
              tickLine={false}
              axisLine={false}
              domain={[0, 100]}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#f3f4f6' }}
              itemStyle={{ color: '#8b5cf6' }}
            />
            <Area 
              type="monotone" 
              dataKey="score" 
              stroke="#8b5cf6" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorScore)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default HealthTrendChart;
