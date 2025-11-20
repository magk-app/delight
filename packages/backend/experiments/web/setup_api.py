"""
Database Setup API

Provides endpoints for database initialization and table creation.
This allows creating tables through the API when direct CLI access is restricted.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

router = APIRouter(prefix="/api/setup", tags=["setup"])

@router.post("/create-tables")
async def create_database_tables():
    """
    Create all database tables using SQLAlchemy.

    This is useful when Alembic migrations cannot be run due to
    environment restrictions.
    """
    try:
        from app.db.session import engine
        from app.models import Base

        tables_created = []

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

            # List created tables
            for table_name in Base.metadata.tables.keys():
                tables_created.append(table_name)

        return {
            "status": "success",
            "message": "Database tables created successfully",
            "tables": tables_created,
            "count": len(tables_created)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": error_trace
            }
        )


@router.post("/drop-tables")
async def drop_database_tables():
    """
    Drop all database tables.

    WARNING: This will delete all data! Use only in development.
    """
    try:
        from app.db.session import engine
        from app.models import Base

        tables_dropped = []

        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)

            # List dropped tables
            for table_name in Base.metadata.tables.keys():
                tables_dropped.append(table_name)

        return {
            "status": "success",
            "message": "Database tables dropped successfully",
            "tables": tables_dropped,
            "count": len(tables_dropped)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": error_trace
            }
        )


@router.post("/reset-database")
async def reset_database():
    """
    Drop all tables and recreate them.

    WARNING: This will delete all data! Use only in development.
    """
    try:
        from app.db.session import engine
        from app.models import Base

        tables = []

        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

            # List tables
            for table_name in Base.metadata.tables.keys():
                tables.append(table_name)

        return {
            "status": "success",
            "message": "Database reset successfully",
            "tables": tables,
            "count": len(tables)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": error_trace
            }
        )


@router.get("/check-tables")
async def check_tables():
    """
    Check which tables exist in the database.
    """
    try:
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import text

        async with AsyncSessionLocal() as db:
            # Query PostgreSQL system tables
            result = await db.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))

            existing_tables = [row[0] for row in result.fetchall()]

        from app.models import Base
        expected_tables = list(Base.metadata.tables.keys())

        return {
            "status": "success",
            "existing_tables": existing_tables,
            "expected_tables": expected_tables,
            "missing_tables": [t for t in expected_tables if t not in existing_tables],
            "extra_tables": [t for t in existing_tables if t not in expected_tables]
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "trace": error_trace
            }
        )
