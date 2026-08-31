from typing import List, Optional
from sqlalchemy import delete, desc, select
from app.extensions import db
from app.models.health import CircularDependencyCluster, HealthMetric
from app.repositories.base_repository import BaseRepository


class HealthRepository(BaseRepository[HealthMetric]):
    """Data access repository for HealthMetric and CircularDependencyCluster."""

    def __init__(self):
        super().__init__(HealthMetric)

    def get_latest_by_project(self, project_id: str) -> Optional[HealthMetric]:
        """Fetch most recent health metrics for project."""
        stmt = (
            select(HealthMetric)
            .where(HealthMetric.project_id == project_id)
            .order_by(desc(HealthMetric.created_at))
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_circular_clusters(self, project_id: str) -> List[CircularDependencyCluster]:
        """Fetch circular dependency clusters for project."""
        stmt = (
            select(CircularDependencyCluster)
            .where(CircularDependencyCluster.project_id == project_id)
            .order_by(CircularDependencyCluster.cycle_length)
        )
        return list(db.session.execute(stmt).scalars().all())

    def create_clusters_batch(self, clusters: List[CircularDependencyCluster]) -> List[CircularDependencyCluster]:
        """Bulk insert circular clusters."""
        if not clusters:
            return []
        db.session.add_all(clusters)
        db.session.commit()
        return clusters

    def delete_by_project(self, project_id: str):
        """Remove health metrics and circular dependency clusters for project."""
        db.session.execute(delete(HealthMetric).where(HealthMetric.project_id == project_id))
        db.session.execute(delete(CircularDependencyCluster).where(CircularDependencyCluster.project_id == project_id))
        db.session.commit()
