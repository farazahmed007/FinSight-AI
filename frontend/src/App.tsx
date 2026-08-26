import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ThemeProvider } from './components/ThemeProvider';
import { AnimatePresence } from 'framer-motion';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Transactions } from './pages/Transactions';
import Budgets from './pages/Budgets';
import { Analytics } from './pages/Analytics';
import { Forecasting } from './pages/Forecasting';
import { AIAssistant } from './pages/AIAssistant';
import { Recommendations } from './pages/Recommendations';
import Goals from './pages/Goals';
import FinancialHealth from './pages/FinancialHealth';
import FinancialPlanning from './pages/FinancialPlanning';

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/login" element={<Login />} />
        
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/budgets" element={<Budgets />} />
          <Route path="/goals" element={<Goals />} />
          <Route path="/financial-health" element={<FinancialHealth />} />
          <Route path="/planning" element={<FinancialPlanning />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/forecast" element={<Forecasting />} />
          <Route path="/assistant" element={<AIAssistant />} />
          <Route path="/recommendations" element={<Recommendations />} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="finsight-theme">
      <BrowserRouter>
        <AnimatedRoutes />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
