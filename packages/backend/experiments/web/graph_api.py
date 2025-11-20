"""
Memory Graph API

Provides endpoints for:
- Creating typed relationships between memories
- Querying graph relationships
- Traversing the memory graph
- Visualizing the graph structure
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.db.session import AsyncSessionLocal
from app.models.memory import Memory
from experiments.memory.memory_graph import MemoryGraph, RelationshipType, GraphPath, GraphNode
from sqlalchemy import select

router = APIRouter(prefix="/api/graph", tags=["graph"])


# ============================================================================
# Pydantic Models
# ============================================================================

class CreateRelationshipRequest(BaseModel):
    from_memory_id: str
    to_memory_id: str
    relationship_type: str  # "works_on", "located_at", etc.
    strength: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    bidirectional: bool = False


class RelationshipResponse(BaseModel):
    from_memory_id: str
    to_memory_id: str
    relationship_type: str
    strength: float
    metadata: Dict[str, Any]


class GraphNodeResponse(BaseModel):
    memory_id: str
    content: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    memory_type: str
    created_at: str


class GraphPathResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    relationships: List[RelationshipResponse]
    total_strength: float
    path_length: int


class GraphVisualizationResponse(BaseModel):
    nodes: List[Dict[str, Any]]  # For D3.js/React Flow
    edges: List[Dict[str, Any]]


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/relationship")
async def create_relationship(request: CreateRelationshipRequest):
    """Create a typed relationship between two memories."""

    try:
        from_id = UUID(request.from_memory_id)
        to_id = UUID(request.to_memory_id)
        rel_type = RelationshipType(request.relationship_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    async with AsyncSessionLocal() as db:
        graph = MemoryGraph()

        try:
            relationship = await graph.create_relationship(
                from_memory_id=from_id,
                to_memory_id=to_id,
                relationship_type=rel_type,
                strength=request.strength,
                metadata=request.metadata or {},
                bidirectional=request.bidirectional,
                db=db
            )

            return {
                "status": "created",
                "relationship": RelationshipResponse(
                    from_memory_id=str(relationship.from_memory_id),
                    to_memory_id=str(relationship.to_memory_id),
                    relationship_type=relationship.relationship_type.value,
                    strength=relationship.strength,
                    metadata=relationship.metadata
                )
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create relationship: {str(e)}")


@router.get("/relationships/{memory_id}")
async def get_relationships(
    memory_id: str,
    relationship_type: Optional[str] = None,
    min_strength: float = 0.0
):
    """Get all relationships for a memory."""

    try:
        mem_id = UUID(memory_id)
        rel_type = RelationshipType(relationship_type) if relationship_type else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    async with AsyncSessionLocal() as db:
        graph = MemoryGraph()

        try:
            related = await graph.get_related_memories(
                memory_id=mem_id,
                relationship_type=rel_type,
                min_strength=min_strength,
                db=db
            )

            return {
                "memory_id": memory_id,
                "relationships": [
                    {
                        "memory": {
                            "id": str(mem.id),
                            "content": mem.content,
                            "entity_id": mem.extra_data.get("entity_id") if mem.extra_data else None,
                            "entity_type": mem.extra_data.get("entity_type") if mem.extra_data else None
                        },
                        "relationship": RelationshipResponse(
                            from_memory_id=memory_id,
                            to_memory_id=str(mem.id),
                            relationship_type=rel.relationship_type.value,
                            strength=rel.strength,
                            metadata=rel.metadata
                        )
                    }
                    for mem, rel in related
                ]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get relationships: {str(e)}")


@router.get("/traverse/{start_memory_id}")
async def traverse_graph(
    start_memory_id: str,
    max_depth: int = 3,
    min_strength: float = 0.5
):
    """Traverse the graph from a starting memory."""

    try:
        start_id = UUID(start_memory_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID")

    async with AsyncSessionLocal() as db:
        graph = MemoryGraph()

        try:
            paths = await graph.traverse_graph(
                start_memory_id=start_id,
                max_depth=max_depth,
                min_strength=min_strength,
                db=db
            )

            return {
                "start_memory_id": start_memory_id,
                "paths_found": len(paths),
                "paths": [
                    GraphPathResponse(
                        nodes=[
                            GraphNodeResponse(
                                memory_id=str(node.memory_id),
                                content=node.content,
                                entity_id=node.entity_id,
                                entity_type=node.entity_type,
                                memory_type="personal",
                                created_at=datetime.now().isoformat()
                            )
                            for node in path.nodes
                        ],
                        relationships=[
                            RelationshipResponse(
                                from_memory_id=str(rel.from_memory_id),
                                to_memory_id=str(rel.to_memory_id),
                                relationship_type=rel.relationship_type.value,
                                strength=rel.strength,
                                metadata=rel.metadata
                            )
                            for rel in path.relationships
                        ],
                        total_strength=path.total_strength,
                        path_length=path.path_length
                    )
                    for path in paths[:10]  # Limit to 10 paths
                ]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to traverse graph: {str(e)}")


@router.get("/visualize/{user_id}")
async def visualize_graph(
    user_id: str,
    entity_type: Optional[str] = None,
    limit: int = 50
):
    """Get graph data for visualization (D3.js/React Flow format)."""

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    try:
        async with AsyncSessionLocal() as db:
            graph = MemoryGraph()

            try:
                # Get all hierarchical memories for user
                stmt = select(Memory).where(
                    Memory.user_id == user_uuid,
                    Memory.extra_data["storage_type"].astext == "hierarchical_eav"
                )

                if entity_type:
                    stmt = stmt.where(Memory.extra_data["entity_type"].astext == entity_type)

                stmt = stmt.limit(limit)

                result = await db.execute(stmt)
                memories = result.scalars().all()

                # Build nodes and edges
                nodes = []
                edges = []
                edge_id = 0

                for memory in memories:
                    if not memory.extra_data or "entity_id" not in memory.extra_data:
                        continue

                    entity_id = memory.extra_data["entity_id"]
                    entity_type_val = memory.extra_data.get("entity_type", "unknown")

                    # Create node
                    node = {
                        "id": str(memory.id),
                        "label": entity_id,
                        "type": entity_type_val,
                        "content": memory.content[:100],
                        "attributes": memory.extra_data.get("attributes", {}),
                        "created_at": memory.created_at.isoformat() if memory.created_at else None
                    }
                    nodes.append(node)

                    # Create edges from relationships
                    relationships_data = memory.extra_data.get("relationships", {})
                    for rel_type, rels in relationships_data.items():
                        for rel in rels:
                            edge_id += 1
                            edge = {
                                "id": f"edge-{edge_id}",
                                "source": str(memory.id),
                                "target": rel["to_memory_id"],
                                "label": rel_type,
                                "strength": rel.get("strength", 1.0),
                                "metadata": rel.get("metadata", {})
                            }
                            edges.append(edge)

                return GraphVisualizationResponse(
                    nodes=nodes,
                    edges=edges
                )

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"❌ Error in visualize_graph (query): {e}")
                print(error_details)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to query graph data: {str(e)}"
                )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in visualize_graph (database): {e}")
        print(error_details)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to visualize graph: {str(e)}"
        )


@router.get("/shortest-path/{from_memory_id}/{to_memory_id}")
async def find_shortest_path(from_memory_id: str, to_memory_id: str):
    """Find shortest path between two memories."""

    try:
        from_id = UUID(from_memory_id)
        to_id = UUID(to_memory_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory IDs")

    async with AsyncSessionLocal() as db:
        graph = MemoryGraph()

        try:
            path = await graph.find_shortest_path(from_id, to_id, db)

            if not path:
                return {"found": False, "message": "No path found between memories"}

            return {
                "found": True,
                "path": GraphPathResponse(
                    nodes=[
                        GraphNodeResponse(
                            memory_id=str(node.memory_id),
                            content=node.content,
                            entity_id=node.entity_id,
                            entity_type=node.entity_type,
                            memory_type="personal",
                            created_at=datetime.now().isoformat()
                        )
                        for node in path.nodes
                    ],
                    relationships=[
                        RelationshipResponse(
                            from_memory_id=str(rel.from_memory_id),
                            to_memory_id=str(rel.to_memory_id),
                            relationship_type=rel.relationship_type.value,
                            strength=rel.strength,
                            metadata=rel.metadata
                        )
                        for rel in path.relationships
                    ],
                    total_strength=path.total_strength,
                    path_length=path.path_length
                )
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to find path: {str(e)}")


@router.get("/entity-graph/{user_id}")
async def get_entity_graph(user_id: str, entity_type: Optional[str] = None):
    """Get complete entity relationship graph."""

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    async with AsyncSessionLocal() as db:
        graph = MemoryGraph()

        try:
            entity_graph = await graph.get_entity_graph(
                user_id=user_uuid,
                entity_type=entity_type,
                db=db
            )

            return {
                "user_id": user_id,
                "entity_count": len(entity_graph),
                "graph": {
                    entity_id: [
                        {
                            "target_entity": target,
                            "relationship_type": rel_type.value,
                            "strength": strength
                        }
                        for target, rel_type, strength in relationships
                    ]
                    for entity_id, relationships in entity_graph.items()
                }
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get entity graph: {str(e)}")
