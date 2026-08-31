import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

class LinearTrendForecaster:
    def __init__(self, horizon_steps: int = 14):
        self.horizon_steps = horizon_steps

    def fit_predict(self, historical_values: List[float], start_time: datetime, step_delta: timedelta) -> Dict[str, Any]:
        if len(historical_values) < 2:
            return {
                "predictions": [],
                "slope": 0.0,
                "intercept": 0.0,
                "r2_score": 0.0
            }

        x = np.arange(len(historical_values))
        y = np.array(historical_values)

        # Fit linear regression
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = float(coeffs[0]), float(coeffs[1])

        # R-squared calculation
        y_pred = slope * x + intercept
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        ss_res = np.sum((y - y_pred) ** 2)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        predictions = []
        last_time = start_time + len(historical_values) * step_delta
        for step in range(1, self.horizon_steps + 1):
            future_x = len(historical_values) + step - 1
            pred_val = max(0.0, slope * future_x + intercept)
            future_time = last_time + (step - 1) * step_delta
            predictions.append({
                "timestamp": future_time.isoformat(),
                "forecast_value": round(float(pred_val), 2),
                "lower_bound": round(float(max(0.0, pred_val * 0.9)), 2),
                "upper_bound": round(float(pred_val * 1.1), 2)
            })

        return {
            "predictions": predictions,
            "slope": round(slope, 4),
            "intercept": round(intercept, 4),
            "r2_score": round(float(r2), 4)
        }
