import json
from typing import Any, Dict, Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class AuditLog(BaseModel):
    """Structured audit log recording security and administrative actions."""
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # project_create, project_delete, analyze_start, login, export
    resource_type: Mapped[str] = mapped_column(String(64), default="project", nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    details_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
