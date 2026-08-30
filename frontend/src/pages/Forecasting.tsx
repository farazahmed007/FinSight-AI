import { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { getForecast } from '../services/api';
import { formatCurrency } from '../utils/formatters';
import { XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Minus, Loader2 } from 'lucide-react';
import { cn } from '../utils/cn';

export const Forecasting = () => {
  const [category, setCategory] = useState('food');
  const [horizon, setHorizon] = useState(30);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const categories = ['food', 'transport', 'shopping', 'entertainment', 'utilities'];

  useEffect(() => {
    const fetchForecast = async () => {
      setLoading(true);
      try {
        const res = await getForecast(category, horizon);
        setData(res);
      } catch (error) {
        console.error("Failed to fetch forecast", error);
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, [category, horizon]);

  const chartData = data?.forecast_dates?.map((date: string, i: number) => ({
    date,
    amount: data.forecast_values[i]
  })) || [];

  const totalForecast = data?.forecast_values?.reduce((a: number, b: number) => a + b, 0) || 0;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Spending Forecast</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Predict future spending based on historical data using Holt-Winters</p>
        </div>
        
        <div className="flex gap-4">
          <select 
            value={category} 
            onChange={e => setCategory(e.target.value)}
            className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 rounded-xl px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none shadow-sm cursor-pointer"
          >
            {categories.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
          </select>
          <select 
            value={horizon} 
            onChange={e => setHorizon(Number(e.target.value))}
            className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 rounded-xl px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none shadow-sm cursor-pointer"
          >
            <option value={7}>Next 7 Days</option>
            <option value={14}>Next 14 Days</option>
            <option value={30}>Next 30 Days</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="col-span-1 md:col-span-2 h-[400px] flex flex-col">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-6">Forecasted Trend</h3>
          <div className="flex-1 min-h-0">
            {loading ? (
              <div className="h-full flex items-center justify-center">
                <Loader2 size={32} className="text-blue-500 animate-spin" />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
                  <XAxis 
                    dataKey="date" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{fill: '#94a3b8', fontSize: 12}} 
                    dy={10}
                    tickFormatter={(val) => {
                      const d = new Date(val);
                      return `${d.getDate()}/${d.getMonth()+1}`;
                    }}
                  />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dx={-10} tickFormatter={(val) => `₹${val}`} />
                  <RechartsTooltip 
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', backgroundColor: 'var(--tw-colors-slate-900)', color: '#fff'}} 
                    formatter={(value: any) => [formatCurrency(Number(value)), 'Predicted Amount']}
                    labelStyle={{color: '#94a3b8', marginBottom: '4px'}}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="amount" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorForecast)"
                    activeDot={{ r: 6, fill: '#3b82f6', stroke: 'var(--tw-colors-slate-900)', strokeWidth: 2 }} 
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 border-none relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <TrendingUp size={100} />
            </div>
            <div className="relative z-10">
              <h3 className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-2">Total Projected</h3>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-slate-900 dark:text-slate-100">
                  {loading ? '...' : formatCurrency(totalForecast)}
                </span>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 font-medium">
                over the next {horizon} days
              </p>
            </div>
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Trend Direction</h3>
            {loading ? (
              <div className="animate-pulse h-16 bg-slate-100 dark:bg-slate-800 rounded-xl"></div>
            ) : (
              <div className="flex items-center gap-4">
                <div className={cn("w-14 h-14 rounded-full flex items-center justify-center shrink-0",
                  data?.trend === 'increasing' ? 'bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400' :
                  data?.trend === 'decreasing' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400' :
                  'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                )}>
                  {data?.trend === 'increasing' ? <TrendingUp size={28} /> :
                   data?.trend === 'decreasing' ? <TrendingDown size={28} /> :
                   <Minus size={28} />}
                </div>
                <div>
                  <p className="text-xl font-bold text-slate-900 dark:text-slate-100 capitalize">{data?.trend}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 font-medium">
                    {data?.method === 'holt-winters' ? 'Holt-Winters ML Model' : 'Simple Average Fallback'}
                  </p>
                </div>
              </div>
            )}
          </Card>
          
          {data?.method === 'average-fallback' && (
            <div className="p-4 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
              <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-400 mb-1">Insufficient History</h4>
              <p className="text-xs text-amber-700 dark:text-amber-500/80 leading-relaxed">
                Not enough historical data (45 days required) for this category to run exponential smoothing. A simple average fallback is being used.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
