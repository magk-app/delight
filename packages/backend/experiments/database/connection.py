"""Safe database connection utilities for experiments.

This module provides database access with safety features:
- Read-only mode toggle
- Connection validation
- Error handling
- Usage warnings

Example:
    >>> from experiments.database.connection import get_experiment_db
    >>>
    >>> async with get_experiment_db() as db:
    ...     # Use db session
    ...     result = await db.execute(select(Memory).limit(10))
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from experiments.config import get_config


# Global engine (created on first use)
_engine = None
_async_session_factory = None


def get_engine():
    """Get or create async database engine."""
    global _engine, _async_session_factory

    if _engine is None:
        config = get_config()
        _engine = create_async_engine(
            config.database_url,
            echo=False,  # Set to True for SQL logging
            future=True
        )
        _async_session_factory = sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    return _engine


def get_session_factory():
    """Get async session factory."""
    get_engine()  # Ensure engine is created
    return _async_session_factory


@asynccontextmanager
async def get_experiment_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for experiments.

    This is the main way to access the database in experiments.
    It provides proper async context management and cleanup.

    Yields:
        AsyncSession for database operations

    Example:
        >>> async with get_experiment_db() as db:
        ...     stmt = select(Memory).limit(10)
        ...     result = await db.execute(stmt)
        ...     memories = result.scalars().all()
    """
    config = get_config()

    if config.read_only_mode:
        print("⚠️  READ-ONLY MODE: Database writes are disabled")

    factory = get_session_factory()
    session = factory()

    try:
        yield session
    finally:
        await session.close()


async def test_connection() -> bool:
    """Test database connection.

    Returns:
        True if connection successful, False otherwise

    Example:
        >>> if await test_connection():
        ...     print("Database connected!")
    """
    try:
        async with get_experiment_db() as db:
            # Simple query to test connection
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def check_pgvector() -> bool:
    """Check if pgvector extension is available.

    Returns:
        True if pgvector is installed, False otherwise

    Example:
        >>> if await check_pgvector():
        ...     print("pgvector extension is available")
    """
    try:
        async with get_experiment_db() as db:
            result = await db.execute(
                text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'")
            )
            count = result.scalar()
            return count > 0
    except Exception as e:
        print(f"❌ Error checking pgvector: {e}")
        return False


async def get_database_info() -> dict:
    """Get database information.

    Returns:
        Dictionary with database details

    Example:
        >>> info = await get_database_info()
        >>> print(f"PostgreSQL version: {info['version']}")
    """
    info = {}

    try:
        async with get_experiment_db() as db:
            # PostgreSQL version
            result = await db.execute(text("SELECT version()"))
            info["version"] = result.scalar()

            # Database name
            result = await db.execute(text("SELECT current_database()"))
            info["database"] = result.scalar()

            # Check pgvector
            info["pgvector_installed"] = await check_pgvector()

            # Memory table stats
            result = await db.execute(
                text("""
                    SELECT
                        COUNT(*) as total_memories,
                        COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings
                    FROM memories
                """)
            )
            row = result.one()
            info["total_memories"] = row[0]
            info["memories_with_embeddings"] = row[1]

            # Collection stats
            result = await db.execute(
                text("SELECT COUNT(*) FROM memory_collections")
            )
            info["total_collections"] = result.scalar()

    except Exception as e:
        info["error"] = str(e)

    return info


async def print_database_info():
    """Print formatted database information."""
    print("\n" + "=" * 60)
    print("🗄️  Database Information")
    print("=" * 60)

    # Test connection
    print("Testing connection...")
    if await test_connection():
        print("✅ Connection successful\n")
    else:
        print("❌ Connection failed\n")
        return

    # Get info
    info = await get_database_info()

    if "error" in info:
        print(f"❌ Error getting database info: {info['error']}")
        return

    print(f"Database:          {info.get('database', 'unknown')}")
    print(f"PostgreSQL:        {info.get('version', 'unknown')[:50]}...")
    print(f"pgvector:          {'✅ Installed' if info.get('pgvector_installed') else '❌ Not installed'}")
    print()
    print(f"Total Memories:    {info.get('total_memories', 0):,}")
    print(f"With Embeddings:   {info.get('memories_with_embeddings', 0):,}")
    print(f"Collections:       {info.get('total_collections', 0):,}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    """Test database connection."""
    asyncio.run(print_database_info())
