from typing import Any, Dict, List, Optional
from sqlalchemy import delete, func, or_, select
from app.extensions import db
from app.models.symbol import ClassDefinition, FunctionDefinition, ImportStatement, Symbol
from app.repositories.base_repository import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    """Data access repository for Symbol, FunctionDefinition, ClassDefinition, and ImportStatement."""

    def __init__(self):
        super().__init__(Symbol)

    def get_by_file(self, source_file_id: str) -> List[Symbol]:
        """Fetch all symbols in a source file."""
        stmt = select(Symbol).where(Symbol.source_file_id == source_file_id).order_by(Symbol.start_line)
        return list(db.session.execute(stmt).scalars().all())

    def get_functions_by_file(self, source_file_id: str) -> List[FunctionDefinition]:
        """Fetch function and method definitions in a source file."""
        stmt = select(FunctionDefinition).where(FunctionDefinition.source_file_id == source_file_id).order_by(FunctionDefinition.start_line)
        return list(db.session.execute(stmt).scalars().all())

    def get_classes_by_file(self, source_file_id: str) -> List[ClassDefinition]:
        """Fetch class definitions in a source file."""
        stmt = select(ClassDefinition).where(ClassDefinition.source_file_id == source_file_id).order_by(ClassDefinition.start_line)
        return list(db.session.execute(stmt).scalars().all())

    def get_imports_by_file(self, source_file_id: str) -> List[ImportStatement]:
        """Fetch import statements in a source file."""
        stmt = select(ImportStatement).where(ImportStatement.source_file_id == source_file_id).order_by(ImportStatement.line_number)
        return list(db.session.execute(stmt).scalars().all())

    def search_symbols(self, project_id: str, query: str, kind: Optional[str] = None, limit: int = 50) -> List[Symbol]:
        """Search symbol names and qualified names within a project."""
        pattern = f"%{query}%"
        stmt = select(Symbol).where(
            Symbol.project_id == project_id,
            or_(Symbol.name.ilike(pattern), Symbol.qualified_name.ilike(pattern)),
        )
        if kind:
            stmt = stmt.where(Symbol.kind == kind)
        stmt = stmt.order_by(Symbol.name).limit(limit)
        return list(db.session.execute(stmt).scalars().all())

    def delete_by_project(self, project_id: str):
        """Remove all symbols, functions, classes, and imports for project."""
        db.session.execute(delete(Symbol).where(Symbol.project_id == project_id))
        db.session.execute(delete(FunctionDefinition).where(FunctionDefinition.project_id == project_id))
        db.session.execute(delete(ClassDefinition).where(ClassDefinition.project_id == project_id))
        db.session.execute(delete(ImportStatement).where(ImportStatement.project_id == project_id))
        db.session.commit()
