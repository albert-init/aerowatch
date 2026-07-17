from typing import Any, Generic, TypeVar
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Define generic types for our SQLAlchemy models
ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        """
        Initializes the repository with the specific SQLAlchemy model.
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Fetch a single record by its primary key, utilizing the Identity Map cache."""
        # Much faster, checks memory before querying the DB
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Fetch multiple records with pagination."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> ModelType:
        """Create and flush a new record to the database."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)

        await db.flush()
        # Pulls generated fields (like created_at timestamps) back into Python
        await db.refresh(db_obj)

        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()

        # Pulls generated fields (like onupdate=func.now()) back into Python
        await db.refresh(db_obj)

        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Delete a record by its primary key."""
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
