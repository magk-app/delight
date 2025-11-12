"""add display_name to users

Revision ID: 002
Revises: 001
Create Date: 2025-11-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add display_name field to users table and make email nullable."""
    # Make email nullable (was NOT NULL before)
    op.alter_column('users', 'email',
                    existing_type=sa.String(length=255),
                    nullable=True)

    # Add display_name column
    op.add_column('users', sa.Column('display_name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove display_name field and make email NOT NULL again."""
    op.drop_column('users', 'display_name')
    op.alter_column('users', 'email',
                    existing_type=sa.String(length=255),
                    nullable=False)
