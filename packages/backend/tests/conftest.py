"""
Test Configuration and Fixtures
Root conftest.py providing shared fixtures for all tests
"""

import importlib
import os
from typing import AsyncGenerator

# Ensure tests default to an isolated database (can override with TEST_DATABASE_URL).
_test_db_url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["TEST_DATABASE_URL"] = _test_db_url
os.environ["DATABASE_URL"] = _test_db_url

# Reload database session module so engine picks up the test database URL.
import app.db.session as _db_session_module

importlib.reload(_db_session_module)

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import NullPool

# Import your FastAPI app and database dependencies
from app.core.config import settings
from app.db.base import Base
from main import app as fastapi_app

# Import all models so they're registered with Base.metadata
# This is required for create_all() to work
from app.models.user import User, UserPreferences  # noqa: F401


# ---------------------------------------------------------------------------
# Dialect fallbacks so PostgreSQL types compile on SQLite during local tests.
# ---------------------------------------------------------------------------


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(element, compiler, **kw):
    return "CHAR(36)"


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "TEXT"


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """
    Test database URL - isolated from development database.

    Set TEST_DATABASE_URL to point at a dedicated PostgreSQL test database.
    Defaults to in-memory SQLite with PostgreSQL type fallbacks for local runs.
    """
    return os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest_asyncio.fixture(scope="session")
async def async_engine(test_database_url: str):
    """
    Create async database engine for tests

    Uses NullPool to prevent connection sharing across async tasks.
    For SQLite in-memory, we need to use a file-based DB to share tables across connections.
    """
    # For SQLite in-memory, we need to ensure all connections share the same database
    # Using a file-based SQLite DB for tests is more reliable
    temp_db_file = None
    if test_database_url.startswith("sqlite"):
        # Use a file-based SQLite DB instead of :memory: for better connection handling
        # This ensures all connections see the same tables
        if ":memory:" in test_database_url:
            import tempfile
            # Create a temporary file-based SQLite database
            temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            temp_db.close()
            temp_db_file = temp_db.name
            test_database_url = f"sqlite+aiosqlite:///{temp_db_file}"
        
        engine = create_async_engine(
            test_database_url,
            poolclass=NullPool,
            connect_args={"check_same_thread": False} if "aiosqlite" in test_database_url else {},
            echo=False,  # Set to True for SQL debugging
        )
    else:
        engine = create_async_engine(
            test_database_url,
            poolclass=NullPool,
            echo=False,
        )
    
    # Create all tables once at session start
    # Import models to ensure they're registered
    from app.models.user import User, UserPreferences  # noqa: F401
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup: drop tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    
    # Clean up temp file if it exists
    if temp_db_file and os.path.exists(temp_db_file):
        try:
            os.unlink(temp_db_file)
        except Exception:
            pass  # Ignore cleanup errors


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide database session with automatic transaction rollback

    Pattern: Each test runs in a transaction that is rolled back after test completes.
    This ensures test isolation without manual cleanup.
    
    Tables are created once at session scope, and each test uses a transaction
    that gets rolled back, so tests don't interfere with each other.

    Usage:
        async def test_create_user(db_session):
            user = User(email="test@example.com")
            db_session.add(user)
            await db_session.commit()
            # Transaction automatically rolled back after test
    """
    # Create session factory
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    # Create session and run test in a transaction
    async with async_session_maker() as session:
        # Start a savepoint transaction for this test
        trans = await session.begin()
        try:
            yield session
        finally:
            # Rollback transaction to clean up test data
            # This ensures each test starts with a clean state
            await trans.rollback()
            await session.close()


# ============================================================================
# FastAPI Test Client Fixtures
# ============================================================================


@pytest.fixture
def app() -> FastAPI:
    """FastAPI application instance"""
    return fastapi_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client for API testing

    Usage:
        async def test_health_check(client):
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
    """
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def mock_clerk_user():
    """Mock Clerk user object for auth tests"""
    return {
        "id": "user_test123",
        "email_addresses": [{"email_address": "test@example.com"}],
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def auth_headers(mock_clerk_user):
    """
    Mock authentication headers for protected endpoints

    Usage:
        async def test_protected_endpoint(client, auth_headers):
            response = await client.get("/api/v1/protected", headers=auth_headers)
            assert response.status_code == 200
    """
    # In real tests, this would generate a valid Clerk JWT
    # For now, return mock headers (update when auth is implemented)
    return {"Authorization": f"Bearer mock_token_{mock_clerk_user['id']}"}


# ============================================================================
# Test Data Cleanup
# ============================================================================


@pytest.fixture(autouse=True)
def reset_test_state():
    """
    Automatically reset test state before each test

    Add cleanup logic here as needed (e.g., clear Redis cache)
    """
    # Setup
    yield
    # Teardown
    pass
