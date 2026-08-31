from flask import Blueprint, jsonify
from app.middleware.auth_middleware import login_required
from app.services.health_service import HealthService

health_bp = Blueprint("health", __name__, url_prefix="/api/projects/<project_id>/health")
health_service = HealthService()


@health_bp.route("", methods=["GET"])
@login_required
def get_health_metrics(project_id: str):
    """Retrieve full codebase health metrics, grades, and technical debt."""
    health_data = health_service.evaluate_code_health(project_id)
    return jsonify({
        "success": True,
        "data": health_data,
    }), 200


@health_bp.route("/hotspots", methods=["GET"])
@login_required
def get_health_hotspots(project_id: str):
    """Retrieve prioritized complexity and maintainability hotspots."""
    health_data = health_service.evaluate_code_health(project_id)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "hotspots_count": len(health_data.get("hotspots", [])),
            "hotspots": health_data.get("hotspots", []),
        },
    }), 200
