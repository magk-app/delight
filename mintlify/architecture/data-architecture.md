---
title: Data Architecture
description: Database schema, models, and data relationships
---

# Data Architecture

## Core Models

### User

Primary user account information:

```python
class User(Base):
    id: UUID  # Primary key
    clerk_user_id: str  # Authoritative user identifier from Clerk
    email: str
    display_name: Optional[str]
    timezone: str  # Default: "UTC"
    theme_preference: str  # "light" | "dark" | "system"
    created_at: datetime
    updated_at: datetime
```

### Mission

User tasks and daily activities:

```python
class Mission(Base):
    id: UUID
    user_id: UUID  # FK to User
    title: str
    description: Optional[str]
    duration_minutes: int
    essence_reward: int
    attribute_type: str  # "Growth" | "Health" | "Craft" | "Connection"
    status: str  # "pending" | "active" | "completed" | "failed"
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

### Character

AI companion personalities:

```python
class Character(Base):
    id: UUID
    name: str  # "Eliza", "Lyra", "Thorne", "Elara"
    personality_prompt: str  # System prompt for character
    attribute_focus: str  # Primary attribute this character coaches
    scenario: str  # "medieval", "sci-fi", etc.
    avatar_url: Optional[str]
```

### Character Relationship

User's relationship progress with each character:

```python
class CharacterRelationship(Base):
    id: UUID
    user_id: UUID  # FK to User
    character_id: UUID  # FK to Character
    relationship_level: int  # 0-10, affects interaction depth
    last_interaction_at: Optional[datetime]
    total_interactions: int
```

### Narrative State

User's story progression:

```python
class NarrativeState(Base):
    id: UUID
    user_id: UUID  # FK to User (1:1 relationship)
    scenario: str  # Current story scenario
    current_chapter: int
    hidden_quests: JSON  # Pre-planned quests not yet revealed
    story_progress: JSON  # Key story events, choices made
    last_narrative_update: datetime
```

### Progress

Daily progress tracking:

```python
class Progress(Base):
    id: UUID
    user_id: UUID  # FK to User
    date: date  # Unique per user per day
    dci_score: float  # 0.0-1.0, Daily Capacity Index
    missions_completed: int
    streak_days: int
    essence_earned: int
    created_at: datetime
```

## Relationships

```mermaid
erDiagram
    USER ||--o{ MISSION : has
    USER ||--o{ CHARACTER_RELATIONSHIP : has
    USER ||--|| NARRATIVE_STATE : has
    USER ||--o{ PROGRESS : tracks
    MISSION ||--o{ EVIDENCE : contains
    CHARACTER ||--o{ CHARACTER_RELATIONSHIP : referenced_by

    USER {
        uuid id PK
        string clerk_user_id UK
        string email
        string timezone
        datetime created_at
    }

    MISSION {
        uuid id PK
        uuid user_id FK
        string title
        int duration_minutes
        string status
        datetime created_at
    }

    CHARACTER_RELATIONSHIP {
        uuid id PK
        uuid user_id FK
        uuid character_id FK
        int relationship_level
    }
```

## Vector Storage (PostgreSQL pgvector)

### Tables with Vector Columns

All memory tables use PostgreSQL with pgvector extension (1536-dimensional embeddings from OpenAI `text-embedding-3-small`):

#### personal_memories

Personal context and emotional state:

```sql
CREATE TABLE personal_memories (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    content TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

CREATE INDEX ON personal_memories USING ivfflat (embedding vector_cosine_ops);
```

#### project_memories

Goal-related memories:

```sql
CREATE TABLE project_memories (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    project_name TEXT,
    content TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE
);
```

#### task_memories

Mission-specific context:

```sql
CREATE TABLE task_memories (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    mission_id UUID REFERENCES missions(id),
    content TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE
);
```

#### character_conversations

Per-character chat history with semantic search:

```sql
CREATE TABLE character_conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    character_id UUID REFERENCES characters(id),
    message TEXT,
    role TEXT,  -- "user" | "assistant"
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE
);
```

## Database Naming Conventions

- **Tables:** `snake_case`, plural (e.g., `users`, `missions`)
- **Columns:** `snake_case` (e.g., `clerk_user_id`, `created_at`)
- **Foreign Keys:** `{table}_id` (e.g., `user_id`, `character_id`)
- **Timestamps:** Always `TIMESTAMP WITH TIME ZONE`
- **UUIDs:** PostgreSQL `gen_random_uuid()` for primary keys

## Migrations

Database schema changes managed via **Alembic**:

```bash
# Create new migration
poetry run alembic revision -m "description" --autogenerate

# Apply migrations
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1
```

## Database Connection

- **Provider:** Supabase (managed PostgreSQL with pgvector pre-installed)
- **Driver:** `asyncpg` (async PostgreSQL driver)
- **Connection String:** `postgresql+asyncpg://user:password@host:5432/database`
- **ORM:** SQLAlchemy 2.0 with async support

## Performance Considerations

### Indexes

```sql
-- User queries
CREATE INDEX idx_users_clerk_id ON users(clerk_user_id);

-- Mission queries
CREATE INDEX idx_missions_user_status ON missions(user_id, status);
CREATE INDEX idx_missions_created ON missions(created_at DESC);

-- Vector similarity search
CREATE INDEX ON personal_memories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON project_memories USING ivfflat (embedding vector_cosine_ops);
```

### Query Optimization

- Use `select_related()` equivalents to minimize N+1 queries
- Paginate large result sets (missions, conversations)
- Cache frequently accessed data (character metadata, user preferences)

## Data Retention

- **Missions:** Retained indefinitely (part of user's journey)
- **Conversations:** Retained for 12 months, then archived
- **Progress records:** Retained indefinitely (historical analytics)
- **Memory embeddings:** Retained while user is active, pruned on deletion

## GDPR Compliance

Users can request:
- **Data export:** JSON export of all user data
- **Data deletion:** Complete removal of user data (CASCADE deletes)
- Clerk handles auth-related GDPR compliance
