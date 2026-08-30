import React, { useState, useEffect } from 'react';
import { Target, Plus, AlertCircle, CheckCircle2, Clock, Trash2, Edit2, TrendingUp, Calendar, Info } from 'lucide-react';
import { motion } from 'framer-motion';
import { getGoals, getGoalSummary, createGoal, updateGoal, deleteGoal } from '../services/api';
import { Card } from '../components/Card';
import { COMMON_CATEGORIES } from '../utils/constants';
import { formatCurrency } from '../utils/formatters';

export default function Goals() {
  const [goals, setGoals] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_amount: '',
    current_amount: '',
    target_date: '',
    category: ''
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [toastMessage, setToastMessage] = useState<{type: 'success'|'error', text: string} | null>(null);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      const [goalsData, summaryData] = await Promise.all([
        getGoals(),
        getGoalSummary()
      ]);
      setGoals(goalsData);
      setSummary(summaryData);
    } catch (error) {
      console.error('Failed to fetch goals:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = {
        name: formData.name,
        description: formData.description,
        target_amount: parseFloat(formData.target_amount),
        current_amount: formData.current_amount ? parseFloat(formData.current_amount) : 0,
        target_date: formData.target_date,
        category: formData.category
      };

      if (editingId) {
        await updateGoal(editingId, data);
        setToastMessage({ type: 'success', text: `Goal "${data.name}" updated successfully.` });
      } else {
        await createGoal(data);
        setToastMessage({ type: 'success', text: `Goal "${data.name}" created successfully.` });
      }
      
      setShowModal(false);
      setFormData({
        name: '', description: '', target_amount: '', current_amount: '', target_date: '', category: ''
      });
      setEditingId(null);
      fetchGoals();
      
      setTimeout(() => setToastMessage(null), 4000);
    } catch (error) {
      console.error('Failed to save goal:', error);
      setToastMessage({ type: 'error', text: 'Unable to create goal. Please check the entered details.' });
      setTimeout(() => setToastMessage(null), 4000);
    }
  };

  const handleEdit = (goal: any) => {
    setFormData({
      name: goal.name,
      description: goal.description || '',
      target_amount: goal.target_amount.toString(),
      current_amount: goal.current_amount.toString(),
      target_date: goal.target_date,
      category: goal.category || ''
    });
    setEditingId(goal.id);
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this goal?')) {
      try {
        await deleteGoal(id);
        fetchGoals();
      } catch (error) {
        console.error('Failed to delete goal:', error);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ON_TRACK': return 'text-green-500 bg-green-50 dark:bg-green-500/10';
      case 'NEAR_TARGET': return 'text-blue-500 bg-blue-50 dark:bg-blue-500/10';
      case 'AT_RISK': return 'text-yellow-500 bg-yellow-50 dark:bg-yellow-500/10';
      case 'BEHIND': return 'text-red-500 bg-red-50 dark:bg-red-500/10';
      case 'COMPLETED': return 'text-emerald-500 bg-emerald-50 dark:bg-emerald-500/10';
      default: return 'text-slate-500 bg-slate-50 dark:bg-slate-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ON_TRACK':
      case 'NEAR_TARGET': return <TrendingUp size={16} />;
      case 'AT_RISK':
      case 'BEHIND': return <AlertCircle size={16} />;
      case 'COMPLETED': return <CheckCircle2 size={16} />;
      default: return <Info size={16} />;
    }
  };

  if (loading && !goals.length) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {toastMessage && (
        <div className={`fixed bottom-4 right-4 p-4 rounded-xl shadow-lg flex items-center gap-3 z-50 text-white ${toastMessage.type === 'error' ? 'bg-red-500' : 'bg-emerald-500'}`}>
          {toastMessage.type === 'error' ? <AlertCircle size={20} /> : <CheckCircle2 size={20} />}
          <span className="font-medium">{toastMessage.text}</span>
        </div>
      )}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Financial Goals</h1>
          <p className="text-slate-500 dark:text-slate-400">Track and manage your savings goals</p>
        </div>
        <button
          onClick={() => {
            setEditingId(null);
            setFormData({ name: '', description: '', target_amount: '', current_amount: '', target_date: '', category: '' });
            setShowModal(true);
          }}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl transition-colors font-medium shadow-sm"
        >
          <Plus size={20} />
          New Goal
        </button>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400">
                <Target size={24} />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Total Goals</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                  {summary.active_goals} <span className="text-sm font-normal text-slate-400">active</span>
                </p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400">
                <CheckCircle2 size={24} />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Total Saved</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                  {formatCurrency(summary.total_saved)}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400">
                <TrendingUp size={24} />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Overall Progress</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                  {summary.overall_progress.toFixed(1)}%
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400">
                <Clock size={24} />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Required Monthly</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                  {formatCurrency(summary.total_required_monthly_savings || 0)}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.map((goal) => (
          <motion.div key={goal.id} layout initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
            <Card className="flex flex-col h-full overflow-hidden group">
              <div className="p-6 flex-1">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-lg text-slate-800 dark:text-slate-100">{goal.name}</h3>
                    {goal.category && (
                      <span className="inline-block px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs rounded-md mt-1">
                        {goal.category}
                      </span>
                    )}
                  </div>
                  <div className={`px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${getStatusColor(goal.status)}`}>
                    {getStatusIcon(goal.status)}
                    {goal.status.replace('_', ' ')}
                  </div>
                </div>

                {goal.description && (
                  <p className="text-sm text-slate-500 dark:text-slate-400 mb-4 line-clamp-2">{goal.description}</p>
                )}

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="font-medium text-slate-700 dark:text-slate-300">
                        {formatCurrency(goal.current_amount)}
                      </span>
                      <span className="text-slate-500 dark:text-slate-400">
                        of {formatCurrency(goal.target_amount)}
                      </span>
                    </div>
                    <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-blue-500"
                        style={{ width: `${goal.progress_percentage}%` }}
                      ></div>
                    </div>
                    <div className="text-right mt-1">
                      <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                        {goal.progress_percentage}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                    <div>
                      <p className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                        <Calendar size={12} /> Target Date
                      </p>
                      <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mt-0.5">
                        {new Date(goal.target_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                        <TrendingUp size={12} /> Req. Monthly
                      </p>
                      <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mt-0.5">
                        {formatCurrency(goal.required_monthly_savings)}
                      </p>
                    </div>
                  </div>
                  
                  {goal.status !== 'COMPLETED' && goal.projected_completion_date && (
                    <div className="text-xs bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg text-slate-600 dark:text-slate-300">
                      Projected to finish: <span className="font-medium">{new Date(goal.projected_completion_date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="border-t border-slate-100 dark:border-slate-800 p-3 bg-slate-50/50 dark:bg-slate-900/50 flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  onClick={() => handleEdit(goal)}
                  className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-white dark:hover:bg-slate-800 rounded-md transition-colors"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  onClick={() => handleDelete(goal.id)}
                  className="p-1.5 text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-white dark:hover:bg-slate-800 rounded-md transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </Card>
          </motion.div>
        ))}

        {goals.length === 0 && !loading && (
          <div className="col-span-full py-12 text-center text-slate-500 dark:text-slate-400">
            <Target size={48} className="mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No goals yet</h3>
            <p>Create your first financial goal to start tracking your savings progress.</p>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div 
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className="bg-white dark:bg-slate-900 rounded-2xl p-6 w-full max-w-md shadow-xl border border-slate-200 dark:border-slate-800"
          >
            <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">
              {editingId ? 'Edit Goal' : 'Create New Goal'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Goal Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g. Emergency Fund"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 capitalize"
                >
                  <option value="">Select a category</option>
                  {COMMON_CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Target Amount (₹) *</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.target_amount}
                    onChange={(e) => setFormData({...formData, target_amount: e.target.value})}
                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="50000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Current Saved (₹)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.current_amount}
                    onChange={(e) => setFormData({...formData, current_amount: e.target.value})}
                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Target Date *</label>
                <input
                  type="date"
                  required
                  value={formData.target_date}
                  onChange={(e) => setFormData({...formData, target_date: e.target.value})}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description (Optional)</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none h-20"
                  placeholder="Why are you saving for this?"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium"
                >
                  {editingId ? 'Update Goal' : 'Create Goal'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
}
