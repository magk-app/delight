"""
EmbeddingService - Handles text embedding generation using OpenAI API

Features:
- OpenAI text-embedding-3-small integration (1536 dimensions)
- Exponential backoff retry logic for API failures
- Graceful degradation on errors
- Optional caching layer (future enhancement)
- Batch embedding support

Usage:
    embedding_service = EmbeddingService()
    vector = await embedding_service.generate_embedding("User loves hiking")
"""

import asyncio
import logging
from typing import List, Optional
from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI API"""

    def __init__(self):
        """Initialize the embedding service with OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY not set - embedding generation will fail. "
                "This is acceptable for development if not testing memory features."
            )
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.model = "text-embedding-3-small"
        self.dimensions = 1536
        self.max_retries = 3
        self.base_delay = 1.0  # seconds

    async def generate_embedding(
        self, text: str, retry_count: int = 0
    ) -> Optional[List[float]]:
        """
        Generate embedding vector for input text with retry logic

        Args:
            text: Input text to embed (max 8191 tokens for text-embedding-3-small)
            retry_count: Current retry attempt (internal use)

        Returns:
            List of 1536 floats representing the embedding vector, or None on failure

        Raises:
            ValueError: If text is empty or client not initialized
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        if not self.client:
            logger.error("OpenAI client not initialized - OPENAI_API_KEY missing")
            return None

        try:
            # Clean and truncate text if needed
            cleaned_text = text.strip()[:8000]  # Conservative limit

            # Call OpenAI API
            response = await self.client.embeddings.create(
                model=self.model, input=cleaned_text, dimensions=self.dimensions
            )

            # Extract embedding vector
            embedding = response.data[0].embedding

            # Validate dimensions
            if len(embedding) != self.dimensions:
                logger.error(
                    f"Unexpected embedding dimensions: got {len(embedding)}, expected {self.dimensions}"
                )
                return None

            logger.debug(f"Generated embedding for text: {cleaned_text[:50]}...")
            return embedding

        except OpenAIError as e:
            # Retry with exponential backoff
            if retry_count < self.max_retries:
                delay = self.base_delay * (2**retry_count)
                logger.warning(
                    f"OpenAI API error (attempt {retry_count + 1}/{self.max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                return await self.generate_embedding(text, retry_count + 1)
            else:
                logger.error(f"Failed to generate embedding after {self.max_retries} retries: {e}")
                return None

        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}")
            return None

    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 100
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of input texts
            batch_size: Maximum texts per API call (OpenAI limit: ~2048)

        Returns:
            List of embedding vectors (same order as input), None for failures
        """
        if not texts:
            return []

        embeddings: List[Optional[List[float]]] = []

        # Process in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                # Filter out empty texts
                valid_texts = [(idx, text) for idx, text in enumerate(batch) if text and text.strip()]

                if not valid_texts:
                    embeddings.extend([None] * len(batch))
                    continue

                # Call OpenAI API with batch
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=[text for _, text in valid_texts],
                    dimensions=self.dimensions,
                )

                # Map results back to original indices
                batch_embeddings: List[Optional[List[float]]] = [None] * len(batch)
                for (original_idx, _), embedding_data in zip(valid_texts, response.data):
                    batch_embeddings[original_idx] = embedding_data.embedding

                embeddings.extend(batch_embeddings)

            except Exception as e:
                logger.error(f"Batch embedding generation failed for batch {i // batch_size}: {e}")
                # Fall back to individual generation
                for text in batch:
                    emb = await self.generate_embedding(text)
                    embeddings.append(emb)

        return embeddings

    async def calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector (1536 dimensions)
            embedding2: Second embedding vector (1536 dimensions)

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if len(embedding1) != self.dimensions or len(embedding2) != self.dimensions:
            raise ValueError(
                f"Invalid embedding dimensions: expected {self.dimensions}, "
                f"got {len(embedding1)} and {len(embedding2)}"
            )

        # Cosine similarity calculation
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get singleton instance of EmbeddingService

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
