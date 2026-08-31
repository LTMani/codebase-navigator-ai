import functools
from typing import Any, Callable, Optional
from flask import g, request
from app.config.settings import BaseConfig
from app.errors.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.tokens import TokenManager

user_repo = UserRepository()


def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from Authorization Bearer header or cookie."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    # Check session cookie fallback
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token.strip()
    return None


def authenticate_request(secret_key: str) -> Optional[User]:
    """Validate token from request and return active User object."""
    token = extract_token_from_request()
    if not token:
        return None

    payload = TokenManager.decode_token(token, secret_key)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload: missing subject.")

    user = user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User account not found or disabled.")

    return user


def login_required(f: Callable) -> Callable:
    """Decorator requiring a valid authenticated user."""
    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        secret_key = request.app.config.get("JWT_SECRET_KEY") if hasattr(request, "app") else BaseConfig.JWT_SECRET_KEY
        user = authenticate_request(secret_key)
        if not user:
            raise AuthenticationError("Authentication required to access this endpoint.")
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def optional_auth(f: Callable) -> Callable:
    """Decorator that populates g.current_user if token present, but does not block unauthenticated."""
    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        try:
            secret_key = request.app.config.get("JWT_SECRET_KEY") if hasattr(request, "app") else BaseConfig.JWT_SECRET_KEY
            g.current_user = authenticate_request(secret_key)
        except Exception:
            g.current_user = None
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f: Callable) -> Callable:
    """Decorator requiring user with 'admin' role."""
    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        secret_key = request.app.config.get("JWT_SECRET_KEY") if hasattr(request, "app") else BaseConfig.JWT_SECRET_KEY
        user = authenticate_request(secret_key)
        if not user:
            raise AuthenticationError("Authentication required.")
        if user.role != "admin":
            raise AuthorizationError("Administrator privileges required.")
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function
