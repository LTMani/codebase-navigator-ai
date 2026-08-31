from flask import Blueprint, jsonify
from app.middleware.auth_middleware import login_required
from app.services.knowledge_map_service import KnowledgeMapService

knowledge_map_bp = Blueprint("knowledge_map", __name__, url_prefix="/api/projects/<project_id>/knowledge-map")
knowledge_map_service = KnowledgeMapService()


@knowledge_map_bp.route("", methods=["GET"])
@login_required
def get_knowledge_map(project_id: str):
    """Retrieve high-level domain clusters, key abstractions, and relationship links."""
    data = knowledge_map_service.generate_knowledge_map(project_id)
    return jsonify({
        "success": True,
        "data": data,
    }), 200
