"""
MemoryService - Core service for memory CRUD and intelligent retrieval

Features:
- 3-tier memory architecture (PERSONAL, PROJECT, TASK)
- Hybrid search: semantic similarity + time decay + access frequency
- Automatic embedding generation via EmbeddingService
- Strategic querying: different strategies per tier
- Memory pruning for TASK tier (30-day retention)
- Dynamic priority calculation from user memories

Architecture:
    ┌─────────────────┐
    │  MemoryService  │
    │                 │
    │  - add_memory() │──► EmbeddingService ──► OpenAI API
    │  - query()      │──► Hybrid Search Algorithm
    │  - prune()      │──► Background Worker (ARQ)
    └─────────────────┘

Hybrid Search Algorithm:
    Base: Cosine similarity from pgvector (1 - distance/2)
    Time Boost: 1 + log(1 + days_since_access + 1)^-1
    Frequency Boost: 1 + (log(access_count) * 0.1)
    Final Score: similarity * time_boost * frequency_boost
"""

import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryType
from app.schemas.memory import (
    MemoryCreate,
    MemoryResponse,
    MemoryUpdate,
    MemoryWithDistance,
)
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for intelligent memory management with hybrid search"""

    def __init__(self):
        """Initialize memory service with embedding service"""
        self.embedding_service = get_embedding_service()
        self.task_retention_days = 30  # TASK memories pruned after 30 days
        self.personal_top_k = 5  # Always retrieve top 5 personal memories
        self.project_top_k = 10  # Retrieve top 10 project memories
        self.task_top_k = 5  # Retrieve top 5 recent task memories

    async def add_memory(
        self, db: AsyncSession, user_id: UUID, memory_data: MemoryCreate
    ) -> Memory:
        """
        Create new memory with automatic embedding generation

        Args:
            db: Database session
            user_id: User ID owning this memory
            memory_data: Memory content and metadata

        Returns:
            Created Memory object with embedding

        Raises:
            ValueError: If embedding generation fails and content is not empty
        """
        # Generate embedding for content
        embedding = None
        if memory_data.content and memory_data.content.strip():
            embedding = await self.embedding_service.generate_embedding(memory_data.content)

            if embedding is None:
                logger.warning(
                    f"Failed to generate embedding for memory. "
                    f"Content: {memory_data.content[:50]}..."
                )
                # Continue without embedding - memory still created but not semantically searchable

        # Create memory object
        memory = Memory(
            user_id=user_id,
            memory_type=memory_data.memory_type,
            content=memory_data.content,
            embedding=embedding,
            extra_data=memory_data.metadata or {},
            created_at=datetime.now(timezone.utc),
            accessed_at=datetime.now(timezone.utc),
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        logger.info(
            f"Created {memory_data.memory_type} memory for user {user_id}: "
            f"{memory_data.content[:50]}..."
        )

        return memory

    async def get_memory(
        self, db: AsyncSession, user_id: UUID, memory_id: UUID
    ) -> Optional[Memory]:
        """
        Retrieve single memory by ID and update access time

        Args:
            db: Database session
            user_id: User ID for authorization
            memory_id: Memory ID to retrieve

        Returns:
            Memory object or None if not found
        """
        result = await db.execute(
            select(Memory).where(and_(Memory.id == memory_id, Memory.user_id == user_id))
        )
        memory = result.scalar_one_or_none()

        if memory:
            # Update access time for LRU tracking
            memory.accessed_at = datetime.now(timezone.utc)
            await db.commit()

        return memory

    async def update_memory(
        self, db: AsyncSession, user_id: UUID, memory_id: UUID, update_data: MemoryUpdate
    ) -> Optional[Memory]:
        """
        Update existing memory and regenerate embedding if content changed

        Args:
            db: Database session
            user_id: User ID for authorization
            memory_id: Memory ID to update
            update_data: Fields to update

        Returns:
            Updated Memory object or None if not found
        """
        memory = await self.get_memory(db, user_id, memory_id)
        if not memory:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)

        # If content changed, regenerate embedding
        if "content" in update_dict and update_dict["content"] != memory.content:
            new_embedding = await self.embedding_service.generate_embedding(
                update_dict["content"]
            )
            if new_embedding:
                update_dict["embedding"] = new_embedding

        # Apply updates
        for field, value in update_dict.items():
            if field == "metadata":
                setattr(memory, "extra_data", value)
            else:
                setattr(memory, field, value)

        await db.commit()
        await db.refresh(memory)

        logger.info(f"Updated memory {memory_id} for user {user_id}")
        return memory

    async def delete_memory(
        self, db: AsyncSession, user_id: UUID, memory_id: UUID
    ) -> bool:
        """
        Delete memory by ID

        Args:
            db: Database session
            user_id: User ID for authorization
            memory_id: Memory ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            delete(Memory).where(and_(Memory.id == memory_id, Memory.user_id == user_id))
        )
        await db.commit()

        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted memory {memory_id} for user {user_id}")
        return deleted

    async def query_memories(
        self,
        db: AsyncSession,
        user_id: UUID,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Memory]:
        """
        Query memories by type with pagination

        Args:
            db: Database session
            user_id: User ID to query
            memory_type: Optional filter by memory tier
            limit: Max results (1-100)
            offset: Pagination offset

        Returns:
            List of Memory objects ordered by access time (most recent first)
        """
        query = select(Memory).where(Memory.user_id == user_id)

        if memory_type:
            query = query.where(Memory.memory_type == memory_type)

        query = query.order_by(desc(Memory.accessed_at)).limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def semantic_search(
        self,
        db: AsyncSession,
        user_id: UUID,
        query_text: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        similarity_threshold: float = 0.5,
    ) -> List[MemoryWithDistance]:
        """
        Hybrid semantic search with time decay and frequency boosting

        Algorithm:
            1. Generate embedding for query text
            2. Find similar memories using cosine distance (pgvector)
            3. Apply time boost: recent memories prioritized
            4. Apply frequency boost: frequently accessed memories boosted
            5. Calculate final score and rank

        Args:
            db: Database session
            user_id: User ID to search
            query_text: Text to find similar memories for
            memory_type: Optional filter by memory tier
            limit: Max results
            similarity_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of MemoryWithDistance sorted by hybrid score (highest first)
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query_text)
        if not query_embedding:
            logger.error(f"Failed to generate embedding for search query: {query_text}")
            return []

        # Build query with vector similarity
        # Note: pgvector cosine_distance returns 0-2 (0=identical, 2=opposite)
        # We convert to similarity: 1 - (distance / 2) = 0.0-1.0 scale
        query = (
            select(
                Memory,
                (Memory.embedding.cosine_distance(query_embedding)).label("distance"),
            )
            .where(Memory.user_id == user_id)
            .where(Memory.embedding.isnot(None))  # Only search memories with embeddings
        )

        if memory_type:
            query = query.where(Memory.memory_type == memory_type)

        # Execute query
        result = await db.execute(query)
        rows = result.all()

        # Apply hybrid scoring algorithm
        scored_memories: List[Tuple[Memory, float, float]] = []
        now = datetime.now(timezone.utc)

        for memory, distance in rows:
            # Base similarity: convert distance to similarity (0-1 scale)
            base_similarity = 1.0 - (distance / 2.0)

            # Skip if below threshold
            if base_similarity < similarity_threshold:
                continue

            # Time boost: recent memories prioritized
            days_since_access = (now - memory.accessed_at).total_seconds() / 86400
            time_boost = 1.0 + (1.0 / math.log1p(days_since_access + 1))

            # Frequency boost: use metadata access_count if available
            access_count = (
                memory.extra_data.get("access_count", 1) if memory.extra_data else 1
            )
            frequency_boost = 1.0 + (math.log1p(access_count) * 0.1)

            # Final hybrid score
            final_score = base_similarity * time_boost * frequency_boost

            scored_memories.append((memory, base_similarity, final_score))

            # Update access count
            if not memory.extra_data:
                memory.extra_data = {}
            memory.extra_data["access_count"] = access_count + 1
            memory.accessed_at = now

        # Commit access tracking updates
        await db.commit()

        # Sort by final score (highest first) and limit results
        scored_memories.sort(key=lambda x: x[2], reverse=True)
        scored_memories = scored_memories[:limit]

        # Convert to MemoryWithDistance schema
        results = [
            MemoryWithDistance(
                id=memory.id,
                user_id=memory.user_id,
                memory_type=memory.memory_type,
                content=memory.content,
                metadata=memory.extra_data or {},
                created_at=memory.created_at,
                accessed_at=memory.accessed_at,
                distance=distance,
                similarity_score=final_score,
            )
            for memory, distance, final_score in scored_memories
        ]

        logger.info(
            f"Semantic search for user {user_id}: found {len(results)} memories "
            f"(query: {query_text[:50]}...)"
        )

        return results

    async def strategic_context_retrieval(
        self, db: AsyncSession, user_id: UUID, query_text: str
    ) -> Dict[str, List[MemoryWithDistance]]:
        """
        3-tier strategic retrieval for AI agent context building

        Strategy:
            - PERSONAL: Always retrieve top 5 (identity, preferences, stressors)
            - PROJECT: Retrieve top 10 if query mentions goals/plans
            - TASK: Retrieve top 5 recent conversations/actions

        Args:
            db: Database session
            user_id: User ID
            query_text: Current conversation context

        Returns:
            Dict with keys: "personal", "project", "task"
            Each contains list of relevant memories
        """
        context = {
            "personal": [],
            "project": [],
            "task": [],
        }

        # PERSONAL: Always retrieve (core identity)
        context["personal"] = await self.semantic_search(
            db,
            user_id,
            query_text,
            memory_type=MemoryType.PERSONAL,
            limit=self.personal_top_k,
            similarity_threshold=0.3,  # Lower threshold for personal
        )

        # PROJECT: Retrieve if goal-related keywords detected
        goal_keywords = ["goal", "plan", "progress", "achieve", "milestone", "ambition"]
        if any(keyword in query_text.lower() for keyword in goal_keywords):
            context["project"] = await self.semantic_search(
                db,
                user_id,
                query_text,
                memory_type=MemoryType.PROJECT,
                limit=self.project_top_k,
                similarity_threshold=0.4,
            )

        # TASK: Recent conversation context
        context["task"] = await self.semantic_search(
            db,
            user_id,
            query_text,
            memory_type=MemoryType.TASK,
            limit=self.task_top_k,
            similarity_threshold=0.4,
        )

        total_memories = sum(len(v) for v in context.values())
        logger.info(
            f"Strategic retrieval for user {user_id}: "
            f"{len(context['personal'])} personal, "
            f"{len(context['project'])} project, "
            f"{len(context['task'])} task "
            f"({total_memories} total)"
        )

        return context

    async def prune_old_task_memories(
        self, db: AsyncSession, user_id: Optional[UUID] = None
    ) -> int:
        """
        Delete TASK memories older than retention period (30 days)

        This should be run as a background job (ARQ worker) daily at 2:00 AM.
        PERSONAL and PROJECT memories are never pruned.

        Args:
            db: Database session
            user_id: Optional specific user (if None, prunes for all users)

        Returns:
            Number of memories deleted
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.task_retention_days)

        delete_query = delete(Memory).where(
            and_(Memory.memory_type == MemoryType.TASK, Memory.created_at < cutoff_date)
        )

        if user_id:
            delete_query = delete_query.where(Memory.user_id == user_id)

        result = await db.execute(delete_query)
        await db.commit()

        deleted_count = result.rowcount
        logger.info(
            f"Pruned {deleted_count} TASK memories older than {self.task_retention_days} days"
            + (f" for user {user_id}" if user_id else " (all users)")
        )

        return deleted_count

    async def calculate_user_priorities(
        self, db: AsyncSession, user_id: UUID
    ) -> Dict[str, float]:
        """
        Analyze PERSONAL memories to identify user's core values/priorities

        Extracts universal factors (learning, discipline, etc.) from stressor
        and preference memories to understand what matters most to the user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dict of priority names to importance scores (0.0-1.0)
        """
        # Retrieve all PERSONAL memories
        personal_memories = await self.query_memories(
            db, user_id, memory_type=MemoryType.PERSONAL, limit=100
        )

        # Aggregate universal_factors from metadata
        priority_scores: Dict[str, List[float]] = {}

        for memory in personal_memories:
            if not memory.extra_data:
                continue

            # Extract universal factors if present
            universal_factors = memory.extra_data.get("universal_factors", {})
            for factor, score in universal_factors.items():
                if factor not in priority_scores:
                    priority_scores[factor] = []
                priority_scores[factor].append(score)

        # Calculate average scores
        priorities = {
            factor: sum(scores) / len(scores) for factor, scores in priority_scores.items()
        }

        # Sort by importance
        priorities = dict(sorted(priorities.items(), key=lambda x: x[1], reverse=True))

        logger.info(f"Calculated priorities for user {user_id}: {priorities}")
        return priorities

    async def store_summary(
        self,
        db: AsyncSession,
        user_id: UUID,
        summary_content: str,
        source_context: str,
        memory_type: MemoryType = MemoryType.TASK,
        metadata: Optional[Dict] = None,
    ) -> Memory:
        """
        Store a summary or derived insight as a memory

        This enables the agent to learn from past interactions by storing
        summaries, search results, or key insights as searchable memories.

        Args:
            db: Database session
            user_id: User ID
            summary_content: The summary or insight text
            source_context: Description of what this summarizes
            memory_type: Memory tier (default: TASK)
            metadata: Additional metadata (tags, sources, etc.)

        Returns:
            Created Memory object
        """
        memory_metadata = metadata or {}
        memory_metadata.update(
            {
                "is_summary": True,
                "source_context": source_context,
                "created_from": "agent_learning",
            }
        )

        memory_data = MemoryCreate(
            memory_type=memory_type, content=summary_content, metadata=memory_metadata
        )

        memory = await self.add_memory(db, user_id, memory_data)

        logger.info(
            f"Stored summary for user {user_id}: {summary_content[:50]}... "
            f"(source: {source_context})"
        )

        return memory


# Singleton instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """
    Get singleton instance of MemoryService

    Returns:
        MemoryService instance
    """
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
