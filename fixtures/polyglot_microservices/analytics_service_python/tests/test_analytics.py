import pytest
from datetime import datetime, timedelta
from fixtures.polyglot_microservices.analytics_service_python.services.timeseries_service import TimeSeriesService
from fixtures.polyglot_microservices.analytics_service_python.services.ml_forecaster import LinearTrendForecaster

def test_rolling_aggregates():
    values = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    result = TimeSeriesService.calculate_rolling_aggregates(values, window_size=3)
    assert len(result) == 5
    assert result[0] == pytest.approx(20.0)
    assert result[-1] == pytest.approx(60.0)

def test_anomaly_detection():
    normal_and_outlier = [10.0, 11.0, 10.5, 9.8, 10.2, 95.0, 10.1]
    anomalies = TimeSeriesService.detect_anomalies(normal_and_outlier, z_threshold=2.0)
    assert len(anomalies) == 1
    assert anomalies[0]["index"] == 5
    assert anomalies[0]["value"] == 95.0

def test_forecaster_trend():
    growth_series = [10.0, 20.0, 30.0, 40.0, 50.0]
    forecaster = LinearTrendForecaster(horizon_steps=3)
    result = forecaster.fit_predict(growth_series, datetime.utcnow(), timedelta(days=1))
    assert result["slope"] == pytest.approx(10.0)
    assert len(result["predictions"]) == 3
    assert result["predictions"][0]["forecast_value"] == pytest.approx(60.0)
