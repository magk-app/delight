"""add performance indexes for memory system

Revision ID: 004
Revises: 003
Create Date: 2025-11-12

Adds performance indexes identified in Story 2.1 code review:
- ix_memories_accessed_at: Required for LRU memory pruning (Story 2.2)
- ix_memory_collections_collection_type: Improves collection filtering queries

These indexes optimize query performance without changing schema structure.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add performance indexes to memories and memory_collections tables.

    Both indexes are created with IF NOT EXISTS for idempotency,
    allowing safe re-runs if indexes were manually added.
    """
    # Add accessed_at index for LRU (Least Recently Used) memory pruning
    # Story 2.2 will use this to find oldest memories for deletion
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_memories_accessed_at
        ON memories(accessed_at);
    """)

    # Add collection_type index for faster collection filtering
    # Common query pattern: "Show me all 'stressor_log' collections for user"
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_memory_collections_collection_type
        ON memory_collections(collection_type);
    """)


def downgrade() -> None:
    """
    Remove performance indexes.

    Uses IF EXISTS for safe rollback even if indexes don't exist.
    """
    op.execute("DROP INDEX IF EXISTS ix_memory_collections_collection_type;")
    op.execute("DROP INDEX IF EXISTS ix_memories_accessed_at;")
