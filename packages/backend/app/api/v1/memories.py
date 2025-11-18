"""
Memory API endpoints - CRUD operations and semantic search

Provides comprehensive memory management:
- Create memory with automatic embedding generation
- Retrieve memories with hybrid search
- Update memory and regenerate embeddings
- Delete memory
- Semantic similarity search
- Strategic context retrieval (3-tier)
- Store summaries and insights
"""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clerk_auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.memory import MemoryType
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemoryWithDistance,
)
from app.services.memory_service import get_memory_service

router = APIRouter(prefix="/memories", tags=["memories"])
memory_service = get_memory_service()


@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(
    memory_data: MemoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create new memory with automatic embedding generation

    - **memory_type**: personal (never pruned), project (goals), task (30-day retention)
    - **content**: Human-readable memory content (1-10000 chars)
    - **metadata**: Optional JSONB metadata (stressor info, emotion scores, etc.)

    Automatically generates 1536-dim embedding vector using OpenAI text-embedding-3-small.

    Returns:
        Created memory with embedding
    """
    memory = await memory_service.add_memory(db, current_user.id, memory_data)
    return memory


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    memory_type: Optional[MemoryType] = Query(None, description="Filter by memory tier"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """
    List user's memories with pagination

    - **memory_type**: Optional filter (personal, project, task)
    - **limit**: Maximum results (1-100)
    - **offset**: Pagination offset

    Returns memories ordered by access time (most recent first).
    """
    memories = await memory_service.query_memories(
        db, current_user.id, memory_type, limit, offset
    )
    return memories


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Retrieve single memory by ID

    Updates access time for LRU tracking.

    Raises:
        404: Memory not found
    """
    memory = await memory_service.get_memory(db, current_user.id, memory_id)

    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: UUID,
    memory_data: MemoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update existing memory

    If content is changed, automatically regenerates embedding.

    Raises:
        404: Memory not found
    """
    memory = await memory_service.update_memory(db, current_user.id, memory_id, memory_data)

    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    return memory


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete memory by ID

    Raises:
        404: Memory not found
    """
    deleted = await memory_service.delete_memory(db, current_user.id, memory_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")

    return None


@router.post("/search", response_model=List[MemoryWithDistance])
async def semantic_search(
    query_text: str = Query(..., min_length=1, description="Search query text"),
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    memory_type: Optional[MemoryType] = Query(None, description="Filter by memory tier"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    similarity_threshold: float = Query(0.5, ge=0.0, le=1.0, description="Min similarity"),
):
    """
    Semantic similarity search with hybrid scoring

    Uses hybrid search algorithm:
    - Base: Cosine similarity from pgvector
    - Time boost: Recent memories prioritized
    - Frequency boost: Frequently accessed memories boosted

    Args:
        query_text: Text to find similar memories for
        memory_type: Optional filter (personal, project, task)
        limit: Max results
        similarity_threshold: Minimum similarity score (0.0-1.0)

    Returns:
        List of memories sorted by hybrid score (highest first)
    """
    results = await memory_service.semantic_search(
        db,
        current_user.id,
        query_text,
        memory_type,
        limit,
        similarity_threshold,
    )

    return results


@router.get("/context/strategic", response_model=dict)
async def get_strategic_context(
    query_text: str = Query(..., min_length=1, description="Current context/conversation"),
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    3-tier strategic context retrieval for AI agents

    Strategy:
    - PERSONAL: Always retrieve top 5 (identity, preferences, stressors)
    - PROJECT: Retrieve top 10 if query mentions goals/plans
    - TASK: Retrieve top 5 recent conversations/actions

    Returns:
        Dict with keys: "personal", "project", "task"
        Each contains list of relevant memories with distance scores
    """
    context = await memory_service.strategic_context_retrieval(
        db, current_user.id, query_text
    )

    return context


@router.post("/summary", response_model=MemoryResponse, status_code=201)
async def store_summary(
    summary_content: str = Query(..., min_length=1, description="Summary text"),
    source_context: str = Query(..., description="What this summarizes"),
    memory_type: MemoryType = Query(MemoryType.TASK, description="Memory tier"),
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Store summary or derived insight as memory

    Enables agent learning by storing summaries, search results, or key insights
    as searchable memories for future reference.

    Args:
        summary_content: The summary or insight text
        source_context: Description of what this summarizes
        memory_type: Memory tier (default: TASK)

    Returns:
        Created memory with embedding
    """
    memory = await memory_service.store_summary(
        db,
        current_user.id,
        summary_content,
        source_context,
        memory_type,
        metadata={
            "is_summary": True,
            "source_context": source_context,
            "created_from": "agent_learning",
        },
    )

    return memory


@router.get("/priorities", response_model=dict)
async def get_user_priorities(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Analyze PERSONAL memories to identify user's core values/priorities

    Extracts universal factors (learning, discipline, etc.) from stressor
    and preference memories to understand what matters most to the user.

    Returns:
        Dict mapping priority names to importance scores (0.0-1.0)
    """
    priorities = await memory_service.calculate_user_priorities(db, current_user.id)

    return {"priorities": priorities}
