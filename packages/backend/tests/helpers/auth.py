"""
Authentication Test Helpers
Mock authentication for testing protected endpoints
"""

from typing import Dict, Any


def create_mock_clerk_token(user_id: str, **claims) -> str:
    """
    Create mock Clerk JWT token for testing

    Args:
        user_id: Clerk user ID
        **claims: Additional JWT claims

    Returns:
        Mock JWT token string

    Usage:
        token = create_mock_clerk_token("user_123")
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/protected", headers=headers)
    """
    # TODO: Generate actual JWT when Story 1.3 auth is implemented
    # For now, return simple mock token
    return f"mock_token_{user_id}"


def mock_auth_dependency(user_id: str = "test_user_123") -> Dict[str, Any]:
    """
    Mock FastAPI auth dependency for testing

    Usage:
        from fastapi import Depends
        from app.core.dependencies import get_current_user

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
