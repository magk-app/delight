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

from app.core.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.async_database_url,  # Use async driver (postgresql+asyncpg://)
    echo=settings.ENVIRONMENT == "development",  # Log SQL in development
    future=True,  # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,  # Test connections before use (important for Supabase)
    pool_size=10,  # Number of persistent connections
    max_overflow=20,  # Additional connections under load (30 max total)
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
