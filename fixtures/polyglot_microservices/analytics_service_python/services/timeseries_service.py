from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

class TimeSeriesService:
    @staticmethod
    def calculate_rolling_aggregates(values: List[float], window_size: int = 7) -> List[float]:
        if not values or window_size <= 0:
            return []
        arr = np.array(values)
        if len(arr) < window_size:
            return [float(np.mean(arr))]
        cumsum = np.cumsum(np.insert(arr, 0, 0))
        return list((cumsum[window_size:] - cumsum[:-window_size]) / float(window_size))

    @staticmethod
    def detect_anomalies(values: List[float], z_threshold: float = 2.5) -> List[Dict[str, Any]]:
        if len(values) < 5:
            return []
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return []
        anomalies = []
        for idx, val in enumerate(arr):
            z_score = abs((val - mean) / std)
            if z_score >= z_threshold:
                anomalies.append({
                    "index": idx,
                    "value": float(val),
                    "z_score": float(z_score),
                    "deviation_pct": float(((val - mean) / mean) * 100.0) if mean != 0 else 0.0
                })
        return anomalies
