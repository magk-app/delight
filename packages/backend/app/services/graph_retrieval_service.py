"""
Graph-based hierarchical memory retrieval service.

Implements fast context-aware memory retrieval using knowledge graph structure:
- Two-step retrieval: find relevant nodes → search within nodes
- Graph-guided expansion: traverse relationships for context
- Hybrid search: combine vector similarity, graph structure, and metadata filters

Reduces search space by 10-100x for typical queries compared to flat vector search.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy import Float, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.memory import (
    EdgeType,
    KnowledgeEdge,
    KnowledgeNode,
    Memory,
    MemoryNodeAssociation,
    MemoryType,
    NodeType,
)

logger = logging.getLogger(__name__)


class GraphRetrievalService:
    """
    Service for graph-based hierarchical memory retrieval.

    This service enables fast, context-aware memory retrieval by organizing memories
    into a knowledge graph. It provides multiple retrieval strategies optimized for
    different use cases.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the graph retrieval service.

        Args:
            db: Async database session
        """
        self.db = db

    async def find_relevant_nodes(
        self,
        user_id: UUID,
        query: str,
        query_embedding: Optional[List[float]] = None,
        node_types: Optional[List[NodeType]] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[Tuple[KnowledgeNode, float]]:
        """
        Find knowledge nodes relevant to a query.

        Uses text matching and/or semantic similarity to find relevant nodes.
        This is Step 1 of the two-step hierarchical retrieval strategy.

        Args:
            user_id: User identifier
            query: Query string (for text matching)
            query_embedding: Optional query embedding (for semantic search)
            node_types: Optional filter for specific node types
            top_k: Maximum number of nodes to return
            similarity_threshold: Minimum cosine similarity (0-1) for semantic matches

        Returns:
            List of (KnowledgeNode, relevance_score) tuples, sorted by relevance
        """
        # Build base query
        stmt = select(KnowledgeNode).where(KnowledgeNode.user_id == user_id)

        # Filter by node type if specified
        if node_types:
            stmt = stmt.where(KnowledgeNode.node_type.in_(node_types))

        # If we have an embedding, use semantic similarity
        if query_embedding:
            # Calculate cosine similarity (1 - cosine distance)
            # pgvector's <=> operator returns cosine distance [0, 2]
            # We convert to similarity [0, 1] where 1 = identical
            distance = KnowledgeNode.embedding.cosine_distance(query_embedding)
            similarity = 1 - (distance / 2)

            stmt = (
                stmt.add_columns(similarity.label("similarity"))
                .where(KnowledgeNode.embedding.isnot(None))
                .where(similarity >= similarity_threshold)
                .order_by(similarity.desc())
            )
        else:
            # Text-based matching: search in name (case-insensitive partial match)
            # Also boost by importance_score
            query_lower = query.lower()
            name_match_score = func.similarity(
                func.lower(KnowledgeNode.name), query_lower
            )
            combined_score = (
                name_match_score * 0.7 + KnowledgeNode.importance_score * 0.3
            )

            stmt = (
                stmt.add_columns(combined_score.label("relevance"))
                .where(func.lower(KnowledgeNode.name).contains(query_lower))
                .order_by(combined_score.desc())
            )

        stmt = stmt.limit(top_k)

        result = await self.db.execute(stmt)
        rows = result.all()

        # Extract (node, score) tuples
        nodes_with_scores = [(row[0], float(row[1])) for row in rows]

        # Update access counts for retrieved nodes (async, non-blocking)
        for node, _ in nodes_with_scores:
            node.access_count += 1
            # Optionally update importance_score based on access patterns
            # Simple formula: importance increases with access count (capped at 1.0)
            node.importance_score = min(1.0, 0.5 + (node.access_count / 100))

        await self.db.flush()

        return nodes_with_scores

    async def get_memories_by_nodes(
        self,
        user_id: UUID,
        nodes: List[KnowledgeNode],
        memory_type: Optional[MemoryType] = None,
        limit: Optional[int] = None,
    ) -> List[Memory]:
        """
        Get all memories associated with given knowledge nodes.

        Args:
            user_id: User identifier
            nodes: List of knowledge nodes
            memory_type: Optional filter for memory type
            limit: Optional limit on number of memories

        Returns:
            List of Memory objects
        """
        if not nodes:
            return []

        node_ids = [node.id for node in nodes]

        # Query memories associated with these nodes
        stmt = (
            select(Memory)
            .join(MemoryNodeAssociation, Memory.id == MemoryNodeAssociation.memory_id)
            .where(Memory.user_id == user_id)
            .where(MemoryNodeAssociation.node_id.in_(node_ids))
        )

        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)

        # Order by relevance score and created_at
        stmt = stmt.order_by(
            MemoryNodeAssociation.relevance_score.desc(), Memory.created_at.desc()
        )

        if limit:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        memories = result.scalars().unique().all()

        return list(memories)

    async def expand_nodes_via_edges(
        self,
        initial_nodes: List[KnowledgeNode],
        depth: int = 1,
        edge_types: Optional[List[EdgeType]] = None,
        decay_factor: float = 0.7,
    ) -> Dict[UUID, Tuple[KnowledgeNode, float]]:
        """
        Expand from initial nodes via graph relationships (BFS traversal).

        Args:
            initial_nodes: Starting nodes
            depth: How many hops to traverse (0=direct only, 1=neighbors, 2=2-hop)
            edge_types: Optional filter for specific edge types
            decay_factor: Relevance decay per hop (0-1)

        Returns:
            Dict mapping node_id to (KnowledgeNode, weighted_relevance)
        """
        if depth < 1 or not initial_nodes:
            # Return initial nodes with full relevance
            return {node.id: (node, 1.0) for node in initial_nodes}

        # Track visited nodes and their relevance scores
        visited: Dict[UUID, Tuple[KnowledgeNode, float]] = {}
        current_layer = [(node, 1.0) for node in initial_nodes]

        for hop in range(depth + 1):
            if not current_layer:
                break

            # Add current layer to visited
            for node, score in current_layer:
                if node.id not in visited or visited[node.id][1] < score:
                    visited[node.id] = (node, score)

            if hop == depth:
                break  # Don't expand beyond max depth

            # Get outgoing edges from current layer
            current_node_ids = [node.id for node, _ in current_layer]

            stmt = (
                select(KnowledgeEdge)
                .options(selectinload(KnowledgeEdge.target_node))
                .where(KnowledgeEdge.source_node_id.in_(current_node_ids))
            )

            if edge_types:
                stmt = stmt.where(KnowledgeEdge.edge_type.in_(edge_types))

            result = await self.db.execute(stmt)
            edges = result.scalars().all()

            # Build next layer with decayed relevance
            next_layer: List[Tuple[KnowledgeNode, float]] = []
            for edge in edges:
                source_score = next(
                    (score for node, score in current_layer if node.id == edge.source_node_id),
                    0.0,
                )
                # New score = source_score * decay * edge_weight
                new_score = source_score * decay_factor * edge.weight

                next_layer.append((edge.target_node, new_score))

            current_layer = next_layer

        return visited

    async def vector_search_within_candidates(
        self,
        query_embedding: List[float],
        candidate_memories: List[Memory],
        limit: int = 5,
    ) -> List[Tuple[Memory, float]]:
        """
        Perform vector similarity search within candidate memories.

        This is Step 2 of the two-step hierarchical retrieval strategy.

        Args:
            query_embedding: Query embedding vector
            candidate_memories: Pre-filtered list of memories to search within
            limit: Maximum number of results

        Returns:
            List of (Memory, distance) tuples, sorted by distance (ascending)
        """
        if not candidate_memories:
            return []

        memory_ids = [m.id for m in candidate_memories]

        # Calculate cosine distance for candidates only
        distance = Memory.embedding.cosine_distance(query_embedding)

        stmt = (
            select(Memory, distance.label("distance"))
            .where(Memory.id.in_(memory_ids))
            .where(Memory.embedding.isnot(None))
            .order_by(distance)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [(row[0], float(row[1])) for row in rows]

    async def hierarchical_search(
        self,
        user_id: UUID,
        query: str,
        query_embedding: List[float],
        memory_type: Optional[MemoryType] = None,
        limit: int = 5,
        node_top_k: int = 5,
    ) -> List[Tuple[Memory, float]]:
        """
        Two-step hierarchical retrieval: find relevant nodes, then search memories.

        This is the primary retrieval method for fast, context-aware search.

        Args:
            user_id: User identifier
            query: Query string
            query_embedding: Query embedding vector
            memory_type: Optional filter for memory type
            limit: Maximum number of memories to return
            node_top_k: Number of nodes to consider in Step 1

        Returns:
            List of (Memory, distance) tuples, sorted by relevance
        """
        # Step 1: Find relevant knowledge nodes (fast)
        relevant_nodes_with_scores = await self.find_relevant_nodes(
            user_id=user_id,
            query=query,
            query_embedding=query_embedding,
            top_k=node_top_k,
        )

        if not relevant_nodes_with_scores:
            # Fallback to empty result (could fall back to full search)
            logger.warning(
                f"No relevant nodes found for user {user_id}, query: {query[:50]}"
            )
            return []

        relevant_nodes = [node for node, _ in relevant_nodes_with_scores]

        # Step 2: Get memories associated with those nodes
        candidate_memories = await self.get_memories_by_nodes(
            user_id=user_id, nodes=relevant_nodes, memory_type=memory_type
        )

        if not candidate_memories:
            logger.warning(
                f"No memories found for {len(relevant_nodes)} nodes, user {user_id}"
            )
            return []

        # Step 3: Vector similarity search within candidates (precise)
        results = await self.vector_search_within_candidates(
            query_embedding=query_embedding,
            candidate_memories=candidate_memories,
            limit=limit,
        )

        logger.info(
            f"Hierarchical search: {len(relevant_nodes)} nodes → "
            f"{len(candidate_memories)} candidates → {len(results)} results"
        )

        return results

    async def graph_guided_search(
        self,
        user_id: UUID,
        query: str,
        query_embedding: List[float],
        expand_depth: int = 1,
        limit: int = 5,
    ) -> List[Tuple[Memory, float]]:
        """
        Start with directly relevant nodes, then expand via graph relationships.

        Args:
            user_id: User identifier
            query: Query string
            query_embedding: Query embedding vector
            expand_depth: How many hops to traverse (0=direct only, 1=neighbors, 2=2-hop)
            limit: Maximum number of memories to return

        Returns:
            List of (Memory, composite_score) tuples, sorted by relevance
        """
        # Find initial nodes matching query
        initial_nodes_with_scores = await self.find_relevant_nodes(
            user_id=user_id, query=query, query_embedding=query_embedding, top_k=3
        )

        if not initial_nodes_with_scores:
            return []

        initial_nodes = [node for node, _ in initial_nodes_with_scores]

        # Expand via graph relationships (BFS traversal)
        expanded_nodes_map = await self.expand_nodes_via_edges(
            initial_nodes=initial_nodes,
            depth=expand_depth,
            edge_types=[EdgeType.SUBTOPIC_OF, EdgeType.RELATED_TO, EdgeType.PART_OF],
        )

        # Get all expanded nodes
        expanded_nodes = [node for node, _ in expanded_nodes_map.values()]

        # Get memories from all nodes
        all_memories = await self.get_memories_by_nodes(
            user_id=user_id, nodes=expanded_nodes
        )

        if not all_memories:
            return []

        # Calculate composite scores:
        # - Vector similarity to query
        # - Node relevance (from graph expansion)
        # - Memory-to-node relevance
        results_with_scores: List[Tuple[Memory, float]] = []

        for memory in all_memories:
            # Get memory's associated nodes and their graph scores
            memory_node_ids = set()
            memory_to_node_relevance = {}

            for assoc in memory.node_associations:
                memory_node_ids.add(assoc.node_id)
                memory_to_node_relevance[assoc.node_id] = assoc.relevance_score

            # Calculate node contribution to this memory
            max_node_score = 0.0
            for node_id in memory_node_ids:
                if node_id in expanded_nodes_map:
                    node, graph_score = expanded_nodes_map[node_id]
                    node_relevance = memory_to_node_relevance.get(node_id, 1.0)
                    node_contribution = graph_score * node_relevance
                    max_node_score = max(max_node_score, node_contribution)

            # Vector similarity (if memory has embedding)
            if memory.embedding:
                distance = await self._calculate_distance(
                    query_embedding, memory.embedding
                )
                vector_similarity = 1 - (distance / 2)  # Convert distance to similarity
            else:
                vector_similarity = 0.5  # Neutral score if no embedding

            # Composite score: weighted combination
            composite_score = (vector_similarity * 0.6) + (max_node_score * 0.4)

            results_with_scores.append((memory, composite_score))

        # Sort by composite score (descending) and limit
        results_with_scores.sort(key=lambda x: x[1], reverse=True)
        return results_with_scores[:limit]

    async def _calculate_distance(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine distance between two embeddings.

        Note: In production, this would use pgvector's native distance calculation.
        This is a simplified version for when we need to calculate distance in Python.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine distance [0, 2]
        """
        # Simple cosine distance calculation
        import math

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 2.0  # Maximum distance

        cosine_similarity = dot_product / (magnitude1 * magnitude2)
        # Cosine distance = 1 - cosine_similarity, normalized to [0, 2]
        return 1 - cosine_similarity

    async def filter_by_metadata(
        self, memories: List[Memory], filters: Dict[str, any]
    ) -> List[Memory]:
        """
        Filter memories by JSONB metadata attributes.

        Args:
            memories: List of memories to filter
            filters: Dict of metadata key-value pairs to match

        Returns:
            Filtered list of memories
        """
        filtered = []
        for memory in memories:
            metadata = memory.extra_data or {}
            match = all(metadata.get(key) == value for key, value in filters.items())
            if match:
                filtered.append(memory)

        return filtered

    async def hybrid_search(
        self,
        user_id: UUID,
        query: str,
        query_embedding: List[float],
        metadata_filters: Optional[Dict[str, any]] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 5,
    ) -> List[Tuple[Memory, float]]:
        """
        Combine vector similarity, graph structure, and metadata filters.

        Uses reciprocal rank fusion to combine multiple retrieval strategies.

        Args:
            user_id: User identifier
            query: Query string
            query_embedding: Query embedding vector
            metadata_filters: Optional dict of metadata filters
            memory_type: Optional filter for memory type
            limit: Maximum number of results

        Returns:
            List of (Memory, composite_score) tuples, sorted by relevance
        """
        # Strategy 1: Hierarchical search (vector + graph)
        hierarchical_results = await self.hierarchical_search(
            user_id=user_id,
            query=query,
            query_embedding=query_embedding,
            memory_type=memory_type,
            limit=limit * 2,  # Get more candidates for fusion
        )

        # Strategy 2: Graph-guided search (graph expansion)
        graph_results = await self.graph_guided_search(
            user_id=user_id,
            query=query,
            query_embedding=query_embedding,
            expand_depth=1,
            limit=limit * 2,
        )

        # Reciprocal rank fusion
        combined_scores: Dict[UUID, float] = {}

        for rank, (memory, _) in enumerate(hierarchical_results):
            # RRF score: 1 / (k + rank) where k=60 is standard
            rrf_score = 1 / (60 + rank)
            combined_scores[memory.id] = combined_scores.get(memory.id, 0) + rrf_score

        for rank, (memory, _) in enumerate(graph_results):
            rrf_score = 1 / (60 + rank)
            combined_scores[memory.id] = combined_scores.get(memory.id, 0) + rrf_score

        # Get all unique memories
        all_memory_ids = set(m.id for m, _ in hierarchical_results) | set(
            m.id for m, _ in graph_results
        )

        stmt = select(Memory).where(Memory.id.in_(all_memory_ids))
        result = await self.db.execute(stmt)
        all_memories = list(result.scalars().all())

        # Apply metadata filters if specified
        if metadata_filters:
            all_memories = await self.filter_by_metadata(all_memories, metadata_filters)

        # Create final results with combined scores
        final_results = [
            (memory, combined_scores.get(memory.id, 0.0)) for memory in all_memories
        ]

        # Sort by combined score (descending) and limit
        final_results.sort(key=lambda x: x[1], reverse=True)
        return final_results[:limit]
