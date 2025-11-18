"""
Pydantic schemas for knowledge graph models.

Defines request/response schemas for knowledge nodes, edges, and associations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.memory import EdgeType, NodeType


# ============================================================================
# Knowledge Node Schemas
# ============================================================================


class KnowledgeNodeBase(BaseModel):
    """Base schema for knowledge node attributes."""

    node_type: NodeType = Field(..., description="Node category")
    name: str = Field(..., min_length=1, max_length=255, description="Node name")
    description: Optional[str] = Field(None, description="Optional description")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Flexible metadata",
        alias="extra_data",
        serialization_alias="metadata",
    )
    importance_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Node importance (0-1)",
    )


class KnowledgeNodeCreate(KnowledgeNodeBase):
    """Schema for creating a knowledge node."""

    embedding: Optional[List[float]] = Field(
        None,
        description="Optional 1536-dim embedding vector",
    )

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimensions(cls, v):
        """Validate embedding has exactly 1536 dimensions."""
        if v is not None and len(v) != 1536:
            raise ValueError("Embedding must be exactly 1536 dimensions")
        return v


class KnowledgeNodeUpdate(BaseModel):
    """Schema for updating a knowledge node."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        alias="extra_data",
        serialization_alias="metadata",
    )
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimensions(cls, v):
        """Validate embedding has exactly 1536 dimensions."""
        if v is not None and len(v) != 1536:
            raise ValueError("Embedding must be exactly 1536 dimensions")
        return v


class KnowledgeNodeResponse(KnowledgeNodeBase):
    """Schema for knowledge node response."""

    id: UUID
    user_id: UUID
    embedding: Optional[List[float]] = Field(
        None,
        description="1536-dim embedding vector (omitted if None)",
    )
    access_count: int = Field(..., description="Number of accesses")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeNodeWithScore(KnowledgeNodeResponse):
    """Knowledge node with relevance score (for search results)."""

    score: float = Field(..., description="Relevance score (0-1)")


# ============================================================================
# Knowledge Edge Schemas
# ============================================================================


class KnowledgeEdgeBase(BaseModel):
    """Base schema for knowledge edge attributes."""

    edge_type: EdgeType = Field(..., description="Relationship type")
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relationship strength (0-1)",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Flexible metadata",
        alias="extra_data",
        serialization_alias="metadata",
    )


class KnowledgeEdgeCreate(KnowledgeEdgeBase):
    """Schema for creating a knowledge edge."""

    source_node_id: UUID = Field(..., description="Source node UUID")
    target_node_id: UUID = Field(..., description="Target node UUID")

    @field_validator("target_node_id")
    @classmethod
    def validate_not_self_loop(cls, v, info):
        """Prevent self-loops (node pointing to itself)."""
        if info.data.get("source_node_id") == v:
            raise ValueError("Edge cannot connect a node to itself")
        return v


class KnowledgeEdgeUpdate(BaseModel):
    """Schema for updating a knowledge edge."""

    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        alias="extra_data",
        serialization_alias="metadata",
    )


class KnowledgeEdgeResponse(KnowledgeEdgeBase):
    """Schema for knowledge edge response."""

    id: UUID
    user_id: UUID
    source_node_id: UUID
    target_node_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Memory-Node Association Schemas
# ============================================================================


class MemoryNodeAssociationCreate(BaseModel):
    """Schema for creating a memory-node association."""

    memory_id: UUID = Field(..., description="Memory UUID")
    node_id: UUID = Field(..., description="Knowledge node UUID")
    relevance_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How relevant memory is to node (0-1)",
    )


class MemoryNodeAssociationResponse(BaseModel):
    """Schema for memory-node association response."""

    id: UUID
    memory_id: UUID
    node_id: UUID
    relevance_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Search/Retrieval Schemas
# ============================================================================


class HierarchicalSearchRequest(BaseModel):
    """Schema for hierarchical search request."""

    query: str = Field(..., min_length=1, description="Search query")
    memory_type: Optional[str] = Field(
        None,
        description="Optional filter for memory type (personal/project/task)",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of results",
    )
    node_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of nodes to consider in Step 1",
    )


class GraphGuidedSearchRequest(BaseModel):
    """Schema for graph-guided search request."""

    query: str = Field(..., min_length=1, description="Search query")
    expand_depth: int = Field(
        default=1,
        ge=0,
        le=3,
        description="How many hops to traverse (0=direct, 1=neighbors, 2=2-hop)",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of results",
    )


class HybridSearchRequest(BaseModel):
    """Schema for hybrid search request."""

    query: str = Field(..., min_length=1, description="Search query")
    metadata_filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata filters",
    )
    memory_type: Optional[str] = Field(
        None,
        description="Optional filter for memory type",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of results",
    )


class FindNodesRequest(BaseModel):
    """Schema for finding relevant nodes."""

    query: str = Field(..., min_length=1, description="Search query")
    node_types: Optional[List[NodeType]] = Field(
        None,
        description="Optional filter for specific node types",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of nodes",
    )
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity for semantic matches",
    )


class MemoryWithDistance(BaseModel):
    """Memory with distance score (for search results)."""

    id: UUID
    user_id: UUID
    memory_type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    accessed_at: datetime
    distance: float = Field(..., description="Distance score (lower = more similar)")

    model_config = {"from_attributes": True}


class GraphSummaryResponse(BaseModel):
    """Schema for knowledge graph summary."""

    total_nodes: int
    nodes_by_type: Dict[str, int]
    total_edges: int
    edges_by_type: Dict[str, int]
    total_associations: int


# ============================================================================
# Entity Extraction Schemas
# ============================================================================


class ExtractedEntity(BaseModel):
    """Schema for an extracted entity."""

    type: NodeType = Field(..., description="Entity type")
    name: str = Field(..., min_length=1, description="Entity name")
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Entity importance",
    )
    relevance: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relevance to source memory",
    )


class ExtractedRelationship(BaseModel):
    """Schema for an extracted relationship."""

    source: str = Field(..., description="Source entity name")
    target: str = Field(..., description="Target entity name")
    type: EdgeType = Field(..., description="Relationship type")
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relationship strength",
    )


class EntityExtractionResponse(BaseModel):
    """Schema for entity extraction response."""

    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]


class AutoOrganizeResponse(BaseModel):
    """Schema for auto-organize response."""

    memory_id: UUID
    created_nodes: List[KnowledgeNodeResponse]
    message: str
