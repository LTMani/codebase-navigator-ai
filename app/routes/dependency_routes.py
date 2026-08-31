from flask import Blueprint, jsonify
from app.middleware.auth_middleware import login_required
from app.services.dependency_service import DependencyService

dependency_bp = Blueprint("dependencies", __name__, url_prefix="/api/projects/<project_id>/dependencies")
dependency_service = DependencyService()


@dependency_bp.route("", methods=["GET"])
@login_required
def get_dependency_graph(project_id: str):
    """Retrieve full dependency graph with nodes, edges, cycles, and PageRank."""
    graph_data = dependency_service.build_dependency_graph(project_id)
    return jsonify({
        "success": True,
        "data": graph_data,
    }), 200


@dependency_bp.route("/cycles", methods=["GET"])
@login_required
def get_circular_dependencies(project_id: str):
    """Retrieve detected circular dependency cycles."""
    graph_data = dependency_service.build_dependency_graph(project_id)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "circular_cycles_count": graph_data["circular_cycles_count"],
            "cycles": graph_data["cycles"],
        },
    }), 200
