import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Project(BaseModel):
    """Represents a registered software repository or codebase imported for intelligence analysis."""
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    repository_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    
    # Ownership
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, default="default_owner")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Filesystem & Storage
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    archive_filename: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # Analysis State
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, scanning, parsing, analyzing, ready, failed
    status_message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    last_analyzed_at: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Summary Statistics
    file_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    folder_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    code_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blank_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # JSON metadata blobs (stored as text for cross-db compatibility)
    languages_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    frameworks_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    entry_points_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    source_folders: Mapped[List["SourceFolder"]] = relationship("SourceFolder", back_populates="project", cascade="all, delete-orphan")
    source_files: Mapped[List["SourceFile"]] = relationship("SourceFile", back_populates="project", cascade="all, delete-orphan")
    analysis_runs: Mapped[List["AnalysisRun"]] = relationship("AnalysisRun", back_populates="project", cascade="all, delete-orphan")
    dependencies: Mapped[List["DependencyEdge"]] = relationship("DependencyEdge", back_populates="project", cascade="all, delete-orphan")
    architecture_findings: Mapped[List["ArchitectureFinding"]] = relationship("ArchitectureFinding", back_populates="project", cascade="all, delete-orphan")
    code_flows: Mapped[List["CodeFlow"]] = relationship("CodeFlow", back_populates="project", cascade="all, delete-orphan")
    health_metrics: Mapped[List["HealthMetric"]] = relationship("HealthMetric", back_populates="project", cascade="all, delete-orphan")
    onboarding_plans: Mapped[List["OnboardingPlan"]] = relationship("OnboardingPlan", back_populates="project", cascade="all, delete-orphan")
    copilot_conversations: Mapped[List["CopilotConversation"]] = relationship("CopilotConversation", back_populates="project", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "user_id" in kwargs and "owner_id" not in kwargs:
            kwargs["owner_id"] = kwargs.pop("user_id")
        if "owner_id" not in kwargs:
            kwargs["owner_id"] = "default_owner"
        super().__init__(**kwargs)

    @property
    def folders(self):
        return self.source_folders

    @property
    def files(self):
        return self.source_files

    @property
    def languages(self) -> Dict[str, Any]:
        try:
            return json.loads(self.languages_json)
        except Exception:
            return {}

    @languages.setter
    def languages(self, value: Dict[str, Any]):
        self.languages_json = json.dumps(value or {})

    @property
    def frameworks(self) -> List[str]:
        try:
            return json.loads(self.frameworks_json)
        except Exception:
            return []

    @frameworks.setter
    def frameworks(self, value: List[str]):
        self.frameworks_json = json.dumps(value or [])

    @property
    def entry_points(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.entry_points_json)
        except Exception:
            return []

    @entry_points.setter
    def entry_points(self, value: List[Dict[str, Any]]):
        self.entry_points_json = json.dumps(value or [])

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["languages"] = self.languages
        data["frameworks"] = self.frameworks
        data["entry_points"] = self.entry_points
        return data


class AnalysisRun(BaseModel):
    """Records historical executions of the codebase analysis pipeline on a project."""
    __tablename__ = "analysis_runs"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)  # manual, upload, scheduled, api
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)  # running, completed, failed
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    files_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    symbols_extracted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dependencies_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="analysis_runs")
