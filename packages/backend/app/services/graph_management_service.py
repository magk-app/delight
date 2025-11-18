"""
Graph management service for knowledge graph creation and updates.

Handles creating, updating, and deleting knowledge nodes and edges,
as well as associating memories with nodes.

Includes LLM-based entity extraction for automatic graph organization.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import (
    EdgeType,
    KnowledgeEdge,
    KnowledgeNode,
    Memory,
    MemoryNodeAssociation,
    NodeType,
)

logger = logging.getLogger(__name__)


class GraphManagementService:
    """
    Service for managing knowledge graph structure.

    Handles CRUD operations for nodes, edges, and memory-node associations,
    as well as automatic graph organization from memory content.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the graph management service.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_node(
        self,
        user_id: UUID,
        node_type: NodeType,
        name: str,
        description: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.5,
    ) -> KnowledgeNode:
        """
        Create a new knowledge graph node.

        Args:
            user_id: User identifier
            node_type: Type of node (topic, project, person, category, event)
            name: Human-readable node name
            description: Optional description
            embedding: Optional 1536-dim embedding vector
            metadata: Optional metadata dict
            importance_score: Initial importance (0-1), defaults to 0.5

        Returns:
            Created KnowledgeNode
        """
        # Check if node with same name and type already exists
        existing_stmt = select(KnowledgeNode).where(
            KnowledgeNode.user_id == user_id,
            KnowledgeNode.node_type == node_type,
            KnowledgeNode.name == name,
        )
        result = await self.db.execute(existing_stmt)
        existing_node = result.scalar_one_or_none()

        if existing_node:
            logger.info(
                f"Node already exists: {name} ({node_type}), returning existing node"
            )
            return existing_node

        node = KnowledgeNode(
            user_id=user_id,
            node_type=node_type,
            name=name,
            description=description,
            embedding=embedding,
            extra_data=metadata or {},
            importance_score=importance_score,
        )

        self.db.add(node)
        await self.db.flush()

        logger.info(f"Created node: {name} ({node_type}), id={node.id}")
        return node

    async def create_edge(
        self,
        user_id: UUID,
        source_node_id: UUID,
        target_node_id: UUID,
        edge_type: EdgeType,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeEdge:
        """
        Create a new knowledge graph edge.

        Args:
            user_id: User identifier
            source_node_id: Source node UUID
            target_node_id: Target node UUID
            edge_type: Type of relationship
            weight: Relationship strength (0-1), defaults to 1.0
            metadata: Optional metadata dict

        Returns:
            Created KnowledgeEdge
        """
        # Check if edge already exists (enforced by unique constraint)
        existing_stmt = select(KnowledgeEdge).where(
            KnowledgeEdge.user_id == user_id,
            KnowledgeEdge.source_node_id == source_node_id,
            KnowledgeEdge.target_node_id == target_node_id,
            KnowledgeEdge.edge_type == edge_type,
        )
        result = await self.db.execute(existing_stmt)
        existing_edge = result.scalar_one_or_none()

        if existing_edge:
            logger.info(
                f"Edge already exists: {source_node_id} -> {target_node_id} ({edge_type})"
            )
            # Update weight if provided
            if weight != existing_edge.weight:
                existing_edge.weight = weight
                await self.db.flush()
            return existing_edge

        edge = KnowledgeEdge(
            user_id=user_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            weight=weight,
            extra_data=metadata or {},
        )

        self.db.add(edge)
        await self.db.flush()

        logger.info(
            f"Created edge: {source_node_id} -> {target_node_id} ({edge_type})"
        )
        return edge

    async def associate_memory_with_node(
        self,
        memory_id: UUID,
        node_id: UUID,
        relevance_score: float = 1.0,
    ) -> MemoryNodeAssociation:
        """
        Associate a memory with a knowledge node.

        Args:
            memory_id: Memory UUID
            node_id: Knowledge node UUID
            relevance_score: How relevant memory is to node (0-1)

        Returns:
            Created MemoryNodeAssociation
        """
        # Check if association already exists (enforced by unique constraint)
        existing_stmt = select(MemoryNodeAssociation).where(
            MemoryNodeAssociation.memory_id == memory_id,
            MemoryNodeAssociation.node_id == node_id,
        )
        result = await self.db.execute(existing_stmt)
        existing_assoc = result.scalar_one_or_none()

        if existing_assoc:
            logger.info(
                f"Association already exists: memory {memory_id} <-> node {node_id}"
            )
            # Update relevance score if different
            if relevance_score != existing_assoc.relevance_score:
                existing_assoc.relevance_score = relevance_score
                await self.db.flush()
            return existing_assoc

        assoc = MemoryNodeAssociation(
            memory_id=memory_id,
            node_id=node_id,
            relevance_score=relevance_score,
        )

        self.db.add(assoc)
        await self.db.flush()

        logger.info(f"Associated memory {memory_id} with node {node_id}")
        return assoc

    async def update_node(
        self,
        node_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        importance_score: Optional[float] = None,
    ) -> Optional[KnowledgeNode]:
        """
        Update an existing knowledge node.

        Args:
            node_id: Node UUID
            name: Optional new name
            description: Optional new description
            embedding: Optional new embedding
            metadata: Optional new metadata (merges with existing)
            importance_score: Optional new importance score

        Returns:
            Updated KnowledgeNode or None if not found
        """
        stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            logger.warning(f"Node not found: {node_id}")
            return None

        if name is not None:
            node.name = name
        if description is not None:
            node.description = description
        if embedding is not None:
            node.embedding = embedding
        if metadata is not None:
            # Merge with existing metadata
            node.extra_data = {**(node.extra_data or {}), **metadata}
        if importance_score is not None:
            node.importance_score = importance_score

        await self.db.flush()

        logger.info(f"Updated node: {node_id}")
        return node

    async def delete_node(self, node_id: UUID) -> bool:
        """
        Delete a knowledge node and all its edges and associations.

        Args:
            node_id: Node UUID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            logger.warning(f"Node not found: {node_id}")
            return False

        # Cascade delete will handle edges and associations
        await self.db.delete(node)
        await self.db.flush()

        logger.info(f"Deleted node: {node_id}")
        return True

    async def delete_edge(self, edge_id: UUID) -> bool:
        """
        Delete a knowledge edge.

        Args:
            edge_id: Edge UUID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(KnowledgeEdge).where(KnowledgeEdge.id == edge_id)
        result = await self.db.execute(stmt)
        edge = result.scalar_one_or_none()

        if not edge:
            logger.warning(f"Edge not found: {edge_id}")
            return False

        await self.db.delete(edge)
        await self.db.flush()

        logger.info(f"Deleted edge: {edge_id}")
        return True

    async def get_or_create_node(
        self,
        user_id: UUID,
        node_type: NodeType,
        name: str,
        **kwargs,
    ) -> KnowledgeNode:
        """
        Get existing node or create if it doesn't exist.

        Args:
            user_id: User identifier
            node_type: Node type
            name: Node name
            **kwargs: Additional arguments for create_node

        Returns:
            Existing or newly created KnowledgeNode
        """
        stmt = select(KnowledgeNode).where(
            KnowledgeNode.user_id == user_id,
            KnowledgeNode.node_type == node_type,
            KnowledgeNode.name == name,
        )
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()

        if node:
            return node

        return await self.create_node(
            user_id=user_id, node_type=node_type, name=name, **kwargs
        )

    async def extract_entities_from_memory(
        self,
        memory: Memory,
        openai_api_key: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Use LLM to extract entities and relationships from memory content.

        This enables automatic graph organization without manual tagging.

        Args:
            memory: Memory object to analyze
            openai_api_key: Optional OpenAI API key (uses env var if not provided)

        Returns:
            Dict with 'entities' and 'relationships' lists
        """
        # Note: This is a placeholder. In production, this would call OpenAI API.
        # For now, return empty structure to avoid API dependency in testing.

        # Example of what would be returned:
        # {
        #     "entities": [
        #         {"type": "topic", "name": "Neural Networks", "importance": 0.9},
        #         {"type": "category", "name": "Academic", "importance": 0.7}
        #     ],
        #     "relationships": [
        #         {"source": "Neural Networks", "target": "Machine Learning", "type": "subtopic_of"}
        #     ]
        # }

        logger.info(
            f"Entity extraction requested for memory {memory.id} (placeholder implementation)"
        )

        return {"entities": [], "relationships": []}

    async def auto_organize_memory(
        self,
        user_id: UUID,
        memory: Memory,
        embedding_service = None,
        openai_api_key: Optional[str] = None,
    ) -> List[KnowledgeNode]:
        """
        Automatically organize a memory into the knowledge graph.

        Extracts entities from memory content, creates nodes and edges,
        and associates the memory with relevant nodes.

        Args:
            user_id: User identifier
            memory: Memory to organize
            embedding_service: Optional service for generating embeddings
            openai_api_key: Optional OpenAI API key

        Returns:
            List of KnowledgeNodes the memory was associated with
        """
        # Extract entities and relationships
        extraction = await self.extract_entities_from_memory(memory, openai_api_key)

        created_nodes: Dict[str, KnowledgeNode] = {}

        # Create nodes for extracted entities
        for entity in extraction.get("entities", []):
            try:
                node_type = NodeType(entity["type"])
            except ValueError:
                logger.warning(f"Invalid node type: {entity['type']}, skipping")
                continue

            node = await self.get_or_create_node(
                user_id=user_id,
                node_type=node_type,
                name=entity["name"],
                importance_score=entity.get("importance", 0.5),
            )

            created_nodes[entity["name"]] = node

            # Associate memory with this node
            await self.associate_memory_with_node(
                memory_id=memory.id,
                node_id=node.id,
                relevance_score=entity.get("relevance", 1.0),
            )

        # Create edges for relationships
        for rel in extraction.get("relationships", []):
            source_node = created_nodes.get(rel["source"])
            target_node = created_nodes.get(rel["target"])

            if source_node and target_node:
                try:
                    edge_type = EdgeType(rel["type"])
                except ValueError:
                    logger.warning(f"Invalid edge type: {rel['type']}, skipping")
                    continue

                await self.create_edge(
                    user_id=user_id,
                    source_node_id=source_node.id,
                    target_node_id=target_node.id,
                    edge_type=edge_type,
                    weight=rel.get("weight", 1.0),
                )

        logger.info(
            f"Auto-organized memory {memory.id} into {len(created_nodes)} nodes"
        )

        return list(created_nodes.values())

    async def get_user_graph_summary(
        self, user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get a summary of the user's knowledge graph.

        Args:
            user_id: User identifier

        Returns:
            Dict with graph statistics
        """
        # Count nodes by type
        node_stmt = select(
            KnowledgeNode.node_type, func.count(KnowledgeNode.id)
        ).where(KnowledgeNode.user_id == user_id).group_by(KnowledgeNode.node_type)

        result = await self.db.execute(node_stmt)
        node_counts = {row[0]: row[1] for row in result.all()}

        # Count edges by type
        edge_stmt = select(
            KnowledgeEdge.edge_type, func.count(KnowledgeEdge.id)
        ).where(KnowledgeEdge.user_id == user_id).group_by(KnowledgeEdge.edge_type)

        result = await self.db.execute(edge_stmt)
        edge_counts = {row[0]: row[1] for row in result.all()}

        # Count total associations
        assoc_stmt = select(func.count(MemoryNodeAssociation.id)).join(
            Memory
        ).where(Memory.user_id == user_id)

        result = await self.db.execute(assoc_stmt)
        total_associations = result.scalar() or 0

        return {
            "total_nodes": sum(node_counts.values()),
            "nodes_by_type": node_counts,
            "total_edges": sum(edge_counts.values()),
            "edges_by_type": edge_counts,
            "total_associations": total_associations,
        }
