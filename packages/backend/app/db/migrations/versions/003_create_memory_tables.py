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

    # Create memory_type enum for 3-tier memory architecture
    op.execute("""
        CREATE TYPE memory_type AS ENUM ('personal', 'project', 'task');
    """)

    # Create memories table with vector embeddings
    op.create_table(
        "memories",
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
            "memory_type",
            postgresql.ENUM("personal", "project", "task", name="memory_type"),
            nullable=False,
            comment="Memory tier: personal (never pruned), project (goals), task (30-day pruning)",
        ),
        sa.Column(
            "content",
            sa.Text,
            nullable=False,
            comment="Human-readable memory content",
        ),
        # Vector column for OpenAI text-embedding-3-small (1536 dimensions)
        sa.Column(
            "embedding",
            postgresql.ARRAY(sa.Float, dimensions=1),  # Will be created as vector(1536) in raw SQL
            nullable=True,
            comment="1536-dim vector embedding from OpenAI text-embedding-3-small",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
            comment="Flexible metadata: stressor info, emotion scores, goal references, etc.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "accessed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Updated on memory retrieval for LRU tracking",
        ),
    )

    # Manually fix the embedding column type to use pgvector's vector type
    # SQLAlchemy doesn't have native Vector type support, so we use ALTER TABLE
    op.execute("""
        ALTER TABLE memories
        ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536);
    """)

    # Create standard indexes for filtering and sorting
    op.create_index("ix_memories_user_id", "memories", ["user_id"])
    op.create_index("ix_memories_memory_type", "memories", ["memory_type"])
    op.create_index("ix_memories_created_at", "memories", ["created_at"])

    # Create HNSW index for fast vector similarity search
    # Parameters optimized for 1536-dim vectors:
    #   m = 16: Max connections per layer (balance recall vs speed)
    #   ef_construction = 64: Build-time search breadth (higher = better recall, slower build)
    #   vector_cosine_ops: Cosine distance metric (1 - cosine_similarity), range [0, 2]
    # Expected performance: < 100ms p95 for 10K memories
    op.execute("""
        CREATE INDEX ix_memories_embedding ON memories
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    # Create memory_collections table for optional grouping
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

    # Create index for memory_collections
    op.create_index("ix_memory_collections_user_id", "memory_collections", ["user_id"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("ix_memory_collections_user_id", "memory_collections")
    op.drop_index("ix_memories_embedding", "memories")
    op.drop_index("ix_memories_created_at", "memories")
    op.drop_index("ix_memories_memory_type", "memories")
    op.drop_index("ix_memories_user_id", "memories")

    # Drop tables (child tables first due to foreign keys)
    op.drop_table("memory_collections")
    op.drop_table("memories")

    # Drop enum type
    op.execute("DROP TYPE memory_type;")

    # Note: We don't drop the vector extension as it may be used by other tables
