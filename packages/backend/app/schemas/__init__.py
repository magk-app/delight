"""Pydantic schemas for request/response validation"""

from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemoryWithDistance,
    MemoryQuery,
    MemorySimilarityQuery,
)
from app.schemas.agent_preferences import (
    AgentPreferencesCreate,
    AgentPreferencesUpdate,
    AgentPreferencesResponse,
)
from app.schemas.knowledge_graph import (
    KnowledgeEntityCreate,
    KnowledgeEntityUpdate,
    KnowledgeEntityResponse,
    KnowledgeEntityWithRelationships,
    KnowledgeRelationshipCreate,
    KnowledgeRelationshipUpdate,
    KnowledgeRelationshipResponse,
    EntitySearchQuery,
    GraphContextQuery,
    GraphContext,
)

__all__ = [
    # Memory schemas
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryResponse",
    "MemoryWithDistance",
    "MemoryQuery",
    "MemorySimilarityQuery",
    # Agent preferences schemas
    "AgentPreferencesCreate",
    "AgentPreferencesUpdate",
    "AgentPreferencesResponse",
    # Knowledge graph schemas
    "KnowledgeEntityCreate",
    "KnowledgeEntityUpdate",
    "KnowledgeEntityResponse",
    "KnowledgeEntityWithRelationships",
    "KnowledgeRelationshipCreate",
    "KnowledgeRelationshipUpdate",
    "KnowledgeRelationshipResponse",
    "EntitySearchQuery",
    "GraphContextQuery",
    "GraphContext",
]
