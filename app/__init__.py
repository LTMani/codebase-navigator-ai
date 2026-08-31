import os
from pathlib import Path
from flask import Flask, render_template, send_from_directory
from app.config.settings import get_config
from app.config.logging_config import configure_logging
from app.extensions import db, cors
from app.errors.handlers import register_error_handlers
from app.middleware.request_logger import init_request_logger
from app.middleware.rate_limiter import check_rate_limit


def create_app(env_name: str | None = None) -> Flask:
    """Application factory for CodeBase Navigator AI."""
    cfg = get_config(env_name)

    base_dir = Path(__file__).resolve().parent.parent
    frontend_dir = base_dir / "frontend"
    templates_dir = frontend_dir / "templates"
    static_dir = frontend_dir / "static"

    application = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )
    application.config.from_object(cfg)

    # Configure Logging
    configure_logging(
        app_name="codebase_navigator",
        log_level=cfg.LOG_LEVEL,
        log_file=cfg.LOG_FILE if not cfg.TESTING else None,
    )

    # Initialize Extensions
    db.init_app(application)
    cors.init_app(application, resources={r"/api/*": {"origins": "*"}})

    # Middleware & Error Handlers
    register_error_handlers(application)
    init_request_logger(application)

    @application.before_request
    def apply_rate_limiting():
        if not application.config.get("TESTING", False):
            check_rate_limit()

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.settings_routes import settings_bp
    application.register_blueprint(auth_bp)
    application.register_blueprint(settings_bp)

    # Register lazy blueprints if already implemented
    try:
        from app.routes.project_routes import project_bp
        application.register_blueprint(project_bp)
    except ImportError:
        pass

    try:
        from app.routes.tree_routes import tree_bp
        application.register_blueprint(tree_bp)
    except ImportError:
        pass

    try:
        from app.routes.file_intelligence_routes import file_intelligence_bp
        application.register_blueprint(file_intelligence_bp)
    except ImportError:
        pass

    try:
        from app.routes.dependency_routes import dependency_bp
        application.register_blueprint(dependency_bp)
    except ImportError:
        pass

    try:
        from app.routes.architecture_routes import architecture_bp
        application.register_blueprint(architecture_bp)
    except ImportError:
        pass

    try:
        from app.routes.flow_routes import flow_bp
        application.register_blueprint(flow_bp)
    except ImportError:
        pass

    try:
        from app.routes.impact_routes import impact_bp
        application.register_blueprint(impact_bp)
    except ImportError:
        pass

    try:
        from app.routes.search_routes import search_bp
        application.register_blueprint(search_bp)
    except ImportError:
        pass

    try:
        from app.routes.health_routes import health_bp
        application.register_blueprint(health_bp)
    except ImportError:
        pass

    try:
        from app.routes.circular_routes import circular_bp
        application.register_blueprint(circular_bp)
    except ImportError:
        pass

    try:
        from app.routes.onboarding_routes import onboarding_bp
        application.register_blueprint(onboarding_bp)
    except ImportError:
        pass

    try:
        from app.routes.knowledge_map_routes import knowledge_map_bp
        application.register_blueprint(knowledge_map_bp)
    except ImportError:
        pass

    try:
        from app.routes.copilot_routes import copilot_bp
        application.register_blueprint(copilot_bp)
    except ImportError:
        pass

    try:
        from app.routes.history_routes import history_bp
        application.register_blueprint(history_bp)
    except ImportError:
        pass

    try:
        from app.routes.report_routes import report_bp
        application.register_blueprint(report_bp)
    except ImportError:
        pass

    # Root and SPA fallback route
    @application.route("/", defaults={"path": ""})
    @application.route("/<path:path>")
    def serve_spa(path: str):
        if path.startswith("api/"):
            return {"success": False, "error": {"code": "ENDPOINT_NOT_FOUND", "message": "API endpoint not found"}}, 404
        index_file = templates_dir / "index.html"
        if index_file.exists():
            return render_template("index.html")
        return {
            "name": cfg.APP_NAME,
            "version": cfg.APP_VERSION,
            "status": "running",
            "message": "CodeBase Navigator AI API server active.",
        }

    # Initialize Database Tables
    with application.app_context():
        from app import models as app_models
        db.create_all()

    return application
