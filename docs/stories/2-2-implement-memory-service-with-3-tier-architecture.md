# Story 2.2: Implement Memory Service with 3-Tier Architecture

**Story ID:** 2.2
**Epic:** 2 - Companion & Memory System
**Status:** drafted
**Priority:** P0 (Core Memory Foundation)
**Estimated Effort:** 12-16 hours (increased due to comprehensive requirements: goal-based search, case study testing, productivity structure, user priority system)
**Assignee:** Claude Dev Agent
**Created:** 2025-11-12
**Updated:** 2025-11-12 (Comprehensive update with user requirements)

---

## User Story

**As a** developer,
**I want** a memory service that manages personal, project, and task memories with automatic embedding generation and hybrid search,
**So that** the AI companion can recall relevant context at the right abstraction level.

---

## Context

### Problem Statement

The Companion & Memory System (Epic 2) requires intelligent memory management to enable Eliza's contextual, empathetic conversations. Story 2.1 established the database foundation (pgvector tables, HNSW indexes), but we now need a service layer that:

1. **Automatically generates embeddings** when memories are created (using OpenAI text-embedding-3-small)
2. **Implements hybrid search** combining semantic similarity, time-weighted recency, and access frequency
3. **Manages 3-tier memory architecture** with strategic querying by type
4. **Prunes old task memories** automatically after 30 days via background worker

This story builds the `MemoryService` that bridges the database layer (Story 2.1) and the Eliza agent (Story 2.3), enabling memory-aware AI conversations.

### Why This Approach?

**From Architecture (ADR-004): Hybrid Search Strategy**

We implement hybrid search (vector similarity + time decay + access frequency) instead of pure vector search because:

- ✅ **Recency Matters**: Recent memories are more relevant than old ones, even if similarity is slightly lower
- ✅ **Access Patterns**: Frequently accessed memories indicate importance (user references them often)
- ✅ **Balanced Retrieval**: Combines semantic understanding (vector) with behavioral signals (time/frequency)
- ✅ **Production-Proven**: Similar approach used in LangChain's `PostgresVectorStore` with time-weighted retrieval

**From Tech Spec (tech-spec-epic-2.md lines 460-488):**

The hybrid search algorithm uses:

- **Base Score**: Cosine similarity from vector search (range 0-1, where 1 = identical)
- **Time Boost**: `1 + log(1 + days_since_access + 1)^-1` (recent memories boosted)
- **Frequency Boost**: `1 + (log(access_count) * 0.1)` (frequently accessed memories boosted)
- **Final Score**: `similarity * time_boost * frequency_boost`

### Dependencies

- **Prerequisite Stories:**

  - 2.1 (PostgreSQL pgvector and Memory Schema) ✅ Complete
  - Database tables (`memories`, `memory_collections`) exist
  - HNSW index created and functional
  - OpenAI API key configured (`OPENAI_API_KEY` environment variable)

- **Epic 2 Context:** This story **enables**:

  - Story 2.3: Eliza Agent uses `MemoryService` for context retrieval
  - Story 2.4: Chat API stores conversation exchanges via `MemoryService`
  - Story 2.6: Emotion detection stores emotional state in memory metadata

- **External Dependencies:**
  - OpenAI API access (for embedding generation)
  - ARQ worker infrastructure (for background pruning job)
  - Redis connection (for ARQ job queue)

### Technical Background from Epic 2 Design Documents

**From "How Eliza Should Respond" (docs/epic-2/):**

The memory service must support:

1. **Stressor Log (Principle 1)**: Store distinct stressors with emotion metadata

   - Example: `{stressor: true, emotion: 'fear', category: 'academic', content: 'Class registration stress'}`
   - Stored as **personal** memory type (never pruned)

2. **3-Tier Strategic Querying**: Agent queries memories by type based on context

   - **Personal tier**: Always queried (top 5) for user identity/preferences
   - **Project tier**: Queried when user discusses goals (keyword detection)
   - **Task tier**: Queried for recent action context (last 3-5 memories)

3. **Time-Weighted Relevance**: Recent memories prioritized even if similarity is lower
   - Enables Eliza to reference "what we talked about yesterday" vs "what we talked about last month"

**From Tech Spec (tech-spec-epic-2.md lines 140-152):**

Complete service design with:

- `MemoryService` class with `add_memory()`, `query_memories()`, `prune_old_task_memories()` methods
- `EmbeddingService` wrapper for OpenAI API calls with caching
- Background worker (`MemoryPruner`) scheduled daily at 2:00 AM
- Hybrid search implementation with configurable thresholds

**From Implementation Guide (docs/epic-2/2-1-to-2-5-implementation-guide.md lines 204-350):**

Step-by-step implementation guidance:

- Service structure with async/await patterns
- Embedding generation with error handling
- Vector similarity query using pgvector operators
- Time decay and frequency boost calculations
- ARQ worker setup for pruning

---

## Acceptance Criteria

### AC1: Memory Service Can Add Memories with Automatic Embedding Generation

**Given** the memory tables exist (Story 2.1) and OpenAI API key is configured
**When** I call `memory_service.add_memory(user_id, memory_type, content, metadata)`
**Then** a memory record is created with:

- Content stored in `memories.content`
- Embedding generated automatically (1536 dimensions) and stored in `memories.embedding`
- Metadata stored in `memories.metadata` JSONB column
- `created_at` and `accessed_at` timestamps set
- Memory returned with UUID

**Verification Steps:**

```python
from app.services.memory_service import MemoryService
from app.models.memory import MemoryType
from app.db.session import get_db

async with get_db() as db:
    service = MemoryService(db)
    memory = await service.add_memory(
        user_id=user_id,
        memory_type=MemoryType.PERSONAL,
        content="I prefer working in the morning",
        metadata={"source": "preferences"}
    )

    assert memory.id is not None
    assert memory.embedding is not None
    assert len(memory.embedding) == 1536
    assert memory.metadata == {"source": "preferences"}
```

### AC2: Memory Service Can Query Memories by Type (3-Tier Architecture)

**Given** memories exist across all three tiers (personal, project, task)
**When** I call `memory_service.query_memories(user_id, query_text, memory_types=[MemoryType.PERSONAL])`
**Then** only memories of the specified type(s) are returned

**And** when I query without `memory_types` filter, all types are searched

**Verification Steps:**

```python
# Create test memories
await service.add_memory(user_id, MemoryType.PERSONAL, "I love coffee", {})
await service.add_memory(user_id, MemoryType.PROJECT, "Goal: Graduate early", {})
await service.add_memory(user_id, MemoryType.TASK, "Completed walk mission", {})

# Query personal only
personal = await service.query_memories(
    user_id, "coffee preferences", memory_types=[MemoryType.PERSONAL]
)
assert all(m.memory_type == MemoryType.PERSONAL for m in personal)

# Query all types
all_memories = await service.query_memories(user_id, "recent activities")
assert len(all_memories) > 0
```

### AC3: Memory Service Implements Hybrid Search (Semantic + Time + Frequency)

**Given** memories exist with varying recency and access patterns
**When** I query memories with `query_memories()`
**Then** results are scored using hybrid algorithm:

- Base similarity score from vector cosine distance
- Time boost applied: `1 + log(1 + days_since_access + 1)^-1`
- Frequency boost applied: `1 + (log(access_count) * 0.1)`
- Final score: `similarity * time_boost * frequency_boost`
- Results sorted by final score (descending)

