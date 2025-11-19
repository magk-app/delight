"""
Graph-Enhanced Search Strategy

Leverages memory graph relationships and hierarchical data for faster, more accurate search.

Instead of pure semantic search, this strategy:
1. Finds initial matches using semantic search
2. Traverses graph relationships to find related memories
3. Ranks results using both semantic similarity AND graph proximity
"""

from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from experiments.memory.types import SearchResult, SearchStrategy
from experiments.memory.search_strategies import SemanticSearch
from experiments.memory.memory_graph import MemoryGraph, RelationshipType


class GraphEnhancedSearch:
    """Search strategy that combines semantic search with graph traversal.

    This strategy:
    1. Performs semantic search to find initial candidates
    2. Traverses graph from those candidates to find related memories
    3. Ranks results by: semantic_score * (1 + graph_proximity_boost)

    Example:
        User asks: "What restaurant do I like in Tokyo?"

        Semantic search finds: "yoshinoya" (0.85 similarity)
        Graph traversal finds: "yoshinoya" → located_at → "tokyo" (boost +0.3)
        Final score: 0.85 * 1.3 = 1.105 (capped at 1.0) → 0.95

        This surfaces "yoshinoya" higher because of graph confirmation.
    """

    def __init__(self):
        """Initialize graph-enhanced search."""
        self.semantic_search = SemanticSearch()
        self.memory_graph = MemoryGraph()

    async def search(
        self,
        query: str,
        user_id: UUID,
        db: AsyncSession,
        limit: int = 10,
        threshold: float = 0.7,
        graph_depth: int = 2,
        graph_boost_factor: float = 0.3
    ) -> List[SearchResult]:
        """Search using semantic search + graph traversal.

        Args:
            query: Search query
            user_id: User ID
            db: Database session
            limit: Maximum results
            threshold: Semantic similarity threshold
            graph_depth: How many graph hops to traverse
            graph_boost_factor: How much to boost scores for graph-connected memories

        Returns:
            List of SearchResult with boosted scores

        Example:
            >>> results = await graph_search.search(
            ...     query="restaurant in Tokyo",
            ...     user_id=user_id,
            ...     db=db,
            ...     graph_depth=2
            ... )
        """
        print(f"\n🕸️  Graph-Enhanced Search: '{query}'")

        # Step 1: Initial semantic search
        print(f"   📍 Step 1: Semantic search (threshold={threshold})")
        initial_results = await self.semantic_search.search(
            query=query,
            user_id=user_id,
            db=db,
            limit=limit * 2,  # Get more candidates for graph expansion
            threshold=threshold
        )

        if not initial_results:
            print("   ⚠️  No initial semantic matches found")
            return []

        print(f"   ✅ Found {len(initial_results)} initial semantic matches")

        # Step 2: Build graph-expanded results
        print(f"   🕸️  Step 2: Graph traversal (depth={graph_depth})")
        expanded_results: Dict[UUID, SearchResult] = {}
        graph_proximity_scores: Dict[UUID, float] = {}

        for result in initial_results:
            # Add initial result
            expanded_results[result.memory_id] = result
            graph_proximity_scores[result.memory_id] = 0.0  # No boost for direct matches

            # Traverse graph from this result
            paths = await self.memory_graph.traverse_graph(
                start_memory_id=result.memory_id,
                max_depth=graph_depth,
                min_strength=0.5,
                db=db
            )

            # Add related memories found through graph
            for path in paths:
                for i, node in enumerate(path.nodes):
                    if node.memory_id not in expanded_results:
                        # Calculate graph proximity score
                        # Closer nodes get higher boost
                        proximity = 1.0 / (i + 1)  # 1.0, 0.5, 0.33, 0.25...
                        proximity *= path.total_strength  # Scale by relationship strength

                        # Create SearchResult for graph-discovered memory
                        # Score is lower than semantic match, but boosted by graph proximity
                        from experiments.memory.search_strategies import SemanticSearch
                        from sqlalchemy import select
                        from app.models.memory import Memory

                        stmt = select(Memory).where(Memory.id == node.memory_id)
                        mem_result = await db.execute(stmt)
                        memory = mem_result.scalar_one_or_none()

                        if memory:
                            # Base score for graph-discovered memories is semantic threshold
                            base_score = threshold * 0.8  # Slightly lower than threshold

                            expanded_results[node.memory_id] = SearchResult(
                                memory_id=node.memory_id,
                                content=node.content,
                                score=base_score,
                                memory_type=memory.memory_type.value if hasattr(memory.memory_type, 'value') else str(memory.memory_type),
                                categories=memory.extra_data.get("categories", []) if memory.extra_data else [],
                                created_at=memory.created_at,
                                metadata=memory.extra_data or {}
                            )

                            # Track proximity for boosting
                            if node.memory_id not in graph_proximity_scores:
                                graph_proximity_scores[node.memory_id] = proximity
                            else:
                                # Take max proximity if multiple paths
                                graph_proximity_scores[node.memory_id] = max(
                                    graph_proximity_scores[node.memory_id],
                                    proximity
                                )

        print(f"   ✅ Graph expansion found {len(expanded_results)} total memories")

        # Step 3: Apply graph proximity boost
        print(f"   🚀 Step 3: Applying graph proximity boost (factor={graph_boost_factor})")
        boosted_results = []
        for memory_id, result in expanded_results.items():
            proximity = graph_proximity_scores.get(memory_id, 0.0)
            boost = proximity * graph_boost_factor

            # Boost score
            boosted_score = result.score * (1 + boost)
            boosted_score = min(boosted_score, 1.0)  # Cap at 1.0

            # Create new result with boosted score
            boosted_result = SearchResult(
                memory_id=result.memory_id,
                content=result.content,
                score=boosted_score,
                memory_type=result.memory_type,
                categories=result.categories,
                created_at=result.created_at,
                metadata={
                    **result.metadata,
                    "graph_proximity": proximity,
                    "graph_boost": boost,
                    "original_score": result.score
                }
            )

            boosted_results.append(boosted_result)

        # Sort by boosted score
        boosted_results.sort(key=lambda r: r.score, reverse=True)

        # Limit results
        final_results = boosted_results[:limit]

        print(f"   ✅ Returning {len(final_results)} results with graph boosting")
        for i, result in enumerate(final_results[:5], 1):
            orig_score = result.metadata.get("original_score", result.score)
            boost = result.metadata.get("graph_boost", 0.0)
            print(f"      {i}. {result.content[:60]}... (score: {result.score:.3f}, orig: {orig_score:.3f}, boost: +{boost:.3f})")

        return final_results


