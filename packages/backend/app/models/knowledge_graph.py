"""
KnowledgeGraph models - Entity and relationship tracking for structured knowledge

Enables the AI agent to build and maintain a structured knowledge graph by:
- Tracking entities (people, projects, concepts, goals, etc.)
- Recording relationships between entities
- Updating properties as new information is learned
- Supporting graph-based reasoning and queries

Example Knowledge Graph:
    [User] --HAS_GOAL--> [Graduate Early]
           --EXPERIENCES--> [Registration Anxiety]

    [Graduate Early] --HAS_DEADLINE--> [November]
                     --REQUIRES--> [Learning]
                     --PROGRESS--> [35%]

This complements vector memory with structured relationship tracking.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class EntityType(str, Enum):
    """
    Classification of knowledge graph entities

    - PERSON: User, family members, friends, colleagues
    - PROJECT: Goals, initiatives, ambitions
    - CONCEPT: Ideas, topics, domains of knowledge
    - EVENT: Meetings, deadlines, milestones
    - STRESSOR: Sources of anxiety or concern
    - HABIT: Behaviors, routines, practices
    - PREFERENCE: Likes, dislikes, settings
    - OTHER: Uncategorized entities
    """

    PERSON = "person"
    PROJECT = "project"
    CONCEPT = "concept"
    EVENT = "event"
    STRESSOR = "stressor"
    HABIT = "habit"
    PREFERENCE = "preference"
    OTHER = "other"


class RelationshipType(str, Enum):
    """
    Types of relationships between entities

    - HAS: Ownership or possession (User HAS Goal)
    - IS_A: Type/category relationship (Georgia_Tech IS_A University)
    - RELATED_TO: Generic association
    - CAUSES: Causal relationship (Registration CAUSES Anxiety)
    - REQUIRES: Dependency (Goal REQUIRES Learning)
    - PART_OF: Component relationship (Week_2 PART_OF Goal)
    - AFFECTS: Influence relationship
    - LOCATED_AT: Physical/temporal location
    - OTHER: Uncategorized relationship
    """

    HAS = "has"
    IS_A = "is_a"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    REQUIRES = "requires"
    PART_OF = "part_of"
    AFFECTS = "affects"
    LOCATED_AT = "located_at"
    OTHER = "other"


class KnowledgeEntity(Base):
    """
    Entity node in the knowledge graph

    Represents a distinct concept, person, project, or thing that the AI
    has learned about. Each entity has:
    - A unique name and type
    - Optional embedding for semantic search
    - Properties (JSONB) for flexible attributes
    - Timestamps for tracking learning and updates
    """

    __tablename__ = "knowledge_entities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique entity identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User whose knowledge graph this belongs to",
    )
    entity_type = Column(
        SQLEnum(
            EntityType,
            name="entity_type",
            create_type=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
        comment="Category of this entity",
    )
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Human-readable entity name (e.g., 'Graduate Early', 'Registration')",
    )
    description = Column(
        Text,
        nullable=True,
        comment="Optional description or context for this entity",
    )
    embedding = Column(
        Vector(1536),
        nullable=True,
        comment="Optional vector embedding for semantic entity search",
    )
    properties = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Flexible entity attributes (deadline, progress, intensity, etc.)",
    )
    confidence = Column(
        Float,
        nullable=False,
        default=1.0,
        comment="Confidence in this entity's existence/accuracy (0.0-1.0)",
    )
    source_memory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="SET NULL"),
        nullable=True,
        comment="Original memory that introduced this entity",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this entity was first learned",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time entity properties were updated",
    )

    # Relationships
    user = relationship("User", back_populates="knowledge_entities")
    source_memory = relationship("Memory")
    outgoing_relationships = relationship(
        "KnowledgeRelationship",
        foreign_keys="KnowledgeRelationship.from_entity_id",
        back_populates="from_entity",
        cascade="all, delete-orphan",
    )
    incoming_relationships = relationship(
        "KnowledgeRelationship",
        foreign_keys="KnowledgeRelationship.to_entity_id",
        back_populates="to_entity",
        cascade="all, delete-orphan",
    )

    # Ensure unique entity names per user (case-insensitive)
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_entity_name"),
        Index("ix_knowledge_entities_user_type", "user_id", "entity_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeEntity(id={self.id}, name='{self.name}', "
            f"type={self.entity_type}, confidence={self.confidence})>"
        )


class KnowledgeRelationship(Base):
    """
    Directed edge between two entities in the knowledge graph

    Represents a typed relationship between entities:
    - From entity → To entity
    - Relationship type (HAS, CAUSES, REQUIRES, etc.)
    - Optional properties (strength, context, metadata)
    - Confidence score for uncertain relationships

    Example:
        User (from) --HAS--> Goal (to)
        Goal (from) --REQUIRES--> Learning (to) [strength: 0.75]
    """

    __tablename__ = "knowledge_relationships"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique relationship identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User whose knowledge graph this belongs to",
    )
    from_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Source entity in the relationship",
    )
    to_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Target entity in the relationship",
    )
    relationship_type = Column(
        SQLEnum(
            RelationshipType,
            name="relationship_type",
            create_type=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
        comment="Type of relationship between entities",
    )
    properties = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Relationship attributes (strength, context, metadata, etc.)",
    )
    confidence = Column(
        Float,
        nullable=False,
        default=1.0,
        comment="Confidence in this relationship's accuracy (0.0-1.0)",
    )
    source_memory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="SET NULL"),
        nullable=True,
        comment="Memory that established this relationship",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this relationship was established",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last time relationship was updated",
    )

    # Relationships
    user = relationship("User", back_populates="knowledge_relationships")
    from_entity = relationship(
        "KnowledgeEntity",
        foreign_keys=[from_entity_id],
        back_populates="outgoing_relationships",
    )
    to_entity = relationship(
        "KnowledgeEntity",
        foreign_keys=[to_entity_id],
        back_populates="incoming_relationships",
    )
    source_memory = relationship("Memory")

    # Prevent duplicate relationships
    __table_args__ = (
        UniqueConstraint(
            "from_entity_id",
            "to_entity_id",
            "relationship_type",
            name="uq_relationship_triple",
        ),
        Index(
            "ix_knowledge_relationships_from_type",
            "from_entity_id",
            "relationship_type",
        ),
        Index(
            "ix_knowledge_relationships_to_type", "to_entity_id", "relationship_type"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeRelationship(id={self.id}, "
            f"{self.from_entity_id} --{self.relationship_type}--> {self.to_entity_id}, "
            f"confidence={self.confidence})>"
        )
