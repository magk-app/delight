# Memory Architecture Specification

**Date:** 2025-11-18
**Epic:** Epic 2 - Companion & Memory System
**Purpose:** Detailed design for 3-tier hierarchical memory with graph structure and vector search

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Memory Tiers](#memory-tiers)
3. [Graph Structure Design](#graph-structure-design)
4. [Database Schema](#database-schema)
5. [Vector Storage Strategy](#vector-storage-strategy)
6. [Memory Lifecycle](#memory-lifecycle)
7. [Performance Optimization](#performance-optimization)

---

## Architecture Overview

Delight's memory architecture combines **hierarchical partitioning** (Personal/Project/Task) with **graph structure** for fast, context-aware retrieval.

### Core Principles

1. **Tiered Abstraction**: Different memory tiers for different timeframes
2. **Graph Navigation**: Structured relationships enable fast routing to relevant memories
3. **Hybrid Search**: Combine metadata filtering + semantic similarity
4. **Automatic Pruning**: Task memories auto-deleted after 30 days
5. **User Control**: Users can view, edit, and delete memories

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ MEMORY ARCHITECTURE                                               │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
│ PERSONAL       │  │  PROJECT         │  │ TASK            │
│ MEMORY         │  │  MEMORY          │  │ MEMORY          │
│                │  │                  │  │                 │
│ Global context │  │ Goal-specific    │  │ Mission-specific│
│ Permanent      │  │ Project duration │  │ 30-day TTL      │
│                │  │                  │  │                 │
│ Examples:      │  │ Examples:        │  │ Examples:       │
│ - User values  │  │ - Goal: Marathon │  │ - Today's run   │
│ - Preferences  │  │ - Training plan  │  │ - Mission notes │
│ - Patterns     │  │ - Progress log   │  │ - Reflections   │
└────────────────┘  └──────────────────┘  └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼────────┐
                    │ GRAPH STRUCTURE  │
                    │ (PostgreSQL)     │
                    │                  │
                    │ Nodes:           │
                    │ - Users          │
                    │ - Goals          │
                    │ - Missions       │
                    │ - Memories       │
                    │                  │
                    │ Edges:           │
                    │ - user_goals     │
                    │ - goal_missions  │
                    │ - memory_refs    │
                    └──────────────────┘
                              │
                    ┌─────────▼────────┐
                    │ VECTOR SEARCH    │
                    │ (pgvector)       │
                    │                  │
                    │ Embeddings:      │
                    │ - 1536 dims      │
                    │ - Cosine similarity│
                    │ - HNSW index     │
                    └──────────────────┘
```

---

## Memory Tiers

### Tier 1: Personal Memory (Long-term, Global)

**Purpose**: Store user identity, preferences, and patterns that persist across all sessions and projects.

**Characteristics**:
- **Persistence**: Permanent (updated, never auto-deleted)
- **Scope**: Global (applies to all interactions)
- **Size**: Small (~50-200 entries per user)
- **Update Frequency**: Weekly consolidation + real-time for critical updates

**What Goes Here**:
- **User Identity**:
  - Name, timezone, productive hours
  - Communication preferences (tone, verbosity)
  - Values and "why" behind goals
- **Emotional Patterns**:
  - What helps when overwhelmed (breathing exercises, short missions)
  - Celebration preferences (enthusiastic vs subtle)
  - Triggers for negative emotions (deadline pressure, perfectionism)
- **Preferences**:
  - Preferred mission length (10min vs 30min)
  - Energy level patterns (morning person vs night owl)
  - Value category focus (Health, Craft, Growth, Connection)
- **Relationship Context**:
  - Relationship level with Eliza and character personas
  - Conversation style preferences
  - Topics user enjoys discussing

**Storage Format**:
```json
{
  "memory_id": "pm_001",
  "memory_type": "personal",
  "category": "emotional_pattern",
  "content": "User feels overwhelmed when presented with more than 3 tasks at once. Prefers priority triads with clear time estimates.",
  "metadata": {
    "learned_from": ["conversation_2024_11_15", "mission_session_042"],
    "confidence": 0.95,
    "last_updated": "2025-11-15T14:30:00Z"
  },
  "embedding": [0.12, -0.34, ...], // 1536-dim vector
  "tags": ["preference", "task_management", "overwhelm"]
}
```

### Tier 2: Project Memory (Medium-term, Goal-specific)

**Purpose**: Store context specific to active goals and ongoing projects.

**Characteristics**:
- **Persistence**: Duration of project (deleted when goal archived)
- **Scope**: Goal-specific (filtered by goal_id)
- **Size**: Medium (~100-500 entries per goal)
- **Update Frequency**: After each mission, weekly summaries

**What Goes Here**:
- **Goal Context**:
  - Goal decomposition (milestones, sub-goals)
  - Domain-specific knowledge (running terminology, piano techniques)
  - Resources and references (articles, videos, tools)
- **Progress Snapshots**:
  - Weekly summaries ("Completed 3 running missions, avg pace improved")
  - Milestone achievements
  - Challenges encountered and solutions
- **Strategy Insights**:
  - What's working (morning runs vs evening)
  - What's not working (30min sessions too long)
  - Adaptive adjustments (reduce mission duration)
- **Narrative State** (Epic 4 integration):
  - Current story chapter for this goal
  - Character relationships tied to this goal
  - Unlocked narrative beats

**Storage Format**:
```json
{
  "memory_id": "pm_marathon_042",
  "memory_type": "project",
  "goal_id": "goal_123",
  "content": "User completed Week 3 of marathon training. Average pace improved from 6:30/km to 6:15/km. Prefers outdoor runs to treadmill, especially morning routes through park.",
  "metadata": {
    "milestone": "week_3_complete",
    "achievement_date": "2025-11-10",
    "insights": ["morning_preference", "outdoor_preference", "pace_improvement"]
  },
  "embedding": [0.45, -0.12, ...],
  "tags": ["progress", "marathon", "running", "week_3"]
}
```

### Tier 3: Task Memory (Short-term, Mission-specific)

**Purpose**: Store immediate context for current and recent missions.

**Characteristics**:
- **Persistence**: 30 days (auto-pruned)
- **Scope**: Mission-specific (filtered by mission_id)
- **Size**: Large (~1000s of entries, pruned regularly)
- **Update Frequency**: Real-time during mission execution

**What Goes Here**:
- **Mission Details**:
  - Mission description, duration, energy level
  - Start time, completion time, actual vs estimated
- **Execution Notes**:
  - User notes during/after mission
  - Reflections and learnings
  - Evidence uploads (photo captions)
- **Emotional State**:
  - Mood before/after mission
  - Emotional state during execution (if shared)
  - Celebration or frustration expressed
- **Micro-insights**:
  - "First 5 minutes were hardest, then momentum kicked in"
  - "Music helped maintain focus"
  - "Interrupted by phone call, had to restart"

**Storage Format**:
```json
{
  "memory_id": "tm_run_042_001",
  "memory_type": "task",
  "mission_id": "mission_042",
  "goal_id": "goal_123",
  "content": "Completed 5km morning run. Started feeling tired around 3km mark but Eliza's encouragement helped push through. Felt accomplished afterward. Weather was perfect (cool, sunny).",
  "metadata": {
    "mission_status": "completed",
    "emotional_state_before": "neutral",
    "emotional_state_after": "joy",
    "duration_actual": 28,
    "duration_estimated": 30
  },
  "embedding": [0.78, -0.23, ...],
  "tags": ["run", "5km", "morning", "completed"],
  "created_at": "2025-11-18T07:00:00Z",
  "expires_at": "2025-12-18T07:00:00Z"  // 30 days from creation
}
```

---

## Graph Structure Design

### Why Graph Structure?

Traditional flat memory stores require scanning all memories for relevance. Graph structure enables **fast routing** to relevant subsets before semantic search:

1. **User asks about marathon goal** → Navigate graph to `goal_123` node → Search only project memories linked to that goal
2. **Eliza recalls recent mission** → Navigate to today's missions → Search task memories from last 24 hours
3. **Character persona interaction** → Navigate to character relationship → Search conversation history with that character

### Graph Schema

```sql
-- Core nodes
users (id, clerk_user_id, timezone, ...)
goals (id, user_id, title, status, ...)
missions (id, goal_id, user_id, status, ...)
memories (id, user_id, memory_type, content, embedding, ...)
characters (id, name, personality_prompt, ...)

-- Edges (relationships)
user_goals (user_id → goal_id)
goal_missions (goal_id → mission_id)
memory_references (memory_id → goal_id | mission_id | character_id)
character_relationships (user_id → character_id, relationship_level)
```

### Graph Navigation Examples

**Example 1: Retrieve memories for current mission**

```
User: "How do I feel about running in the morning?"

Graph traversal:
1. user_id → goals (filter: value_category = "Health")
2. goal_id → project_memories (search: "running morning")
3. goal_id → missions (filter: recent, completed)
4. mission_id → task_memories (search: "morning" + "feeling")

Result: Relevant memories from:
- Project tier: "User prefers morning runs to evening"
- Task tier: "Last 3 morning runs felt energizing"
```

**Example 2: Character-initiated interaction**

```
System: Lyra (Craft mentor) wants to reach out

Graph traversal:
1. user_id → goals (filter: value_category = "Craft")
2. goal_id → project_memories (recent activity check)
3. user_id → character_relationships (find Lyra's relationship level)
4. character_id → conversation_history (semantic search: recent topics)

Result: Lyra knows about user's craft goals and recent interactions
```

### Graph Benefits

✅ **Speed**: Narrow search space before vector similarity (10x faster)
✅ **Relevance**: Context-aware retrieval (only goal-related memories)
✅ **Scalability**: As user accumulates memories, graph prevents slowdown
✅ **Consistency**: Prevent referencing memories from wrong context (e.g., mixing up goals)

---

## Database Schema

### Tables with Vector Columns

```sql
-- Personal Memories
CREATE TABLE personal_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,  -- 'identity', 'emotional_pattern', 'preference', 'relationship'
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,  -- OpenAI text-embedding-3-small
    metadata JSONB NOT NULL DEFAULT '{}',
    tags TEXT[] NOT NULL DEFAULT '{}',
    confidence FLOAT NOT NULL DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    CONSTRAINT personal_memories_user_id_idx CHECK (user_id IS NOT NULL)
);

CREATE INDEX idx_personal_memories_user ON personal_memories(user_id);
CREATE INDEX idx_personal_memories_category ON personal_memories(category);
CREATE INDEX idx_personal_memories_embedding ON personal_memories
    USING hnsw (embedding vector_cosine_ops);  -- Fast vector search
CREATE INDEX idx_personal_memories_tags ON personal_memories USING GIN(tags);

-- Project Memories
CREATE TABLE project_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_project_memories_user ON project_memories(user_id);
CREATE INDEX idx_project_memories_goal ON project_memories(goal_id);
CREATE INDEX idx_project_memories_embedding ON project_memories
    USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_project_memories_tags ON project_memories USING GIN(tags);

-- Task Memories
CREATE TABLE task_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,  -- Auto-delete after 30 days

    CONSTRAINT task_memories_expires CHECK (expires_at > created_at)
);

CREATE INDEX idx_task_memories_user ON task_memories(user_id);
CREATE INDEX idx_task_memories_mission ON task_memories(mission_id);
CREATE INDEX idx_task_memories_goal ON task_memories(goal_id);
CREATE INDEX idx_task_memories_expires ON task_memories(expires_at);
CREATE INDEX idx_task_memories_embedding ON task_memories
    USING hnsw (embedding vector_cosine_ops);

-- Character Conversation Memories (separate namespace per character)
CREATE TABLE character_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    speaker VARCHAR(20) NOT NULL,  -- 'user' or 'character'
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_char_conv_user_char ON character_conversations(user_id, character_id);
CREATE INDEX idx_char_conv_embedding ON character_conversations
    USING hnsw (embedding vector_cosine_ops);
```

### Memory Metadata Examples

**Personal Memory Metadata**:
```json
{
  "learned_from": ["conversation_id_123", "mission_session_042"],
  "confidence": 0.95,
  "last_validated": "2025-11-15T14:30:00Z",
  "user_confirmed": true
}
```

**Project Memory Metadata**:
```json
{
  "milestone": "week_3_complete",
  "achievement_date": "2025-11-10",
  "insights": ["morning_preference", "pace_improvement"],
  "source": "mission_summary"
}
```

**Task Memory Metadata**:
```json
{
  "mission_status": "completed",
  "emotional_state_before": "neutral",
  "emotional_state_after": "joy",
  "duration_actual": 28,
  "duration_estimated": 30,
  "interruptions": 0
}
```

---

## Vector Storage Strategy

### Embedding Generation

Use **OpenAI text-embedding-3-small** for consistency and cost-effectiveness:

```python
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_embedding(text: str) -> list[float]:
    """Generate 1536-dim embedding for text."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

**Cost**: $0.02 per 1M tokens (very cheap for memory storage)

### Vector Search with pgvector

```python
from sqlalchemy import select, func

async def search_memories_vector(
    db: AsyncSession,
    user_id: str,
    query_embedding: list[float],
    memory_type: str,
    limit: int = 10
) -> list[PersonalMemory]:
    """Search memories using vector similarity."""

    # Cosine similarity search
    stmt = select(PersonalMemory).where(
        PersonalMemory.user_id == user_id,
        PersonalMemory.memory_type == memory_type
    ).order_by(
        PersonalMemory.embedding.cosine_distance(query_embedding)
    ).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()
```

### Hybrid Search (Metadata + Vector)

Combine metadata filtering with semantic search for best results:

```python
async def hybrid_search(
    db: AsyncSession,
    user_id: str,
    query: str,
    goal_id: str = None,
    tags: list[str] = None,
    limit: int = 10
) -> list[ProjectMemory]:
    """Hybrid search: metadata filters + vector similarity."""

    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Build query with filters
    stmt = select(ProjectMemory).where(
        ProjectMemory.user_id == user_id
    )

    # Filter by goal if specified (graph routing)
    if goal_id:
        stmt = stmt.where(ProjectMemory.goal_id == goal_id)

    # Filter by tags if specified
    if tags:
        stmt = stmt.where(ProjectMemory.tags.overlap(tags))

    # Order by vector similarity
    stmt = stmt.order_by(
        ProjectMemory.embedding.cosine_distance(query_embedding)
    ).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()
```

---

## Memory Lifecycle

### 1. Memory Creation

**Trigger**: After conversation, mission completion, or user action

```python
async def create_memory(
    db: AsyncSession,
    user_id: str,
    content: str,
    memory_type: str,
    metadata: dict = {},
    tags: list[str] = []
) -> PersonalMemory:
    """Create a new memory with embedding."""

    # Generate embedding
    embedding = generate_embedding(content)

    # Create memory record
    memory = PersonalMemory(
        user_id=user_id,
        category=metadata.get('category', 'general'),
        content=content,
        embedding=embedding,
        metadata=metadata,
        tags=tags
    )

    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    return memory
```

### 2. Memory Retrieval

**Trigger**: User query, AI reasoning, context gathering

```python
async def retrieve_relevant_memories(
    db: AsyncSession,
    user_id: str,
    query: str,
    context: dict = {}
) -> dict:
    """Retrieve relevant memories from all tiers."""

    query_embedding = generate_embedding(query)

    # Personal tier (always included)
    personal = await search_memories_vector(
        db, user_id, query_embedding, "personal", limit=5
    )

    # Project tier (if goal context provided)
    project = []
    if context.get('goal_id'):
        project = await hybrid_search(
            db, user_id, query, goal_id=context['goal_id'], limit=10
        )

    # Task tier (recent missions)
    task = await search_recent_task_memories(
        db, user_id, query_embedding, days=7, limit=10
    )

    return {
        "personal": personal,
        "project": project,
        "task": task
    }
```

### 3. Memory Update

**Trigger**: User correction, new insights, confidence adjustment

```python
async def update_memory_confidence(
    db: AsyncSession,
    memory_id: str,
    new_confidence: float,
    validation_source: str
) -> PersonalMemory:
    """Update memory confidence based on validation."""

    memory = await db.get(PersonalMemory, memory_id)
    memory.confidence = new_confidence
    memory.metadata['last_validated'] = datetime.now().isoformat()
    memory.metadata['validated_by'] = validation_source
    memory.updated_at = datetime.now()

    await db.commit()
    return memory
```

### 4. Memory Consolidation

**Trigger**: Weekly background job (ARQ worker)

```python
async def consolidate_task_memories(
    db: AsyncSession,
    user_id: str,
    goal_id: str
) -> ProjectMemory:
    """Consolidate task memories into project summary."""

    # Get all task memories for goal from past week
    task_memories = await get_task_memories(
        db, user_id, goal_id, days=7
    )

    # Use LLM to summarize insights
    summary = await summarize_memories_with_llm(task_memories)

    # Create project memory
    project_memory = await create_memory(
        db,
        user_id=user_id,
        content=summary,
        memory_type="project",
        metadata={
            "goal_id": goal_id,
            "source": "task_consolidation",
            "week": get_current_week()
        },
        tags=["weekly_summary", "consolidated"]
    )

    return project_memory
```

### 5. Memory Pruning

**Trigger**: Daily background job (ARQ worker)

```python
async def prune_expired_task_memories(db: AsyncSession):
    """Delete task memories older than 30 days."""

    cutoff_date = datetime.now() - timedelta(days=30)

    stmt = delete(TaskMemory).where(
        TaskMemory.expires_at < cutoff_date
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount  # Number of deleted memories
```

---

## Performance Optimization

### 1. Indexing Strategy

- **HNSW index** on embedding columns (fast approximate nearest neighbor)
- **B-tree indexes** on user_id, goal_id, mission_id (fast filtering)
- **GIN indexes** on tags arrays (fast tag filtering)
- **Partial index** on expires_at for active task memories only

```sql
-- Fast vector search
CREATE INDEX idx_personal_memories_embedding ON personal_memories
    USING hnsw (embedding vector_cosine_ops);

-- Fast expiration checks
CREATE INDEX idx_task_memories_active ON task_memories(expires_at)
    WHERE expires_at > NOW();
```

### 2. Query Optimization

- **Graph routing first**: Filter by goal_id/mission_id before vector search
- **Limit results**: Top 10-20 memories per tier (avoid overload)
- **Time windows**: Search recent memories first (recency bias)
- **Batched embeddings**: Generate embeddings in batches when possible

### 3. Caching Strategy

- **Redis cache** for frequently accessed memories (user preferences, current goal context)
- **TTL**: 15 minutes for personal memories, 5 minutes for project/task
- **Cache invalidation**: On memory updates

```python
from redis import asyncio as aioredis

async def get_cached_memories(
    cache: aioredis.Redis,
    user_id: str,
    cache_key: str
) -> list | None:
    """Get memories from cache if available."""

    key = f"memories:{user_id}:{cache_key}"
    cached = await cache.get(key)

    if cached:
        return json.loads(cached)
    return None

async def cache_memories(
    cache: aioredis.Redis,
    user_id: str,
    cache_key: str,
    memories: list,
    ttl: int = 900  # 15 minutes
):
    """Cache memories for faster retrieval."""

    key = f"memories:{user_id}:{cache_key}"
    await cache.setex(key, ttl, json.dumps(memories))
```

### 4. Cost Optimization

- **Embedding reuse**: Store embeddings, don't regenerate
- **Batched operations**: Consolidate multiple memory writes
- **Pruning automation**: Remove expired task memories to save storage
- **Selective retrieval**: Only search tiers relevant to current context

**Cost Estimate**:
- Embedding generation: $0.02 per 1M tokens
- Average memory: ~100 tokens
- Daily memories per user: ~10
- Cost per user: ~$0.0002/day (negligible)

---

## Summary

Delight's hierarchical memory architecture provides:

✅ **Tiered abstraction** for different timeframes (Personal/Project/Task)
✅ **Graph structure** for fast, context-aware retrieval
✅ **Hybrid search** combining metadata + semantic similarity
✅ **Automatic lifecycle** management (creation, consolidation, pruning)
✅ **Performance optimization** through indexing and caching
✅ **Cost efficiency** within $0.50/user/day budget

**Next**: Read `03-STATE-MANAGEMENT.md` for goal-driven state transitions and tool orchestration.

---

**Last Updated**: 2025-11-18
**Status**: Design Specification
**Maintainer**: Jack & Delight Team
