"""
Clerk user synchronization service.
Handles creating and updating users from Clerk webhook events.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.webhook import ClerkUserData


class ClerkService:
    """Service for Clerk user lifecycle management."""

    @staticmethod
    async def create_or_update_user(
        db: AsyncSession, clerk_data: ClerkUserData
    ) -> User:
        """
        Create or update user from Clerk webhook data.
        Idempotent operation - safe to call multiple times with same data.

        Args:
            db: Database session
            clerk_data: User data from Clerk webhook

        Returns:
            User: Created or updated user record
        """
        # Extract email (primary email address)
        email = None
        if clerk_data.email_addresses:
            email = clerk_data.email_addresses[0].email_address

        # Construct display name from first_name + last_name
        display_name = None
        if clerk_data.first_name or clerk_data.last_name:
            parts = filter(None, [clerk_data.first_name, clerk_data.last_name])
            display_name = " ".join(parts)

        # If no display_name but has username, use that
        if not display_name and clerk_data.username:
            display_name = clerk_data.username

        # Check if user exists
        result = await db.execute(
            select(User).where(User.clerk_user_id == clerk_data.id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Update existing user
            user.email = email
            user.display_name = display_name
        else:
            # Create new user
            user = User(
                clerk_user_id=clerk_data.id,
                email=email,
                display_name=display_name,
                timezone="UTC",  # Default timezone, can be updated later
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)
        return user
