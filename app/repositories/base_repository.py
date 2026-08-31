from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select, update, delete, func
from app.extensions import db
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing standard data access operations with SQLAlchemy 2.0 style queries."""

    def __init__(self, model_class: Type[ModelType]):
        self.model_class = model_class

    def get_by_id(self, entity_id: str) -> Optional[ModelType]:
        """Fetch a single record by its UUID primary key."""
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """Retrieve paginated list of records."""
        stmt = select(self.model_class).limit(limit).offset(offset)
        return list(db.session.execute(stmt).scalars().all())

    def count(self) -> int:
        """Count total records for this entity."""
        stmt = select(func.count()).select_from(self.model_class)
        return db.session.execute(stmt).scalar() or 0

    def create(self, entity: ModelType) -> ModelType:
        """Add new entity to session and commit."""
        db.session.add(entity)
        db.session.commit()
        db.session.refresh(entity)
        return entity

    def create_many(self, entities: List[ModelType]) -> List[ModelType]:
        """Bulk add entities to session and commit."""
        if not entities:
            return []
        db.session.add_all(entities)
        db.session.commit()
        return entities

    def update(self, entity: ModelType, **kwargs) -> ModelType:
        """Update entity attributes and commit."""
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        db.session.commit()
        db.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> bool:
        """Delete entity from database and commit."""
        db.session.delete(entity)
        db.session.commit()
        return True

    def delete_by_id(self, entity_id: str) -> bool:
        """Delete entity by ID if found."""
        entity = self.get_by_id(entity_id)
        if entity:
            return self.delete(entity)
        return False
