"""
Data Factories for Test Data Generation
Uses Faker for realistic test data with auto-cleanup
"""

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from uuid import uuid4

fake = Faker()


class UserFactory:
    """
    Factory for creating test users
    
    Usage:
        async def test_user_creation(db_session):
            factory = UserFactory(db_session)
            user = await factory.create_user(email="custom@example.com")
            assert user.email == "custom@example.com"
            # Cleanup automatic via transaction rollback
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.created_ids = []
    
    async def create_user(self, **overrides) -> Dict[str, Any]:
        """
        Create test user with optional field overrides
        
        Args:
            **overrides: Override default values (email, clerk_user_id, etc.)
        
        Returns:
            User model instance
        """
        user_data = {
            "id": uuid4(),
            "clerk_user_id": fake.uuid4(),
            "email": fake.email(),
            "timezone": "UTC",
            **overrides,
        }
        
        # TODO: Replace with actual User model when Story 1.2 is complete
        # from app.models.user import User
        # user = User(**user_data)
        # self.db_session.add(user)
        # await self.db_session.commit()
        # await self.db_session.refresh(user)
        # self.created_ids.append(user.id)
        # return user
        
        # For now, return dict (update after models exist)
        return user_data
    
    async def create_batch(self, count: int, **overrides) -> list:
        """Create multiple users"""
        return [await self.create_user(**overrides) for _ in range(count)]


class QuestFactory:
    """
    Factory for creating test quests
    
    Usage:
        async def test_quest_creation(db_session):
            factory = QuestFactory(db_session)
            quest = await factory.create_quest(
                user_id=user_id,
                title="Learn Python"
            )
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.created_ids = []
    
    async def create_quest(self, user_id: str, **overrides) -> Dict[str, Any]:
        """
        Create test quest with optional field overrides
        
        Args:
            user_id: User who owns the quest
            **overrides: Override default values
        
        Returns:
            Quest model instance
        """
        quest_data = {
            "id": uuid4(),
            "user_id": user_id,
            "title": fake.sentence(nb_words=4),
            "description": fake.paragraph(),
            "type": "short_term",
            "status": "active",
            **overrides,
        }
        
        # TODO: Replace with actual Quest model when Story 3.1 is complete
        # from app.models.quest import Quest
        # quest = Quest(**quest_data)
        # self.db_session.add(quest)
        # await self.db_session.commit()
        # await self.db_session.refresh(quest)
        # self.created_ids.append(quest.id)
        # return quest
        
        # For now, return dict (update after models exist)
        return quest_data

