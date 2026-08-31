from flask import Blueprint, current_app, g, jsonify, request
from app.middleware.auth_middleware import login_required
from app.schemas.auth_schemas import UserLoginSchema, UserRegisterSchema
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_service = AuthService()
audit_service = AuditService()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    schema = UserRegisterSchema.from_dict(request.get_json() or {})
    jwt_secret = current_app.config["JWT_SECRET_KEY"]
    expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"]

    result = auth_service.register(schema, jwt_secret_key=jwt_secret, expires_minutes=expires)
    audit_service.log(
        action="user_registered",
        user_id=result["user"]["id"],
        resource_type="user",
        resource_id=result["user"]["id"],
        details={"username": schema.username, "email": schema.email},
    )

    return jsonify({
        "success": True,
        "message": "User registered successfully.",
        "data": result,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Sign in existing user with email/username and password."""
    schema = UserLoginSchema.from_dict(request.get_json() or {})
    jwt_secret = current_app.config["JWT_SECRET_KEY"]
    expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"]

    result = auth_service.login(schema, jwt_secret_key=jwt_secret, expires_minutes=expires)
    audit_service.log(
        action="user_login",
        user_id=result["user"]["id"],
        resource_type="user",
        resource_id=result["user"]["id"],
    )

    return jsonify({
        "success": True,
        "message": "Authentication successful.",
        "data": result,
    }), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Get authenticated user profile."""
    profile = auth_service.get_profile(g.current_user.id)
    return jsonify({
        "success": True,
        "data": {
            "user": profile,
        },
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Client-side session termination endpoint."""
    return jsonify({
        "success": True,
        "message": "Logged out successfully.",
    }), 200
