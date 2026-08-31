from pathlib import Path
from flask import Blueprint, current_app, g, jsonify, request
from app.errors.exceptions import NotFoundError, ValidationError
from app.middleware.auth_middleware import login_required
from app.schemas.project_schemas import ProjectCreateSchema, ProjectUpdateSchema
from app.services.audit_service import AuditService
from app.services.project_service import ProjectService

project_bp = Blueprint("projects", __name__, url_prefix="/api/projects")
project_service = ProjectService()
audit_service = AuditService()


@project_bp.route("", methods=["GET"])
@login_required
def list_projects():
    """List all projects belonging to the current user."""
    projects = project_service.list_user_projects(g.current_user.id)
    return jsonify({
        "success": True,
        "data": {
            "projects": projects,
            "total": len(projects),
        },
    }), 200


@project_bp.route("", methods=["POST"])
@login_required
def create_project():
    """Create and register a new project."""
    schema = ProjectCreateSchema.from_dict(request.get_json() or {})
    storage_dir = Path(current_app.config["STORAGE_BASE_DIR"])

    project = project_service.create_project(schema, owner_id=g.current_user.id, storage_base_dir=storage_dir)
    audit_service.log(
        action="project_created",
        user_id=g.current_user.id,
        project_id=project.id,
        resource_id=project.id,
        details={"name": project.name, "slug": project.slug},
    )

    return jsonify({
        "success": True,
        "message": "Project registered successfully.",
        "data": {
            "project": project.to_dict(),
        },
    }), 201


@project_bp.route("/<project_id>", methods=["GET"])
@login_required
def get_project(project_id: str):
    """Retrieve details and status for a specific project."""
    summary = project_service.get_project_summary(project_id)
    return jsonify({
        "success": True,
        "data": {
            "project": summary,
        },
    }), 200


@project_bp.route("/<project_id>/upload", methods=["POST"])
@login_required
def upload_project_archive(project_id: str):
    """Upload project archive file (.zip, .tar.gz), unpack safely, and index files."""
    if "file" not in request.files:
        raise ValidationError("No archive file provided in multipart request under 'file' key.")

    file_obj = request.files["file"]
    if not file_obj.filename:
        raise ValidationError("Uploaded file has no filename.")

    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    extract_dir = Path(current_app.config["EXTRACT_DIR"])

    upload_res = project_service.upload_and_extract_archive(
        project_id=project_id,
        file_storage=file_obj,
        upload_dir=upload_dir,
        extract_base_dir=extract_dir,
    )

    # Immediately trigger scanning and AST parsing
    scan_res = project_service.scan_and_index_project(project_id)

    audit_service.log(
        action="project_uploaded_and_scanned",
        user_id=g.current_user.id,
        project_id=project_id,
        resource_id=project_id,
        details={"files_scanned": scan_res.get("file_count")},
    )

    return jsonify({
        "success": True,
        "message": "Archive uploaded, safely extracted, and parsed successfully.",
        "data": {
            "upload": upload_res,
            "scan": scan_res,
        },
    }), 200


@project_bp.route("/<project_id>/scan", methods=["POST"])
@login_required
def scan_project(project_id: str):
    """Trigger on-demand re-scan and AST re-parse of project files."""
    scan_res = project_service.scan_and_index_project(project_id)
    return jsonify({
        "success": True,
        "message": "Project scanned and AST symbols indexed.",
        "data": scan_res,
    }), 200


@project_bp.route("/<project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id: str):
    """Delete project and remove files from storage."""
    project_service.delete_project(project_id)
    audit_service.log(
        action="project_deleted",
        user_id=g.current_user.id,
        project_id=project_id,
        resource_id=project_id,
    )
    return jsonify({
        "success": True,
        "message": "Project deleted successfully.",
    }), 200
