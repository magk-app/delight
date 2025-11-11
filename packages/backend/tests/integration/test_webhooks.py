"""
Integration Tests: Clerk Webhooks (Story 1.3)

Tests for Clerk webhook handling:
- Signature verification (Svix)
- User creation (user.created)
- User updates (user.updated)
- Idempotency
- Error handling
"""

import hmac
import json
import time
from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def generate_svix_signature(payload: bytes, secret: str, timestamp: str) -> str:
    """
    Generate valid Svix webhook signature for testing.

    Svix uses HMAC-SHA256 with a specific format:
    msg_id.timestamp.payload -> base64(hmac-sha256(msg_id,timestamp,payload))

    Args:
        payload: Raw webhook payload bytes
        secret: Webhook secret (whsec_...)
        timestamp: Unix timestamp as string

    Returns:
        Signature in format: v1,signature1 v1,signature2
    """
    # Extract the base64 part of the secret (remove "whsec_" prefix)
    if secret.startswith("whsec_"):
        secret = secret[6:]

    # Svix signature format: f"{msg_id}.{timestamp}.{payload}"
    msg_id = "msg_test123"
    to_sign = f"{msg_id}.{timestamp}.{payload.decode('utf-8')}"

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret.encode(), to_sign.encode(), digestmod="sha256"
    ).hexdigest()

    # Svix format: "v1,signature"
    return f"v1,{signature}"


def create_webhook_headers(payload: Dict, secret: str) -> Dict[str, str]:
    """
    Create valid Svix webhook headers for testing.

    Args:
        payload: Webhook payload dict
        secret: Webhook secret

    Returns:
        Dict with svix-id, svix-timestamp, svix-signature headers
    """
    payload_bytes = json.dumps(payload).encode("utf-8")
    timestamp = str(int(time.time()))
    signature = generate_svix_signature(payload_bytes, secret, timestamp)

    return {
        "svix-id": "msg_test123",
        "svix-timestamp": timestamp,
        "svix-signature": signature,
        "Content-Type": "application/json",
    }


