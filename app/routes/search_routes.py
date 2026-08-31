from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import login_required
from app.schemas.search_schemas import SearchQuerySchema
from app.services.search_service import SearchService

search_bp = Blueprint("search", __name__, url_prefix="/api/projects/<project_id>/search")
search_service = SearchService()


@search_bp.route("", methods=["GET"])
@login_required
def search_codebase(project_id: str):
    """Search project files, symbols, functions, classes, and content."""
    schema = SearchQuerySchema.from_dict(request.args.to_dict())
    results = search_service.search(project_id, schema)
    return jsonify({
        "success": True,
        "data": results,
    }), 200
