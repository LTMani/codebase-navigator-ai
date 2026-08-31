import React from 'react';
import { MetricSummary } from '../types/models';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  data: MetricSummary;
}

export const MetricCard: React.FC<MetricCardProps> = ({ data }) => {
  const isPositive = data.trend === 'up';
  const isNegative = data.trend === 'down';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex justify-between items-center text-slate-400 text-sm font-medium">
        <span>{data.metricName}</span>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-3xl font-bold text-white tracking-tight">
          {data.currentValue.toLocaleString()}
        </span>
        <div className={`flex items-center text-xs font-semibold px-2 py-1 rounded-full ${
          isPositive ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
          isNegative ? 'bg-rose-950 text-rose-400 border border-rose-800' :
          'bg-slate-800 text-slate-400'
        }`}>
          {isPositive && <TrendingUp className="w-3.5 h-3.5 mr-1" />}
          {isNegative && <TrendingDown className="w-3.5 h-3.5 mr-1" />}
          {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-1" />}
          <span>{Math.abs(data.changePercentage)}%</span>
        </div>
      </div>
    </div>
  );
};
