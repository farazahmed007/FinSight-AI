import { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { getRecommendations } from '../services/api';
import { X, ArrowRight, AlertCircle, CheckCircle, Info, Loader2, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';
import { useNavigate } from 'react-router-dom';

export const Recommendations = () => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const handleDismiss = (index: number) => {
    setRecommendations(prev => prev.filter((_, i) => i !== index));
  };
  
  const handleAction = (rec: any) => {
    if (rec.suggested_action.toLowerCase().includes('what-if') || rec.suggested_action.toLowerCase().includes('simulate')) {
      navigate('/planning');
    } else if (rec.type === 'budget_alert') {
      navigate('/dashboard');
    } else {
      navigate('/planning');
    }
  };

  useEffect(() => {
    const fetchRecs = async () => {
      try {
        const res = await getRecommendations();
        setRecommendations(res);
      } catch (error) {
        console.error("Failed to fetch recommendations", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRecs();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-12rem)]">
        <Loader2 size={40} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">AI Recommendations</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Smart insights based on your spending trends</p>
        </div>
        <div className="px-4 py-2 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-xl flex items-center gap-2 font-medium border border-blue-100 dark:border-blue-500/20 shadow-sm">
          <Zap size={18} className="fill-blue-600 dark:fill-blue-400" />
          <span>Real-time Analysis</span>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <Card className="text-center py-20 border-dashed border-2">
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", bounce: 0.5 }}
            className="w-20 h-20 bg-emerald-100 dark:bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
          >
            <CheckCircle size={40} className="text-emerald-500 dark:text-emerald-400" />
          </motion.div>
          <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">You're doing great!</h3>
          <p className="text-slate-500 dark:text-slate-400 max-w-sm mx-auto">We don't have any specific alerts or recommendations for you right now based on your recent spending.</p>
        </Card>
      ) : (
        <div className="grid gap-6">
          <AnimatePresence>
            {recommendations.map((rec, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className={cn("p-6 rounded-2xl flex flex-col sm:flex-row gap-5 items-start relative overflow-hidden border shadow-sm",
                  rec.severity === 'high' ? 'bg-red-50 dark:bg-red-500/5 border-red-200 dark:border-red-500/20' :
                  rec.severity === 'medium' ? 'bg-amber-50 dark:bg-amber-500/5 border-amber-200 dark:border-amber-500/20' :
                  'bg-emerald-50 dark:bg-emerald-500/5 border-emerald-200 dark:border-emerald-500/20'
                )}
              >
                <div className="absolute top-0 right-0 p-6 opacity-[0.03] dark:opacity-[0.05] pointer-events-none">
                  {rec.severity === 'low' ? (
                    <CheckCircle size={120} />
                  ) : rec.severity === 'high' ? (
                    <AlertCircle size={120} />
                  ) : (
                    <Info size={120} />
                  )}
                </div>

                <div className={cn("shrink-0 w-12 h-12 rounded-full flex items-center justify-center relative z-10 shadow-sm",
                   rec.severity === 'low' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400' : 
                   rec.severity === 'high' ? 'bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400' : 
                   'bg-amber-100 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400'
                )}>
                  {rec.severity === 'low' ? (
                    <CheckCircle size={24} />
                  ) : rec.severity === 'high' ? (
                    <AlertCircle size={24} />
                  ) : (
                    <Info size={24} />
                  )}
                </div>
                
                <div className="flex-1 relative z-10 w-full">
                  <div className="flex flex-wrap items-center gap-3 mb-2">
                    <h3 className={cn("font-bold text-lg",
                      rec.severity === 'high' ? 'text-red-900 dark:text-red-400' :
                      rec.severity === 'medium' ? 'text-amber-900 dark:text-amber-400' :
                      'text-emerald-900 dark:text-emerald-400'
                    )}>{rec.message}</h3>
                    <span className={cn("text-xs px-2.5 py-1 rounded-full uppercase font-bold tracking-wider",
                      rec.severity === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400' :
                      rec.severity === 'medium' ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400' :
                      'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400'
                    )}>{rec.category}</span>
                  </div>
                  
                  <p className={cn("mb-5 leading-relaxed",
                    rec.severity === 'high' ? 'text-red-700/80 dark:text-red-400/80' :
                    rec.severity === 'medium' ? 'text-amber-700/80 dark:text-amber-400/80' :
                    'text-emerald-700/80 dark:text-emerald-400/80'
                  )}>{rec.reason}</p>
                  
                  <div className="bg-white/80 dark:bg-slate-900/50 p-4 rounded-xl font-medium text-slate-800 dark:text-slate-200 border border-slate-200/50 dark:border-slate-700/50 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
                      <span className="text-slate-400 mt-0.5 sm:mt-0 uppercase text-xs tracking-wider">Action</span>
                      <span>{rec.suggested_action}</span>
                    </div>
                    
                    <button 
                      onClick={() => handleAction(rec)}
                      className={cn("shrink-0 px-4 py-2 rounded-lg font-bold flex items-center gap-2 transition-colors",
                        rec.severity === 'high' ? 'bg-red-600 hover:bg-red-700 text-white' :
                        rec.severity === 'medium' ? 'bg-amber-600 hover:bg-amber-700 text-white' :
                        'bg-emerald-600 hover:bg-emerald-700 text-white'
                      )}
                    >
                      <span>Take Action</span>
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
                
                <button 
                  onClick={() => handleDismiss(i)}
                  className="absolute top-4 right-4 p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:text-slate-300 dark:hover:bg-slate-800 transition-colors z-20"
                  title="Dismiss this recommendation"
                >
                  <X size={20} />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};
