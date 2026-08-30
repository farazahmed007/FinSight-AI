import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if not already on login
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const getTransactions = () => api.get('/transactions').then(res => res.data);
export const getAnalyticsSummary = () => api.get('/analytics/summary').then(res => res.data);
export const getAnalyticsCategories = (days = 30) => api.get(`/analytics/categories?days=${days}`).then(res => res.data);
export const getAnalyticsMonthly = () => api.get('/analytics/monthly').then(res => res.data);
export const getForecast = (category: string, horizon = 30) => api.get(`/forecast/${category}?horizon=${horizon}`).then(res => res.data);
export const getRecommendations = () => api.get('/recommendations').then(res => res.data);
export const queryAssistant = (query: string) => api.post('/query', { query }).then(res => res.data);

// Budget endpoints
export const getBudgets = (month?: string) => api.get(`/budgets${month ? `?month=${month}` : ''}`).then(res => res.data);
export const getBudgetSummary = (month?: string) => api.get(`/budgets/summary${month ? `?month=${month}` : ''}`).then(res => res.data);
export const createBudget = (data: {category: string, amount: number, month: string}) => api.post('/budgets', data).then(res => res.data);
export const updateBudget = (id: number, data: {amount: number}) => api.put(`/budgets/${id}`, data).then(res => res.data);
export const deleteBudget = (id: number) => api.delete(`/budgets/${id}`).then(res => res.data);

// Goals endpoints
export const getGoals = () => api.get('/goals').then(res => res.data);
export const getGoalSummary = () => api.get('/goals/summary').then(res => res.data);
export const createGoal = (data: {name: string, description?: string, target_amount: number, current_amount?: number, target_date: string, category?: string}) => api.post('/goals', data).then(res => res.data);
export const updateGoal = (id: number, data: any) => api.put(`/goals/${id}`, data).then(res => res.data);
export const deleteGoal = (id: number) => api.delete(`/goals/${id}`).then(res => res.data);

// Financial Health endpoints
export const getFinancialHealth = () => api.get('/financial-health').then(res => res.data);
export const getFinancialHealthHistory = () => api.get('/financial-health/history').then(res => res.data);

// Planning endpoints
export const simulateScenario = (data: any) => api.post('/planning/simulate', data).then(res => res.data);
export const checkAffordability = (data: any) => api.post('/planning/affordability', data).then(res => res.data);
export const calculateGoalPlan = (data: any) => api.post('/planning/goal-calculator', data).then(res => res.data);

export default api;
