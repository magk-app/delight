"""
Memory Graph - Typed Relationships and Graph Traversal

Enables linking memories with typed relationships for:
- Faster search through graph traversal
- Relationship-based memory retrieval
- Entity relationship mapping

Relationship Types:
- belongs_to: Entity belongs to category (jack → education)
- works_on: Working relationship (jack → delight_project)
- located_at: Location relationship (yoshinoya → tokyo)
- prefers: Preference relationship (jack → typescript)
- similar_to: Similarity relationship (memory1 → memory2)
- derived_from: Derivation relationship (summary → original)
"""

from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.memory import Memory


# ============================================================================
# Relationship Types
# ============================================================================

class RelationshipType(str, Enum):
    """Types of relationships between memories/entities."""
    BELONGS_TO = "belongs_to"  # Entity belongs to category
    WORKS_ON = "works_on"  # Working relationship
    LOCATED_AT = "located_at"  # Location relationship
    PREFERS = "prefers"  # Preference relationship
    SIMILAR_TO = "similar_to"  # Similarity relationship
    DERIVED_FROM = "derived_from"  # Derivation relationship
    RELATED_TO = "related_to"  # Generic relationship
    DEPENDS_ON = "depends_on"  # Dependency relationship
    PART_OF = "part_of"  # Composition relationship
    OPPOSITE_OF = "opposite_of"  # Opposition relationship


# ============================================================================
# Models
# ============================================================================

class Relationship(BaseModel):
    """A typed relationship between two memories."""
    from_memory_id: UUID = Field(description="Source memory ID")
    to_memory_id: UUID = Field(description="Target memory ID")
    relationship_type: RelationshipType = Field(description="Type of relationship")
    strength: float = Field(
        description="Strength of relationship (0-1)",
        ge=0.0,
        le=1.0,
        default=1.0
    )
    metadata: Dict = Field(
        description="Additional metadata about relationship",
        default_factory=dict
    )
    bidirectional: bool = Field(
        description="Whether relationship goes both ways",
        default=False
    )


class GraphNode(BaseModel):
    """Node in the memory graph."""
    memory_id: UUID
    content: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None


class GraphPath(BaseModel):
    """Path through the memory graph."""
    nodes: List[GraphNode]
    relationships: List[Relationship]
    total_strength: float
    path_length: int


# ============================================================================
# Memory Graph Service
# ============================================================================

