import React, { useState, useEffect } from 'react';
import { getFinancialHealth, getFinancialHealthHistory } from '../services/api';
import HealthScoreCard from '../components/FinancialHealth/HealthScoreCard';
import HealthBreakdown from '../components/FinancialHealth/HealthBreakdown';
import HealthInsightCard from '../components/FinancialHealth/HealthInsightCard';
import HealthTrendChart from '../components/FinancialHealth/HealthTrendChart';
import { Loader2 } from 'lucide-react';

const FinancialHealth: React.FC = () => {
  const [healthData, setHealthData] = useState<any>(null);
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [health, history] = await Promise.all([
          getFinancialHealth(),
          getFinancialHealthHistory()
        ]);
        setHealthData(health);
        setHistoryData(history);
      } catch (err) {
        console.error("Failed to fetch financial health data", err);
        setError('Failed to load financial health data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={48} />
      </div>
    );
  }

  if (error || !healthData) {
    return (
      <div className="p-8">
        <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-xl">
          {error || 'An error occurred'}
        </div>
      </div>
    );
  }

  // Get previous score if available
  const previousScore = historyData.length > 1 ? historyData[historyData.length - 2].score : undefined;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-fade-in">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Financial Health</h1>
          <p className="text-gray-400">AI-powered insights into your financial well-being</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Score and Breakdown */}
        <div className="lg:col-span-1 space-y-6">
          <HealthScoreCard 
            score={healthData.score} 
            status={healthData.status} 
            previousScore={previousScore} 
          />
          <HealthBreakdown breakdown={healthData.breakdown} />
        </div>

        {/* Right Column: Insights and Trend */}
        <div className="lg:col-span-2 space-y-6">
          <div className="h-[400px]">
            <HealthInsightCard 
              insights={healthData.insights}
              strengths={healthData.strengths}
              weaknesses={healthData.weaknesses}
              improvements={healthData.improvement_opportunities}
            />
          </div>
          <HealthTrendChart history={historyData} />
        </div>
      </div>
    </div>
  );
};

export default FinancialHealth;
