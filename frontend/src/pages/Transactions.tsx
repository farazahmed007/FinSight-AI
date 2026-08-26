import { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { getTransactions } from '../services/api';
import { Loader2, Search, Filter, ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../utils/cn';

export const Transactions = () => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  useEffect(() => {
    const fetchTx = async () => {
      try {
        const data = await getTransactions();
        setTransactions(data);
      } catch (error) {
        console.error("Failed to fetch transactions", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTx();
  }, []);

  const filteredTransactions = transactions.filter(tx => 
    tx.merchant.toLowerCase().includes(searchTerm.toLowerCase()) || 
    tx.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Transactions</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">View and search your complete transaction history</p>
        </div>
        
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:flex-none">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text"
              placeholder="Search merchants, categories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-72 pl-10 pr-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow dark:text-slate-200"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shrink-0 font-medium">
            <Filter size={18} />
            Filter
          </button>
        </div>
      </div>

      <Card noPadding className="overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <Loader2 size={32} className="animate-spin text-blue-500" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-slate-50/50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider font-semibold border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-4">Transaction</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {filteredTransactions.map((tx, idx) => {
                  const isIncome = tx.type === 'income';
                  return (
                    <motion.tr 
                      initial={{ opacity: 0, y: 5 }} 
                      animate={{ opacity: 1, y: 0 }} 
                      transition={{ delay: idx * 0.02 }}
                      key={tx.id || idx} 
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            "w-10 h-10 rounded-full flex items-center justify-center shrink-0",
                            isIncome 
                              ? "bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400" 
                              : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 group-hover:bg-slate-200 dark:group-hover:bg-slate-700 transition-colors"
                          )}>
                            {isIncome ? <ArrowDownRight size={18} /> : <ArrowUpRight size={18} />}
                          </div>
                          <span className="font-medium text-slate-900 dark:text-slate-100">{tx.merchant}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-3 py-1 rounded-md text-xs font-medium border border-slate-200 dark:border-slate-700">
                          {tx.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 dark:text-slate-400">
                        {new Date(tx.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </td>
                      <td className={cn(
                        "px-6 py-4 text-right font-bold text-base",
                        isIncome ? "text-emerald-600 dark:text-emerald-400" : "text-slate-900 dark:text-slate-100"
                      )}>
                        {isIncome ? '+' : '-'}₹{Math.abs(tx.amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
            {filteredTransactions.length === 0 && (
              <div className="p-12 text-center text-slate-500 dark:text-slate-400 flex flex-col items-center gap-3">
                <Search size={40} className="text-slate-300 dark:text-slate-600" />
                <p>No transactions found matching "{searchTerm}"</p>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};
