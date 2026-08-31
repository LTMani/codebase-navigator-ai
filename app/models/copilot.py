import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class CopilotConversation(BaseModel):
    """Chat conversation thread with the Codebase Copilot."""
    __tablename__ = "copilot_conversations"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(256), default="Codebase Conversation", nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="copilot_conversations")
    user: Mapped["User"] = relationship("User", back_populates="copilot_conversations")
    messages: Mapped[List["CopilotMessage"]] = relationship("CopilotMessage", back_populates="conversation", cascade="all, delete-orphan")


class CopilotMessage(BaseModel):
    """Individual user prompt or assistant response in a Copilot conversation."""
    __tablename__ = "copilot_messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("copilot_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # explain_arch, trace_flow, change_impact, find_symbol, general_qa
    
    citations_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    grounded_symbols_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    provider_used: Mapped[str] = mapped_column(String(32), default="deterministic", nullable=False)
    is_grounded: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    conversation: Mapped["CopilotMessage"] = relationship("CopilotConversation", back_populates="messages")

    @property
    def citations(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.citations_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["citations"] = self.citations
        return data
