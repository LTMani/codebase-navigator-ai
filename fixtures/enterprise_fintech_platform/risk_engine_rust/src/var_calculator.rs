use std::cmp::Ordering;

/// Value at Risk (VaR) & Conditional VaR (Expected Shortfall) Engine
pub struct ValueAtRiskEngine {
    confidence_level: f64,
}

impl ValueAtRiskEngine {
    pub fn new(confidence_level: f64) -> Self {
        Self { confidence_level }
    }

    /// Historical Simulation VaR
    pub fn calculate_historical_var(&self, pnl_series: &mut [f64]) -> (f64, f64) {
        if pnl_series.is_empty() {
            return (0.0, 0.0);
        }

        pnl_series.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));

        let index = ((1.0 - self.confidence_level) * pnl_series.len() as f64).floor() as usize;
        let var_cutoff = -pnl_series[index.min(pnl_series.len() - 1)];

        // Expected Shortfall: average loss exceeding VaR
        let tail_losses: Vec<f64> = pnl_series[..=index].iter().map(|&x| -x).collect();
        let expected_shortfall = if !tail_losses.is_empty() {
            tail_losses.iter().sum::<f64>() / tail_losses.len() as f64
        } else {
            var_cutoff
        };

        (var_cutoff.max(0.0), expected_shortfall.max(0.0))
    }

    /// Parametric Variance-Covariance VaR
    pub fn calculate_parametric_var(&self, portfolio_value: f64, daily_volatility: f64, holding_period_days: f64) -> f64 {
        // Z-score for 99% = 2.326, 95% = 1.645
        let z_score = if self.confidence_level >= 0.99 {
            2.3263
        } else {
            1.6449
        };

        portfolio_value * z_score * daily_volatility * holding_period_days.sqrt()
    }
}
