import os
from flask import Blueprint, jsonify, request
from app.errors.exceptions import NotFoundError
from app.middleware.auth_middleware import login_required
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.symbol_repository import SymbolRepository

file_intelligence_bp = Blueprint("file_intelligence", __name__, url_prefix="/api/projects/<project_id>/files")
file_repo = FileRepository()
symbol_repo = SymbolRepository()
dep_repo = DependencyRepository()
project_repo = ProjectRepository()


@file_intelligence_bp.route("/intelligence", methods=["GET"])
@login_required
def get_file_intelligence(project_id: str):
    """Retrieve detailed AST intelligence for a file: symbols, functions, classes, imports, dependents."""
    rel_path = request.args.get("path")
    if not rel_path:
        raise NotFoundError("Query parameter 'path' is required.")

    project = project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundError("Project not found.")

    source_file = file_repo.get_by_path(project_id, rel_path)
    if not source_file:
        raise NotFoundError(f"Source file '{rel_path}' not found.")

    # Fetch symbols, functions, classes, imports
    symbols = symbol_repo.get_by_file(source_file.id)
    functions = symbol_repo.get_functions_by_file(source_file.id)
    classes = symbol_repo.get_classes_by_file(source_file.id)
    imports = symbol_repo.get_imports_by_file(source_file.id)

    # Dependencies & Dependents
    dependencies = dep_repo.get_file_dependencies(source_file.id)
    dependents = dep_repo.get_file_dependents(source_file.id)

    # Load content
    full_path = os.path.join(project.storage_path, rel_path)
    content = ""
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            pass

    return jsonify({
        "success": True,
        "data": {
            "file": source_file.to_dict(),
            "content": content,
            "symbols": [s.to_dict() for s in symbols],
            "functions": [fn.to_dict() for fn in functions],
            "classes": [c.to_dict() for c in classes],
            "imports": [i.to_dict() for i in imports],
            "dependencies": [d.to_dict() for d in dependencies],
            "dependents": [d.to_dict() for d in dependents],
        },
    }), 200
