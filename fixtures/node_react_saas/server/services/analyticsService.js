class AnalyticsService {
    getExecutiveMetrics(timeRange = '30d') {
        return {
            timeRange,
            dailyActiveUsers: [
                { date: '2026-08-01', users: 1120 },
                { date: '2026-08-10', users: 1240 },
                { date: '2026-08-20', users: 1380 },
                { date: '2026-08-30', users: 1450 },
            ],
            churnRatePercent: 1.8,
            avgSessionDurationMinutes: 14.5,
            serverUptimePercent: 99.98,
        };
    }

    computeConversionFunnel(visitors, signups, activated, paid) {
        return {
            visitors,
            signupRate: Math.round((signups / Math.max(visitors, 1)) * 1000) / 10,
            activationRate: Math.round((activated / Math.max(signups, 1)) * 1000) / 10,
            conversionRate: Math.round((paid / Math.max(activated, 1)) * 1000) / 10,
        };
    }
}

module.exports = new AnalyticsService();
