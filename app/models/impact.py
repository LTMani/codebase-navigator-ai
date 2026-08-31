import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class ImpactAnalysisResult(BaseModel):
    """Change blast radius computation results when a module or file is modified."""
    __tablename__ = "impact_analysis_results"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    target_file_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    target_symbol_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    direct_dependents_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    indirect_dependents_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blast_radius_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 - 100.0
    risk_level: Mapped[str] = mapped_column(String(32), default="low", nullable=False)  # low, medium, high, critical

    direct_dependents_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    indirect_dependents_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    affected_routes_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    affected_tests_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    public_interfaces_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    @property
    def direct_dependents(self) -> List[str]:
        try:
            return json.loads(self.direct_dependents_json)
        except Exception:
            return []

    @property
    def indirect_dependents(self) -> List[str]:
        try:
            return json.loads(self.indirect_dependents_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["direct_dependents"] = self.direct_dependents
        data["indirect_dependents"] = self.indirect_dependents
        return data