@pytest.mark.integration
@pytest.mark.webhooks
class TestWebhookSignatureValidation:
    """
    Test suite for Svix webhook signature verification.

    Security-critical: Only process webhooks with valid signatures.
    """

    async def test_webhook_with_valid_signature(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Valid signature should process webhook

        Given: Properly signed webhook payload
        When: POST /api/v1/webhooks/clerk
        Then: 200 OK, user created/updated
        """
        payload = {
            "type": "user.created",
            "data": {
                "id": "user_test_valid_sig_123",
                "email_addresses": [{"email_address": "valid@example.com"}],
                "first_name": "Valid",
                "last_name": "User",
            },
            "object": "event",
        }

        # Generate valid signature
        # Note: Uses test webhook secret from settings
        from app.core.config import settings

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Verify user was created
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == "user_test_valid_sig_123")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "valid@example.com"

    async def test_webhook_missing_svix_headers(self, client: AsyncClient):
        """
        Story 1.3: Missing Svix headers should return 400

        Given: Payload without required Svix headers
        When: POST /api/v1/webhooks/clerk
        Then: 400 Bad Request

        Security: Reject webhooks that can't be verified
        """
        payload = {
            "type": "user.created",
            "data": {"id": "user_test_123", "email_addresses": []},
            "object": "event",
        }

        # Send without Svix headers
        response = await client.post("/api/v1/webhooks/clerk", json=payload)

        assert response.status_code == 400
        assert "Missing webhook headers" in response.json()["detail"]

    async def test_webhook_invalid_signature(self, client: AsyncClient):
        """
        Story 1.3: Invalid signature should return 400

        Given: Payload with incorrect/fake signature
        When: POST /api/v1/webhooks/clerk
        Then: 400 Bad Request

        Security: Prevent webhook spoofing
        """
        payload = {
            "type": "user.created",
            "data": {"id": "user_test_123", "email_addresses": []},
            "object": "event",
        }

        # Use fake signature
        headers = {
            "svix-id": "msg_fake",
            "svix-timestamp": str(int(time.time())),
            "svix-signature": "v1,fakesignature123456",
            "Content-Type": "application/json",
        }

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 400
        assert "Invalid webhook signature" in response.json()["detail"]

    async def test_webhook_missing_svix_id(self, client: AsyncClient):
        """
        Story 1.3: Missing svix-id header should return 400

        Given: Payload missing svix-id header
        When: POST /api/v1/webhooks/clerk
        Then: 400 Bad Request
        """
        payload = {"type": "user.created", "data": {"id": "user_test_123"}}

        headers = {
            "svix-timestamp": str(int(time.time())),
            "svix-signature": "v1,signature",
        }

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 400

    async def test_webhook_missing_svix_timestamp(self, client: AsyncClient):
        """
        Story 1.3: Missing svix-timestamp header should return 400

        Given: Payload missing svix-timestamp header
        When: POST /api/v1/webhooks/clerk
        Then: 400 Bad Request
        """
        payload = {"type": "user.created", "data": {"id": "user_test_123"}}

        headers = {"svix-id": "msg_123", "svix-signature": "v1,signature"}

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 400

    async def test_webhook_missing_svix_signature(self, client: AsyncClient):
        """
        Story 1.3: Missing svix-signature header should return 400

        Given: Payload missing svix-signature header
        When: POST /api/v1/webhooks/clerk
        Then: 400 Bad Request
        """
        payload = {"type": "user.created", "data": {"id": "user_test_123"}}

        headers = {"svix-id": "msg_123", "svix-timestamp": str(int(time.time()))}

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.webhooks
class TestUserCreatedWebhook:
    """
    Test suite for user.created webhook events.

    Verifies user creation from Clerk webhook data.
    """

    async def test_user_created_creates_new_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: user.created webhook should create new user

        Given: user.created webhook for new user
        When: Webhook processed
        Then: User created in database with correct data
        """
        from app.core.config import settings

        clerk_user_id = "user_created_test_001"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "newuser@example.com"}],
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        # Verify user exists in database
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user is not None
        assert user.clerk_user_id == clerk_user_id
        assert user.email == "newuser@example.com"
        assert user.display_name == "New User"
        assert user.timezone == "UTC"  # Default

    async def test_user_created_extracts_primary_email(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Extract primary email from email_addresses array

        Given: Webhook with multiple email addresses
        When: User created
        Then: First email in array is set as user.email
        """
        from app.core.config import settings

        clerk_user_id = "user_email_test_002"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [
                    {"email_address": "primary@example.com"},
                    {"email_address": "secondary@example.com"},
                ],
                "first_name": "Email",
                "last_name": "Test",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        # Verify primary email extracted
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.email == "primary@example.com"

    async def test_user_created_constructs_display_name(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Construct display_name from first_name + last_name

        Given: Webhook with first_name and last_name
        When: User created
        Then: display_name is "FirstName LastName"
        """
        from app.core.config import settings

        clerk_user_id = "user_name_test_003"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "name@example.com"}],
                "first_name": "John",
                "last_name": "Doe",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.display_name == "John Doe"

    async def test_user_created_only_first_name(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Handle user with only first_name

        Given: Webhook with first_name but no last_name
        When: User created
        Then: display_name is just first_name
        """
        from app.core.config import settings

        clerk_user_id = "user_firstname_test_004"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "firstname@example.com"}],
                "first_name": "Alice",
                "last_name": None,
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.display_name == "Alice"

    async def test_user_created_falls_back_to_username(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Use username if no first/last name

        Given: Webhook without first_name/last_name but has username
        When: User created
        Then: display_name is username
        """
        from app.core.config import settings

        clerk_user_id = "user_username_test_005"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "username@example.com"}],
                "first_name": None,
                "last_name": None,
                "username": "cooluser123",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.display_name == "cooluser123"

    async def test_user_created_sets_default_timezone(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Default timezone should be UTC

        Given: New user webhook
        When: User created
        Then: timezone defaults to "UTC"
        """
        from app.core.config import settings

        clerk_user_id = "user_timezone_test_006"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "tz@example.com"}],
                "first_name": "Timezone",
                "last_name": "User",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.timezone == "UTC"

    async def test_user_created_handles_missing_email(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Handle user without email addresses

        Given: Webhook without email_addresses (or empty array)
        When: User created
        Then: email is None, user still created

        Edge case: OAuth users might not have email
        """
        from app.core.config import settings

        clerk_user_id = "user_no_email_test_007"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [],  # Empty array
                "first_name": "No",
                "last_name": "Email",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user is not None
        assert user.email is None
        assert user.display_name == "No Email"


@pytest.mark.integration
@pytest.mark.webhooks
class TestUserUpdatedWebhook:
    """
    Test suite for user.updated webhook events.

    Verifies user updates from Clerk webhook data.
    """

    async def test_user_updated_updates_existing_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: user.updated should update existing user

        Given: Existing user in database
        When: user.updated webhook received
        Then: User updated with new data
        """
        from app.core.config import settings
        from tests.helpers.auth import create_test_user

        # Create existing user
        clerk_user_id = "user_update_test_001"
        await create_test_user(
            db_session,
            clerk_user_id=clerk_user_id,
            email="old@example.com",
            display_name="Old Name",
        )

        # Send update webhook
        payload = {
            "type": "user.updated",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "new@example.com"}],
                "first_name": "New",
                "last_name": "Name",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 200

        # Verify user updated
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.email == "new@example.com"
        assert user.display_name == "New Name"

    async def test_user_updated_preserves_user_id(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Updates should not change user.id (UUID)

        Given: Existing user with specific UUID
        When: user.updated webhook
        Then: UUID unchanged, only mutable fields updated

        Critical: Internal ID must remain stable
        """
        from app.core.config import settings
        from tests.helpers.auth import create_test_user

        clerk_user_id = "user_preserve_id_002"
        original_user = await create_test_user(
            db_session,
            clerk_user_id=clerk_user_id,
            email="preserve@example.com",
        )
        original_uuid = original_user.id

        # Send update
        payload = {
            "type": "user.updated",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "updated@example.com"}],
                "first_name": "Updated",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        await client.post("/api/v1/webhooks/clerk", json=payload, headers=headers)

        # Verify UUID unchanged
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        updated_user = result.scalar_one_or_none()

        assert updated_user.id == original_uuid
        assert updated_user.email == "updated@example.com"


