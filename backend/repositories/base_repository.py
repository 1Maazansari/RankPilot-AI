"""
Generic Base Repository for CRUD operations.
"""

from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

from backend.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing common CRUD operations.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, obj: ModelType) -> ModelType:
        """Create a new record."""
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_id(self, db: Session, obj_id: int) -> ModelType | None:
        """Get record by primary key."""
        return db.get(self.model, obj_id)

    def get_all(self, db: Session) -> list[ModelType]:
        """Return all records."""
        return db.query(self.model).all()

    def update(self, db: Session, obj: ModelType) -> ModelType:
        """Update an existing record."""
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType) -> None:
        """Delete a record."""
        db.delete(obj)
        db.commit()