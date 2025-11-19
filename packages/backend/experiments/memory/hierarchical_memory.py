"""
Hierarchical Memory Storage

Stores memories in hierarchical structures with Entity-Attribute-Value organization.
Enables complex nested objects like:
  - jack_education: { universities: ["UCSB", "MIT", "Georgia Tech"] }
  - yoshinoya: { favorite_dish: "tonkatsu", price: "$10", locations: ["Tokyo", "America"] }

This module bridges EAV extraction and database storage.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.memory import Memory, MemoryType
from experiments.memory.eav_extractor import Entity, AttributeValue, EAVExtractor
from experiments.memory.embedding_service import EmbeddingService


# ============================================================================
# Hierarchical Memory Builder
# ============================================================================

class HierarchicalMemory:
    """Represents a memory with hierarchical entity-attribute-value structure.

    Example:
        {
            "entity_id": "yoshinoya",
            "entity_type": "place",
            "attributes": {
                "type": "restaurant",
                "favorite_dish": "tonkatsu bowl",
                "price": "$10",
                "locations": ["Tokyo", "America"]
            },
            "related_entities": ["jack_preferences"],
            "confidence": 0.92
        }
    """

    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        attributes: Dict[str, Any],
        related_entities: List[str] = None,
        confidence: float = 1.0
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.attributes = attributes
        self.related_entities = related_entities or []
        self.confidence = confidence

    @staticmethod
    def from_entity(entity: Entity) -> "HierarchicalMemory":
        """Create HierarchicalMemory from EAV Entity."""
        # Convert AttributeValue list to dict
        attributes = {}
        total_confidence = 0.0

        for attr in entity.attributes:
            attributes[attr.attribute] = attr.value
            total_confidence += attr.confidence

        # Average confidence
        avg_confidence = total_confidence / len(entity.attributes) if entity.attributes else 1.0

        return HierarchicalMemory(
            entity_id=entity.entity_name,
            entity_type=entity.entity_type,
            attributes=attributes,
            related_entities=entity.related_entities,
            confidence=min(avg_confidence, 1.0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "attributes": self.attributes,
            "related_entities": self.related_entities,
            "confidence": self.confidence,
            "storage_type": "hierarchical_eav"
        }

    def to_content_string(self) -> str:
        """Generate searchable content string from hierarchical data.

        This creates a text representation for embedding generation and search.
        """
        parts = [f"{self.entity_id} ({self.entity_type})"]

        for key, value in self.attributes.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
                parts.append(f"{key}: {value_str}")
            elif isinstance(value, dict):
                # Nested dict
                for nested_key, nested_value in value.items():
                    parts.append(f"{key}.{nested_key}: {nested_value}")
            else:
                parts.append(f"{key}: {value}")

        return " | ".join(parts)


# ============================================================================
# Hierarchical Memory Service
# ============================================================================

class HierarchicalMemoryService:
    """Service for managing hierarchical memories with EAV structure.

    This service:
    - Extracts entities from messages using EAV extractor
    - Converts entities to hierarchical memories
    - Stores in database with proper metadata
    - Enables querying by entity, attribute, or value
    """

    def __init__(self):
        self.eav_extractor = EAVExtractor()
        self.embedding_service = EmbeddingService()

    async def create_hierarchical_memories(
        self,
        user_id: UUID,
        message: str,
        memory_type: MemoryType,
        db: AsyncSession,
        context_entities: Optional[List[str]] = None
    ) -> List[Memory]:
        """Create hierarchical memories from message.

        Args:
            user_id: User ID
            message: User message
            memory_type: Type of memory
            db: Database session
            context_entities: Optional list of known entities for context

        Returns:
            List of created Memory objects with hierarchical structure

        Example:
            >>> memories = await service.create_hierarchical_memories(
            ...     user_id=uuid4(),
            ...     message="I love Yoshinoya's tonkatsu for $10",
            ...     memory_type=MemoryType.PERSONAL,
            ...     db=session
            ... )
            >>> memories[0].extra_data['entity_id']
            'yoshinoya'
            >>> memories[0].extra_data['attributes']['favorite_dish']
            'tonkatsu'
        """
        print(f"\n🌳 Creating hierarchical memories from message...")

        # Extract EAV triples
        eav_result = await self.eav_extractor.extract_eav(message, context_entities)

        if not eav_result.entities:
            print("⚠️  No entities extracted")
            return []

        print(f"✅ Extracted {len(eav_result.entities)} entities")

        memories_created = []

        for entity in eav_result.entities:
            # Convert to hierarchical memory
            hierarchical_mem = HierarchicalMemory.from_entity(entity)

            # Generate content string for search
            content = hierarchical_mem.to_content_string()

            print(f"  📝 Creating memory for entity: {hierarchical_mem.entity_id}")
            print(f"     Content: {content[:100]}...")

            # Generate embedding
            embedding = await self.embedding_service.embed_text(content)

            # Create memory with hierarchical metadata
            memory = Memory(
                id=uuid4(),
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                embedding=embedding,
                extra_data=hierarchical_mem.to_dict()
            )

            db.add(memory)
            memories_created.append(memory)

        await db.commit()

        # Refresh all
        for memory in memories_created:
            await db.refresh(memory)

        print(f"✅ Created {len(memories_created)} hierarchical memories\n")
        return memories_created

    async def get_entity(
        self,
        user_id: UUID,
        entity_id: str,
        db: AsyncSession
    ) -> Optional[HierarchicalMemory]:
        """Get hierarchical memory by entity ID.

        Args:
            user_id: User ID
            entity_id: Entity identifier
            db: Database session

        Returns:
            HierarchicalMemory or None
        """
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.extra_data["entity_id"].astext == entity_id
        )

        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()

        if not memory:
            return None

        return HierarchicalMemory(
            entity_id=memory.extra_data["entity_id"],
            entity_type=memory.extra_data["entity_type"],
            attributes=memory.extra_data["attributes"],
            related_entities=memory.extra_data.get("related_entities", []),
            confidence=memory.extra_data.get("confidence", 1.0)
        )

    async def get_entities_by_type(
        self,
        user_id: UUID,
        entity_type: str,
        db: AsyncSession
    ) -> List[HierarchicalMemory]:
        """Get all hierarchical memories of a specific entity type.

        Args:
            user_id: User ID
            entity_type: Type of entity (person, place, project, etc.)
            db: Database session

        Returns:
            List of HierarchicalMemory objects
        """
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.extra_data["entity_type"].astext == entity_type
        )

        result = await db.execute(stmt)
        memories = result.scalars().all()

        hierarchical_memories = []
        for memory in memories:
            if memory.extra_data and "entity_id" in memory.extra_data:
                hierarchical_memories.append(HierarchicalMemory(
                    entity_id=memory.extra_data["entity_id"],
                    entity_type=memory.extra_data["entity_type"],
                    attributes=memory.extra_data["attributes"],
                    related_entities=memory.extra_data.get("related_entities", []),
                    confidence=memory.extra_data.get("confidence", 1.0)
                ))

        return hierarchical_memories

    async def query_by_attribute(
        self,
        user_id: UUID,
        attribute_name: str,
        db: AsyncSession
    ) -> List[HierarchicalMemory]:
        """Find entities that have a specific attribute.

        Args:
            user_id: User ID
            attribute_name: Name of attribute to search for
            db: Database session

        Returns:
            List of HierarchicalMemory objects with that attribute

        Example:
            >>> memories = await service.query_by_attribute(
            ...     user_id=uuid4(),
            ...     attribute_name="universities",
            ...     db=session
            ... )
            >>> memories[0].attributes["universities"]
            ["UCSB", "MIT", "Georgia Tech"]
        """
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.extra_data["attributes"].has_key(attribute_name)
        )

        result = await db.execute(stmt)
        memories = result.scalars().all()

        hierarchical_memories = []
        for memory in memories:
            if memory.extra_data and "entity_id" in memory.extra_data:
                hierarchical_memories.append(HierarchicalMemory(
                    entity_id=memory.extra_data["entity_id"],
                    entity_type=memory.extra_data["entity_type"],
                    attributes=memory.extra_data["attributes"],
                    related_entities=memory.extra_data.get("related_entities", []),
                    confidence=memory.extra_data.get("confidence", 1.0)
                ))

        return hierarchical_memories

    async def merge_entity_attributes(
        self,
        user_id: UUID,
        entity_id: str,
        new_attributes: Dict[str, Any],
        db: AsyncSession
    ) -> Optional[Memory]:
        """Merge new attributes into existing entity.

        If entity doesn't exist, returns None.
        If entity exists, merges attributes and updates memory.

        Args:
            user_id: User ID
            entity_id: Entity identifier
            new_attributes: New attributes to merge
            db: Database session

        Returns:
            Updated Memory object or None
        """
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.extra_data["entity_id"].astext == entity_id
        )

        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()

        if not memory:
            print(f"⚠️  Entity {entity_id} not found for merging")
            return None

        # Merge attributes
        current_attributes = memory.extra_data.get("attributes", {})
        merged_attributes = {**current_attributes, **new_attributes}

        # Update extra_data
        memory.extra_data["attributes"] = merged_attributes

        # Regenerate content string
        hierarchical_mem = HierarchicalMemory(
            entity_id=entity_id,
            entity_type=memory.extra_data["entity_type"],
            attributes=merged_attributes,
            related_entities=memory.extra_data.get("related_entities", []),
            confidence=memory.extra_data.get("confidence", 1.0)
        )

        memory.content = hierarchical_mem.to_content_string()

        # Regenerate embedding
        memory.embedding = await self.embedding_service.embed_text(memory.content)

        await db.commit()
        await db.refresh(memory)

        print(f"✅ Merged attributes into entity {entity_id}")
        return memory

    def print_entity_summary(self, hierarchical_mem: HierarchicalMemory):
        """Print formatted entity summary."""
        print("\n" + "=" * 70)
        print(f"📦 Entity: {hierarchical_mem.entity_id}")
        print("=" * 70)
        print(f"Type: {hierarchical_mem.entity_type}")
        print(f"Confidence: {hierarchical_mem.confidence:.2f}")
        print("\nAttributes:")

        for key, value in hierarchical_mem.attributes.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for nested_key, nested_value in value.items():
                    print(f"    {nested_key}: {nested_value}")
            else:
                print(f"  {key}: {value}")

        if hierarchical_mem.related_entities:
            print(f"\nRelated Entities: {', '.join(hierarchical_mem.related_entities)}")

        print("=" * 70 + "\n")


if __name__ == "__main__":
    """Test hierarchical memory storage."""
    print("""
