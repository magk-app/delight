"""
Embedding service for generating vector embeddings using OpenAI.

This service:
- Generates 1536-dim embeddings using text-embedding-3-small
- Handles batching for efficiency
- Tracks token usage and costs
- Provides retry logic for API failures
"""

import asyncio
from typing import List, Optional
from openai import AsyncOpenAI
from app.core.config import get_settings


class EmbeddingService:
    """Service for generating OpenAI embeddings."""

    # Model configuration
    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536
    MAX_BATCH_SIZE = 100  # OpenAI limit

    # Pricing (as of 2024)
    COST_PER_1M_TOKENS = 0.02  # $0.02 per 1M tokens

    def __init__(self):
        """Initialize embedding service."""
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Statistics
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost_usd = 0.0

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            1536-dimensional embedding vector

        Raises:
            ValueError: If text is empty
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(
        self,
        texts: List[str],
        max_retries: int = 3
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            max_retries: Number of retries on failure

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
            Exception: If API call fails after retries
        """
        if not texts:
            raise ValueError("Cannot embed empty list")

        # Filter out empty strings
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")

        # Batch if needed
        if len(valid_texts) > self.MAX_BATCH_SIZE:
            return await self._embed_large_batch(valid_texts, max_retries)

        # Single batch
        for attempt in range(max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=self.MODEL,
                    input=valid_texts,
                    dimensions=self.DIMENSIONS
                )

                # Update statistics
                self.total_requests += 1
                self.total_tokens += response.usage.total_tokens
                self.total_cost_usd += (response.usage.total_tokens / 1_000_000) * self.COST_PER_1M_TOKENS

                # Extract embeddings
                embeddings = [item.embedding for item in response.data]

                return embeddings

            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate embeddings after {max_retries} attempts: {e}")

                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

    async def _embed_large_batch(
        self,
        texts: List[str],
        max_retries: int
    ) -> List[List[float]]:
        """Embed large batch by splitting into smaller batches.

        Args:
            texts: List of texts to embed
            max_retries: Number of retries per batch

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        for i in range(0, len(texts), self.MAX_BATCH_SIZE):
            batch = texts[i:i + self.MAX_BATCH_SIZE]
            batch_embeddings = await self.embed_batch(batch, max_retries)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    async def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        # Validate dimensions
        if len(embedding1) != self.DIMENSIONS or len(embedding2) != self.DIMENSIONS:
            raise ValueError(f"Embeddings must be {self.DIMENSIONS} dimensions")

        # Compute dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))

        # Compute magnitudes
        mag1 = sum(a * a for a in embedding1) ** 0.5
        mag2 = sum(b * b for b in embedding2) ** 0.5

        # Compute cosine similarity
        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def get_statistics(self) -> dict:
        """Get embedding service statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "model": self.MODEL,
            "dimensions": self.DIMENSIONS
        }

    def reset_statistics(self):
        """Reset usage statistics."""
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost_usd = 0.0
