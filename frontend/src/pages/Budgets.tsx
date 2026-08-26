import { useState, useEffect } from 'react';
import { Plus, ChevronLeft, ChevronRight, Loader2, RefreshCw } from 'lucide-react';
import type { BudgetSummary, BudgetCategorySummary } from '../types/budget';
import { getBudgets, getBudgetSummary, createBudget, updateBudget, deleteBudget } from '../services/api';
import { BudgetSummaryCards } from '../components/budgets/BudgetSummaryCards';
import { BudgetCard } from '../components/budgets/BudgetCard';
import { BudgetChart } from '../components/budgets/BudgetChart';
import { BudgetAlerts } from '../components/budgets/BudgetAlerts';
import { CreateBudgetModal } from '../components/budgets/CreateBudgetModal';

export default function Budgets() {
  const [summary, setSummary] = useState<BudgetSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Month selection (defaults to current month YYYY-MM)
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<BudgetCategorySummary | null>(null);

  const getMonthString = (date: Date) => {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  };

  const getMonthDisplay = (date: Date) => {
    return date.toLocaleString('default', { month: 'long', year: 'numeric' });
  };

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getBudgetSummary(getMonthString(currentDate));
      setSummary(data);
    } catch (err: any) {
      console.error('Error fetching budgets:', err);
      setError('Failed to load budget data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, [currentDate]);

  const handlePrevMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() - 1);
    setCurrentDate(newDate);
  };

  const handleNextMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + 1);
    setCurrentDate(newDate);
  };

  const handleCreateOrUpdate = async (data: { category: string, amount: number, month: string }) => {
    try {
      if (editingCategory) {
        // We'd ideally have the ID, but our API allows finding by category and month.
        // Wait, the API delete/update uses budget ID.
        // Wait, our backend schema for budget return might not include ID in the summary.
        // Let's assume we can just re-create it since the DB has a UNIQUE constraint,
        // Wait, the backend has an update endpoint that takes ID, but our UI only has category in summary.
        // Actually, our API updateBudget takes ID. Let's modify the backend or just use createBudget 
        // because createBudget might handle upsert, or we fetch the full budgets list.
        // Actually, if we just call createBudget, it will fail if it exists (Duplicate budget).
        // Let's just refetch after.
        // For now, let's assume we can fetch the budget ID or just use create Budget (if we implement upsert in backend).
        // Wait, I didn't implement upsert in backend create_budget. It raises 400 if exists.
        // Let's fetch all budgets to get the ID, or we can just send an update if we know the ID.
        // For simplicity, let's just make it call the API and refresh.
        // If we don't have ID, we can't update properly. Let's just use create for now and we'll fix it if needed.
        
        // Actually, we can fetch the budget list to find the ID.
        const budgetsResponse = await getBudgets(getMonthString(currentDate));
        const budgetToUpdate = budgetsResponse.budgets.find((b: any) => b.category === data.category);
        
        if (budgetToUpdate) {
          await updateBudget(budgetToUpdate.id, { amount: data.amount });
        } else {
          await createBudget(data);
        }
      } else {
        await createBudget(data);
      }
      setIsModalOpen(false);
      setEditingCategory(null);
      fetchBudgets();
    } catch (err: any) {
      console.error('Error saving budget:', err);
      alert(err.response?.data?.detail || 'Failed to save budget');
    }
  };

  const handleDelete = async (category: string) => {
    if (window.confirm(`Are you sure you want to delete the budget for ${category}?`)) {
      try {
        const budgetsResponse = await getBudgets(getMonthString(currentDate));
        const budgetToDelete = budgetsResponse.budgets.find((b: any) => b.category === category);
        
        if (budgetToDelete) {
          await deleteBudget(budgetToDelete.id);
          fetchBudgets();
        }
      } catch (err: any) {
        console.error('Error deleting budget:', err);
        alert('Failed to delete budget');
      }
    }
  };

  const openCreateModal = () => {
    setEditingCategory(null);
    setIsModalOpen(true);
  };

  const openEditModal = (category: string) => {
    if (summary) {
      const catSummary = summary.categories.find(c => c.category === category);
      if (catSummary) {
        setEditingCategory(catSummary);
        setIsModalOpen(true);
      }
    }
  };

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  // To fix TypeScript error for getBudgets not imported, let's import it above. (Already did)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Budgets</h1>
          <p className="text-gray-500 dark:text-gray-400">Track and manage your spending limits</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 rounded-lg p-1 border border-gray-200 dark:border-gray-700">
            <button 
              onClick={handlePrevMonth}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            >
              <ChevronLeft size={20} className="text-gray-600 dark:text-gray-300" />
            </button>
            <span className="text-sm font-medium text-gray-900 dark:text-white min-w-[120px] text-center">
              {getMonthDisplay(currentDate)}
            </span>
            <button 
              onClick={handleNextMonth}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            >
              <ChevronRight size={20} className="text-gray-600 dark:text-gray-300" />
            </button>
          </div>
          
          <button 
            onClick={openCreateModal}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-medium shadow-sm shadow-blue-500/20"
          >
            <Plus size={20} />
            <span>New Budget</span>
          </button>
        </div>
      </div>

      {error ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900 p-4 rounded-lg flex items-center justify-between">
          <span className="text-red-700 dark:text-red-400">{error}</span>
          <button onClick={fetchBudgets} className="text-red-700 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 flex items-center">
            <RefreshCw size={16} className="mr-1" /> Retry
          </button>
        </div>
      ) : summary ? (
        <>
          <BudgetSummaryCards summary={summary} />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <BudgetChart categories={summary.categories} />
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Category Budgets
                </h3>
                {summary.categories.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {summary.categories.map((cat, idx) => (
                      <BudgetCard 
                        key={idx} 
                        categorySummary={cat} 
                        onEdit={openEditModal}
                        onDelete={handleDelete}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-8 text-center border border-dashed border-gray-300 dark:border-gray-700">
                    <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
                      <Plus size={24} />
                    </div>
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Budgets Set</h4>
                    <p className="text-gray-500 dark:text-gray-400 mb-6">
                      You haven't set any budgets for this month. Start by creating your first budget.
                    </p>
                    <button 
                      onClick={openCreateModal}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium shadow-sm"
                    >
                      Create Budget
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-1 space-y-6">
              <div className="sticky top-6">
                <BudgetAlerts alerts={summary.alerts} />
              </div>
            </div>
          </div>
        </>
      ) : null}

      <CreateBudgetModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateOrUpdate}
        editingCategory={editingCategory}
        selectedMonth={getMonthString(currentDate)}
      />
    </div>
  );
}
