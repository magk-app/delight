"""
Token Usage Tracking Service

Tracks OpenAI API token usage and calculates costs.
Stores usage data to database for analytics.
"""

from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

# Token pricing (per 1M tokens) - Updated as of Jan 2025
TOKEN_PRICING = {
    # GPT-4o models
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},

    # GPT-3.5 models
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},

    # O1 models (reasoning)
    "o1-preview": {"input": 15.00, "output": 60.00},
    "o1-mini": {"input": 3.00, "output": 12.00},

    # Embedding models
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
    "text-embedding-ada-002": {"input": 0.10, "output": 0.0},
}


class TokenTracker:
    """Service for tracking and recording OpenAI token usage"""

    @staticmethod
    def calculate_cost(model: str, tokens_input: int, tokens_output: int) -> tuple[float, float, float]:
        """
        Calculate cost for token usage.

        Args:
            model: OpenAI model name
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens

        Returns:
            tuple: (cost_input, cost_output, total_cost) in USD
        """
        pricing = TOKEN_PRICING.get(model, {"input": 0.0, "output": 0.0})

        # Cost = (tokens / 1_000_000) * price_per_million
        cost_input = (tokens_input / 1_000_000) * pricing["input"]
        cost_output = (tokens_output / 1_000_000) * pricing["output"]
        total_cost = cost_input + cost_output

        return cost_input, cost_output, total_cost

    @staticmethod
    async def track_usage(
        db: AsyncSession,
        user_id: Optional[UUID],
        operation_type: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track token usage and save to database.

        Args:
            db: Database session
            user_id: User ID (optional for system operations)
            operation_type: Type of operation (chat, fact_extraction, etc.)
            model: OpenAI model name
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            metadata: Additional context (conversation_id, memory_id, etc.)
        """
        from app.models.token_usage import TokenUsage, OperationType

        # Calculate costs
        cost_input, cost_output, total_cost = TokenTracker.calculate_cost(
            model, tokens_input, tokens_output
        )

        # Create usage record
        usage = TokenUsage(
            user_id=user_id,
            operation_type=OperationType(operation_type),
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            total_tokens=tokens_input + tokens_output,
            cost_input=cost_input,
            cost_output=cost_output,
            total_cost=total_cost,
            metadata=metadata or {}
        )

        db.add(usage)
        # Note: Caller should commit the transaction

    @staticmethod
    def extract_tokens_from_response(response: Any) -> tuple[int, int]:
        """
        Extract token counts from OpenAI API response.

        Args:
            response: OpenAI API response object

        Returns:
            tuple: (tokens_input, tokens_output)
        """
        try:
            usage = response.usage
            tokens_input = usage.prompt_tokens
            tokens_output = usage.completion_tokens
            return tokens_input, tokens_output
        except AttributeError:
            # Response doesn't have usage info (shouldn't happen with OpenAI)
            return 0, 0