@pytest.mark.integration
@pytest.mark.webhooks
class TestWebhookIdempotency:
    """
    Test suite for webhook idempotency.

    Webhooks may be delivered multiple times - service must handle duplicates.
    """

    async def test_duplicate_user_created_events(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Duplicate user.created events should be idempotent

        Given: user.created webhook sent twice for same user
        When: Both webhooks processed
        Then: Only one user created, second treated as update

        Idempotency: Critical for webhook reliability
        """
        from app.core.config import settings

        clerk_user_id = "user_duplicate_001"
        payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "duplicate@example.com"}],
                "first_name": "Duplicate",
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        # Send first webhook
        response1 = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )
        assert response1.status_code == 200

        # Send duplicate (regenerate headers with new timestamp)
        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)
        response2 = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )
        assert response2.status_code == 200

        # Verify only one user exists
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        users = result.scalars().all()

        assert len(users) == 1
        assert users[0].email == "duplicate@example.com"

    async def test_user_created_then_updated(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: user.created followed by user.updated should work correctly

        Given: user.created webhook followed by user.updated
        When: Both processed in sequence
        Then: User created then updated correctly
        """
        from app.core.config import settings

        clerk_user_id = "user_sequence_002"

        # Create user
        create_payload = {
            "type": "user.created",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "create@example.com"}],
                "first_name": "Initial",
            },
            "object": "event",
        }

        headers = create_webhook_headers(create_payload, settings.CLERK_WEBHOOK_SECRET)
        response1 = await client.post(
            "/api/v1/webhooks/clerk", json=create_payload, headers=headers
        )
        assert response1.status_code == 200

        # Update user
        update_payload = {
            "type": "user.updated",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "updated@example.com"}],
                "first_name": "Updated",
            },
            "object": "event",
        }

        headers = create_webhook_headers(update_payload, settings.CLERK_WEBHOOK_SECRET)
        response2 = await client.post(
            "/api/v1/webhooks/clerk", json=update_payload, headers=headers
        )
        assert response2.status_code == 200

        # Verify final state
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.email == "updated@example.com"
        assert user.display_name == "Updated"

    async def test_multiple_updates_same_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Multiple updates to same user

        Given: Multiple user.updated webhooks in sequence
        When: All processed
        Then: Final state reflects last webhook
        """
        from app.core.config import settings
        from tests.helpers.auth import create_test_user

        clerk_user_id = "user_multi_update_003"
        await create_test_user(db_session, clerk_user_id=clerk_user_id)

        # Update 1
        payload1 = {
            "type": "user.updated",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "update1@example.com"}],
                "first_name": "Update1",
            },
            "object": "event",
        }
        headers1 = create_webhook_headers(payload1, settings.CLERK_WEBHOOK_SECRET)
        await client.post("/api/v1/webhooks/clerk", json=payload1, headers=headers1)

        # Update 2
        payload2 = {
            "type": "user.updated",
            "data": {
                "id": clerk_user_id,
                "email_addresses": [{"email_address": "update2@example.com"}],
                "first_name": "Update2",
            },
            "object": "event",
        }
        headers2 = create_webhook_headers(payload2, settings.CLERK_WEBHOOK_SECRET)
        await client.post("/api/v1/webhooks/clerk", json=payload2, headers=headers2)

        # Verify final state is from last update
        result = await db_session.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()

        assert user.email == "update2@example.com"
        assert user.display_name == "Update2"


@pytest.mark.integration
@pytest.mark.webhooks
class TestWebhookErrorHandling:
    """
    Test suite for webhook error scenarios.

    Verifies graceful handling of invalid payloads and system errors.
    """

    async def test_invalid_payload_format(self, client: AsyncClient):
        """
        Story 1.3: Malformed JSON should return 400

        Given: Invalid JSON payload
        When: Webhook processed
        Then: 400 Bad Request
        """
        from app.core.config import settings

        # Send invalid JSON (missing required fields)
        payload = {"type": "invalid"}  # Missing 'data' and 'object'

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        assert response.status_code == 400
        assert "Invalid payload format" in response.json()["detail"]

    async def test_unhandled_event_type_returns_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Story 1.3: Unhandled event types should return 200 (logged)

        Given: Valid webhook with unhandled event type
        When: Webhook processed
        Then: 200 OK (logged as unhandled, no error)

        Rationale: Clerk may add new event types - don't fail
        """
        from app.core.config import settings

        payload = {
            "type": "user.deleted",  # Not yet implemented
            "data": {
                "id": "user_deleted_test",
                "email_addresses": [],
            },
            "object": "event",
        }

        headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)

        response = await client.post(
            "/api/v1/webhooks/clerk", json=payload, headers=headers
        )

        # Should succeed but log as unhandled
        assert response.status_code == 200
        assert response.json()["status"] == "success"


# ============================================================================
# Test Helpers
# ============================================================================
# Webhook signature generation and header creation helpers are defined above:
# - generate_svix_signature()
# - create_webhook_headers()
# ============================================================================
