"""Multi-modal search strategies for memory retrieval.

This module implements 6 different search strategies for fast, flexible memory retrieval:

1. **Semantic Search**: Vector similarity using pgvector (best for conceptual queries)
2. **Keyword Search**: BM25 full-text search (best for specific terms)
3. **Categorical Search**: Filter by auto-generated categories (best for topic filtering)
4. **Temporal Search**: Time-based retrieval (best for recent/date-range queries)
5. **Graph Search**: Relationship traversal (best for connected knowledge)
6. **Hybrid Search**: Weighted combination of strategies (best for complex queries)

Each strategy returns unified SearchResult objects for consistent processing.
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryCollection
from app.models.user import User
from experiments.config import get_config
from experiments.memory.embedding_service import EmbeddingService
from experiments.memory.types import SearchResult, SearchStrategy, HybridSearchConfig


class BaseSearchStrategy:
    """Base class for all search strategies."""

    def __init__(self):
        """Initialize base strategy."""
        self.config = get_config()

    def _memory_to_search_result(
        self,
        memory: Memory,
        score: float,
        memory_type_override: Optional[str] = None
    ) -> SearchResult:
        """Convert Memory model to SearchResult.

        Args:
            memory: Memory ORM object
            score: Relevance score
            memory_type_override: Optional override for memory_type (uses memory.memory_type.value by default)

        Returns:
            SearchResult object
        """
        # Get categories from extra_data (which maps to metadata column)
        categories = []
        if memory.extra_data:
            categories = memory.extra_data.get("categories", [])

        return SearchResult(
            memory_id=memory.id,
            content=memory.content,
            score=score,
            memory_type=memory_type_override or memory.memory_type.value,
            categories=categories,
            created_at=memory.created_at,
            metadata=memory.extra_data or {}
        )


class SemanticSearch(BaseSearchStrategy):
    """Vector similarity search using pgvector.

    Best for: Conceptual queries, paraphrasing, related ideas
    Example: "What are my programming preferences?" (finds facts about coding likes/dislikes)

    This strategy uses cosine similarity (<=> operator in PostgreSQL with pgvector)
    to find memories with embeddings closest to the query embedding.
    """

    def __init__(self):
        """Initialize semantic search."""
        super().__init__()
        self.embedding_service = EmbeddingService()

    async def search(
        self,
        query: str,
        user_id: UUID,
        db: AsyncSession,
        limit: int = 10,
        threshold: float = 0.3,  # LOWERED from 0.7 to 0.3 for better recall
        memory_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search using vector similarity.

        Args:
            query: Search query text
            user_id: User ID to filter memories
            db: Database session
            limit: Maximum results
            threshold: Minimum similarity score (0-1)
            memory_types: Optional filter by memory types (personal, project, task)

        Returns:
            List of SearchResult sorted by similarity (descending)

        Example:
            >>> search = SemanticSearch()
            >>> results = await search.search(
            ...     query="programming languages I like",
            ...     user_id=user_id,
            ...     db=session
            ... )
        """
        # Generate query embedding
        print(f"      🔮 Generating embedding for query: '{query[:60]}...'")
        query_embedding = await self.embedding_service.embed_text(query)
        print(f"      ✅ Generated embedding (dim: {len(query_embedding)})")

        # Build query with pgvector similarity
        # Note: <=> is cosine distance, so smaller is better (1 - <=>  = similarity)
        stmt = (
            select(
                Memory,
                (1 - Memory.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .where(Memory.user_id == user_id)
            .where(Memory.embedding.isnot(None))  # Only memories with embeddings
        )

        # Filter by memory types if specified
        if memory_types:
            stmt = stmt.where(Memory.memory_type.in_(memory_types))

        # Order by similarity and limit
        stmt = stmt.order_by(text("similarity DESC")).limit(limit * 2)  # Get extra for filtering

        # Execute query
        print(f"      🔍 Executing vector similarity search (threshold: {threshold})...")
        result = await db.execute(stmt)
        rows = result.all()
        print(f"      📊 Database returned {len(rows)} memories with embeddings")

        # Convert to SearchResults and filter by threshold
        results = []
        below_threshold = 0
        for memory, similarity in rows:
            if similarity >= threshold:
                results.append(
                    self._memory_to_search_result(memory, similarity)
                )
                if len(results) <= 3:
                    print(f"         ✅ [{similarity:.3f}] {memory.content[:80]}...")
            else:
                below_threshold += 1

        if below_threshold > 0:
            print(f"      ⚠️ Filtered out {below_threshold} memories below threshold {threshold}")

        print(f"      ✅ Returning {len(results[:limit])} results")

        # Return top results
        return results[:limit]


class KeywordSearch(BaseSearchStrategy):
    """BM25 full-text search using PostgreSQL.

    Best for: Specific terms, names, exact phrases
    Example: "Python FastAPI" (finds memories containing these exact keywords)

    This strategy uses PostgreSQL's full-text search with ts_rank_cd
    for BM25-like scoring.
    """

    async def search(
        self,
        query: str,
        user_id: UUID,
        db: AsyncSession,
        limit: int = 10,
        memory_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search using keyword matching and BM25 scoring.

        Args:
            query: Search query with keywords
            user_id: User ID to filter memories
            db: Database session
            limit: Maximum results
            memory_types: Optional filter by memory types

        Returns:
            List of SearchResult sorted by relevance

        Example:
            >>> search = KeywordSearch()
            >>> results = await search.search(
            ...     query="typescript fastapi",
            ...     user_id=user_id,
            ...     db=session
            ... )
        """
        # Prepare search query (tsquery format)
        # Remove common stop words and use OR for better recall
        stop_words = {
            'hi', 'hello', 'hey', 'do', 'does', 'did', 'you', 'your', 'the', 'a', 'an',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must',
            'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours',
            'what', 'which', 'who', 'when', 'where', 'why', 'how',
            'remember', 'recall', 'know', 'tell', 'show', 'find'
        }

        # Extract meaningful words (remove stop words)
        words = [w.lower() for w in query.strip().split() if w.lower() not in stop_words]

        # If no meaningful words left, use original query
        if not words:
            words = query.strip().split()

        # Use OR (|) instead of AND (&) for better recall
        # "city like" → "city | like" (matches memories containing EITHER word)
        search_terms = " | ".join(words)

        print(f"      🔤 Keyword search: '{query}' → '{search_terms}'")

        # Build full-text search query
        # Uses to_tsvector for text indexing and ts_rank_cd for BM25-like scoring
        stmt = (
            select(
                Memory,
                func.ts_rank_cd(
                    func.to_tsvector('english', Memory.content),
                    func.to_tsquery('english', search_terms)
                ).label("rank")
            )
            .where(Memory.user_id == user_id)
            .where(
                func.to_tsvector('english', Memory.content).op('@@')(
                    func.to_tsquery('english', search_terms)
                )
            )
        )

        # Filter by memory types if specified
        if memory_types:
            stmt = stmt.where(Memory.memory_type.in_(memory_types))

        # Order by rank and limit
        stmt = stmt.order_by(text("rank DESC")).limit(limit)

        # Execute query
        result = await db.execute(stmt)
        rows = result.all()

        # Convert to SearchResults
        # Normalize rank scores to 0-1 range
        max_rank = max([row[1] for row in rows], default=1.0)

        results = []
        for memory, rank in rows:
            normalized_score = rank / max_rank if max_rank > 0 else 0.5
            results.append(
                self._memory_to_search_result(memory, normalized_score)
            )

        return results


class CategoricalSearch(BaseSearchStrategy):
    """Filter by auto-generated categories.

    Best for: Topic filtering, browsing by category
    Example: "programming preferences" (finds all memories in these categories)

    This strategy filters memories whose metadata contains matching categories,
    using JSONB operators for efficient category matching.
    """

    async def search(
        self,
        categories: List[str],
        user_id: UUID,
        db: AsyncSession,
        limit: int = 10,
        match_all: bool = False,
        memory_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search by categories.

        Args:
            categories: List of categories to match
            user_id: User ID to filter memories
            db: Database session
            limit: Maximum results
            match_all: If True, require all categories; if False, any category
            memory_types: Optional filter by memory types

        Returns:
            List of SearchResult sorted by recency

        Example:
            >>> search = CategoricalSearch()
            >>> results = await search.search(
            ...     categories=["programming", "preferences"],
            ...     user_id=user_id,
            ...     db=session
            ... )
        """
        # Build JSONB category filter
        # metadata->'categories' ?| array['cat1', 'cat2'] (contains any)
        # metadata->'categories' ?& array['cat1', 'cat2'] (contains all)

        # Build JSONB filter - check if categories array contains search categories
        # Use PostgreSQL JSONB ?| (contains any) or ?& (contains all) operators
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
        )
        
        # Add category filter using JSONB array operators
        if categories:
            # Build condition: metadata->'categories' ?| array['cat1', 'cat2'] (any)
            # or metadata->'categories' ?& array['cat1', 'cat2'] (all)
            jsonb_op = "?&" if match_all else "?|"
            # Create array literal for PostgreSQL (escape single quotes in category names)
            escaped_categories = [cat.replace("'", "''") for cat in categories]
            category_array_str = "ARRAY[" + ",".join([f"'{cat}'" for cat in escaped_categories]) + "]"
            
            stmt = stmt.where(
                text(f"memories.metadata->'categories' {jsonb_op} {category_array_str}")
            )

        # Filter by memory types if specified
        if memory_types:
            stmt = stmt.where(Memory.memory_type.in_(memory_types))

        # Order by recency (most recent first)
        stmt = stmt.order_by(Memory.created_at.desc()).limit(limit)

        # Execute query
        result = await db.execute(stmt)
        memories = result.scalars().all()

        # Convert to SearchResults
        # Score based on how many categories match
        results = []
        for memory in memories:
            memory_categories = memory.extra_data.get("categories", []) if memory.extra_data else []
            matches = len(set(categories) & set(memory_categories))
            score = matches / len(categories) if categories else 0.5

            results.append(
                self._memory_to_search_result(memory, score)
            )

        return results


class TemporalSearch(BaseSearchStrategy):
    """Time-based memory retrieval.

    Best for: Recent queries, date ranges, time-ordered events
    Example: "last week", "Q1 2025", "recent programming work"

    This strategy filters memories by creation timestamp and supports:
    - Relative time (last week, yesterday, etc.)
    - Absolute date ranges
    - Recency-based scoring
    """

    async def search(
        self,
        user_id: UUID,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        relative_time: Optional[str] = None,
        limit: int = 10,
        memory_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search by time range.

        Args:
            user_id: User ID to filter memories
            db: Database session
            start_date: Start of time range (inclusive)
            end_date: End of time range (inclusive)
            relative_time: Relative time string (e.g., "1 week", "3 days")
            limit: Maximum results
            memory_types: Optional filter by memory types

        Returns:
            List of SearchResult sorted by recency

        Example:
            >>> search = TemporalSearch()
            >>> # Last week
            >>> results = await search.search(
            ...     user_id=user_id,
            ...     db=session,
            ...     relative_time="1 week"
            ... )
            >>> # Specific date range
            >>> results = await search.search(
            ...     user_id=user_id,
            ...     db=session,
            ...     start_date=datetime(2024, 11, 1),
            ...     end_date=datetime(2024, 11, 30)
            ... )
        """
        # Handle relative time
        if relative_time:
            end_date = datetime.now()
            start_date = self._parse_relative_time(relative_time)

        # Build query
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
        )

        # Add time filters
        if start_date:
            stmt = stmt.where(Memory.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Memory.created_at <= end_date)

        # Filter by memory types if specified
        if memory_types:
            stmt = stmt.where(Memory.memory_type.in_(memory_types))

        # Order by recency
        stmt = stmt.order_by(Memory.created_at.desc()).limit(limit)

        # Execute query
        result = await db.execute(stmt)
        memories = result.scalars().all()

        # Convert to SearchResults with recency-based scoring
        now = datetime.now()
        results = []
        for memory in memories:
            # Score based on recency (exponential decay)
            age_hours = (now - memory.created_at).total_seconds() / 3600
            score = 1.0 / (1.0 + age_hours / 24.0)  # Decay over days

            results.append(
                self._memory_to_search_result(memory, score)
            )

        return results

    def _parse_relative_time(self, relative_time: str) -> datetime:
        """Parse relative time string to datetime.

        Args:
            relative_time: String like "1 week", "3 days", "2 hours"

        Returns:
            Datetime in the past

        Example:
            >>> search._parse_relative_time("1 week")
            datetime.datetime(2024, 11, 11, ...)  # 1 week ago
        """
        parts = relative_time.lower().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid relative time format: {relative_time}")

        try:
            amount = int(parts[0])
            unit = parts[1].rstrip('s')  # Remove plural 's'

            if unit in ['hour', 'hr', 'h']:
                delta = timedelta(hours=amount)
            elif unit in ['day', 'd']:
                delta = timedelta(days=amount)
            elif unit in ['week', 'wk', 'w']:
                delta = timedelta(weeks=amount)
            elif unit in ['month', 'mo', 'm']:
                delta = timedelta(days=amount * 30)  # Approximate
            else:
                raise ValueError(f"Unknown time unit: {unit}")

            return datetime.now() - delta

        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse relative time '{relative_time}': {e}")


class GraphSearch(BaseSearchStrategy):
    """Graph traversal for related memories.

    Best for: Finding connected knowledge, relationship queries
    Example: "What's related to my Delight project?"

    This strategy performs BFS traversal of the memory graph using
    relationship metadata stored in JSONB fields.
    """

    async def search(
        self,
        root_memory_id: UUID,
        db: AsyncSession,
        max_depth: int = 3,
        relationship_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search by traversing memory relationships.

        Args:
            root_memory_id: Starting memory node
            db: Database session
            max_depth: Maximum traversal depth
            relationship_types: Filter by relationship types
            limit: Maximum results

        Returns:
            List of SearchResult sorted by graph distance

        Example:
            >>> search = GraphSearch()
            >>> results = await search.search(
            ...     root_memory_id=project_memory_id,
            ...     db=session,
            ...     max_depth=2
            ... )
        """
        # Fetch root memory
        stmt = select(Memory).where(Memory.id == root_memory_id)
        result = await db.execute(stmt)
        root_memory = result.scalar_one_or_none()

        if not root_memory:
            return []

        # BFS traversal
        visited: Set[UUID] = {root_memory_id}
        queue: List[Tuple[UUID, int]] = [(root_memory_id, 0)]  # (memory_id, depth)
        found_memories: List[Tuple[Memory, int]] = []

        while queue and len(found_memories) < limit * 2:
            current_id, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Fetch current memory
            stmt = select(Memory).where(Memory.id == current_id)
            result = await db.execute(stmt)
            current_memory = result.scalar_one_or_none()

            if not current_memory:
                continue

            # Get relationships from extra_data (which maps to metadata column)
            relationships = current_memory.extra_data.get("relationships", {}) if current_memory.extra_data else {}

            # Traverse relationships
            for rel_type, target_ids in relationships.items():
                # Filter by relationship types if specified
                if relationship_types and rel_type not in relationship_types:
                    continue

                for target_id_str in target_ids:
                    try:
                        target_id = UUID(target_id_str)
                    except ValueError:
                        continue

                    if target_id not in visited:
                        visited.add(target_id)
                        queue.append((target_id, depth + 1))

                        # Fetch target memory
                        stmt = select(Memory).where(Memory.id == target_id)
                        result = await db.execute(stmt)
                        memory = result.scalar_one_or_none()

                        if memory:
                            found_memories.append((memory, depth + 1))

        # Convert to SearchResults with distance-based scoring
        results = []
        for memory, depth in found_memories[:limit]:
            # Score inversely proportional to depth
            score = 1.0 / (depth + 1)

            results.append(
                self._memory_to_search_result(memory, score)
            )

        return results


class HybridSearch(BaseSearchStrategy):
    """Weighted combination of multiple search strategies.

    Best for: Complex queries requiring multiple approaches
    Example: "Recent programming decisions for my AI project"
    (combines temporal + categorical + semantic)

    This strategy runs multiple searches in parallel and combines
    their results using weighted scoring.
    """

    def __init__(self):
        """Initialize hybrid search with all strategies."""
        super().__init__()
        self.semantic = SemanticSearch()
        self.keyword = KeywordSearch()
        self.categorical = CategoricalSearch()
        self.temporal = TemporalSearch()
        self.graph = GraphSearch()

    async def search(
        self,
        query: str,
        user_id: UUID,
        db: AsyncSession,
        config: Optional[HybridSearchConfig] = None,
        limit: int = 10,
        memory_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search using weighted combination of strategies.

        Args:
            query: Search query
            user_id: User ID
            db: Database session
            config: Hybrid search configuration (weights, etc.)
            limit: Maximum results
            memory_types: Optional filter by memory types

        Returns:
            List of SearchResult with combined scores

        Example:
            >>> search = HybridSearch()
            >>> config = HybridSearchConfig(weights={
            ...     SearchStrategy.SEMANTIC: 0.7,
            ...     SearchStrategy.KEYWORD: 0.3
            ... })
            >>> results = await search.search(
            ...     query="python programming",
            ...     user_id=user_id,
            ...     db=session,
            ...     config=config
            ... )
        """
        # Default config: 70% semantic, 30% keyword
        if config is None:
            config = HybridSearchConfig(weights={
                SearchStrategy.SEMANTIC: 0.7,
                SearchStrategy.KEYWORD: 0.3
            })

        # Run searches in parallel
        tasks = []
        strategies = []

        for strategy, weight in config.weights.items():
            if strategy == SearchStrategy.SEMANTIC:
                task = self.semantic.search(query, user_id, db, limit * 2, memory_types=memory_types)
            elif strategy == SearchStrategy.KEYWORD:
                task = self.keyword.search(query, user_id, db, limit * 2, memory_types=memory_types)
            # Add more strategies as configured

            if task:
                tasks.append(task)
                strategies.append((strategy, weight))

        # Execute all searches
        results_list = await asyncio.gather(*tasks)

        # Combine results with weighted scores
        memory_scores: Dict[UUID, float] = defaultdict(float)
        memory_objects: Dict[UUID, SearchResult] = {}

        for results, (strategy, weight) in zip(results_list, strategies):
            for result in results:
                memory_scores[result.memory_id] += result.score * weight
                memory_objects[result.memory_id] = result

        # Sort by combined score
        sorted_memories = sorted(
            memory_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Build final results
        final_results = []
        for memory_id, combined_score in sorted_memories[:limit]:
            result = memory_objects[memory_id]
            result.score = combined_score
            result.match_explanation = f"Hybrid search (combined score: {combined_score:.3f})"
            final_results.append(result)

        return final_results


if __name__ == "__main__":
    """Example usage and testing (requires database setup)."""
    print("""
Search Strategies Module
========================

This module provides 6 search strategies:

1. SemanticSearch - Vector similarity (best for concepts)
2. KeywordSearch - BM25 full-text (best for specific terms)
3. CategoricalSearch - Filter by categories (best for topics)
4. TemporalSearch - Time-based (best for recency)
5. GraphSearch - Relationship traversal (best for connected knowledge)
6. HybridSearch - Combined approach (best for complex queries)

Usage examples:
    # Semantic search
    semantic = SemanticSearch()
    results = await semantic.search("programming preferences", user_id, db)

    # Keyword search
    keyword = KeywordSearch()
    results = await keyword.search("Python FastAPI", user_id, db)

    # Categorical search
    categorical = CategoricalSearch()
    results = await categorical.search(["programming", "preferences"], user_id, db)

    # Temporal search
    temporal = TemporalSearch()
    results = await temporal.search(user_id, db, relative_time="1 week")

    # Hybrid search
    hybrid = HybridSearch()
    results = await hybrid.search("recent AI projects", user_id, db)

See individual class docstrings for more details.
    """)
