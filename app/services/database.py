"""DatabaseService — async SQLAlchemy abstraction layer."""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class DatabaseService(Generic[T]):
    """
    Generic async database service following the Repository pattern.
    Provides CRUD operations with explicit transaction management.
    Configured for Neon PostgreSQL serverless with small pool sizes.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, instance: T) -> T:
        """Create a new record. Raises on constraint violations."""
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, model_class: Type[T], record_id: int) -> Optional[T]:
        """Fetch a single record by primary key."""
        result = await self.session.execute(
            select(model_class).where(model_class.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(
        self, model_class: Type[T], field_name: str, value: Any
    ) -> Optional[T]:
        """Fetch a single record by an arbitrary field."""
        column = getattr(model_class, field_name)
        result = await self.session.execute(
            select(model_class).where(column == value)
        )
        return result.scalar_one_or_none()

    async def get_first(self, model_class: Type[T]) -> Optional[T]:
        """Fetch the first record (useful for singleton models like Profile)."""
        result = await self.session.execute(
            select(model_class).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        model_class: Type[T],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List] = None,
    ) -> List[T]:
        """Fetch paginated records with optional filters and ordering."""
        query = select(model_class)

        if filters:
            for field, value in filters.items():
                column = getattr(model_class, field)
                query = query.where(column == value)

        if order_by:
            query = query.order_by(*order_by)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, instance: T, data: Dict[str, Any]) -> T:
        """Update a record with the provided field values."""
        for field, value in data.items():
            if hasattr(instance, field) and value is not None:
                setattr(instance, field, value)
        # Update updated_at if the model has it
        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.utcnow()
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: T) -> bool:
        """Delete a record."""
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def count(
        self,
        model_class: Type[T],
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count records with optional filters."""
        query = select(func.count()).select_from(model_class)

        if filters:
            for field, value in filters.items():
                column = getattr(model_class, field)
                query = query.where(column == value)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_latest(self, model_class: Type[T]) -> Optional[T]:
        """Fetch the most recently created record."""
        result = await self.session.execute(
            select(model_class).order_by(model_class.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def ping(self) -> bool:
        """Check database connectivity. Returns True if reachable."""
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            logger.warning("database_ping_failed", error=str(exc))
            return False


def get_db_service(session: AsyncSession) -> DatabaseService:
    """Factory function to create a DatabaseService from a session."""
    return DatabaseService(session)