class MemoryGraph:
    """Service for managing typed relationships and graph traversal.

    This service enables:
    - Creating typed relationships between memories
    - Graph traversal for finding related memories
    - Relationship-based search enhancement
    - Entity relationship mapping
    """

    def __init__(self):
        """Initialize memory graph service."""
        pass

    async def create_relationship(
        self,
        from_memory_id: UUID,
        to_memory_id: UUID,
        relationship_type: RelationshipType,
        strength: float = 1.0,
        metadata: Optional[Dict] = None,
        bidirectional: bool = False,
        db: AsyncSession = None
    ) -> Relationship:
        """Create a typed relationship between two memories.

        Args:
            from_memory_id: Source memory ID
            to_memory_id: Target memory ID
            relationship_type: Type of relationship
            strength: Relationship strength (0-1)
            metadata: Optional metadata
            bidirectional: Whether relationship goes both ways
            db: Database session

        Returns:
            Created Relationship object

        Example:
            >>> # Link jack to delight_project
            >>> relationship = await graph.create_relationship(
            ...     from_memory_id=jack_memory_id,
            ...     to_memory_id=delight_memory_id,
            ...     relationship_type=RelationshipType.WORKS_ON,
            ...     strength=0.95
            ... )
        """
        if metadata is None:
            metadata = {}

        relationship = Relationship(
            from_memory_id=from_memory_id,
            to_memory_id=to_memory_id,
            relationship_type=relationship_type,
            strength=strength,
            metadata=metadata,
            bidirectional=bidirectional
        )

        # Store relationship in source memory's extra_data
        if db:
            stmt = select(Memory).where(Memory.id == from_memory_id)
            result = await db.execute(stmt)
            from_memory = result.scalar_one_or_none()

            if from_memory:
                if not from_memory.extra_data:
                    from_memory.extra_data = {}

                if "relationships" not in from_memory.extra_data:
                    from_memory.extra_data["relationships"] = {}

                rel_type_key = relationship_type.value
                if rel_type_key not in from_memory.extra_data["relationships"]:
                    from_memory.extra_data["relationships"][rel_type_key] = []

                from_memory.extra_data["relationships"][rel_type_key].append({
                    "to_memory_id": str(to_memory_id),
                    "strength": strength,
                    "metadata": metadata
                })

                # If bidirectional, also add reverse relationship
                if bidirectional:
                    stmt = select(Memory).where(Memory.id == to_memory_id)
                    result = await db.execute(stmt)
                    to_memory = result.scalar_one_or_none()

                    if to_memory:
                        if not to_memory.extra_data:
                            to_memory.extra_data = {}

                        if "relationships" not in to_memory.extra_data:
                            to_memory.extra_data["relationships"] = {}

                        if rel_type_key not in to_memory.extra_data["relationships"]:
                            to_memory.extra_data["relationships"][rel_type_key] = []

                        to_memory.extra_data["relationships"][rel_type_key].append({
                            "to_memory_id": str(from_memory_id),
                            "strength": strength,
                            "metadata": metadata
                        })

                await db.commit()
                print(f"✅ Created {relationship_type.value} relationship: {from_memory_id} → {to_memory_id}")

        return relationship

    async def get_related_memories(
        self,
        memory_id: UUID,
        relationship_type: Optional[RelationshipType] = None,
        min_strength: float = 0.0,
        db: AsyncSession = None
    ) -> List[Tuple[Memory, Relationship]]:
        """Get memories related to a given memory.

        Args:
            memory_id: Source memory ID
            relationship_type: Optional filter by relationship type
            min_strength: Minimum relationship strength
            db: Database session

        Returns:
            List of (related_memory, relationship) tuples

        Example:
            >>> related = await graph.get_related_memories(
            ...     memory_id=jack_memory_id,
            ...     relationship_type=RelationshipType.WORKS_ON,
            ...     db=session
            ... )
            >>> related[0][0].content  # delight_project content
        """
        if not db:
            return []

        stmt = select(Memory).where(Memory.id == memory_id)
        result = await db.execute(stmt)
        source_memory = result.scalar_one_or_none()

        if not source_memory or not source_memory.extra_data:
            return []

        relationships_data = source_memory.extra_data.get("relationships", {})
        related_memories = []

        # Filter by relationship type if specified
        if relationship_type:
            rel_types = [relationship_type.value]
        else:
            rel_types = relationships_data.keys()

        for rel_type in rel_types:
            if rel_type not in relationships_data:
                continue

            for rel_data in relationships_data[rel_type]:
                strength = rel_data.get("strength", 1.0)
                if strength < min_strength:
                    continue

                target_id = UUID(rel_data["to_memory_id"])

                # Fetch target memory
                stmt = select(Memory).where(Memory.id == target_id)
                result = await db.execute(stmt)
                target_memory = result.scalar_one_or_none()

                if target_memory:
                    relationship = Relationship(
                        from_memory_id=memory_id,
                        to_memory_id=target_id,
                        relationship_type=RelationshipType(rel_type),
                        strength=strength,
                        metadata=rel_data.get("metadata", {})
                    )
                    related_memories.append((target_memory, relationship))

        return related_memories

    async def traverse_graph(
        self,
        start_memory_id: UUID,
        max_depth: int = 3,
        relationship_types: Optional[List[RelationshipType]] = None,
        min_strength: float = 0.5,
        db: AsyncSession = None
    ) -> List[GraphPath]:
        """Traverse memory graph from starting point.

        Args:
            start_memory_id: Starting memory ID
            max_depth: Maximum traversal depth
            relationship_types: Optional filter by relationship types
            min_strength: Minimum relationship strength
            db: Database session

        Returns:
            List of GraphPath objects representing different paths

        Example:
            >>> paths = await graph.traverse_graph(
            ...     start_memory_id=jack_memory_id,
            ...     max_depth=2,
            ...     relationship_types=[RelationshipType.WORKS_ON, RelationshipType.LOCATED_AT],
            ...     db=session
            ... )
            >>> paths[0].nodes  # [jack, delight_project, san_francisco]
        """
        if not db:
            return []

        visited: Set[UUID] = set()
        paths: List[GraphPath] = []

        async def dfs(
            current_id: UUID,
            current_path_nodes: List[GraphNode],
            current_path_rels: List[Relationship],
            current_strength: float,
            depth: int
        ):
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)

            # Get current memory
            stmt = select(Memory).where(Memory.id == current_id)
            result = await db.execute(stmt)
            current_memory = result.scalar_one_or_none()

            if not current_memory:
                return

            # Create node
            node = GraphNode(
                memory_id=current_id,
                content=current_memory.content,
                entity_id=current_memory.extra_data.get("entity_id") if current_memory.extra_data else None,
                entity_type=current_memory.extra_data.get("entity_type") if current_memory.extra_data else None
            )

            current_path_nodes.append(node)

            # If we have a path (not just starting node), save it
            if len(current_path_nodes) > 1:
                path = GraphPath(
                    nodes=current_path_nodes.copy(),
                    relationships=current_path_rels.copy(),
                    total_strength=current_strength,
                    path_length=len(current_path_nodes) - 1
                )
                paths.append(path)

            # Get related memories
            related = await self.get_related_memories(
                memory_id=current_id,
                min_strength=min_strength,
                db=db
            )

            # Filter by relationship type if specified
            if relationship_types:
                related = [
                    (mem, rel) for mem, rel in related
                    if rel.relationship_type in relationship_types
                ]

            # Traverse to related memories
            for related_memory, relationship in related:
                if related_memory.id not in visited:
                    new_strength = current_strength * relationship.strength
                    current_path_rels.append(relationship)

                    await dfs(
                        related_memory.id,
                        current_path_nodes.copy(),
                        current_path_rels.copy(),
                        new_strength,
                        depth + 1
                    )

                    current_path_rels.pop()

            current_path_nodes.pop()
            visited.remove(current_id)

        # Start DFS traversal
        await dfs(start_memory_id, [], [], 1.0, 0)

        # Sort paths by strength
        paths.sort(key=lambda p: p.total_strength, reverse=True)

        return paths

    async def find_shortest_path(
        self,
        from_memory_id: UUID,
        to_memory_id: UUID,
        db: AsyncSession = None
    ) -> Optional[GraphPath]:
        """Find shortest path between two memories.

        Args:
            from_memory_id: Source memory ID
            to_memory_id: Target memory ID
            db: Database session

        Returns:
            GraphPath representing shortest path, or None if no path exists

        Example:
            >>> path = await graph.find_shortest_path(
            ...     from_memory_id=jack_id,
            ...     to_memory_id=tokyo_id,
            ...     db=session
            ... )
            >>> [node.entity_id for node in path.nodes]
            ['jack', 'yoshinoya', 'tokyo']
        """
        if not db:
            return None

        # BFS for shortest path
        from collections import deque

        queue = deque([(from_memory_id, [], [], 1.0)])
        visited = {from_memory_id}

        while queue:
            current_id, path_nodes, path_rels, strength = queue.popleft()

            if current_id == to_memory_id:
                # Found target - build final path
                stmt = select(Memory).where(Memory.id == current_id)
                result = await db.execute(stmt)
                final_memory = result.scalar_one_or_none()

                if final_memory:
                    final_node = GraphNode(
                        memory_id=current_id,
                        content=final_memory.content,
                        entity_id=final_memory.extra_data.get("entity_id") if final_memory.extra_data else None,
                        entity_type=final_memory.extra_data.get("entity_type") if final_memory.extra_data else None
                    )
                    path_nodes.append(final_node)

                    return GraphPath(
                        nodes=path_nodes,
                        relationships=path_rels,
                        total_strength=strength,
                        path_length=len(path_nodes) - 1
                    )

            # Get related memories
            related = await self.get_related_memories(current_id, db=db)

            for related_memory, relationship in related:
                if related_memory.id not in visited:
                    visited.add(related_memory.id)

                    node = GraphNode(
                        memory_id=current_id,
                        content=(await db.execute(select(Memory).where(Memory.id == current_id))).scalar_one().content,
                        entity_id=None,
                        entity_type=None
                    )

                    new_path_nodes = path_nodes + [node]
                    new_path_rels = path_rels + [relationship]
                    new_strength = strength * relationship.strength

                    queue.append((related_memory.id, new_path_nodes, new_path_rels, new_strength))

        return None  # No path found

    async def get_entity_graph(
        self,
        user_id: UUID,
        entity_type: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, List[Tuple[str, RelationshipType, float]]]:
        """Get graph of all entities and their relationships.

        Args:
            user_id: User ID
            entity_type: Optional filter by entity type
            db: Database session

        Returns:
            Dict mapping entity_id to list of (related_entity_id, relationship_type, strength)

        Example:
            >>> graph = await memory_graph.get_entity_graph(user_id=uuid4(), db=session)
            >>> graph['jack']
            [('delight_project', RelationshipType.WORKS_ON, 0.95), ...]
        """
        if not db:
            return {}

        # Get all hierarchical memories
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.extra_data["storage_type"].astext == "hierarchical_eav"
        )

        if entity_type:
            stmt = stmt.where(Memory.extra_data["entity_type"].astext == entity_type)

        result = await db.execute(stmt)
        memories = result.scalars().all()

        entity_graph = {}

        for memory in memories:
            if not memory.extra_data or "entity_id" not in memory.extra_data:
                continue

            entity_id = memory.extra_data["entity_id"]
            relationships_data = memory.extra_data.get("relationships", {})

            entity_graph[entity_id] = []

            for rel_type, rels in relationships_data.items():
                for rel in rels:
                    target_id = rel["to_memory_id"]
                    strength = rel.get("strength", 1.0)

                    # Get target entity_id
                    target_stmt = select(Memory).where(Memory.id == UUID(target_id))
                    target_result = await db.execute(target_stmt)
                    target_memory = target_result.scalar_one_or_none()

                    if target_memory and target_memory.extra_data:
                        target_entity_id = target_memory.extra_data.get("entity_id", target_id)
                        entity_graph[entity_id].append((
                            target_entity_id,
                            RelationshipType(rel_type),
                            strength
                        ))

        return entity_graph


