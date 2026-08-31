import re
from typing import Tuple
from werkzeug.security import generate_password_hash, check_password_hash


class PasswordManager:
    """Handles secure password hashing, verification, and policy enforcement."""

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        """Generate secure scrypt/pbkdf2 hash of plaintext password."""
        if not plain_password:
            raise ValueError("Password cannot be empty.")
        return generate_password_hash(plain_password, method="scrypt")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against stored hash with timing attack resistance."""
        if not plain_password or not hashed_password:
            return False
        return check_password_hash(hashed_password, plain_password)

    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, str]:
        """Check password against strength criteria: length, digits, and characters."""
        if not password:
            return False, "Password cannot be empty."
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long."
        if len(password) > cls.MAX_LENGTH:
            return False, f"Password cannot exceed {cls.MAX_LENGTH} characters."
        if not re.search(r"[A-Za-z]", password):
            return False, "Password must contain at least one letter."
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one digit."
        return True, "Password meets strength criteria."
