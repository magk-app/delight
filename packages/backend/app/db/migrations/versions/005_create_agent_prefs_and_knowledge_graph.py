"""create agent preferences and knowledge graph tables

Revision ID: 005
Revises: 004
Create Date: 2025-11-18

Creates tables for:
1. Agent Preferences - Customizable AI agent behavior settings
2. Knowledge Graph - Structured entity and relationship tracking

New Tables:
- agent_preferences: Memory settings, model selection, reasoning depth, safety, interaction style
- knowledge_entities: Graph nodes (people, projects, concepts, events, etc.)
- knowledge_relationships: Graph edges (relationships between entities)

All tables support vector embeddings via pgvector for semantic search.
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
    # Create enums for agent preferences (idempotent)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'model_preference') THEN
                CREATE TYPE model_preference AS ENUM ('auto', 'fast', 'balanced', 'powerful');
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reasoning_depth') THEN
                CREATE TYPE reasoning_depth AS ENUM ('quick', 'medium', 'thorough');
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interaction_style') THEN
                CREATE TYPE interaction_style AS ENUM ('concise', 'balanced', 'detailed', 'transparent');
            END IF;
        END $$;
    """)

    # Create enums for knowledge graph (idempotent)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'entity_type') THEN
                CREATE TYPE entity_type AS ENUM ('person', 'project', 'concept', 'event', 'stressor', 'habit', 'preference', 'other');
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'relationship_type') THEN
                CREATE TYPE relationship_type AS ENUM ('has', 'is_a', 'related_to', 'causes', 'requires', 'part_of', 'affects', 'located_at', 'other');
            END IF;
        END $$;
    """)

    # Check existing tables
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    # ========================================================================
    # Create agent_preferences table
    # ========================================================================
    if "agent_preferences" not in existing_tables:
        op.execute("""
            CREATE TABLE agent_preferences (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

                -- Memory Settings
                memory_recency_bias FLOAT NOT NULL DEFAULT 0.5,
                memory_similarity_threshold FLOAT NOT NULL DEFAULT 0.4,
                personal_memory_top_k INTEGER NOT NULL DEFAULT 5,
                project_memory_top_k INTEGER NOT NULL DEFAULT 10,
                task_memory_top_k INTEGER NOT NULL DEFAULT 5,
                enable_memory_grouping JSONB DEFAULT '{"by_project": true, "by_type": true}'::jsonb,

                -- Model Selection Settings
                default_model_preference model_preference NOT NULL DEFAULT 'auto',
                task_specific_models JSONB DEFAULT '{"coding": "fast", "writing": "balanced", "analysis": "powerful", "conversation": "fast"}'::jsonb,

                -- Reasoning Settings
                reasoning_depth reasoning_depth NOT NULL DEFAULT 'medium',
                max_research_cycles INTEGER NOT NULL DEFAULT 3,
                enable_multi_hop_reasoning JSONB DEFAULT '{"enabled": true, "max_hops": 5}'::jsonb,

                -- Safety Settings
                content_filter_level VARCHAR(20) NOT NULL DEFAULT 'medium',
                enable_fact_verification JSONB DEFAULT '{"enabled": false, "require_sources": false}'::jsonb,
                allowed_search_domains JSONB DEFAULT '[]'::jsonb,
                blocked_search_domains JSONB DEFAULT '[]'::jsonb,

                -- Interaction Style Settings
                interaction_style interaction_style NOT NULL DEFAULT 'balanced',
                show_planning_nodes JSONB DEFAULT '{"enabled": false, "on_request": true}'::jsonb,
                preferred_language VARCHAR(10) NOT NULL DEFAULT 'en',
                use_technical_jargon JSONB DEFAULT '{"enabled": true, "domains": []}'::jsonb,

                -- Custom Settings
                custom_settings JSONB DEFAULT '{}'::jsonb,

                -- Metadata
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            )
        """)

        # Create indexes
        op.create_index("ix_agent_preferences_user_id", "agent_preferences", ["user_id"])

        # Add comments
        op.execute("COMMENT ON TABLE agent_preferences IS 'User-specific AI agent behavior customization settings'")
        op.execute("COMMENT ON COLUMN agent_preferences.memory_recency_bias IS 'Weight for recent memories (0.0=no bias, 1.0=strong recency)'")
        op.execute("COMMENT ON COLUMN agent_preferences.default_model_preference IS 'Default model selection strategy'")
        op.execute("COMMENT ON COLUMN agent_preferences.reasoning_depth IS 'Default reasoning thoroughness'")
        op.execute("COMMENT ON COLUMN agent_preferences.content_filter_level IS 'Content filtering strictness: low, medium, high'")
        op.execute("COMMENT ON COLUMN agent_preferences.interaction_style IS 'Response verbosity and detail level'")

    else:
        print("Table 'agent_preferences' already exists, skipping creation")

    # ========================================================================
    # Create knowledge_entities table
    # ========================================================================
    if "knowledge_entities" not in existing_tables:
        op.execute("""
            CREATE TABLE knowledge_entities (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                entity_type entity_type NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                embedding vector(1536),
                properties JSONB DEFAULT '{}'::jsonb,
                confidence FLOAT NOT NULL DEFAULT 1.0,
                source_memory_id UUID REFERENCES memories(id) ON DELETE SET NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

                -- Unique constraint: one entity name per user (case-insensitive)
                CONSTRAINT uq_user_entity_name UNIQUE (user_id, name)
            )
        """)

        # Create indexes
        op.create_index("ix_knowledge_entities_user_id", "knowledge_entities", ["user_id"])
        op.create_index("ix_knowledge_entities_entity_type", "knowledge_entities", ["entity_type"])
        op.create_index("ix_knowledge_entities_name", "knowledge_entities", ["name"])
        op.create_index("ix_knowledge_entities_user_type", "knowledge_entities", ["user_id", "entity_type"])

        # Create HNSW index for vector similarity search
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_knowledge_entities_embedding ON knowledge_entities
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """)

        # Add comments
        op.execute("COMMENT ON TABLE knowledge_entities IS 'Knowledge graph entities (nodes)'")
        op.execute("COMMENT ON COLUMN knowledge_entities.entity_type IS 'Category of this entity'")
        op.execute("COMMENT ON COLUMN knowledge_entities.name IS 'Human-readable entity name'")
        op.execute("COMMENT ON COLUMN knowledge_entities.embedding IS 'Optional vector embedding for semantic entity search'")
        op.execute("COMMENT ON COLUMN knowledge_entities.properties IS 'Flexible entity attributes (deadline, progress, intensity, etc.)'")
        op.execute("COMMENT ON COLUMN knowledge_entities.confidence IS 'Confidence in entity existence/accuracy (0.0-1.0)'")
        op.execute("COMMENT ON COLUMN knowledge_entities.source_memory_id IS 'Original memory that introduced this entity'")

    else:
        print("Table 'knowledge_entities' already exists, skipping creation")

    # ========================================================================
    # Create knowledge_relationships table
    # ========================================================================
    if "knowledge_relationships" not in existing_tables:
        op.execute("""
            CREATE TABLE knowledge_relationships (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                from_entity_id UUID NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
                to_entity_id UUID NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
                relationship_type relationship_type NOT NULL,
                properties JSONB DEFAULT '{}'::jsonb,
                confidence FLOAT NOT NULL DEFAULT 1.0,
                source_memory_id UUID REFERENCES memories(id) ON DELETE SET NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

                -- Prevent duplicate relationships
                CONSTRAINT uq_relationship_triple UNIQUE (from_entity_id, to_entity_id, relationship_type)
            )
        """)

        # Create indexes
        op.create_index("ix_knowledge_relationships_user_id", "knowledge_relationships", ["user_id"])
        op.create_index("ix_knowledge_relationships_from_entity_id", "knowledge_relationships", ["from_entity_id"])
        op.create_index("ix_knowledge_relationships_to_entity_id", "knowledge_relationships", ["to_entity_id"])
        op.create_index("ix_knowledge_relationships_relationship_type", "knowledge_relationships", ["relationship_type"])
        op.create_index("ix_knowledge_relationships_from_type", "knowledge_relationships", ["from_entity_id", "relationship_type"])
        op.create_index("ix_knowledge_relationships_to_type", "knowledge_relationships", ["to_entity_id", "relationship_type"])

        # Add comments
        op.execute("COMMENT ON TABLE knowledge_relationships IS 'Knowledge graph relationships (edges)'")
        op.execute("COMMENT ON COLUMN knowledge_relationships.from_entity_id IS 'Source entity in the relationship'")
        op.execute("COMMENT ON COLUMN knowledge_relationships.to_entity_id IS 'Target entity in the relationship'")
        op.execute("COMMENT ON COLUMN knowledge_relationships.relationship_type IS 'Type of relationship between entities'")
        op.execute("COMMENT ON COLUMN knowledge_relationships.properties IS 'Relationship attributes (strength, context, metadata, etc.)'")
        op.execute("COMMENT ON COLUMN knowledge_relationships.confidence IS 'Confidence in relationship accuracy (0.0-1.0)'")
        op.execute("COMMENT ON COLUMN knowledge_relationships.source_memory_id IS 'Memory that established this relationship'")

    else:
        print("Table 'knowledge_relationships' already exists, skipping creation")


def downgrade() -> None:
    # Drop tables in reverse order (respect foreign keys)
    op.drop_table("knowledge_relationships")
    op.drop_table("knowledge_entities")
    op.drop_table("agent_preferences")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS relationship_type;")
    op.execute("DROP TYPE IF EXISTS entity_type;")
    op.execute("DROP TYPE IF EXISTS interaction_style;")
    op.execute("DROP TYPE IF EXISTS reasoning_depth;")
    op.execute("DROP TYPE IF EXISTS model_preference;")
