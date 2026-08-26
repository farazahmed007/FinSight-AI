import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, ReceiptText, BarChart3, TrendingUp, Bot, Lightbulb, LogOut, Sun, Moon, Bell, Target, Activity } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import { motion, AnimatePresence } from 'framer-motion';

export const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, setTheme } = useTheme();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} />, group: 'OVERVIEW' },
    { name: 'Analytics', path: '/analytics', icon: <BarChart3 size={20} />, group: 'OVERVIEW' },
    { name: 'Transactions', path: '/transactions', icon: <ReceiptText size={20} />, group: 'MONEY' },
    { name: 'Budgets', path: '/budgets', icon: <Target size={20} />, group: 'MONEY' },
    { name: 'Goals', path: '/goals', icon: <Target size={20} />, group: 'MONEY' },
    { name: 'Forecasting', path: '/forecast', icon: <TrendingUp size={20} />, group: 'INTELLIGENCE' },
    { name: 'Financial Health', path: '/financial-health', icon: <Activity size={20} />, group: 'INTELLIGENCE' },
    { name: 'Financial Planning', path: '/planning', icon: <BarChart3 size={20} />, group: 'INTELLIGENCE' },
    { name: 'AI Assistant', path: '/assistant', icon: <Bot size={20} />, group: 'INTELLIGENCE' },
    { name: 'Recommendations', path: '/recommendations', icon: <Lightbulb size={20} />, group: 'INTELLIGENCE' },
  ];

  const groupedNav = navItems.reduce((acc, item) => {
    if (!acc[item.group]) acc[item.group] = [];
    acc[item.group].push(item);
    return acc;
  }, {} as Record<string, typeof navItems>);

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col z-20 shadow-sm relative">
        <div className="p-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent flex items-center gap-2">
            <Bot size={28} className="text-blue-600 dark:text-blue-400" />
            FinSight AI
          </h1>
        </div>
        <nav className="flex-1 px-4 mt-2 overflow-y-auto space-y-6">
          {Object.entries(groupedNav).map(([groupName, items]) => (
            <div key={groupName}>
              <h3 className="px-4 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
                {groupName}
              </h3>
              <div className="space-y-1">
                {items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className="relative flex items-center gap-3 px-4 py-2.5 rounded-xl transition-colors group text-sm font-medium"
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <motion.div 
                            layoutId="active-nav"
                            className="absolute inset-0 bg-blue-50 dark:bg-blue-900/30 rounded-xl"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                          />
                        )}
                        <span className={`relative z-10 flex items-center gap-3 w-full ${
                          isActive 
                            ? 'text-blue-700 dark:text-blue-400' 
                            : 'text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-slate-200'
                        }`}>
                          {item.icon}
                          {item.name}
                        </span>
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 w-full transition-colors text-sm font-medium"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-8 py-4 flex justify-between items-center z-10 sticky top-0">
          <div>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
              {navItems.find(i => i.path === (location.pathname === '/' ? '/' : `/${location.pathname.split('/')[1]}`))?.name || 'Welcome back, User!'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-full text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button className="p-2 rounded-full text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full border border-white dark:border-slate-900"></span>
            </button>
            <div className="h-8 w-[1px] bg-slate-200 dark:bg-slate-700 mx-2"></div>
            <div className="flex items-center gap-3 cursor-pointer">
              <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center text-white font-semibold text-sm shadow-sm border-2 border-white dark:border-slate-800">
                U
              </div>
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-8 relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};
