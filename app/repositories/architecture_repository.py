from typing import List, Optional
from sqlalchemy import delete, select
from app.extensions import db
from app.models.architecture import ArchitectureFinding, ArchitectureViolation
from app.repositories.base_repository import BaseRepository


class ArchitectureRepository(BaseRepository[ArchitectureFinding]):
    """Data access repository for Architecture findings and violation reports."""

    def __init__(self):
        super().__init__(ArchitectureFinding)

    def get_by_project(self, project_id: str) -> List[ArchitectureFinding]:
        """Fetch all architecture findings for project."""
        stmt = select(ArchitectureFinding).where(ArchitectureFinding.project_id == project_id).order_by(ArchitectureFinding.layer_name)
        return list(db.session.execute(stmt).scalars().all())

    def get_violations_by_project(self, project_id: str) -> List[ArchitectureViolation]:
        """Fetch all architectural boundary violations for project."""
        stmt = select(ArchitectureViolation).where(ArchitectureViolation.project_id == project_id).order_by(ArchitectureViolation.severity)
        return list(db.session.execute(stmt).scalars().all())

    def create_violations_batch(self, violations: List[ArchitectureViolation]) -> List[ArchitectureViolation]:
        """Bulk insert violations."""
        if not violations:
            return []
        db.session.add_all(violations)
        db.session.commit()
        return violations

    def delete_by_project(self, project_id: str):
        """Remove architecture findings and violations for project."""
        db.session.execute(delete(ArchitectureFinding).where(ArchitectureFinding.project_id == project_id))
        db.session.execute(delete(ArchitectureViolation).where(ArchitectureViolation.project_id == project_id))
        db.session.commit()
