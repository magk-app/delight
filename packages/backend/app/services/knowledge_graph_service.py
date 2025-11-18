"""
KnowledgeGraphService - Graph knowledge tracking and updates

Enables the AI agent to build and maintain a structured knowledge graph by:
- Creating and updating entities (people, projects, concepts, etc.)
- Recording relationships between entities
- Updating entity properties as new information is learned
- Querying the graph for context and reasoning

This complements vector memory with structured relationship tracking.

Example Usage:
    # Create entities
    user_entity = await kg_service.create_entity(db, user_id, "User", EntityType.PERSON)
    goal_entity = await kg_service.create_entity(
        db, user_id, "Graduate Early", EntityType.PROJECT,
        properties={"deadline": "November", "progress": 0.35}
    )

    # Create relationship
    await kg_service.create_relationship(
        db, user_id, user_entity.id, goal_entity.id,
        RelationshipType.HAS, properties={"priority": "high"}
    )

    # Update entity properties
    await kg_service.update_entity_properties(
        db, user_id, goal_entity.id, {"progress": 0.50}
    )

    # Query related entities
    goals = await kg_service.get_related_entities(
        db, user_id, user_entity.id, RelationshipType.HAS
    )
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_graph import (
    EntityType,
    KnowledgeEntity,
    KnowledgeRelationship,
    RelationshipType,
)
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Service for managing structured knowledge graph operations"""

    def __init__(self):
        """Initialize knowledge graph service"""
        self.embedding_service = get_embedding_service()

    async def create_entity(
        self,
        db: AsyncSession,
        user_id: UUID,
        name: str,
        entity_type: EntityType,
        description: Optional[str] = None,
        properties: Optional[Dict] = None,
        confidence: float = 1.0,
        source_memory_id: Optional[UUID] = None,
    ) -> KnowledgeEntity:
        """
        Create new entity in the knowledge graph

        Args:
            db: Database session
            user_id: User ID
            name: Entity name (e.g., "Graduate Early", "Registration Anxiety")
            entity_type: EntityType enum
            description: Optional description
            properties: Optional JSONB properties (deadline, progress, etc.)
            confidence: Confidence score (0.0-1.0)
            source_memory_id: Memory that introduced this entity

        Returns:
            Created KnowledgeEntity
        """
        # Check if entity already exists (case-insensitive)
        existing = await self.get_entity_by_name(db, user_id, name)
        if existing:
            logger.info(f"Entity '{name}' already exists for user {user_id}, returning existing")
            return existing

        # Generate embedding for entity name and description
        text_for_embedding = f"{name}"
        if description:
            text_for_embedding += f" {description}"

        embedding = await self.embedding_service.generate_embedding(text_for_embedding)

        # Create entity
        entity = KnowledgeEntity(
            user_id=user_id,
            entity_type=entity_type,
            name=name,
            description=description,
            embedding=embedding,
            properties=properties or {},
            confidence=confidence,
            source_memory_id=source_memory_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(entity)
        await db.commit()
        await db.refresh(entity)

        logger.info(
            f"Created {entity_type} entity '{name}' for user {user_id} "
            f"(confidence: {confidence})"
        )

        return entity

    async def get_entity_by_name(
        self, db: AsyncSession, user_id: UUID, name: str
    ) -> Optional[KnowledgeEntity]:
        """
        Find entity by name (case-insensitive)

        Args:
            db: Database session
            user_id: User ID
            name: Entity name to search

        Returns:
            KnowledgeEntity or None
        """
        result = await db.execute(
            select(KnowledgeEntity).where(
                and_(
                    KnowledgeEntity.user_id == user_id,
                    KnowledgeEntity.name.ilike(name),  # Case-insensitive
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_entity_properties(
        self,
        db: AsyncSession,
        user_id: UUID,
        entity_id: UUID,
        properties: Dict,
        merge: bool = True,
    ) -> Optional[KnowledgeEntity]:
        """
        Update entity properties (learning new information)

        Args:
            db: Database session
            user_id: User ID
            entity_id: Entity ID to update
            properties: New properties to add/update
            merge: If True, merge with existing properties; if False, replace

        Returns:
            Updated KnowledgeEntity or None if not found
        """
        entity = await db.get(KnowledgeEntity, entity_id)
        if not entity or entity.user_id != user_id:
            return None

        # Merge or replace properties
        if merge:
            updated_props = entity.properties or {}
            updated_props.update(properties)
            entity.properties = updated_props
        else:
            entity.properties = properties

        entity.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(entity)

        logger.info(
            f"Updated entity '{entity.name}' properties for user {user_id}: "
            f"{properties}"
        )

        return entity

    async def create_relationship(
        self,
        db: AsyncSession,
        user_id: UUID,
        from_entity_id: UUID,
        to_entity_id: UUID,
        relationship_type: RelationshipType,
        properties: Optional[Dict] = None,
        confidence: float = 1.0,
        source_memory_id: Optional[UUID] = None,
    ) -> KnowledgeRelationship:
        """
        Create relationship between two entities

        Args:
            db: Database session
            user_id: User ID
            from_entity_id: Source entity
            to_entity_id: Target entity
            relationship_type: RelationshipType enum
            properties: Optional relationship attributes
            confidence: Confidence score (0.0-1.0)
            source_memory_id: Memory that established this relationship

        Returns:
            Created KnowledgeRelationship

        Raises:
            ValueError: If entities don't exist or belong to different users
        """
        # Verify both entities exist and belong to user
        from_entity = await db.get(KnowledgeEntity, from_entity_id)
        to_entity = await db.get(KnowledgeEntity, to_entity_id)

        if not from_entity or from_entity.user_id != user_id:
            raise ValueError(f"From entity {from_entity_id} not found for user {user_id}")

        if not to_entity or to_entity.user_id != user_id:
            raise ValueError(f"To entity {to_entity_id} not found for user {user_id}")

        # Check if relationship already exists
        existing = await self.get_relationship(
            db, user_id, from_entity_id, to_entity_id, relationship_type
        )
        if existing:
            logger.info(
                f"Relationship {from_entity.name} --{relationship_type}--> "
                f"{to_entity.name} already exists, returning existing"
            )
            return existing

        # Create relationship
        relationship = KnowledgeRelationship(
            user_id=user_id,
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            relationship_type=relationship_type,
            properties=properties or {},
            confidence=confidence,
            source_memory_id=source_memory_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(relationship)
        await db.commit()
        await db.refresh(relationship)

        logger.info(
            f"Created relationship: {from_entity.name} --{relationship_type}--> "
            f"{to_entity.name} (confidence: {confidence})"
        )

        return relationship

    async def get_relationship(
        self,
        db: AsyncSession,
        user_id: UUID,
        from_entity_id: UUID,
        to_entity_id: UUID,
        relationship_type: RelationshipType,
    ) -> Optional[KnowledgeRelationship]:
        """
        Find specific relationship between two entities

        Args:
            db: Database session
            user_id: User ID
            from_entity_id: Source entity
            to_entity_id: Target entity
            relationship_type: Relationship type

        Returns:
            KnowledgeRelationship or None
        """
        result = await db.execute(
            select(KnowledgeRelationship).where(
                and_(
                    KnowledgeRelationship.user_id == user_id,
                    KnowledgeRelationship.from_entity_id == from_entity_id,
                    KnowledgeRelationship.to_entity_id == to_entity_id,
                    KnowledgeRelationship.relationship_type == relationship_type,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_related_entities(
        self,
        db: AsyncSession,
        user_id: UUID,
        entity_id: UUID,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "outgoing",
    ) -> List[Tuple[KnowledgeEntity, KnowledgeRelationship]]:
        """
        Get entities related to a given entity

        Args:
            db: Database session
            user_id: User ID
            entity_id: Entity to find relationships for
            relationship_type: Optional filter by relationship type
            direction: "outgoing" (from entity), "incoming" (to entity), or "both"

        Returns:
            List of (related_entity, relationship) tuples
        """
        results = []

        # Outgoing relationships (entity → others)
        if direction in ["outgoing", "both"]:
            query = (
                select(KnowledgeEntity, KnowledgeRelationship)
                .join(
                    KnowledgeRelationship,
                    KnowledgeRelationship.to_entity_id == KnowledgeEntity.id,
                )
                .where(
                    and_(
                        KnowledgeRelationship.user_id == user_id,
                        KnowledgeRelationship.from_entity_id == entity_id,
                    )
                )
            )

            if relationship_type:
                query = query.where(
                    KnowledgeRelationship.relationship_type == relationship_type
                )

            result = await db.execute(query)
            results.extend(result.all())

        # Incoming relationships (others → entity)
        if direction in ["incoming", "both"]:
            query = (
                select(KnowledgeEntity, KnowledgeRelationship)
                .join(
                    KnowledgeRelationship,
                    KnowledgeRelationship.from_entity_id == KnowledgeEntity.id,
                )
                .where(
                    and_(
                        KnowledgeRelationship.user_id == user_id,
                        KnowledgeRelationship.to_entity_id == entity_id,
                    )
                )
            )

            if relationship_type:
                query = query.where(
                    KnowledgeRelationship.relationship_type == relationship_type
                )

            result = await db.execute(query)
            results.extend(result.all())

        logger.info(
            f"Found {len(results)} related entities for entity {entity_id} "
            f"(direction: {direction}, type: {relationship_type})"
        )

        return results

    async def extract_entities_from_memory(
        self, db: AsyncSession, user_id: UUID, memory_id: UUID, memory_content: str
    ) -> List[KnowledgeEntity]:
        """
        Extract entities from memory content and add to knowledge graph

        This is a simplified version - in production, you'd use NLP/LLM to extract entities.
        For now, we use keyword detection and pattern matching.

        Args:
            db: Database session
            user_id: User ID
            memory_id: Source memory ID
            memory_content: Text to extract entities from

        Returns:
            List of created/updated entities
        """
        entities = []

        # TODO: Implement proper NLP entity extraction
        # For now, use simple keyword detection

        # Example: Detect goal-related entities
        if "goal" in memory_content.lower():
            # Extract goal name (simplified - would use NLP in production)
            goal_entity = await self.create_entity(
                db,
                user_id,
                "Extracted Goal",  # Would extract actual goal name
                EntityType.PROJECT,
                description=memory_content[:200],
                source_memory_id=memory_id,
                confidence=0.7,  # Lower confidence for auto-extracted
            )
            entities.append(goal_entity)

        # Example: Detect stressor entities
        if any(word in memory_content.lower() for word in ["anxiety", "stress", "worry"]):
            stressor_entity = await self.create_entity(
                db,
                user_id,
                "Stressor",  # Would extract actual stressor
                EntityType.STRESSOR,
                description=memory_content[:200],
                source_memory_id=memory_id,
                confidence=0.7,
            )
            entities.append(stressor_entity)

        logger.info(
            f"Extracted {len(entities)} entities from memory {memory_id} for user {user_id}"
        )

        return entities

    async def get_entity_context(
        self, db: AsyncSession, user_id: UUID, entity_id: UUID, max_depth: int = 2
    ) -> Dict:
        """
        Get full context for an entity including relationships

        Args:
            db: Database session
            user_id: User ID
            entity_id: Entity to get context for
            max_depth: Maximum relationship depth to traverse

        Returns:
            Dict with entity details and related entities
        """
        entity = await db.get(KnowledgeEntity, entity_id)
        if not entity or entity.user_id != user_id:
            return {}

        # Get direct relationships
        related = await self.get_related_entities(db, user_id, entity_id, direction="both")

        context = {
            "entity": {
                "id": str(entity.id),
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.description,
                "properties": entity.properties,
                "confidence": entity.confidence,
            },
            "relationships": {
                "outgoing": [],
                "incoming": [],
            },
        }

        # Organize relationships
        for related_entity, relationship in related:
            rel_data = {
                "entity": {
                    "id": str(related_entity.id),
                    "name": related_entity.name,
                    "type": related_entity.entity_type,
                },
                "relationship": {
                    "type": relationship.relationship_type,
                    "properties": relationship.properties,
                    "confidence": relationship.confidence,
                },
            }

            if relationship.from_entity_id == entity_id:
                context["relationships"]["outgoing"].append(rel_data)
            else:
                context["relationships"]["incoming"].append(rel_data)

        logger.info(f"Retrieved context for entity '{entity.name}' (user {user_id})")
        return context


# Singleton instance
_knowledge_graph_service: Optional[KnowledgeGraphService] = None


def get_knowledge_graph_service() -> KnowledgeGraphService:
    """
    Get singleton instance of KnowledgeGraphService

    Returns:
        KnowledgeGraphService instance
    """
    global _knowledge_graph_service
    if _knowledge_graph_service is None:
        _knowledge_graph_service = KnowledgeGraphService()
    return _knowledge_graph_service
