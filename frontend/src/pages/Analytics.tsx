import { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { getAnalyticsCategories, getAnalyticsMonthly, getFinancialHealthHistory } from '../services/api';
import { XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import HealthTrendChart from '../components/FinancialHealth/HealthTrendChart';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export const Analytics = () => {
  const [categories, setCategories] = useState<any[]>([]);
  const [monthly, setMonthly] = useState<any[]>([]);
  const [healthHistory, setHealthHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(90);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [catRes, monthRes, healthRes] = await Promise.all([
          getAnalyticsCategories(days),
          getAnalyticsMonthly(),
          getFinancialHealthHistory()
        ]);
        
        const formattedCats = Object.entries(catRes)
          .map(([category, amount]) => ({ category, amount }))
          .sort((a, b) => Number(b.amount) - Number(a.amount));
          
        setCategories(formattedCats);
        setMonthly(monthRes);
        setHealthHistory(healthRes);
      } catch (error) {
        console.error("Failed to fetch analytics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [days]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Analytics Deep Dive</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Explore your spending patterns and category breakdowns</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 h-[500px] flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Income & Expenses Over Time</h3>
          </div>
          <div className="flex-1 min-h-0">
            {loading ? (
              <div className="h-full flex justify-center items-center"><Loader2 size={32} className="animate-spin text-blue-500" /></div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthly} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} dy={10} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} dx={-10} tick={{fill: '#94a3b8', fontSize: 12}} tickFormatter={(val) => `₹${val/1000}k`} />
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
                  <RechartsTooltip 
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', backgroundColor: 'var(--tw-colors-slate-900)', color: '#fff'}} 
                    itemStyle={{color: '#fff'}}
                  />
                  <Legend verticalAlign="top" height={36} iconType="circle"/>
                  <Area type="monotone" dataKey="income" name="Income" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorIncome)" />
                  <Area type="monotone" dataKey="expense" name="Expense" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorExpense)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        <Card className="h-[500px] flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Top Categories</h3>
            <select 
              value={days}
              onChange={e => setDays(Number(e.target.value))}
              className="text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow cursor-pointer"
            >
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
              <option value={180}>Last 180 Days</option>
              <option value={365}>Last Year</option>
            </select>
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {loading ? (
              <div className="h-full flex justify-center items-center"><Loader2 size={32} className="animate-spin text-blue-500" /></div>
            ) : (
              <div className="space-y-6">
                {categories.map((c, i) => {
                  const maxAmount = Number(categories[0]?.amount) || 1;
                  const percentage = Math.min((Number(c.amount) / maxAmount) * 100, 100);
                  return (
                    <motion.div 
                      key={i}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                    >
                      <div className="flex justify-between text-sm mb-2">
                        <span className="font-medium text-slate-700 dark:text-slate-300 capitalize">{c.category}</span>
                        <span className="font-bold text-slate-900 dark:text-slate-100">₹{Number(c.amount).toLocaleString(undefined, {maximumFractionDigits: 0})}</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                        <motion.div 
                          className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full" 
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </motion.div>
                  );
                })}
                {categories.length === 0 && (
                  <div className="text-center text-slate-500 py-10">No data available for this period.</div>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Financial Health Trend Row */}
      <div className="mt-6">
        <HealthTrendChart history={healthHistory} />
      </div>
    </div>
  );
};
