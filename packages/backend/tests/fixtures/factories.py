"""
Data Factories for Test Data Generation
Uses Faker for realistic test data with auto-cleanup
"""

from typing import Any, Dict, List, Tuple
from uuid import uuid4

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserPreferences

fake = Faker()


class UserFactory:
    """
    Factory for creating test users backed by actual ORM models.

    Usage:
        async def test_user_creation(db_session):
            factory = UserFactory(db_session)
            user = await factory.create_user(email="custom@example.com")
            assert user.email == "custom@example.com"
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, **overrides) -> User:
        """
        Create test user with optional field overrides.

        Args:
            **overrides: Override default values (email, clerk_user_id, etc.)

        Returns:
            Persisted User instance.
        """
        user_data = {
            "clerk_user_id": overrides.pop("clerk_user_id", fake.uuid4()),
            "email": overrides.pop("email", fake.email()),
            "timezone": overrides.pop("timezone", "UTC"),
        }
        user_kwargs = {**user_data, **overrides}
        user = User(**user_kwargs)
        self.db_session.add(user)
        await self.db_session.flush()
        await self.db_session.refresh(user)
        return user

    async def create_user_with_preferences(
        self,
        preferences: Dict[str, Any] | None = None,
        **user_overrides,
    ) -> Tuple[User, UserPreferences]:
        """
        Create a user plus a one-to-one preferences record.

        Args:
            preferences: Optional overrides for UserPreferences fields.
            **user_overrides: Overrides for the user record.

        Returns:
            (User, UserPreferences)
        """
        user = await self.create_user(**user_overrides)
        pref_data = {
            "user_id": user.id,
            "theme": "modern",
            "custom_hours": {
                "start": "09:00",
                "end": "17:00",
                "timezone": "UTC",
            },
            "communication_preferences": {"email": True, "sms": False, "in_app": True},
            "onboarding_completed": False,
        }
        if preferences:
            pref_data.update(preferences)

        prefs = UserPreferences(**pref_data)
        self.db_session.add(prefs)
        await self.db_session.flush()
        await self.db_session.refresh(prefs)
        return user, prefs

    async def create_batch(self, count: int, **overrides) -> List[User]:
        """Create multiple users."""
        return [await self.create_user(**overrides) for _ in range(count)]


class QuestFactory:
    """
    Placeholder factory for future quest models.
    Currently returns dictionaries until Story 3.1 lands.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_quest(self, user_id: str, **overrides) -> Dict[str, Any]:
        quest_data = {
            "id": uuid4(),
            "user_id": user_id,
            "title": fake.sentence(nb_words=4),
            "description": fake.paragraph(),
            "type": "short_term",
            "status": "active",
            **overrides,
        }
        return quest_data
