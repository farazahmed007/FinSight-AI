import React, { useState } from 'react';
import { checkAffordability } from '../../services/api';
import { DollarSign, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

interface AffordabilityResult {
  purchase_amount: number;
  months: number;
  current_projected_capacity: number;
  required_monthly_savings: number;
  status: string;
  shortfall: number;
}

const AffordabilityCalculator: React.FC = () => {
  const [purchaseAmount, setPurchaseAmount] = useState(5000);
  const [months, setMonths] = useState(6);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AffordabilityResult | null>(null);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await checkAffordability({
        purchase_amount: purchaseAmount,
        months: months
      });
      setResult(res);
    } catch (error) {
      console.error("Failed to check affordability", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 mt-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Affordability Calculator</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Find out if you can afford a specific purchase without compromising your financial stability.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Purchase Amount
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <DollarSign className="h-5 w-5 text-gray-400" />
              </div>
              <input 
                type="number" 
                value={purchaseAmount}
                onChange={(e) => setPurchaseAmount(Number(e.target.value))}
                className="pl-10 w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Timeframe ({months} Months)
            </label>
            <input 
              type="range" 
              min="1" 
              max="60" 
              step="1"
              value={months}
              onChange={(e) => setMonths(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" 
            />
          </div>
          
          <button 
            onClick={handleCalculate}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Calculating...' : 'Check Affordability'}
          </button>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-xl flex flex-col justify-center">
          {result ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 mb-4">
                {result.status === 'AFFORDABLE' && <CheckCircle2 className="w-8 h-8 text-green-500" />}
                {result.status === 'TIGHT' && <AlertTriangle className="w-8 h-8 text-yellow-500" />}
                {result.status === 'NOT_AFFORDABLE' && <XCircle className="w-8 h-8 text-red-500" />}
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  {result.status === 'AFFORDABLE' && "It's Affordable!"}
                  {result.status === 'TIGHT' && "It's a Tight Fit"}
                  {result.status === 'NOT_AFFORDABLE' && "Not Currently Affordable"}
                </h3>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Required Monthly Savings:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result.required_monthly_savings)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Your Current Monthly Capacity:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result.current_projected_capacity)}</span>
                </div>
                
                {result.shortfall > 0 && (
                  <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-red-500 font-medium">Monthly Shortfall:</span>
                    <span className="font-bold text-red-500">{formatCurrency(result.shortfall)}</span>
                  </div>
                )}
              </div>
              
              <p className="text-sm mt-4 text-gray-600 dark:text-gray-300">
                {result.status === 'AFFORDABLE' && "Based on your current spending habits, you have enough cash flow to save for this."}
                {result.status === 'TIGHT' && "You can technically afford this, but it will consume a large portion of your remaining capacity."}
                {result.status === 'NOT_AFFORDABLE' && "You do not have enough monthly cash flow to save for this. Consider extending the timeframe or cutting back on expenses."}
              </p>
            </div>
          ) : (
            <div className="text-center text-gray-400">
              <CalculatorIcon className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p>Enter details to check affordability</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const CalculatorIcon = (props: any) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="16" height="20" x="4" y="2" rx="2" />
    <line x1="8" x2="16" y1="6" y2="6" />
    <line x1="16" x2="16.01" y1="10" y2="10" />
    <line x1="12" x2="12.01" y1="10" y2="10" />
    <line x1="8" x2="8.01" y1="10" y2="10" />
    <line x1="16" x2="16.01" y1="14" y2="14" />
    <line x1="12" x2="12.01" y1="14" y2="14" />
    <line x1="8" x2="8.01" y1="14" y2="14" />
    <line x1="16" x2="16.01" y1="18" y2="18" />
    <line x1="12" x2="12.01" y1="18" y2="18" />
    <line x1="8" x2="8.01" y1="18" y2="18" />
  </svg>
);

export default AffordabilityCalculator;