**And** memories below `similarity_threshold` (default 0.7) are filtered out

**Verification Steps:**

```python
# Create memories with different access times
old_memory = await service.add_memory(user_id, MemoryType.PERSONAL, "Old preference", {})
# Simulate old access: set accessed_at to 30 days ago
old_memory.accessed_at = datetime.now() - timedelta(days=30)
await db.commit()

recent_memory = await service.add_memory(user_id, MemoryType.PERSONAL, "Recent preference", {})
# Recent memory has accessed_at = now (default)

# Query should prioritize recent memory even if similarity is slightly lower
results = await service.query_memories(user_id, "preferences")
assert results[0].id == recent_memory.id  # Recent memory ranked higher
```

### AC4: Memory Service Updates Access Tracking on Query

**Given** memories are queried via `query_memories()`
**When** memories are retrieved
**Then** `accessed_at` timestamp is updated to current time

**And** `access_count` in metadata is incremented (or initialized to 1 if missing)

**Verification Steps:**

```python
memory = await service.add_memory(user_id, MemoryType.PERSONAL, "Test memory", {})
original_accessed = memory.accessed_at

# Wait 1 second, then query
await asyncio.sleep(1)
results = await service.query_memories(user_id, "test", memory_types=[MemoryType.PERSONAL])

# Refresh memory from DB
await db.refresh(memory)
assert memory.accessed_at > original_accessed
assert memory.metadata.get("access_count", 0) >= 1
```

### AC5: Memory Service Can Prune Old Task Memories (30-Day Retention)

**Given** task memories exist older than 30 days
**When** I call `memory_service.prune_old_task_memories()`
**Then** all task memories with `created_at < (NOW() - INTERVAL '30 days')` are deleted

**And** personal and project memories are never pruned (regardless of age)

**And** the method returns the count of deleted memories

**Verification Steps:**

```python
# Create old task memory (31 days ago)
old_task = await service.add_memory(user_id, MemoryType.TASK, "Old task", {})
old_task.created_at = datetime.now() - timedelta(days=31)
await db.commit()

# Create old personal memory (should NOT be pruned)
old_personal = await service.add_memory(user_id, MemoryType.PERSONAL, "Old personal", {})
old_personal.created_at = datetime.now() - timedelta(days=31)
await db.commit()

# Prune
deleted_count = await service.prune_old_task_memories()
assert deleted_count == 1

# Verify task memory deleted, personal memory retained
task_exists = await db.get(Memory, old_task.id)
personal_exists = await db.get(Memory, old_personal.id)
assert task_exists is None
assert personal_exists is not None
```

### AC6: Embedding Service Handles Errors Gracefully

**Given** OpenAI API is unavailable or returns an error
**When** I call `add_memory()` with content
**Then** the service handles the error gracefully:

- Retries with exponential backoff (3 attempts)
- If all retries fail, stores memory without embedding (embedding = NULL)
- Logs error with context (user_id, content preview)
- Does not raise exception (allows conversation to continue)

**Verification Steps:**

```python
# Mock OpenAI API to raise exception
with patch('app.services.memory_service.AsyncOpenAI') as mock_openai:
    mock_openai.return_value.embeddings.create.side_effect = Exception("API Error")

    # Should not raise exception
    memory = await service.add_memory(user_id, MemoryType.PERSONAL, "Test", {})
    assert memory.embedding is None  # Stored without embedding
    assert memory.content == "Test"  # Content still stored
```

### AC7: Background Worker Prunes Task Memories Daily

**Given** ARQ worker infrastructure is configured
**When** the scheduled job runs (daily at 2:00 AM)
**Then** `prune_old_task_memories()` is called automatically

**And** the job logs the number of pruned memories

**And** job failures are retried (3 attempts with exponential backoff)

**Verification Steps:**

```python
# In app/workers/memory_pruner.py
from arq import cron

class WorkerSettings:
    cron_jobs = [
        cron(memory_pruner.prune_task_memories_job, hour=2, minute=0),  # 2:00 AM daily
    ]

# Test job execution
async def test_prune_job(ctx):
    result = await memory_pruner.prune_task_memories_job(ctx)
    assert isinstance(result, int)  # Returns count of pruned memories
```

### AC8: Memory Service Supports Metadata for Stressor Logging

**Given** I want to store a stressor with emotion metadata
**When** I call `add_memory()` with stressor metadata
**Then** metadata is stored correctly in JSONB format

**And** the memory can be queried and filtered by metadata fields

**Verification Steps:**

```python
# Store stressor (from "How Eliza Should Respond" case study)
stressor_memory = await service.add_memory(
    user_id=user_id,
    memory_type=MemoryType.PERSONAL,
    content="Class registration stress and debt email anxiety",
    metadata={
        "stressor": True,
        "emotion": "fear",
        "category": "academic",
        "intensity": 0.8
    }
)

# Query stressors
results = await service.query_memories(user_id, "stressors")
# Filter by metadata in application code
stressors = [m for m in results if m.metadata.get("stressor") == True]
assert len(stressors) > 0
```

### AC9: Goal-Based Memory Search When User Discusses Goals

**Given** project memories exist linked to goals and user mentions goals in conversation
**When** I call `query_memories()` with goal-related query text
**Then** the service searches through project memories specifically

**And** when query contains goal-related keywords (e.g., "goal", "plan", "objective", "target"), project tier memories are prioritized

**And** goal-linked memories can be filtered by `goal_id` in metadata

**Verification Steps:**

```python
# Create project memory linked to goal
goal_memory = await service.add_memory(
    user_id=user_id,
    memory_type=MemoryType.PROJECT,
    content="Goal: Graduate early from Georgia Tech",
    metadata={"goal_id": "uuid-123", "category": "academic"}
)

# Query with goal-related text
results = await service.query_memories(
    user_id,
    "I want to work on my goals",
    memory_types=[MemoryType.PROJECT]  # Explicitly search project tier
)
assert len(results) > 0
assert any(m.metadata.get("goal_id") for m in results)
```

### AC10: Comprehensive Case Study Testing with Real User Scenarios

**Given** memories are created from real user conversations (case study scenarios)
**When** I query memories with different emotional prompts
**Then** the service retrieves relevant memories correctly for each scenario

**Test Scenarios (User Case Study):**

1. **Overwhelm Scenario**: "I'm recently overwhelmed with my schoolwork because I have to catch up"

   - Should retrieve: schoolwork-related memories, stressor memories, academic category memories
   - Verify: Memories about catching up, academic stress, overwhelm patterns

2. **Family Issues Scenario**: "I have my family issue where I have to choose sides with dad and mom. But I don't think it's a big issue because it's not something I'm prioritizing"

   - Should retrieve: Family-related memories, relationship memories, priority context
   - Verify: Non-priority stressors are stored but not over-weighted

3. **Love Interest Scenario**: "I really like this girl, it's just regarding love"

   - Should retrieve: Relationship memories, emotional memories, personal preferences
   - Verify: Love/romance category memories, emotional state tracking

4. **Isolation/Loneliness Scenario**: "I feel isolated and lonely"
   - Should retrieve: Emotional state memories, social context memories, support needs
   - Verify: Isolation patterns, loneliness indicators, emotional support context

