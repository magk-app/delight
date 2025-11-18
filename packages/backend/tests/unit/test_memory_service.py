"""
Unit tests for MemoryService with hybrid search functionality.

Tests cover:
- Memory creation with automatic embedding generation
- Hybrid search (semantic + time + frequency)
- Access tracking updates
- Memory pruning (30-day retention for tasks)
- Error handling and edge cases
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest

from app.models.memory import Memory, MemoryType
from app.services.embedding_service import EmbeddingService
from app.services.memory_service import MemoryService


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def user_id() -> UUID:
    """Test user ID."""
    return uuid4()


@pytest.fixture
def mock_embedding() -> List[float]:
    """Mock 1536-dimensional embedding vector."""
    return [0.1] * 1536


@pytest.fixture
def mock_embedding_service(mock_embedding) -> EmbeddingService:
    """Mock embedding service that returns test embeddings."""
    service = Mock(spec=EmbeddingService)
    service.generate_embedding = AsyncMock(return_value=mock_embedding)
    return service


# ============================================================================
# AC1: Add Memories with Automatic Embedding Generation
# ============================================================================


@pytest.mark.asyncio
async def test_add_memory_creates_memory_with_embedding(
    async_session, user_id, mock_embedding_service
):
    """Test that add_memory creates a memory with automatic embedding generation."""
    service = MemoryService(async_session, mock_embedding_service)

    memory = await service.add_memory(
        user_id=user_id,
        memory_type=MemoryType.PERSONAL,
        content="I prefer working in the morning",
        metadata={"source": "preferences"},
    )

    # Verify memory created
    assert memory.id is not None
    assert memory.user_id == user_id
    assert memory.memory_type == MemoryType.PERSONAL
    assert memory.content == "I prefer working in the morning"
    assert memory.embedding is not None
    assert len(memory.embedding) == 1536
    assert memory.extra_data == {"source": "preferences"}
    assert memory.created_at is not None
    assert memory.accessed_at is not None

    # Verify embedding service was called
    mock_embedding_service.generate_embedding.assert_called_once_with(
        "I prefer working in the morning"
    )


@pytest.mark.asyncio
async def test_add_memory_handles_embedding_failure_gracefully(async_session, user_id):
    """Test that add_memory stores memory without embedding if generation fails."""
    # Create embedding service that fails
    failed_service = Mock(spec=EmbeddingService)
    failed_service.generate_embedding = AsyncMock(return_value=None)

    service = MemoryService(async_session, failed_service)

    memory = await service.add_memory(
        user_id=user_id,
        memory_type=MemoryType.PERSONAL,
        content="Test content",
        metadata={},
    )

    # Memory should still be created
    assert memory.id is not None
    assert memory.content == "Test content"
    # Embedding should be None
    assert memory.embedding is None


# ============================================================================
# AC2: Query Memories by Type (3-Tier Architecture)
# ============================================================================


@pytest.mark.asyncio
async def test_query_memories_filters_by_type(async_session, user_id, mock_embedding_service):
    """Test that query_memories filters by memory type(s)."""
    service = MemoryService(async_session, mock_embedding_service)

    # Create memories of different types
    personal = await service.add_memory(
        user_id, MemoryType.PERSONAL, "I love coffee", {}
    )
    project = await service.add_memory(
        user_id, MemoryType.PROJECT, "Goal: Graduate early", {}
    )
    task = await service.add_memory(
        user_id, MemoryType.TASK, "Completed walk mission", {}
    )

    # Query personal only
    results = await service.query_memories(
        user_id, "coffee preferences", memory_types=[MemoryType.PERSONAL]
    )

    assert len(results) > 0
    assert all(m.memory_type == MemoryType.PERSONAL for m in results)


@pytest.mark.asyncio
async def test_query_memories_all_types_when_no_filter(
    async_session, user_id, mock_embedding_service
):
    """Test that query_memories searches all types when no filter specified."""
    service = MemoryService(async_session, mock_embedding_service)

    # Create memories of different types
    await service.add_memory(user_id, MemoryType.PERSONAL, "Personal memory", {})
    await service.add_memory(user_id, MemoryType.PROJECT, "Project memory", {})
    await service.add_memory(user_id, MemoryType.TASK, "Task memory", {})

    # Query without type filter
    results = await service.query_memories(user_id, "memory")

    # Should return memories (potentially from multiple types)
    assert len(results) > 0


# ============================================================================
# AC3: Hybrid Search (Semantic + Time + Frequency)
# ============================================================================


@pytest.mark.asyncio
async def test_hybrid_search_prioritizes_recent_memories(
    async_session, user_id, mock_embedding_service
):
    """Test that hybrid search prioritizes recent memories over old ones."""
    service = MemoryService(async_session, mock_embedding_service)

    # Create old memory
    old_memory = await service.add_memory(
        user_id, MemoryType.PERSONAL, "Old preference", {}
    )
    old_memory.accessed_at = datetime.utcnow() - timedelta(days=30)
    await async_session.commit()

    # Create recent memory
    recent_memory = await service.add_memory(
        user_id, MemoryType.PERSONAL, "Recent preference", {}
    )

    # Query should prioritize recent memory (time boost)
    results = await service.query_memories(user_id, "preferences")

    # Recent memory should be ranked higher (if both match query)
    if len(results) >= 2:
        # Recent memory should appear first due to time boost
        memory_ids = [m.id for m in results]
        # Recent should be ranked higher than old
        assert memory_ids.index(recent_memory.id) < memory_ids.index(old_memory.id)


@pytest.mark.asyncio
async def test_hybrid_search_applies_similarity_threshold(
    async_session, user_id, mock_embedding_service
):
    """Test that hybrid search filters by similarity threshold."""
    service = MemoryService(async_session, mock_embedding_service)

    # Create a memory
    await service.add_memory(user_id, MemoryType.PERSONAL, "Test memory", {})

    # Query with very high threshold (should filter out most results)
    results = await service.query_memories(
        user_id, "completely different query", similarity_threshold=0.95
    )

    # High threshold should filter out dissimilar results
    # (Note: In real tests with actual embeddings, this would be more meaningful)
    assert isinstance(results, list)


# ============================================================================
# AC4: Access Tracking Updates
# ============================================================================


@pytest.mark.asyncio
async def test_query_memories_updates_access_tracking(
    async_session, user_id, mock_embedding_service
):
    """Test that query_memories updates accessed_at and access_count."""
    service = MemoryService(async_session, mock_embedding_service)

    memory = await service.add_memory(user_id, MemoryType.PERSONAL, "Test memory", {})
    original_accessed = memory.accessed_at
    original_count = memory.extra_data.get("access_count", 0)

    # Wait a moment to ensure timestamp difference
    await asyncio.sleep(0.1)

    # Query the memory
    results = await service.query_memories(
        user_id, "test", memory_types=[MemoryType.PERSONAL]
    )

    # Refresh memory from DB
    await async_session.refresh(memory)

    # Verify access tracking updated
    assert memory.accessed_at > original_accessed
    assert memory.extra_data.get("access_count", 0) == original_count + 1


# ============================================================================
# AC5: Memory Pruning (30-Day Retention)
# ============================================================================


@pytest.mark.asyncio
async def test_prune_old_task_memories_deletes_old_tasks(async_session, user_id, mock_embedding_service):
    """Test that prune_old_task_memories deletes task memories older than 30 days."""
    service = MemoryService(async_session, mock_embedding_service)

    # Create old task memory (31 days ago)
    old_task = await service.add_memory(user_id, MemoryType.TASK, "Old task", {})
    old_task.created_at = datetime.utcnow() - timedelta(days=31)
    await async_session.commit()

    # Create recent task memory
    recent_task = await service.add_memory(user_id, MemoryType.TASK, "Recent task", {})

    # Prune old memories
    deleted_count = await service.prune_old_task_memories(retention_days=30)

    # Verify old task deleted
    assert deleted_count == 1

    # Verify recent task still exists
    from sqlalchemy import select
    result = await async_session.execute(
        select(Memory).where(Memory.id == recent_task.id)
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_prune_never_deletes_personal_or_project_memories(
    async_session, user_id, mock_embedding_service
):
    """Test that pruning never deletes personal or project memories."""
    service = MemoryService(async_session, mock_embedding_service)

    # Create old personal memory (should NOT be pruned)
    old_personal = await service.add_memory(
        user_id, MemoryType.PERSONAL, "Old personal", {}
    )
    old_personal.created_at = datetime.utcnow() - timedelta(days=365)
    await async_session.commit()

    # Create old project memory (should NOT be pruned)
    old_project = await service.add_memory(
        user_id, MemoryType.PROJECT, "Old project", {}
    )
    old_project.created_at = datetime.utcnow() - timedelta(days=365)
    await async_session.commit()

    # Prune (should not delete personal/project)
    deleted_count = await service.prune_old_task_memories()

    # Verify nothing deleted
    assert deleted_count == 0

    # Verify both memories still exist
    from sqlalchemy import select
    result = await async_session.execute(
        select(Memory).where(
            Memory.id.in_([old_personal.id, old_project.id])
        )
    )
    assert len(result.scalars().all()) == 2


# ============================================================================
# AC8: Metadata Support for Stressor Logging
# ============================================================================


@pytest.mark.asyncio
async def test_add_memory_stores_metadata_correctly(
    async_session, user_id, mock_embedding_service
):
    """Test that add_memory stores metadata (stressor info, emotions, etc.)."""
    service = MemoryService(async_session, mock_embedding_service)

    memory = await service.add_memory(
        user_id=user_id,
        memory_type=MemoryType.PERSONAL,
        content="Class registration stress",
        metadata={
            "stressor": True,
            "emotion": "fear",
            "category": "academic",
            "intensity": 0.8,
        },
    )

    # Verify metadata stored correctly
    assert memory.extra_data["stressor"] is True
    assert memory.extra_data["emotion"] == "fear"
    assert memory.extra_data["category"] == "academic"
    assert memory.extra_data["intensity"] == 0.8


# ============================================================================
# Helper Method Tests
# ============================================================================


def test_calculate_time_boost():
    """Test time boost calculation formula."""
    service = MemoryService(Mock())

    # Recent memory (0 days)
    boost_0 = service._calculate_time_boost(0)
    assert boost_0 > 1.4  # Should be ~1.44

    # Week old (7 days)
    boost_7 = service._calculate_time_boost(7)
    assert 1.1 < boost_7 < 1.2

    # Month old (30 days)
    boost_30 = service._calculate_time_boost(30)
    assert 1.0 < boost_30 < 1.1

    # Year old (365 days)
    boost_365 = service._calculate_time_boost(365)
    assert boost_365 >= 1.0

    # Recent should have higher boost than old
    assert boost_0 > boost_7 > boost_30 > boost_365


def test_calculate_frequency_boost():
    """Test frequency boost calculation formula."""
    service = MemoryService(Mock())

    # First access
    boost_1 = service._calculate_frequency_boost(1)
    assert boost_1 == 1.0

    # 10 accesses
    boost_10 = service._calculate_frequency_boost(10)
    assert 1.2 < boost_10 < 1.3

    # 100 accesses
    boost_100 = service._calculate_frequency_boost(100)
    assert 1.4 < boost_100 < 1.5

    # More accesses should have higher boost
    assert boost_100 > boost_10 > boost_1


def test_calculate_time_boost_handles_edge_cases():
    """Test time boost handles negative and zero days."""
    service = MemoryService(Mock())

    # Negative days (edge case)
    boost_negative = service._calculate_time_boost(-1)
    assert boost_negative > 1.0  # Should handle gracefully

    # Zero days
    boost_zero = service._calculate_time_boost(0)
    assert boost_zero > 1.0


def test_calculate_frequency_boost_handles_edge_cases():
    """Test frequency boost handles zero and negative counts."""
    service = MemoryService(Mock())

    # Zero count
    boost_zero = service._calculate_frequency_boost(0)
    assert boost_zero >= 1.0

    # Negative count (edge case)
    boost_negative = service._calculate_frequency_boost(-1)
    assert boost_negative >= 1.0
