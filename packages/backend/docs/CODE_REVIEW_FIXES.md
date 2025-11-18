# Code Review - Critical Fixes Required

## Priority Fixes

### 1. HIGH: Fix SQLAlchemy Query Pattern in ModelRouter

**File**: `app/services/model_router.py:123`

**Current Code (WRONG)**:
```python
async def get_user_preferences(self, db: AsyncSession, user_id: UUID):
    result = await db.execute(
        db.query(AgentPreferences).filter(AgentPreferences.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

**Fixed Code**:
```python
from sqlalchemy import select

async def get_user_preferences(self, db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(AgentPreferences).where(AgentPreferences.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

**Reason**: `db.query()` is sync API, not compatible with async AsyncSession.

---

### 2. MEDIUM: Add Index on accessed_at Column

**File**: `app/db/migrations/versions/005_create_agent_prefs_and_knowledge_graph.py`

**Add to `upgrade()` function, after line 93**:
```python
# Add index for LRU tracking and hybrid search sorting
op.create_index("ix_memories_accessed_at", "memories", ["accessed_at"])
```

**Reason**: Hybrid search sorts by `accessed_at`, memory pruning uses it for LRU tracking.

**Note**: This index might already exist from migration 003 (line 80). Verify before adding.

---

### 3. MEDIUM: Robust Redis URL Parsing

**File**: `app/workers/memory_pruner.py:177`

**Current Code (FRAGILE)**:
```python
redis_settings = RedisSettings(
    host=settings.REDIS_URL.split("://")[-1].split(":")[0] if settings.REDIS_URL else "localhost",
    port=int(settings.REDIS_URL.split(":")[-1]) if settings.REDIS_URL and ":" in settings.REDIS_URL.split("://")[-1] else 6379,
)
```

**Fixed Code**:
```python
from urllib.parse import urlparse

def parse_redis_url(url: str) -> tuple:
    """Parse Redis URL into host and port"""
    if not url:
        return ("localhost", 6379)

    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    return (host, port)

# Usage:
redis_host, redis_port = parse_redis_url(settings.REDIS_URL) if settings.REDIS_URL else ("localhost", 6379)
redis_settings = RedisSettings(host=redis_host, port=redis_port)
```

**Reason**: Handles complex URLs with auth, paths, etc.

---

## Advisory Improvements (Low Priority)

### 4. Add Input Validation Limits

**Files**: All API endpoints accepting text input

**Add to schemas**:
```python
# In MemoryCreate, KnowledgeEntityCreate, etc.
content: str = Field(
    ...,
    min_length=1,
    max_length=10000,  # Already present ✓
    description="..."
)
```

**Action**: Verify all text fields have max_length to prevent DoS.

---

### 5. Document Placeholder Implementations

**Files**:
- `app/services/validation_safety.py:verify_fact()`
- `app/services/validation_safety.py:check_rate_limit()`
- `app/services/knowledge_graph_service.py:extract_entities_from_memory()`

**Add TODO comments**:
```python
async def verify_fact(self, fact: str, require_sources: bool = False):
    """
    TODO: Implement actual fact verification
    This would use:
    1. Web search for corroborating sources
    2. LLM-based fact checking
    3. Knowledge graph cross-referencing
    """
    # Placeholder implementation
    ...
```

**Reason**: Make it clear these are not production-ready.

---

### 6. Add Batch Size Limits

**File**: `app/services/embedding_service.py:generate_embeddings_batch()`

**Current**:
```python
async def generate_embeddings_batch(
    self, texts: List[str], batch_size: int = 100
):
```

**Add validation**:
```python
async def generate_embeddings_batch(
    self, texts: List[str], batch_size: int = 100
):
    if batch_size > 2048:
        raise ValueError("batch_size cannot exceed 2048 (OpenAI limit)")
    ...
```

---

## Testing Requirements

Before production:

1. **Unit Tests**:
   - [ ] Test EmbeddingService with mocked OpenAI API
   - [ ] Test MemoryService hybrid search algorithm
   - [ ] Test KnowledgeGraphService entity/relationship CRUD
   - [ ] Test ModelRouter complexity estimation
   - [ ] Test ValidationSafety content filtering

2. **Integration Tests**:
   - [ ] Test memory API endpoints with real database
   - [ ] Test knowledge graph API with entity creation and querying
   - [ ] Test agent preferences creation and updates
   - [ ] Test background worker memory pruning

3. **E2E Tests**:
   - [ ] Test complete memory creation → search → retrieval flow
   - [ ] Test knowledge graph building from memories
   - [ ] Test preferences affecting model selection

---

## Performance Benchmarks to Run

Before production:

1. **Vector Search Performance**:
   - Measure p95 latency for semantic search with 1K, 10K, 100K memories
   - Verify HNSW index effectiveness

2. **Embedding Generation**:
   - Measure throughput for batch embedding generation
   - Test retry logic under API rate limits

3. **Memory Pruning**:
   - Test pruning performance with 10K, 100K, 1M memories
   - Verify no lock contention during pruning

4. **Knowledge Graph Traversal**:
   - Measure query time for depth-2 and depth-5 traversals
   - Test with 1K, 10K entities

---

## Security Hardening

Before production:

1. **Rate Limiting**:
   - [ ] Implement Redis-based rate limiting
   - [ ] Add per-user, per-endpoint limits
   - [ ] Return 429 Too Many Requests when exceeded

2. **Input Sanitization**:
   - [ ] Add HTML/JS sanitization if displaying user content
   - [ ] Validate all UUIDs before database queries
   - [ ] Add request size limits (max body size)

3. **API Security**:
   - [ ] Add CORS configuration
   - [ ] Consider adding API versioning headers
   - [ ] Add request logging for audit trail

---

## Next Steps

1. **Immediate** (before any testing):
   - Fix HIGH priority items (#1, #2)
   - Fix MEDIUM priority item (#3)

2. **Short-term** (next sprint):
   - Add comprehensive tests
   - Implement rate limiting
   - Run performance benchmarks

3. **Long-term**:
   - Replace placeholder implementations
   - Add monitoring and alerting
   - Implement adaptive customization

---

**Review Date**: 2025-11-18
**Reviewer**: Claude (AI Code Review)
**Status**: CHANGES REQUESTED (3 medium/high priority fixes)
