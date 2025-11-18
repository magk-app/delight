"""
Knowledge Graph API endpoints - Entity and relationship management

Enables structured knowledge tracking:
- Create and update entities (people, projects, concepts, etc.)
- Record relationships between entities
- Query graph for context and reasoning
- Extract entities from memories
"""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clerk_auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.knowledge_graph import EntityType, RelationshipType, KnowledgeEntity
from app.schemas.knowledge_graph import (
    KnowledgeEntityCreate,
    KnowledgeEntityUpdate,
    KnowledgeEntityResponse,
    KnowledgeRelationshipCreate,
    KnowledgeRelationshipUpdate,
    KnowledgeRelationshipResponse,
)
from app.services.knowledge_graph_service import get_knowledge_graph_service

router = APIRouter(prefix="/knowledge", tags=["knowledge-graph"])
kg_service = get_knowledge_graph_service()


# ============================================================================
# Entity Endpoints
# ============================================================================


@router.post("/entities", response_model=KnowledgeEntityResponse, status_code=201)
async def create_entity(
    entity_data: KnowledgeEntityCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create new knowledge entity

    Automatically generates embedding for semantic entity search.
    Returns existing entity if name already exists.

    Args:
        entity_data: Entity details (type, name, description, properties)

    Returns:
        Created (or existing) entity with embedding
    """
    entity = await kg_service.create_entity(
        db,
        current_user.id,
        entity_data.name,
        entity_data.entity_type,
        entity_data.description,
        entity_data.properties,
        entity_data.confidence,
        entity_data.source_memory_id,
    )

    return entity


@router.get("/entities/{entity_id}", response_model=KnowledgeEntityResponse)
async def get_entity(
    entity_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get entity by ID

    Raises:
        404: Entity not found
    """
    entity = await db.get(KnowledgeEntity, entity_id)

    if not entity or entity.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Entity not found")

    return entity


@router.put("/entities/{entity_id}", response_model=KnowledgeEntityResponse)
async def update_entity_properties(
    entity_id: UUID,
    properties: dict = Query(..., description="Properties to update/merge"),
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    merge: bool = Query(True, description="Merge with existing properties"),
):
    """
    Update entity properties (learning new information)

    Args:
        entity_id: Entity to update
        properties: New properties to add/update
        merge: If True, merge with existing; if False, replace

    Raises:
        404: Entity not found
    """
    entity = await kg_service.update_entity_properties(
        db, current_user.id, entity_id, properties, merge
    )

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return entity


@router.get("/entities", response_model=List[KnowledgeEntityResponse])
async def search_entities(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    search_text: Optional[str] = Query(None, description="Search in names/descriptions"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """
    Search entities

    TODO: Implement full search with semantic similarity
    For now, returns basic filtered list.
    """
    from sqlalchemy import select
    from app.models.knowledge_graph import KnowledgeEntity

    query = select(KnowledgeEntity).where(KnowledgeEntity.user_id == current_user.id)

    if entity_type:
        query = query.where(KnowledgeEntity.entity_type == entity_type)

    if search_text:
        query = query.where(KnowledgeEntity.name.ilike(f"%{search_text}%"))

    query = query.limit(limit)

    result = await db.execute(query)
    entities = result.scalars().all()

    return entities


# ============================================================================
# Relationship Endpoints
# ============================================================================


@router.post("/relationships", response_model=KnowledgeRelationshipResponse, status_code=201)
async def create_relationship(
    rel_data: KnowledgeRelationshipCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create relationship between two entities

    Returns existing relationship if same triple already exists.

    Args:
        rel_data: Relationship details (from, to, type, properties)

    Returns:
        Created (or existing) relationship

    Raises:
        400: Entities don't exist or belong to different user
    """
    try:
        relationship = await kg_service.create_relationship(
            db,
            current_user.id,
            rel_data.from_entity_id,
            rel_data.to_entity_id,
            rel_data.relationship_type,
            rel_data.properties,
            rel_data.confidence,
            rel_data.source_memory_id,
        )

        return relationship

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/relationships/{relationship_id}", response_model=KnowledgeRelationshipResponse)
async def get_relationship(
    relationship_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get relationship by ID

    Raises:
        404: Relationship not found
    """
    from app.models.knowledge_graph import KnowledgeRelationship

    relationship = await db.get(KnowledgeRelationship, relationship_id)

    if not relationship or relationship.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return relationship


@router.get("/entities/{entity_id}/related", response_model=dict)
async def get_related_entities(
    entity_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    relationship_type: Optional[RelationshipType] = Query(
        None, description="Filter by relationship type"
    ),
    direction: str = Query(
        "both", description="Direction: outgoing, incoming, or both"
    ),
):
    """
    Get entities related to a given entity

    Args:
        entity_id: Entity to find relationships for
        relationship_type: Optional filter by relationship type
        direction: outgoing (from entity), incoming (to entity), or both

    Returns:
        List of (related_entity, relationship) tuples
    """
    if direction not in ["outgoing", "incoming", "both"]:
        raise HTTPException(
            status_code=400,
            detail="direction must be: outgoing, incoming, or both",
        )

    related = await kg_service.get_related_entities(
        db, current_user.id, entity_id, relationship_type, direction
    )

    # Format response
    return {
        "entity_id": str(entity_id),
        "related_count": len(related),
        "related": [
            {
                "entity": {
                    "id": str(entity.id),
                    "name": entity.name,
                    "type": entity.entity_type,
                    "description": entity.description,
                    "properties": entity.properties,
                },
                "relationship": {
                    "id": str(rel.id),
                    "type": rel.relationship_type,
                    "properties": rel.properties,
                    "confidence": rel.confidence,
                    "direction": (
                        "outgoing"
                        if rel.from_entity_id == entity_id
                        else "incoming"
                    ),
                },
            }
            for entity, rel in related
        ],
    }


@router.get("/entities/{entity_id}/context", response_model=dict)
async def get_entity_context(
    entity_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    max_depth: int = Query(2, ge=1, le=5, description="Max relationship depth"),
):
    """
    Get full context for an entity including relationships

    Returns entity details and all connected entities/relationships.

    Args:
        entity_id: Entity to get context for
        max_depth: Maximum relationship depth to traverse

    Returns:
        Complete entity context including relationships
    """
    context = await kg_service.get_entity_context(
        db, current_user.id, entity_id, max_depth
    )

    if not context:
        raise HTTPException(status_code=404, detail="Entity not found")

    return context


# ============================================================================
# Utility Endpoints
# ============================================================================


@router.post("/extract-from-memory/{memory_id}", response_model=List[KnowledgeEntityResponse])
async def extract_entities_from_memory(
    memory_id: UUID,
    memory_content: str = Query(..., description="Memory content to extract from"),
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Extract entities from memory content and add to knowledge graph

    Uses NLP/LLM to identify entities in memory content.
    (Simplified implementation - would use advanced NLP in production)

    Args:
        memory_id: Source memory ID
        memory_content: Text to extract entities from

    Returns:
        List of extracted/created entities
    """
    entities = await kg_service.extract_entities_from_memory(
        db, current_user.id, memory_id, memory_content
    )

    return entities
