import React, { useEffect, useState } from 'react';
import { MetricCard } from '../components/MetricCard';
import { MetricSummary } from '../types/models';

export const DashboardView: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Simulated metric hydration
    setMetrics([
      { metricName: 'Total Active Projects', currentValue: 124, previousValue: 110, changePercentage: 12.7, trend: 'up' },
      { metricName: 'Parsed AST Nodes', currentValue: 1458200, previousValue: 1200000, changePercentage: 21.5, trend: 'up' },
      { metricName: 'Architectural Hotspots', currentValue: 8, previousValue: 14, changePercentage: -42.8, trend: 'down' },
      { metricName: 'Mean System Latency (ms)', currentValue: 24.2, previousValue: 24.0, changePercentage: 0.8, trend: 'neutral' },
    ]);
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="p-8 text-slate-400">Loading enterprise dashboard...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">System Architecture &amp; Telemetry</h1>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((m) => (
          <MetricCard key={m.metricName} data={m} />
        ))}
      </div>
    </div>
  );
};
