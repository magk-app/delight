"""
Memory and MemoryCollection database models.
Defines 3-tier memory architecture for AI companion system.
Includes graph-based hierarchical retrieval with knowledge nodes and edges.
"""

import uuid
from enum import Enum
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text, UniqueConstraint, event, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class MemoryType(str, Enum):
    """
    Memory tier classification for 3-tier architecture.

    - PERSONAL: Identity, preferences, emotional patterns (never pruned)
      Examples: "I prefer working in the morning", "Class registration causes anxiety"

    - PROJECT: Goals, plans, progress snapshots (medium-term storage)
      Examples: "Goal: Graduate early from Georgia Tech", "Week 2 progress: 35% complete"

    - TASK: Mission details, conversation context (pruned after 30 days)
      Examples: "Completed 20-minute walk mission yesterday", "Discussed time management"
    """

    PERSONAL = "personal"
    PROJECT = "project"
    TASK = "task"


class NodeType(str, Enum):
    """
    Knowledge graph node type classification.

    Node types organize information into a hierarchical knowledge graph for
    fast context retrieval and semantic organization.

    - TOPIC: Subject matter or domain (e.g., "Machine Learning", "Time Management")
    - PROJECT: Specific goal or initiative (e.g., "Graduate Early", "Build Portfolio")
    - PERSON: Individual mentioned in memories (e.g., "Professor Smith", "Friend Alex")
    - CATEGORY: Organizational bucket (e.g., "Academic", "Career", "Health")
    - EVENT: Significant occurrence (e.g., "CS6200 Midterm", "Job Interview")
    """

    TOPIC = "topic"
    PROJECT = "project"
    PERSON = "person"
    CATEGORY = "category"
    EVENT = "event"


class EdgeType(str, Enum):
    """
    Knowledge graph edge type classification.

    Edge types define relationships between knowledge nodes, enabling
    graph traversal and hierarchical organization.

    - SUBTOPIC_OF: Hierarchical relationship (e.g., "Neural Networks" → "Machine Learning")
    - RELATED_TO: Symmetric association (e.g., "Time Management" ↔ "Stress Reduction")
    - PART_OF: Component relationship (e.g., "Week 2 Milestone" → "Graduate Early Project")
    - DEPENDS_ON: Dependency (e.g., "Apply to Grad School" → "Complete Undergrad")
    - PRECEDES: Temporal sequence (e.g., "Midterm" → "Final Exam")
    """

    SUBTOPIC_OF = "subtopic_of"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    PRECEDES = "precedes"


class Memory(Base):
    """
    Core memory storage with vector embeddings for semantic similarity search.

    Stores memories across 3 tiers (personal/project/task) with optional vector
    embeddings for AI-powered memory retrieval. Uses pgvector HNSW index for
    fast cosine similarity search.

    Vector Embedding:
    - Model: OpenAI text-embedding-3-small
    - Dimensions: 1536
    - Distance Metric: Cosine distance (vector_cosine_ops)
    - HNSW Index: m=16, ef_construction=64 (optimized for speed/recall balance)

    Extra Data (metadata column in DB) Examples:
    - Personal: {"stressor": true, "emotion": "fear", "category": "academic"}
    - Project: {"goal_id": "uuid", "milestone": "Week 2", "completion": 0.35}
    - Task: {"conversation_id": "uuid", "exchange_type": "goal_planning"}

    Note: The attribute is named 'extra_data' in Python code but maps to 'metadata' column in database.
    This is because 'metadata' is a reserved attribute name in SQLAlchemy.
    """

    __tablename__ = "memories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique memory identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this memory",
    )
    memory_type = Column(
        SQLEnum(
            MemoryType,
            name="memory_type",
            create_type=False,  # Don't create enum - already exists from migration
            values_callable=lambda x: [e.value for e in x],  # Use enum values ('personal'), not names ('PERSONAL')
        ),
        nullable=False,
        index=True,
        comment="Memory tier: personal (never pruned), project (goals), task (30-day pruning)",
    )
    content = Column(
        Text,
        nullable=False,
        comment="Human-readable memory content",
    )
    embedding = Column(
        Vector(1536),
        nullable=True,
        comment="1536-dim vector embedding from OpenAI text-embedding-3-small",
    )
    # Note: Using 'extra_data' as attribute name because 'metadata' is reserved by SQLAlchemy
    # This maps to the 'metadata' column in the database
    extra_data = Column(
        "metadata",  # Actual column name in database
        JSONB,
        nullable=True,
        default={},
        comment="Flexible metadata: stressor info, emotion scores, goal references, etc.",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Memory creation timestamp",
    )
    accessed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Last access time (updated on retrieval for LRU tracking)",
    )

    # Relationships
    user = relationship("User", back_populates="memories")

    def __repr__(self) -> str:
        return (
            f"<Memory(id={self.id}, user_id={self.user_id}, "
            f"type={self.memory_type}, content='{self.content[:50]}...')>"
        )


