"""
Companion Chat API endpoints.

Provides chat interface with Eliza including:
- Real-time SSE streaming responses
- Conversation persistence across sessions
- Memory storage and retrieval with LLM-based classification
- Token counting and cost tracking
"""

import json
import logging
import tiktoken
from datetime import datetime, timedelta
from typing import Any, AsyncIterator, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.clerk_auth import get_current_user
from app.db.session import get_db
from app.models.memory import Memory, MemoryType
from app.models.user import User
from app.schemas.companion import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    ConversationResponse,
    ConversationMessage,
    MemoryDebugStats,
    MemoryKnowledgeSummary,
    MemoryTypeStats,
    CostSummary,
    MemoryMetadata,
    EmotionMetadata,
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companion", tags=["companion"])

# OpenAI client (initialized once)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# Token encoder for cost tracking
try:
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
except Exception:
    encoding = tiktoken.get_encoding("cl100k_base")  # Fallback encoding


# ============================================================================
# Helper Functions: Embeddings
# ============================================================================


async def _generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate 1536-dim embedding using OpenAI text-embedding-3-small.

    Returns None if API fails after retries.
    """
    if not openai_client:
        logger.error("OpenAI client not initialized (OPENAI_API_KEY missing)")
        return None

    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Limit to 8K characters for embedding
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}", extra={"text_preview": text[:100]})
        return None


# ============================================================================
# Helper Functions: Memory Operations
# ============================================================================


async def _store_memory(
    db: AsyncSession,
    user_id: UUID,
    memory_type: MemoryType,
    content: str,
    metadata: Dict[str, Any],
    conversation_id: Optional[UUID] = None
) -> Memory:
    """
    Store memory with automatic embedding generation.

    Uses extra_data (not metadata) due to SQLAlchemy reserved keyword.
    """
    embedding = await _generate_embedding(content)

    # Add conversation_id to metadata if provided
    if conversation_id:
        metadata["conversation_id"] = str(conversation_id)

    memory = Memory(
        user_id=user_id,
        memory_type=memory_type,
        content=content,
        embedding=embedding,
        extra_data=metadata  # Remember: use extra_data, not metadata!
    )

    db.add(memory)
    try:
        await db.commit()
        await db.refresh(memory)
        logger.info(f"Stored {memory_type.value} memory for user {user_id}", extra={
            "memory_id": str(memory.id),
            "content_length": len(content),
            "has_embedding": embedding is not None
        })
        return memory
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to store memory: {e}", extra={"user_id": str(user_id)})
        raise


async def _query_memories(
    db: AsyncSession,
    user_id: UUID,
    query_text: str,
    memory_types: Optional[List[MemoryType]] = None,
    limit: int = 5
) -> List[Memory]:
    """
    Query memories using basic vector similarity search.

    Note: This is simplified version for Story 2.5.
    Story 2.2 will add hybrid search (time decay + frequency boost).
    """
    query_embedding = await _generate_embedding(query_text)
    if not query_embedding:
        logger.warning("Could not generate query embedding, returning empty results")
        return []

    # Build query with vector similarity
    query = select(Memory).where(Memory.user_id == user_id)

    # Filter by memory types if provided
    if memory_types:
        query = query.where(Memory.memory_type.in_(memory_types))

    # Order by vector similarity (cosine distance)
    # Note: embedding <=> query_embedding uses pgvector's cosine distance operator
    query = query.order_by(Memory.embedding.cosine_distance(query_embedding))
    query = query.limit(limit)

    result = await db.execute(query)
    memories = result.scalars().all()

    logger.info(f"Retrieved {len(memories)} memories for query", extra={
        "user_id": str(user_id),
        "query_length": len(query_text),
        "memory_types": [mt.value for mt in memory_types] if memory_types else None
    })

    return list(memories)


# ============================================================================
# Helper Functions: LLM-Based Memory Classification
# ============================================================================


async def _classify_message_metadata_llm(
    message: str,
    memory_type: MemoryType
) -> Dict[str, Any]:
    """
    Use LLM to classify message and generate rich metadata.

    This is the CORRECT approach (not keyword heuristics).
    Returns type-specific metadata based on memory_type.
    """
    if not openai_client:
        return {"source": "conversation"}

    try:
        # Build classification prompt based on memory type
        if memory_type == MemoryType.PERSONAL:
            system_prompt = """You are an emotion and stressor classification expert.