**Verification Steps:**

```python
# Create case study memories
await service.add_memory(user_id, MemoryType.PERSONAL,
    "I'm overwhelmed with schoolwork, need to catch up",
    {"stressor": True, "emotion": "overwhelm", "category": "academic"})

await service.add_memory(user_id, MemoryType.PERSONAL,
    "Family issue: choosing sides between dad and mom, not prioritizing",
    {"stressor": True, "emotion": "neutral", "category": "family", "priority": "low"})

await service.add_memory(user_id, MemoryType.PERSONAL,
    "I really like this girl, regarding love",
    {"emotion": "love", "category": "romance", "intensity": 0.7})

await service.add_memory(user_id, MemoryType.PERSONAL,
    "Feeling isolated and lonely",
    {"emotion": "sadness", "category": "social", "intensity": 0.8})

# Test each scenario
overwhelm_results = await service.query_memories(user_id, "I'm overwhelmed with schoolwork")
assert any("schoolwork" in m.content.lower() or "catch up" in m.content.lower()
           for m in overwhelm_results)

family_results = await service.query_memories(user_id, "family issues")
assert any("family" in m.content.lower() or m.metadata.get("category") == "family"
           for m in family_results)

love_results = await service.query_memories(user_id, "I like this girl")
assert any("love" in m.content.lower() or m.metadata.get("category") == "romance"
           for m in love_results)

loneliness_results = await service.query_memories(user_id, "I feel isolated and lonely")
assert any("isolated" in m.content.lower() or "lonely" in m.content.lower()
           or m.metadata.get("emotion") == "sadness"
           for m in loneliness_results)
```

### AC11: Nuanced Emotion Detection (Beyond Basic Classifiers)

**Given** emotion detection is integrated (Story 2.6 dependency)
**When** memories are created with emotion metadata
**Then** emotions are stored with nuanced context, not just classifier labels

**And** emotion metadata includes:

- **Dominant emotion**: Primary classifier result (joy, anger, sadness, fear, love, surprise, neutral)
- **Emotion scores**: Full distribution across all emotion categories
- **Emotion context**: Nuanced interpretation (e.g., "overwhelm" = fear + sadness + stress indicators)
- **Emotion intensity**: 0.0-1.0 scale
- **Emotion triggers**: What in the message triggered this emotion (optional)

**And** classifiers serve as reference point, but system can evolve to more sophisticated detection

**Verification Steps:**

```python
# Store memory with nuanced emotion
memory = await service.add_memory(
    user_id=user_id,
    memory_type=MemoryType.PERSONAL,
    content="I'm overwhelmed with everything and can't catch up",
    metadata={
        "emotion": {
            "dominant": "fear",
            "scores": {"fear": 0.7, "sadness": 0.5, "anger": 0.2, "neutral": 0.1},
            "context": "overwhelm",  # Nuanced interpretation
            "intensity": 0.8,
            "triggers": ["overwhelmed", "can't catch up"]
        },
        "stressor": True
    }
)

# Verify nuanced emotion structure
emotion_data = memory.metadata.get("emotion")
assert emotion_data["dominant"] == "fear"
assert "scores" in emotion_data
assert emotion_data["context"] == "overwhelm"  # More nuanced than just "fear"
assert emotion_data["intensity"] > 0.5
```

### AC12: Productivity Structure Support (Goals → Tasks → Subtasks)

**Given** productivity structure exists (Goals, Tasks, Subtasks hierarchy)
**When** memories are created related to productivity items
**Then** memories can reference the full hierarchy structure

**And** memory metadata supports:

- **Goal references**: `goal_id`, `goal_title`
- **Task references**: `task_id`, `task_title`, `task_priority`
- **Subtask references**: `subtask_id`, `subtask_title`
- **Category classification**: Universal factors (Health, Learning, Craft, Connection, Discipline, etc.)
- **Weighting system**: Task contribution to universal factors (e.g., studying = 0.75 learning, 0.15 discipline)

**And** weighting system calculates how each task contributes to universal factors:

- Example: Studying task → `{learning: 0.75, discipline: 0.15, health: 0.05, craft: 0.05}`
- Weights sum to ~1.0 (can be >1.0 if task contributes significantly to multiple factors)

**Verification Steps:**

```python
# Store memory with productivity structure
memory = await service.add_memory(
    user_id=user_id,
    memory_type=MemoryType.PROJECT,
    content="Completed studying session for calculus exam",
    metadata={
        "goal_id": "goal-uuid",
        "goal_title": "Graduate early",
        "task_id": "task-uuid",
        "task_title": "Study for calculus",
        "task_priority": "high",
        "subtask_id": "subtask-uuid",
        "subtask_title": "Review chapter 5",
        "category": "academic",
        "universal_factors": {
            "learning": 0.75,
            "discipline": 0.15,
            "health": 0.05,
            "craft": 0.05
        }
    }
)

# Verify productivity structure
assert memory.metadata.get("goal_id") is not None
assert memory.metadata.get("universal_factors") is not None
factors = memory.metadata["universal_factors"]
assert factors["learning"] == 0.75
assert sum(factors.values()) <= 1.2  # Allow slight over-weighting
```

### AC13: User Priority System (Dynamic Value Identification)

**Given** user interactions and memory patterns exist
**When** the system analyzes user behavior
**Then** it identifies what the user values most and what pushes them furthest

**And** priority system accounts for:

- **Emotional state**: High stress = prioritize well-being, low stress = prioritize growth
- **Access patterns**: Frequently accessed memories indicate values
- **Goal completion patterns**: Which categories of goals user completes most
- **Universal factor weights**: Which factors user naturally gravitates toward
- **Dynamic adaptation**: Priorities shift based on current context (not deterministic)

**And** system calculates user priority profile:

- **Value weights**: `{health: 0.3, learning: 0.4, craft: 0.2, connection: 0.1}` (example)
- **Push factors**: What motivates user most (e.g., achievement, relationships, growth)
- **Current context**: Current emotional state, stress level, energy level
- **Adaptive recommendations**: What should be prioritized now vs. later

**Verification Steps:**

```python
# Analyze user priority profile
priority_profile = await service.calculate_user_priorities(user_id)

# Verify profile structure
assert "value_weights" in priority_profile
assert "push_factors" in priority_profile
assert "current_context" in priority_profile
assert "recommendations" in priority_profile

# Verify dynamic adaptation
# User in high stress → prioritize well-being
high_stress_profile = await service.calculate_user_priorities(
    user_id,
    current_emotion="overwhelm",
    stress_level="high"
)
assert high_stress_profile["value_weights"]["health"] > 0.3  # Increased

# User in low stress → prioritize growth
low_stress_profile = await service.calculate_user_priorities(
    user_id,
    current_emotion="neutral",
    stress_level="low"
)
assert low_stress_profile["value_weights"]["learning"] > 0.3  # Increased
```

### AC14: Different Embeddings for Different Memory Types

**Given** memories exist across different types (personal, project, task)
**When** embeddings are generated
**Then** different memory types can use different embedding strategies if needed

**And** embedding generation considers:

- **Memory type context**: Personal memories may benefit from different context than task memories
- **Content structure**: Project memories (goal-related) vs. task memories (action-related) may need different embeddings
- **Future extensibility**: System designed to support type-specific embedding models if needed

