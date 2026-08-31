from typing import List, Optional
from sqlalchemy import delete, select
from app.extensions import db
from app.models.dependency import DependencyEdge
from app.repositories.base_repository import BaseRepository


class DependencyRepository(BaseRepository[DependencyEdge]):
    """Data access repository for DependencyEdge records."""

    def __init__(self):
        super().__init__(DependencyEdge)

    def get_by_project(self, project_id: str) -> List[DependencyEdge]:
        """Fetch all dependency graph edges for project."""
        stmt = select(DependencyEdge).where(DependencyEdge.project_id == project_id)
        return list(db.session.execute(stmt).scalars().all())

    def get_file_dependencies(self, source_file_id: str) -> List[DependencyEdge]:
        """Fetch outbound dependencies for a file (what it imports/calls)."""
        stmt = select(DependencyEdge).where(DependencyEdge.source_file_id == source_file_id)
        return list(db.session.execute(stmt).scalars().all())

    def get_file_dependents(self, target_file_id: str) -> List[DependencyEdge]:
        """Fetch inbound dependents for a file (who imports/calls it)."""
        stmt = select(DependencyEdge).where(DependencyEdge.target_file_id == target_file_id)
        return list(db.session.execute(stmt).scalars().all())

    def get_circular_edges(self, project_id: str) -> List[DependencyEdge]:
        """Fetch dependency edges that participate in circular loops."""
        stmt = select(DependencyEdge).where(
            DependencyEdge.project_id == project_id,
            DependencyEdge.is_circular == True,
        )
        return list(db.session.execute(stmt).scalars().all())

    def delete_by_project(self, project_id: str):
        """Remove all dependency edges for project."""
        db.session.execute(delete(DependencyEdge).where(DependencyEdge.project_id == project_id))
        db.session.commit()
