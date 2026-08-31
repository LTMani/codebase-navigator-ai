from typing import List, Optional
from sqlalchemy import desc, select
from app.extensions import db
from app.models.project import AnalysisRun, Project
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Data access repository for Project records."""

    def __init__(self):
        super().__init__(Project)

    def get_by_slug(self, slug: str) -> Optional[Project]:
        """Lookup project by unique url slug."""
        stmt = select(Project).where(Project.slug == slug)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_owner(self, owner_id: str, limit: int = 100, offset: int = 0) -> List[Project]:
        """Get projects owned by specific user ordered by last updated."""
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(desc(Project.updated_at))
            .limit(limit)
            .offset(offset)
        )
        return list(db.session.execute(stmt).scalars().all())

    def get_public_projects(self, limit: int = 50, offset: int = 0) -> List[Project]:
        """Get public projects for exploratory viewing."""
        stmt = (
            select(Project)
            .where(Project.is_public == True)
            .order_by(desc(Project.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(db.session.execute(stmt).scalars().all())

    def slug_exists(self, slug: str, exclude_project_id: Optional[str] = None) -> bool:
        """Check if slug already exists."""
        stmt = select(Project.id).where(Project.slug == slug)
        if exclude_project_id:
            stmt = stmt.where(Project.id != exclude_project_id)
        return db.session.execute(stmt).first() is not None

    def create_analysis_run(self, run: AnalysisRun) -> AnalysisRun:
        """Store new analysis run record."""
        db.session.add(run)
        db.session.commit()
        db.session.refresh(run)
        return run

    def get_latest_analysis_run(self, project_id: str) -> Optional[AnalysisRun]:
        """Retrieve most recent analysis execution for project."""
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.project_id == project_id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_analysis_history(self, project_id: str, limit: int = 20) -> List[AnalysisRun]:
        """Get chronological history of analysis runs for project."""
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.project_id == project_id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(limit)
        )
        return list(db.session.execute(stmt).scalars().all())