**Note**: MVP uses same embedding model (`text-embedding-3-small`) for all types, but architecture supports future differentiation

**Verification Steps:**

```python
# Generate embeddings for different memory types
personal_memory = await service.add_memory(
    user_id, MemoryType.PERSONAL, "I prefer working in the morning", {}
)
project_memory = await service.add_memory(
    user_id, MemoryType.PROJECT, "Goal: Graduate early", {}
)
task_memory = await service.add_memory(
    user_id, MemoryType.TASK, "Completed 20-minute walk", {}
)

# Verify all have embeddings (same model for MVP)
assert personal_memory.embedding is not None
assert project_memory.embedding is not None
assert task_memory.embedding is not None

# Future: Could use different embedding models per type
# Architecture supports: embedding_model_per_type configuration
```

---

## Tasks / Subtasks

### Task 1: Create Embedding Service (AC: #1, #6)

- [ ] **1.1** Create `packages/backend/app/services/embedding_service.py`
- [ ] **1.2** Implement `EmbeddingService` class with `generate_embedding(text: str) -> List[float]`
- [ ] **1.3** Use OpenAI `text-embedding-3-small` model (1536 dimensions)
- [ ] **1.4** Implement retry logic with exponential backoff (3 attempts)
- [ ] **1.5** Add error handling: return `None` if all retries fail (log error)
- [ ] **1.6** Add caching layer (optional): cache embeddings by content SHA-256 hash
- [ ] **1.7** Add unit tests for embedding generation and error handling

### Task 2: Create Memory Service Core Methods (AC: #1, #2, #3, #4)

- [ ] **2.1** Create `packages/backend/app/services/memory_service.py`
- [ ] **2.2** Implement `MemoryService.__init__(db: AsyncSession)` with OpenAI client initialization
- [ ] **2.3** Implement `add_memory()` method:
  - Generate embedding via `EmbeddingService`
  - Create `Memory` model instance
  - Set `created_at` and `accessed_at` timestamps
  - Commit to database
  - Return memory object
- [ ] **2.4** Implement `query_memories()` method:
  - Generate query embedding
  - Build SQL query with vector similarity (`embedding <=> query_vector`)
  - Filter by `memory_types` if provided
  - Filter by `user_id`
  - Apply `similarity_threshold` filter
  - Calculate time boost: `1 + log(1 + days_since_access + 1)^-1`
  - Calculate frequency boost: `1 + (log(access_count) * 0.1)`
  - Calculate final score: `similarity * time_boost * frequency_boost`
  - Sort by final score descending
  - Limit results to `limit` parameter
  - Update `accessed_at` for all retrieved memories
  - Increment `access_count` in metadata
  - Return list of `Memory` objects
- [ ] **2.5** Add helper method `_calculate_time_boost(days_since_access: int) -> float`
- [ ] **2.6** Add helper method `_calculate_frequency_boost(access_count: int) -> float`
- [ ] **2.7** Add helper method `_update_access_tracking(memories: List[Memory])` for batch updates

### Task 3: Implement Memory Pruning (AC: #5, #7)

- [ ] **3.1** Implement `prune_old_task_memories()` method in `MemoryService`:
  - Query: `SELECT * FROM memories WHERE memory_type = 'task' AND created_at < (NOW() - INTERVAL '30 days')`
  - Delete matching memories
  - Return count of deleted memories
  - Log pruning activity
- [ ] **3.2** Create `packages/backend/app/workers/memory_pruner.py`
- [ ] **3.3** Implement ARQ worker function `prune_task_memories_job(ctx)`:
  - Get database session
  - Initialize `MemoryService`
  - Call `prune_old_task_memories()`
  - Log result
  - Return deleted count
- [ ] **3.4** Configure ARQ worker settings with cron schedule (daily at 2:00 AM)
- [ ] **3.5** Add retry configuration (3 attempts, exponential backoff)
- [ ] **3.6** Test worker execution manually

### Task 4: Add Pydantic Schemas for Memory Operations (AC: #1, #2)

- [ ] **4.1** Update `packages/backend/app/schemas/memory.py` (if not exists, create it)
- [ ] **4.2** Add `MemoryQuery` schema for query parameters:
  ```python
  class MemoryQuery(BaseModel):
      query_text: str = Field(..., min_length=1, max_length=5000)
      memory_types: Optional[List[MemoryType]] = None
      limit: int = Field(default=10, ge=1, le=100)
      similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
  ```
- [ ] **4.3** Add `MemoryWithScore` schema for query results (includes final_score):
  ```python
  class MemoryWithScore(MemoryResponse):
      final_score: float
      similarity_score: float
      time_boost: float
      frequency_boost: float
  ```

### Task 5: Add Configuration and Environment Variables (AC: #1, #6)

- [ ] **5.1** Update `packages/backend/app/core/config.py`:
  - Add `OPENAI_API_KEY: str` from environment
  - Add `EMBEDDING_MODEL: str = "text-embedding-3-small"`
  - Add `EMBEDDING_DIMENSIONS: int = 1536`
  - Add `MEMORY_SIMILARITY_THRESHOLD: float = 0.7`
  - Add `MEMORY_PRUNE_RETENTION_DAYS: int = 30`
- [ ] **5.2** Update `packages/backend/env.example`:
  - Add `OPENAI_API_KEY=your_openai_api_key_here`
- [ ] **5.3** Document OpenAI API key setup in `docs/dev/SETUP.md`

### Task 6: Add Dependencies to pyproject.toml (AC: #1)

- [ ] **6.1** Update `packages/backend/pyproject.toml`:
  ```toml
  [tool.poetry.dependencies]
  openai = "^1.10.0"  # For embedding generation
  # ARQ already installed (from Epic 1)
  ```
- [ ] **6.2** Run `poetry install` to install dependencies
- [ ] **6.3** Verify imports work: `from openai import AsyncOpenAI`

### Task 7: Create Unit Tests (AC: All)

- [ ] **7.1** Create `packages/backend/tests/services/test_memory_service.py`
- [ ] **7.2** Test `add_memory()`:
  - Creates memory with embedding
  - Handles OpenAI API errors gracefully
  - Stores metadata correctly
- [ ] **7.3** Test `query_memories()`:
  - Filters by memory type
  - Returns results sorted by hybrid score
  - Updates access tracking
  - Applies similarity threshold
- [ ] **7.4** Test `prune_old_task_memories()`:
  - Deletes old task memories (>30 days)
  - Retains personal/project memories
  - Returns correct count
- [ ] **7.5** Test hybrid search scoring:
  - Time boost calculation
  - Frequency boost calculation
  - Final score ordering
- [ ] **7.6** Mock OpenAI API for all tests (use `unittest.mock`)
- [ ] **7.7** Use pytest fixtures for database sessions
- [ ] **7.8** Target: 80%+ test coverage for `MemoryService`

### Task 8: Integration Testing (AC: #1, #2, #3, #5, #9, #10)

- [ ] **8.1** Create `packages/backend/tests/integration/test_memory_integration.py`
- [ ] **8.2** Test end-to-end flow:
  - Add memories across all tiers
  - Query memories with hybrid search
  - Verify embeddings generated correctly
  - Verify pruning works
