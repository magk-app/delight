"""
Memory service for managing user memories with semantic search.

This service:
- Creates, reads, updates, deletes memories
- Generates embeddings automatically
- Performs semantic similarity search using pgvector
- Manages memory collections
- Provides memory statistics
"""

import uuid
import json
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from app.models.memory import Memory, MemoryType, MemoryCollection
from app.services.embedding_service import EmbeddingService


class MemoryService:
    """Service for memory operations with semantic search."""

    def __init__(self, db: AsyncSession):
        """Initialize memory service.

        Args:
            db: Database session
        """
        self.db = db
        self.embedding_service = EmbeddingService()

    async def create_memory(
        self,
        user_id: uuid.UUID,
        content: str,
        memory_type: MemoryType,
        extra_data: Optional[dict] = None,
        embedding: Optional[List[float]] = None
    ) -> Memory:
        """Create a new memory.

        Args:
            user_id: User ID
            content: Memory content
            memory_type: Memory type (PERSONAL, PROJECT, TASK)
            extra_data: Optional metadata
            embedding: Optional pre-computed embedding (auto-generates if None)

        Returns:
            Created memory
        """
        # Generate embedding if not provided
        if embedding is None:
            embedding = await self.embedding_service.embed_text(content)

        # Create memory
        memory = Memory(
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            embedding=embedding,
            extra_data=extra_data or {}
        )

        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)

        return memory

    async def get_memory(self, memory_id: uuid.UUID) -> Optional[Memory]:
        """Get memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory if found, None otherwise
        """
        result = await self.db.execute(
            select(Memory).where(Memory.id == memory_id)
        )
        return result.scalar_one_or_none()

    async def get_user_memories(
        self,
        user_id: uuid.UUID,
        memory_type: Optional[MemoryType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Memory]:
        """Get all memories for a user.

        Args:
            user_id: User ID
            memory_type: Optional filter by memory type
            limit: Maximum number of memories
            offset: Offset for pagination

        Returns:
            List of memories
        """
        query = select(Memory).where(Memory.user_id == user_id)

        if memory_type:
            query = query.where(Memory.memory_type == memory_type)

        query = query.order_by(desc(Memory.created_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_semantic(
        self,
        user_id: uuid.UUID,
        query_text: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Tuple[Memory, float]]:
        """Search memories using semantic similarity.

        Args:
            user_id: User ID
            query_text: Query text
            memory_type: Optional filter by memory type
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (memory, similarity_score) tuples, ordered by similarity
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query_text)

        # Build SQL query with cosine distance
        # Note: pgvector uses distance (lower = more similar)
        # We convert to similarity (higher = more similar) for user-friendly scores
        query = (
            select(
                Memory,
                (1 - Memory.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .where(Memory.user_id == user_id)
            .where(Memory.embedding.isnot(None))
        )

        if memory_type:
            query = query.where(Memory.memory_type == memory_type)

        # Filter by threshold and sort by similarity
        query = (
            query
            .having(func.cast(1 - Memory.embedding.cosine_distance(query_embedding), func.Float) >= threshold)
            .order_by(desc("similarity"))
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Return list of (memory, score) tuples
        return [(row[0], float(row[1])) for row in rows]

    async def search_by_embedding(
        self,
        user_id: uuid.UUID,
        query_embedding: List[float],
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Tuple[Memory, float]]:
        """Search memories using pre-computed embedding.

        Args:
            user_id: User ID
            query_embedding: Query embedding vector
            memory_type: Optional filter by memory type
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (memory, similarity_score) tuples
        """
        query = (
            select(
                Memory,
                (1 - Memory.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .where(Memory.user_id == user_id)
            .where(Memory.embedding.isnot(None))
        )

        if memory_type:
            query = query.where(Memory.memory_type == memory_type)

        query = (
            query
            .having(func.cast(1 - Memory.embedding.cosine_distance(query_embedding), func.Float) >= threshold)
            .order_by(desc("similarity"))
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [(row[0], float(row[1])) for row in rows]

    async def update_memory(
        self,
        memory_id: uuid.UUID,
        content: Optional[str] = None,
        extra_data: Optional[dict] = None,
        regenerate_embedding: bool = False
    ) -> Optional[Memory]:
        """Update a memory.

        Args:
            memory_id: Memory ID
            content: New content (optional)
            extra_data: New metadata (optional)
            regenerate_embedding: Whether to regenerate embedding

        Returns:
            Updated memory if found, None otherwise
        """
        memory = await self.get_memory(memory_id)
        if not memory:
            return None

        if content:
            memory.content = content
            if regenerate_embedding:
                memory.embedding = await self.embedding_service.embed_text(content)

        if extra_data is not None:
            memory.extra_data = extra_data

        await self.db.commit()
        await self.db.refresh(memory)

        return memory

    async def delete_memory(self, memory_id: uuid.UUID) -> bool:
        """Delete a memory.

        Args:
            memory_id: Memory ID

        Returns:
            True if deleted, False if not found
        """
        memory = await self.get_memory(memory_id)
        if not memory:
            return False

        await self.db.delete(memory)
        await self.db.commit()

        return True

    async def get_memory_stats(self, user_id: uuid.UUID) -> dict:
        """Get memory statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics
        """
        # Count by type
        result = await self.db.execute(
            select(
                Memory.memory_type,
                func.count(Memory.id)
            )
            .where(Memory.user_id == user_id)
            .group_by(Memory.memory_type)
        )
        counts_by_type = dict(result.all())

        # Total count
        total_result = await self.db.execute(
            select(func.count(Memory.id)).where(Memory.user_id == user_id)
        )
        total_count = total_result.scalar()

        # Count with embeddings
        embedded_result = await self.db.execute(
            select(func.count(Memory.id))
            .where(Memory.user_id == user_id)
            .where(Memory.embedding.isnot(None))
        )
        embedded_count = embedded_result.scalar()

        return {
            "total_memories": total_count,
            "memories_with_embeddings": embedded_count,
            "by_type": {
                "personal": counts_by_type.get(MemoryType.PERSONAL, 0),
                "project": counts_by_type.get(MemoryType.PROJECT, 0),
                "task": counts_by_type.get(MemoryType.TASK, 0)
            },
            "embedding_stats": self.embedding_service.get_statistics()
        }

    async def export_memories(
        self,
        user_id: uuid.UUID,
        include_embeddings: bool = False
    ) -> str:
        """Export all user memories as JSON.

        Args:
            user_id: User ID
            include_embeddings: Whether to include embedding vectors

        Returns:
            JSON string of memories
        """
        memories = await self.get_user_memories(user_id, limit=10000)

        export_data = {
            "user_id": str(user_id),
            "exported_at": datetime.now().isoformat(),
            "total_memories": len(memories),
            "memories": []
        }

        for memory in memories:
            memory_dict = {
                "id": str(memory.id),
                "content": memory.content,
                "memory_type": memory.memory_type.value,
                "metadata": memory.extra_data,
                "created_at": memory.created_at.isoformat(),
                "accessed_at": memory.accessed_at.isoformat()
            }

            if include_embeddings and memory.embedding:
                memory_dict["embedding"] = memory.embedding

            export_data["memories"].append(memory_dict)

        return json.dumps(export_data, indent=2)
