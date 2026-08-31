import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class HealthMetric(BaseModel):
    """Overall codebase health, maintainability index, and technical debt score."""
    __tablename__ = "health_metrics"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    overall_health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)  # 0 - 100
    maintainability_grade: Mapped[str] = mapped_column(String(8), default="A", nullable=False)  # A, B, C, D, F
    average_cyclomatic_complexity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    average_maintainability_index: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    documentation_coverage_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    circular_dependency_cycles_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    large_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    complex_functions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_technical_debt_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    hotspots_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    recommendations_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    debt_breakdown_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="health_metrics")

    @property
    def hotspots(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.hotspots_json)
        except Exception:
            return []

    @property
    def recommendations(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.recommendations_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["hotspots"] = self.hotspots
        data["recommendations"] = self.recommendations
        return data


class CircularDependencyCluster(BaseModel):
    """A group of mutually dependent modules forming a cycle in the dependency graph."""
    __tablename__ = "circular_dependency_clusters"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    cycle_length: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="warning", nullable=False)
    
    files_in_cycle_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    cycle_path_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    refactoring_suggestion: Mapped[str] = mapped_column(Text, nullable=False)

    @property
    def files_in_cycle(self) -> List[str]:
        try:
            return json.loads(self.files_in_cycle_json)
        except Exception:
            return []

    @property
    def cycle_path(self) -> List[str]:
        try:
            return json.loads(self.cycle_path_json)
        except Exception:
            return []
