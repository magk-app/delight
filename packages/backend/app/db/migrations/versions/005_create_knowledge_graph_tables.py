"""create knowledge graph tables for hierarchical memory retrieval

Revision ID: 005
Revises: 004
Create Date: 2025-11-18

Implements graph-based hierarchical retrieval for fast context-aware memory access:
- KnowledgeNode: Concepts, topics, projects, people, categories that organize memories
- KnowledgeEdge: Relationships between nodes (subtopic_of, related_to, part_of, etc.)
- MemoryNodeAssociation: Links memories to graph nodes for hierarchical organization

Two-step retrieval strategy:
1. Find relevant nodes (fast, using name/metadata/embeddings)
2. Search memories within those nodes (precise, reduced search space by 10-100x)

Uses pgvector for semantic node search, enabling concept-level matching before
drilling down to specific memories.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector extension already enabled in migration 001
    # Verify it's available (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Enable pg_trgm extension for text similarity search (used in graph_retrieval_service)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # Create node_type enum (idempotent)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'node_type') THEN
                CREATE TYPE node_type AS ENUM ('topic', 'project', 'person', 'category', 'event');
            END IF;
        END $$;
    """)

    # Create edge_type enum (idempotent)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'edge_type') THEN
                CREATE TYPE edge_type AS ENUM ('subtopic_of', 'related_to', 'part_of', 'depends_on', 'precedes');
            END IF;
        END $$;
    """)

    # Check if tables already exist (in case of partial migration failure)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create knowledge_nodes table (if not exists)
    if "knowledge_nodes" not in existing_tables:
        op.execute("""
            CREATE TABLE knowledge_nodes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                node_type node_type NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                embedding vector(1536),
                metadata JSONB DEFAULT '{}'::jsonb,
                importance_score REAL NOT NULL DEFAULT 0.5,
                access_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            )
        """)

        # Add column comments
        op.execute("COMMENT ON COLUMN knowledge_nodes.node_type IS 'Node category: topic, project, person, category, event'")
        op.execute("COMMENT ON COLUMN knowledge_nodes.name IS 'Human-readable node name (e.g., Machine Learning, Professor Smith)'")
        op.execute("COMMENT ON COLUMN knowledge_nodes.embedding IS '1536-dim vector embedding for semantic node search'")
        op.execute("COMMENT ON COLUMN knowledge_nodes.metadata IS 'Flexible metadata: status, deadline, priority, field, etc.'")
        op.execute("COMMENT ON COLUMN knowledge_nodes.importance_score IS 'Node importance (0-1) for ranking, updated based on access patterns'")
        op.execute("COMMENT ON COLUMN knowledge_nodes.access_count IS 'Number of times this node has been accessed (for popularity tracking)'")

        # Create indexes for knowledge_nodes
        op.create_index("ix_knowledge_nodes_user_id", "knowledge_nodes", ["user_id"])
        op.create_index("ix_knowledge_nodes_node_type", "knowledge_nodes", ["node_type"])
        op.create_index("ix_knowledge_nodes_name", "knowledge_nodes", ["name"])
        op.create_index("ix_knowledge_nodes_importance_score", "knowledge_nodes", ["importance_score"])

        # Create HNSW index for semantic node search
        # Same parameters as memory embeddings (m=16, ef_construction=64)
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_knowledge_nodes_embedding ON knowledge_nodes
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """)
    else:
        print("Table 'knowledge_nodes' already exists, skipping creation")

    # Create knowledge_edges table (if not exists)
    if "knowledge_edges" not in existing_tables:
        op.execute("""
            CREATE TABLE knowledge_edges (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                source_node_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
                target_node_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
                edge_type edge_type NOT NULL,
                weight REAL NOT NULL DEFAULT 1.0,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                CONSTRAINT uq_knowledge_edges_source_target_type UNIQUE (source_node_id, target_node_id, edge_type)
            )
        """)

        # Add column comments
        op.execute("COMMENT ON COLUMN knowledge_edges.edge_type IS 'Relationship type: subtopic_of, related_to, part_of, depends_on, precedes'")
        op.execute("COMMENT ON COLUMN knowledge_edges.weight IS 'Relationship strength (0-1), used for ranking during graph traversal'")
        op.execute("COMMENT ON COLUMN knowledge_edges.metadata IS 'Flexible metadata: discovery method, confidence, temporal distance, etc.'")

        # Create indexes for knowledge_edges
        op.create_index("ix_knowledge_edges_user_id", "knowledge_edges", ["user_id"])
        op.create_index("ix_knowledge_edges_source_node_id", "knowledge_edges", ["source_node_id"])
        op.create_index("ix_knowledge_edges_target_node_id", "knowledge_edges", ["target_node_id"])
        op.create_index("ix_knowledge_edges_edge_type", "knowledge_edges", ["edge_type"])
    else:
        print("Table 'knowledge_edges' already exists, skipping creation")

    # Create memory_node_associations table (if not exists)
    if "memory_node_associations" not in existing_tables:
        op.execute("""
            CREATE TABLE memory_node_associations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                memory_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
                node_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
                relevance_score REAL NOT NULL DEFAULT 1.0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                CONSTRAINT uq_memory_node_assoc_memory_node UNIQUE (memory_id, node_id)
            )
        """)

        # Add column comments
        op.execute("COMMENT ON COLUMN memory_node_associations.relevance_score IS 'How relevant this memory is to the node (0-1), used for ranking'")

        # Create indexes for memory_node_associations
        op.create_index("ix_memory_node_assoc_memory_id", "memory_node_associations", ["memory_id"])
        op.create_index("ix_memory_node_assoc_node_id", "memory_node_associations", ["node_id"])
    else:
        print("Table 'memory_node_associations' already exists, skipping creation")


def downgrade() -> None:
    # Drop indexes first (using IF EXISTS to handle cases where indexes don't exist)
    # This makes the downgrade idempotent and safe to run even if upgrade was partial

    # memory_node_associations indexes
    op.execute("DROP INDEX IF EXISTS ix_memory_node_assoc_node_id;")
    op.execute("DROP INDEX IF EXISTS ix_memory_node_assoc_memory_id;")

    # knowledge_edges indexes
    op.execute("DROP INDEX IF EXISTS ix_knowledge_edges_edge_type;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_edges_target_node_id;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_edges_source_node_id;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_edges_user_id;")

    # knowledge_nodes indexes
    op.execute("DROP INDEX IF EXISTS ix_knowledge_nodes_embedding;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_nodes_importance_score;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_nodes_name;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_nodes_node_type;")
    op.execute("DROP INDEX IF EXISTS ix_knowledge_nodes_user_id;")

    # Drop tables (child tables first due to foreign keys)
    # Check if tables exist before dropping to handle partial migrations
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    # Drop association table first (has FKs to both memories and knowledge_nodes)
    if "memory_node_associations" in existing_tables:
        op.drop_table("memory_node_associations")

    # Drop edges table (has FKs to knowledge_nodes)
    if "knowledge_edges" in existing_tables:
        op.drop_table("knowledge_edges")

    # Drop nodes table last (referenced by edges and associations)
    if "knowledge_nodes" in existing_tables:
        op.drop_table("knowledge_nodes")

    # Drop enum types (using IF EXISTS for safety)
    op.execute("DROP TYPE IF EXISTS edge_type;")
    op.execute("DROP TYPE IF EXISTS node_type;")

    # Note: We don't drop the vector extension as it may be used by other tables
