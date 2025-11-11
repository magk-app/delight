"""
Integration Tests: Authentication System (Story 1.3)

Tests for Clerk authentication:
- get_current_user() dependency
- Token validation
- Protected endpoints
- Error handling
"""

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.helpers.auth import create_mock_jwt_token, create_test_user


@pytest.mark.integration
@pytest.mark.auth
class TestGetCurrentUser:
    """
    Test suite for get_current_user() authentication dependency.

    This dependency validates JWT tokens and loads authenticated users.
    Security is critical - test both success and failure cases.
    """

    async def test_get_current_user_with_valid_token(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Valid token should return authenticated user

        Given: User exists in database with clerk_user_id
        When: Request with valid JWT token containing matching clerk_user_id
        Then: get_current_user() returns User object
        """
        # Create test user
        clerk_user_id = "user_test_valid_token_123"
        user = await create_test_user(
            db_session,
            clerk_user_id=clerk_user_id,
            email="valid@example.com",
            display_name="Valid User",
        )

        # Create valid JWT token
        token = create_mock_jwt_token(clerk_user_id)

        # Make request to protected endpoint
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["clerk_user_id"] == clerk_user_id
        assert data["email"] == "valid@example.com"
        assert data["display_name"] == "Valid User"

    async def test_get_current_user_missing_authorization_header(
        self, client: AsyncClient
    ):
        """
        Story 1.3: Missing Authorization header should return 403

        Given: No Authorization header
        When: Request to protected endpoint
        Then: 403 Forbidden with WWW-Authenticate header
        """
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 403
        assert response.json()["detail"] == "Missing Authorization header"
        # Should include WWW-Authenticate header per OAuth 2.0 spec
        assert "WWW-Authenticate" in response.headers

    async def test_get_current_user_invalid_bearer_scheme(self, client: AsyncClient):
        """
        Story 1.3: Invalid authorization scheme should return 401

        Given: Authorization header without "Bearer " prefix
        When: Request to protected endpoint
        Then: 401 Unauthorized
        """
        # Try with "Basic" scheme instead of "Bearer"
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": "Basic user:pass"}
        )

        assert response.status_code == 401
        assert "Invalid authorization scheme" in response.json()["detail"]

    async def test_get_current_user_empty_token(self, client: AsyncClient):
        """
        Story 1.3: Empty token should return 401

        Given: "Bearer " with no token
        When: Request to protected endpoint
        Then: 401 Unauthorized
        """
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": "Bearer "}
        )

        assert response.status_code == 401
        assert response.json()["detail"] in [
            "Invalid token format",
            "Invalid authentication credentials",
        ]

    async def test_get_current_user_malformed_token(self, client: AsyncClient):
        """
        Story 1.3: Malformed JWT should return 401

        Given: Invalid JWT format (not base64, missing parts)
        When: Request with malformed token
        Then: 401 Unauthorized
        """
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer not.a.valid.jwt.token"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] in [
            "Invalid token format",
            "Invalid authentication credentials",
        ]

    async def test_get_current_user_token_missing_sub_claim(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: JWT without 'sub' claim should return 401

        Given: Valid JWT structure but missing 'sub' (user ID) claim
        When: Request with incomplete token
        Then: 401 Unauthorized

        Security: Prevents authentication with incomplete tokens
        """
        # Create JWT without 'sub' claim
        token = jwt.encode(
            {"aud": "test", "iat": 1234567890}, key="secret", algorithm="HS256"
        )

        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token format"

    async def test_get_current_user_not_in_database(self, client: AsyncClient):
        """
        Story 1.3: Valid token but user not in DB should return 401

        Given: Valid JWT with clerk_user_id not in database
        When: Request with token for non-existent user
        Then: 401 Unauthorized (not 404 to prevent user enumeration)

        Security: Returns 401 instead of 404 to prevent attackers from
        discovering which user IDs exist in the system.
        """
        # Create token for user that doesn't exist
        clerk_user_id = "user_does_not_exist_999"
        token = create_mock_jwt_token(clerk_user_id)

        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        # Should be 401, not 404 (security best practice)
        assert response.status_code == 401
        assert response.json()["detail"] == "User not found in database"

    async def test_get_current_user_with_special_characters_in_id(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Handle clerk_user_id with special characters

        Given: User with clerk_user_id containing special characters
        When: Request with valid token
        Then: Successfully authenticates

        Edge case: Clerk IDs can contain underscores, hyphens, etc.
        """
        clerk_user_id = "user_test-special_chars.123"
        await create_test_user(
            db_session,
            clerk_user_id=clerk_user_id,
            email="special@example.com",
        )

        token = create_mock_jwt_token(clerk_user_id)

        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["clerk_user_id"] == clerk_user_id


@pytest.mark.integration
@pytest.mark.api
class TestProtectedEndpoints:
    """
    Test suite for protected API endpoints.

    Verifies that authentication is correctly applied to protected routes.
    """

    async def test_get_me_endpoint_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: /api/v1/users/me should return authenticated user profile

        Given: Authenticated user
        When: GET /api/v1/users/me
        Then: Returns complete user profile
        """
        clerk_user_id = "user_test_get_me_123"
        await create_test_user(
            db_session,
            clerk_user_id=clerk_user_id,
            email="getme@example.com",
            display_name="Get Me User",
            timezone="America/Los_Angeles",
        )

        token = create_mock_jwt_token(clerk_user_id)

        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["clerk_user_id"] == clerk_user_id
        assert data["email"] == "getme@example.com"
        assert data["display_name"] == "Get Me User"
        assert data["timezone"] == "America/Los_Angeles"
        assert "created_at" in data
        assert "updated_at" in data

    async def test_get_me_endpoint_unauthenticated(self, client: AsyncClient):
        """
        Story 1.3: Unauthenticated request should be rejected

        Given: No authentication credentials
        When: GET /api/v1/users/me
        Then: 403 Forbidden
        """
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 403
        assert "Missing Authorization header" in response.json()["detail"]

    async def test_get_me_endpoint_returns_correct_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Endpoint should return only the authenticated user's data

        Given: Multiple users in database
        When: Authenticated request from user A
        Then: Returns only user A's data, not user B's

        Security: Verify no data leakage between users
        """
        # Create two users
        user_a_clerk_id = "user_a_123"
        user_b_clerk_id = "user_b_456"

        await create_test_user(
            db_session,
            clerk_user_id=user_a_clerk_id,
            email="usera@example.com",
            display_name="User A",
        )

        await create_test_user(
            db_session,
            clerk_user_id=user_b_clerk_id,
            email="userb@example.com",
            display_name="User B",
        )

        # Authenticate as user A
        token = create_mock_jwt_token(user_a_clerk_id)

        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should return User A's data only
        assert data["clerk_user_id"] == user_a_clerk_id
        assert data["email"] == "usera@example.com"
        assert data["display_name"] == "User A"

        # Should NOT contain User B's data
        assert data["email"] != "userb@example.com"

    async def test_get_me_endpoint_with_minimal_user_data(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Handle users with minimal profile data

        Given: User with only required fields (clerk_user_id)
        When: GET /api/v1/users/me
        Then: Returns user with null optional fields

        Edge case: User might not have email or display_name yet
        """
        clerk_user_id = "user_minimal_123"
        await create_test_user(
            db_session,
            clerk_user_id=clerk_user_id,
            email=None,  # Optional
            display_name=None,  # Optional
        )

        token = create_mock_jwt_token(clerk_user_id)

        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["clerk_user_id"] == clerk_user_id
        assert data["email"] is None
        assert data["display_name"] is None
        assert data["timezone"] == "UTC"  # Default value


# ============================================================================
# Performance and Load Tests (Optional)
# ============================================================================


@pytest.mark.skip(reason="Performance tests - run manually")
@pytest.mark.performance
class TestAuthenticationPerformance:
    """
    Optional performance tests for authentication system.

    Run manually to verify auth dependency doesn't add excessive latency.
    """

    async def test_auth_latency_under_50ms(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Authentication should add minimal latency

        Target: Auth dependency adds < 50ms overhead
        """
        import time

        clerk_user_id = "user_perf_test_123"
        await create_test_user(db_session, clerk_user_id=clerk_user_id)
        token = create_mock_jwt_token(clerk_user_id)

        # Warm up
        await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        # Measure 10 requests
        start = time.perf_counter()
        for _ in range(10):
            await client.get(
                "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
            )
        end = time.perf_counter()

        avg_latency_ms = ((end - start) / 10) * 1000
        assert avg_latency_ms < 50, f"Auth latency too high: {avg_latency_ms:.2f}ms"


# ============================================================================
# Test Helpers
# ============================================================================
# See tests/helpers/auth.py for:
# - create_mock_jwt_token()
# - create_test_user()
# ============================================================================
