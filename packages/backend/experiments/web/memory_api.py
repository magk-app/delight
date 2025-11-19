"""
Memory API for experimental frontend

Provides endpoints for managing memories stored in PostgreSQL database.
Now integrated with sophisticated search strategies!
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

class MemorySearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 10
    auto_route: bool = True

# Try to import real memory service and search strategies
try:
    from app.db.session import AsyncSessionLocal
    from app.models.memory import Memory, MemoryType
    from sqlalchemy import select, desc, delete as sql_delete
    from experiments.memory.search_router import SearchRouter
    from experiments.memory.search_strategies import SemanticSearch

    class MemoryService:
        def __init__(self):
            """Initialize memory service with search capabilities"""
            self.search_router = SearchRouter()
            self.semantic_search = SemanticSearch()

        async def search_memories(
            self,
            query: str,
            user_id: UUID,
            limit: int = 10,
            auto_route: bool = True
        ) -> List:
            """Search memories using intelligent routing with fallback"""
            async with AsyncSessionLocal() as db:
                try:
                    print(f"\n🔍 Searching memories for user {user_id}")
                    print(f"   Query: '{query}'")
                    print(f"   Auto-route: {auto_route}")

                    results = await self.search_router.search(
                        query=query,
                        user_id=user_id,
                        db=db,
                        auto_route=auto_route,
                        limit=limit
                    )

                    # If no results, try with lower threshold semantic search
                    if len(results) == 0:
                        print(f"   ⚠️ No results with primary strategy, trying fallback...")
                        try:
                            # Try semantic search with lower threshold
                            fallback_results = await self.semantic_search.search(
                                query=query,
                                user_id=user_id,
                                db=db,
                                limit=limit,
                                threshold=0.5  # Lower threshold
                            )

                            if len(fallback_results) > 0:
                                print(f"   ✅ Fallback found {len(fallback_results)} results")
                                return fallback_results

                        except Exception as fallback_error:
                            print(f"   ❌ Fallback search error: {fallback_error}")

                        # If still no results, return most recent memories
                        print(f"   📅 No semantic results, returning most recent memories")
                        recent_memories = await self.get_memories(
                            user_id=user_id,
                            limit=limit
                        )

                        # Convert Memory objects to SearchResult-like format
                        from experiments.memory.types import SearchResult
                        results = [
                            SearchResult(
                                memory_id=m.id,
                                content=m.content,
                                score=0.5,  # Default score
                                memory_type=m.memory_type.value if hasattr(m.memory_type, 'value') else str(m.memory_type),
                                categories=m.extra_data.get("categories", []) if m.extra_data else [],
                                created_at=m.created_at,
                                metadata=m.extra_data or {}
                            )
                            for m in recent_memories
                        ]

                    print(f"   ✅ Returning {len(results)} total results")
                    return results
                except Exception as e:
                    print(f"   ❌ Search error: {e}")
                    import traceback
                    traceback.print_exc()
                    return []

        @staticmethod
        async def get_memories(
            user_id: Optional[UUID] = None,
            memory_type: Optional[str] = None,
            category: Optional[str] = None,
            limit: int = 50
        ) -> List[Memory]:
            """Get memories from database with filters (chronological order)"""
            async with AsyncSessionLocal() as db:
                try:
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
                        memories = [m for m in memories if category in m.extra_data.get("categories", []) if m.extra_data]

                    return memories
                except Exception as e:
                    print(f"❌ Error fetching memories: {e}")
                    import traceback
                    traceback.print_exc()
                    raise

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
            """Delete a memory with proper error handling"""
            async with AsyncSessionLocal() as db:
                try:
                    print(f"\n🗑️  Deleting memory {memory_id}")

                    # Fetch the memory first
                    query = select(Memory).where(Memory.id == memory_id)
                    result = await db.execute(query)
                    memory = result.scalar_one_or_none()

                    if not memory:
                        print(f"   ❌ Memory {memory_id} not found")
                        raise HTTPException(status_code=404, detail="Memory not found")

                    # Delete the memory
                    await db.delete(memory)
                    await db.commit()

                    print(f"   ✅ Successfully deleted memory {memory_id}")

                except HTTPException:
                    raise
                except Exception as e:
                    print(f"   ❌ Error deleting memory: {e}")
                    import traceback
                    traceback.print_exc()
                    await db.rollback()
                    raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")

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

    try:
        await memory_service.delete_memory(UUID(memory_id))
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")


@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(request: MemorySearchRequest):
    """Search memories using intelligent routing and semantic search"""
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service not available")

    try:
        user_uuid = UUID(request.user_id)

        # Use the search router with semantic search
        results = await memory_service.search_memories(
            query=request.query,
            user_id=user_uuid,
            limit=request.limit,
            auto_route=request.auto_route
        )

        # Convert SearchResult objects to MemoryResponse format
        responses = []
        for result in results:
            responses.append(MemoryResponse(
                id=str(result.memory_id),
                user_id=str(user_uuid),
                content=result.content,
                memory_type=result.memory_type,
                importance=result.score,  # Use search score as importance
                metadata=result.metadata or {},
                embedding=None,  # Don't send embeddings to frontend
                created_at=result.created_at.isoformat() if result.created_at else datetime.now().isoformat(),
                updated_at=result.created_at.isoformat() if result.created_at else datetime.now().isoformat()
            ))

        return responses

    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


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


@router.get("/debug/{user_id}")
async def debug_memories(user_id: str):
    """Debug endpoint to check memory state and embeddings"""
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service not available")

    try:
        user_uuid = UUID(user_id)
        all_memories = await memory_service.get_memories(user_id=user_uuid, limit=100)

        memories_with_embeddings = sum(1 for m in all_memories if m.embedding is not None)
        memories_without_embeddings = len(all_memories) - memories_with_embeddings

        # Get sample of memories
        sample_memories = []
        for m in all_memories[:10]:
            sample_memories.append({
                "id": str(m.id),
                "content": m.content[:100],
                "memory_type": m.memory_type.value if hasattr(m.memory_type, 'value') else str(m.memory_type),
                "has_embedding": m.embedding is not None,
                "embedding_dim": len(m.embedding) if m.embedding else 0,
                "categories": m.extra_data.get("categories", []) if m.extra_data else [],
                "created_at": m.created_at.isoformat() if m.created_at else None
            })

        return {
            "user_id": user_id,
            "total_memories": len(all_memories),
            "with_embeddings": memories_with_embeddings,
            "without_embeddings": memories_without_embeddings,
            "embedding_coverage": f"{(memories_with_embeddings / len(all_memories) * 100) if all_memories else 0:.1f}%",
            "sample_memories": sample_memories,
            "recommendation": (
                "✅ Good! Most memories have embeddings and can be searched semantically."
                if memories_with_embeddings > len(all_memories) * 0.8
                else "⚠️ Warning: Many memories are missing embeddings. Semantic search may not work well."
            )
        }

    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")
