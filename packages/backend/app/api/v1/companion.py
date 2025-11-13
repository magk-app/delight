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
            f"✅ STORED {memory_type.value.upper()} memory for user {user_id}: '{content[:50]}...'"
        )
        logger.debug(f"   Metadata: {metadata}")
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
    Determine memory type from message content using keyword heuristics.

    Fast classification based on content patterns:
    - PERSONAL: Emotions, feelings, struggles (never pruned)
    - PROJECT: Goals, plans, aspirations (meaningful retention)
    - TASK: Immediate actions, questions (30-day pruning)

    Args:
        message: User message content

    Returns:
        MemoryType: Detected memory tier
    """
    message_lower = message.lower()

    # PERSONAL: Emotional expressions, feelings, struggles
    personal_keywords = [
        "feel", "feeling", "felt", "overwhelmed", "stressed", "anxious",
        "worried", "scared", "frustrated", "tired", "exhausted",
        "struggling", "sad", "depressed", "angry", "nervous",
    ]
    if any(kw in message_lower for kw in personal_keywords):
        logger.info(f"🔍 DETECTED PERSONAL: '{message[:50]}...'")
        return MemoryType.PERSONAL

    # PROJECT: Goals, plans, long-term intentions
    project_keywords = [
        "goal", "want to", "plan", "working on", "trying to",
        "hope to", "dream", "graduate", "career", "thesis",
        "semester", "long-term", "future", "achieve",
    ]
    if any(kw in message_lower for kw in project_keywords):
        logger.info(f"🔍 DETECTED PROJECT: '{message[:50]}...'")
        return MemoryType.PROJECT

    # Default: TASK
    logger.info(f"🔍 DETECTED TASK (default): '{message[:50]}...'")
    return MemoryType.TASK


async def _classify_message_metadata_llm(
    message: str, memory_type: MemoryType
) -> Dict[str, Any]:
    """
    Use LLM to classify emotions, intensity, categories for rich metadata.

    Uses GPT-4o-mini for fast, accurate classification of:
    - Emotions (joy, fear, sadness, anger, etc.)
    - Emotion severity/intensity
    - Categories (academic, social, health, etc.)
    - Goal scope (big/small goals)
    - Task priority/difficulty

    Args:
        message: User message content
        memory_type: Detected memory type

    Returns:
        Dict[str, Any]: Rich metadata from LLM classification
    """
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Build classification prompt based on memory type
        if memory_type == MemoryType.PERSONAL:
            system_prompt = """Analyze this emotional message and return JSON with:
{
  "emotion": "joy" | "sadness" | "fear" | "anger" | "surprise" | "neutral",
  "emotion_severity": "mild_annoyance" | "moderate_concern" | "persistent_stressor" | "crisis",
  "category": "academic" | "social" | "health" | "financial" | "family" | "other",
  "intensity": 0.0 to 1.0
}"""
        elif memory_type == MemoryType.PROJECT:
            system_prompt = """Analyze this goal/plan message and return JSON with:
{
  "goal_scope": "small_goal" | "big_goal",
  "category": "academic" | "career" | "personal_growth" | "health" | "creative" | "other",
  "timeline": "days" | "weeks" | "months" | "years",
  "confidence": 0.0 to 1.0
}"""
        else:  # TASK
            system_prompt = """Analyze this task message and return JSON with:
{
  "task_priority": "low" | "medium" | "high",
  "task_difficulty": "easy" | "medium" | "hard",
  "category": "academic" | "personal" | "work" | "other",
  "estimated_time": "minutes" | "hours" | "days"
}"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0,
            max_tokens=200,
            response_format={"type": "json_object"},  # Force JSON output
        )

        llm_metadata = json.loads(response.choices[0].message.content)
        logger.debug(f"📊 LLM metadata: {llm_metadata}")

        # Merge LLM results with base metadata
        metadata = {
            "source": "conversation",
            "timestamp": datetime.utcnow().isoformat(),
            **llm_metadata,
        }

        # Add type-specific flags
        if memory_type == MemoryType.PERSONAL:
            metadata["stressor"] = True
        elif memory_type == MemoryType.PROJECT:
            metadata["goal_related"] = True
        else:
            metadata["task_related"] = True

        return metadata

    except Exception as e:
        # Fallback to simple metadata if LLM fails
        logger.warning(
            f"LLM metadata classification failed, using fallback: {type(e).__name__}: {str(e)}"
        )
        return {
            "source": "conversation",
            "timestamp": datetime.utcnow().isoformat(),
            "category": "unknown",
            "fallback": True,
        }


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

        logger.info(f"📨 USER MESSAGE: '{request.message[:100]}...'")

        # Detect memory type from message content (fast keyword-based)
        memory_type = _detect_memory_type(request.message)
        logger.info(f"   → Memory type detected: {memory_type.value.upper()}")

        # Generate rich metadata using LLM (async)
        metadata = await _classify_message_metadata_llm(request.message, memory_type)
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
            last_user_memory_type = MemoryType.TASK  # Default for new conversations

            for mem in reversed(conversation_memories):  # Chronological order
                role = mem.extra_data.get("role", "user")
                conversation_history.append({"role": role, "content": mem.content})

                # Track last user message for memory query
                if role == "user":
                    last_user_message = mem.content
                    last_user_memory_type = mem.memory_type  # Inherit type from user

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

            # Store assistant response with SAME memory type as user message
            # This maintains semantic coherence - emotional support stays PERSONAL,
            # goal guidance stays PROJECT, task help stays TASK
            logger.info(f"🤖 ASSISTANT RESPONSE: '{full_response[:100]}...'")
            logger.info(f"   → Memory type: {last_user_memory_type.value.upper()} (inherited from user message)")

            assistant_metadata = {
                "source": "conversation",
                "conversation_id": str(conversation_id),
                "role": "assistant",
                "timestamp": datetime.utcnow().isoformat(),
            }

            await _store_memory(
                db=db,
                user_id=current_user.id,
                memory_type=last_user_memory_type,  # Inherit type from user message!
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


@router.get("/debug/memory-stats")
async def get_memory_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    DEBUG ENDPOINT: Get memory type distribution for current user.

    Returns counts of PERSONAL, PROJECT, and TASK memories.
    """
    try:
        from sqlalchemy import func

        # Count memories by type
        result = await db.execute(
            select(Memory.memory_type, func.count(Memory.id))
            .where(Memory.user_id == current_user.id)
            .group_by(Memory.memory_type)
        )
        counts = result.all()

        # Build distribution dict
        distribution = {
            "PERSONAL": 0,
            "PROJECT": 0,
            "TASK": 0,
        }

        for memory_type, count in counts:
            distribution[memory_type.value.upper()] = count

        # Get recent memories by type
        recent_by_type = {}
        for mem_type in [MemoryType.PERSONAL, MemoryType.PROJECT, MemoryType.TASK]:
            result = await db.execute(
                select(Memory.content, Memory.created_at, Memory.extra_data)
                .where(
                    Memory.user_id == current_user.id,
                    Memory.memory_type == mem_type,
                )
                .order_by(Memory.created_at.desc())
                .limit(3)
            )
            memories = result.all()
            recent_by_type[mem_type.value.upper()] = [
                {
                    "content": mem[0][:100],
                    "created_at": mem[1].isoformat(),
                    "role": mem[2].get("role", "unknown") if mem[2] else "unknown",
                }
                for mem in memories
            ]

        return {
            "user_id": str(current_user.id),
            "distribution": distribution,
            "total": sum(distribution.values()),
            "recent_by_type": recent_by_type,
        }

    except Exception as e:
        logger.error(f"Error getting memory stats: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get memory stats",
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
