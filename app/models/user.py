from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class User(BaseModel):
    """User entity representing an authenticated developer or admin."""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    role: Mapped[str] = mapped_column(String(32), default="developer", nullable=False)  # developer, admin, viewer
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    copilot_conversations: Mapped[List["CopilotConversation"]] = relationship(
        "CopilotConversation", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self, include_sensitive: bool = False):
        data = super().to_dict()
        if not include_sensitive:
            data.pop("password_hash", None)
        return data
