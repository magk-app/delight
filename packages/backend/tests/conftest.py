"""
Test Configuration and Fixtures
Root conftest.py providing shared fixtures for all tests
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

# Import your FastAPI app and database dependencies
from app.db.base import Base
from main import app as fastapi_app


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """
    Test database URL - isolated from development database
    
    Uses in-memory SQLite for fast tests. For PostgreSQL-specific features,
    override this fixture in specific test files.
    """
    # SQLite in-memory database (fast, isolated)
    return "sqlite+aiosqlite:///:memory:"
    
    # Alternative: PostgreSQL test database (use for pgvector tests)
    # return "postgresql+asyncpg://postgres:postgres@localhost:5432/delight_test"


@pytest.fixture(scope="session")
def async_engine(test_database_url: str):
    """
    Create async database engine for tests
    
    Uses NullPool to prevent connection sharing across async tasks
    """
    engine = create_async_engine(
        test_database_url,
        poolclass=NullPool,  # Disable connection pooling for tests
        echo=False,  # Set to True for SQL debugging
    )
    return engine


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide database session with automatic transaction rollback
    
    Pattern: Each test runs in a transaction that is rolled back after test completes.
    This ensures test isolation without manual cleanup.
    
    Usage:
        async def test_create_user(db_session):
            user = User(email="test@example.com")
            db_session.add(user)
            await db_session.commit()
            # Transaction automatically rolled back after test
    """
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session with transaction
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        async with session.begin():
            yield session
            # Transaction automatically rolled back
    
    # Drop all tables after test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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
    async with AsyncClient(app=app, base_url="http://test") as ac:
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
    return {
        "Authorization": f"Bearer mock_token_{mock_clerk_user['id']}"
    }


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

