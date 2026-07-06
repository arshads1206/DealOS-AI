"""
DealOS AI — Generic CRUD Repository.

Implements the Repository Pattern with generic typing.

Why the Repository Pattern?
- Encapsulates data access logic away from business logic
- Makes services testable (mock the repository, not the ORM)
- Provides a consistent API for CRUD across all models
- Centralizes query optimization (eager loading, filtering)

Type parameter T must be a SQLAlchemy model inheriting from Base.
"""

import uuid
from typing import Generic, TypeVar, Any

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class CRUDRepository(Generic[T]):
    """
    Generic async CRUD repository.

    Provides: create, get_by_id, get_all, update, soft_delete, hard_delete, count.

    Usage:
        class UserRepository(CRUDRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)

            async def get_by_email(self, email: str) -> User | None:
                # Custom query method
                ...
    """

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def create(self, **kwargs: Any) -> T:
        """Create a new record."""
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """Get a single record by ID, excluding soft-deleted."""
        query = select(self._model).where(self._model.id == id)

        # Apply soft-delete filter if model supports it
        if hasattr(self._model, "is_deleted"):
            query = query.where(self._model.is_deleted == False)  # noqa: E712

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        descending: bool = True,
        filters: dict[str, Any] | None = None,
    ) -> list[T]:
        """
        Get paginated records with optional filtering.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum records to return.
            order_by: Column name to sort by.
            descending: Sort order.
            filters: Column name → value equality filters.
        """
        query = select(self._model)

        # Apply soft-delete filter if model supports it
        if hasattr(self._model, "is_deleted"):
            query = query.where(self._model.is_deleted == False)  # noqa: E712

        # Apply dynamic filters
        if filters:
            for key, value in filters.items():
                if hasattr(self._model, key) and value is not None:
                    query = query.where(getattr(self._model, key) == value)

        # Apply ordering
        order_column = getattr(self._model, order_by, None)
        if order_column is not None:
            query = query.order_by(
                order_column.desc() if descending else order_column.asc()
            )

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, id: uuid.UUID, **kwargs: Any) -> T | None:
        """Update a record by ID. Returns the updated record or None."""
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def soft_delete(self, id: uuid.UUID) -> bool:
        """Soft-delete a record. Returns True if the record existed."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        if hasattr(instance, "is_deleted"):
            instance.is_deleted = True
            await self._session.flush()
            return True

        return False

    async def hard_delete(self, id: uuid.UUID) -> bool:
        """
        Permanently delete a record.

        WARNING: Use with extreme caution. Most operations should use soft_delete.
        Hard delete is reserved for non-critical data (e.g., chunks during reprocessing).
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self._session.delete(instance)
        await self._session.flush()
        return True

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count records with optional filtering."""
        query = select(func.count()).select_from(self._model)

        if hasattr(self._model, "is_deleted"):
            query = query.where(self._model.is_deleted == False)  # noqa: E712

        if filters:
            for key, value in filters.items():
                if hasattr(self._model, key) and value is not None:
                    query = query.where(getattr(self._model, key) == value)

        result = await self._session.execute(query)
        return result.scalar_one()

    async def exists(self, id: uuid.UUID) -> bool:
        """Check if a record exists."""
        return await self.get_by_id(id) is not None
