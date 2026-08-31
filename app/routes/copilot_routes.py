from flask import Blueprint, current_app, g, jsonify, request
from app.errors.exceptions import NotFoundError
from app.middleware.auth_middleware import login_required
from app.repositories.copilot_repository import CopilotRepository
from app.schemas.copilot_schemas import CopilotPromptSchema
from app.services.copilot_service import CopilotService

copilot_bp = Blueprint("copilot", __name__, url_prefix="/api/projects/<project_id>/copilot")
copilot_service = CopilotService()
copilot_repo = CopilotRepository()


@copilot_bp.route("/query", methods=["POST"])
@login_required
def query_copilot(project_id: str):
    """Ask questions to the codebase copilot with grounded AST intelligence."""
    schema = CopilotPromptSchema.from_dict(request.get_json() or {})
    provider = current_app.config.get("AI_PROVIDER", "offline")
    api_key = current_app.config.get("AI_API_KEY")

    result = copilot_service.process_query(
        project_id=project_id,
        user_id=g.current_user.id,
        schema=schema,
        ai_provider=provider,
        ai_api_key=api_key,
    )
    return jsonify({
        "success": True,
        "data": result,
    }), 200


@copilot_bp.route("/conversations", methods=["GET"])
@login_required
def list_conversations(project_id: str):
    """Retrieve chat conversation threads for user in project."""
    convs = copilot_repo.get_by_user_and_project(g.current_user.id, project_id)
    return jsonify({
        "success": True,
        "data": {
            "project_id": project_id,
            "conversations": [c.to_dict() for c in convs],
        },
    }), 200


@copilot_bp.route("/conversations/<conversation_id>", methods=["GET"])
@login_required
def get_conversation_history(project_id: str, conversation_id: str):
    """Retrieve all messages in a specific Copilot conversation thread."""
    conv = copilot_repo.get_by_id(conversation_id)
    if not conv or conv.project_id != project_id:
        raise NotFoundError("Conversation not found.")

    messages = copilot_repo.get_messages(conversation_id)
    return jsonify({
        "success": True,
        "data": {
            "conversation": conv.to_dict(),
            "messages": [m.to_dict() for m in messages],
        },
    }), 200
