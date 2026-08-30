import { useState, useRef, useEffect } from 'react';
import { Card } from '../components/Card';
import { queryAssistant } from '../services/api';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';
import { formatCurrency } from '../utils/formatters';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: any;
}

export const AIAssistant = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am FinSight AI. Ask me anything about your spending, trends, or how to save money.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "How much will I spend on food next month?",
    "What is the status of my goals?",
    "What is my financial health score?",
    "How can I reduce my subscription expenses?",
    "What is my spending summary for last month?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent, textOverride?: string) => {
    e?.preventDefault();
    const query = textOverride || input;
    if (!query.trim()) return;

    const newMessage: Message = { id: Date.now().toString(), role: 'user', content: query };
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await queryAssistant(query);
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.message,
        data: res
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (error: any) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: error.response?.data?.message || 'Sorry, I encountered an error processing your request.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <Card noPadding className="flex-1 flex flex-col overflow-hidden border-0 shadow-lg ring-1 ring-slate-200 dark:ring-slate-800">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-5 flex items-center gap-4 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Sparkles size={80} />
          </div>
          <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shrink-0 border border-white/20 shadow-inner z-10">
            <Bot size={24} className="text-white" />
          </div>
          <div className="z-10">
            <h2 className="font-bold text-lg">FinSight AI Assistant</h2>
            <p className="text-blue-100/90 text-sm font-medium">Your personal financial advisor</p>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50 dark:bg-[#0f172a] custom-scrollbar">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div 
                key={msg.id}
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.3 }}
                className={cn("flex gap-4", msg.role === 'user' ? 'flex-row-reverse' : '')}
              >
                <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm mt-1",
                  msg.role === 'user' 
                    ? 'bg-gradient-to-br from-indigo-500 to-purple-500 text-white' 
                    : 'bg-gradient-to-br from-blue-500 to-indigo-500 text-white'
                )}>
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={cn("max-w-[80%] rounded-2xl px-5 py-3.5 shadow-sm",
                  msg.role === 'user' 
                    ? 'bg-indigo-600 text-white rounded-tr-sm' 
                    : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-tl-sm'
                )}>
                  <p className="text-[15px] leading-relaxed">{msg.content}</p>
                  
                  {/* Optional rich data display */}
                  {msg.data?.intent === 'FORECAST_REQUEST' && msg.data.forecast_amount && (
                    <div className="mt-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
                      <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-2">Forecast Details</span>
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-slate-700 dark:text-slate-300 capitalize">{msg.data.category} <span className="text-slate-400 font-normal">({msg.data.horizon_days} days)</span></span>
                        <span className="font-bold text-lg text-blue-600 dark:text-blue-400">{formatCurrency(msg.data.forecast_amount)}</span>
                      </div>
                    </div>
                  )}
                  
                  {msg.data?.intent === 'RECOMMENDATION' && msg.data.recommendations && msg.data.recommendations.length > 0 && (
                    <div className="mt-4 space-y-3">
                      {msg.data.recommendations.map((rec: any, idx: number) => (
                        <div key={idx} className="bg-amber-50 dark:bg-amber-500/10 p-4 rounded-xl border border-amber-100 dark:border-amber-500/20 text-sm">
                          <strong className="text-amber-800 dark:text-amber-400 block mb-1">{rec.message}</strong>
                          <span className="text-amber-700 dark:text-amber-500/80 leading-relaxed block">{rec.suggested_action}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {msg.data?.intent && msg.data.intent.startsWith('FINANCIAL_HEALTH') && msg.data.score && (
                    <div className="mt-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Health Score</span>
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${msg.data.score > 75 ? 'bg-emerald-500/20 text-emerald-500' : msg.data.score > 50 ? 'bg-blue-500/20 text-blue-500' : 'bg-amber-500/20 text-amber-500'}`}>
                          {msg.data.status}
                        </span>
                      </div>
                      <div className="flex items-end gap-2 mb-4">
                        <span className="text-4xl font-bold text-slate-800 dark:text-slate-100">{msg.data.score}</span>
                        <span className="text-slate-400 text-sm mb-1">/ 100</span>
                      </div>
                      
                      {msg.data.breakdown && (
                        <div className="space-y-2 mt-4 pt-4 border-t border-slate-200 dark:border-slate-700/50">
                          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-2">Breakdown</span>
                          <div className="flex justify-between text-sm">
                            <span className="text-slate-600 dark:text-slate-300">Savings</span>
                            <span className="font-medium text-slate-800 dark:text-slate-200">{msg.data.breakdown.savings}/100</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-slate-600 dark:text-slate-300">Budget Discipline</span>
                            <span className="font-medium text-slate-800 dark:text-slate-200">{msg.data.breakdown.budget_discipline}/100</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-slate-600 dark:text-slate-300">Goal Progress</span>
                            <span className="font-medium text-slate-800 dark:text-slate-200">{msg.data.breakdown.goal_progress}/100</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {loading && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-4"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 text-white flex items-center justify-center shrink-0 mt-1 shadow-sm">
                  <Bot size={16} />
                </div>
                <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm flex gap-1.5 items-center h-[52px]">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.15s'}}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.3s'}}></div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 sm:p-5 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 z-10">
          <div className="flex flex-wrap gap-2 mb-4 hidden sm:flex">
            {suggestedQuestions.map((q, i) => (
              <button 
                key={i} 
                onClick={(e) => handleSubmit(e, q)}
                className="text-xs font-medium bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 px-3 py-1.5 rounded-full transition-colors"
                disabled={loading}
              >
                {q}
              </button>
            ))}
          </div>
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about spending, forecasts, or advice..."
              className="w-full pl-5 pr-14 py-3.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-slate-800 transition-colors shadow-sm dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="absolute right-2 p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
};
