from typing import Any, Dict, List, Optional
from sqlalchemy import delete, func, select
from app.extensions import db
from app.models.source_file import SourceFile, SourceFolder
from app.repositories.base_repository import BaseRepository


class FileRepository(BaseRepository[SourceFile]):
    """Data access repository for SourceFile and SourceFolder entities."""

    def __init__(self):
        super().__init__(SourceFile)

    def get_by_path(self, project_id: str, relative_path: str) -> Optional[SourceFile]:
        """Find source file by its relative path within project."""
        stmt = select(SourceFile).where(
            SourceFile.project_id == project_id,
            SourceFile.relative_path == relative_path,
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_all_by_project(self, project_id: str) -> List[SourceFile]:
        """Get all source files for a given project ordered by path."""
        stmt = select(SourceFile).where(SourceFile.project_id == project_id).order_by(SourceFile.relative_path)
        return list(db.session.execute(stmt).scalars().all())

    def get_entry_points(self, project_id: str) -> List[SourceFile]:
        """Get source files flagged as potential application entry points."""
        stmt = select(SourceFile).where(
            SourceFile.project_id == project_id,
            SourceFile.is_entry_point == True,
        ).order_by(SourceFile.relative_path)
        return list(db.session.execute(stmt).scalars().all())

    def get_folders_by_project(self, project_id: str) -> List[SourceFolder]:
        """Get all directory tree folder nodes for project."""
        stmt = select(SourceFolder).where(SourceFolder.project_id == project_id).order_by(SourceFolder.depth, SourceFolder.relative_path)
        return list(db.session.execute(stmt).scalars().all())

    def get_folder_by_path(self, project_id: str, relative_path: str) -> Optional[SourceFolder]:
        """Lookup folder node by relative path."""
        stmt = select(SourceFolder).where(
            SourceFolder.project_id == project_id,
            SourceFolder.relative_path == relative_path,
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def create_folders_batch(self, folders: List[SourceFolder]) -> List[SourceFolder]:
        """Bulk insert folder nodes."""
        if not folders:
            return []
        db.session.add_all(folders)
        db.session.commit()
        return folders

    def delete_by_project(self, project_id: str):
        """Remove all files and folders belonging to project."""
        db.session.execute(delete(SourceFile).where(SourceFile.project_id == project_id))
        db.session.execute(delete(SourceFolder).where(SourceFolder.project_id == project_id))
        db.session.commit()

    def get_language_breakdown(self, project_id: str) -> List[Dict[str, Any]]:
        """Calculate lines of code and file counts grouped by programming language."""
        stmt = (
            select(
                SourceFile.language,
                func.count(SourceFile.id).label("file_count"),
                func.sum(SourceFile.total_lines).label("total_lines"),
                func.sum(SourceFile.code_lines).label("code_lines"),
                func.sum(SourceFile.comment_lines).label("comment_lines"),
                func.sum(SourceFile.blank_lines).label("blank_lines"),
                func.sum(SourceFile.size_bytes).label("total_bytes"),
            )
            .where(SourceFile.project_id == project_id)
            .group_by(SourceFile.language)
            .order_by(func.sum(SourceFile.total_lines).desc())
        )
        rows = db.session.execute(stmt).all()
        return [
            {
                "language": row.language,
                "file_count": row.file_count,
                "total_lines": row.total_lines or 0,
                "code_lines": row.code_lines or 0,
                "comment_lines": row.comment_lines or 0,
                "blank_lines": row.blank_lines or 0,
                "total_bytes": row.total_bytes or 0,
            }
            for row in rows
        ]
