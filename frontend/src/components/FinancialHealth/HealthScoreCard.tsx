import React from 'react';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface HealthScoreCardProps {
  score: number;
  status: string;
  previousScore?: number;
}

const HealthScoreCard: React.FC<HealthScoreCardProps> = ({ score, status, previousScore }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'EXCELLENT': return 'text-green-500';
      case 'GOOD': return 'text-blue-500';
      case 'FAIR': return 'text-yellow-500';
      case 'POOR': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'EXCELLENT': return 'bg-green-500/10';
      case 'GOOD': return 'bg-blue-500/10';
      case 'FAIR': return 'bg-yellow-500/10';
      case 'POOR': return 'bg-red-500/10';
      default: return 'bg-gray-500/10';
    }
  };

  const getScoreCircleColor = (score: number) => {
    if (score >= 80) return 'stroke-green-500';
    if (score >= 60) return 'stroke-blue-500';
    if (score >= 40) return 'stroke-yellow-500';
    return 'stroke-red-500';
  };

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  const diff = previousScore ? score - previousScore : 0;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Activity size={120} />
      </div>
      
      <h3 className="text-lg font-medium text-gray-400 mb-6 relative z-10">Overall Financial Health</h3>
      
      <div className="flex items-center justify-between relative z-10">
        <div className="relative w-40 h-40 flex items-center justify-center">
          <svg className="transform -rotate-90 w-40 h-40">
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              className="text-gray-800"
            />
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className={`${getScoreCircleColor(score)} transition-all duration-1000 ease-out`}
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-white">{score}</span>
            <span className="text-xs text-gray-500 uppercase tracking-wider">Out of 100</span>
          </div>
        </div>

        <div className="flex flex-col gap-4 text-right">
          <div>
            <div className="text-sm text-gray-400 mb-1">Status</div>
            <div className={`px-4 py-2 rounded-lg inline-block font-semibold ${getStatusBg(status)} ${getStatusColor(status)}`}>
              {status}
            </div>
          </div>
          
          {previousScore !== undefined && (
            <div>
              <div className="text-sm text-gray-400 mb-1">vs Last Month</div>
              <div className={`flex items-center justify-end gap-1 font-medium ${
                diff > 0 ? 'text-green-500' : diff < 0 ? 'text-red-500' : 'text-gray-400'
              }`}>
                {diff > 0 ? <TrendingUp size={18} /> : diff < 0 ? <TrendingDown size={18} /> : <Minus size={18} />}
                <span>{Math.abs(diff)} pts</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HealthScoreCard;
