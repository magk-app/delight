# Memory Updates and System Customization Guide

This guide explains the continuous memory update system and comprehensive customization features implemented in the Delight AI companion platform.

## Table of Contents

- [Overview](#overview)
- [Vector Memory Updates](#vector-memory-updates)
- [Graph Knowledge Tracking](#graph-knowledge-tracking)
- [System Customization](#system-customization)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Background Workers](#background-workers)

---

## Overview

The memory and customization system enables the AI agent to:

1. **Learn continuously** by storing summaries, search results, and insights as searchable memories
2. **Build structured knowledge** through entity and relationship tracking
3. **Adapt to user preferences** via comprehensive customization settings
4. **Optimize performance** through intelligent model selection
5. **Ensure safety** via content filtering and validation

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Memory System                            │
│                                                              │
│  ┌────────────────┐    ┌──────────────────┐                │
│  │ OpenAI API     │───>│ EmbeddingService │                │
│  └────────────────┘    └────────┬─────────┘                │
│                                  │                           │
│                          ┌───────▼────────┐                 │
│                          │ MemoryService  │                 │
│                          │                │                 │
│                          │ • CRUD         │                 │
│                          │ • Hybrid Search│                 │
│                          │ • Pruning      │                 │
│                          │ • Priorities   │                 │
│                          └───────┬────────┘                 │
│                                  │                           │
│                    ┌─────────────┴────────────┐            │
│                    ▼                          ▼             │
│          ┌──────────────────┐    ┌──────────────────┐     │
│          │ Vector Storage   │    │ Knowledge Graph  │     │
│          │ (pgvector/HNSW)  │    │ (entities/rels)  │     │
│          └──────────────────┘    └──────────────────┘     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 Customization System                         │
│                                                              │
│  ┌────────────────────┐    ┌──────────────────┐            │
│  │ AgentPreferences   │───>│ ModelRouter      │            │
│  │                    │    │                  │            │
│  │ • Memory Settings  │    │ • Task Analysis  │            │
│  │ • Model Selection  │    │ • Cost Optimizer │            │
│  │ • Reasoning Depth  │    │ • Model Selection│            │
│  │ • Safety Filters   │    └──────────────────┘            │
│  │ • Interaction      │                                     │
│  └────────────────────┘    ┌──────────────────┐            │
│                            │ValidationSafety  │            │
│                            │                  │            │
│                            │ • Content Filter │            │
│                            │ • PII Detection  │            │
│                            │ • Fact Verify    │            │
│                            └──────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## Vector Memory Updates

### Overview

The vector memory system stores memories with semantic embeddings for intelligent retrieval:

- **Automatic embedding generation** using OpenAI text-embedding-3-small (1536 dimensions)
- **Hybrid search algorithm** combining semantic similarity, time decay, and access frequency
- **3-tier architecture**: PERSONAL (never pruned), PROJECT (goals), TASK (30-day retention)
- **Summary storage** for agent learning and knowledge accumulation

### Hybrid Search Algorithm

```python
# Base similarity from pgvector (cosine distance)
base_similarity = 1.0 - (distance / 2.0)

# Time boost: recent memories prioritized
days_since_access = (now - accessed_at).total_seconds() / 86400
time_boost = 1.0 + (1.0 / math.log1p(days_since_access + 1))

# Frequency boost: frequently accessed memories boosted
access_count = metadata.get("access_count", 1)
frequency_boost = 1.0 + (math.log1p(access_count) * 0.1)

# Final hybrid score
final_score = base_similarity * time_boost * frequency_boost
```

### Strategic Context Retrieval

The 3-tier strategic retrieval optimizes memory access for AI agents:

- **PERSONAL tier**: Always retrieve top 5 (core identity, preferences, stressors)
- **PROJECT tier**: Retrieve top 10 when goal-related keywords detected
- **TASK tier**: Retrieve top 5 recent conversation contexts

### Memory Pruning

- **TASK memories**: Automatically pruned after 30 days
- **PERSONAL memories**: Never pruned (core identity)
- **PROJECT memories**: Never pruned (long-term goals)
- **Background worker**: Runs daily at 2:00 AM UTC

---

## Graph Knowledge Tracking

### Overview

The knowledge graph complements vector memory with structured relationship tracking:

- **Entities**: People, projects, concepts, events, stressors, habits, preferences
- **Relationships**: Directed edges with types (HAS, CAUSES, REQUIRES, etc.)
- **Semantic search**: Vector embeddings for entities
- **Confidence tracking**: Each entity/relationship has confidence score (0.0-1.0)

### Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| `PERSON` | People in user's life | User, family, friends, colleagues |
| `PROJECT` | Goals and initiatives | "Graduate early", "Learn Python" |
| `CONCEPT` | Abstract ideas | "Machine learning", "Time management" |
| `EVENT` | Meetings, deadlines | "Registration deadline", "Final exam" |
| `STRESSOR` | Anxiety sources | "Class registration", "Public speaking" |
| `HABIT` | Behaviors, routines | "Morning walk", "Study schedule" |
| `PREFERENCE` | Likes, dislikes | "Prefers morning work", "Dislikes crowds" |
| `OTHER` | Uncategorized | Miscellaneous entities |

### Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| `HAS` | Ownership | User HAS Goal |
| `IS_A` | Type/category | Georgia_Tech IS_A University |
| `RELATED_TO` | Generic association | Study RELATED_TO Learning |
| `CAUSES` | Causal relationship | Registration CAUSES Anxiety |
| `REQUIRES` | Dependency | Goal REQUIRES Learning |
| `PART_OF` | Component | Week_2 PART_OF Goal |
| `AFFECTS` | Influence | Anxiety AFFECTS Performance |
| `LOCATED_AT` | Location | Meeting LOCATED_AT Campus |
| `OTHER` | Uncategorized | Custom relationships |

### Example Knowledge Graph

```
[User] ──HAS──> [Graduate Early (Goal)]
         │
         └──EXPERIENCES──> [Registration Anxiety (Stressor)]

[Graduate Early] ──HAS_DEADLINE──> [November (Event)]
                 │
                 ├──REQUIRES──> [Learning (Concept)]
                 │
                 └──HAS_PROPERTY──> {"progress": 0.35}

[Registration Anxiety] ──CAUSES──> [Stress Response]
                       │
                       └──AFFECTS──> [Focus]
```

---

## System Customization

### AgentPreferences Model

Comprehensive customization across 5 categories:

#### 1. Memory Settings

```python
{
    "recency_bias": 0.5,           # 0.0 = no bias, 1.0 = strong recency
    "similarity_threshold": 0.4,   # Minimum similarity for retrieval
    "top_k": {
        "personal": 5,             # PERSONAL memories to retrieve
        "project": 10,             # PROJECT memories to retrieve
        "task": 5                  # TASK memories to retrieve
    },
    "grouping": {
        "by_project": true,        # Group by project
        "by_type": true            # Group by type
    }
}
```

#### 2. Model Selection

```python
{
    "default": "auto",             # auto, fast, balanced, powerful
    "task_specific": {
        "coding": "fast",          # GPT-4o-mini
        "writing": "balanced",     # GPT-4o
        "analysis": "powerful",    # o1-preview
        "conversation": "fast"     # GPT-4o-mini
    }
}
```

**Model Tiers**:

| Tier | Models | Cost (per 1M tokens) | Use Case |
|------|--------|----------------------|----------|
| `fast` | GPT-4o-mini, Claude Haiku | $0.15/$0.60 | Chat, simple tasks |
| `balanced` | GPT-4o, Claude Sonnet | $2.50/$10.00 | Standard operations |
| `powerful` | o1-preview, Claude Opus | $15.00/$60.00 | Deep analysis |

#### 3. Reasoning Settings

```python
{
    "depth": "medium",             # quick, medium, thorough
    "max_cycles": 3,               # Max research/reasoning cycles
    "multi_hop": {
        "enabled": true,
        "max_hops": 5              # Max relationship traversal depth
    }
}
```

**Reasoning Depth**:

- **QUICK**: 1-2 steps, minimal research (fast answers)
- **MEDIUM**: 3-5 steps, moderate research (balanced)
- **THOROUGH**: 5-10 steps, extensive research (deep analysis)

#### 4. Safety & Validation

```python
{
    "filter_level": "medium",      # low, medium, high
    "fact_verification": {
        "enabled": false,
        "require_sources": false   # Require citation sources
    },
    "search_domains": {
        "allowed": [],             # Whitelist (empty = all allowed)
        "blocked": []              # Blacklist
    }
}
```

**Safety Levels**:

- **LOW**: Minimal filtering, trust user
- **MEDIUM**: Standard filtering, block obvious issues
- **HIGH**: Strict filtering, verify facts, require sources

#### 5. Interaction Style

```python
{
    "style": "balanced",           # concise, balanced, detailed, transparent
    "show_planning": {
        "enabled": false,
        "on_request": true         # Show reasoning if user asks
    },
    "language": "en",              # ISO 639-1 language code
    "technical_jargon": {
        "enabled": true,
        "domains": []              # Specific domains for jargon
    }
}
```

**Interaction Styles**:

- **CONCISE**: Brief answers, minimal explanation
- **BALANCED**: Standard responses with some detail
- **DETAILED**: Verbose explanations, show thinking
- **TRANSPARENT**: Show all planning nodes and reasoning steps

---

## API Reference

### Memory Endpoints (`/api/v1/memories`)

#### Create Memory

```http
POST /api/v1/memories
Content-Type: application/json

{
    "memory_type": "personal",
    "content": "User prefers working in the morning",
    "metadata": {
        "preference": true,
        "category": "work_habits"
    }
}
```

#### Semantic Search

```http
POST /api/v1/memories/search?query_text=anxiety&limit=10&similarity_threshold=0.5
```

#### Strategic Context Retrieval

```http
GET /api/v1/memories/context/strategic?query_text=I want to talk about my goals
```

Returns:
```json
{
    "personal": [...],  // Top 5 personal memories
    "project": [...],   // Top 10 project memories (if goal-related)
    "task": [...]       // Top 5 recent task memories
}
```

#### Store Summary

```http
POST /api/v1/memories/summary
  ?summary_content=User struggles with time management
  &source_context=Analysis of recent conversations
  &memory_type=personal
```

### Agent Preferences Endpoints (`/api/v1/agent-preferences`)

#### Get Preferences

```http
GET /api/v1/agent-preferences
```

Creates default preferences if none exist.

#### Update Preferences (Partial)

```http
PUT /api/v1/agent-preferences
Content-Type: application/json

{
    "memory_recency_bias": 0.7,
    "reasoning_depth": "thorough",
    "interaction_style": "detailed"
}
```

#### Get as Dictionary

```http
GET /api/v1/agent-preferences/dict
```

Returns preferences organized by category.

### Knowledge Graph Endpoints (`/api/v1/knowledge`)

#### Create Entity

```http
POST /api/v1/knowledge/entities
Content-Type: application/json

{
    "entity_type": "project",
    "name": "Graduate Early",
    "description": "Goal to graduate from Georgia Tech early",
    "properties": {
        "deadline": "November 2025",
        "progress": 0.35
    },
    "confidence": 1.0
}
```

#### Create Relationship

```http
POST /api/v1/knowledge/relationships
Content-Type: application/json

{
    "from_entity_id": "user-entity-uuid",
    "to_entity_id": "goal-entity-uuid",
    "relationship_type": "has",
    "properties": {
        "priority": "high"
    },
    "confidence": 1.0
}
```

#### Get Related Entities

```http
GET /api/v1/knowledge/entities/{entity_id}/related?direction=both
```

#### Get Entity Context

```http
GET /api/v1/knowledge/entities/{entity_id}/context?max_depth=2
```

---

## Usage Examples

### Example 1: Learning from Conversations

```python
# Agent summarizes a conversation about user's anxiety
summary_content = "User experiences anxiety during class registration due to system crashes"

# Store as PERSONAL memory (never pruned)
memory = await memory_service.store_summary(
    db,
    user_id,
    summary_content,
    source_context="Conversation about registration stress",
    memory_type=MemoryType.PERSONAL,
    metadata={
        "stressor": True,
        "emotion": "anxiety",
        "category": "academic",
        "intensity": 0.8
    }
)
```

### Example 2: Building Knowledge Graph from Memory

```python
# Extract entities from memory
memory_content = "I need to graduate early from Georgia Tech to pursue my startup"

# Create entities
user_entity = await kg_service.create_entity(
    db, user_id, "User", EntityType.PERSON
)

goal_entity = await kg_service.create_entity(
    db, user_id, "Graduate Early", EntityType.PROJECT,
    description="Graduate from Georgia Tech early",
    properties={"target_date": "May 2024", "progress": 0.25}
)

startup_entity = await kg_service.create_entity(
    db, user_id, "Startup", EntityType.PROJECT,
    description="User's entrepreneurial venture"
)

# Create relationships
await kg_service.create_relationship(
    db, user_id,
    user_entity.id, goal_entity.id,
    RelationshipType.HAS,
    properties={"priority": "high"}
)

await kg_service.create_relationship(
    db, user_id,
    goal_entity.id, startup_entity.id,
    RelationshipType.REQUIRES,
    properties={"reason": "Need early graduation to pursue startup"}
)
```

### Example 3: Customizing Agent Behavior

```python
# User wants thorough analysis with detailed explanations
preferences = AgentPreferences(
    user_id=user_id,

    # Use powerful models for analysis
    default_model_preference=ModelPreference.POWERFUL,
    task_specific_models={
        "analysis": "powerful",
        "planning": "balanced"
    },

    # Deep reasoning
    reasoning_depth=ReasoningDepth.THOROUGH,
    max_research_cycles=5,
    enable_multi_hop_reasoning={"enabled": True, "max_hops": 7},

    # Detailed interaction
    interaction_style=InteractionStyle.DETAILED,
    show_planning_nodes={"enabled": True, "on_request": False},

    # High safety
    content_filter_level="high",
    enable_fact_verification={"enabled": True, "require_sources": True}
)
```

### Example 4: Intelligent Model Selection

```python
from app.services.model_router import get_model_router, TaskType

router = get_model_router()

# For simple conversation - uses fast model (GPT-4o-mini)
model = await router.select_model(
    db, user_id,
    task_type=TaskType.CONVERSATION
)
# => {"provider": "openai", "model": "gpt-4o-mini", "tier": "fast"}

# For deep analysis - uses powerful model (o1-preview)
model = await router.select_model(
    db, user_id,
    task_type=TaskType.ANALYSIS,
    estimated_complexity=0.9
)
# => {"provider": "openai", "model": "o1-preview", "tier": "powerful"}

# Estimate cost
cost = await router.estimate_cost(
    model,
    input_tokens=1000,
    output_tokens=500
)
# => 0.045 USD
```

---

## Background Workers

### Memory Pruner

ARQ background worker for automatic memory pruning.

#### Setup

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Configure Redis**:
   ```bash
   export REDIS_URL=redis://localhost:6379
   ```

3. **Start worker**:
   ```bash
   poetry run arq app.workers.memory_pruner.WorkerSettings
   ```

#### Cron Schedule

- **Frequency**: Daily at 2:00 AM UTC
- **Operation**: Delete TASK memories older than 30 days
- **Scope**: All users
- **Exclusions**: PERSONAL and PROJECT memories

#### Manual Execution

```bash
# Test pruning immediately
poetry run python -c "import asyncio; from app.workers.memory_pruner import run_prune_now; asyncio.run(run_prune_now())"

# Prune specific user (via ARQ)
from arq import create_pool
redis = await create_pool()
await redis.enqueue_job('prune_user_task_memories', user_id='uuid-here')
```

#### Monitoring

Worker logs include:
- Number of memories deleted
- Processing duration
- Timestamp

Example log:
```
Memory pruning completed: 127 memories deleted in 2.34 seconds
```

---

## Best Practices

### Memory Management

1. **Use appropriate tiers**:
   - PERSONAL: Core identity, preferences, stressors
   - PROJECT: Goals, plans, progress snapshots
   - TASK: Conversations, temporary context

2. **Store summaries, not raw data**:
   - Store final insights, not every conversation exchange
   - Keep signal-to-noise ratio high
   - Tag with source references for verification

3. **Update incrementally**:
   - Update entity properties as new information learned
   - Increase confidence when information confirmed
   - Merge duplicate entities

### Customization

1. **Start with defaults**:
   - Let users try default settings first
   - Adjust based on feedback and usage patterns

2. **Match settings to use case**:
   - Casual chat → fast models, concise responses
   - Deep work → powerful models, thorough reasoning
   - Learning → detailed explanations, show planning

3. **Balance cost and quality**:
   - Use AUTO mode for most tasks
   - Reserve powerful models for complex analysis
   - Monitor cost via estimate_cost()

### Safety

1. **Adjust safety levels by context**:
   - PUBLIC: High safety, strict filtering
   - PERSONAL: Medium safety, balanced
   - DEVELOPMENT: Low safety, permissive

2. **Whitelist trusted domains**:
   - Specify allowed domains for web search
   - Block known problematic sources

3. **Enable fact verification for critical tasks**:
   - Medical, legal, financial advice
   - Public statements
   - Important decisions

---

## Troubleshooting

### Memory Not Found in Search

**Cause**: Embedding not generated or similarity threshold too high

**Solution**:
```python
# Check if memory has embedding
memory = await memory_service.get_memory(db, user_id, memory_id)
if memory.embedding is None:
    # Regenerate embedding
    await memory_service.update_memory(
        db, user_id, memory_id,
        MemoryUpdate(content=memory.content)
    )

# Lower similarity threshold
results = await memory_service.semantic_search(
    db, user_id, query,
    similarity_threshold=0.3  # Lower threshold
)
```

### Slow Semantic Search

**Cause**: No HNSW index or too many memories

**Solution**:
```bash
# Check index exists
psql -c "SELECT indexname FROM pg_indexes WHERE tablename='memories';"

# Rebuild HNSW index if needed
psql -c "REINDEX INDEX ix_memories_embedding;"

# Adjust ef_search for speed/recall tradeoff
psql -c "SET hnsw.ef_search = 40;"  # Lower = faster, less accurate
```

### Knowledge Graph Circular Dependencies

**Cause**: Relationships forming cycles

**Solution**:
```python
# Check for cycles before creating relationship
existing = await kg_service.get_relationship(
    db, user_id,
    to_entity_id, from_entity_id,  # Reversed
    relationship_type
)

if existing:
    # Cycle detected, handle appropriately
    logger.warning(f"Circular relationship detected: {from_entity} <-> {to_entity}")
```

---

## Performance Considerations

### Memory System

- **Vector search**: <100ms p95 for 10K memories (HNSW index)
- **Embedding generation**: ~50-100ms per text (OpenAI API)
- **Batch embeddings**: 100 texts in ~500ms (batched API call)

### Knowledge Graph

- **Entity lookup**: <10ms (indexed by user_id + name)
- **Relationship traversal**: <50ms for depth 2
- **Context retrieval**: <100ms including related entities

### Optimization Tips

1. **Batch operations**:
   ```python
   # Bad: Generate embeddings one by one
   for text in texts:
       embedding = await embedding_service.generate_embedding(text)

   # Good: Batch embedding generation
   embeddings = await embedding_service.generate_embeddings_batch(texts)
   ```

2. **Cache preferences**:
   ```python
   # Cache user preferences in memory
   user_prefs_cache = {}

   async def get_cached_preferences(db, user_id):
       if user_id not in user_prefs_cache:
           prefs = await get_user_preferences(db, user_id)
           user_prefs_cache[user_id] = prefs
       return user_prefs_cache[user_id]
   ```

3. **Limit graph traversal depth**:
   ```python
   # Limit relationship depth to avoid expensive queries
   context = await kg_service.get_entity_context(
       db, user_id, entity_id,
       max_depth=2  # Don't go deeper than 2 levels
   )
   ```

---

## Roadmap

### Planned Enhancements

1. **Memory Deduplication**:
   - Detect and merge duplicate memories
   - Use embedding similarity to identify near-duplicates

2. **Advanced Entity Extraction**:
   - Use LLM to extract entities from memory content
   - NER (Named Entity Recognition) integration
   - Automatic relationship inference

3. **Memory Summarization**:
   - Periodically summarize old memories
   - Store summaries, archive raw memories
   - Reduce storage costs while preserving knowledge

4. **Adaptive Customization**:
   - Learn user preferences from behavior
   - Adjust settings automatically
   - A/B test different configurations

5. **Multi-modal Memory**:
   - Support image embeddings (CLIP)
   - Audio transcription + embedding
   - Video content indexing

---

## References

- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **pgvector**: https://github.com/pgvector/pgvector
- **HNSW Algorithm**: https://arxiv.org/abs/1603.09320
- **ARQ Background Jobs**: https://arq-docs.helpmanual.io/

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Maintained By**: Delight Team
