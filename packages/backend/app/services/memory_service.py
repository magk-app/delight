"""
Memory service implementing 3-tier architecture with hybrid search.

Provides memory management for personal, project, and task memories with:
- Automatic embedding generation (OpenAI text-embedding-3-small)
- Hybrid search combining semantic similarity, time decay, and access frequency
- Memory pruning for task tier (30-day retention)
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryType
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing AI companion memory system with 3-tier architecture.

    **3-Tier Memory Architecture:**
    - **Personal**: Identity, preferences, emotional patterns (never pruned)
    - **Project**: Goals, plans, progress snapshots (never pruned)
    - **Task**: Mission details, conversation context (pruned after 30 days)

    **Hybrid Search Algorithm:**
    Combines three signals for optimal memory retrieval:
    1. Semantic similarity: Vector cosine distance (base score)
    2. Time boost: Recent memories prioritized (recency bias)
    3. Frequency boost: Frequently accessed memories prioritized (importance signal)

    Final Score = similarity * time_boost * frequency_boost

    Example:
        >>> service = MemoryService(db)
        >>> memory = await service.add_memory(
        ...     user_id=user.id,
        ...     memory_type=MemoryType.PERSONAL,
        ...     content="I prefer working in the morning",
        ...     metadata={"category": "preferences"}
        ... )
        >>> results = await service.query_memories(user.id, "work preferences")
    """

    def __init__(self, db: AsyncSession, embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize memory service.

        Args:
            db: Async database session
            embedding_service: Optional custom embedding service (defaults to new instance)
        """
        self.db = db
        self.embedding_service = embedding_service or EmbeddingService()

    async def add_memory(
        self,
        user_id: UUID,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Create a new memory with automatic embedding generation.

        Generates vector embedding using OpenAI API. If embedding fails,
        memory is still created (with embedding=None) to maintain data integrity.

        Args:
            user_id: UUID of user who owns this memory
            memory_type: Memory tier (PERSONAL, PROJECT, or TASK)
            content: Human-readable memory content
            metadata: Optional metadata (stressor info, emotion scores, goal references)

        Returns:
            Created Memory instance

        Example:
            >>> memory = await service.add_memory(
            ...     user_id=UUID("..."),
            ...     memory_type=MemoryType.PERSONAL,
            ...     content="Class registration stress and debt email anxiety",
            ...     metadata={
            ...         "stressor": True,
            ...         "emotion": "fear",
            ...         "category": "academic",
            ...         "intensity": 0.8
            ...     }
            ... )
        """
        # Generate embedding (None if fails after retries)
        embedding = await self.embedding_service.generate_embedding(content)

        if embedding is None:
            logger.warning(
                f"Failed to generate embedding for memory (user_id={user_id}, "
                f"type={memory_type}). Storing without embedding."
            )

        # Create memory instance
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            extra_data=metadata or {},  # Maps to 'metadata' column in DB
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
        )

        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)

        logger.info(
            f"Created memory: id={memory.id}, user_id={user_id}, type={memory_type}, "
            f"has_embedding={embedding is not None}"
        )

        return memory

    async def query_memories(
        self,
        user_id: UUID,
        query_text: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[Memory]:
        """
        Query memories using hybrid search (semantic + time + frequency).

        **Hybrid Search Algorithm:**
        1. Generate query embedding
        2. Calculate base similarity score (cosine distance)
        3. Apply time boost: recent memories prioritized
        4. Apply frequency boost: frequently accessed memories prioritized
        5. Calculate final score: similarity * time_boost * frequency_boost
        6. Sort by final score (descending)
        7. Update access tracking for retrieved memories

        **Scoring Formulas:**
        - Time Boost: `1 + log(1 + days_since_access + 1)^-1`
        - Frequency Boost: `1 + (log(access_count) * 0.1)`

        Args:
            user_id: UUID of user querying memories
            query_text: Natural language query for semantic search
            memory_types: Optional filter by memory tiers (defaults to all types)
            limit: Maximum number of memories to return
            similarity_threshold: Minimum similarity score (0.0-1.0, higher = stricter)

        Returns:
            List of Memory objects sorted by final hybrid score

        Example:
            >>> # Query personal memories only
            >>> results = await service.query_memories(
            ...     user_id=user.id,
            ...     query_text="coffee preferences",
            ...     memory_types=[MemoryType.PERSONAL]
            ... )
            >>>
            >>> # Query all memory types
            >>> results = await service.query_memories(
            ...     user_id=user.id,
            ...     query_text="recent activities"
            ... )
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query_text)

        if query_embedding is None:
            logger.error(
                f"Failed to generate query embedding for user_id={user_id}, "
                f"query='{query_text[:100]}'"
            )
            return []

        # Build base query
        query = select(Memory).where(Memory.user_id == user_id)

        # Filter by memory types if specified
        if memory_types:
            query = query.where(Memory.memory_type.in_(memory_types))

        # Filter out memories without embeddings
        query = query.where(Memory.embedding.is_not(None))

        # Add vector similarity calculation (cosine distance)
        # Note: pgvector's <=> operator returns cosine distance (0=identical, 2=opposite)
        # We convert to similarity: similarity = 1 - (distance / 2) for range [0, 1]
        query = query.add_columns(
            Memory.embedding.cosine_distance(query_embedding).label("distance")
        )

        # Execute query
        result = await self.db.execute(query)
        rows = result.all()

        # Calculate hybrid scores and filter by threshold
        scored_memories = []
        now = datetime.utcnow()

        for memory, distance in rows:
            # Convert distance to similarity score (0-1 range, 1=identical)
            similarity = 1 - (distance / 2)

            # Filter by similarity threshold
            if similarity < similarity_threshold:
                continue

            # Calculate time boost (recent memories prioritized)
            days_since_access = (now - memory.accessed_at).days
            time_boost = self._calculate_time_boost(days_since_access)

            # Calculate frequency boost (frequently accessed memories prioritized)
            access_count = memory.extra_data.get("access_count", 0) if memory.extra_data else 0
            frequency_boost = self._calculate_frequency_boost(access_count)

            # Calculate final score
            final_score = similarity * time_boost * frequency_boost

            scored_memories.append((memory, final_score, similarity, time_boost, frequency_boost))

        # Sort by final score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        # Take top N results
        top_memories = [item[0] for item in scored_memories[:limit]]

        # Update access tracking for retrieved memories
        if top_memories:
            await self._update_access_tracking(top_memories)

        logger.info(
            f"Query returned {len(top_memories)} memories (user_id={user_id}, "
            f"query='{query_text[:50]}', filtered_by_threshold={len(rows) - len(scored_memories)})"
        )

        return top_memories

    async def prune_old_task_memories(self, retention_days: int = 30) -> int:
        """
        Delete task memories older than retention period.

        Only task memories are pruned. Personal and project memories are
        never deleted (permanent retention for identity and goals).

        Args:
            retention_days: Number of days to retain task memories (default: 30)

        Returns:
            Number of memories deleted

        Example:
            >>> deleted_count = await service.prune_old_task_memories()
            >>> print(f"Pruned {deleted_count} old task memories")
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Delete task memories older than cutoff
        delete_stmt = (
            delete(Memory)
            .where(Memory.memory_type == MemoryType.TASK)
            .where(Memory.created_at < cutoff_date)
        )

        result = await self.db.execute(delete_stmt)
        await self.db.commit()

        deleted_count = result.rowcount

        logger.info(
            f"Pruned {deleted_count} task memories older than {retention_days} days "
            f"(cutoff: {cutoff_date.isoformat()})"
        )

        return deleted_count

    def _calculate_time_boost(self, days_since_access: int) -> float:
        """
        Calculate time boost factor for hybrid scoring.

        Formula: `1 + log(1 + days_since_access + 1)^-1`

        Recent memories get higher boost:
        - 0 days: boost ≈ 1.44
        - 7 days: boost ≈ 1.13
        - 30 days: boost ≈ 1.03
        - 365 days: boost ≈ 1.00

        Args:
            days_since_access: Days since last access

        Returns:
            Time boost multiplier (>= 1.0)
        """
        # Handle edge case: negative days
        if days_since_access < 0:
            days_since_access = 0

        # Calculate boost: more recent = higher boost
        boost = 1 + (1 / math.log(1 + days_since_access + 1))

        return boost

    def _calculate_frequency_boost(self, access_count: int) -> float:
        """
        Calculate frequency boost factor for hybrid scoring.

        Formula: `1 + (log(access_count) * 0.1)`

        Frequently accessed memories get higher boost:
        - 1 access: boost = 1.0
        - 10 accesses: boost ≈ 1.23
        - 100 accesses: boost ≈ 1.46
        - 1000 accesses: boost ≈ 1.69

        Args:
            access_count: Number of times memory has been accessed

        Returns:
            Frequency boost multiplier (>= 1.0)
        """
        # Handle edge case: zero or negative count
        if access_count <= 0:
            access_count = 1

        # Calculate boost: more accesses = higher boost
        boost = 1 + (math.log(access_count) * 0.1)

        return boost

    async def _update_access_tracking(self, memories: List[Memory]) -> None:
        """
        Update access timestamps and counts for retrieved memories.

        Updates:
        - accessed_at: Set to current timestamp
        - access_count: Increment by 1 (stored in metadata)

        Args:
            memories: List of Memory objects to update

        Note:
            Commits changes to database automatically.
        """
        now = datetime.utcnow()

        for memory in memories:
            # Update accessed_at timestamp
            memory.accessed_at = now

            # Increment access_count in metadata
            if memory.extra_data is None:
                memory.extra_data = {}

            access_count = memory.extra_data.get("access_count", 0)
            memory.extra_data["access_count"] = access_count + 1

        await self.db.commit()

        logger.debug(f"Updated access tracking for {len(memories)} memories")
