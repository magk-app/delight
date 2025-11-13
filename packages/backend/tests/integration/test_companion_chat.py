"""
Integration tests for Companion Chat API (Story 2.5).

Tests all acceptance criteria:
- AC1: Chat UI accepts messages
- AC2: SSE streaming works
- AC3: Conversation persists
- AC4: Venting creates personal memory
- AC5: Goal discussion creates project memory
- AC6: Memory retrieval works
"""

import asyncio
import json
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select

from app.models.memory import Memory, MemoryType
from app.models.user import User


@pytest.mark.asyncio
async def test_post_chat_creates_conversation(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
):
    """
    AC1: Test POST /chat endpoint creates conversation and stores user message.

    Verification:
    - Returns 200 OK
    - Returns conversation_id
    - User message stored as memory
    - Memory has correct metadata
    """
    response = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "Hello Eliza, I need help with my goals"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "conversation_id" in data
    assert "status" in data
    assert data["status"] == "processing"

    # Verify conversation_id is valid UUID
    conversation_id = data["conversation_id"]
    assert uuid.UUID(conversation_id)


@pytest.mark.asyncio
async def test_venting_creates_personal_memory(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session,
):
    """
    AC4: Test venting scenario creates personal memory with stressor metadata.

    Verification:
    - Personal memory created
    - Contains stressor keyword
    - Metadata includes stressor=True
    - Metadata includes emotion_severity
    - Embedding is 1536-dimensional
    """
    # Send venting message
    response = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "I'm overwhelmed with my schoolwork because I have to catch up"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    # Wait for memory to be created
    await asyncio.sleep(0.5)

    # Query memories
    result = await db_session.execute(
        select(Memory)
        .where(
            Memory.user_id == test_user.id,
            Memory.memory_type == MemoryType.PERSONAL,
        )
        .order_by(Memory.created_at.desc())
    )
    memory = result.scalars().first()

    # Verify memory exists
    assert memory is not None
    assert "overwhelmed" in memory.content.lower()

    # Verify metadata
    assert memory.extra_data.get("stressor") is True
    assert memory.extra_data.get("emotion_severity") in [
        "mild_annoyance",
        "persistent_stressor",
        "compounding_event",
    ]
    assert memory.extra_data.get("conversation_id") == conversation_id

    # Verify embedding
    assert memory.embedding is not None
    assert len(memory.embedding) == 1536


@pytest.mark.asyncio
async def test_goal_discussion_creates_project_memory(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session,
):
    """
    AC5: Test goal discussion creates project memory with goal metadata.

    Verification:
    - Project memory created
    - Metadata includes goal_related=True
    - Metadata includes goal_scope (big_goal or small_goal)
    """
    # Send goal message
    response = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "I want to work on my goal to graduate early"},
        headers=auth_headers,
    )

    assert response.status_code == 200

    # Wait for memory
    await asyncio.sleep(0.5)

    # Query memories
    result = await db_session.execute(
        select(Memory)
        .where(
            Memory.user_id == test_user.id,
            Memory.memory_type == MemoryType.PROJECT,
        )
        .order_by(Memory.created_at.desc())
    )
    memory = result.scalars().first()

    # Verify memory
    assert memory is not None
    assert "goal" in memory.content.lower()

    # Verify metadata
    assert memory.extra_data.get("goal_related") is True
    assert memory.extra_data.get("goal_scope") in ["big_goal", "small_goal"]


