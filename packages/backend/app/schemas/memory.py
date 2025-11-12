"""
Pydantic schemas for Memory and MemoryCollection.
Used for request validation and response serialization in API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.memory import MemoryType


# ============================================================================
# Memory Schemas
# ============================================================================


class MemoryBase(BaseModel):
    """Base schema with common memory fields."""

    memory_type: MemoryType = Field(
        ...,
        description="Memory tier: personal (never pruned), project (goals), task (30-day pruning)",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Human-readable memory content",
    )
    # Using 'extra_data' to match SQLAlchemy model, but serialized as 'metadata' in JSON
    extra_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        alias="metadata",  # Accept 'metadata' in JSON input
        serialization_alias="metadata",  # Output as 'metadata' in JSON
        description="Flexible metadata: stressor info, emotion scores, goal references, etc.",
    )


class MemoryCreate(MemoryBase):
    """
    Schema for creating a new memory.

    Note: embedding is NOT included here as it will be generated
    server-side using OpenAI embeddings service in Story 2.2.
    """

    pass


class MemoryUpdate(BaseModel):
    """
    Schema for updating an existing memory.

    All fields optional to support partial updates.
    """

    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10000,
        description="Updated memory content",
    )
    # Using 'extra_data' to match SQLAlchemy model, but serialized as 'metadata' in JSON
    extra_data: Optional[Dict[str, Any]] = Field(
        None,
        alias="metadata",
        serialization_alias="metadata",
        description="Updated metadata",
    )


class MemoryResponse(MemoryBase):
    """
    Schema for memory responses from API.

    Includes database-generated fields (id, timestamps).
    embedding is included but may be None if not yet generated.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    embedding: Optional[List[float]] = Field(
        None,
        description="1536-dim vector embedding (None if not yet generated)",
    )
    created_at: datetime
    accessed_at: datetime


class MemoryWithDistance(MemoryResponse):
    """
    Extended response schema for similarity search results.

    Includes distance score from vector similarity query.
    """

    distance: float = Field(
        ...,
        description="Cosine distance from query vector (0=identical, 2=opposite)",
    )


# ============================================================================
# MemoryCollection Schemas
# ============================================================================


class MemoryCollectionBase(BaseModel):
    """Base schema with common collection fields."""

    collection_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Collection category: goal, stressor_log, preferences, etc.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable collection name",
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional description of collection purpose",
    )


class MemoryCollectionCreate(MemoryCollectionBase):
    """Schema for creating a new memory collection."""

    pass


class MemoryCollectionUpdate(BaseModel):
    """
    Schema for updating an existing collection.

    All fields optional to support partial updates.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated collection name",
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Updated description",
    )


class MemoryCollectionResponse(MemoryCollectionBase):
    """
    Schema for collection responses from API.

    Includes database-generated fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime


# ============================================================================
# Query Schemas
# ============================================================================


class MemoryQuery(BaseModel):
    """
    Schema for querying memories with filters.

    Used in Story 2.2 for memory service implementation.
    """

    memory_type: Optional[MemoryType] = Field(
        None,
        description="Filter by memory tier",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of memories to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of memories to skip (pagination)",
    )


class MemorySimilarityQuery(BaseModel):
    """
    Schema for semantic similarity search.

    Used in Story 2.2 for vector-based memory retrieval.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language query to find similar memories",
    )
    memory_type: Optional[MemoryType] = Field(
        None,
        description="Filter by memory tier (optional)",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of similar memories to return",
    )
    threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Maximum distance threshold (0=identical, 2=opposite)",
    )
