import os
import re
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from app.models.source_file import SourceFile
from app.models.symbol import ClassDefinition, FunctionDefinition, Symbol
from app.repositories.file_repository import FileRepository
from app.repositories.symbol_repository import SymbolRepository
from app.schemas.search_schemas import SearchQuerySchema


class SearchService:
    """Unified search engine supporting symbol matching, full-text regex scanning, and scope filtering."""

    def __init__(
        self,
        file_repo: Optional[FileRepository] = None,
        symbol_repo: Optional[SymbolRepository] = None,
    ):
        self.file_repo = file_repo or FileRepository()
        self.symbol_repo = symbol_repo or SymbolRepository()

    def search(self, project_id: str, schema: SearchQuerySchema) -> Dict[str, Any]:
        """Perform multi-target scoped search across project entities."""
        query = schema.query.strip()
        q_lower = query.lower()

        files_results: List[Dict[str, Any]] = []
        symbols_results: List[Dict[str, Any]] = []
        functions_results: List[Dict[str, Any]] = []
        classes_results: List[Dict[str, Any]] = []
        content_matches: List[Dict[str, Any]] = []

        all_files = self.file_repo.get_all_by_project(project_id)

        # 1. Search Files
        if schema.search_type in ("all", "files"):
            for sf in all_files:
                if schema.language and sf.language.lower() != schema.language.lower():
                    continue
                if schema.layer and sf.layer_classification.lower() != schema.layer.lower():
                    continue

                if q_lower in sf.relative_path.lower() or q_lower in sf.filename.lower():
                    files_results.append({
                        "type": "file",
                        "id": sf.id,
                        "path": sf.relative_path,
                        "filename": sf.filename,
                        "language": sf.language,
                        "layer": sf.layer_classification,
                        "lines": sf.total_lines,
                        "complexity": sf.cyclomatic_complexity,
                        "purpose": sf.purpose_summary,
                    })

        # 2. Search Symbols & Functions & Classes
        if schema.search_type in ("all", "symbols", "functions", "classes"):
            for sf in all_files:
                if schema.language and sf.language.lower() != schema.language.lower():
                    continue
                if schema.layer and sf.layer_classification.lower() != schema.layer.lower():
                    continue

                # Functions
                if schema.search_type in ("all", "functions"):
                    for fn in sf.functions:
                        if q_lower in fn.name.lower() or (fn.docstring and q_lower in fn.docstring.lower()):
                            functions_results.append({
                                "type": "function",
                                "id": fn.id,
                                "name": fn.name,
                                "qualified_name": fn.qualified_name,
                                "file_path": sf.relative_path,
                                "start_line": fn.start_line,
                                "end_line": fn.end_line,
                                "parameters": fn.parameters,
                                "return_type": fn.return_type,
                                "is_async": fn.is_async,
                                "complexity": fn.cyclomatic_complexity,
                                "docstring": fn.docstring,
                            })

                # Classes
                if schema.search_type in ("all", "classes"):
                    for cls in sf.classes:
                        if q_lower in cls.name.lower() or (cls.docstring and q_lower in cls.docstring.lower()):
                            classes_results.append({
                                "type": "class",
                                "id": cls.id,
                                "name": cls.name,
                                "qualified_name": cls.qualified_name,
                                "file_path": sf.relative_path,
                                "start_line": cls.start_line,
                                "end_line": cls.end_line,
                                "base_classes": cls.base_classes,
                                "methods_count": cls.methods_count,
                                "docstring": cls.docstring,
                            })

                # Generic Symbols
                if schema.search_type in ("all", "symbols"):
                    for sym in sf.symbols:
                        if q_lower in sym.name.lower() or q_lower in sym.qualified_name.lower():
                            symbols_results.append({
                                "type": "symbol",
                                "id": sym.id,
                                "name": sym.name,
                                "kind": sym.kind,
                                "qualified_name": sym.qualified_name,
                                "file_path": sf.relative_path,
                                "start_line": sym.start_line,
                                "signature": sym.signature,
                            })

        # 3. Full-text Content Match
        if schema.search_type in ("all", "content") and len(query) >= 3:
            project_dir = None
            if all_files and hasattr(all_files[0], "project") and all_files[0].project:
                project_dir = getattr(all_files[0].project, "storage_path", None)

            if project_dir and os.path.exists(project_dir):
                for sf in all_files[:100]:
                    full_file_path = os.path.join(project_dir, sf.relative_path)
                    if not os.path.exists(full_file_path):
                        continue
                    try:
                        with open(full_file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, start=1):
                                if q_lower in line.lower():
                                    content_matches.append({
                                        "type": "content",
                                        "file_path": sf.relative_path,
                                        "line_number": idx,
                                        "snippet": line.strip()[:160],
                                        "language": sf.language,
                                    })
                                    if len(content_matches) >= 50:
                                        break
                    except Exception:
                        pass
                    if len(content_matches) >= 50:
                        break

        total_hits = (
            len(files_results)
            + len(functions_results)
            + len(classes_results)
            + len(symbols_results)
            + len(content_matches)
        )

        return {
            "query": query,
            "total_results": total_hits,
            "results": {
                "files": files_results[:schema.limit],
                "functions": functions_results[:schema.limit],
                "classes": classes_results[:schema.limit],
                "symbols": symbols_results[:schema.limit],
                "content": content_matches[:schema.limit],
            },
        }
