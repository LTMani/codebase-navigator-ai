from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class MetricDataPoint(Base):
    __tablename__ = "metric_data_points"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(128), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False, index=True)
    value = Column(Float, nullable=False)
    dimensions = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
