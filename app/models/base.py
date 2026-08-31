import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db


def generate_uuid() -> str:
    """Generate a canonical UUIDv4 string for primary keys."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class BaseModel(db.Model):
    """Abstract base model providing UUID primary key, timestamps, and serialization utilities."""
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize model attributes to dictionary."""
        result = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, datetime):
                result[column.name] = val.isoformat()
            else:
                result[column.name] = val
        return result
