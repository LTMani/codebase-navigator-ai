from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError
from app.security.password import PasswordManager


@dataclass
class UserRegisterSchema:
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "developer"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserRegisterSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a valid JSON object.")

        username = str(data.get("username", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        full_name = data.get("full_name")
        if full_name:
            full_name = str(full_name).strip()
        role = str(data.get("role", "developer")).strip().lower()

        if not username:
            raise ValidationError("Username is required.")
        if len(username) < 3 or len(username) > 64:
            raise ValidationError("Username must be between 3 and 64 characters.")
        if not username.replace("_", "").replace("-", "").isalnum():
            raise ValidationError("Username may only contain letters, numbers, hyphens, and underscores.")

        if not email:
            raise ValidationError("Email is required.")
        if "@" not in email or "." not in email or len(email) > 128:
            raise ValidationError("A valid email address is required.")

        valid, msg = PasswordManager.validate_password_strength(password)
        if not valid:
            raise ValidationError(msg)

        if role not in ("developer", "admin", "viewer"):
            role = "developer"

        return cls(username=username, email=email, password=password, full_name=full_name, role=role)


@dataclass
class UserLoginSchema:
    email_or_username: str
    password: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserLoginSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a valid JSON object.")

        ident = str(data.get("email_or_username", data.get("email", data.get("username", "")))).strip()
        password = str(data.get("password", ""))

        if not ident:
            raise ValidationError("Email or username is required.")
        if not password:
            raise ValidationError("Password is required.")

        return cls(email_or_username=ident, password=password)