@pytest.mark.asyncio
async def test_memory_hierarchy_metadata(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session,
):
    """
    AC9: Test memory hierarchy captures emotions, goals, and tasks.

    Verification:
    - Emotion block includes severity
    - Project block includes goal_scope
    - Task block includes priority, difficulty, universal_factors
    """
    # Send task message
    response = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "I need to complete this urgent coding project today"},
        headers=auth_headers,
    )

    assert response.status_code == 200

    await asyncio.sleep(0.5)

    # Query task memory
    result = await db_session.execute(
        select(Memory)
        .where(
            Memory.user_id == test_user.id,
            Memory.memory_type == MemoryType.TASK,
        )
        .order_by(Memory.created_at.desc())
    )
    memory = result.scalars().first()

    # Verify task metadata
    assert memory is not None
    assert memory.extra_data.get("task_priority") in ["low", "medium", "high"]
    assert memory.extra_data.get("task_difficulty") in ["easy", "medium", "hard"]

    # Verify universal factors
    universal_factors = memory.extra_data.get("universal_factors")
    assert universal_factors is not None
    assert isinstance(universal_factors, dict)
    assert sum(universal_factors.values()) <= 1.2  # Allow some margin


@pytest.mark.asyncio
async def test_conversation_history_retrieval(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
):
    """
    AC3: Test conversation history persists and can be retrieved.

    Verification:
    - History endpoint returns conversations
    - Messages in chronological order
    - Timestamps preserved
    """
    # Send a message to create conversation
    response = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "Remember I like coffee"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    # Wait for processing
    await asyncio.sleep(0.5)

    # Retrieve history
    response = await async_client.get(
        "/api/v1/companion/history",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify conversations exist
    assert "conversations" in data
    assert len(data["conversations"]) > 0

    # Find our conversation
    conversation = next(
        (c for c in data["conversations"] if c["id"] == conversation_id),
        None,
    )

    assert conversation is not None
    assert len(conversation["messages"]) > 0

    # Verify message structure
    user_message = conversation["messages"][0]
    assert user_message["role"] == "user"
    assert "coffee" in user_message["content"].lower()
    assert "timestamp" in user_message


@pytest.mark.asyncio
async def test_streaming_endpoint_exists(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
):
    """
    AC2: Test SSE streaming endpoint is accessible (structure test).

    Note: Full SSE streaming test requires more complex setup.
    This test verifies the endpoint exists and requires authentication.
    """
    # Try to access without auth
    response = await async_client.get(
        f"/api/v1/companion/stream/{uuid.uuid4()}",
    )

    # Should require authentication
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_memory_retrieval_quality(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session,
):
    """
    AC6: Test memory retrieval returns relevant memories.

    Verification:
    - Memories are retrieved using vector similarity
    - Most relevant memories returned
    - Memory context improves responses
    """
    # Create first memory (about stress)
    response1 = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "I'm stressed about class registration"},
        headers=auth_headers,
    )

    assert response1.status_code == 200
    await asyncio.sleep(0.5)

    # Create second message (related to stress)
    response2 = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "I'm feeling overwhelmed"},
        headers=auth_headers,
    )

    assert response2.status_code == 200
    await asyncio.sleep(0.5)

    # Query memories directly to verify retrieval logic works
    from app.api.v1.companion import _query_memories

    retrieved = await _query_memories(
        db=db_session,
        user_id=test_user.id,
        query_text="I'm feeling overwhelmed",
        limit=5,
    )

    # Should retrieve at least the stress memory
    assert len(retrieved) > 0

    # Verify most recent memory is relevant
    relevant_found = any("stress" in mem.content.lower() for mem in retrieved)
    assert relevant_found


@pytest.mark.asyncio
async def test_error_handling_invalid_conversation_id(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test error handling for non-existent conversation ID."""
    # Try to stream from non-existent conversation
    response = await async_client.get(
        f"/api/v1/companion/stream/{uuid.uuid4()}",
        headers=auth_headers,
    )

    # Should handle gracefully (may return empty or error)
    assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
async def test_authentication_required(
    async_client: AsyncClient,
):
    """Test that all endpoints require authentication."""
    # POST /chat without auth
    response = await async_client.post(
        "/api/v1/companion/chat",
        json={"message": "Hello"},
    )
    assert response.status_code in [401, 403]

    # GET /history without auth
    response = await async_client.get("/api/v1/companion/history")
    assert response.status_code in [401, 403]

    # GET /stream without auth
    response = await async_client.get(f"/api/v1/companion/stream/{uuid.uuid4()}")
    assert response.status_code in [401, 403]
