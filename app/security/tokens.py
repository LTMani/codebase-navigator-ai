import datetime
from typing import Any, Dict, Optional
import jwt
from app.errors.exceptions import AuthenticationError


class TokenManager:
    """Handles JSON Web Token creation, validation, and claims parsing."""

    @classmethod
    def create_access_token(
        cls,
        user_id: str,
        email: str,
        role: str,
        secret_key: str,
        expires_minutes: int = 1440,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate signed JWT access token with user claims and expiration timestamp."""
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=expires_minutes),
        }
        if extra_claims:
            payload.update(extra_claims)

        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token

    @classmethod
    def decode_token(cls, token: str, secret_key: str) -> Dict[str, Any]:
        """Decode and verify JWT signature and expiration."""
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Authentication token has expired. Please sign in again.")
        except jwt.InvalidTokenError as err:
            raise AuthenticationError(f"Invalid authentication token: {str(err)}")
