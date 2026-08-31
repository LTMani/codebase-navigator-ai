from typing import List, Optional
from sqlalchemy import desc, select
from app.extensions import db
from app.models.audit import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Data access repository for AuditLog events."""

    def __init__(self):
        super().__init__(AuditLog)

    def get_by_project(self, project_id: str, limit: int = 50) -> List[AuditLog]:
        """Fetch recent audit log entries for project."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.project_id == project_id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return list(db.session.execute(stmt).scalars().all())

    def get_by_user(self, user_id: str, limit: int = 50) -> List[AuditLog]:
        """Fetch recent audit log entries triggered by user."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return list(db.session.execute(stmt).scalars().all())
