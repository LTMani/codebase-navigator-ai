import pytest
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.password import PasswordManager
from app.security.tokens import TokenManager

user_repo = UserRepository()


def test_password_hashing_and_verification():
    raw_pass = "MySecretPass123"
    hashed = PasswordManager.hash_password(raw_pass)
    assert hashed != raw_pass
    assert PasswordManager.verify_password(raw_pass, hashed) is True
    assert PasswordManager.verify_password("WrongPass123", hashed) is False


def test_password_strength_validation():
    valid, _ = PasswordManager.validate_password_strength("Short1")
    assert valid is False  # too short
    valid, _ = PasswordManager.validate_password_strength("alllowercase123")
    assert valid is True
    valid, _ = PasswordManager.validate_password_strength("NoDigitsHere!")
    assert valid is False


def test_jwt_token_generation_and_decoding():
    secret = "test-secret-key-32-bytes-minimum!"
    token = TokenManager.create_access_token(
        user_id="12345",
        email="test@example.com",
        role="developer",
        secret_key=secret,
        expires_minutes=60,
    )
    assert isinstance(token, str)
    decoded = TokenManager.decode_token(token, secret)
    assert decoded["sub"] == "12345"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "developer"


def test_user_registration_api(client):
    res = client.post(
        "/api/auth/register",
        json={
            "username": "alice_dev",
            "email": "alice@example.com",
            "password": "Password1234",
            "full_name": "Alice Engineer",
        },
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["username"] == "alice_dev"
    assert "token" in data["data"]


def test_user_login_api(client, test_user):
    res = client.post(
        "/api/auth/login",
        json={
            "email_or_username": "developer@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data["data"]


def test_login_invalid_password(client, test_user):
    res = client.post(
        "/api/auth/login",
        json={
            "email_or_username": "developer@example.com",
            "password": "WrongPassword999!",
        },
    )
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_get_current_user_profile(client, test_user, app):
    secret = app.config["JWT_SECRET_KEY"]
    token = TokenManager.create_access_token(
        user_id=test_user.id,
        email=test_user.email,
        role=test_user.role,
        secret_key=secret,
    )
    res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["username"] == "testdeveloper"
