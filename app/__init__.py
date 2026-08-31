import os
from flask import Flask, render_template
from app.extensions import db, cors
from app.config import get_config

from app.routes.project_routes import project_bp
from app.routes.search_routes import search_bp
from app.routes.architecture_routes import architecture_bp
from app.routes.dependency_routes import dependency_bp
from app.routes.flow_routes import flow_bp
from app.routes.impact_routes import impact_bp
from app.routes.circular_routes import circular_bp
from app.routes.copilot_routes import copilot_bp
from app.routes.file_intelligence_routes import file_intelligence_bp
from app.routes.tree_routes import tree_bp
from app.routes.auth_routes import auth_bp
from app.routes.health_routes import health_bp
from app.routes.history_routes import history_bp
from app.routes.knowledge_map_routes import knowledge_map_bp
from app.routes.onboarding_routes import onboarding_bp
from app.routes.report_routes import report_bp
from app.routes.settings_routes import settings_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.security_routes import security_bp
from app.routes.compliance_routes import compliance_bp
from app.routes.git_routes import git_bp
from app.routes.refactor_routes import refactor_bp
from app.routes.cfg_routes import cfg_bp
from app.routes.metrics_routes import metrics_bp
from app.routes.export_routes import export_bp

def create_app(config_object="development"):
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )
    
    if isinstance(config_object, str):
        if config_object in ("testing", "development", "production", "default"):
            cfg = get_config(config_object)
            app.config.from_object(cfg)
        else:
            try:
                app.config.from_object(config_object)
            except Exception:
                cfg = get_config("development")
                app.config.from_object(cfg)
    else:
        app.config.from_object(config_object)

    db.init_app(app)
    cors.init_app(app)
    from app.errors.handlers import register_error_handlers
    register_error_handlers(app)

    # Register all blueprints
    app.register_blueprint(project_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(architecture_bp)
    app.register_blueprint(dependency_bp)
    app.register_blueprint(flow_bp)
    app.register_blueprint(impact_bp)
    app.register_blueprint(circular_bp)
    app.register_blueprint(copilot_bp)
    app.register_blueprint(file_intelligence_bp)
    app.register_blueprint(tree_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(knowledge_map_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(git_bp)
    app.register_blueprint(refactor_bp)
    app.register_blueprint(cfg_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(export_bp)

    @app.route("/")
    @app.register_blueprint if False else app.route("/project/<path:subpath>")
    def index(subpath=""):
        return render_template("index.html")

    return app
