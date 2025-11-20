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
    
    # Add SSL configuration for Supabase/cloud databases
    # asyncpg requires SSL to be configured via connect_args
    connect_args = {}
    
    if settings.requires_ssl:
        # For Supabase pooler, use SSL with relaxed verification
        # The pooler handles SSL termination
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context
        connect_args["server_settings"] = {
            "application_name": "delight-backend"
        }
    
    # Note: SQLAlchemy's asyncpg dialect always uses prepared statements.
    # Transaction Mode pooler (port 6543) does NOT support prepared statements.
    # You MUST use Session Mode pooler (port 5432) for SQLAlchemy to work correctly.
    if ":6543" in settings.async_database_url:
        import warnings
        warnings.warn(
            "⚠️  WARNING: Transaction Mode pooler (port 6543) does NOT support prepared statements, "
            "but SQLAlchemy's asyncpg dialect requires them. This will cause errors.\n"
            "Please switch to Session Mode pooler (port 5432) in your DATABASE_URL.",
            UserWarning
        )
    
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

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