if __name__ == "__main__":
    """Test memory graph."""
    print("""
Memory Graph - Typed Relationships and Traversal
=================================================

This module enables creating typed relationships between memories and traversing
the memory graph for enhanced search.

Example Usage:
    from experiments.memory.memory_graph import MemoryGraph, RelationshipType
    from app.db.session import AsyncSessionLocal
    from uuid import uuid4

    graph = MemoryGraph()

    async with AsyncSessionLocal() as db:
        # Create relationship
        relationship = await graph.create_relationship(
            from_memory_id=jack_memory_id,
            to_memory_id=delight_memory_id,
            relationship_type=RelationshipType.WORKS_ON,
            strength=0.95,
            bidirectional=True,
            db=db
        )

        # Get related memories
        related = await graph.get_related_memories(
            memory_id=jack_memory_id,
            relationship_type=RelationshipType.WORKS_ON,
            db=db
        )

        # Traverse graph
        paths = await graph.traverse_graph(
            start_memory_id=jack_memory_id,
            max_depth=3,
            db=db
        )

        # Find shortest path
        path = await graph.find_shortest_path(
            from_memory_id=jack_id,
            to_memory_id=tokyo_id,
            db=db
        )

Features:
- Typed relationships (works_on, located_at, prefers, etc.)
- Relationship strength scoring
- Graph traversal with depth limits
- Shortest path finding
- Entity relationship mapping
- Bidirectional relationships

This enables faster search by traversing relationships instead of semantic search.
    """)
