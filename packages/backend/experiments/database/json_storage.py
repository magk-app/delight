"""JSON-based storage backend for experiments without PostgreSQL.

This module provides a simple file-based storage system that can be used
when PostgreSQL is unavailable or for lightweight testing.

Features:
- Store memories in JSON files
- In-memory indexing for fast search
- Automatic file persistence
- Compatible with the same interface as PostgreSQL storage

Example:
    >>> storage = JSONStorage()
    >>> memory = await storage.create_memory(
    ...     user_id=user_id,
    ...     content="Test memory",
    ...     memory_type="personal"
    ... )
    >>> memories = await storage.search_memories(user_id, "test")
"""

import json
import os
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from experiments.config import get_config


class JSONMemory:
    """In-memory representation of a memory."""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        content: str,
        memory_type: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.memory_type = memory_type
        self.embedding = embedding
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "content": self.content,
            "memory_type": self.memory_type,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JSONMemory":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            content=data["content"],
            memory_type=data["memory_type"],
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


class JSONStorage:
    """JSON file-based storage backend.

    This provides a simple storage layer that persists memories to JSON files
    and keeps them indexed in memory for fast retrieval.

    Example:
        >>> storage = JSONStorage()
        >>> memory = await storage.create_memory(
        ...     user_id=user_id,
        ...     content="I love Python",
        ...     memory_type="personal",
        ...     metadata={"categories": ["programming"]}
        ... )
        >>> print(f"Created memory: {memory.id}")
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize JSON storage.

        Args:
            storage_path: Path to JSON file (default from config)
        """
        config = get_config()
        self.storage_path = Path(storage_path or config.json_storage_path)

        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory index
        self.memories: Dict[UUID, JSONMemory] = {}
        self.user_memories: Dict[UUID, List[UUID]] = defaultdict(list)

        # Load existing data
        self._load()

        print(f"📁 JSON Storage initialized: {self.storage_path}")
        print(f"   Loaded {len(self.memories)} memories")

    def _load(self):
        """Load memories from JSON file."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            for memory_data in data.get("memories", []):
                memory = JSONMemory.from_dict(memory_data)
                self.memories[memory.id] = memory
                self.user_memories[memory.user_id].append(memory.id)

        except Exception as e:
            print(f"⚠️  Error loading JSON storage: {e}")

    def _save(self):
        """Save memories to JSON file."""
        try:
            data = {
                "memories": [m.to_dict() for m in self.memories.values()],
                "last_updated": datetime.now().isoformat()
            }

            # Save full version with embeddings
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Save clean version WITHOUT embeddings for human readability
            self._save_clean_version()

        except Exception as e:
            print(f"⚠️  Error saving JSON storage: {e}")

    def _save_clean_version(self):
        """Save human-readable version without embeddings."""
        try:
            clean_path = self.storage_path.parent / "memories_clean.json"

            clean_data = {
                "memories": [],
                "last_updated": datetime.now().isoformat(),
                "total_memories": len(self.memories),
                "note": "This is a human-readable version. Embeddings are stored in memories.json"
            }

            for memory in self.memories.values():
                clean_memory = {
                    "id": str(memory.id),
                    "user_id": str(memory.user_id),
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "metadata": memory.metadata,
                    "created_at": memory.created_at.isoformat(),
                    "has_embedding": memory.embedding is not None
                }
                clean_data["memories"].append(clean_memory)

            with open(clean_path, 'w') as f:
                json.dump(clean_data, f, indent=2)

            print(f"💾 Saved clean version: {clean_path}")

        except Exception as e:
            print(f"⚠️  Error saving clean version: {e}")

    async def create_memory(
        self,
        user_id: UUID,
        content: str,
        memory_type: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JSONMemory:
        """Create a new memory.

        Args:
            user_id: User ID
            content: Memory content
            memory_type: Type (personal, project, task)
            embedding: Optional embedding vector
            metadata: Optional metadata dict

        Returns:
            Created JSONMemory object

        Example:
            >>> memory = await storage.create_memory(
            ...     user_id=user_id,
            ...     content="I love Python programming",
            ...     memory_type="personal",
            ...     metadata={"categories": ["programming", "preferences"]}
            ... )
        """
        memory = JSONMemory(
            id=uuid.uuid4(),
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            embedding=embedding,
            metadata=metadata
        )

        self.memories[memory.id] = memory
        self.user_memories[user_id].append(memory.id)

        self._save()

        return memory

    async def get_memory(self, memory_id: UUID) -> Optional[JSONMemory]:
        """Get memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            JSONMemory or None if not found
        """
        return self.memories.get(memory_id)

    async def get_user_memories(
        self,
        user_id: UUID,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[JSONMemory]:
        """Get all memories for a user.

        Args:
            user_id: User ID
            memory_type: Optional filter by type
            limit: Optional limit

        Returns:
            List of JSONMemory objects
        """
        memory_ids = self.user_memories.get(user_id, [])
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]

        # Filter by type
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        # Sort by created_at (newest first)
        memories.sort(key=lambda m: m.created_at, reverse=True)

        # Limit
        if limit:
            memories = memories[:limit]

        return memories

    async def search_semantic(
        self,
        user_id: UUID,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Tuple[JSONMemory, float]]:
        """Search using embedding similarity.

        Args:
            user_id: User ID
            query_embedding: Query embedding vector
            limit: Maximum results
            threshold: Minimum similarity

        Returns:
            List of (memory, similarity_score) tuples
        """
        results = []

        for memory_id in self.user_memories.get(user_id, []):
            memory = self.memories.get(memory_id)
            if not memory or not memory.embedding:
                continue

            # Compute cosine similarity
            similarity = self._cosine_similarity(query_embedding, memory.embedding)

            if similarity >= threshold:
                results.append((memory, similarity))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    async def search_keyword(
        self,
        user_id: UUID,
        query: str,
        limit: int = 10
    ) -> List[Tuple[JSONMemory, float]]:
        """Search using keyword matching.

        Args:
            user_id: User ID
            query: Search query
            limit: Maximum results

        Returns:
            List of (memory, relevance_score) tuples
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        results = []

        for memory_id in self.user_memories.get(user_id, []):
            memory = self.memories.get(memory_id)
            if not memory:
                continue

            # Simple keyword matching
            content_lower = memory.content.lower()

            # Count matching terms
            matches = sum(1 for term in query_terms if term in content_lower)

            if matches > 0:
                # Score based on proportion of query terms matched
                score = matches / len(query_terms) if query_terms else 0
                results.append((memory, score))

        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    async def search_categorical(
        self,
        user_id: UUID,
        categories: List[str],
        limit: int = 10
    ) -> List[JSONMemory]:
        """Search by categories.

        Args:
            user_id: User ID
            categories: List of categories to match
            limit: Maximum results

        Returns:
            List of JSONMemory objects
        """
        results = []
        categories_set = set(cat.lower() for cat in categories)

        for memory_id in self.user_memories.get(user_id, []):
            memory = self.memories.get(memory_id)
            if not memory:
                continue

            # Check if memory has any matching categories
            memory_categories = memory.metadata.get("categories", [])
            memory_categories_set = set(cat.lower() for cat in memory_categories)

            if categories_set & memory_categories_set:  # Intersection
                results.append(memory)

        # Sort by recency
        results.sort(key=lambda m: m.created_at, reverse=True)

        return results[:limit]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_statistics(self) -> dict:
        """Get storage statistics.

        Returns:
            Dictionary with stats
        """
        total_memories = len(self.memories)
        with_embeddings = sum(1 for m in self.memories.values() if m.embedding)

        # Count by type
        by_type = defaultdict(int)
        for memory in self.memories.values():
            by_type[memory.memory_type] += 1

        # Count by user
        users = len(self.user_memories)

        return {
            "total_memories": total_memories,
            "memories_with_embeddings": with_embeddings,
            "total_users": users,
            "by_type": dict(by_type),
            "storage_path": str(self.storage_path),
            "file_size_kb": (
                self.storage_path.stat().st_size / 1024
                if self.storage_path.exists()
                else 0
            )
        }

    def print_statistics(self):
        """Print formatted statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("📊 JSON Storage Statistics")
        print("=" * 60)
        print(f"Total Memories:      {stats['total_memories']:,}")
        print(f"With Embeddings:     {stats['memories_with_embeddings']:,}")
        print(f"Total Users:         {stats['total_users']:,}")
        print(f"Storage File:        {stats['storage_path']}")
        print(f"File Size:           {stats['file_size_kb']:.2f} KB")
        print()
        print("Memories by Type:")
        for mem_type, count in stats['by_type'].items():
            print(f"  {mem_type:15} {count:,}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    """Test JSON storage."""
    import asyncio

    async def test():
        storage = JSONStorage()

        # Create test user
        user_id = uuid.uuid4()

        # Create some memories
        print("Creating test memories...")
        memories = []

        for content, mem_type, categories in [
            ("I love Python programming", "personal", ["programming", "preferences"]),
            ("Working on Delight project", "project", ["work", "ai"]),
            ("Based in San Francisco", "personal", ["location"]),
            ("Prefer async programming", "personal", ["programming", "preferences"]),
        ]:
            memory = await storage.create_memory(
                user_id=user_id,
                content=content,
                memory_type=mem_type,
                metadata={"categories": categories}
            )
            memories.append(memory)
            print(f"  ✅ {content}")

        # Test keyword search
        print("\n🔍 Keyword search for 'programming':")
        results = await storage.search_keyword(user_id, "programming", limit=5)
        for memory, score in results:
            print(f"  [{score:.2f}] {memory.content}")

        # Test categorical search
        print("\n🏷️  Categorical search for 'programming':")
        results = await storage.search_categorical(user_id, ["programming"], limit=5)
        for memory in results:
            print(f"  - {memory.content}")

        # Print statistics
        storage.print_statistics()

    asyncio.run(test())
