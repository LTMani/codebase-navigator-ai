import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MetricsWidget from './components/MetricsWidget';

export default function App() {
    const [analytics, setAnalytics] = useState({
        activeUsers: 1420,
        monthlyRevenue: 48500,
        retentionRate: 94.2,
    });

    return (
        <div className="saas-app-container flex">
            <Sidebar />
            <div className="main-viewport flex-1">
                <Header title="Executive Overview" />
                <div className="dashboard-grid p-6">
                    <MetricsWidget title="Active Subscriptions" value={analytics.activeUsers} trend="+12%" />
                    <MetricsWidget title="Monthly Recurring Revenue" value={`$${analytics.monthlyRevenue.toLocaleString()}`} trend="+8.4%" />
                    <MetricsWidget title="Customer Retention" value={`${analytics.retentionRate}%`} trend="+1.1%" />
                </div>
            </div>
        </div>
    );
}
