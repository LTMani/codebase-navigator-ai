import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class CodeFlow(BaseModel):
    """Synthesized execution path through application layers from entry point to database/output."""
    __tablename__ = "code_flows"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    flow_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    flow_type: Mapped[str] = mapped_column(String(64), default="request_response", nullable=False)  # request_response, worker, lifecycle, cli_command
    entry_point: Mapped[str] = mapped_column(String(512), nullable=False)
    endpoint_method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # GET, POST, PUT, DELETE
    endpoint_path: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.75, nullable=False)
    step_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    steps_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="code_flows")
    flow_nodes: Mapped[List["FlowNode"]] = relationship("FlowNode", back_populates="code_flow", cascade="all, delete-orphan")

    @property
    def steps(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.steps_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["steps"] = self.steps
        return data


class FlowNode(BaseModel):
    """A single discrete step or hop in an execution flow graph."""
    __tablename__ = "flow_nodes"

    code_flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("code_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    
    step_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    layer_name: Mapped[str] = mapped_column(String(64), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    symbol_name: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(256), nullable=False)
    certainty: Mapped[str] = mapped_column(String(32), default="confirmed", nullable=False)  # confirmed, inferred, heuristic

    code_flow: Mapped["CodeFlow"] = relationship("CodeFlow", back_populates="flow_nodes")
