from flask import Blueprint, jsonify
from app.middleware.auth_middleware import login_required
from app.services.health_service import HealthService

circular_bp = Blueprint("circular", __name__, url_prefix="/api/projects/<project_id>/circular-dependencies")
health_service = HealthService()


@circular_bp.route("", methods=["GET"])
@login_required
def get_circular_dependency_details(project_id: str):
    """Retrieve detailed circular dependency clusters, cycle paths, and refactoring tips."""
    health_data = health_service.evaluate_code_health(project_id)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "circular_cycles_count": health_data.get("circular_dependency_cycles_count", 0),
            "clusters": health_data.get("clusters", []),
        },
    }), 200