Analyze the message and provide:
1. Dominant emotion (joy, anger, sadness, fear, love, surprise, neutral)
2. Emotion scores (all 7 emotions, 0.0-1.0)
3. Context (nuanced interpretation like 'overwhelm', 'frustration', 'loneliness')
4. Intensity (0.0-1.0)
5. Severity (mild_annoyance, persistent_stressor, compounding_event)
6. Whether it's a stressor (true/false)
7. Category (academic, family, social, work, health, relationship, financial, etc.)

Return JSON only, no explanation."""

            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify this message:\n\n{message}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for consistent classification
            )

            result = json.loads(response.choices[0].message.content)

            # Structure emotion metadata properly
            emotion_data = {
                "dominant": result.get("dominant_emotion", "neutral"),
                "scores": result.get("emotion_scores", {}),
                "context": result.get("context", ""),
                "intensity": result.get("intensity", 0.5),
                "severity": result.get("severity")
            }

            return {
                "source": "conversation",
                "emotion": emotion_data,
                "stressor": result.get("stressor", False),
                "category": result.get("category", "general"),
                "timestamp": datetime.utcnow().isoformat()
            }

        elif memory_type == MemoryType.PROJECT:
            system_prompt = """You are a goal classification expert.
Analyze the message and provide:
1. Goal scope (small_goal, big_goal)
2. Category (academic, career, personal, health, financial, relationship, etc.)
3. Timeline (short-term, medium-term, long-term)
4. Confidence (how committed the user seems, 0.0-1.0)
5. Whether it's goal-related (true/false)

Return JSON only, no explanation."""

            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify this goal/project message:\n\n{message}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            return {
                "source": "conversation",
                "goal_related": result.get("goal_related", True),
                "goal_scope": result.get("goal_scope", "small_goal"),
                "category": result.get("category", "general"),
                "timeline": result.get("timeline", "medium-term"),
                "confidence": result.get("confidence", 0.7),
                "timestamp": datetime.utcnow().isoformat()
            }

        elif memory_type == MemoryType.TASK:
            system_prompt = """You are a task classification expert.
Analyze the message and provide:
1. Task priority (low, medium, high)
2. Task difficulty (easy, medium, hard)
3. Category (academic, work, personal, health, etc.)
4. Estimated time (quick <30min, medium 30min-2h, long >2h)

Return JSON only, no explanation."""

            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify this task message:\n\n{message}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            return {
                "source": "conversation",
                "task_priority": result.get("task_priority", "medium"),
                "task_difficulty": result.get("task_difficulty", "medium"),
                "category": result.get("category", "general"),
                "estimated_time": result.get("estimated_time", "medium"),
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"LLM classification failed: {e}")
        return {"source": "conversation", "timestamp": datetime.utcnow().isoformat()}


async def _detect_memory_type_llm(message: str) -> MemoryType:
    """
    Use LLM to detect memory type (not keyword heuristics).

    This is the CORRECT approach that fixes the classification issues
    identified in the code review.
    """
    if not openai_client:
        return MemoryType.TASK  # Default fallback

    try:
        system_prompt = """You are a memory type classifier.
Classify the message into ONE of these types:

- PERSONAL: Emotions, struggles, stressors, preferences, identity
  Examples: "I'm overwhelmed", "I feel stressed", "I prefer mornings"

- PROJECT: Goals, plans, aspirations, long-term objectives
  Examples: "I want to graduate early", "My goal is to...", "I'm working towards..."

- TASK: Actions, activities, specific things to do
  Examples: "I completed my walk", "I need to study", "I'm working on chapter 3"

