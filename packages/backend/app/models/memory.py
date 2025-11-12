"""
Memory and MemoryCollection database models.
Defines 3-tier memory architecture for AI companion system.
"""

import uuid
from enum import Enum
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text, event, func
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


# Validation: Ensure embedding dimensions match expected size (1536)
@event.listens_for(Memory, "before_insert")
@event.listens_for(Memory, "before_update")
def validate_embedding_dimensions(mapper, connection, target):
    """
    Validate that embedding vector has exactly 1536 dimensions.

    Raises ValueError if embedding is not None and has wrong dimensions.
    This prevents runtime errors from OpenAI embedding mismatches.
    """
    if target.embedding is not None:
        if len(target.embedding) != 1536:
            raise ValueError(
                f"Memory embedding must be exactly 1536 dimensions "
                f"(OpenAI text-embedding-3-small), got {len(target.embedding)}"
            )
