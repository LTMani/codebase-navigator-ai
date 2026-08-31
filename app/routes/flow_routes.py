from flask import Blueprint, jsonify
from app.errors.exceptions import NotFoundError
from app.middleware.auth_middleware import login_required
from app.repositories.flow_repository import FlowRepository
from app.services.code_flow_service import CodeFlowService

flow_bp = Blueprint("flows", __name__, url_prefix="/api/projects/<project_id>/flows")
flow_service = CodeFlowService()
flow_repo = FlowRepository()


@flow_bp.route("", methods=["GET"])
@login_required
def list_code_flows(project_id: str):
    """Retrieve all discovered multi-layer execution flows in project."""
    flows = flow_service.discover_code_flows(project_id)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "flows_count": len(flows),
            "flows": flows,
        },
    }), 200


@flow_bp.route("/<flow_id>", methods=["GET"])
@login_required
def get_flow_details(project_id: str, flow_id: str):
    """Retrieve discrete steps and nodes for a specific execution flow."""
    flow = flow_repo.get_by_id(flow_id)
    if not flow or flow.project_id != project_id:
        raise NotFoundError("Code flow not found.")

    nodes = flow_repo.get_nodes_by_flow(flow_id)
    return jsonify({
        "success": True,
        "data": {
            "flow": flow.to_dict(),
            "nodes": [n.to_dict() for n in nodes],
        },
    }), 200
