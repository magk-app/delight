"""
Embedding generation service using OpenAI API.
Provides text-to-vector conversion with retry logic and error handling.
"""

import asyncio
import hashlib
import logging
from typing import List, Optional

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating vector embeddings from text using OpenAI API.

    Uses text-embedding-3-small model (1536 dimensions) with:
    - Exponential backoff retry logic (3 attempts)
    - Graceful error handling (returns None on failure)
    - Optional caching by content hash (future enhancement)

    Example:
        >>> service = EmbeddingService()
        >>> embedding = await service.generate_embedding("I prefer working in the morning")
        >>> len(embedding)  # Should be 1536 or None if failed
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
        max_retries: int = 3,
    ):
        """
        Initialize embedding service with OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
            model: OpenAI embedding model name
            dimensions: Expected embedding dimensions
            max_retries: Maximum retry attempts on failure
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY not configured. Embedding generation will fail gracefully."
            )

        self.model = model
        self.dimensions = dimensions
        self.max_retries = max_retries
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for given text with retry logic.

        Implements exponential backoff retry strategy:
        - Attempt 1: Immediate
        - Attempt 2: 1 second delay
        - Attempt 3: 2 seconds delay
        - Attempt 4: 4 seconds delay

        Args:
            text: Input text to embed (should be <= 8191 tokens)

        Returns:
            List of floats (1536 dimensions) or None if all retries failed

        Example:
            >>> embedding = await service.generate_embedding("Hello world")
            >>> if embedding:
            ...     print(f"Generated {len(embedding)}-dimensional embedding")
        """
        if not self.client:
            logger.error("OpenAI client not initialized (missing API key)")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return None

        # Truncate text preview for logging (avoid logging sensitive data)
        text_preview = text[:100] + "..." if len(text) > 100 else text

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Generating embedding (attempt {attempt + 1}/{self.max_retries}): "
                    f"{text_preview}"
                )

                # Call OpenAI API
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text,
                    encoding_format="float",
                )

                # Extract embedding from response
                embedding = response.data[0].embedding

                # Validate dimensions
                if len(embedding) != self.dimensions:
                    logger.error(
                        f"Unexpected embedding dimensions: got {len(embedding)}, "
                        f"expected {self.dimensions}"
                    )
                    return None

                logger.debug(
                    f"Successfully generated embedding with {len(embedding)} dimensions"
                )
                return embedding

            except OpenAIError as e:
                # OpenAI-specific errors (rate limits, API errors, etc.)
                logger.warning(
                    f"OpenAI API error on attempt {attempt + 1}/{self.max_retries}: "
                    f"{type(e).__name__}: {str(e)}"
                )

                # Calculate exponential backoff delay
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt  # 1s, 2s, 4s
                    logger.debug(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Failed to generate embedding after {self.max_retries} attempts: "
                        f"{text_preview}"
                    )
                    return None

            except Exception as e:
                # Unexpected errors (network issues, invalid input, etc.)
                logger.error(
                    f"Unexpected error generating embedding (attempt {attempt + 1}): "
                    f"{type(e).__name__}: {str(e)}, text: {text_preview}"
                )

                # Still retry on unexpected errors
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt
                    await asyncio.sleep(delay)
                else:
                    return None

        return None

    def _calculate_content_hash(self, text: str) -> str:
        """
        Calculate SHA-256 hash of content for caching purposes.

        Args:
            text: Content to hash

        Returns:
            Hexadecimal hash string

        Note:
            This is a placeholder for future caching implementation.
            Redis cache can use: embedding:cache:{hash} -> [float, ...]
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