class MemoryCollection(Base):
    """
    Optional grouping mechanism for related memories.

    Collections organize memories by category (goals, stressor logs, preferences).
    Not required for basic memory operations, but useful for:
    - Stressor logs (tracking specific anxieties over time)
    - Goal-specific memories (all memories related to one goal)
    - Preference categories (work habits, communication style, etc.)
    """

    __tablename__ = "memory_collections"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique collection identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this collection",
    )
    collection_type = Column(
        String(50),
        nullable=False,
        comment="Collection category: goal, stressor_log, preferences, etc.",
    )
    name = Column(
        String(255),
        nullable=False,
        comment="Human-readable collection name",
    )
    description = Column(
        Text,
        nullable=True,
        comment="Optional description of collection purpose",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Collection creation timestamp",
    )

    # Relationships
    user = relationship("User", back_populates="memory_collections")

    def __repr__(self) -> str:
        return (
            f"<MemoryCollection(id={self.id}, user_id={self.user_id}, "
            f"type={self.collection_type}, name='{self.name}')>"
        )


class KnowledgeNode(Base):
    """
    Knowledge graph node for hierarchical memory organization.

    Nodes represent concepts, topics, projects, people, or categories that organize
    memories into a structured knowledge graph. This enables:
    - Fast context-aware retrieval (find relevant node → search within that node)
    - Hierarchical organization (e.g., Project → Subtopic → Memory)
    - Semantic node search with embeddings
    - Importance-based ranking and popularity tracking

    Node embeddings enable semantic matching at the concept level before drilling
    down to specific memories, reducing search space by 10-100x for typical queries.

    Metadata Examples:
    - Topic: {"field": "computer_science", "difficulty": "advanced"}
    - Project: {"status": "active", "deadline": "2025-05-15", "priority": "high"}
    - Person: {"role": "professor", "department": "CS", "relationship": "advisor"}
    """

    __tablename__ = "knowledge_nodes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique node identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this knowledge node",
    )
    node_type = Column(
        SQLEnum(
            NodeType,
            name="node_type",
            create_type=False,  # Created in migration
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
        comment="Node category: topic, project, person, category, event",
    )
    name = Column(
        String(255),
        nullable=False,
        index=True,  # For text-based node search
        comment="Human-readable node name (e.g., 'Machine Learning', 'Professor Smith')",
    )
    description = Column(
        Text,
        nullable=True,
        comment="Optional detailed description of the node",
    )
    embedding = Column(
        Vector(1536),
        nullable=True,
        comment="1536-dim vector embedding for semantic node search",
    )
    extra_data = Column(
        "metadata",  # Column name in DB
        JSONB,
        nullable=True,
        default={},
        comment="Flexible metadata: status, deadline, priority, field, etc.",
    )
    importance_score = Column(
        Float,
        nullable=False,
        default=0.5,
        index=True,
        comment="Node importance (0-1) for ranking, updated based on access patterns",
    )
    access_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times this node has been accessed (for popularity tracking)",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Node creation timestamp",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp",
    )

    # Relationships
    user = relationship("User", back_populates="knowledge_nodes")
    outgoing_edges = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    incoming_edges = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )
    memory_associations = relationship(
        "MemoryNodeAssociation",
        back_populates="node",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeNode(id={self.id}, type={self.node_type}, "
            f"name='{self.name}', importance={self.importance_score:.2f})>"
        )


class KnowledgeEdge(Base):
    """
    Knowledge graph edge representing relationships between nodes.

    Edges define how knowledge nodes relate to each other, enabling:
    - Hierarchical organization (subtopic_of, part_of)
    - Semantic associations (related_to)
    - Dependencies (depends_on)
    - Temporal sequences (precedes)

    Graph traversal allows expanding search context intelligently, e.g.:
    - Query about "Neural Networks" → expand to "Machine Learning" parent topic
    - Query about "Graduate Early Project" → include related subtasks and milestones

    Weight indicates relationship strength (0-1), used for ranking during traversal.

    Metadata Examples:
    - {"discovered_via": "llm_extraction", "confidence": 0.9}
    - {"temporal_distance_days": 7, "criticality": "high"}
    """

    __tablename__ = "knowledge_edges"
    __table_args__ = (
        UniqueConstraint(
            "source_node_id",
            "target_node_id",
            "edge_type",
            name="uq_knowledge_edges_source_target_type",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique edge identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this edge",
    )
    source_node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Source node of the relationship",
    )
    target_node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Target node of the relationship",
    )
    edge_type = Column(
        SQLEnum(
            EdgeType,
            name="edge_type",
            create_type=False,  # Created in migration
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
        comment="Relationship type: subtopic_of, related_to, part_of, depends_on, precedes",
    )
    weight = Column(
        Float,
        nullable=False,
        default=1.0,
        comment="Relationship strength (0-1), used for ranking during graph traversal",
    )
    extra_data = Column(
        "metadata",  # Column name in DB
        JSONB,
        nullable=True,
        default={},
        comment="Flexible metadata: discovery method, confidence, temporal distance, etc.",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Edge creation timestamp",
    )

    # Relationships
    user = relationship("User", back_populates="knowledge_edges")
    source_node = relationship(
        "KnowledgeNode",
        foreign_keys=[source_node_id],
        back_populates="outgoing_edges",
    )
    target_node = relationship(
        "KnowledgeNode",
        foreign_keys=[target_node_id],
        back_populates="incoming_edges",
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeEdge(id={self.id}, type={self.edge_type}, "
            f"source={self.source_node_id}, target={self.target_node_id}, weight={self.weight:.2f})>"
        )


class MemoryNodeAssociation(Base):
    """
    Association table linking memories to knowledge graph nodes.

    This enables hierarchical retrieval: find relevant nodes first, then search
    memories within those nodes. A memory can be associated with multiple nodes
    to support multi-faceted organization.

    Examples:
    - Memory "Studied neural networks for 3 hours" might link to:
      - Topic node: "Neural Networks" (relevance=1.0)
      - Topic node: "Machine Learning" (relevance=0.8)
      - Category node: "Academic" (relevance=0.9)

    Relevance score indicates how strongly the memory relates to the node,
    used for ranking memories within a node during retrieval.
    """

    __tablename__ = "memory_node_associations"
    __table_args__ = (
        UniqueConstraint(
            "memory_id",
            "node_id",
            name="uq_memory_node_assoc_memory_node",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique association identifier",
    )
    memory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Memory being associated with a node",
    )
    node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Knowledge node the memory belongs to",
    )
    relevance_score = Column(
        Float,
        nullable=False,
        default=1.0,
        comment="How relevant this memory is to the node (0-1), used for ranking",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Association creation timestamp",
    )

    # Relationships
    memory = relationship("Memory", back_populates="node_associations")
    node = relationship("KnowledgeNode", back_populates="memory_associations")

    def __repr__(self) -> str:
        return (
            f"<MemoryNodeAssociation(id={self.id}, memory={self.memory_id}, "
            f"node={self.node_id}, relevance={self.relevance_score:.2f})>"
        )


# Update Memory model to include node associations relationship
Memory.node_associations = relationship(
    "MemoryNodeAssociation",
    back_populates="memory",
    cascade="all, delete-orphan",
)


# Validation: Ensure embedding dimensions match expected size (1536)
@event.listens_for(Memory, "before_insert")
@event.listens_for(Memory, "before_update")
def validate_memory_embedding_dimensions(mapper, connection, target):
    """
    Validate that Memory embedding vector has exactly 1536 dimensions.

    Raises ValueError if embedding is not None and has wrong dimensions.
    This prevents runtime errors from OpenAI embedding mismatches.
    """
    if target.embedding is not None:
        if len(target.embedding) != 1536:
            raise ValueError(
                f"Memory embedding must be exactly 1536 dimensions "
                f"(OpenAI text-embedding-3-small), got {len(target.embedding)}"
            )


@event.listens_for(KnowledgeNode, "before_insert")
@event.listens_for(KnowledgeNode, "before_update")
def validate_node_embedding_dimensions(mapper, connection, target):
    """
    Validate that KnowledgeNode embedding vector has exactly 1536 dimensions.

    Raises ValueError if embedding is not None and has wrong dimensions.
    """
    if target.embedding is not None:
        if len(target.embedding) != 1536:
            raise ValueError(
                f"KnowledgeNode embedding must be exactly 1536 dimensions "
                f"(OpenAI text-embedding-3-small), got {len(target.embedding)}"
            )
