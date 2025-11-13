"""
Pydantic schemas for Companion Chat API.
Defines request/response models for chat interactions with Eliza.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Chat Request/Response Schemas
# ============================================================================


class ChatRequest(BaseModel):
    """
    Schema for sending a message to Eliza.

    The conversation_id is optional - if not provided, a new conversation
    will be created. If provided, the message will be added to the existing
    conversation.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's message to Eliza",
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Existing conversation ID (optional, creates new conversation if not provided)",
    )


class ChatResponse(BaseModel):
    """
    Schema for response after sending a message.

    Returns the conversation ID for SSE streaming.
    The actual response content streams via GET /stream/{conversation_id}.
    """

    conversation_id: UUID = Field(
        ...,
        description="Conversation ID for retrieving the streaming response",
    )
    status: str = Field(
        default="processing",
        description="Status of the chat request",
    )


# ============================================================================
# Conversation History Schemas
# ============================================================================


class MessageResponse(BaseModel):
    """Schema for a single message in conversation history."""

    role: str = Field(
        ...,
        description="Message role: 'user' or 'assistant'",
    )
    content: str = Field(
        ...,
        description="Message content",
    )
    timestamp: datetime = Field(
        ...,
        description="Message timestamp",
    )


class ConversationResponse(BaseModel):
    """Schema for a single conversation with messages."""

    id: UUID = Field(
        ...,
        description="Conversation ID",
    )
    messages: List[MessageResponse] = Field(
        default_factory=list,
        description="List of messages in chronological order",
    )
    created_at: datetime = Field(
        ...,
        description="Conversation creation timestamp",
    )


class ConversationHistoryResponse(BaseModel):
    """Schema for conversation history response."""

    conversations: List[ConversationResponse] = Field(
        default_factory=list,
        description="List of user's conversations, sorted by creation date (newest first)",
    )


# ============================================================================
# SSE Event Schemas (for documentation)
# ============================================================================


class TokenEvent(BaseModel):
    """SSE event for streaming tokens."""

    type: str = Field(
        default="token",
        description="Event type",
    )
    content: str = Field(
        ...,
        description="Token content",
    )


class CompleteEvent(BaseModel):
    """SSE event indicating streaming complete."""

    type: str = Field(
        default="complete",
        description="Event type",
    )


class ErrorEvent(BaseModel):
    """SSE event indicating an error."""

    type: str = Field(
        default="error",
        description="Event type",
    )
    message: str = Field(
        ...,
        description="Error message",
    )
