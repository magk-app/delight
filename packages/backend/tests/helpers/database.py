"""
Database Test Helpers
Utilities for database setup and teardown in tests
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.db.base import Base


async def create_test_tables(engine: AsyncEngine):
    """
    Create all database tables for testing

    Usage:
        async def test_with_fresh_db(async_engine):
            await create_test_tables(async_engine)
            # Run tests
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def clear_test_data(session: AsyncSession, table_name: str):
    """
    Clear specific table data during tests

    Args:
        session: Database session
        table_name: Name of table to clear

    Usage:
        await clear_test_data(db_session, "users")
    """
    await session.execute(f"DELETE FROM {table_name}")
    await session.commit()
