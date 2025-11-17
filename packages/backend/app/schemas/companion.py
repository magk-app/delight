"""
Pydantic schemas for Companion Chat API.
Used for chat interactions, conversation history, and streaming responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Chat Request/Response Schemas
# ============================================================================


class ChatRequest(BaseModel):
    """
    Schema for sending a chat message to Eliza.

    Example:
        {
            "message": "I'm feeling overwhelmed with my thesis work",
            "conversation_id": "uuid" (optional - creates new if not provided),
            "model": "gpt-4o-mini" (optional - defaults to gpt-4o-mini)
        }
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message to send to Eliza",
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Existing conversation ID (creates new conversation if not provided)",
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use (gpt-3.5-turbo, gpt-4o-mini, gpt-4o)",
    )


class ChatResponse(BaseModel):
    """
    Schema for chat response after message is sent.

    Returns conversation_id for SSE streaming endpoint.
    """

    conversation_id: UUID = Field(
        ...,
        description="Conversation ID for retrieving streaming response",
    )
    message: str = Field(
        ...,
        description="Echo of user message sent",
    )
    status: str = Field(
        default="processing",
        description="Message status (processing, completed, error)",
    )


# ============================================================================
# Conversation History Schemas
# ============================================================================


class ConversationMessage(BaseModel):
    """
    Individual message in conversation history.
    """

    role: str = Field(
        ...,
        description="Message role (user or assistant)",
    )
    content: str = Field(
        ...,
        description="Message content",
    )
    timestamp: datetime = Field(
        ...,
        description="Message timestamp",
    )
    tokens_used: Optional[int] = Field(
        None,
        description="Token count for this message (if tracked)",
    )
    cost: Optional[float] = Field(
        None,
        description="Cost for this message in USD (if tracked)",
    )
    model: Optional[str] = Field(
        None,
        description="Model used for this message (for assistant messages)",
    )


class ConversationSummary(BaseModel):
    """
    Summary of a single conversation.
    """

    conversation_id: UUID
    started_at: datetime
    last_message_at: datetime
    message_count: int
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None


class ConversationResponse(BaseModel):
    """
    Full conversation with messages.
    """

    conversation_id: UUID
    messages: List[ConversationMessage]
    started_at: datetime
    last_message_at: datetime
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None


class ConversationHistoryResponse(BaseModel):
    """
    Response containing multiple conversations.
    """

    conversations: List[ConversationResponse]
    total_count: int


# ============================================================================
# Streaming Event Schemas
# ============================================================================


class StreamTokenEvent(BaseModel):
    """SSE event for token streaming."""

    type: Literal["token"] = "token"
    content: str = Field(..., description="Token content")


class StreamCompleteEvent(BaseModel):
    """SSE event for stream completion."""

    type: Literal["complete"] = "complete"
    total_tokens: Optional[int] = Field(None, description="Total tokens used")
    cost: Optional[float] = Field(None, description="Cost in USD")
    model: Optional[str] = Field(None, description="Model used")


class StreamErrorEvent(BaseModel):
    """SSE event for streaming errors."""

    type: Literal["error"] = "error"
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


# ============================================================================
# Memory Stats Schemas
# ============================================================================


class MemoryTypeStats(BaseModel):
    """Statistics for a single memory type."""

    memory_type: str
    count: int
    recent_count: int  # Last 7 days


class MemoryDebugStats(BaseModel):
    """
    Debug statistics for memory system.

    Shows distribution and recent memories for development debugging.
    """

    total_memories: int
    by_type: List[MemoryTypeStats]
    recent_memories: List[Dict[str, Any]]  # Last 10 memories


class MemoryKnowledgeSummary(BaseModel):
    """
    Semantic summary of what Eliza knows about the user.

    This is the user-facing knowledge dashboard (not just stats).
    """

    goals: List[str] = Field(
        default_factory=list,
        description="Goals Eliza knows you're working on",
    )
    struggles: List[str] = Field(
        default_factory=list,
        description="Struggles and stressors Eliza remembers",
    )
    important_facts: List[str] = Field(
        default_factory=list,
        description="Important facts about you Eliza knows",
    )
    total_memories: int = Field(
        ...,
        description="Total number of memories stored",
    )


# ============================================================================
# Cost Tracking Schemas
# ============================================================================


class CostSummary(BaseModel):
    """
    Summary of API costs for the user.

    Tracks token usage and costs across different models.
    """

    total_cost: float = Field(
        ...,
        description="Total cost in USD",
    )
    total_tokens: int = Field(
        ...,
        description="Total tokens used (input + output)",
    )
    by_model: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cost breakdown by model",
        examples=[{
            "gpt-4o-mini": {
                "tokens": 1000,
                "cost": 0.03,
                "count": 5
            }
        }]
    )
    period: str = Field(
        ...,
        description="Time period for stats (today, week, month, all_time)",
    )


# ============================================================================
# Memory Classification Schemas
# ============================================================================


class EmotionMetadata(BaseModel):
    """
    Emotion metadata with nuanced context (not just classifier labels).
    """

    dominant: str = Field(
        ...,
        description="Primary emotion (joy, anger, sadness, fear, love, surprise, neutral)",
    )
    scores: Dict[str, float] = Field(
        ...,
        description="Full distribution across emotion categories (0.0-1.0)",
    )
    context: str = Field(
        ...,
        description="Nuanced interpretation (e.g., 'overwhelm', 'frustration', 'loneliness')",
    )
    intensity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall emotional intensity",
    )
    severity: Optional[str] = Field(
        None,
        description="Emotion severity level (mild_annoyance, persistent_stressor, compounding_event)",
    )


class MemoryMetadata(BaseModel):
    """
    Complete memory metadata structure.

    Includes emotion, goal, task, and productivity information.
    """

    source: str = Field(
        default="conversation",
        description="Source of memory (conversation, goal_planning, etc.)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When memory was created",
    )

    # Emotion metadata
    emotion: Optional[EmotionMetadata] = None
    stressor: Optional[bool] = None

    # Goal/project metadata
    goal_id: Optional[UUID] = None
    goal_title: Optional[str] = None
    goal_related: Optional[bool] = None
    goal_scope: Optional[str] = None  # small_goal, big_goal
    timeline: Optional[str] = None

    # Task metadata
    task_id: Optional[UUID] = None
    task_title: Optional[str] = None
    task_priority: Optional[str] = None
    task_difficulty: Optional[str] = None
    estimated_time: Optional[str] = None

    # Category classification
    category: Optional[str] = None  # academic, family, social, work, health, etc.

    # Universal factors (for productivity structure)
    universal_factors: Optional[Dict[str, float]] = None

    # Conversation context
    conversation_id: Optional[UUID] = None
    exchange_type: Optional[str] = None