Return ONLY one word: PERSONAL, PROJECT, or TASK"""

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.1,  # Very low temperature for consistent classification
            max_tokens=10
        )

        result = response.choices[0].message.content.strip().upper()

        if result == "PERSONAL":
            return MemoryType.PERSONAL
        elif result == "PROJECT":
            return MemoryType.PROJECT
        else:
            return MemoryType.TASK

    except Exception as e:
        logger.error(f"LLM memory type detection failed: {e}")
        return MemoryType.TASK  # Safe default


async def _classify_assistant_response(response: str) -> MemoryType:
    """
    Classify assistant response INDEPENDENTLY (don't inherit from user).

    This fixes the critical issue identified in code review where
    assistant responses incorrectly inherited the user's memory type.
    """
    return await _detect_memory_type_llm(response)


# ============================================================================
# Helper Functions: Token Counting and Cost Tracking
# ============================================================================


def _count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text using tiktoken.
    """
    try:
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Token counting failed: {e}")
        return len(text) // 4  # Rough approximation


def _calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Calculate cost in USD based on model pricing.

    Pricing (per 1M tokens):
    - gpt-3.5-turbo: $0.50 / $1.50 (input/output)
    - gpt-4o-mini: $0.15 / $0.60 (input/output)
    - gpt-4o: $2.50 / $10.00 (input/output)
    """
    pricing = {
        "gpt-3.5-turbo": (0.50 / 1_000_000, 1.50 / 1_000_000),
        "gpt-4o-mini": (0.15 / 1_000_000, 0.60 / 1_000_000),
        "gpt-4o": (2.50 / 1_000_000, 10.00 / 1_000_000),
    }

    input_price, output_price = pricing.get(model, pricing["gpt-4o-mini"])

    return (input_tokens * input_price) + (output_tokens * output_price)


# ============================================================================
# Main Endpoints
# ============================================================================


@router.post("/chat", response_model=ChatResponse)
async def chat_with_eliza(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to Eliza and initiate conversation.

    Returns conversation_id for retrieving SSE streaming response.
    """
    try:
        # Create or retrieve conversation ID
        conversation_id = request.conversation_id or uuid4()

        # Detect memory type using LLM (not keywords!)
        user_memory_type = await _detect_memory_type_llm(request.message)

        # Classify message metadata using LLM
        user_metadata = await _classify_message_metadata_llm(request.message, user_memory_type)
        user_metadata["conversation_id"] = str(conversation_id)
        user_metadata["model_requested"] = request.model

        # Store user message as memory
        await _store_memory(
            db=db,
            user_id=current_user.id,
            memory_type=user_memory_type,
            content=request.message,
            metadata=user_metadata,
            conversation_id=conversation_id
        )

        logger.info(f"Chat message received from user {current_user.id}", extra={
            "conversation_id": str(conversation_id),
            "memory_type": user_memory_type.value,
            "message_length": len(request.message),
            "model": request.model
        })

        return ChatResponse(
            conversation_id=conversation_id,
            message=request.message,
            status="processing"
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")


@router.get("/stream/{conversation_id}")
async def stream_response(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    token: str = Query(..., description="Auth token for EventSource")  # EventSource can't set headers
):
    """
    Stream Eliza's response via SSE (Server-Sent Events).

    Returns token-by-token streaming response with final token count and cost.
    """
    async def event_generator():
        try:
            # Get user's last message in this conversation
            result = await db.execute(
                select(Memory)
                .where(
                    Memory.user_id == current_user.id,
                    Memory.extra_data["conversation_id"].astext == str(conversation_id)
                )
                .order_by(desc(Memory.created_at))
                .limit(1)
            )
            last_user_memory = result.scalars().first()

            if not last_user_memory:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No messages found in conversation'})}\n\n"
                return

            last_user_message = last_user_memory.content
            last_user_memory_type = last_user_memory.memory_type

            # Get model from user's message metadata (or default)
            model = last_user_memory.extra_data.get("model_requested", "gpt-4o-mini")

            # Query relevant memories for context (last 10 messages + 5 semantic matches)
            conversation_history_result = await db.execute(
                select(Memory)
                .where(
                    Memory.user_id == current_user.id,
                    Memory.extra_data["conversation_id"].astext == str(conversation_id)
                )
                .order_by(desc(Memory.created_at))
                .limit(10)
            )
            conversation_history = conversation_history_result.scalars().all()

            # Semantic search for relevant memories
            relevant_memories = await _query_memories(
                db=db,
                user_id=current_user.id,
                query_text=last_user_message,
                limit=5
            )

            # Build system prompt with memory context
            system_prompt = """You are Eliza, an emotionally intelligent AI companion.

You help users balance ambition with well-being. You:
- Listen empathetically to their struggles
- Remember past conversations and reference them
- Validate their feelings before offering suggestions
- Distinguish between controllable and uncontrollable stressors
- Suggest circuit breakers when they're overwhelmed
- Celebrate their wins and encourage momentum

Be warm, supportive, and contextual."""

            if relevant_memories:
                memory_context = "\n\nWhat you remember about this user:\n"
                for memory in relevant_memories:
                    memory_type_label = memory.memory_type.value.upper()
                    memory_context += f"- [{memory_type_label}] {memory.content}\n"
                system_prompt += memory_context

            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history (last 10 messages, in chronological order)
            for msg in reversed(list(conversation_history)):
                # Determine role based on metadata or content
                role = "assistant" if msg.extra_data.get("role") == "assistant" else "user"
                messages.append({"role": role, "content": msg.content})

            # Count input tokens
            input_text = system_prompt + "\n".join([m["content"] for m in messages])
            input_tokens = _count_tokens(input_text, model)

            # Stream response from OpenAI
            if not openai_client:
                yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI client not configured'})}\n\n"
                return

            stream = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000
            )

            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            # Count output tokens and calculate cost
            output_tokens = _count_tokens(full_response, model)
            total_tokens = input_tokens + output_tokens
            cost = _calculate_cost(input_tokens, output_tokens, model)

            # Classify assistant response INDEPENDENTLY (don't inherit user's type)
            assistant_memory_type = await _classify_assistant_response(full_response)

            # Generate metadata for assistant response
            assistant_metadata = await _classify_message_metadata_llm(full_response, assistant_memory_type)
            assistant_metadata["conversation_id"] = str(conversation_id)
            assistant_metadata["role"] = "assistant"
            assistant_metadata["model"] = model
            assistant_metadata["tokens_used"] = total_tokens
            assistant_metadata["cost"] = cost

            # Store assistant response as memory (with INDEPENDENT typing)
            await _store_memory(
                db=db,
                user_id=current_user.id,
                memory_type=assistant_memory_type,  # INDEPENDENT classification!
                content=full_response,
                metadata=assistant_metadata,
                conversation_id=conversation_id
            )

            logger.info(f"Completed streaming response", extra={
                "conversation_id": str(conversation_id),
                "user_memory_type": last_user_memory_type.value,
                "assistant_memory_type": assistant_memory_type.value,  # May differ!
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
                "model": model
            })

            # Send completion event with cost info
            yield f"data: {json.dumps({'type': 'complete', 'total_tokens': total_tokens, 'cost': cost, 'model': model})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation history for user.

    Returns conversations grouped by conversation_id with messages.
    """
    try:
        # Get all memories with conversation_id for this user
        result = await db.execute(
            select(Memory)
            .where(Memory.user_id == current_user.id)
            .where(Memory.extra_data["conversation_id"].isnot(None))
            .order_by(desc(Memory.created_at))
            .limit(limit * 2)  # Fetch more to account for grouping
        )
        memories = result.scalars().all()

        # Group memories by conversation_id
        conversations_dict = {}
        for memory in memories:
            conv_id = memory.extra_data.get("conversation_id")
            if not conv_id:
                continue

            if conv_id not in conversations_dict:
                conversations_dict[conv_id] = {
                    "conversation_id": conv_id,
                    "messages": [],
                    "started_at": memory.created_at,
                    "last_message_at": memory.created_at,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }

            # Add message
            role = memory.extra_data.get("role", "user")
            conversations_dict[conv_id]["messages"].append(
                ConversationMessage(
                    role=role,
                    content=memory.content,
                    timestamp=memory.created_at,
                    tokens_used=memory.extra_data.get("tokens_used"),
                    cost=memory.extra_data.get("cost"),
                    model=memory.extra_data.get("model")
                )
            )

            # Update timestamps
            if memory.created_at < conversations_dict[conv_id]["started_at"]:
                conversations_dict[conv_id]["started_at"] = memory.created_at
            if memory.created_at > conversations_dict[conv_id]["last_message_at"]:
                conversations_dict[conv_id]["last_message_at"] = memory.created_at

            # Accumulate tokens and cost
            if memory.extra_data.get("tokens_used"):
                conversations_dict[conv_id]["total_tokens"] += memory.extra_data["tokens_used"]
            if memory.extra_data.get("cost"):
                conversations_dict[conv_id]["total_cost"] += memory.extra_data["cost"]

        # Convert to list and sort by last_message_at
        conversations = [
            ConversationResponse(
                conversation_id=UUID(conv["conversation_id"]),
                messages=sorted(conv["messages"], key=lambda m: m.timestamp),
                started_at=conv["started_at"],
                last_message_at=conv["last_message_at"],
                total_tokens=conv["total_tokens"] if conv["total_tokens"] > 0 else None,
                total_cost=conv["total_cost"] if conv["total_cost"] > 0 else None
            )
            for conv in conversations_dict.values()
        ]
        conversations.sort(key=lambda c: c.last_message_at, reverse=True)
        conversations = conversations[:limit]

        return ConversationHistoryResponse(
            conversations=conversations,
            total_count=len(conversations)
        )

    except Exception as e:
        logger.error(f"History endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation history: {str(e)}")


@router.get("/debug/memory-stats", response_model=MemoryDebugStats)
async def get_memory_debug_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get memory statistics for debugging (not user-facing).

    Shows distribution by type and recent memories.
    """
    try:
        # Get total memory count
        total_result = await db.execute(
            select(func.count(Memory.id)).where(Memory.user_id == current_user.id)
        )
        total_memories = total_result.scalar()

        # Get counts by type
        by_type_stats = []
        for memory_type in MemoryType:
            count_result = await db.execute(
                select(func.count(Memory.id))
                .where(Memory.user_id == current_user.id)
                .where(Memory.memory_type == memory_type)
            )
            count = count_result.scalar()

            recent_count_result = await db.execute(
                select(func.count(Memory.id))
                .where(Memory.user_id == current_user.id)
                .where(Memory.memory_type == memory_type)
                .where(Memory.created_at >= datetime.utcnow() - timedelta(days=7))
            )
            recent_count = recent_count_result.scalar()

            by_type_stats.append(
                MemoryTypeStats(
                    memory_type=memory_type.value,
                    count=count,
                    recent_count=recent_count
                )
            )

        # Get recent memories
        recent_result = await db.execute(
            select(Memory)
            .where(Memory.user_id == current_user.id)
            .order_by(desc(Memory.created_at))
            .limit(10)
        )
        recent_memories = recent_result.scalars().all()

        recent_memories_data = [
            {
                "id": str(mem.id),
                "type": mem.memory_type.value,
                "content": mem.content[:100] + "..." if len(mem.content) > 100 else mem.content,
                "created_at": mem.created_at.isoformat(),
                "metadata": mem.extra_data
            }
            for mem in recent_memories
        ]

        return MemoryDebugStats(
            total_memories=total_memories,
            by_type=by_type_stats,
            recent_memories=recent_memories_data
        )

    except Exception as e:
        logger.error(f"Memory stats endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory stats: {str(e)}")


@router.get("/cost-summary", response_model=CostSummary)
async def get_cost_summary(
    period: str = Query("today", regex="^(today|week|month|all_time)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost summary for user's API usage.

    Tracks token usage and costs across different models.
    """
    try:
        # Determine time filter
        time_filter = None
        if period == "today":
            time_filter = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            time_filter = datetime.utcnow() - timedelta(days=7)
        elif period == "month":
            time_filter = datetime.utcnow() - timedelta(days=30)

        # Query memories with cost data
        query = select(Memory).where(Memory.user_id == current_user.id)
        if time_filter:
            query = query.where(Memory.created_at >= time_filter)

        result = await db.execute(query)
        memories = result.scalars().all()

        # Aggregate by model
        total_cost = 0.0
        total_tokens = 0
        by_model = {}

        for memory in memories:
            if not memory.extra_data.get("cost"):
                continue

            model = memory.extra_data.get("model", "unknown")
            cost = memory.extra_data.get("cost", 0.0)
            tokens = memory.extra_data.get("tokens_used", 0)

            total_cost += cost
            total_tokens += tokens

            if model not in by_model:
                by_model[model] = {"tokens": 0, "cost": 0.0, "count": 0}

            by_model[model]["tokens"] += tokens
            by_model[model]["cost"] += cost
            by_model[model]["count"] += 1

        return CostSummary(
            total_cost=round(total_cost, 4),
            total_tokens=total_tokens,
            by_model=by_model,
            period=period
        )

    except Exception as e:
        logger.error(f"Cost summary endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cost summary: {str(e)}")
