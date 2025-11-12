# Epic Technical Specification: Companion & Memory System

Date: 2025-11-11 (Updated: 2025-11-12 - Story order revised for vertical slice approach)
Author: Claude (with Jack)
Epic ID: 2
Status: Draft - Ready for Implementation

---

## Overview

Epic 2 builds the emotionally intelligent AI companion (Eliza) with a 3-tier memory system that enables contextual, empathetic conversations. This epic delivers the core differentiator of Delight: an AI companion that remembers your context, understands your emotional state, and helps you balance ambition with well-being.

The companion system implements four key architectural patterns:

1. **3-Tier Memory Architecture**: Personal (long-term identity), Project (goals), Task (short-term, pruned)
2. **LangGraph State Machine**: Stateful agent orchestration with memory-aware reasoning
3. **Hybrid Search**: Vector similarity + time decay + access frequency
4. **Emotional Intelligence**: Emotion detection informing response strategies

This epic aligns with the Product Brief's vision of "emotionally aware AI coaching" by ensuring Eliza can:
- Remember user preferences, stressors, and patterns across conversations
- Detect when users are overwhelmed and offer circuit breakers instead of pushing
- Balance between productivity coaching and well-being support
- Build trust through consistent, context-aware interactions

## Implementation Strategy: Vertical Slice Approach (REVISED 2025-11-12)

**IMPORTANT: Story order revised to follow vertical slice pattern**

Instead of building horizontal layers (infrastructure first, then UI), we build **vertical slices** (working features end-to-end):

### Story Sequence (Revised):
1. **Story 2.1**: Database foundation (pgvector, memory tables) ✅ COMPLETE
2. **Story 2.5**: Chat UI + Essential Memory (VERTICAL SLICE - do this FIRST)
   - Working chat interface with SSE streaming
   - Essential memory operations inline (not extracted yet)
   - All test scenarios working (venting, goals, memory recall)
   - **Validates**: Memory patterns, search quality, UX flow
3. **Story 2.2**: Memory Service Extraction (REFACTORED - do this SECOND)
   - Extract proven memory operations into proper service
   - Add hybrid search (time decay, frequency boost)
   - Add pruning worker
   - **Benefits from**: Learnings from Story 2.5
4. **Story 2.3**: Full Eliza Agent (LangGraph)
5. **Story 2.4**: Enhanced Chat API (advanced features)
6. **Story 2.6**: Emotion Detection

### Why This Order?

