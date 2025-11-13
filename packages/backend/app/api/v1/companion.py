"""
Companion Chat API endpoints.

Provides chat interface with Eliza including:
- POST /chat: Send message and create/continue conversation
- GET /stream/{conversation_id}: SSE streaming of Eliza's response
- GET /history: Retrieve conversation history

Memory operations are inline for Story 2.5 vertical slice.
Story 2.2 will extract these into a proper memory service.
"""

import json
import logging
import uuid
from typing import Any, Dict, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.core.clerk_auth import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.memory import Memory, MemoryType
from app.models.user import User
from app.schemas.companion import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    ConversationResponse,
    MessageResponse,
)
from app.agents.simple_eliza import SimpleElizaAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companion", tags=["companion"])


# ============================================================================
# Inline Memory Helper Functions (Story 2.5 - Vertical Slice)
# Story 2.2 will extract these into a proper MemoryService
# ============================================================================


async def _generate_embedding(text: str) -> List[float]:
    """
    Generate 1536-dim embedding using OpenAI text-embedding-3-small.

    Args:
        text: Text to embed

    Returns:
        List[float]: 1536-dimensional embedding vector

    Raises:
        Exception: If OpenAI API call fails
    """
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model="text-embedding-3-small",  # 1536 dimensions
            input=text,
        )
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {type(e).__name__}: {str(e)}")
        raise


async def _store_memory(
    db: AsyncSession,
    user_id: uuid.UUID,
    memory_type: MemoryType,
    content: str,
    metadata: Dict[str, Any],
) -> Memory:
    """
    Store memory with automatic embedding generation.

    CRITICAL: Uses extra_data attribute (not metadata) due to SQLAlchemy reserved keyword.

    Args:
        db: Database session
        user_id: User ID
        memory_type: Memory tier (PERSONAL, PROJECT, TASK)
        content: Human-readable memory content
        metadata: Flexible metadata dict (stressor info, goal references, etc.)

    Returns:
        Memory: Created memory object

    Raises:
        Exception: If embedding generation or database operation fails
    """
    try:
        # Generate embedding
        embedding = await _generate_embedding(content)

        # Create memory
        # CRITICAL: Use extra_data, not metadata (SQLAlchemy reserved keyword)
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            extra_data=metadata,  # NOTE: extra_data, not metadata!
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        logger.info(
            f"Stored {memory_type.value} memory for user {user_id}: {content[:50]}..."
        )
        return memory

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to store memory: {type(e).__name__}: {str(e)}")
        raise