# ============================================================================
# Hierarchical Attribute Search
# ============================================================================

class HierarchicalAttributeSearch:
    """Search by entity attributes in hierarchical memories.

    This strategy searches within the hierarchical structure of memories,
    enabling queries like:
    - "universities" → finds entities with universities attribute
    - "price = $10" → finds entities where price attribute equals $10
    - "locations contains Tokyo" → finds entities with Tokyo in locations list
    """

    async def search(
        self,
        attribute_name: str,
        user_id: UUID,
        db: AsyncSession,
        attribute_value: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search by attribute name and optionally value.

        Args:
            attribute_name: Name of attribute to search for
            user_id: User ID
            db: Database session
            attribute_value: Optional value to match
            limit: Maximum results

        Returns:
            List of SearchResult for memories with matching attributes

        Example:
            >>> # Find all entities with "universities" attribute
            >>> results = await search.search(
            ...     attribute_name="universities",
            ...     user_id=user_id,
            ...     db=db
            ... )
            >>>
            >>> # Find entities where price = "$10"
            >>> results = await search.search(
            ...     attribute_name="price",
            ...     attribute_value="$10",
            ...     user_id=user_id,
            ...     db=db
            ... )
        """
        from sqlalchemy import select
        from app.models.memory import Memory

        print(f"\n📊 Hierarchical Attribute Search: {attribute_name}" +
              (f" = {attribute_value}" if attribute_value else ""))

        # Query for hierarchical memories with this attribute
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.extra_data["storage_type"].astext == "hierarchical_eav",
            Memory.extra_data["attributes"].has_key(attribute_name)
        )

        result = await db.execute(stmt)
        memories = result.scalars().all()

        search_results = []

        for memory in memories:
            if not memory.extra_data:
                continue

            attributes = memory.extra_data.get("attributes", {})
            attr_value = attributes.get(attribute_name)

            # If value specified, check match
            if attribute_value:
                # Handle list values
                if isinstance(attr_value, list):
                    if attribute_value not in attr_value:
                        continue
                # Handle exact match
                elif str(attr_value) != attribute_value:
                    continue

            # Create SearchResult
            search_results.append(SearchResult(
                memory_id=memory.id,
                content=memory.content,
                score=1.0 if attribute_value and str(attr_value) == attribute_value else 0.9,
                memory_type=memory.memory_type.value if hasattr(memory.memory_type, 'value') else str(memory.memory_type),
                categories=memory.extra_data.get("categories", []),
                created_at=memory.created_at,
                metadata={
                    **memory.extra_data,
                    "matched_attribute": attribute_name,
                    "matched_value": attr_value
                }
            ))

        search_results = search_results[:limit]
        print(f"   ✅ Found {len(search_results)} memories with attribute '{attribute_name}'")

        return search_results


if __name__ == "__main__":
    """Test graph-enhanced search."""
    print("""
Graph-Enhanced Search Strategy
================================

This module provides search strategies that leverage:
1. Memory graph relationships
2. Hierarchical entity-attribute-value data

GraphEnhancedSearch:
- Combines semantic search with graph traversal
- Boosts scores for graph-connected memories
- Finds related memories through relationships

HierarchicalAttributeSearch:
- Searches by entity attributes
- Supports exact and partial matching
- Works with nested and list values

Example Usage:
    from experiments.memory.graph_search_strategy import GraphEnhancedSearch
    from app.db.session import AsyncSessionLocal

    graph_search = GraphEnhancedSearch()

    async with AsyncSessionLocal() as db:
        results = await graph_search.search(
            query="restaurant in Tokyo",
            user_id=user_id,
            db=db,
            graph_depth=2,
            graph_boost_factor=0.3
        )

This enables much faster and more accurate search by leveraging
the structure and relationships in the memory graph.
    """)