- [ ] **8.3** Test goal-based search:
  - Create project memories linked to goals
  - Query with goal-related keywords
  - Verify project tier memories prioritized
- [ ] **8.4** Test case study scenarios (AC10):
  - Overwhelm scenario (schoolwork, catch up)
  - Family issues scenario (non-priority stressor)
  - Love interest scenario (romance category)
  - Isolation/loneliness scenario (emotional support)
  - Verify correct memory retrieval for each scenario
- [ ] **8.5** Test with real database (use test database, not production)
- [ ] **8.6** Test ARQ worker execution (manual trigger for testing)

### Task 9: Goal-Based Search Implementation (AC: #9)

- [ ] **9.1** Add goal keyword detection to `query_memories()`:
  - Keywords: "goal", "goals", "plan", "plans", "objective", "objectives", "target", "targets"
  - When detected, prioritize `MemoryType.PROJECT` tier
- [ ] **9.2** Add `goal_id` filtering support in query parameters
- [ ] **9.3** Add helper method `_detect_goal_keywords(query_text: str) -> bool`
- [ ] **9.4** Update query logic to automatically include project tier when goal keywords detected
- [ ] **9.5** Add unit tests for goal-based search

### Task 10: Productivity Structure Support (AC: #12)

- [ ] **10.1** Design universal factors taxonomy:
  - Core factors: Health, Learning, Craft, Connection, Discipline
  - Extended factors: Growth, Achievement, Well-being, Creativity, Social
- [ ] **10.2** Create weighting calculation system:
  - Function: `calculate_task_weights(task_content: str, task_category: str) -> Dict[str, float]`
  - Use LLM or rule-based system to assign weights
  - Example: "studying" → `{learning: 0.75, discipline: 0.15, health: 0.05, craft: 0.05}`
- [ ] **10.3** Update memory metadata schema to support:
  - `goal_id`, `goal_title`
  - `task_id`, `task_title`, `task_priority`
  - `subtask_id`, `subtask_title`
  - `universal_factors`: Dict[str, float]
- [ ] **10.4** Add helper method `_calculate_universal_factors(content: str, category: str) -> Dict[str, float]`
- [ ] **10.5** Document weighting system in code comments

### Task 11: User Priority System (AC: #13)

- [ ] **11.1** Create `calculate_user_priorities()` method:
  - Analyze memory access patterns
  - Analyze goal completion patterns
  - Calculate value weights from universal factors
  - Identify push factors (motivation patterns)
- [ ] **11.2** Implement dynamic adaptation:
  - High stress → increase health/well-being weights
  - Low stress → increase learning/growth weights
  - Account for current emotional state
- [ ] **11.3** Create priority profile structure:
  ```python
  {
      "value_weights": {"health": 0.3, "learning": 0.4, ...},
      "push_factors": ["achievement", "growth"],
      "current_context": {"emotion": "overwhelm", "stress": "high"},
      "recommendations": {"prioritize": "well-being", "defer": "learning"}
  }
  ```
- [ ] **11.4** Add caching for priority profiles (recalculate daily, cache for session)
- [ ] **11.5** Add unit tests for priority calculation

### Task 12: Nuanced Emotion Detection Support (AC: #11)

- [ ] **12.1** Design nuanced emotion metadata structure:
  - `dominant`: str (classifier result)
  - `scores`: Dict[str, float] (full distribution)
  - `context`: str (nuanced interpretation like "overwhelm")
  - `intensity`: float (0.0-1.0)
  - `triggers`: List[str] (what triggered emotion)
- [ ] **12.2** Update memory service to accept nuanced emotion structure
- [ ] **12.3** Document that classifiers are starting point, system evolves
- [ ] **12.4** Add helper method `_interpret_emotion_context(scores: Dict[str, float]) -> str`
  - Maps emotion scores to nuanced contexts (e.g., fear + sadness → "overwhelm")
- [ ] **12.5** Add unit tests for emotion metadata handling

### Task 13: Case Study Testing Script (AC: #10)

- [ ] **13.1** Create `packages/backend/tests/case_study/test_user_case_study.py`
- [ ] **13.2** Implement test scenarios:
  - Overwhelm: "I'm overwhelmed with schoolwork, need to catch up"
  - Family: "Family issue: choosing sides, not prioritizing"
  - Love: "I really like this girl, regarding love"
  - Isolation: "Feeling isolated and lonely"
- [ ] **13.3** Create test memories for each scenario
- [ ] **13.4** Test memory retrieval with various query prompts
- [ ] **13.5** Verify correct memories retrieved for each scenario
- [ ] **13.6** Document test results and algorithm performance

### Task 14: Documentation and Code Comments (AC: All)

- [ ] **14.1** Add comprehensive docstrings to `MemoryService` methods
- [ ] **14.2** Document hybrid search algorithm in code comments
- [ ] **14.3** Document goal-based search logic
- [ ] **14.4** Document productivity structure and weighting system
- [ ] **14.5** Document user priority system and dynamic adaptation
- [ ] **14.6** Add usage examples in docstrings
- [ ] **14.7** Update `docs/API-TESTING-GUIDE.md` with memory service examples
- [ ] **14.8** Document ARQ worker setup in `docs/dev/SETUP.md`
- [ ] **14.9** Add memory service to architecture documentation
- [ ] **14.10** Document case study testing approach

---

## Dev Notes

### Memory Service Architecture (3-Tier Design)

**Personal Tier (Never Pruned):**

- Identity, preferences, emotional patterns
- Stressors log (from "How Eliza Should Respond" case study)
- Example: "I prefer working in the morning", "Class registration stress (fear, academic)"
- Always queried by Eliza for user context (top 5)
- Metadata: `{stressor: true, emotion: 'fear', category: 'academic'}`

**Project Tier (Goal-Related):**

- Goals, plans, progress snapshots
- Queried when user discusses specific goals (keyword detection in Story 2.3)
- Example: "Goal: Graduate early from Georgia Tech"
- Metadata: `{goal_id: "uuid", milestone: "Week 2 checkpoint"}`

**Task Tier (Short-Term, Pruned after 30 days):**

- Mission details, conversation exchanges
- Recent action context
- Example: "Completed 20-minute walk mission yesterday"
- Pruned by ARQ worker (this story)
- Metadata: `{conversation_id: "uuid", exchange_type: "goal_planning"}`

### Hybrid Search Algorithm Details

**From Tech Spec (tech-spec-epic-2.md lines 460-488):**

The hybrid search combines three signals:

1. **Semantic Similarity (Base Score)**:

   - Vector cosine distance: `1 - cosine_similarity(query_embedding, memory_embedding)`
   - Range: [0, 2] where 0 = identical, 2 = opposite
   - Convert to similarity score: `similarity = 1 - (distance / 2)` (range [0, 1])

2. **Time Decay Boost**:

   - Formula: `time_boost = 1 + log(1 + days_since_access + 1)^-1`
   - Recent memories (0 days): boost ≈ 1.44
   - Old memories (30 days): boost ≈ 1.03
   - Very old memories (365 days): boost ≈ 1.00
   - Ensures recent memories ranked higher even if similarity is slightly lower

3. **Access Frequency Boost**:

   - Formula: `frequency_boost = 1 + (log(access_count) * 0.1)`
   - First access (count=1): boost = 1.0
   - 10 accesses: boost ≈ 1.23
   - 100 accesses: boost ≈ 1.46
   - Rewards frequently referenced memories

