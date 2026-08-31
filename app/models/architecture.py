import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class ArchitectureFinding(BaseModel):
    """Architectural layer classifications and structural role heuristics discovered in project."""
    __tablename__ = "architecture_findings"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    layer_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # presentation, api, service, domain, repository, infrastructure, utility
    component_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    
    patterns_detected_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    associated_files_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    inbound_dependencies_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    outbound_dependencies_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="architecture_findings")

    @property
    def patterns_detected(self) -> List[str]:
        try:
            return json.loads(self.patterns_detected_json)
        except Exception:
            return []

    @property
    def associated_files(self) -> List[str]:
        try:
            return json.loads(self.associated_files_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["patterns_detected"] = self.patterns_detected
        data["associated_files"] = self.associated_files
        return data


class ArchitectureViolation(BaseModel):
    """Architectural boundary violations (e.g. presentation directly invoking repository)."""
    __tablename__ = "architecture_violations"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_layer: Mapped[str] = mapped_column(String(64), nullable=False)
    target_layer: Mapped[str] = mapped_column(String(64), nullable=False)
    source_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    target_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="warning", nullable=False)  # info, warning, error
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    refactoring_advice: Mapped[str] = mapped_column(Text, nullable=False)
