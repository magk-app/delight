"""
Database models package.
Imports all models to register them with SQLAlchemy Base.
"""

from app.db.base import Base
from app.models.user import User, UserPreferences
from app.models.memory import Memory, MemoryCollection, MemoryType
from app.models.user_preferences import (
    AgentPreferences,
    ModelPreference,
    ReasoningDepth,
    InteractionStyle,
)
from app.models.knowledge_graph import (
    KnowledgeEntity,
    KnowledgeRelationship,
    EntityType,
    RelationshipType,
)

__all__ = [
    "Base",
    "User",
    "UserPreferences",
    "AgentPreferences",
    "Memory",
    "MemoryCollection",
    "MemoryType",
    "ModelPreference",
    "ReasoningDepth",
    "InteractionStyle",
    "KnowledgeEntity",
    "KnowledgeRelationship",
    "EntityType",
    "RelationshipType",
]