4. **Final Score**:
   - `final_score = similarity * time_boost * frequency_boost`
   - Sorted descending (highest score = most relevant)
   - Filtered by `similarity_threshold` (default 0.7) before applying boosts

**Implementation Notes:**

- Use `math.log()` for natural logarithm
- Handle edge cases: `access_count = 0` → use 1, `days_since_access < 0` → use 0
- Cache time/frequency boosts in memory (don't recalculate for same memory)

### Embedding Generation Strategy

**Model:** OpenAI `text-embedding-3-small`

- Dimensions: 1536
- Cost: ~$0.02 per 1M tokens (very cheap)
- Speed: ~200ms per embedding generation (API latency)
- Quality: Proven effective for semantic search in production systems

**Error Handling:**

- Retry with exponential backoff: 1s, 2s, 4s delays
- If all retries fail: Store memory without embedding (`embedding = NULL`)
- Log error with context: `user_id`, `content[:100]` (truncated), `error_message`
- Continue conversation flow (don't block user interaction)

**Caching (Optional Enhancement):**

- Cache embeddings by content SHA-256 hash
- Store in Redis: `embedding:cache:{hash}` → `[float, ...]`
- TTL: 30 days (embeddings don't change for same content)
- Reduces API calls for duplicate content

### Memory Pruning Strategy

**Retention Policy:**

- **Personal**: Never pruned (long-term identity)
- **Project**: Never pruned (goal context)
- **Task**: 30-day retention (short-term mission context)

**Pruning Logic:**

```sql
DELETE FROM memories
WHERE memory_type = 'task'
AND created_at < (NOW() - INTERVAL '30 days');
```

**ARQ Worker Configuration:**

- Schedule: Daily at 2:00 AM (low traffic time)
- Retry: 3 attempts with exponential backoff (2s, 4s, 8s)
- Dead letter queue: Failed jobs after max retries
- Monitoring: Log deleted count, alert if >1000 memories pruned (indicates issue)

**Performance Considerations:**

- Use batch delete (single SQL statement, not loop)
- Index on `(memory_type, created_at)` for fast filtering
- Run during off-peak hours (2:00 AM) to minimize impact

### Learnings from Previous Story (2.1)

**From Story 2.1 Dev Notes:**

1. **SQLAlchemy Reserved Keywords**: `metadata` is reserved, use `extra_data` attribute with column mapping

   - **Impact**: MemoryService must use `memory.extra_data` internally, but API schemas use `metadata` alias

2. **Vector Similarity Query**: Use pgvector's `<=>` operator for cosine distance

   - **Implementation**: `embedding <=> query_embedding::vector`
   - **Ordering**: `ORDER BY embedding <=> query_embedding::vector ASC` (lower distance = more similar)

3. **HNSW Index Performance**: Index already created in Story 2.1, queries should be fast (<100ms p95)

   - **Verification**: Monitor query performance in production

4. **Database Connection**: Use async SQLAlchemy 2.0 patterns throughout
   - **Pattern**: `async with get_db() as db: service = MemoryService(db)`

### Project Structure Notes

**New Files Created:**

```
packages/backend/
├── app/
│   ├── services/
│   │   ├── memory_service.py          # NEW: Main memory service
│   │   └── embedding_service.py       # NEW: Embedding generation wrapper
│   └── workers/
│       └── memory_pruner.py           # NEW: ARQ worker for pruning
├── tests/
│   ├── services/
│   │   └── test_memory_service.py     # NEW: Unit tests
│   └── integration/
│       └── test_memory_integration.py # NEW: Integration tests
```

**Modified Files:**

```
packages/backend/
├── app/
│   ├── core/
│   │   └── config.py                  # UPDATE: Add OpenAI config
│   └── schemas/
│       └── memory.py                  # UPDATE: Add query schemas
├── pyproject.toml                     # UPDATE: Add openai dependency
└── env.example                         # UPDATE: Add OPENAI_API_KEY
```

### Relationship to Epic 2 Stories

This story (2.2) **enables**:

- **Story 2.3 (Eliza Agent)**: Agent's `recall_context` node uses `MemoryService.query_memories()`
- **Story 2.4 (Chat API)**: Stores conversation exchanges via `MemoryService.add_memory(type=TASK)`
- **Story 2.6 (Emotion Detection)**: Stores emotion scores in memory metadata

**Dependencies Flow:**

```
Story 2.1 (Memory Schema)
    ↓ (provides database tables)
Story 2.2 (Memory Service) ← THIS STORY
    ↓ (provides memory management)
Story 2.3 (Eliza Agent)
    ↓ (provides AI reasoning)
Story 2.4 (Chat API)
    ↓ (provides streaming interface)
Story 2.5 (Chat UI)
    = Working AI Companion! 🎉
```

### References

**Source Documents:**

- **Epic 2 Tech Spec**: `docs/tech-spec-epic-2.md` (lines 140-152: Service design, lines 460-488: Hybrid search algorithm)
- **Epics File**: `docs/epics.md` (lines 342-377: Story 2.2 requirements)
- **How Eliza Should Respond**: `docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md` (Stressor log, memory principles)
- **Implementation Guide**: `docs/epic-2/2-1-to-2-5-implementation-guide (draft).md` (lines 204-350: Step-by-step implementation)
- **Story 2.1**: `docs/stories/2-1-set-up-postgresql-pgvector-and-memory-schema.md` (Database foundation)

**Technical Documentation:**

- **OpenAI Embeddings API**: https://platform.openai.com/docs/guides/embeddings
- **LangChain PostgresVectorStore**: https://python.langchain.com/docs/integrations/vectorstores/pgvector
- **ARQ Workers**: https://arq-docs.helpmanual.io/
- **pgvector Operators**: https://github.com/pgvector/pgvector#operators

---

## Definition of Done

- [ ] ✅ `MemoryService` class created with `add_memory()`, `query_memories()`, `prune_old_task_memories()` methods
- [ ] ✅ `EmbeddingService` created with OpenAI integration and error handling
- [ ] ✅ `add_memory()` generates embeddings automatically (1536 dimensions)
- [ ] ✅ `query_memories()` implements hybrid search (semantic + time + frequency)
- [ ] ✅ `query_memories()` filters by memory type (3-tier architecture)
- [ ] ✅ `query_memories()` updates access tracking (`accessed_at`, `access_count`)
- [ ] ✅ Goal-based search implemented (AC9): detects goal keywords, prioritizes project tier
- [ ] ✅ Case study testing completed (AC10): all 4 scenarios tested and verified
- [ ] ✅ Nuanced emotion detection support (AC11): emotion structure with context and triggers
- [ ] ✅ Productivity structure support (AC12): Goals→Tasks→Subtasks, universal factors, weighting
- [ ] ✅ User priority system implemented (AC13): dynamic value identification, adaptation rules
- [ ] ✅ Different embeddings support (AC14): architecture supports type-specific embeddings (MVP uses same model)
- [ ] ✅ `prune_old_task_memories()` deletes old task memories (>30 days)
- [ ] ✅ ARQ worker configured for daily pruning (2:00 AM)
- [ ] ✅ Error handling: OpenAI API failures don't block memory creation
- [ ] ✅ Pydantic schemas created for memory operations
- [ ] ✅ Configuration added: `OPENAI_API_KEY`, embedding model settings
- [ ] ✅ Dependencies added: `openai` package in `pyproject.toml`
- [ ] ✅ Unit tests created with 80%+ coverage
- [ ] ✅ Integration tests created (end-to-end flow)
- [ ] ✅ Case study test suite created (`tests/case_study/test_user_case_study.py`)
- [ ] ✅ All acceptance criteria manually verified (AC1-AC14)
- [ ] ✅ Code follows async SQLAlchemy 2.0 patterns
- [ ] ✅ No secrets committed (API keys in .env only)
- [ ] ✅ Documentation updated (docstrings, SETUP.md, API guide, case study testing approach)
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline

- **Task 1** (Embedding Service): 1.5 hours
- **Task 2** (Memory Service Core): 2.5 hours
- **Task 3** (Memory Pruning): 1 hour
- **Task 4** (Pydantic Schemas): 30 minutes
- **Task 5** (Configuration): 30 minutes
- **Task 6** (Dependencies): 15 minutes
- **Task 7** (Unit Tests): 2 hours
- **Task 8** (Integration Tests): 1 hour
- **Task 9** (Documentation): 1 hour

**Total:** 10 hours (aligns with story estimate of 6-8 hours, with buffer)

### Risk Mitigation

**Risk:** OpenAI API rate limits or outages

- **Mitigation**: Implement retry logic with exponential backoff, store memories without embedding if API fails
- **Impact**: Medium (conversations continue, but memory search degraded)

**Risk:** Hybrid search performance degrades with large memory tables (>10K memories per user)

- **Mitigation**: HNSW index already optimized (Story 2.1), limit query results, monitor query time
- **Impact**: Low (HNSW index handles large datasets efficiently)

**Risk:** ARQ worker fails silently

- **Mitigation**: Add comprehensive logging, monitor dead letter queue, alert on failures
- **Impact**: Medium (old task memories accumulate, but doesn't block user interactions)

**Risk:** Time decay calculation incorrect

- **Mitigation**: Unit tests for boost calculations, verify with known test cases
- **Impact**: Low (easy to fix if discovered)

### Goal-Based Memory Search

**From User Requirements:**

When users discuss goals, the system should search through goals specifically. This enables Eliza to provide context-aware responses about the user's objectives and plans.

**Implementation Strategy:**

1. **Keyword Detection**: Detect goal-related keywords in query text:

   - Keywords: "goal", "goals", "plan", "plans", "objective", "objectives", "target", "targets"
   - Use simple keyword matching or LLM-based detection

2. **Tier Prioritization**: When goal keywords detected:

   - Automatically include `MemoryType.PROJECT` in search
   - Boost project tier memories in hybrid scoring
   - Filter by `goal_id` if provided in query context

3. **Query Enhancement**:

   ```python
   def _detect_goal_keywords(query_text: str) -> bool:
       goal_keywords = ["goal", "goals", "plan", "plans", "objective", "target"]
       return any(keyword in query_text.lower() for keyword in goal_keywords)

   # In query_memories():
   if _detect_goal_keywords(query_text) and MemoryType.PROJECT not in memory_types:
       memory_types = memory_types or []
       memory_types.append(MemoryType.PROJECT)
   ```

**Benefits:**

- More relevant memory retrieval when discussing goals
- Better context for Eliza's goal-related responses
- Supports Epic 3 (Goal & Mission Management) integration

### Comprehensive Case Study Testing

**From User Requirements:**

The memory retrieval algorithm must be thoroughly tested with real user scenarios to ensure it works correctly for different emotional prompts and contexts.

**Test Scenarios (User Case Study):**

1. **Overwhelm Scenario**: "I'm recently overwhelmed with my schoolwork because I have to catch up"

   - **Expected Retrieval**: Schoolwork-related memories, stressor memories, academic category memories
   - **Test Queries**:
     - "I'm overwhelmed with schoolwork"
     - "I need to catch up"
     - "academic stress"
   - **Success Criteria**: Top 3 results include overwhelm/schoolwork/catch-up related memories

2. **Family Issues Scenario**: "I have my family issue where I have to choose sides with dad and mom. But I don't think it's a big issue because it's not something I'm prioritizing"

   - **Expected Retrieval**: Family-related memories, relationship memories, priority context
   - **Test Queries**:
     - "family issues"
     - "choosing sides"
     - "dad and mom"
   - **Success Criteria**: Family memories retrieved, but not over-weighted (low priority noted)

3. **Love Interest Scenario**: "I really like this girl, it's just regarding love"

   - **Expected Retrieval**: Relationship memories, emotional memories, personal preferences
   - **Test Queries**:
     - "I like this girl"
     - "love interest"
     - "romance"
   - **Success Criteria**: Love/romance category memories retrieved

4. **Isolation/Loneliness Scenario**: "I feel isolated and lonely"
   - **Expected Retrieval**: Emotional state memories, social context memories, support needs
   - **Test Queries**:
     - "I feel isolated"
     - "loneliness"
     - "social support"
   - **Success Criteria**: Isolation/loneliness patterns retrieved, emotional support context available

**Testing Approach:**

- Create comprehensive test suite: `tests/case_study/test_user_case_study.py`
- Seed database with case study memories
- Test various query prompts for each scenario
- Measure retrieval accuracy (top-K recall)
- Document algorithm performance and edge cases

**Importance:**

This testing is **critical** because it validates the core memory retrieval algorithm works correctly for real user scenarios. The hybrid search algorithm (semantic + time + frequency) must retrieve relevant memories even when query phrasing varies.

### Nuanced Emotion Detection

**From User Requirements:**

Emotion detection should not be just basic sentiment analysis. It should be more complex and nuanced. Classifiers are a good starting point, but the system should evolve beyond simple classification.

**Current Approach (Story 2.6 Dependency):**

- **Base Classifier**: `cardiffnlp/twitter-roberta-base-emotion-multilingual-latest`
  - 7 emotions: joy, anger, sadness, fear, love, surprise, neutral
  - Fast inference (~50ms on CPU)
  - Provides emotion scores distribution

**Nuanced Emotion Structure:**

```python
{
    "emotion": {
        "dominant": "fear",  # Classifier result
        "scores": {
            "fear": 0.7,
            "sadness": 0.5,
            "anger": 0.2,
            "neutral": 0.1,
            "joy": 0.05,
            "surprise": 0.03,
            "love": 0.02
        },
        "context": "overwhelm",  # Nuanced interpretation
        "intensity": 0.8,  # Overall intensity (0.0-1.0)
        "triggers": ["overwhelmed", "can't catch up"]  # What triggered emotion
    }
}
```

**Emotion Context Interpretation:**

Map emotion score combinations to nuanced contexts:

- **Fear + Sadness** → "overwhelm" (user feels overwhelmed)
- **Fear + Anger** → "frustration" (user is frustrated)
- **Sadness + Low Joy** → "loneliness" (user feels isolated)
- **Love + Joy** → "romantic interest" (user has romantic feelings)
- **Neutral + Low Everything** → "detached" (user is emotionally detached)

**Future Evolution:**

- **LLM-Based Interpretation**: Use GPT-4o-mini to interpret emotion scores and generate nuanced context
- **Context-Aware Detection**: Consider conversation history, not just single message
- **Emotion Trajectory**: Track emotion changes over time
- **Emotion Triggers**: Identify what specifically triggered the emotion (using LLM)

**Implementation Notes:**

- Store full emotion structure in memory metadata
- Classifiers provide starting point, but system can evolve
- Document that this is MVP approach, future enhancements planned

### Productivity Structure (Goals → Tasks → Subtasks)

**From User Requirements:**

Even though not shown to the user initially, the productivity structure should be solid:

- **Hierarchy**: Goals → Tasks → Subtasks
- **Priorities**: Different priority levels
- **Categories**: Different categories
- **Universal Factors**: Health, Learning, Craft, Connection, Discipline, etc.
- **Weighting System**: Each task contributes to universal factors with weights

**Universal Factors Taxonomy:**

**Core Factors:**

- **Health**: Physical and mental well-being
- **Learning**: Knowledge acquisition, skill development
- **Craft**: Creative expression, making things
- **Connection**: Relationships, social bonds
- **Discipline**: Self-control, consistency, habits

**Extended Factors:**

- **Growth**: Personal development, self-improvement
- **Achievement**: Accomplishments, milestones
- **Well-being**: Overall life satisfaction
- **Creativity**: Innovation, originality
- **Social**: Community involvement, networking

**Weighting System:**

Each task contributes to universal factors with weights that sum to ~1.0 (can be >1.0 if task contributes significantly to multiple factors).

**Examples:**

- **Studying**: `{learning: 0.75, discipline: 0.15, health: 0.05, craft: 0.05}`
- **Exercise**: `{health: 0.70, discipline: 0.20, learning: 0.10}`
- **Art Project**: `{craft: 0.60, creativity: 0.25, learning: 0.15}`
- **Social Event**: `{connection: 0.70, social: 0.20, well-being: 0.10}`
- **Meditation**: `{well-being: 0.50, health: 0.30, discipline: 0.20}`

**Calculation Approach:**

1. **Rule-Based (MVP)**: Predefined weights for common task categories
2. **LLM-Based (Future)**: Use GPT-4o-mini to analyze task content and assign weights dynamically

**Memory Metadata Structure:**

```python
{
    "goal_id": "uuid",
    "goal_title": "Graduate early",
    "task_id": "uuid",
    "task_title": "Study for calculus",
    "task_priority": "high",
    "subtask_id": "uuid",
    "subtask_title": "Review chapter 5",
    "category": "academic",
    "universal_factors": {
        "learning": 0.75,
        "discipline": 0.15,
        "health": 0.05,
        "craft": 0.05
    }
}
```

**Benefits:**

- Enables future task prioritization based on user values
- Supports Epic 3 (Goal & Mission Management) integration
- Foundation for intelligent task recommendations
- Tracks what universal factors user is focusing on

### User Priority System (Dynamic Value Identification)

**From User Requirements:**

The system should identify what the user values more and what pushes them furthest. This should be dynamic and smart, not deterministic. It should account for emotions, stress, and act like a psychologist + coach.

**Priority Profile Structure:**

```python
{
    "value_weights": {
        "health": 0.3,
        "learning": 0.4,
        "craft": 0.2,
        "connection": 0.1
    },
    "push_factors": ["achievement", "growth"],  # What motivates user
    "current_context": {
        "emotion": "overwhelm",
        "stress_level": "high",
        "energy_level": "low"
    },
    "recommendations": {
        "prioritize": "well-being",  # What to focus on now
        "defer": "learning",  # What can wait
        "suggest": "20-minute walk"  # Specific action
    }
}
```

**Calculation Method:**

1. **Value Weights** (from memory patterns):

   - Analyze which universal factors appear most in user's memories
   - Weight by access frequency (frequently accessed = more important)
   - Normalize to sum to 1.0

2. **Push Factors** (from goal completion patterns):

   - Which categories of goals user completes most
   - What motivates user (achievement, relationships, growth, etc.)
   - Derived from goal completion rates and memory patterns

3. **Dynamic Adaptation** (based on current context):
   - **High Stress**: Increase health/well-being weights, decrease learning/growth
   - **Low Stress**: Increase learning/growth weights, maintain health
   - **High Energy**: Prioritize challenging tasks
   - **Low Energy**: Prioritize easy wins, well-being

**Adaptation Rules:**

```python
def adapt_priorities(base_weights, emotion, stress_level, energy_level):
    adapted = base_weights.copy()

    if stress_level == "high" or emotion in ["overwhelm", "fear", "sadness"]:
        # Prioritize well-being
        adapted["health"] *= 1.5
        adapted["well_being"] = adapted.get("well_being", 0) + 0.2
        adapted["learning"] *= 0.7  # Decrease learning focus

    if stress_level == "low" and energy_level == "high":
        # Prioritize growth
        adapted["learning"] *= 1.3
        adapted["growth"] = adapted.get("growth", 0) + 0.15

    # Normalize
    total = sum(adapted.values())
    return {k: v/total for k, v in adapted.items()}
```

**Implementation:**

- Method: `calculate_user_priorities(user_id, current_emotion=None, stress_level=None, energy_level=None)`
- Cache results: Recalculate daily, cache for session
- Update on memory access: Incremental updates based on new memories

**Benefits:**

- Enables intelligent task prioritization
- Supports Eliza's coaching decisions (when to push vs. when to support)
- Acts like psychologist + coach (understands user, adapts to context)
- Dynamic and smart (not deterministic, adapts to user state)

### Future Enhancements (Post-Story)

- [ ] Add memory deduplication (detect and merge similar memories)
- [ ] Implement memory consolidation (summarize old memories)
- [ ] Add memory importance scoring (prioritize retrieval beyond frequency)
- [ ] Create memory search API endpoint (debugging/admin)
- [ ] Add memory export/import for user data portability
- [ ] Implement embedding caching (Redis cache by content hash)
- [ ] Add memory analytics (track memory growth, access patterns)
- [ ] LLM-based emotion context interpretation (beyond classifiers)
- [ ] LLM-based universal factor weighting (dynamic task analysis)
- [ ] Emotion trajectory tracking (emotion changes over time)
- [ ] Context-aware emotion detection (consider conversation history)

---

**Last Updated:** 2025-11-12 (Comprehensive update with user requirements)
**Story Status:** drafted
**Next Steps:** Run `story-context` workflow to generate technical context XML → mark `ready-for-dev`

## User Requirements Integration Summary

This story has been comprehensively updated based on user requirements:

1. **Goal-Based Search**: When users discuss goals, system searches through goals specifically (AC9)
2. **Case Study Testing**: Comprehensive testing with real user scenarios (overwhelm, family, love, isolation) (AC10)
3. **Nuanced Emotion Detection**: Beyond basic classifiers, includes context and triggers (AC11)
4. **Productivity Structure**: Goals→Tasks→Subtasks hierarchy with universal factors and weighting system (AC12)
5. **User Priority System**: Dynamic value identification that adapts to emotions/stress, acts like psychologist + coach (AC13)
6. **Different Embeddings**: Architecture supports type-specific embeddings (MVP uses same model) (AC14)

All requirements have been integrated into acceptance criteria, tasks, and dev notes with comprehensive implementation guidance.
