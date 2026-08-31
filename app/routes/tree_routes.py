import os
from flask import Blueprint, jsonify, request
from app.errors.exceptions import NotFoundError
from app.middleware.auth_middleware import login_required
from app.repositories.file_repository import FileRepository
from app.repositories.project_repository import ProjectRepository

tree_bp = Blueprint("tree", __name__, url_prefix="/api/projects/<project_id>/tree")
file_repo = FileRepository()
project_repo = ProjectRepository()


@tree_bp.route("", methods=["GET"])
@login_required
def get_project_tree(project_id: str):
    """Retrieve full hierarchical directory and file tree for project."""
    project = project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundError("Project not found.")

    source_files = file_repo.get_all_by_project(project_id)
    folders = file_repo.get_folders_by_project(project_id)

    # Build nested tree structure
    root = {
        "name": project.name,
        "path": "",
        "type": "directory",
        "children": {},
    }

    for sf in source_files:
        parts = sf.relative_path.split("/")
        curr = root
        for i, part in enumerate(parts[:-1]):
            subpath = "/".join(parts[: i + 1])
            if part not in curr["children"]:
                curr["children"][part] = {
                    "name": part,
                    "path": subpath,
                    "type": "directory",
                    "children": {},
                }
            curr = curr["children"][part]

        file_name = parts[-1]
        curr["children"][file_name] = {
            "id": sf.id,
            "name": file_name,
            "path": sf.relative_path,
            "type": "file",
            "extension": sf.extension,
            "language": sf.language,
            "lines": sf.total_lines,
            "code_lines": sf.code_lines,
            "size_bytes": sf.size_bytes,
            "layer": sf.layer_classification,
            "is_entry_point": sf.is_entry_point,
            "complexity": sf.cyclomatic_complexity,
            "maintainability": sf.maintainability_index,
        }

    def convert_dict_to_list(node: dict) -> dict:
        if "children" in node and isinstance(node["children"], dict):
            children_list = [convert_dict_to_list(child) for child in node["children"].values()]
            # Sort directories first, then files
            children_list.sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"].lower()))
            node["children"] = children_list
        return node

    tree_structure = convert_dict_to_list(root)

    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "tree": tree_structure,
            "total_files": len(source_files),
            "total_folders": len(folders),
        },
    }), 200


@tree_bp.route("/file", methods=["GET"])
@login_required
def get_file_content(project_id: str):
    """Retrieve raw file source code and metadata by relative path."""
    rel_path = request.args.get("path")
    if not rel_path:
        raise NotFoundError("Path parameter is required.")

    project = project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundError("Project not found.")

    source_file = file_repo.get_by_path(project_id, rel_path)
    if not source_file:
        raise NotFoundError(f"File '{rel_path}' not found in project index.")

    full_path = os.path.join(project.storage_path, rel_path)
    content = ""
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = "/* Failed to read file content */"

    return jsonify({
        "success": True,
        "data": {
            "file": source_file.to_dict(),
            "content": content,
        },
    }), 200
