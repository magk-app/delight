"""create users and preferences tables

Revision ID: 001
Revises:
Create Date: 2025-11-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension (if not already enabled)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('clerk_user_id', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create index on clerk_user_id for fast lookups
    op.create_index('ix_users_clerk_user_id', 'users', ['clerk_user_id'])

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('custom_hours', postgresql.JSONB),
        sa.Column('theme', sa.String(50), server_default='modern'),
        sa.Column('communication_preferences', postgresql.JSONB),
        sa.Column('onboarding_completed', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    # Drop tables in reverse order (child table first due to foreign key)
    op.drop_table('user_preferences')
    op.drop_index('ix_users_clerk_user_id', 'users')
    op.drop_table('users')
    # Note: We don't drop the vector extension as it may be used by other tables
