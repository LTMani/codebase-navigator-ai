from typing import Any, Dict, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class DependencyEdge(BaseModel):
    """Directed dependency relationship between two source files or external modules."""
    __tablename__ = "dependency_edges"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True)
    target_file_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True, index=True)

    source_path: Mapped[str] = mapped_column(String(512), nullable=False)
    target_path: Mapped[str] = mapped_column(String(512), nullable=False)
    target_module: Mapped[str] = mapped_column(String(256), nullable=False)
    
    dependency_type: Mapped[str] = mapped_column(String(32), default="import", nullable=False)  # import, call, inheritance, type_reference
    is_external: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_circular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # reference frequency

    project: Mapped["Project"] = relationship("Project", back_populates="dependencies")
    source_file: Mapped["SourceFile"] = relationship("SourceFile", foreign_keys=[source_file_id])
    target_file: Mapped[Optional["SourceFile"]] = relationship("SourceFile", foreign_keys=[target_file_id])
