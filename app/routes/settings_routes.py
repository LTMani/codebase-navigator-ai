from flask import Blueprint, current_app, jsonify, request
from app.middleware.auth_middleware import login_required

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@settings_bp.route("", methods=["GET"])
@login_required
def get_settings():
    """Retrieve non-sensitive system settings and runtime configuration."""
    cfg = current_app.config
    return jsonify({
        "success": True,
        "data": {
            "app_name": cfg.get("APP_NAME", "CodeBase Navigator AI"),
            "app_version": cfg.get("APP_VERSION", "1.0.0"),
            "environment": cfg.get("APP_ENV", "development"),
            "ai_provider": cfg.get("AI_PROVIDER", "offline"),
            "ai_model": cfg.get("AI_MODEL_NAME", "default"),
            "has_ai_key": bool(cfg.get("AI_API_KEY")),
            "max_file_size_mb": cfg.get("MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024) // (1024 * 1024),
            "max_project_files": cfg.get("MAX_PROJECT_FILES", 15000),
            "allowed_archives": cfg.get("ALLOWED_ARCHIVE_EXTENSIONS", [".zip", ".tar.gz"]),
        },
    }), 200


@settings_bp.route("/ai", methods=["POST"])
@login_required
def update_ai_settings():
    """Update runtime AI provider configuration (temporary in-memory for session/runtime)."""
    data = request.get_json() or {}
    provider = data.get("provider")
    api_key = data.get("api_key")
    model_name = data.get("model_name")

    if provider:
        current_app.config["AI_PROVIDER"] = str(provider).strip().lower()
    if api_key is not None:
        current_app.config["AI_API_KEY"] = str(api_key).strip() if api_key else None
    if model_name:
        current_app.config["AI_MODEL_NAME"] = str(model_name).strip()

    return jsonify({
        "success": True,
        "message": "AI settings updated successfully.",
        "data": {
            "ai_provider": current_app.config["AI_PROVIDER"],
            "ai_model": current_app.config.get("AI_MODEL_NAME", "default"),
            "has_ai_key": bool(current_app.config.get("AI_API_KEY")),
        },
    }), 200
