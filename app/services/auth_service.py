from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.errors.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import UserLoginSchema, UserRegisterSchema
from app.security.password import PasswordManager
from app.security.tokens import TokenManager


class AuthService:
    """Business logic for user account registration, password authentication, and session token issuance."""

    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    def register(self, schema: UserRegisterSchema, jwt_secret_key: str, expires_minutes: int = 1440) -> Dict[str, Any]:
        """Register a new user account and generate an immediate access token."""
        if self.user_repo.email_exists(schema.email):
            raise ConflictError(f"A user with email '{schema.email}' already exists.")

        if self.user_repo.username_exists(schema.username):
            raise ConflictError(f"Username '{schema.username}' is already taken.")

        password_hash = PasswordManager.hash_password(schema.password)
        user = User(
            username=schema.username,
            email=schema.email,
            password_hash=password_hash,
            full_name=schema.full_name,
            role=schema.role,
            is_active=True,
            last_login_at=datetime.now(timezone.utc),
        )
        saved_user = self.user_repo.create(user)

        token = TokenManager.create_access_token(
            user_id=saved_user.id,
            email=saved_user.email,
            role=saved_user.role,
            secret_key=jwt_secret_key,
            expires_minutes=expires_minutes,
        )

        return {
            "token": token,
            "user": saved_user.to_dict(),
            "expires_in_minutes": expires_minutes,
        }

    def login(self, schema: UserLoginSchema, jwt_secret_key: str, expires_minutes: int = 1440) -> Dict[str, Any]:
        """Authenticate user credentials and return signed access token."""
        user = None
        if "@" in schema.email_or_username:
            user = self.user_repo.get_by_email(schema.email_or_username)
        else:
            user = self.user_repo.get_by_username(schema.email_or_username)

        if not user:
            raise AuthenticationError("Invalid username/email or password.")

        if not user.is_active:
            raise AuthenticationError("This user account has been deactivated.")

        if not PasswordManager.verify_password(schema.password, user.password_hash):
            raise AuthenticationError("Invalid username/email or password.")

        # Update last login timestamp
        self.user_repo.update(user, last_login_at=datetime.now(timezone.utc))

        token = TokenManager.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            secret_key=jwt_secret_key,
            expires_minutes=expires_minutes,
        )

        return {
            "token": token,
            "user": user.to_dict(),
            "expires_in_minutes": expires_minutes,
        }

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user profile by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User profile not found.")
        return user.to_dict()
