import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class SourceFolder(BaseModel):
    """Represents a directory node within the project tree structure."""
    __tablename__ = "source_folders"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("source_folders.id", ondelete="CASCADE"), nullable=True)
    relative_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="source_folders")
    parent: Mapped[Optional["SourceFolder"]] = relationship("SourceFolder", remote_side="SourceFolder.id", backref="children")


class SourceFile(BaseModel):
    """Represents a single analyzed source code file in the project."""
    __tablename__ = "source_files"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    folder_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("source_folders.id", ondelete="SET NULL"), nullable=True)
    
    # Path & Identity
    relative_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    extension: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    language: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False, index=True)
    file_hash: Mapped[str] = mapped_column(String(64), default="", nullable=False)

    # Size & Metrics
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    code_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blank_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Complexity & Quality Indicators
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cognitive_complexity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    maintainability_index: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    documentation_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Architecture & Role
    layer_classification: Mapped[str] = mapped_column(String(64), default="unclassified", nullable=False)  # presentation, api, service, domain, repository, infrastructure, utility
    layer_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_entry_point: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_test_file: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_config_file: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Analysis State
    ast_parsed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parser_messages_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    purpose_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="source_files")
    symbols: Mapped[List["Symbol"]] = relationship("Symbol", back_populates="source_file", cascade="all, delete-orphan")
    functions: Mapped[List["FunctionDefinition"]] = relationship("FunctionDefinition", back_populates="source_file", cascade="all, delete-orphan")
    classes: Mapped[List["ClassDefinition"]] = relationship("ClassDefinition", back_populates="source_file", cascade="all, delete-orphan")
    imports: Mapped[List["ImportStatement"]] = relationship("ImportStatement", back_populates="source_file", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        try:
            data["parser_messages"] = json.loads(self.parser_messages_json)
        except Exception:
            data["parser_messages"] = []
        return data
