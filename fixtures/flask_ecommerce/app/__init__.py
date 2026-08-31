"""Flask E-Commerce Application Configuration and Core Factory."""

import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_ecommerce_app(config_override=None):
    """Application factory for Flask E-Commerce micro-monolith."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-12345")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    # Register blueprints
    from fixtures.flask_ecommerce.app.routes.auth_routes import auth_bp
    from fixtures.flask_ecommerce.app.routes.catalog_routes import catalog_bp
    from fixtures.flask_ecommerce.app.routes.cart_routes import cart_bp
    from fixtures.flask_ecommerce.app.routes.order_routes import order_bp
    from fixtures.flask_ecommerce.app.routes.payment_routes import payment_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(catalog_bp, url_prefix="/api/v1/catalog")
    app.register_blueprint(cart_bp, url_prefix="/api/v1/cart")
    app.register_blueprint(order_bp, url_prefix="/api/v1/orders")
    app.register_blueprint(payment_bp, url_prefix="/api/v1/payments")

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy", "service": "Flask E-Commerce Backend"}), 200

    with app.app_context():
        db.create_all()

    return app
