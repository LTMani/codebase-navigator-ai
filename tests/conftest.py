import os
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.security.password import PasswordManager


@pytest.fixture(scope="session")
def app():
    """Create test application context with in-memory SQLite database."""
    flask_app = create_app("testing")
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean all tables before each test execution."""
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    yield


@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create default authenticated test user."""
    with app.app_context():
        user = User(
            username="testdeveloper",
            email="developer@example.com",
            password_hash=PasswordManager.hash_password("SecurePassword123!"),
            full_name="Test Developer",
            role="developer",
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user
