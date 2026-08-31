import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class OnboardingPlan(BaseModel):
    """Generated curriculum for new developers to understand the project efficiently."""
    __tablename__ = "onboarding_plans"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    architecture_overview: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_read_time_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    reading_path_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    core_concepts_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    knowledge_check_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="onboarding_plans")
    steps: Mapped[List["OnboardingStep"]] = relationship("OnboardingStep", back_populates="plan", cascade="all, delete-orphan")

    @property
    def reading_path(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.reading_path_json)
        except Exception:
            return []

    @property
    def core_concepts(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.core_concepts_json)
        except Exception:
            return []

    @property
    def knowledge_check(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.knowledge_check_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["reading_path"] = self.reading_path
        data["core_concepts"] = self.core_concepts
        data["knowledge_check"] = self.knowledge_check
        return data


class OnboardingStep(BaseModel):
    """Individual step in the onboarding roadmap."""
    __tablename__ = "onboarding_steps"

    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("onboarding_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="overview", nullable=False)  # overview, architecture, entry_point, core_service, data_flow, deep_dive
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    key_takeaways_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    plan: Mapped["OnboardingPlan"] = relationship("OnboardingPlan", back_populates="steps")
