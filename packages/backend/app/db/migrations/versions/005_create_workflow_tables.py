"""create workflow tables for node-based planning

Revision ID: 005
Revises: 004
Create Date: 2025-11-18

Creates tables for the Node-Based Workflow Planning and Transparency feature:
- workflows: Main workflow/plan container
- workflow_nodes: Individual steps/tasks in workflows
- workflow_edges: Connections between nodes
- workflow_executions: Execution state and history

This enables:
- LLM-generated workflow plans from user queries
- Manual workflow creation and editing
- Parallel and conditional node execution
- Real-time progress tracking via SSE
- Workflow approval/modification by users
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
    """
    Create workflow tables for node-based planning system.
    """
    # Create enum types
    op.execute("""
        CREATE TYPE workflowstatus AS ENUM (
            'draft', 'pending_approval', 'approved', 'executing',
            'paused', 'completed', 'failed', 'cancelled'
        );
    """)

    op.execute("""
        CREATE TYPE nodetype AS ENUM (
            'task', 'decision', 'parallel_group', 'conditional',
            'input', 'output', 'verification'
        );
    """)

    op.execute("""
        CREATE TYPE nodestatus AS ENUM (
            'pending', 'ready', 'in_progress', 'completed',
            'failed', 'skipped', 'blocked'
        );
    """)

    op.execute("""
        CREATE TYPE edgetype AS ENUM (
            'sequential', 'parallel', 'conditional'
        );
    """)

    op.execute("""
        CREATE TYPE executionstatus AS ENUM (
            'running', 'paused', 'completed', 'failed'
        );
    """)

    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum(
            'draft', 'pending_approval', 'approved', 'executing',
            'paused', 'completed', 'failed', 'cancelled',
            name='workflowstatus'
        ), nullable=False, server_default='draft'),
        sa.Column('llm_generated', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflows_user_id', 'workflows', ['user_id'])
    op.create_index('ix_workflows_status', 'workflows', ['status'])

    # Create workflow_nodes table
    op.create_table(
        'workflow_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('node_type', sa.Enum(
            'task', 'decision', 'parallel_group', 'conditional',
            'input', 'output', 'verification',
            name='nodetype'
        ), nullable=False, server_default='task'),
        sa.Column('status', sa.Enum(
            'pending', 'ready', 'in_progress', 'completed',
            'failed', 'skipped', 'blocked',
            name='nodestatus'
        ), nullable=False, server_default='pending'),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('input_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('can_run_parallel', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('position', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_nodes_workflow_id', 'workflow_nodes', ['workflow_id'])
    op.create_index('ix_workflow_nodes_status', 'workflow_nodes', ['status'])

    # Create workflow_edges table
    op.create_table(
        'workflow_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('edge_type', sa.Enum(
            'sequential', 'parallel', 'conditional',
            name='edgetype'
        ), nullable=False, server_default='sequential'),
        sa.Column('condition', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_node_id'], ['workflow_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_node_id'], ['workflow_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_edges_workflow_id', 'workflow_edges', ['workflow_id'])

    # Create workflow_executions table
    op.create_table(
        'workflow_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum(
            'running', 'paused', 'completed', 'failed',
            name='executionstatus'
        ), nullable=False, server_default='running'),
        sa.Column('current_node_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['current_node_id'], ['workflow_nodes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_executions_workflow_id', 'workflow_executions', ['workflow_id'])
    op.create_index('ix_workflow_executions_status', 'workflow_executions', ['status'])


def downgrade() -> None:
    """
    Drop workflow tables and enum types.
    """
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index('ix_workflow_executions_status', 'workflow_executions')
    op.drop_index('ix_workflow_executions_workflow_id', 'workflow_executions')
    op.drop_table('workflow_executions')

    op.drop_index('ix_workflow_edges_workflow_id', 'workflow_edges')
    op.drop_table('workflow_edges')

    op.drop_index('ix_workflow_nodes_status', 'workflow_nodes')
    op.drop_index('ix_workflow_nodes_workflow_id', 'workflow_nodes')
    op.drop_table('workflow_nodes')

    op.drop_index('ix_workflows_status', 'workflows')
    op.drop_index('ix_workflows_user_id', 'workflows')
    op.drop_table('workflows')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS executionstatus;')
    op.execute('DROP TYPE IF EXISTS edgetype;')
    op.execute('DROP TYPE IF EXISTS nodestatus;')
    op.execute('DROP TYPE IF EXISTS nodetype;')
    op.execute('DROP TYPE IF EXISTS workflowstatus;')
