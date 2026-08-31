from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime, timedelta
import uuid
from fixtures.polyglot_microservices.analytics_service_python.schemas.metric_schema import (
    MetricDataPointCreate,
    MetricDataPointResponse,
    ForecastResult,
)
from fixtures.polyglot_microservices.analytics_service_python.services.timeseries_service import TimeSeriesService
from fixtures.polyglot_microservices.analytics_service_python.services.ml_forecaster import LinearTrendForecaster

router = APIRouter(prefix="/metrics", tags=["Metrics"])

# In-memory storage mock
_metrics_store: List[dict] = []

@router.post("", response_model=MetricDataPointResponse, status_code=status.HTTP_201_CREATED)
async def record_metric(payload: MetricDataPointCreate):
    record = {
        "id": str(uuid.uuid4()),
        "metric_name": payload.metric_name,
        "entity_id": payload.entity_id,
        "value": payload.value,
        "dimensions": payload.dimensions or {},
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    _metrics_store.append(record)
    return record

@router.get("/forecast/{entity_id}", response_model=ForecastResult)
async def generate_entity_forecast(entity_id: str, metric_name: str = "cpu_usage"):
    values = [m["value"] for m in _metrics_store if m["entity_id"] == entity_id and m["metric_name"] == metric_name]
    if len(values) < 3:
        values = [45.0, 48.0, 52.0, 50.0, 56.0, 61.0, 64.0]

    forecaster = LinearTrendForecaster(horizon_steps=10)
    result = forecaster.fit_predict(values, datetime.utcnow() - timedelta(days=7), timedelta(days=1))

    return ForecastResult(
        metric_name=metric_name,
        entity_id=entity_id,
        predictions=result["predictions"],
        trend_slope=result["slope"],
        confidence_interval=0.95,
        generated_at=datetime.utcnow()
    )
