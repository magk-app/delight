"""
Pydantic schemas for user-related API responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User profile response schema."""

    id: UUID
    clerk_user_id: str
    email: str | None
    display_name: str | None
    timezone: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