**❌ Original Plan (2.2 → 2.5):**
- Build memory service blindly (can't test until UI exists)
- Discover UX issues late
- Hard to iterate on architecture

**✅ Revised Plan (2.5 → 2.2):**
- See memory working immediately in browser
- Test all scenarios (venting, tasks, recall) right away
- Refine architecture based on real usage
- Faster feedback loop, lower risk

### Story 2.2 Status Note (2025-11-12)

Story 2.2 is **being refactored** to focus on service extraction and enhancements after Story 2.5 validates the patterns. The current draft (14 ACs) will be simplified to:
- Extract memory operations from Story 2.5 into proper service
- Add hybrid search based on Story 2.5 learnings
- Add pruning worker
- Advanced features (goal-based search, user priorities) may move to Story 2.2b

See `docs/stories/2-5-companion-chat-ui-with-essential-memory.md` for the vertical slice implementation.

## Objectives and Scope

### In Scope

1. **Memory Foundation (Story 2.1)** ✅ COMPLETE
   - PostgreSQL pgvector integration for vector storage
   - 3-tier memory tables (personal, project, task)
   - HNSW index for fast similarity search

2. **Working Chat with Essential Memory (Story 2.5)** ← DO THIS FIRST
   - Chat UI with SSE streaming
   - Essential memory operations (inline, not service yet)
   - Basic semantic search (vector similarity only)
   - All test scenarios working
   - **Output**: Working chat you can test in browser!

3. **Memory Service Extraction (Story 2.2)** ← DO THIS SECOND
   - Extract memory service from Story 2.5
   - Add hybrid search (semantic + time + frequency)
   - Add pruning worker (30-day retention for task memories)
   - Optimize based on Story 2.5 learnings

4. **Eliza Agent (Story 2.3)**
   - LangGraph state machine with 5 nodes
   - System prompt emphasizing empathy and emotional intelligence
   - Memory-aware context retrieval (strategic querying by tier)
   - Conversation state management across sessions

5. **Enhanced Chat API (Story 2.4)**
   - Advanced features and optimizations
   - Conversation management endpoints
   - Performance tuning

6. **Emotional State Detection (Story 2.6)**
   - Open source RoBERTa emotion model (7 emotions)
   - Integration with Eliza agent for emotion-aware responses
   - User emotional state tracking in database
   - Circuit breaker protocol for overwhelm detection

### Out of Scope (Future Stories)

- **Multiple Character Personas** (Story 2.7 - future epic)
  - Lyra, Thorne, Elara characters
  - Character-initiated interactions
  - Per-character memory namespaces
- **Advanced Memory Features**
  - Memory consolidation/summarization
  - Cross-user memory insights
  - Memory export/import
- **Voice/Audio**
  - Voice notes
  - Text-to-speech responses
- **Narrative Integration** (Epic 4 dependency)
  - Story-driven conversations
  - Hidden quest unlocks from conversations

## System Architecture Alignment

This epic implements the AI orchestration layer of the architecture:

### Technology Stack

**AI & LLM:**
- **LangGraph**: Stateful agent orchestration (MIT license)
- **LangChain**: LLM integration and abstractions
- **OpenAI GPT-4o-mini**: Primary conversational model ($0.15/$0.60 per 1M tokens)
- **OpenAI text-embedding-3-small**: Embeddings for memory (1536 dim, $0.02/1M tokens)
- **cardiffnlp/roberta-emotion**: Self-hosted emotion detection (Apache 2.0 license)

**Memory & Storage:**
- **PostgreSQL pgvector**: Vector storage extension (unified with main DB)
- **HNSW index**: Hierarchical Navigable Small World for fast similarity search
- **JSONB**: Metadata storage for flexible context

**Streaming:**
- **Server-Sent Events (SSE)**: One-way streaming from AI to client
- **OpenAI Streaming API**: Token-by-token response generation

**Background Jobs:**
- **ARQ**: Async Redis queue for memory pruning, future character initiation

### Cost Management (Target: $0.50/user/day)

**Epic 2 AI Cost Breakdown (per user per day):**

| Component | Usage | Model | Cost |
|-----------|-------|-------|------|
| Chat conversations | ~10K tokens in + 5K tokens out | GPT-4o-mini | $0.001 + $0.003 = $0.004 |
| Memory embeddings | ~2K tokens/day | text-embedding-3-small | $0.00004 |
| Emotion detection | ~20 messages/day | Self-hosted (free) | $0 |
| **Total Epic 2** | | | **~$0.004/user/day** |

**Remaining budget for other epics:** $0.496/user/day (well within target)

### Data Flow

```
User Message
    ↓
[Clerk Auth] → Validate session
    ↓
[Chat API] → Create/retrieve conversation
    ↓
[Eliza Agent] → LangGraph State Machine
    ├─ receive_input: Parse message, detect emotion
    ├─ recall_context: Query 3-tier memory (vector search)
    ├─ reason: LLM processes with memory context
    ├─ respond: Generate empathetic response (streaming)
    └─ store_memory: Save conversation to task memory
    ↓
[SSE Stream] → Token-by-token to frontend
    ↓
[Frontend] → Display with animations
    ↓
[Memory Service] → Update accessed_at, increment access_count
```

## Detailed Design

### Services and Modules

| Service/Module | Responsibility | Inputs | Outputs | Location |
|----------------|---------------|---------|---------|----------|
| **Memory Service** | Add memories, query with hybrid search, prune old memories | user_id, content, memory_type | List[Memory], Memory | `app/services/memory_service.py` |
| **Embedding Service** | Generate embeddings, cache results | text | List[float] (1536-dim) | `app/services/embedding_service.py` |
| **Emotion Service** | Detect emotions from text | text | Dict[emotion: score] | `app/services/emotion_service.py` |
| **Eliza Agent** | Orchestrate conversation with memory | user_id, message, context | response_text | `app/agents/eliza_agent.py` |
| **Companion API** | Handle chat requests, stream responses | ChatRequest | SSE Stream | `app/api/v1/companion.py` |
| **Memory Pruner** | Background job to prune old task memories | None | int (deleted count) | `app/workers/memory_pruner.py` |

### Data Models and Contracts

#### Memory Tables (PostgreSQL)

```sql
-- Enum for memory types
CREATE TYPE memory_type AS ENUM ('personal', 'project', 'task');

-- Main memories table with vector embeddings
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    memory_type memory_type NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- pgvector column
    metadata JSONB,  -- {emotion: 'joy', source: 'conversation', stressor: true}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX ix_memories_user_id ON memories(user_id);
CREATE INDEX ix_memories_memory_type ON memories(memory_type);
CREATE INDEX ix_memories_created_at ON memories(created_at);

-- HNSW index for fast vector similarity search
CREATE INDEX ix_memories_embedding ON memories
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Memory collections (optional grouping)
CREATE TABLE memory_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    collection_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_memory_collections_user_id ON memory_collections(user_id);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]',  -- [{role, content, timestamp}]
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_conversations_user_id ON conversations(user_id);
CREATE INDEX ix_conversations_updated_at ON conversations(updated_at);
```

#### SQLAlchemy Models

```python
# app/models/memory.py
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum as PyEnum
from sqlalchemy import Column, Text, ForeignKey, Enum, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.models.base import Base

class MemoryType(str, PyEnum):
    PERSONAL = "personal"  # Long-term identity, preferences, patterns
    PROJECT = "project"    # Goals, plans, progress snapshots
    TASK = "task"          # Short-term mission context (pruned after 30 days)

class Memory(Base):
    __tablename__ = "memories"

    id: UUID = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: UUID = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_type: MemoryType = Column(Enum(MemoryType), nullable=False, index=True)
    content: str = Column(Text, nullable=False)
    embedding: Optional[list[float]] = Column(Vector(1536), nullable=True)
    metadata: Optional[Dict[str, Any]] = Column(JSONB, nullable=True, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    accessed_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="memories")

class Conversation(Base):
    __tablename__ = "conversations"

    id: UUID = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: UUID = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    messages: list[dict] = Column(JSONB, nullable=False, default=list)
    started_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now(), index=True)

    user = relationship("User", back_populates="conversations")
```

Update `app/models/user.py`:
```python
# Add to User model
memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
```

#### Pydantic Schemas

```python
# app/schemas/memory.py
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.memory import MemoryType

class MemoryCreate(BaseModel):
    memory_type: MemoryType
    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None

class MemoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    accessed_at: datetime

    class Config:
        from_attributes = True

# app/schemas/companion.py
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str

class EmotionState(BaseModel):
    dominant_emotion: str
    scores: Dict[str, float]
    timestamp: datetime
```

### APIs and Interfaces

#### Companion Chat Endpoints

```
POST /api/v1/companion/chat
Description: Initiate a chat session with Eliza
Auth: Required (Clerk session)
Request Body:
{
  "message": "I'm feeling overwhelmed with my goals",
  "conversation_id": "uuid-or-null",  // null for new conversation
  "context": {
    "current_mission_id": "uuid",  // optional
    "emotional_state": "stressed"  // optional
  }
}
Response:
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Stream started"
}
```

```
GET /api/v1/companion/stream/{conversation_id}
Description: SSE stream for Eliza's response
Auth: Required (Clerk session)
Query Params: ?token={clerk_token}
Response: Server-Sent Events (text/event-stream)

Event Format:
data: {"type": "token", "content": "I ", "conversation_id": "..."}
data: {"type": "token", "content": "hear ", "conversation_id": "..."}
data: {"type": "token", "content": "you", "conversation_id": "..."}
data: {"type": "complete", "conversation_id": "..."}

Error Format:
data: {"type": "error", "message": "Error description"}
```

```
GET /api/v1/companion/history?limit=50
Description: Get conversation history
Auth: Required (Clerk session)
Response:
{
  "conversations": [
    {
      "id": "uuid",
      "messages": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
      ],
      "started_at": "2025-11-11T10:00:00Z",
      "updated_at": "2025-11-11T10:05:00Z"
    }
  ]
}
```

#### Memory Management Endpoints (Internal/Future)

```
POST /api/v1/memory
Description: Manually add a memory (internal use)
Auth: Required (Clerk session)
Request Body:
{
  "memory_type": "personal",
  "content": "I prefer working in the morning",
  "metadata": {"source": "preferences"}
}

GET /api/v1/memory/search?q=morning&type=personal&limit=10
Description: Search memories (debugging/future feature)
Auth: Required (Clerk session)
Response: List[MemoryResponse]
```

### Workflows and Sequencing

#### Chat Flow (Complete User Journey)

```
1. User Types Message in Frontend
   ├─ Input: "I'm feeling overwhelmed with my goals"
   └─ Component: CompanionChat.tsx

2. Frontend: Send Chat Request
   ├─ POST /api/v1/companion/chat
   │  └─ Headers: Authorization: Bearer {clerk_token}
   └─ Receive: {conversation_id: "uuid"}

3. Backend: Create/Retrieve Conversation
   ├─ Validate Clerk session token
   ├─ Get or create Conversation record
   ├─ Append user message to conversation.messages
   └─ Return conversation_id

4. Frontend: Establish SSE Connection
   ├─ new EventSource(`/api/v1/companion/stream/{conversation_id}?token={clerk_token}`)
   └─ Listen for: onmessage, onerror

5. Backend: Initialize Eliza Agent
   ├─ MemoryService(db)
   ├─ ElizaAgent(memory_service)
   └─ agent.chat(user_id, message, context)

6. LangGraph State Machine Execution
   ├─ Node: receive_input
   │  ├─ Parse user message
   │  ├─ Detect emotion (Story 2.6)
   │  └─ Update state: {emotional_state: {...}}
   │
   ├─ Node: recall_context
   │  ├─ Query personal memories (always, top 5)
   │  ├─ Query project memories (if goal-related keywords)
   │  ├─ Query task memories (recent context, top 3)
   │  └─ Update state: {retrieved_memories: [...]}
   │
   ├─ Node: reason
   │  ├─ Build context from memories
   │  ├─ Construct messages: [SystemMessage, context, conversation]
   │  ├─ LLM: ChatOpenAI.astream(messages)  # Streaming!
   │  └─ Update state: {messages: [...AIMessage]}
   │
   ├─ Node: respond
   │  ├─ Response already in state.messages
   │  └─ Stream tokens via SSE
   │
   └─ Node: store_memory
      ├─ Extract last exchange (human + AI)
      ├─ memory_service.add_memory(type=TASK, content=exchange)
      └─ Update conversation.messages in DB

7. SSE Streaming to Frontend
   ├─ For each token from LLM:
   │  └─ yield f"data: {json.dumps({type: 'token', content: word})}\n\n"
   ├─ On complete:
   │  └─ yield f"data: {json.dumps({type: 'complete'})}\n\n"
   └─ On error:
      └─ yield f"data: {json.dumps({type: 'error', message: str(e)})}\n\n"

8. Frontend: Update UI
   ├─ onmessage: Append token to AI message
   ├─ Smooth scrolling to bottom
   ├─ Loading state management
   └─ oncomplete: Enable input field
```

#### Memory Hybrid Search Algorithm

```
1. User Query: "I'm stressed about my goals"
   ├─ Generate query embedding (OpenAI text-embedding-3-small)
   └─ Query: vector(1536)

2. Base SQL Query
   ├─ SELECT * FROM memories
   ├─ WHERE user_id = $1
   ├─ AND memory_type IN ['personal', 'project']  -- Strategic filtering
   ├─ ORDER BY embedding <=> $query_vector  -- Cosine distance
   └─ LIMIT 20  -- Get more than needed for post-processing

3. Time Decay Scoring
   ├─ For each memory:
   │  ├─ days_since_access = (now - memory.accessed_at).days
   │  ├─ time_boost = 1 + log(1 + days_since_access + 1)^-1
   │  ├─ access_count = memory.metadata.get('access_count', 1)
   │  ├─ frequency_boost = 1 + (log(access_count) * 0.1)
   │  └─ final_score = similarity * time_boost * frequency_boost
   └─ Sort by final_score descending

4. Filter and Return
   ├─ Filter: final_score >= 0.7  -- Similarity threshold
   ├─ Take top 10
   ├─ Update accessed_at for all retrieved memories
   └─ Increment access_count in metadata
```

#### Memory Pruning (Background Worker)

```
1. ARQ Scheduler
   ├─ Cron: Daily at 2:00 AM
   └─ Trigger: prune_task_memories()

2. Memory Pruner Worker
   ├─ Query: SELECT * FROM memories
   │         WHERE memory_type = 'task'
   │         AND created_at < (NOW() - INTERVAL '30 days')
   ├─ Delete: All matching memories
   ├─ Log: "Pruned {count} old task memories"
   └─ Commit

3. Retention Policy
   ├─ Personal: Never pruned (long-term identity)
   ├─ Project: Never pruned (goal context)
   └─ Task: 30-day retention (short-term mission context)
```

## Non-Functional Requirements

### Performance

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Memory Query (p95)** | < 100ms | Fast recall for conversation flow |
| **Embedding Generation** | < 200ms | OpenAI API latency + network |
| **LLM First Token (p95)** | < 1s | Streaming starts quickly |
| **LLM Complete Response** | < 5s | Full response for typical message |
| **Vector Index Build** | < 5s per 10K memories | HNSW index efficient |
| **SSE Connection Latency** | < 50ms | Low overhead streaming |

**Optimization Strategies:**
- Cache embeddings for identical content (SHA-256 hash)
- Use HNSW index (m=16, ef_construction=64) for O(log n) search
- Limit conversation history to last 10 messages in context
- Prune task memories to keep memory table lean

### Security

1. **Authentication & Authorization**
   - All endpoints require Clerk session token validation
   - User can only access their own memories and conversations
   - API keys (OpenAI) stored in environment variables, not database

2. **Data Privacy**
   - User memories never leave Delight infrastructure (except OpenAI API calls)
   - Emotion detection model self-hosted (no external API for sensitive data)
   - Conversation history encrypted at rest (PostgreSQL encryption)
   - SSE connections require valid session token in query param

3. **API Security**
   - Rate limiting on chat endpoint: 60 requests/minute per user
   - Input validation: Max message length 5000 characters
   - SQL injection prevention: Parameterized queries (SQLAlchemy)
   - CORS configured to allow only frontend domain

4. **Prompt Injection Prevention**
   - System prompts are not user-configurable
   - User messages sanitized before embedding/LLM calls
   - LLM outputs parsed and validated before storage

### Reliability/Availability

1. **Error Handling**
   - **OpenAI API Failures**: Retry with exponential backoff (3 attempts)
   - **Database Failures**: Connection pool retries, graceful degradation
   - **SSE Disconnections**: Client auto-reconnects, server resumes from last token
   - **Embedding Failures**: Store memory without embedding, retry async

2. **Graceful Degradation**
   - If memory query fails: Continue conversation without memory context
   - If emotion detection fails: Default to neutral emotion state
   - If streaming fails: Return complete response via HTTP fallback

3. **Data Consistency**
   - Conversation messages stored in JSONB transactions
   - Memory creation atomic: embedding + metadata + content
   - Worker failures don't block user interactions

4. **Monitoring**
   - Sentry alerts on OpenAI API failures (> 5% error rate)
   - Track SSE disconnection rate (alert if > 10%)
   - Monitor memory query latency (alert if p95 > 200ms)
   - Log LLM token usage for cost tracking

### Observability

1. **Logging**
   - Structured JSON logs with context: user_id, conversation_id, agent_node
   - Log levels: DEBUG (dev), INFO (conversation events), ERROR (failures)
   - Sensitive data masked: message content abbreviated in logs

2. **Metrics**
   - Chat API: request count, response time, error rate
   - Memory queries: query time, result count, cache hit rate
   - LLM calls: token count (input/output), cost per request
   - SSE streams: connection count, duration, token rate

3. **Tracing** (Future)
   - OpenTelemetry spans for full request lifecycle
   - Trace: API → Agent → Memory → LLM → SSE
   - Track memory retrieval impact on response quality

## Dependencies and Integrations

### Python Dependencies (Backend)

```toml
# pyproject.toml additions for Epic 2
[tool.poetry.dependencies]
# AI & LLM
langchain = "^0.1.0"
langgraph = "^0.0.20"
langchain-openai = "^0.0.5"
langchain-postgres = "^0.0.3"
openai = "^1.10.0"

# Vector & Embeddings
pgvector = "^0.2.4"

# Emotion Detection (Story 2.6)
transformers = "^4.36.0"
torch = "^2.1.0"  # For emotion model inference

# Already installed
fastapi = "^0.109.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.25"}
asyncpg = "^0.29.0"
redis = "^5.0.1"
arq = "^0.26.0"
```

### Frontend Dependencies

```json
// package.json additions for Epic 2
{
  "dependencies": {
    "framer-motion": "^11.0.0"  // For chat animations
    // Already installed: next, react, @clerk/nextjs
  }
}
```

### External Service Integrations

1. **OpenAI API**
   - **Purpose**: LLM (GPT-4o-mini) and embeddings (text-embedding-3-small)
   - **Configuration**: `OPENAI_API_KEY` environment variable
   - **Cost**: ~$0.004/user/day (within budget)
   - **Retry Strategy**: 3 attempts with exponential backoff
   - **Monitoring**: Track API call success rate, latency, token usage

2. **Clerk Authentication** (from Epic 1)
   - **Purpose**: Session token validation for API access
   - **Integration**: `get_current_user` dependency in FastAPI
   - **Already configured** in Epic 1

3. **Hugging Face (Emotion Model)**
   - **Purpose**: Download emotion classification model
   - **Model**: `cardiffnlp/twitter-roberta-base-emotion-multilingual-latest`
   - **Hosting**: Self-hosted on backend (CPU inference ~50ms)
   - **Fallback**: If model load fails, default to neutral emotion

## Acceptance Criteria (Authoritative)

### AC1: Memory System Operational (Stories 2.1-2.2)

- **Given** migrations are applied and OpenAI API key is configured
- **When** a memory is added via MemoryService
- **Then**:
  - Memory is stored in `memories` table with correct type
  - Embedding is generated (1536 dimensions)
  - Hybrid search returns relevant memories sorted by combined score
  - Personal memories always retrieved (top 5)
  - Project memories retrieved when query contains goal keywords
  - Task memories retrieved for recent context
  - Old task memories (>30 days) are pruned by background worker

### AC2: Eliza Agent Functional (Story 2.3)

- **Given** MemoryService and LangGraph agent are initialized
- **When** user sends a message via agent.chat()
- **Then**:
  - LangGraph state machine executes all 5 nodes (receive_input, recall_context, reason, respond, store_memory)
  - Agent queries personal memories for user context
  - Agent queries project/task memories based on message content
  - LLM generates empathetic response using memory context
  - Conversation exchange is stored as task memory
  - Response acknowledges user's emotional state
  - Agent uses "Control Triage" (controllable vs uncontrollable stressors)
  - Agent applies "Energy-Based Push" (validates before pushing)

### AC3: Chat API with SSE Streaming (Story 2.4)

- **Given** Clerk session is valid and backend is running
- **When** frontend sends POST /api/v1/companion/chat
- **Then**:
  - Conversation is created/retrieved in database
  - User message is appended to conversation.messages
  - conversation_id is returned
  - SSE stream endpoint is available
  - Tokens stream in real-time (< 50ms per token)
  - Complete message event sent on finish
  - AI response is saved to conversation.messages
  - Error events sent if LLM/memory fails

### AC4: Chat UI with Streaming (Story 2.5)

- **Given** user is authenticated and viewing /companion page
- **When** user types message and clicks Send
- **Then**:
  - Message appears immediately in chat history
  - Loading indicator shows (typing dots animation)
  - AI response streams in token-by-token
  - Message animations are smooth (Framer Motion)
  - Auto-scroll to bottom as tokens arrive
  - Mobile responsive (works on <768px screens)
  - Accessible (keyboard navigation, ARIA labels)
  - Input field disabled during loading
  - Connection errors show user-friendly message

### AC5: Emotional State Detection (Story 2.6)

- **Given** emotion model is loaded and user sends message
- **When** message contains emotional content (e.g., "I'm overwhelmed")
- **Then**:
  - Emotion scores returned for 7 emotions (joy, anger, sadness, fear, love, surprise, neutral)
  - Dominant emotion identified (highest score)
  - Emotional state stored in conversation metadata
  - Eliza's response adapts to detected emotion:
    - **Overwhelm/Fear**: Offers circuit breaker (20-min walk, not push)
    - **Sadness/Anger**: Validates feeling, suggests breaking down tasks
    - **Joy/Love**: Celebrates wins, encourages momentum
    - **Neutral**: Normal conversational flow
  - User emotional state tracked in `user_preferences.current_emotional_state` JSONB

### AC6: Integration Testing

- **Given** full Epic 2 implementation is complete
- **When** running end-to-end test scenario
- **Then**:
  - User can register (Epic 1) and access /companion page
  - First message creates new conversation
  - Eliza responds with empathetic, contextual reply
  - Second message uses memory from first exchange
  - Stressors mentioned are stored in personal memory
  - Circuit breaker suggested when overwhelm detected
  - Conversation history persists across page refreshes
  - Background worker prunes task memories after 30 days

## Traceability Mapping

| AC | Spec Section | Components/APIs | Test Idea |
|----|--------------|----------------|-----------|
| AC1 | Memory System | MemoryService, PostgreSQL pgvector, HNSW index | Test: Add memory, query by similarity, verify pruning |
| AC2 | Eliza Agent | ElizaAgent, LangGraph, ChatOpenAI | Test: Send message, verify memory retrieval, check response |
| AC3 | Chat API | POST /api/v1/companion/chat, SSE streaming | Test: Mock user message, verify SSE events, check DB storage |
| AC4 | Chat UI | CompanionChat.tsx, EventSource, Framer Motion | Test: Playwright E2E test for full chat flow |
| AC5 | Emotion Detection | EmotionService, cardiffnlp/roberta model | Test: Send emotional messages, verify emotion scores |
| AC6 | Full Integration | All components | Test: Complete user journey with multiple conversations |

## Risks, Assumptions, Open Questions

### Risks

1. **Risk**: OpenAI API rate limits or outages
   - **Mitigation**: Implement retry logic, consider fallback to cached responses, monitor API health
   - **Impact**: High (blocks all conversations)

2. **Risk**: pgvector performance degrades with large memory tables (>100K memories per user)
   - **Mitigation**: HNSW index optimized, regular pruning, consider sharding if needed
   - **Impact**: Medium (affects query speed)

3. **Risk**: LangGraph streaming integration complex (not natively supported)
   - **Mitigation**: Use OpenAI streaming API directly within reason node, chunk responses
   - **Impact**: Low (workaround available)

4. **Risk**: Emotion model inference slow on CPU
   - **Mitigation**: Load model once on startup, cache results, consider GPU in production
   - **Impact**: Low (50ms acceptable for MVP)

5. **Risk**: SSE connections drop on mobile networks
   - **Mitigation**: Auto-reconnect logic, fallback to HTTP polling, resume from last token
   - **Impact**: Medium (UX degradation)

### Assumptions

1. **Assumption**: Users will have <10K memories per user (reasonable for MVP)
   - **Validation**: Monitor memory growth, implement limits if needed

2. **Assumption**: GPT-4o-mini quality sufficient for empathetic conversations
   - **Validation**: User feedback, compare with GPT-4o if quality issues arise

3. **Assumption**: Self-hosted emotion model provides adequate accuracy
   - **Validation**: Compare with Hume AI or GPT-4 emotion detection

4. **Assumption**: SSE works across all browsers and networks
   - **Validation**: Test on mobile, add HTTP fallback if needed

5. **Assumption**: 30-day retention for task memories balances memory and context
   - **Validation**: User feedback, adjust retention period if users want longer history

### Open Questions

1. **Question**: Should we implement memory consolidation (summarize old memories)?
   - **Decision Needed**: After MVP, based on memory growth rate
   - **Timeline**: Epic 3 or later

2. **Question**: How to handle multi-turn context (long conversations)?
   - **Decision**: Limit to last 10 messages in LLM context, summarize older messages
   - **Timeline**: Implement in Story 2.3

3. **Question**: Should emotion detection run on every message or selectively?
   - **Decision**: Run on every message for MVP (fast enough), optimize later
   - **Timeline**: Story 2.6

4. **Question**: How to version control Eliza's system prompt?
   - **Decision**: Store prompt in code (not DB) for version control
   - **Timeline**: Story 2.3

5. **Question**: Should we support voice input/output in Epic 2?
   - **Decision**: No, defer to future epic (focus on text chat for MVP)
   - **Timeline**: Post-MVP

## Test Strategy Summary

### Test Levels

1. **Unit Tests**
   - **Memory Service**: Test add_memory, query_memories, time decay logic
   - **Embedding Service**: Test embedding generation, caching
   - **Eliza Agent**: Mock LLM, test state transitions, memory retrieval
   - **Emotion Service**: Test emotion detection with sample texts
   - **Target Coverage**: 80%+ for services and agents

2. **Integration Tests**
   - **Memory + PostgreSQL**: Test vector search, HNSW index performance
   - **Agent + Memory**: Test full conversation flow with real DB
   - **Chat API + SSE**: Test streaming with mock EventSource
   - **Clerk Auth + Chat API**: Test session validation

3. **End-to-End Tests**
   - **Playwright**: Full user journey (sign in → chat → memory recall)
   - **SSE Streaming**: Test token-by-token display
   - **Mobile Responsive**: Test on <768px viewport
   - **Accessibility**: Test keyboard navigation, screen reader

### Test Frameworks

- **Backend**: pytest, pytest-asyncio, httpx (async test client)
- **Frontend**: Playwright (E2E), React Testing Library (components)
- **Database**: pytest fixtures with transactional rollback
- **Mocking**: unittest.mock for OpenAI API, LangChain LLM

### Critical Test Scenarios

1. **First Conversation (Cold Start)**
   - Test: User sends first message (no memories)
   - Expected: Eliza responds warmly, introduces herself
   - Verify: Personal memory created from conversation

2. **Memory Recall Across Sessions**
   - Test: User mentions "I'm stressed" in message 1, then "stressed" in message 5
   - Expected: Eliza references earlier stressor
   - Verify: Personal memory retrieved with stressor metadata

3. **Overwhelm Detection + Circuit Breaker**
   - Test: User sends long message with multiple stressors + fear emotion
   - Expected: Eliza suggests 20-min walk (circuit breaker), not task push
   - Verify: Emotional state = fear, response includes non-work action

4. **SSE Connection Recovery**
   - Test: Disconnect SSE mid-stream, reconnect
   - Expected: Frontend reconnects, resumes from last token
   - Verify: No duplicate tokens, smooth UX

5. **Memory Pruning**
   - Test: Create 31-day-old task memory, run pruner
   - Expected: Task memory deleted, personal/project memories retained
   - Verify: Memory count reduced

### Continuous Integration

- **Pre-commit**: Ruff linting, Black formatting
- **CI Pipeline**:
  1. Install dependencies (Poetry, pnpm)
  2. Run backend unit tests (pytest)
  3. Run frontend E2E tests (Playwright)
  4. Build Docker images
  5. Deploy to staging (if on main branch)

### Manual Testing Checklist (Story 2.5)

- [ ] Sign in with Clerk
- [ ] Navigate to /companion page
- [ ] Send first message, verify Eliza responds
- [ ] Send second message, verify memory recall
- [ ] Test mobile responsive (Chrome DevTools)
- [ ] Test keyboard navigation (Tab, Enter)
- [ ] Test SSE disconnection (kill server mid-stream)
- [ ] Verify conversation persists across page refresh

## Post-Review Follow-ups

- **Story 2.1 (High)** – Verify HNSW index parameters (m=16, ef_construction=64) are optimal for 1536-dim vectors. Benchmark query performance with 1K, 10K, 100K memories.
- **Story 2.3 (High)** – Test LangGraph streaming integration. If native streaming not supported, implement workaround with OpenAI streaming API in reason node.
- **Story 2.4 (Medium)** – Implement SSE reconnection logic on frontend to handle mobile network drops gracefully.
- **Story 2.6 (Medium)** – Benchmark emotion model inference time on CPU. If >100ms, consider GPU or model quantization.

---

## Key Design Principles (From Case Study)

### 1. The Stressor Log (Memory Tier 1 - Personal)

**Implementation in Epic 2:**
- When emotion sensor detects high-intensity negative emotions (fear, sadness, anger) + long message, trigger "Stressor Ingest" mode
- Agent's `reason` node prompted to "summarize distinct problems or stressors in user's message"
- Store stressors in personal memory with metadata: `{stressor: true, emotion: 'fear', category: 'academic'}`
- Future conversations: `recall_context` retrieves stressors, Eliza references them: "Is this about the class registration and debt email, or something new?"

### 2. Control Triage (Technique in Reason Node)

**Implementation in Epic 2:**
- Eliza's system prompt includes: "Distinguish between controllable and uncontrollable stressors. Push gently on controllable, guide to acceptance on uncontrollable."
- Uncontrollable examples: "other people's feelings," "closed registration," "external events"
- Controllable examples: "assignments," "email responses," "internship applications"
- Agent action:
  - **Uncontrollable**: "We can't change that, so let's focus on what we can control."
  - **Controllable**: "Let's break this down into one small step."

### 3. Energy-Based Push (Balancing)

**Implementation in Epic 2:**
- Agent maintains `user_energy_level` variable informed by emotion sensor (Story 2.6)
- **High Energy** (joy, neutral): "You're on a roll! Let's use this momentum."
- **Low Energy** (sadness, fear): 80% validation + 20% "one small win"
- Response structure:
  1. Validate feeling: "That's completely valid."
  2. Offer circuit breaker: "Let's try a 20-min walk first."
  3. Micro-task: "Then just open the email, don't solve it."

### 4. Circuit Breaker (Anti-Cripple Protocol)

**Implementation in Epic 2:**
- **Trigger**: `(stressor_count > 5) AND (emotion == 'overwhelm' OR 'fear') AND (time_of_day > 20:00)`
- **Agent Action**: Primary goal shifts from Productivity → Preservation
- **Response**: "My analysis suggests forcing work now will be counterproductive. You mentioned you enjoy [activity from memory]. Let's schedule that first."
- Store in system prompt: "You have permission to suggest not working when user is overwhelmed."

---

**Epic 2 Technical Specification Complete**

This specification provides the comprehensive technical blueprint for implementing the Companion & Memory System. All stories (2.1-2.6) can be implemented following this design.

**Next Step**: Draft individual story files (2.1-2.6) using this spec as the foundation.
