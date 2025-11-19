"""
Memory API for experimental frontend

Provides endpoints for managing memories stored in PostgreSQL database.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

router = APIRouter(prefix="/api/memories", tags=["memories"])

# Pydantic models
class MemoryResponse(BaseModel):
    id: str
    user_id: str
    content: str
    memory_type: str
    importance: float
    metadata: dict
    embedding: Optional[List[float]] = None
    created_at: str
    updated_at: str

class MemoryUpdateRequest(BaseModel):
    content: Optional[str] = None
    importance: Optional[float] = None
    metadata: Optional[dict] = None

# Try to import real memory service
try:
    from app.db.session import AsyncSessionLocal
    from app.models.memory import Memory, MemoryType
    from sqlalchemy import select, desc

    class MemoryService:
        @staticmethod
        async def get_memories(
            user_id: Optional[UUID] = None,
            memory_type: Optional[str] = None,
            category: Optional[str] = None,
            limit: int = 50
        ) -> List[Memory]:
            """Get memories from database with filters"""
            async with AsyncSessionLocal() as db:
                query = select(Memory).order_by(desc(Memory.created_at))

                if user_id:
                    query = query.where(Memory.user_id == user_id)
                if memory_type:
                    query = query.where(Memory.memory_type == MemoryType(memory_type))

                query = query.limit(limit)

                result = await db.execute(query)
                memories = result.scalars().all()

                # Filter by category if specified
                if category:
                    memories = [m for m in memories if category in m.metadata.get("categories", [])]

                return memories

        @staticmethod
        async def update_memory(memory_id: UUID, updates: dict) -> Memory:
            """Update a memory"""
            async with AsyncSessionLocal() as db:
                query = select(Memory).where(Memory.id == memory_id)
                result = await db.execute(query)
                memory = result.scalar_one_or_none()

                if not memory:
                    raise HTTPException(status_code=404, detail="Memory not found")

                # Update fields
                if "content" in updates:
                    memory.content = updates["content"]
                if "importance" in updates:
                    memory.importance = updates["importance"]
                if "metadata" in updates:
                    memory.metadata = {**memory.metadata, **updates["metadata"]}

                await db.commit()
                await db.refresh(memory)

                return memory

        @staticmethod
        async def delete_memory(memory_id: UUID):
            """Delete a memory"""
            async with AsyncSessionLocal() as db:
                query = select(Memory).where(Memory.id == memory_id)
                result = await db.execute(query)
                memory = result.scalar_one_or_none()

                if not memory:
                    raise HTTPException(status_code=404, detail="Memory not found")

                await db.delete(memory)
                await db.commit()

    memory_service = MemoryService()
    print("✅ Real MemoryService loaded for API")

except ImportError as e:
    print(f"⚠️  Could not load MemoryService: {e}")
    memory_service = None


# API Endpoints
@router.get("/", response_model=List[MemoryResponse])
async def get_memories(
    user_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Get memories with optional filters"""
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service not available")

    user_uuid = UUID(user_id) if user_id else None

    memories = await memory_service.get_memories(
        user_id=user_uuid,
        memory_type=memory_type,
        category=category,
        limit=limit
    )

    return [
        MemoryResponse(
            id=str(m.id),
            user_id=str(m.user_id),
            content=m.content,
            memory_type=m.memory_type.value if hasattr(m.memory_type, 'value') else m.memory_type,
            importance=0.5,  # Default importance (not stored in DB yet)
            metadata=m.extra_data or {},  # extra_data maps to metadata column
            embedding=None,  # Don't send embeddings to frontend
            created_at=m.created_at.isoformat() if m.created_at else datetime.now().isoformat(),
            updated_at=m.accessed_at.isoformat() if m.accessed_at else m.created_at.isoformat(),  # Use accessed_at as updated_at
        )
        for m in memories
    ]


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: str, updates: MemoryUpdateRequest):
    """Update a memory"""
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service not available")

    update_dict = {}
    if updates.content is not None:
        update_dict["content"] = updates.content
    if updates.importance is not None:
        update_dict["importance"] = updates.importance
    if updates.metadata is not None:
        update_dict["metadata"] = updates.metadata

    memory = await memory_service.update_memory(UUID(memory_id), update_dict)

    return MemoryResponse(
        id=str(memory.id),
        user_id=str(memory.user_id),
        content=memory.content,
        memory_type=memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
        importance=0.5,  # Default importance
        metadata=memory.extra_data or {},  # extra_data maps to metadata column
        embedding=None,
        created_at=memory.created_at.isoformat() if memory.created_at else datetime.now().isoformat(),
        updated_at=memory.accessed_at.isoformat() if memory.accessed_at else memory.created_at.isoformat(),
    )


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory"""
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service not available")

    await memory_service.delete_memory(UUID(memory_id))

    return {"status": "deleted", "memory_id": memory_id}


@router.get("/stats")
async def get_memory_stats(user_id: Optional[str] = None):
    """Get memory statistics"""
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service not available")

    user_uuid = UUID(user_id) if user_id else None

    all_memories = await memory_service.get_memories(user_id=user_uuid, limit=10000)

    by_type = {}
    for memory in all_memories:
        mem_type = memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type
        by_type[mem_type] = by_type.get(mem_type, 0) + 1

    return {
        "total_memories": len(all_memories),
        "by_type": by_type,
        "recent_count": len([m for m in all_memories[:10]]),
    }
