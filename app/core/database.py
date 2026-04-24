"""Database engine initialization and FastAPI dependency."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# Create async engine with Neon-optimized settings
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,           # Small pool for serverless
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=300,      # Recycle connections every 5 min
    pool_pre_ping=True,    # Verify connection before use
    connect_args={
        "server_settings": {"application_name": "portfolio"}
    },
    echo=settings.is_development,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
