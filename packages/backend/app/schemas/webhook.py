"""
Pydantic schemas for Clerk webhook payloads.
"""

from typing import Literal

from pydantic import BaseModel


class ClerkEmailAddress(BaseModel):
    """Clerk email address object."""

    email_address: str
    id: str | None = None
    verification: dict | None = None


class ClerkUserData(BaseModel):
    """Clerk user data from webhook."""

    id: str  # clerk_user_id
    email_addresses: list[ClerkEmailAddress]
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    profile_image_url: str | None = None
    created_at: int | None = None
    updated_at: int | None = None


class ClerkWebhookPayload(BaseModel):
    """Clerk webhook event payload."""

    type: Literal["user.created", "user.updated", "user.deleted"]
    data: ClerkUserData
    object: Literal["event"] = "event"