Hierarchical Memory Storage Module
===================================

This module enables storing complex nested memory structures using Entity-Attribute-Value
organization.

Example Usage:
    from experiments.memory.hierarchical_memory import HierarchicalMemoryService
    from app.db.session import AsyncSessionLocal
    from app.models.memory import MemoryType
    from uuid import uuid4

    service = HierarchicalMemoryService()

    async with AsyncSessionLocal() as db:
        # Create hierarchical memories
        memories = await service.create_hierarchical_memories(
            user_id=uuid4(),
            message="I went to UCSB, MIT, and Georgia Tech. My favorite restaurant is Yoshinoya with tonkatsu for $10.",
            memory_type=MemoryType.PERSONAL,
            db=db
        )

        # Query by entity
        entity = await service.get_entity(user_id, "yoshinoya", db)
        print(entity.attributes)  # {"type": "restaurant", "favorite_dish": "tonkatsu", "price": "$10", ...}

        # Query by attribute
        education_memories = await service.query_by_attribute(user_id, "universities", db)

Features:
- Hierarchical storage (nested attributes)
- Entity-based organization
- Attribute querying
- Entity merging (update existing entities with new data)
- Automatic embedding generation
- Relationship tracking between entities

See eav_extractor.py for Entity-Attribute-Value extraction logic.
    """)
