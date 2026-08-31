from flask import Blueprint, jsonify
from app.middleware.auth_middleware import login_required
from app.repositories.project_repository import ProjectRepository

history_bp = Blueprint("history", __name__, url_prefix="/api/projects/<project_id>/history")
project_repo = ProjectRepository()


@history_bp.route("", methods=["GET"])
@login_required
def get_analysis_history(project_id: str):
    """Retrieve chronological history of analysis runs for project."""
    history = project_repo.get_analysis_history(project_id, limit=25)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "total_runs": len(history),
            "history": [h.to_dict() for h in history],
        },
    }), 200
