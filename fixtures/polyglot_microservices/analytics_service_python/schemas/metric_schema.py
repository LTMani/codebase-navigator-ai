from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class MetricDataPointCreate(BaseModel):
    metric_name: str = Field(..., min_length=2, max_length=128)
    entity_id: str = Field(..., min_length=1, max_length=64)
    value: float
    dimensions: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class MetricDataPointResponse(BaseModel):
    id: str
    metric_name: str
    entity_id: str
    value: float
    dimensions: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True

class TimeSeriesAggregate(BaseModel):
    bucket_start: datetime
    avg_value: float
    min_value: float
    max_value: float
    sample_count: int

class ForecastResult(BaseModel):
    metric_name: str
    entity_id: str
    predictions: List[Dict[str, Any]]
    trend_slope: float
    confidence_interval: float
    generated_at: datetime
