"""OpenAI embedding generation and management.

This service handles:
- Text embedding generation using OpenAI text-embedding-3-small (1536-dim)
- Batch processing with rate limiting
- Cost tracking and optimization
- Database storage integration
- Similarity computation
"""

import asyncio
import time
from typing import List, Optional
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory
from experiments.config import get_config
from experiments.memory.types import SearchResult


class EmbeddingService:
    """OpenAI text-embedding-3-small integration for semantic search.

    This service provides efficient embedding generation with:
    - Batch processing to minimize API calls
    - Rate limiting to avoid hitting API limits
    - Cost tracking for monitoring usage
    - Direct database integration for storage

    Example:
        >>> service = EmbeddingService()
        >>> embedding = await service.embed_text("Hello world")
        >>> len(embedding)
        1536
    """

    def __init__(self):
        """Initialize embedding service."""
        self.config = get_config()

        if not self.config.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not set in environment. "
                "Please set it in .env file."
            )

        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.model = self.config.embedding_model
        self.dimensions = self.config.embedding_dimensions

        # Cost tracking
        self.total_tokens = 0
        self.total_requests = 0
        self.total_cost_usd = 0.0

        # Rate limiting (text-embedding-3-small: 5000 RPM, 5M TPM)
        self.requests_per_minute = 0
        self.last_request_time = time.time()

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text.

        Args:
            text: Input text to embed

        Returns:
            1536-dimensional embedding vector

        Raises:
            ValueError: If text is empty
            openai.APIError: If API call fails

        Example:
            >>> embedding = await service.embed_text("I love Python")
            >>> isinstance(embedding, list)
            True
            >>> len(embedding)
            1536
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        await self._check_rate_limit()

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )

            embedding = response.data[0].embedding

            # Track usage
            self._track_usage(
                tokens=response.usage.total_tokens,
                requests=1
            )

            return embedding

        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            raise

    async def batch_embed(
        self,
        texts: List[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts with batching.

        OpenAI allows up to 2048 texts per request, but we use smaller
        batches to avoid timeout and manage rate limits better.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (default: 100)
            show_progress: Print progress updates

        Returns:
            List of embeddings in same order as input texts

        Example:
            >>> texts = ["Hello", "World", "Python"]
            >>> embeddings = await service.batch_embed(texts)
            >>> len(embeddings) == len(texts)
            True
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_indices = []
        valid_texts = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_indices.append(i)
                valid_texts.append(text)

        if not valid_texts:
            raise ValueError("No valid (non-empty) texts to embed")

        all_embeddings = []
        total_batches = (len(valid_texts) + batch_size - 1) // batch_size

        for batch_idx in range(0, len(valid_texts), batch_size):
            batch = valid_texts[batch_idx:batch_idx + batch_size]

            if show_progress:
                batch_num = batch_idx // batch_size + 1
                print(f"🔄 Processing batch {batch_num}/{total_batches} "
                      f"({len(batch)} texts)...")

            await self._check_rate_limit()

            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )

                # Extract embeddings in correct order
                batch_embeddings = [
                    item.embedding for item in response.data
                ]
                all_embeddings.extend(batch_embeddings)

                # Track usage
                self._track_usage(
                    tokens=response.usage.total_tokens,
                    requests=1
                )

            except Exception as e:
                print(f"❌ Error in batch {batch_num}: {e}")
                raise

            # Small delay between batches to avoid rate limits
            if batch_idx + batch_size < len(valid_texts):
                await asyncio.sleep(0.1)

        if show_progress:
            print(f"✅ Generated {len(all_embeddings)} embeddings")

        # Reconstruct full list with None for invalid indices
        result = [None] * len(texts)
        for i, embedding in zip(valid_indices, all_embeddings):
            result[i] = embedding

        return result

    async def embed_and_store(
        self,
        memory_id: UUID,
        text: str,
        db: AsyncSession
    ):
        """Generate embedding and update memory record in database.

        Args:
            memory_id: UUID of memory to update
            text: Text to embed
            db: Database session

        Raises:
            ValueError: If memory not found

        Example:
            >>> await service.embed_and_store(
            ...     memory_id=uuid.uuid4(),
            ...     text="Important memory",
            ...     db=db_session
            ... )
        """
        # Generate embedding
        embedding = await self.embed_text(text)

        # Update database
        stmt = (
            update(Memory)
            .where(Memory.id == memory_id)
            .values(embedding=embedding)
        )

        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise ValueError(f"Memory {memory_id} not found")

        print(f"✅ Stored embedding for memory {memory_id}")

    async def batch_embed_and_store(
        self,
        memory_texts: List[tuple[UUID, str]],
        db: AsyncSession,
        batch_size: int = 100
    ):
        """Generate embeddings and update multiple memory records.

        Args:
            memory_texts: List of (memory_id, text) tuples
            db: Database session
            batch_size: Embedding batch size

        Example:
            >>> memory_data = [
            ...     (uuid1, "First memory"),
            ...     (uuid2, "Second memory")
            ... ]
            >>> await service.batch_embed_and_store(memory_data, db)
        """
        if not memory_texts:
            return

        print(f"🔄 Generating embeddings for {len(memory_texts)} memories...")

        # Extract texts
        memory_ids = [mid for mid, _ in memory_texts]
        texts = [text for _, text in memory_texts]

        # Generate embeddings
        embeddings = await self.batch_embed(texts, batch_size=batch_size)

        # Update database in batches
        print("💾 Updating database...")
        for memory_id, embedding in zip(memory_ids, embeddings):
            if embedding:  # Skip invalid embeddings
                stmt = (
                    update(Memory)
                    .where(Memory.id == memory_id)
                    .values(embedding=embedding)
                )
                await db.execute(stmt)

        await db.commit()
        print(f"✅ Updated {len(memory_texts)} memories")

    def compute_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity score (0-1, higher is more similar)

        Example:
            >>> vec1 = await service.embed_text("Python programming")
            >>> vec2 = await service.embed_text("Python coding")
            >>> similarity = service.compute_similarity(vec1, vec2)
            >>> similarity > 0.9  # Very similar
            True
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        # Cosine similarity = dot product / (norm1 * norm2)
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def find_similar_memories(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 10,
        threshold: float = 0.7,
        user_id: Optional[UUID] = None
    ) -> List[SearchResult]:
        """Find memories similar to query using embeddings.

        This is a simple implementation using Python similarity computation.
        For production, use pgvector's <=> operator for better performance.

        Args:
            query: Search query text
            db: Database session
            limit: Maximum results to return
            threshold: Minimum similarity score (0-1)
            user_id: Optional user filter

        Returns:
            List of search results sorted by similarity

        Example:
            >>> results = await service.find_similar_memories(
            ...     query="programming languages",
            ...     db=db_session,
            ...     limit=5
            ... )
        """
        # Generate query embedding
        query_embedding = await self.embed_text(query)

        # Fetch memories (with optional user filter)
        stmt = select(Memory)
        if user_id:
            # Would need to join with collections, simplified here
            pass

        result = await db.execute(stmt)
        memories = result.scalars().all()

        # Compute similarities
        results = []
        for memory in memories:
            if not memory.embedding:
                continue

            similarity = self.compute_similarity(
                query_embedding,
                memory.embedding
            )

            if similarity >= threshold:
                # Get metadata
                categories = memory.metadata.get("categories", [])

                results.append(SearchResult(
                    memory_id=memory.id,
                    content=memory.content,
                    score=similarity,
                    memory_type="unknown",  # Would need collection join
                    categories=categories,
                    created_at=memory.created_at,
                    metadata=memory.metadata
                ))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()

        # Reset counter every minute
        if current_time - self.last_request_time >= 60:
            self.requests_per_minute = 0
            self.last_request_time = current_time

        # Check if we're approaching limit
        if self.requests_per_minute >= self.config.max_api_calls_per_minute:
            wait_time = 60 - (current_time - self.last_request_time)
            if wait_time > 0:
                print(f"⏳ Rate limit reached, waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                self.requests_per_minute = 0
                self.last_request_time = time.time()

        self.requests_per_minute += 1

    def _track_usage(self, tokens: int, requests: int):
        """Track API usage and cost.

        OpenAI pricing (as of 2024):
        - text-embedding-3-small: $0.02 / 1M tokens
        """
        self.total_tokens += tokens
        self.total_requests += requests

        # Calculate cost (text-embedding-3-small: $0.02 per 1M tokens)
        cost_per_million = 0.02
        self.total_cost_usd = (self.total_tokens / 1_000_000) * cost_per_million

    def get_usage_stats(self) -> dict:
        """Get current usage statistics.

        Returns:
            Dictionary with tokens, requests, and cost

        Example:
            >>> stats = service.get_usage_stats()
            >>> print(f"Cost: ${stats['total_cost_usd']:.4f}")
        """
        return {
            "total_tokens": self.total_tokens,
            "total_requests": self.total_requests,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "average_tokens_per_request": (
                self.total_tokens // self.total_requests
                if self.total_requests > 0
                else 0
            )
        }

    def print_usage_stats(self):
        """Print usage statistics in formatted output."""
        stats = self.get_usage_stats()
        print("\n" + "=" * 50)
        print("📊 OpenAI Embedding Service - Usage Statistics")
        print("=" * 50)
        print(f"Total Requests:  {stats['total_requests']:,}")
        print(f"Total Tokens:    {stats['total_tokens']:,}")
        print(f"Avg per Request: {stats['average_tokens_per_request']:,}")
        print(f"Total Cost:      ${stats['total_cost_usd']:.4f} USD")
        print("=" * 50 + "\n")


# Convenience function for quick embedding
async def quick_embed(text: str) -> List[float]:
    """Quick embedding generation without service instance.

    Args:
        text: Text to embed

    Returns:
        1536-dimensional embedding

    Example:
        >>> from experiments.memory.embedding_service import quick_embed
        >>> embedding = await quick_embed("Hello world")
    """
    service = EmbeddingService()
    return await service.embed_text(text)


if __name__ == "__main__":
    """Example usage and testing."""
    import asyncio

    async def main():
        service = EmbeddingService()

        # Test single embedding
        print("Testing single embedding...")
        text = "I love programming in Python and TypeScript"
        embedding = await service.embed_text(text)
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        print(f"   First 5 values: {embedding[:5]}")

        # Test batch embedding
        print("\nTesting batch embedding...")
        texts = [
            "Python is great for data science",
            "JavaScript is used for web development",
            "I prefer TypeScript over JavaScript",
            "FastAPI is a modern Python framework",
            "React is a popular frontend library"
        ]
        embeddings = await service.batch_embed(texts, batch_size=2)
        print(f"✅ Generated {len(embeddings)} embeddings")

        # Test similarity
        print("\nTesting similarity computation...")
        sim1 = service.compute_similarity(embeddings[0], embeddings[3])  # Both Python
        sim2 = service.compute_similarity(embeddings[1], embeddings[2])  # Both JS/TS
        print(f"   Python-Python similarity: {sim1:.3f}")
        print(f"   JavaScript-TypeScript similarity: {sim2:.3f}")

        # Print usage stats
        service.print_usage_stats()

    asyncio.run(main())