async def _query_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    query_text: str,
    limit: int = 5,
) -> List[Memory]:
    """
    Query memories using basic vector similarity search.

    Uses HNSW index for fast cosine distance search. Story 2.2 will add
    hybrid search with time decay and frequency boost.

    Args:
        db: Database session
        user_id: User ID
        query_text: Natural language query
        limit: Maximum number of memories to return (default 5)

    Returns:
        List[Memory]: Relevant memories sorted by similarity

    Raises:
        Exception: If embedding generation or query fails
    """
    try:
        # Generate query embedding
        query_embedding = await _generate_embedding(query_text)

        # Basic vector search (no hybrid scoring yet)
        # Uses cosine distance with HNSW index (fast!)
        result = await db.execute(
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        memories = result.scalars().all()

        logger.info(
            f"Retrieved {len(memories)} memories for query: {query_text[:50]}..."
        )
        return list(memories)

    except Exception as e:
        logger.error(f"Failed to query memories: {type(e).__name__}: {str(e)}")
        raise


def _detect_memory_type(message: str) -> MemoryType:
    """
    Determine memory type from message content using simple heuristics.

    Story 2.3 will improve this with LLM-based classification.

    Heuristics:
    - Stressors/venting (overwhelmed, stressed, anxious) → PERSONAL
    - Goals/plans (goal, plan, want to, working on) → PROJECT
    - Default → TASK

    Args:
        message: User message content

    Returns:
        MemoryType: Detected memory tier
    """
    message_lower = message.lower()

    # Check for stressors/venting (personal tier)
    stressor_keywords = [
        "overwhelmed",
        "stressed",
        "anxious",
        "worried",
        "nervous",
        "scared",
        "frustrated",
        "tired",
        "exhausted",
        "struggling",
    ]
    if any(keyword in message_lower for keyword in stressor_keywords):
        return MemoryType.PERSONAL

    # Check for goals/plans (project tier)
    goal_keywords = [
        "goal",
        "plan",
        "want to",
        "working on",
        "trying to",
        "hope to",
        "dream",
        "ambition",
        "achieve",
    ]
    if any(keyword in message_lower for keyword in goal_keywords):
        return MemoryType.PROJECT

    # Default to task tier
    return MemoryType.TASK


def _classify_message_metadata(message: str, memory_type: MemoryType) -> Dict[str, Any]:
    """
    Generate metadata for message based on content and type.

    Story 2.5 AC9 requires emotion severity, goal scope, task priority.
    This is a simple version - Story 2.2 will add full emotion detection.

    Args:
        message: User message content
        memory_type: Detected memory type

    Returns:
        Dict[str, Any]: Metadata with source, category, and type-specific fields
    """
    metadata = {
        "source": "conversation",
        "timestamp": datetime.utcnow().isoformat(),
    }

    message_lower = message.lower()

    # Personal memory metadata (stressors)
    if memory_type == MemoryType.PERSONAL:
        metadata["stressor"] = True

        # Simple emotion detection (Story 2.6 will add cardiffnlp/roberta model)
        if any(
            word in message_lower for word in ["overwhelmed", "stressed", "anxious"]
        ):
            metadata["emotion"] = "fear"
            metadata["category"] = "academic"  # Simplified categorization

        # Emotion severity (AC9) - simplified intensity estimation
        # Story 2.6 will add proper emotion detection with intensity scores
        if any(word in message_lower for word in ["very", "extremely", "completely"]):
            metadata["emotion_severity"] = "persistent_stressor"  # 0.4-0.7 intensity
        else:
            metadata["emotion_severity"] = "mild_annoyance"  # <0.4 intensity

    # Project memory metadata (goals)
    elif memory_type == MemoryType.PROJECT:
        metadata["goal_related"] = True

        # Goal scope detection (AC9)
        # Big goal: mentions semester, year, months, or long timelines
        # Small goal: short-term, immediate
        if any(
            word in message_lower
            for word in [
                "semester",
                "year",
                "month",
                "graduate",
                "career",
                "long-term",
            ]
        ):
            metadata["goal_scope"] = "big_goal"
        else:
            metadata["goal_scope"] = "small_goal"

        metadata["category"] = "goal"

    # Task memory metadata
    else:
        metadata["task_related"] = True

        # Task priority estimation (AC9) - based on urgency keywords
        if any(word in message_lower for word in ["urgent", "asap", "immediately"]):
            metadata["task_priority"] = "high"
        elif any(word in message_lower for word in ["soon", "today", "tomorrow"]):
            metadata["task_priority"] = "medium"
        else:
            metadata["task_priority"] = "low"

        # Task difficulty estimation (AC9)
        if any(word in message_lower for word in ["difficult", "hard", "complex"]):
            metadata["task_difficulty"] = "hard"
        elif any(word in message_lower for word in ["easy", "simple", "quick"]):
            metadata["task_difficulty"] = "easy"
        else:
            metadata["task_difficulty"] = "medium"

        # Universal factors (AC9) - simplified defaults
        # Story 2.2 will add sophisticated factor detection
        metadata["universal_factors"] = {
            "learning": 0.4,
            "discipline": 0.3,
            "health": 0.1,
            "craft": 0.2,
            "connection": 0.0,
        }

    return metadata


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/chat", response_model=ChatResponse)
async def chat_with_eliza(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Send message to Eliza and create/continue conversation.

    This endpoint:
    1. Creates or retrieves conversation
    2. Stores user message as memory
    3. Returns conversation ID for streaming response

    The actual response streams via GET /stream/{conversation_id}

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user (from Clerk token)
        db: Database session

    Returns:
        ChatResponse: Conversation ID and status

    Raises:
        HTTPException: 500 if memory storage fails
    """
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or uuid.uuid4()

        # Detect memory type from message content
        memory_type = _detect_memory_type(request.message)

        # Generate metadata
        metadata = _classify_message_metadata(request.message, memory_type)
        metadata["conversation_id"] = str(conversation_id)
        metadata["role"] = "user"

        # Store user message as memory
        await _store_memory(
            db=db,
            user_id=current_user.id,
            memory_type=memory_type,
            content=request.message,
            metadata=metadata,
        )

        logger.info(
            f"User {current_user.id} sent message in conversation {conversation_id}"
        )

        return ChatResponse(
            conversation_id=conversation_id,
            status="processing",
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )


async def get_current_user_from_query(
    token: str,
    db: AsyncSession,
) -> User:
    """
    Get current user from query parameter token (for SSE endpoints).

    EventSource doesn't support custom headers, so we accept token as query param.
    """
    from fastapi import Request

    # Create a minimal request with the token in Authorization header
    fake_request = Request(scope={
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"authorization", f"Bearer {token}".encode())],
        "query_string": b"",
        "server": ("localhost", 8000),
    })

    return await get_current_user(fake_request, db)


@router.get("/stream/{conversation_id}")
async def stream_response(
    conversation_id: uuid.UUID,
    token: str,  # Required: Accept token as query param for EventSource
    db: AsyncSession = Depends(get_db),
):
    """
    Stream Eliza's response via Server-Sent Events (SSE).

    This endpoint:
    1. Retrieves recent conversation history
    2. Queries relevant memories (vector search)
    3. Generates streaming response with Eliza agent
    4. Stores assistant response as task memory
    5. Yields SSE events (token, complete, or error)

    Args:
        conversation_id: Conversation ID from POST /chat
        current_user: Authenticated user (from Clerk token)
        db: Database session

    Returns:
        StreamingResponse: SSE stream with tokens

    Event Format:
        - data: {"type": "token", "content": "..."}  # Token event
        - data: {"type": "complete"}                 # Complete event
        - data: {"type": "error", "message": "..."}  # Error event
    """

    async def event_generator():
        try:
            # Authenticate user from token
            current_user = await get_current_user_from_query(token, db)

            # Retrieve recent conversation history (last 10 messages)
            result = await db.execute(
                select(Memory)
                .where(
                    Memory.user_id == current_user.id,
                    Memory.extra_data["conversation_id"].astext
                    == str(conversation_id),
                )
                .order_by(Memory.created_at.desc())
                .limit(10)
            )
            conversation_memories = list(result.scalars().all())

            # Build conversation history for agent
            conversation_history = []
            last_user_message = ""

            for mem in reversed(conversation_memories):  # Chronological order
                role = mem.extra_data.get("role", "user")
                conversation_history.append({"role": role, "content": mem.content})

                # Track last user message for memory query
                if role == "user":
                    last_user_message = mem.content

            # Query relevant memories (basic vector search)
            retrieved_memories = []
            if last_user_message:
                retrieved_memories = await _query_memories(
                    db=db,
                    user_id=current_user.id,
                    query_text=last_user_message,
                    limit=5,
                )

            # Generate response with Eliza agent
            agent = SimpleElizaAgent(openai_api_key=settings.OPENAI_API_KEY)
            full_response = ""

            async for response_token in agent.generate_response(
                user_message=last_user_message,
                conversation_history=conversation_history[
                    :-1
                ],  # Exclude last user message (already in user_message)
                retrieved_memories=retrieved_memories,
            ):
                full_response += response_token
                yield f"data: {json.dumps({'type': 'token', 'content': response_token})}\n\n"

            # Store assistant response as task memory
            assistant_metadata = {
                "source": "conversation",
                "conversation_id": str(conversation_id),
                "role": "assistant",
                "timestamp": datetime.utcnow().isoformat(),
            }

            await _store_memory(
                db=db,
                user_id=current_user.id,
                memory_type=MemoryType.TASK,  # Assistant responses are task tier
                content=full_response,
                metadata=assistant_metadata,
            )

            # Send complete event
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

            logger.info(
                f"Completed streaming response for conversation {conversation_id}"
            )

        except Exception as e:
            logger.error(f"Streaming error: {type(e).__name__}: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive",
        },
    )


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationHistoryResponse:
    """
    Retrieve user's conversation history.

    Groups messages by conversation_id and returns them in chronological order.

    Args:
        limit: Maximum number of messages to return (default 50)
        current_user: Authenticated user (from Clerk token)
        db: Database session

    Returns:
        ConversationHistoryResponse: List of conversations with messages

    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        # Retrieve all conversation memories for user
        result = await db.execute(
            select(Memory)
            .where(
                Memory.user_id == current_user.id,
                Memory.extra_data.has_key("conversation_id"),  # Only conversation messages
            )
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        memories = list(result.scalars().all())

        # Group by conversation_id
        conversations_dict: Dict[str, List[Memory]] = {}
        for memory in memories:
            conv_id = memory.extra_data.get("conversation_id")
            if conv_id:
                if conv_id not in conversations_dict:
                    conversations_dict[conv_id] = []
                conversations_dict[conv_id].append(memory)

        # Build response
        conversations = []
        for conv_id, conv_memories in conversations_dict.items():
            # Sort messages chronologically
            conv_memories.sort(key=lambda m: m.created_at)

            messages = [
                MessageResponse(
                    role=mem.extra_data.get("role", "user"),
                    content=mem.content,
                    timestamp=mem.created_at,
                )
                for mem in conv_memories
            ]

            conversations.append(
                ConversationResponse(
                    id=uuid.UUID(conv_id),
                    messages=messages,
                    created_at=conv_memories[0].created_at,  # First message timestamp
                )
            )

        # Sort conversations by creation date (newest first)
        conversations.sort(key=lambda c: c.created_at, reverse=True)

        logger.info(
            f"Retrieved {len(conversations)} conversations for user {current_user.id}"
        )

        return ConversationHistoryResponse(conversations=conversations)

    except Exception as e:
        logger.error(f"Error retrieving history: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history",
        )
