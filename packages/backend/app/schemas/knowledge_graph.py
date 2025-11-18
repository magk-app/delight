"""
Pydantic schemas for KnowledgeGraph (entities and relationships).
Used for request validation and response serialization in API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.knowledge_graph import EntityType, RelationshipType


# ============================================================================
# KnowledgeEntity Schemas
# ============================================================================


class KnowledgeEntityBase(BaseModel):
    """Base schema for knowledge entities"""

    entity_type: EntityType = Field(
        ...,
        description="Category of this entity",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable entity name",
    )
    description: Optional[str] = Field(
        None,
        description="Optional description or context for this entity",
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible entity attributes (deadline, progress, etc.)",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this entity's existence/accuracy",
    )


class KnowledgeEntityCreate(KnowledgeEntityBase):
    """Schema for creating a knowledge entity"""

    source_memory_id: Optional[UUID] = Field(
        None,
        description="Original memory that introduced this entity",
    )


class KnowledgeEntityUpdate(BaseModel):
    """Schema for updating a knowledge entity (partial updates allowed)"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class KnowledgeEntityResponse(KnowledgeEntityBase):
    """Schema for knowledge entity responses from API"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    embedding: Optional[List[float]] = Field(
        None,
        description="1536-dim vector embedding (None if not yet generated)",
    )
    source_memory_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class KnowledgeEntityWithRelationships(KnowledgeEntityResponse):
    """Extended entity response with related entities"""

    outgoing_relationships: List["RelationshipInfo"] = Field(
        default=[],
        description="Relationships from this entity to others",
    )
    incoming_relationships: List["RelationshipInfo"] = Field(
        default=[],
        description="Relationships to this entity from others",
    )


# ============================================================================
# KnowledgeRelationship Schemas
# ============================================================================


class KnowledgeRelationshipBase(BaseModel):
    """Base schema for knowledge relationships"""

    relationship_type: RelationshipType = Field(
        ...,
        description="Type of relationship between entities",
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relationship attributes (strength, context, etc.)",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this relationship's accuracy",
    )


class KnowledgeRelationshipCreate(KnowledgeRelationshipBase):
    """Schema for creating a knowledge relationship"""

    from_entity_id: UUID = Field(
        ...,
        description="Source entity in the relationship",
    )
    to_entity_id: UUID = Field(
        ...,
        description="Target entity in the relationship",
    )
    source_memory_id: Optional[UUID] = Field(
        None,
        description="Memory that established this relationship",
    )


class KnowledgeRelationshipUpdate(BaseModel):
    """Schema for updating a knowledge relationship (partial updates allowed)"""

    properties: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class KnowledgeRelationshipResponse(KnowledgeRelationshipBase):
    """Schema for knowledge relationship responses from API"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    from_entity_id: UUID
    to_entity_id: UUID
    source_memory_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class RelationshipInfo(BaseModel):
    """Simplified relationship info for entity context"""

    relationship_id: UUID
    relationship_type: RelationshipType
    related_entity_id: UUID
    related_entity_name: str
    related_entity_type: EntityType
    properties: Dict[str, Any]
    confidence: float


# ============================================================================
# Graph Query Schemas
# ============================================================================


class EntitySearchQuery(BaseModel):
    """Query parameters for entity search"""

    entity_type: Optional[EntityType] = Field(
        None,
        description="Filter by entity type",
    )
    search_text: Optional[str] = Field(
        None,
        description="Search in entity names and descriptions",
    )
    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity for semantic search",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results to return",
    )


class GraphContextQuery(BaseModel):
    """Query parameters for getting entity context with relationships"""

    entity_id: UUID = Field(
        ...,
        description="Entity to get context for",
    )
    max_depth: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum relationship depth to traverse",
    )
    relationship_types: Optional[List[RelationshipType]] = Field(
        None,
        description="Filter by relationship types (None = all types)",
    )


class GraphContext(BaseModel):
    """Complete context for an entity including relationships"""

    entity: KnowledgeEntityResponse
    relationships: Dict[str, List[RelationshipInfo]] = Field(
        description="Organized by direction: outgoing, incoming"
    )
    related_entities: List[KnowledgeEntityResponse] = Field(
        description="All entities connected to this one"
    )


# Update forward references
KnowledgeEntityWithRelationships.model_rebuild()
