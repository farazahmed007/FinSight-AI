import React from 'react';
import { AlertCircle, CheckCircle, Info, ChevronRight, TrendingUp } from 'lucide-react';

interface Insight {
  type: string;
  severity: string;
  title: string;
  message: string;
  reason: string;
  category?: string;
  suggested_action: string;
}

interface Improvement {
  action: string;
  estimated_points: number;
}

interface HealthInsightCardProps {
  insights: Insight[];
  strengths: string[];
  weaknesses: string[];
  improvements: Improvement[];
}

const HealthInsightCard: React.FC<HealthInsightCardProps> = ({ insights, improvements }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <AlertCircle className="text-red-500" size={24} />;
      case 'medium': return <Info className="text-yellow-500" size={24} />;
      case 'low': return <Info className="text-blue-500" size={24} />;
      case 'positive': return <CheckCircle className="text-green-500" size={24} />;
      default: return <Info className="text-gray-400" size={24} />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-500/10 border-red-500/20';
      case 'medium': return 'bg-yellow-500/10 border-yellow-500/20';
      case 'low': return 'bg-blue-500/10 border-blue-500/20';
      case 'positive': return 'bg-green-500/10 border-green-500/20';
      default: return 'bg-gray-800 border-gray-700';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-white">Smart Insights</h3>
        <span className="bg-indigo-500/20 text-indigo-400 text-xs font-semibold px-2 py-1 rounded-full flex items-center gap-1">
          AI Powered
        </span>
      </div>
      
      <div className="space-y-4 flex-grow overflow-y-auto pr-2 custom-scrollbar">
        {insights.map((insight, index) => (
          <div key={index} className={`p-4 rounded-lg border ${getSeverityBg(insight.severity)}`}>
            <div className="flex gap-4">
              <div className="mt-1 flex-shrink-0">
                {getSeverityIcon(insight.severity)}
              </div>
              <div>
                <h4 className="text-white font-medium mb-1">{insight.title}</h4>
                <p className="text-sm text-gray-300 mb-3">{insight.message}</p>
                <div className="bg-gray-950/50 rounded p-3 mt-2">
                  <p className="text-xs text-gray-400 mb-1"><span className="font-semibold">Why:</span> {insight.reason}</p>
                  <p className="text-xs text-indigo-300 font-medium flex items-center gap-1 mt-2">
                    <ChevronRight size={14} /> Action: {insight.suggested_action}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {improvements.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-800">
            <h4 className="text-md font-medium text-gray-300 mb-3 flex items-center gap-2">
              <TrendingUp size={18} className="text-emerald-500" />
              How to improve your score
            </h4>
            <div className="space-y-2">
              {improvements.map((imp, idx) => (
                <div key={idx} className="flex justify-between items-center bg-gray-800/50 p-3 rounded-lg">
                  <span className="text-sm text-gray-300">{imp.action}</span>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/20 px-2 py-1 rounded">
                    +{imp.estimated_points} pts
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthInsightCard;
