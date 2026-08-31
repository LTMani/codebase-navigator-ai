from flask import Blueprint, jsonify
from app.middleware.auth_middleware import login_required
from app.services.architecture_service import ArchitectureService

architecture_bp = Blueprint("architecture", __name__, url_prefix="/api/projects/<project_id>/architecture")
architecture_service = ArchitectureService()


@architecture_bp.route("", methods=["GET"])
@login_required
def get_architecture_overview(project_id: str):
    """Retrieve classified architectural layers, confidence scores, and interaction matrix."""
    arch_data = architecture_service.analyze_architecture(project_id)
    return jsonify({
        "success": True,
        "data": arch_data,
    }), 200


@architecture_bp.route("/violations", methods=["GET"])
@login_required
def get_architecture_violations(project_id: str):
    """Retrieve detected architectural boundary violations and refactoring advice."""
    arch_data = architecture_service.analyze_architecture(project_id)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "violations_count": len(arch_data["violations"]),
            "violations": arch_data["violations"],
        },
    }), 200
