"""
Database session management with async SQLAlchemy.
Provides async engine, session factory, and FastAPI dependency.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

is_sqlite = settings.async_database_url.startswith("sqlite")
engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
    "future": True,
}

if is_sqlite:
    # In-memory SQLite (used in tests) cannot use pooled connections
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update(
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Create async engine with environment-aware pooling
engine = create_async_engine(
    settings.async_database_url,  # Use async driver (postgresql+asyncpg://)
    **engine_kwargs,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# FastAPI dependency for database sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get a database session.

    Usage in routes:
        @router.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
