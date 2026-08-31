from typing import List, Optional
from sqlalchemy import delete, desc, select
from app.extensions import db
from app.models.onboarding import OnboardingPlan, OnboardingStep
from app.repositories.base_repository import BaseRepository


class OnboardingRepository(BaseRepository[OnboardingPlan]):
    """Data access repository for OnboardingPlan and OnboardingStep."""

    def __init__(self):
        super().__init__(OnboardingPlan)

    def get_by_project(self, project_id: str) -> Optional[OnboardingPlan]:
        """Fetch latest onboarding roadmap for project."""
        stmt = (
            select(OnboardingPlan)
            .where(OnboardingPlan.project_id == project_id)
            .order_by(desc(OnboardingPlan.created_at))
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_steps_by_plan(self, plan_id: str) -> List[OnboardingStep]:
        """Fetch ordered steps in an onboarding plan."""
        stmt = select(OnboardingStep).where(OnboardingStep.plan_id == plan_id).order_by(OnboardingStep.step_order)
        return list(db.session.execute(stmt).scalars().all())

    def create_steps_batch(self, steps: List[OnboardingStep]) -> List[OnboardingStep]:
        """Bulk insert onboarding steps."""
        if not steps:
            return []
        db.session.add_all(steps)
        db.session.commit()
        return steps

    def delete_by_project(self, project_id: str):
        """Remove onboarding plans and steps for project."""
        stmt_plan_ids = select(OnboardingPlan.id).where(OnboardingPlan.project_id == project_id)
        plan_ids = list(db.session.execute(stmt_plan_ids).scalars().all())
        if plan_ids:
            db.session.execute(delete(OnboardingStep).where(OnboardingStep.plan_id.in_(plan_ids)))
        db.session.execute(delete(OnboardingPlan).where(OnboardingPlan.project_id == project_id))
        db.session.commit()
