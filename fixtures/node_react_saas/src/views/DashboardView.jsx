import React, { useState, useEffect } from 'react';
import MetricsWidget from '../components/MetricsWidget';

export default function DashboardView() {
    const [stats, setStats] = useState({
        mrr: 54200,
        subscribers: 1890,
        activeWorkspaces: 340,
    });

    return (
        <div className="view-dashboard p-6 space-y-6">
            <h2 className="text-2xl font-bold text-slate-800">Executive Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricsWidget title="Monthly Recurring Revenue" value={`$${stats.mrr.toLocaleString()}`} trend="+14.2%" />
                <MetricsWidget title="Active Subscriptions" value={stats.subscribers} trend="+8.1%" />
                <MetricsWidget title="Active Workspaces" value={stats.activeWorkspaces} trend="+22.5%" />
            </div>
        </div>
    );
}
