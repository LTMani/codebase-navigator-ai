from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import login_required
from app.repositories.impact_repository import ImpactRepository
from app.schemas.analysis_schemas import ImpactSimulationSchema
from app.services.impact_service import ImpactService

impact_bp = Blueprint("impact", __name__, url_prefix="/api/projects/<project_id>/impact")
impact_service = ImpactService()
impact_repo = ImpactRepository()


@impact_bp.route("/simulate", methods=["POST"])
@login_required
def simulate_change_impact(project_id: str):
    """Calculate blast radius and affected downstream components when a file/symbol changes."""
    schema = ImpactSimulationSchema.from_dict(request.get_json() or {})
    result = impact_service.calculate_impact(
        project_id=project_id,
        target_file_path=schema.target_file_path,
        target_symbol_name=schema.target_symbol_name,
    )
    return jsonify({
        "success": True,
        "data": result,
    }), 200


@impact_bp.route("/high-risk", methods=["GET"])
@login_required
def get_high_risk_modules(project_id: str):
    """Retrieve modules with highest blast radius scores in project."""
    high_risk = impact_repo.get_high_risk_modules(project_id, limit=20)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "high_risk_modules": [m.to_dict() for m in high_risk],
        },
    }), 200
