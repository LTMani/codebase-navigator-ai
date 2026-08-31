from typing import Optional
from sqlalchemy import select
from app.extensions import db
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access repository for User entities."""

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Lookup user by unique email address."""
        stmt = select(User).where(User.email == email.strip().lower())
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        """Lookup user by unique username."""
        stmt = select(User).where(User.username == username.strip())
        return db.session.execute(stmt).scalar_one_or_none()

    def email_exists(self, email: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check whether email is already taken."""
        stmt = select(User.id).where(User.email == email.strip().lower())
        if exclude_user_id:
            stmt = stmt.where(User.id != exclude_user_id)
        return db.session.execute(stmt).first() is not None

    def username_exists(self, username: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check whether username is already taken."""
        stmt = select(User.id).where(User.username == username.strip())
        if exclude_user_id:
            stmt = stmt.where(User.id != exclude_user_id)
        return db.session.execute(stmt).first() is not None
