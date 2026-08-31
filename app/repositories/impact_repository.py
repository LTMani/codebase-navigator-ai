from typing import List, Optional
from sqlalchemy import delete, select
from app.extensions import db
from app.models.impact import ImpactAnalysisResult
from app.repositories.base_repository import BaseRepository


class ImpactRepository(BaseRepository[ImpactAnalysisResult]):
    """Data access repository for ImpactAnalysisResult cache."""

    def __init__(self):
        super().__init__(ImpactAnalysisResult)

    def get_by_target(self, project_id: str, target_file_path: str, target_symbol_name: Optional[str] = None) -> Optional[ImpactAnalysisResult]:
        """Fetch cached blast radius result for file or symbol."""
        stmt = select(ImpactAnalysisResult).where(
            ImpactAnalysisResult.project_id == project_id,
            ImpactAnalysisResult.target_file_path == target_file_path,
        )
        if target_symbol_name:
            stmt = stmt.where(ImpactAnalysisResult.target_symbol_name == target_symbol_name)
        else:
            stmt = stmt.where(ImpactAnalysisResult.target_symbol_name.is_(None))
        return db.session.execute(stmt).scalar_one_or_none()

    def get_high_risk_modules(self, project_id: str, limit: int = 20) -> List[ImpactAnalysisResult]:
        """Fetch project modules with highest blast radius score."""
        stmt = (
            select(ImpactAnalysisResult)
            .where(ImpactAnalysisResult.project_id == project_id)
            .order_by(ImpactAnalysisResult.blast_radius_score.desc())
            .limit(limit)
        )
        return list(db.session.execute(stmt).scalars().all())

    def delete_by_project(self, project_id: str):
        """Remove impact analysis results for project."""
        db.session.execute(delete(ImpactAnalysisResult).where(ImpactAnalysisResult.project_id == project_id))
        db.session.commit()
