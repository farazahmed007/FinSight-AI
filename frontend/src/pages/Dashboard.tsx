import { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { getAnalyticsSummary, getAnalyticsMonthly, getAnalyticsCategories, getBudgetSummary, getGoalSummary, getFinancialHealth } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { IndianRupee, TrendingUp, TrendingDown, PiggyBank, ReceiptText, Activity, Sparkles, Bell, Target, ArrowRight, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<any>(null);
  const [monthly, setMonthly] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [budgetAlerts, setBudgetAlerts] = useState<any[]>([]);
  const [goalSummary, setGoalSummary] = useState<any>(null);
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumRes, monthRes, catRes, goalRes, healthRes] = await Promise.all([
          getAnalyticsSummary(),
          getAnalyticsMonthly(),
          getAnalyticsCategories(30),
          getGoalSummary(),
          getFinancialHealth()
        ]);
        
        let budgRes = null;
        try {
          // get current month YYYY-MM
          const now = new Date();
          const monthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
          budgRes = await getBudgetSummary(monthStr);
        } catch (e) {
          console.error("Error fetching budgets for dashboard", e);
        }

        setSummary(sumRes);
        setMonthly(monthRes);
        setBudgetAlerts(budgRes?.alerts || []);
        setGoalSummary(goalRes);
        setHealthData(healthRes);
        
        // Format categories for PieChart
        const formattedCats = Object.entries(catRes).map(([name, value]) => ({ name, value }));
        setCategories(formattedCats);
      } catch (error) {
        console.error("Error fetching dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

  if (loading) {
    return (
      <div className="grid gap-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1,2,3,4].map(i => <div key={i} className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
          <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  const healthScore = healthData?.score || 0;
  const healthStatus = healthData?.status || 'UNKNOWN';
  const healthColor = healthStatus === 'EXCELLENT' ? 'text-emerald-500' : healthStatus === 'GOOD' ? 'text-blue-500' : healthStatus === 'FAIR' ? 'text-yellow-500' : 'text-red-500';

  return (
    <div className="space-y-8">
      {/* Financial Health & AI Insights Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card 
          className="lg:col-span-1 bg-gradient-to-br from-slate-900 to-slate-800 dark:from-slate-800 dark:to-slate-950 text-white relative overflow-hidden border-none shadow-lg cursor-pointer transition-transform hover:scale-[1.02]"
          onClick={() => navigate('/financial-health')}
        >
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-32 h-32 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
          <div className="absolute top-0 right-20 w-32 h-32 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>
          
          <div className="relative z-10 flex flex-col h-full justify-between">
            <div>
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-slate-300 font-medium flex items-center gap-2">
                  <Activity size={18} /> Financial Health
                </h3>
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold bg-white/10 ${healthColor}`}>
                  {healthStatus}
                </span>
              </div>
              
              <div className="flex items-end gap-4 mb-6">
                <span className="text-6xl font-bold tracking-tight">{healthScore}</span>
                <span className="text-slate-400 text-sm mb-2">/ 100</span>
              </div>
            </div>

            <div className="flex items-center text-sm text-indigo-300 gap-1 group">
              View full analysis <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </Card>

        <Card className="lg:col-span-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border-blue-100 dark:border-blue-900/50">
          <div className="flex items-start gap-4 h-full">
            <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-md">
              <Sparkles size={24} />
            </div>
            <div className="flex flex-col justify-center h-full w-full">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">AI Financial Insight</h3>
              </div>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed line-clamp-3">
                {healthData?.summary || "Finsight AI is analyzing your transactions..."}
              </p>
              {healthData?.insights?.length > 0 && (
                <div className="mt-3 text-sm text-indigo-600 dark:text-indigo-400 font-medium">
                  Suggestion: {healthData.insights[0].suggested_action}
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* Plan Your Future Widget */}
        <Card 
          className="lg:col-span-1 bg-gradient-to-br from-indigo-600 to-purple-600 text-white relative overflow-hidden border-none shadow-lg cursor-pointer transition-transform hover:scale-[1.02]"
          onClick={() => navigate('/planning')}
        >
          <div className="relative z-10 flex flex-col h-full justify-between">
            <div>
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-indigo-100 font-medium flex items-center gap-2">
                  <BarChart3 size={18} /> Financial Planning
                </h3>
              </div>
              
              <div className="mb-6">
                <h4 className="text-2xl font-bold mb-2">What-If Simulator</h4>
                <p className="text-indigo-200 text-sm">See how changes in income or spending impact your future goals.</p>
              </div>
            </div>

            <div className="flex items-center text-sm text-indigo-100 gap-1 group font-medium bg-white/10 w-fit px-4 py-2 rounded-full backdrop-blur-sm">
              Try Simulator <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </Card>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {[
          { title: 'Total Balance', value: `₹${(summary?.net_savings || 0).toLocaleString()}`, icon: IndianRupee, color: 'blue' },
          { title: 'Total Income', value: `₹${(summary?.total_income || 0).toLocaleString()}`, icon: TrendingUp, color: 'emerald' },
          { title: 'Total Expenses', value: `₹${(summary?.total_expenses || 0).toLocaleString()}`, icon: TrendingDown, color: 'red' },
          { title: 'Savings Rate', value: `${summary?.savings_rate || 0}%`, icon: PiggyBank, color: 'indigo' },
          { title: 'Active Goals', value: `${goalSummary?.active_goals || 0}`, icon: Target, color: 'purple' },
        ].map((stat, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <Card className="flex items-center gap-5 hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 
                bg-${stat.color}-100 text-${stat.color}-600 dark:bg-${stat.color}-900/30 dark:text-${stat.color}-400`}>
                <stat.icon size={26} />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400 font-medium mb-1">{stat.title}</p>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stat.value}</h3>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Budget Alerts */}
      {budgetAlerts.length > 0 && (
        <Card className="bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-900/50 p-4">
          <div className="flex items-start gap-3">
            <Bell className="text-orange-600 dark:text-orange-400 mt-1 shrink-0" size={20} />
            <div>
              <h4 className="font-semibold text-orange-800 dark:text-orange-300 mb-1">Budget Alerts</h4>
              <ul className="space-y-1">
                {budgetAlerts.map((alert, idx) => (
                  <li key={idx} className="text-sm text-orange-700 dark:text-orange-400">
                    • {alert.message}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="h-[450px] flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Income vs Expenses</h3>
          </div>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly} margin={{ top: 5, right: 10, left: 0, bottom: 5 }} barSize={32}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dx={-10} 
                  tickFormatter={(val) => `₹${val/1000}k`}
                />
                <RechartsTooltip 
                  cursor={{fill: 'rgba(148, 163, 184, 0.1)'}} 
                  contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)', backgroundColor: 'var(--tw-colors-slate-900)', color: '#fff'}} 
                  itemStyle={{color: '#fff'}}
                />
                <Legend wrapperStyle={{paddingTop: '20px'}} />
                <Bar dataKey="income" name="Income" fill="#10b981" radius={[6, 6, 0, 0]} />
                <Bar dataKey="expense" name="Expense" fill="#ef4444" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="h-[450px] flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Spending Breakdown</h3>
          </div>
          <div className="flex-1 min-h-0">
            {categories.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categories}
                    cx="50%"
                    cy="45%"
                    innerRadius={90}
                    outerRadius={130}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                  >
                    {categories.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', backgroundColor: 'var(--tw-colors-slate-900)', color: '#fff'}} 
                    itemStyle={{color: '#fff'}}
                  />
                  <Legend iconType="circle" wrapperStyle={{fontSize: '12px', paddingTop: '10px'}} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 dark:text-slate-400 flex-col gap-3">
                <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                  <ReceiptText size={32} className="text-slate-300 dark:text-slate-600" />
                </div>
                <p>No recent transactions</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
