"""create memory tables with pgvector support

Revision ID: 003
Revises: 002
Create Date: 2025-11-12

Memory system for AI companion with 3-tier architecture:
- Personal: Identity, preferences, emotional patterns (never pruned)
- Project: Goals, plans, progress (medium-term)
- Task: Mission context, conversations (pruned after 30 days)

Uses pgvector extension for semantic similarity search with HNSW indexing.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector extension already enabled in migration 001
    # Verify it's available (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create memory_type enum for 3-tier memory architecture (idempotent)
    # Check if enum exists before creating to handle re-runs
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'memory_type') THEN
                CREATE TYPE memory_type AS ENUM ('personal', 'project', 'task');
            END IF;
        END $$;
    """)

    # Check if tables already exist (in case of partial migration failure)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create memories table with vector embeddings (if not exists)
    # Using raw SQL to bypass SQLAlchemy's ENUM event handler which tries to
    # auto-create the enum even with create_type=False
    # NOTE: Split into separate op.execute() calls because asyncpg doesn't support
    # multiple statements in a single prepared statement
    if "memories" not in existing_tables:
        # Create the table
        op.execute("""
            CREATE TABLE memories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                memory_type memory_type NOT NULL,
                content TEXT NOT NULL,
                embedding vector(1536),
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            )
        """)
        
        # Add column comments (separate statements for asyncpg compatibility)
        op.execute("COMMENT ON COLUMN memories.memory_type IS 'Memory tier: personal (never pruned), project (goals), task (30-day pruning)'")
        op.execute("COMMENT ON COLUMN memories.content IS 'Human-readable memory content'")
        op.execute("COMMENT ON COLUMN memories.embedding IS '1536-dim vector embedding from OpenAI text-embedding-3-small'")
        op.execute("COMMENT ON COLUMN memories.metadata IS 'Flexible metadata: stressor info, emotion scores, goal references, etc.'")
        op.execute("COMMENT ON COLUMN memories.accessed_at IS 'Updated on memory retrieval for LRU tracking'")

        # Create standard indexes for filtering and sorting
        op.create_index("ix_memories_user_id", "memories", ["user_id"])
        op.create_index("ix_memories_memory_type", "memories", ["memory_type"])
        op.create_index("ix_memories_created_at", "memories", ["created_at"])
        op.create_index("ix_memories_accessed_at", "memories", ["accessed_at"])  # For LRU pruning

        # Create HNSW index for fast vector similarity search
        # Parameters optimized for 1536-dim vectors:
        #   m = 16: Max connections per layer (balance recall vs speed)
        #   ef_construction = 64: Build-time search breadth (higher = better recall, slower build)
        #   vector_cosine_ops: Cosine distance metric (1 - cosine_similarity), range [0, 2]
        # Expected performance: < 100ms p95 for 10K memories
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_memories_embedding ON memories
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """)
    else:
        print("Table 'memories' already exists, skipping creation")

    # Create memory_collections table for optional grouping (if not exists)
    if "memory_collections" not in existing_tables:
        op.create_table(
            "memory_collections",
            sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "collection_type",
            sa.String(50),
            nullable=False,
            comment="Collection category: goal, stressor_log, preferences, etc.",
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
            comment="Human-readable collection name",
        ),
        sa.Column(
            "description",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        )

        # Create indexes for memory_collections
        op.create_index("ix_memory_collections_user_id", "memory_collections", ["user_id"])
        op.create_index("ix_memory_collections_collection_type", "memory_collections", ["collection_type"])
    else:
        print("Table 'memory_collections' already exists, skipping creation")


def downgrade() -> None:
    # Drop indexes first (using IF EXISTS to handle cases where indexes don't exist)
    # This makes the downgrade idempotent and safe to run even if upgrade was partial
    op.execute("DROP INDEX IF EXISTS ix_memory_collections_collection_type;")
    op.execute("DROP INDEX IF EXISTS ix_memory_collections_user_id;")
    op.execute("DROP INDEX IF EXISTS ix_memories_embedding;")
    op.execute("DROP INDEX IF EXISTS ix_memories_accessed_at;")
    op.execute("DROP INDEX IF EXISTS ix_memories_created_at;")
    op.execute("DROP INDEX IF EXISTS ix_memories_memory_type;")
    op.execute("DROP INDEX IF EXISTS ix_memories_user_id;")

    # Drop tables (child tables first due to foreign keys)
    # Check if tables exist before dropping to handle partial migrations
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if "memory_collections" in existing_tables:
        op.drop_table("memory_collections")
    if "memories" in existing_tables:
        op.drop_table("memories")

    # Drop enum type (using IF EXISTS for safety)
    op.execute("DROP TYPE IF EXISTS memory_type;")

    # Note: We don't drop the vector extension as it may be used by other tables
