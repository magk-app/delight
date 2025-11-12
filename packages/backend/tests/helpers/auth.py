"""
Authentication Test Helpers
Helper functions for testing Clerk authentication (Story 1.3)
"""

import jwt
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def create_mock_jwt_token(clerk_user_id: str, **claims) -> str:
    """
    Create mock Clerk JWT token for testing.

    Generates a JWT with the correct structure expected by get_current_user().
    Note: Does not verify signature in current implementation, but includes
    all required claims for future signature verification.

    Args:
        clerk_user_id: Clerk user ID (will be set as 'sub' claim)
        **claims: Additional JWT claims to include

    Returns:
        JWT token string

    Usage:
        token = create_mock_jwt_token("user_123")
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/protected", headers=headers)
    """
    payload = {
        "sub": clerk_user_id,  # Subject claim - Clerk user ID
        "aud": "test",  # Audience
        "iss": "https://clerk.test.dev",  # Issuer
        "iat": 1234567890,  # Issued at
        "exp": 9999999999,  # Expiration (far future for tests)
        **claims,  # Additional claims
    }

    # Encode JWT (no signature verification in test environment)
    token = jwt.encode(payload, key="test_secret", algorithm="HS256")
    return token


def create_auth_headers(clerk_user_id: str) -> Dict[str, str]:
    """
    Create authentication headers for testing protected endpoints.

    Args:
        clerk_user_id: Clerk user ID

    Returns:
        Dict with Authorization header

    Usage:
        headers = create_auth_headers("user_123")
        response = await client.get("/api/v1/users/me", headers=headers)
    """
    token = create_mock_jwt_token(clerk_user_id)
    return {"Authorization": f"Bearer {token}"}


async def create_test_user(
    db: AsyncSession,
    clerk_user_id: str,
    email: str | None = None,
    display_name: str | None = None,
    timezone: str = "UTC",
    **kwargs,
) -> User:
    """
    Create a test user in the database.

    Useful for setting up test data before testing protected endpoints.
    User will be automatically cleaned up via transaction rollback.

    Args:
        db: Database session
        clerk_user_id: Clerk user ID (required, unique)
        email: User email (optional)
        display_name: Display name (optional)
        timezone: User timezone (default: UTC)
        **kwargs: Additional User model fields

    Returns:
        Created User object

    Usage:
        user = await create_test_user(
            db_session,
            clerk_user_id="user_123",
            email="test@example.com",
            display_name="Test User"
        )
    """
    user = User(
        clerk_user_id=clerk_user_id,
        email=email,
        display_name=display_name,
        timezone=timezone,
        **kwargs,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


def mock_auth_dependency(user_id: str = "test_user_123") -> Dict[str, Any]:
    """
    Mock FastAPI auth dependency for testing.

    Use this to override the get_current_user dependency in tests
    that don't need actual JWT validation.

    Args:
        user_id: Mock user ID

    Returns:
        Dict mimicking User object

    Usage:
        from app.core.clerk_auth import get_current_user

        # In test
        app.dependency_overrides[get_current_user] = lambda: mock_auth_dependency()

        # Test runs with mocked auth
        response = await client.get("/api/v1/protected")

        # Cleanup
        app.dependency_overrides.clear()
    """
    return {
        "id": user_id,
        "email": f"{user_id}@example.com",
        "clerk_user_id": f"clerk_{user_id}",
    }
