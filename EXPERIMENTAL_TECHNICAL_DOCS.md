# Experimental Features - Technical Documentation

**Version:** 1.0.0
**Last Updated:** 2025-11-19
**Author:** Claude (AI Assistant)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend Components](#backend-components)
3. [Frontend Components](#frontend-components)
4. [API Reference](#api-reference)
5. [Data Flow](#data-flow)
6. [Method Index](#method-index)
7. [Debugging Guide](#debugging-guide)
8. [Known Issues & Solutions](#known-issues--solutions)
9. [Performance Considerations](#performance-considerations)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│  http://localhost:3000/experimental                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     NEXT.JS FRONTEND                             │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐         │
│  │ Page        │  │ Components  │  │ API Client       │         │
│  │ /experim... │→ │ Chat, Mem.. │→ │ experimental-... │         │
│  └─────────────┘  └─────────────┘  └──────────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ fetch() to localhost:8001
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                EXPERIMENTAL BACKEND (FastAPI)                    │
│  Port: 8001                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐         │
│  │ Chat API    │  │ Memory API  │  │ Analytics API    │         │
│  │ /api/chat   │  │ /api/mem... │  │ /api/analytics   │         │
│  └─────────────┘  └─────────────┘  └──────────────────┘         │
│                         │                                        │
│                         │ Uses                                   │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────┐        │
│  │            MEMORY SERVICE                            │        │
│  │  • MemoryService                                     │        │
│  │  • FactExtractor                                     │        │
│  │  • DynamicCategorizer                                │        │
│  │  • EmbeddingService                                  │        │
│  │  • SearchRouter                                      │        │
│  └─────────────────────────────────────────────────────┘        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ asyncpg (async PostgreSQL)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  POSTGRESQL + pgvector                           │
│  Tables: users, memories, memory_collections                     │
│  Extension: pgvector (for embeddings)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ External API calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OPENAI API                                   │
│  • GPT-4o-mini (chat, fact extraction, categorization)           │
│  • text-embedding-3-small (embeddings, 1536 dims)                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation from Main Dashboard**: All experimental code lives in `/experimental` route and `experiments/` backend folder
2. **Fault Tolerance**: Mock fallbacks when dependencies unavailable
3. **Type Safety**: TypeScript frontend, Pydantic backend
4. **Async Everything**: All I/O operations are async (database, OpenAI, embeddings)
5. **Memory-First Architecture**: Chat is built on top of memory system, not the other way around

---

## Backend Components

### Directory Structure

```
packages/backend/experiments/
├── config.py                    # Configuration management
├── web/
│   ├── dashboard_server.py      # Main FastAPI app
│   ├── chat_api.py              # Chat API endpoints
│   ├── templates/               # Jinja2 templates (old dashboard)
│   └── static/                  # JS/CSS for old dashboard
├── memory/
│   ├── memory_service.py        # ⭐ Main memory orchestration
│   ├── fact_extractor.py        # LLM-based fact extraction
│   ├── categorizer.py           # Hierarchical categorization
│   ├── embedding_service.py     # OpenAI embeddings
│   ├── search_router.py         # Intelligent search routing
│   ├── search_strategies.py     # 6 search strategies
│   └── types.py                 # Type definitions
├── cli/
│   ├── chatbot.py               # CLI chat interface
│   └── chat_repl.py             # REPL implementation
└── database/
    ├── connection.py            # Database connection
    └── json_storage.py          # Fallback JSON storage
```

### Core Backend Classes

#### 1. MemoryService (`memory/memory_service.py`)

**Purpose**: High-level orchestration of all memory operations

**Key Methods**:
- `create_memory_from_message(user_id, message, memory_type, db, **options)` → `List[Memory]`
  - Orchestrates the complete memory creation flow
  - Optionally extracts facts, categorizes, generates embeddings, links memories
  - Returns list of created Memory objects

- `search_memories(user_id, query, db, auto_route=True, **options)` → `List[SearchResult]`
  - Unified search interface
  - Automatically routes to best search strategy if `auto_route=True`
  - Supports manual strategy override

- `_create_single_memory(user_id, content, memory_type, **options)` → `Memory`
  - Internal method to create one memory with all features
  - Handles categorization and embedding generation

- `_ensure_user_exists(user_id, db)` → `UUID`
  - Creates test user if not found in database
  - Prevents foreign key violations

- `get_statistics()` → `dict`
  - Returns comprehensive usage statistics

**Dependencies**:
- FactExtractor
- DynamicCategorizer
- EmbeddingService
- SearchRouter

**Database Operations**:
- Inserts into `memories` table
- Creates entries in `memory_collections` table (if used)
- Updates memory metadata with categories and relationships

---

#### 2. FactExtractor (`memory/fact_extractor.py`)

**Purpose**: Extract discrete facts from complex messages using LLM

**Key Methods**:
- `extract_facts(message, max_facts=None, min_confidence=0.5)` → `ExtractionResult`
  - Calls OpenAI GPT-4o-mini with structured output
  - Returns list of `Fact` objects with confidence scores
  - Tracks token usage

**LLM Integration**:
- Model: `gpt-4o-mini`
- Mode: Structured output (Pydantic schema)
- Temperature: 0.3 (consistent extraction)
- Max facts: Configurable (default 20)

**Fact Types**:
```python
class FactType(str, Enum):
    IDENTITY = "identity"        # Name, age, role
    LOCATION = "location"        # Geographic info
    PROFESSION = "profession"    # Job, career
    PREFERENCE = "preference"    # Likes, dislikes
    PROJECT = "project"          # Work projects
    TECHNICAL = "technical"      # Tech stack
    TIMELINE = "timeline"        # Dates, deadlines
    RELATIONSHIP = "relationship"  # Connections
    SKILL = "skill"              # Abilities
    GOAL = "goal"                # Objectives
    EMOTION = "emotion"          # Feelings
    EXPERIENCE = "experience"    # Past events
    OTHER = "other"              # Uncategorized
```

**Example**:
```python
message = "I'm Jack, a developer in SF working on an AI app with Python."

result = await extractor.extract_facts(message)
# Returns:
# [
#   Fact("Name is Jack", type=IDENTITY, confidence=0.99),
#   Fact("Profession is developer", type=PROFESSION, confidence=0.95),
#   Fact("Located in San Francisco", type=LOCATION, confidence=0.98),
#   Fact("Working on AI app", type=PROJECT, confidence=0.92),
#   Fact("Uses Python", type=TECHNICAL, confidence=0.90)
# ]
```

---

#### 3. DynamicCategorizer (`memory/categorizer.py`)

**Purpose**: Generate hierarchical categories for facts

**Key Methods**:
- `categorize(fact, context=None)` → `CategorizationResult`
  - Generates 4-level category hierarchy
  - Returns categories as both list and path string

- `batch_categorize(facts, show_progress=True)` → `List[CategorizationResult]`
  - Categorize multiple facts efficiently

- `cluster_facts(facts, n_clusters=5)` → `Dict[str, List[Fact]]`
  - Optional: Group similar facts using K-means clustering
  - Requires scikit-learn

**Category Hierarchy**:
```
Level 1: Broad (personal, project, technical, social, professional, temporal)
Level 2: Domain (preferences, timeline, skills, frameworks)
Level 3: Specific (programming, backend, frontend)
Level 4: Most specific (typescript, fastapi, react)

Example: "personal/preferences/programming/typescript"
```

**LLM Integration**:
- Model: `gpt-4o-mini`
- Mode: Structured output
- Temperature: 0.2 (consistent categorization)

**Example**:
```python
result = await categorizer.categorize("Prefers TypeScript over JavaScript")
# Returns:
# CategorizationResult(
#   categories=["personal", "preferences", "programming", "typescript"],
#   hierarchy=CategoryHierarchy(
#     level_1="personal",
#     level_2="preferences",
#     level_3="programming",
#     level_4="typescript"
#   ),
#   confidence=0.95
# )
```

---

#### 4. EmbeddingService (`memory/embedding_service.py`)

**Purpose**: Generate and manage OpenAI embeddings for semantic search

**Key Methods**:
- `embed_text(text)` → `List[float]`
  - Generate single embedding (1536 dimensions)
  - Rate limited to avoid API limits

- `batch_embed(texts, batch_size=100)` → `List[List[float]]`
  - Efficient batch processing
  - Handles rate limiting automatically
  - Progress tracking

- `get_usage_stats()` → `dict`
  - Returns token usage and cost tracking

**OpenAI Integration**:
- Model: `text-embedding-3-small`
- Dimensions: 1536
- Cost: ~$0.00002 per 1K tokens
- Rate limits: 5000 RPM, 5M TPM

**Example**:
```python
embedding = await service.embed_text("I love Python programming")
# Returns: [0.123, -0.456, 0.789, ...] (1536 floats)
```

---

#### 5. SearchRouter (`memory/search_router.py`)

**Purpose**: Analyze queries and route to optimal search strategy

**Key Methods**:
- `analyze_query(query)` → `SearchIntent`
  - Uses LLM to determine best search strategy
  - Extracts parameters (keywords, categories, dates)

- `search(query, user_id, db, auto_route=True, **options)` → `List[SearchResult]`
  - Main search interface
  - Automatically selects and executes best strategy

**Available Strategies**:
1. **Semantic**: Vector similarity (pgvector cosine distance)
2. **Keyword**: BM25 full-text search (PostgreSQL `ts_rank_cd`)
3. **Categorical**: JSONB category filtering
4. **Temporal**: Time-based filtering
5. **Graph**: Relationship traversal (via metadata)
6. **Hybrid**: Weighted combination of strategies

**LLM Integration**:
- Model: `gpt-4o-mini`
- Mode: Structured output
- Temperature: 0.3

**Query Routing Examples**:
```python
"What are my programming preferences?"
→ HYBRID (semantic 0.6 + categorical 0.4)

"Python FastAPI TypeScript"
→ KEYWORD (specific technical terms)

"What did I work on last week?"
→ TEMPORAL (time expression "last week")

"Show me technical facts"
→ CATEGORICAL (domain filtering)

"What's related to Delight project?"
→ GRAPH (relationship query)
```

---

#### 6. Search Strategies (`memory/search_strategies.py`)

**Base Class**: `BaseSearchStrategy`
- Provides `_memory_to_search_result()` for consistent result formatting

**SemanticSearch**:
```python
await semantic.search(query, user_id, db, limit=10, threshold=0.7)
# Uses: pgvector <=> operator for cosine similarity
# Returns: Memories with similarity >= threshold
```

**KeywordSearch**:
```python
await keyword.search(query, user_id, db, limit=10)
# Uses: PostgreSQL to_tsvector + ts_rank_cd (BM25-like)
# Returns: Memories matching keywords, ranked by relevance
```

**CategoricalSearch**:
```python
await categorical.search(categories, user_id, db, match_all=False)
# Uses: JSONB ?| (contains any) or ?& (contains all)
# Returns: Memories with matching categories
```

**TemporalSearch**:
```python
await temporal.search(user_id, db, relative_time="1 week")
# Uses: created_at >= (now - interval)
# Returns: Recent memories
```

**GraphSearch**:
```python
await graph.search(root_memory_id, db, max_depth=3)
# Uses: Breadth-first traversal via metadata relationships
# Returns: Connected memories
```

**HybridSearch**:
```python
config = HybridSearchConfig(weights={
    SearchStrategy.SEMANTIC: 0.7,
    SearchStrategy.KEYWORD: 0.3
})
await hybrid.search(query, user_id, db, config=config)
# Combines multiple strategies with weighted scoring
# Returns: Merged and re-ranked results
```

---

#### 7. ChatService (`web/chat_api.py`)

**Purpose**: Handle chat requests with memory integration

**Key Methods**:
- `_ensure_user_exists(user_id, db)` → `UUID`
  - **CRITICAL**: Creates test user if not found
  - Prevents foreign key violations when creating memories
  - Uses pattern: `experimental_chat_{user_id}`

- `process_message(message, user_id, conversation_history)` → `ChatResponse`
  - **Step 0**: Ensure user exists (prevents FK errors)
  - **Step 1**: Search for relevant memories
  - **Step 2**: Build context and generate AI response
  - **Step 3**: Extract facts and create new memories
  - Returns: AI response + memories used + memories created

**Chat Flow**:
```
1. User sends message
2. ChatService.process_message() called
3. Ensure user exists in database ← IMPORTANT!
4. Search memories with query (via MemoryService)
5. Build system prompt with memory context
6. Call OpenAI GPT-4o-mini for response
7. Extract facts from user message
8. Create memories for each fact
9. Link related facts in graph
10. Return response + memory metadata
```

**OpenAI Integration**:
- Model: `gpt-4o-mini`
- Temperature: 0.7 (balanced creativity)
- Max tokens: 500 (concise responses)
- System prompt includes retrieved memories

**Mock Fallback**:
```python
class MockChatService:
    async def process_message(message, user_id, conversation_history):
        return ChatResponse(
            response=f"Echo: {message}\n\n(This is a mock response...)",
            memories_retrieved=[],
            memories_created=[],
            timestamp=datetime.now().isoformat()
        )
```

---

#### 8. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Key Settings**:
```python
class ExperimentConfig:
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    read_only_mode: bool = False

    # OpenAI Models
    chat_model: str = "gpt-4o-mini"
    reasoning_model: str = "o1-preview"
    expensive_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    # Memory System
    max_personal_memories: int = 10000
    max_project_memories: int = 5000
    max_task_memories: int = 100
    similarity_threshold: float = 0.7

    # Fact Extraction
    min_fact_length: int = 10
    max_facts_per_message: int = 20
    auto_categorize: bool = True

    # Search
    default_search_limit: int = 10
    hybrid_search_weight_vector: float = 0.7  # 70% vector, 30% keyword
    graph_traversal_max_depth: int = 3
```

**Usage**:
```python
from experiments.config import get_config
config = get_config()
model = config.chat_model  # "gpt-4o-mini"
```

---

## Frontend Components

### Directory Structure

```
packages/frontend/src/
├── app/experimental/
│   └── page.tsx                 # Main experimental page
├── components/experimental/
│   ├── ChatInterface.tsx        # Chat UI
│   ├── MemoryVisualization.tsx  # Memory browser
│   ├── AnalyticsDashboard.tsx   # Analytics UI
│   ├── ConfigurationPanel.tsx   # Config UI
│   └── index.ts                 # Exports
├── lib/
│   ├── api/
│   │   └── experimental-client.ts   # ⭐ API client
│   └── hooks/
│       └── useExperimentalAPI.ts    # ⭐ React hooks
```

### Core Frontend Components

#### 1. ExperimentalAPIClient (`lib/api/experimental-client.ts`)

**Purpose**: Type-safe API client for all backend endpoints

**Key Methods**:

**Health Check**:
```typescript
async healthCheck(): Promise<{
  status: string;
  timestamp: string;
  storage: string;
  version: string;
}>
```

**Chat**:
```typescript
async sendChatMessage(request: ChatRequest): Promise<ChatResponse>
// ChatRequest: { message, user_id?, conversation_history? }
// ChatResponse: { response, memories_retrieved[], memories_created[], timestamp }
```

**Memories**:
```typescript
async getMemories(filters?: {
  user_id?: string;
  memory_type?: string;
  category?: string;
  limit?: number;
}): Promise<Memory[]>

async getMemory(memoryId: string): Promise<Memory>

async deleteMemory(memoryId: string): Promise<{ status: string }>
```

**Analytics**:
```typescript
async getMemoryStats(userId?: string): Promise<MemoryStats>

async getTokenUsage(hours?: number): Promise<TokenUsageSummary>
```

**Configuration**:
```typescript
async getConfig(): Promise<SystemConfig>

async updateConfig(config: SystemConfig): Promise<{ status: string }>
```

**Graph**:
```typescript
async getMemoryGraph(userId?: string, limit?: number): Promise<GraphData>
```

**WebSocket** (optional):
```typescript
connectWebSocket(
  onMessage: (event: string, data: any) => void
): WebSocket

disconnectWebSocket(): void
```

**Usage Example**:
```typescript
import experimentalAPI from '@/lib/api/experimental-client';

// Send chat message
const response = await experimentalAPI.sendChatMessage({
  message: "I love hiking",
  conversation_history: []
});

// Get memories
const memories = await experimentalAPI.getMemories({
  memory_type: "personal",
  limit: 50
});
```

---

#### 2. React Hooks (`lib/hooks/useExperimentalAPI.ts`)

**Purpose**: Easy-to-use React hooks for API access

**Available Hooks**:

**useHealthCheck**:
```typescript
const { healthy, checking, error } = useHealthCheck();
// Auto-polls every 5 seconds
// healthy: boolean - true if backend is reachable
// checking: boolean - true during health check
```

**useMemories**:
```typescript
const { memories, loading, error, refresh, deleteMemory } = useMemories({
  user_id?: string,
  memory_type?: string,
  category?: string,
  limit?: number
});
// memories: Memory[] - list of memories
// refresh: () => Promise<void> - reload memories
// deleteMemory: (id: string) => Promise<void> - delete one memory
```

**useMemoryStats**:
```typescript
const { stats, loading, error, refresh } = useMemoryStats(userId?);
// stats: MemoryStats - total counts, by_type, by_category
```

**useConfig**:
```typescript
const { config, loading, error, saving, refresh, updateConfig } = useConfig();
// config: SystemConfig - current configuration
// updateConfig: (newConfig) => Promise<void> - save changes
```

**useTokenUsage**:
```typescript
const { usage, loading, error, refresh } = useTokenUsage(hours = 24);
// usage: TokenUsageSummary - token usage in last N hours
```

**useMemoryGraph**:
```typescript
const { graph, loading, error, refresh } = useMemoryGraph(userId?, limit = 100);
// graph: GraphData - nodes and edges for visualization
```

**IMPORTANT FIX**: Infinite Loop Prevention
```typescript
// ❌ WRONG - causes infinite loop
const { memories } = useMemories(filters);  // filters object changes every render

// ✅ CORRECT - stringify to stabilize dependency
const filtersString = JSON.stringify(filters || {});
const refresh = useCallback(async () => {
  const parsedFilters = JSON.parse(filtersString);
  const data = await experimentalAPI.getMemories(parsedFilters);
  setMemories(data);
}, [filtersString]);  // Only changes when VALUES change
```

---

#### 3. ChatInterface (`components/experimental/ChatInterface.tsx`)

**Purpose**: Chat UI with memory visualization

**Key Features**:
- Real-time chat with AI
- Displays memories retrieved (with relevance scores)
- Shows memories created from conversation
- Auto-scroll to latest message
- Loading states with animated dots
- Error handling with helpful instructions

**State Management**:
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  memories_retrieved?: SearchResult[];
  memories_created?: Memory[];
  loading?: boolean;
}

const [messages, setMessages] = useState<Message[]>([...]);
const [input, setInput] = useState('');
const [isProcessing, setIsProcessing] = useState(false);
```

**Chat Flow**:
```
1. User types message and presses Enter
2. Add user message to messages array
3. Add loading message ("Thinking...")
4. Call experimentalAPI.sendChatMessage()
5. Replace loading message with AI response
6. Display memories retrieved (purple boxes)
7. Display memories created (cyan boxes)
8. Auto-scroll to bottom
```

**Error Handling**:
```typescript
try {
  const response = await experimentalAPI.sendChatMessage({...});
  // Show response
} catch (error) {
  // Show error message with instructions:
  // "Make sure experimental backend is running on port 8001"
}
```

---

#### 4. MemoryVisualization (`components/experimental/MemoryVisualization.tsx`)

**Purpose**: Browse and manage memories

**Key Features**:
- List view and graph view (graph is placeholder)
- Filter by memory type (personal, project, task, fact)
- Search memories by content
- Delete memories with confirmation
- Refresh button
- Real-time stats (total count, filtered by type)

**State Management**:
```typescript
const [viewMode, setViewMode] = useState<'list' | 'graph'>('list');
const [selectedType, setSelectedType] = useState<string>('all');
const [searchQuery, setSearchQuery] = useState('');

const { memories, loading, error, refresh, deleteMemory } = useMemories({
  user_id: userId,
  memory_type: selectedType === 'all' ? undefined : selectedType,
  limit: 50
});

const filteredMemories = memories.filter(m =>
  searchQuery ? m.content.toLowerCase().includes(searchQuery.toLowerCase()) : true
);
```

**Memory Display**:
```typescript
{filteredMemories.map(memory => (
  <MemoryCard
    key={memory.id}
    content={memory.content}
    type={memory.memory_type}
    categories={memory.metadata.categories}
    created_at={memory.created_at}
    onDelete={() => handleDelete(memory.id)}
  />
))}
```

---

#### 5. AnalyticsDashboard (`components/experimental/AnalyticsDashboard.tsx`)

**Purpose**: Display system analytics and usage

**Key Metrics**:
- Total memories count
- Memories by type (bar chart)
- Top categories (list)
- Token usage (last 24 hours)
- Cost breakdown by model
- Recent search queries (placeholder)

**Data Sources**:
```typescript
const { stats } = useMemoryStats(userId);
const { usage } = useTokenUsage(24);

// stats.total_memories
// stats.by_type: { personal: 10, project: 5, ... }
// stats.by_category: { programming: 8, preferences: 5, ... }

// usage.total_tokens
// usage.total_cost
// usage.by_model: { "gpt-4o-mini": { tokens: 1000, cost: 0.01 }, ... }
```

---

#### 6. ConfigurationPanel (`components/experimental/ConfigurationPanel.tsx`)

**Purpose**: Modify system configuration

**Configurable Settings**:

**Models**:
- Chat model (dropdown: gpt-4o-mini, gpt-4o, gpt-4-turbo)
- Reasoning model (dropdown: o1-preview, o1-mini, gpt-4o)
- Embedding model (dropdown: text-embedding-3-small, text-embedding-3-large)

**Search Settings**:
- Similarity threshold (slider: 0.0 - 1.0)
- Default search limit (input: number)
- Hybrid search weight (slider: vector vs keyword)
- Graph traversal max depth (input: number)

**Fact Extraction Settings**:
- Max facts per message (input: number)
- Auto-categorize (checkbox)
- Max categories per fact (input: number)
- Min fact length (input: number)

**Save/Reset**:
```typescript
const { config, saving, updateConfig } = useConfig();

const handleSave = async () => {
  await updateConfig(modifiedConfig);
  alert("Configuration saved!");
};

const handleReset = () => {
  setModifiedConfig(config);  // Reset to original
};
```

---

#### 7. Experimental Page (`app/experimental/page.tsx`)

**Purpose**: Main container for all experimental features

**Layout**:
```
┌────────────────────────────────────────────┐
│ HEADER                                     │
│ • Title: "Experimental Lab"                │
│ • Backend status indicator (green/red dot) │
│ • Warning if backend offline               │
├────────────────────────────────────────────┤
│ TABS                                       │
│ [💬 Chat] [🧠 Memories] [📊 Analytics] [...] │
├────────────────────────────────────────────┤
│ MAIN CONTENT                               │
│ (Active tab component rendered here)       │
│                                            │
│                                            │
└────────────────────────────────────────────┘
│ FOOTER (fixed at bottom)                   │
│ Backend: http://localhost:8001 (status)    │
└────────────────────────────────────────────┘
```

**Tab Management**:
```typescript
type TabType = 'chat' | 'memories' | 'analytics' | 'config';
const [activeTab, setActiveTab] = useState<TabType>('chat');

{activeTab === 'chat' && <ChatInterface />}
{activeTab === 'memories' && <MemoryVisualization />}
{activeTab === 'analytics' && <AnalyticsDashboard />}
{activeTab === 'config' && <ConfigurationPanel />}
```

**Health Monitoring**:
```typescript
const { healthy, checking } = useHealthCheck();

<div className={`status-dot ${
  checking ? 'bg-yellow-400 animate-pulse' :
  healthy ? 'bg-green-400' : 'bg-red-400'
}`} />

{!healthy && (
  <div className="warning">
    ⚠️ Backend not running. Start with:
    <code>cd packages/backend && poetry run python experiments/web/dashboard_server.py</code>
  </div>
)}
```

---

## API Reference

### Base URL
```
http://localhost:8001
```

### Health Check

**GET `/health`**
```json
Response:
{
  "status": "healthy",
  "timestamp": "2025-11-19T10:30:00",
  "storage": "json" | "postgresql",
  "version": "0.1.0"
}
```

---

### Chat Endpoints

**POST `/api/chat/message`**

Send a message and get AI response with memory context.

Request:
```json
{
  "message": "I love hiking in the mountains",
  "user_id": "optional-uuid",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous message",
      "timestamp": "2025-11-19T10:00:00"
    }
  ]
}
```

Response:
```json
{
  "response": "That sounds wonderful! I'll remember that you enjoy hiking...",
  "memories_retrieved": [
    {
      "id": "uuid",
      "content": "User enjoys outdoor activities",
      "memory_type": "personal",
      "score": 0.85,
      "categories": ["personal", "preferences", "activities"]
    }
  ],
  "memories_created": [
    {
      "id": "uuid",
      "content": "User loves hiking in mountains",
      "memory_type": "personal",
      "categories": ["personal", "preferences", "activities", "hiking"]
    },
    {
      "id": "uuid",
      "content": "User prefers mountain hiking",
      "memory_type": "personal",
      "categories": ["personal", "preferences", "location", "mountains"]
    }
  ],
  "timestamp": "2025-11-19T10:30:00"
}
```

**GET `/api/chat/health`**

Check chat service health.

Response:
```json
{
  "status": "healthy",
  "service": "chat",
  "mode": "real" | "mock",
  "timestamp": "2025-11-19T10:30:00"
}
```

---

### Memory Endpoints

**GET `/api/memories`**

Get memories with optional filters.

Query Parameters:
- `user_id` (optional): Filter by user UUID
- `memory_type` (optional): Filter by type (personal, project, task, fact)
- `category` (optional): Filter by category string
- `limit` (optional): Max results (default: 50)

Response:
```json
[
  {
    "id": "uuid",
    "content": "User loves Python programming",
    "memory_type": "personal",
    "user_id": "uuid",
    "metadata": {
      "categories": ["personal", "preferences", "programming", "python"],
      "fact_type": "preference",
      "confidence": 0.95
    },
    "created_at": "2025-11-19T10:00:00"
  }
]
```

**GET `/api/memories/{memory_id}`**

Get single memory by ID.

Response: Single memory object (same structure as array item above)

**DELETE `/api/memories/{memory_id}`**

Delete a memory.

Response:
```json
{
  "status": "success",
  "message": "Memory deleted"
}
```

**GET `/api/memories/categories/hierarchy`**

Get category hierarchy for all memories.

Query Parameters:
- `user_id` (optional): Filter by user

Response:
```json
{
  "personal": {
    "programming": 15,
    "preferences": 10,
    "location": 3
  },
  "project": {
    "delight": 8,
    "goals": 5
  }
}
```

---

### Analytics Endpoints

**GET `/api/analytics/stats`**

Get memory statistics.

Query Parameters:
- `user_id` (optional): Filter by user

Response:
```json
{
  "total_memories": 42,
  "by_type": {
    "personal": 25,
    "project": 12,
    "task": 5
  },
  "by_category": {
    "programming": 18,
    "preferences": 10,
    "location": 5
  },
  "total_embeddings": 42,
  "avg_embedding_time_ms": 120.5,
  "storage_size_bytes": 1048576
}
```

**GET `/api/analytics/token-usage`**

Get token usage summary.

Query Parameters:
- `hours` (optional): Time range in hours (default: 24)

Response:
```json
{
  "total_tokens": 15000,
  "total_cost": 0.023,
  "by_model": {
    "gpt-4o-mini": {
      "tokens": 10000,
      "cost": 0.015
    },
    "gpt-4o": {
      "tokens": 5000,
      "cost": 0.008
    }
  }
}
```

**POST `/api/analytics/token-usage`**

Record token usage (for tracking).

Request:
```json
{
  "model": "gpt-4o-mini",
  "tokens_input": 100,
  "tokens_output": 200,
  "cost": 0.005,
  "timestamp": "2025-11-19T10:30:00"
}
```

---

### Configuration Endpoints

**GET `/api/config`**

Get current system configuration.

Response:
```json
{
  "models": {
    "chat_model": "gpt-4o-mini",
    "reasoning_model": "o1-preview",
    "expensive_model": "gpt-4o",
    "embedding_model": "text-embedding-3-small"
  },
  "search": {
    "similarity_threshold": 0.7,
    "default_search_limit": 10,
    "hybrid_search_weight_vector": 0.7,
    "graph_traversal_max_depth": 3
  },
  "fact_extraction": {
    "max_facts_per_message": 20,
    "auto_categorize": true,
    "max_categories_per_fact": 3,
    "min_fact_length": 10
  }
}
```

**POST `/api/config`**

Update system configuration.

Request: Same structure as GET response

Response:
```json
{
  "status": "success",
  "message": "Configuration updated"
}
```

**GET `/api/models/available`**

Get list of available models.

Response:
```json
{
  "chat": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
  "reasoning": ["o1-preview", "o1-mini", "gpt-4o", "gpt-4-turbo"],
  "embedding": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
}
```

---

### Graph Endpoints

**GET `/api/graph/memories`**

Get memory graph for visualization.

Query Parameters:
- `user_id` (optional): Filter by user
- `limit` (optional): Max nodes (default: 100)

Response:
```json
{
  "nodes": [
    {
      "id": "uuid-1",
      "label": "User loves Python programming",
      "type": "personal",
      "categories": ["personal", "preferences", "programming"],
      "created_at": "2025-11-19T10:00:00"
    }
  ],
  "edges": [
    {
      "source": "uuid-1",
      "target": "uuid-2",
      "type": "related_to"
    }
  ]
}
```

---

### WebSocket Endpoint

**WS `/ws/updates`**

Real-time updates for memory changes.

Connection:
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/updates');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

Message Format:
```json
{
  "type": "memory_created" | "memory_updated" | "memory_deleted" | "pong",
  "data": { ... }
}
```

---

## Data Flow

### Chat Message Flow

```
User Input → Frontend ChatInterface
    ↓
    │ 1. User types "I love hiking"
    │ 2. Press Enter
    ↓
Frontend: handleSendMessage()
    ↓
    │ 3. Add user message to messages[]
    │ 4. Add loading message
    │ 5. Prepare conversation_history
    ↓
experimentalAPI.sendChatMessage()
    ↓
    │ 6. POST http://localhost:8001/api/chat/message
    │    Body: { message, conversation_history }
    ↓
Backend: chat_api.py → send_message()
    ↓
    │ 7. Parse request (ChatRequest schema)
    │ 8. Generate or use provided user_id
    │ 9. Convert Pydantic models to dicts
    ↓
ChatService.process_message()
    ↓
    │ 10. STEP 0: _ensure_user_exists(user_id, db)
    │     ├─ Check if user exists in users table
    │     └─ Create if not found (prevents FK error)
    │
    │ 11. STEP 1: Search for relevant memories
    │     ├─ MemoryService.search_memories(query=message)
    │     ├─ SearchRouter analyzes query intent
    │     ├─ Executes optimal search strategy
    │     └─ Returns List[SearchResult] (top 5)
    │
    │ 12. STEP 2: Generate AI response
    │     ├─ Build system prompt with memory context
    │     ├─ Append conversation history (last 10 messages)
    │     ├─ Call OpenAI chat.completions.create()
    │     │   Model: gpt-4o-mini
    │     │   Temperature: 0.7
    │     │   Max tokens: 500
    │     └─ Extract assistant_message from response
    │
    │ 13. STEP 3: Create memories from user message
    │     ├─ MemoryService.create_memory_from_message()
    │     ├─ FactExtractor.extract_facts(message)
    │     │   ├─ Call OpenAI with structured output
    │     │   └─ Returns List[Fact] (e.g., "User loves hiking")
    │     ├─ For each fact:
    │     │   ├─ DynamicCategorizer.categorize(fact)
    │     │   ├─ EmbeddingService.embed_text(fact)
    │     │   ├─ Create Memory in database
    │     │   └─ Store categories in metadata
    │     └─ Link facts as related in graph
    │
    │ 14. db.commit() - Persist all memories
    ↓
Return ChatResponse
    ↓
    │ 15. Format response with:
    │     - assistant_message
    │     - memories_retrieved (with scores)
    │     - memories_created (with categories)
    │     - timestamp
    ↓
Backend → Frontend (HTTP response)
    ↓
    │ 16. Frontend receives ChatResponse
    │ 17. Create assistant Message object
    │ 18. Add memories_retrieved[] and memories_created[]
    ↓
Frontend: Update UI
    ↓
    │ 19. Replace loading message with assistant message
    │ 20. Render AI response in chat bubble
    │ 21. Show "Memories Used" section (purple boxes)
    │ 22. Show "Memories Created" section (cyan boxes)
    │ 23. Auto-scroll to bottom
    ↓
User sees response with memory context
```

---

### Memory Creation Flow (Detailed)

```
Input: "I'm Jack, a developer in SF working on an AI app with Python."

MemoryService.create_memory_from_message()
    ↓
    │ extract_facts=True
    ↓
FactExtractor.extract_facts()
    ↓
    │ 1. Call OpenAI GPT-4o-mini
    │    Prompt: SYSTEM_PROMPT + "Extract facts from this message"
    │    Response format: FactExtractionResponse (Pydantic)
    │
    │ 2. LLM returns:
    │    [
    │      { content: "Name is Jack", fact_type: "identity", confidence: 0.99 },
    │      { content: "Profession is developer", fact_type: "profession", confidence: 0.95 },
    │      { content: "Located in San Francisco", fact_type: "location", confidence: 0.98 },
    │      { content: "Working on AI app", fact_type: "project", confidence: 0.92 },
    │      { content: "Uses Python", fact_type: "technical", confidence: 0.90 }
    │    ]
    │
    │ 3. Convert to Fact objects
    ↓
Return List[Fact] (5 facts)
    ↓
MemoryService: For each fact
    ↓
    │ auto_categorize=True
    ↓
DynamicCategorizer.categorize(fact.content)
    ↓
    │ 1. Call OpenAI GPT-4o-mini
    │    Prompt: SYSTEM_PROMPT + "Categorize this fact"
    │    Response format: CategorizationResponse (Pydantic)
    │
    │ Example for "Profession is developer":
    │ {
    │   level_1: "professional",
    │   level_2: "career",
    │   level_3: "software",
    │   level_4: "developer",
    │   confidence: 0.95
    │ }
    │
    │ 2. Create CategoryHierarchy object
    │    Path: "professional/career/software/developer"
    │    List: ["professional", "career", "software", "developer"]
    ↓
Return CategorizationResult
    ↓
    │ generate_embeddings=True
    ↓
EmbeddingService.embed_text(fact.content)
    ↓
    │ 1. Call OpenAI embeddings API
    │    Model: text-embedding-3-small
    │    Input: "Profession is developer"
    │
    │ 2. Receive 1536-dimensional vector
    │    [0.123, -0.456, 0.789, ..., 0.234]
    ↓
Return embedding: List[float]
    ↓
Create Memory object
    ↓
    │ Memory(
    │   id=UUID,
    │   user_id=user_id,
    │   memory_type=MemoryType.PERSONAL,
    │   content="Profession is developer",
    │   embedding=[0.123, -0.456, ...],  # 1536 floats
    │   extra_data={
    │     "categories": ["professional", "career", "software", "developer"],
    │     "category_hierarchy": "professional/career/software/developer",
    │     "categorization_confidence": 0.95,
    │     "fact_type": "profession",
    │     "confidence": 0.95,
    │     "original_message": "I'm Jack, a developer in SF...",
    │     "extraction_method": "llm_structured"
    │   }
    │ )
    ↓
db.add(memory)
    ↓
    │ INSERT INTO memories (id, user_id, memory_type, content, embedding, metadata, created_at)
    │ VALUES (uuid, uuid, 'personal', 'Profession is developer', [...], {...}, now())
    ↓
Repeat for all 5 facts
    ↓
    │ link_facts=True
    ↓
_link_memories_as_related()
    ↓
    │ For each memory:
    │   memory.extra_data["relationships"]["related_to"] = [
    │     uuid-of-fact-2,
    │     uuid-of-fact-3,
    │     uuid-of-fact-4,
    │     uuid-of-fact-5
    │   ]
    ↓
db.commit()
    ↓
Return List[Memory] (5 memories)
```

---

### Memory Search Flow

```
Query: "What are my programming preferences?"

SearchRouter.search(query, user_id, db, auto_route=True)
    ↓
    │ auto_route=True
    ↓
SearchRouter.analyze_query()
    ↓
    │ 1. Call OpenAI GPT-4o-mini
    │    Prompt: SYSTEM_PROMPT + "Analyze this query"
    │    Response format: QueryAnalysisResponse (Pydantic)
    │
    │ 2. LLM returns:
    │    {
    │      strategy: "hybrid",
    │      confidence: 0.92,
    │      reasoning: "Conceptual query requiring semantic + categorical",
    │      hybrid_strategies: ["semantic", "categorical"],
    │      hybrid_weights: { "semantic": 0.6, "categorical": 0.4 },
    │      categories: ["programming", "preferences"]
    │    }
    │
    │ 3. Create SearchIntent object
    ↓
Return SearchIntent(strategy=HYBRID, ...)
    ↓
Execute HybridSearch
    ↓
    │ weights = { SEMANTIC: 0.6, CATEGORICAL: 0.4 }
    ↓
1. Execute SemanticSearch
    ↓
    │ a. Generate query embedding
    │    EmbeddingService.embed_text("What are my programming preferences?")
    │    → [0.567, -0.234, ..., 0.891] (1536 dims)
    │
    │ b. SQL query:
    │    SELECT memory, (1 - embedding <=> query_embedding) AS similarity
    │    FROM memories
    │    WHERE user_id = :user_id
    │    AND embedding IS NOT NULL
    │    ORDER BY similarity DESC
    │    LIMIT 20
    │
    │ c. PostgreSQL pgvector:
    │    Uses <=> operator for cosine distance
    │    Finds memories with closest embeddings
    │
    │ d. Filter by threshold (0.7)
    │    Only keep memories with similarity >= 0.7
    │
    │ e. Returns:
    │    [
    │      SearchResult(content="Prefers TypeScript", score=0.89),
    │      SearchResult(content="Loves async programming", score=0.85),
    │      SearchResult(content="Uses Python and React", score=0.82)
    │    ]
    ↓
Return List[SearchResult] (semantic results)
    ↓
2. Execute CategoricalSearch
    ↓
    │ a. Categories: ["programming", "preferences"]
    │
    │ b. SQL query:
    │    SELECT memory
    │    FROM memories
    │    WHERE user_id = :user_id
    │    AND metadata->'categories' ?| ARRAY['programming', 'preferences']
    │    ORDER BY created_at DESC
    │    LIMIT 20
    │
    │ c. PostgreSQL JSONB:
    │    Uses ?| operator (contains any)
    │    Finds memories with ANY matching category
    │
    │ d. Returns:
    │    [
    │      SearchResult(content="Tech stack includes Python", score=1.0),
    │      SearchResult(content="Prefers TypeScript", score=1.0),
    │      SearchResult(content="Loves late night coding", score=1.0)
    │    ]
    ↓
Return List[SearchResult] (categorical results)
    ↓
3. Combine results with weighted scoring
    ↓
    │ For each result:
    │   If in both lists:
    │     combined_score = (semantic_score * 0.6) + (categorical_score * 0.4)
    │   If in semantic only:
    │     combined_score = semantic_score * 0.6
    │   If in categorical only:
    │     combined_score = categorical_score * 0.4
    │
    │ Example:
    │   "Prefers TypeScript"
    │   - Semantic score: 0.89
    │   - Categorical score: 1.0 (found in programming+preferences)
    │   - Combined: (0.89 * 0.6) + (1.0 * 0.4) = 0.534 + 0.4 = 0.934
    ↓
4. Sort by combined score (descending)
    ↓
5. Remove duplicates (keep highest score)
    ↓
6. Limit to top N (default: 10)
    ↓
Return final List[SearchResult]
    ↓
    │ [
    │   SearchResult(content="Prefers TypeScript", score=0.934),
    │   SearchResult(content="Loves async programming", score=0.850),
    │   SearchResult(content="Tech stack includes Python", score=0.820),
    │   ...
    │ ]
    ↓
Backend → Frontend
    ↓
Frontend displays results in chat with relevance scores
```

---

## Method Index

### Backend Methods (Alphabetical)

**ChatService**:
- `_ensure_user_exists(user_id, db)` → `UUID` - Create user if not exists
- `process_message(message, user_id, conversation_history)` → `ChatResponse` - Full chat flow

**DynamicCategorizer**:
- `batch_categorize(facts, show_progress)` → `List[CategorizationResult]` - Batch categorization
- `categorize(fact, context)` → `CategorizationResult` - Categorize single fact
- `categorize_fact_object(fact)` → `CategorizationResult` - Categorize Fact object
- `cluster_facts(facts, n_clusters, show_progress)` → `Dict[str, List[Fact]]` - K-means clustering
- `get_statistics()` → `dict` - Usage statistics
- `print_categorization(fact, result)` - Pretty print result

**EmbeddingService**:
- `batch_embed(texts, batch_size, show_progress)` → `List[List[float]]` - Batch embedding
- `embed_text(text)` → `List[float]` - Single embedding
- `get_usage_stats()` → `dict` - Token usage and costs

**FactExtractor**:
- `extract_and_validate(message, expected_min_facts)` → `ExtractionResult` - Extract with validation
- `extract_facts(message, max_facts, min_confidence)` → `ExtractionResult` - Main extraction
- `get_facts_by_type(facts, fact_type)` → `List[Fact]` - Filter by type
- `get_high_confidence_facts(facts, threshold)` → `List[Fact]` - Filter by confidence
- `get_statistics()` → `dict` - Usage statistics
- `print_extraction_summary(result)` - Pretty print result

**MemoryService**:
- `create_memory_from_message(user_id, message, memory_type, db, **options)` → `List[Memory]` - Main creation flow
- `get_statistics()` → `dict` - Comprehensive statistics
- `print_statistics()` - Pretty print statistics
- `search_memories(user_id, query, db, **options)` → `List[SearchResult]` - Unified search
- `_create_single_memory(user_id, content, memory_type, **options)` → `Memory` - Create one memory
- `_ensure_user_exists(user_id, db)` → `UUID` - Create user if needed
- `_get_or_create_collection(user_id, memory_type, project_id, session_id, db)` → `MemoryCollection` - Get/create collection
- `_link_memories_as_related(memories, db)` - Create graph relationships

**SearchRouter**:
- `analyze_query(query)` → `SearchIntent` - LLM-based query analysis
- `get_statistics()` → `dict` - Usage statistics
- `print_statistics()` - Pretty print statistics
- `search(query, user_id, db, **options)` → `List[SearchResult]` - Main search interface

**Search Strategies**:
- `CategoricalSearch.search(categories, user_id, db, **options)` → `List[SearchResult]`
- `GraphSearch.search(root_memory_id, db, **options)` → `List[SearchResult]`
- `HybridSearch.search(query, user_id, db, config, **options)` → `List[SearchResult]`
- `KeywordSearch.search(query, user_id, db, **options)` → `List[SearchResult]`
- `SemanticSearch.search(query, user_id, db, **options)` → `List[SearchResult]`
- `TemporalSearch.search(user_id, db, **options)` → `List[SearchResult]`

---

### Frontend Methods (Alphabetical)

**experimentalAPI (API Client)**:
- `connectWebSocket(onMessage)` → `WebSocket` - Connect to real-time updates
- `deleteMemory(memoryId)` → `Promise<{status}>` - Delete memory
- `disconnectWebSocket()` - Close WebSocket connection
- `getConfig()` → `Promise<SystemConfig>` - Get configuration
- `getMemories(filters)` → `Promise<Memory[]>` - Get memories
- `getMemory(memoryId)` → `Promise<Memory>` - Get single memory
- `getMemoryGraph(userId, limit)` → `Promise<GraphData>` - Get graph data
- `getMemoryStats(userId)` → `Promise<MemoryStats>` - Get statistics
- `getTokenUsage(hours)` → `Promise<TokenUsageSummary>` - Get token usage
- `healthCheck()` → `Promise<{status, timestamp, storage, version}>` - Check health
- `sendChatMessage(request)` → `Promise<ChatResponse>` - Send chat message
- `updateConfig(config)` → `Promise<{status}>` - Update configuration

**React Hooks**:
- `useConfig()` → `{ config, loading, error, saving, refresh, updateConfig }` - Configuration hook
- `useHealthCheck()` → `{ healthy, checking, error }` - Backend health check
- `useMemories(filters)` → `{ memories, loading, error, refresh, deleteMemory }` - Memories hook
- `useMemoryGraph(userId, limit)` → `{ graph, loading, error, refresh }` - Graph hook
- `useMemoryStats(userId)` → `{ stats, loading, error, refresh }` - Statistics hook
- `useTokenUsage(hours)` → `{ usage, loading, error, refresh }` - Token usage hook

**Component Methods**:
- `ChatInterface.handleSendMessage()` - Send chat message
- `ChatInterface.handleKeyPress(e)` - Handle Enter key
- `MemoryVisualization.handleDelete(memoryId)` - Delete memory with confirmation
- `ExperimentalPage.TabButton` - Tab button component

---

## Debugging Guide

### Common Issues and Solutions

#### 1. Chat API Returning 404

**Symptoms**:
```
POST http://localhost:8001/api/chat/message 404 Not Found
```

**Root Cause**:
- Chat router not included in FastAPI app
- Import error in `dashboard_server.py`

**Diagnosis**:
```bash
cd packages/backend
poetry run python experiments/web/dashboard_server.py

# Look for in startup logs:
✅ Chat API enabled  ← GOOD
⚠️  Chat API not available: ...  ← BAD
```

**Fix**:
1. Check `dashboard_server.py` lines 542-549
2. Ensure `chat_api.py` exists in `experiments/web/`
3. Check for import errors (traceback will show)

**Prevention**:
- Always check startup logs for "Chat API enabled"
- Run backend in verbose mode to see all import errors

---

#### 2. Infinite Loop - Maximum Update Depth Exceeded

**Symptoms**:
```
Error: Maximum update depth exceeded. This can happen when a component
repeatedly calls setState inside componentWillUpdate or componentDidUpdate.
```

**Root Cause**:
```typescript
// filters object creates new reference every render
const refresh = useCallback(async () => {
  await getMemories(filters);  // filters changes every render
}, [filters]);  // ← New object every time

useEffect(() => {
  refresh();  // Runs every render
}, [refresh]);  // ← refresh changes every render

// LOOP: render → new filters → new refresh → useEffect → setState → render
```

**Diagnosis**:
1. Open browser console (F12)
2. Click "Memories" tab
3. See rapid console spam with "Maximum update depth exceeded"

**Fix**:
```typescript
// Stringify filters to stabilize reference
const filtersString = JSON.stringify(filters || {});

const refresh = useCallback(async () => {
  const parsedFilters = JSON.parse(filtersString);
  await getMemories(parsedFilters);
}, [filtersString]);  // Only changes when VALUES change
```

**Prevention**:
- **Never use object dependencies directly in useCallback/useEffect**
- Always stringify objects for stable references
- Or use `useMemo` to memoize the object

---

#### 3. Foreign Key Violation on Memory Creation

**Symptoms**:
```
sqlalchemy.exc.IntegrityError: insert or update on table "memories"
violates foreign key constraint "memories_user_id_fkey"
DETAIL: Key (user_id)=(uuid) is not present in table "users"
```

**Root Cause**:
- Chat API generates random UUID for user
- Memory creation tries to use non-existent user_id
- PostgreSQL foreign key constraint fails

**Diagnosis**:
```bash
# Backend logs will show:
ERROR:  insert or update on table "memories" violates foreign key constraint
```

**Fix**:
In `chat_api.py`, add user creation before memory creation:

```python
async def _ensure_user_exists(self, user_id: UUID, db) -> UUID:
    """Ensure user exists in database, create if needed"""
    from sqlalchemy import select
    from app.models.user import User

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user_id

    # Create test user
    test_clerk_id = f"experimental_chat_{user_id}"
    new_user = User(
        id=user_id,
        clerk_user_id=test_clerk_id,
        email=f"experimental-{user_id.hex[:8]}@delight.local",
        display_name="Experimental Chat User"
    )
    db.add(new_user)
    await db.flush()
    return user_id

async def process_message(...):
    async with AsyncSessionLocal() as db:
        # Step 0: Ensure user exists
        await self._ensure_user_exists(user_id, db)
        # Now safe to create memories
```

**Prevention**:
- Always check user existence before foreign key operations
- Use `db.flush()` to make new records available immediately
- Add database constraints only after ensuring data integrity

---

#### 4. Backend Not Starting - Port Already in Use

**Symptoms**:
```
ERROR:    [Errno 48] Address already in use
```

**Diagnosis**:
```bash
# Find process using port 8001
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows
```

**Fix**:
```bash
# Option 1: Kill existing process
kill -9 <PID>

# Option 2: Use different port
poetry run uvicorn experiments.web.dashboard_server:app --port 8002

# Update frontend API client baseUrl to match
```

**Prevention**:
- Always stop backend before restarting
- Use Ctrl+C to gracefully shutdown

---

#### 5. CORS Error - Frontend Can't Reach Backend

**Symptoms**:
```
Access to fetch at 'http://localhost:8001/api/chat/message' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Diagnosis**:
1. Open browser DevTools → Network tab
2. Look for failed request with CORS error

**Fix**:
Check `dashboard_server.py` lines 189-198:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Prevention**:
- Ensure CORS middleware is added BEFORE routes
- Add all frontend origins to `allow_origins`

---

#### 6. OpenAI API Key Missing

**Symptoms**:
```
ValueError: OPENAI_API_KEY not set in environment
```

**Diagnosis**:
```bash
cd packages/backend
echo $OPENAI_API_KEY
# Should print: sk-proj-...
```

**Fix**:
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-proj-your-key-here
EOF

# Verify
poetry run python -c "from experiments.config import get_config; print(get_config().openai_api_key)"
```

**Prevention**:
- Always set environment variables in `.env` file
- Never commit `.env` to git

---

#### 7. Database Connection Error

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Diagnosis**:
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
cd packages/backend
poetry run python -c "
from app.db.session import engine
import asyncio
asyncio.run(engine.connect())
"
```

**Fix**:
1. Verify PostgreSQL is running
2. Check DATABASE_URL format:
   ```
   postgresql+asyncpg://user:password@host:port/database
   ```
3. Test connection with psql:
   ```bash
   psql "postgresql://user:password@host:port/database"
   ```

**Prevention**:
- Use connection pooling
- Add retry logic for transient failures
- Enable connection timeout

---

### Debugging Checklist

When something isn't working:

1. **Backend Health**:
   ```bash
   curl http://localhost:8001/health
   # Should return: {"status": "healthy", ...}
   ```

2. **Frontend to Backend Connection**:
   ```bash
   curl -X POST http://localhost:8001/api/chat/message \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
   # Should return JSON (not 404)
   ```

3. **Database Connection**:
   ```bash
   cd packages/backend
   poetry run python -c "
   from app.db.session import AsyncSessionLocal
   import asyncio
   async def test():
       async with AsyncSessionLocal() as db:
           print('Connected!')
   asyncio.run(test())
   "
   ```

4. **OpenAI API**:
   ```bash
   poetry run python -c "
   from openai import AsyncOpenAI
   from experiments.config import get_config
   import asyncio
   async def test():
       client = AsyncOpenAI(api_key=get_config().openai_api_key)
       response = await client.chat.completions.create(
           model='gpt-4o-mini',
           messages=[{'role': 'user', 'content': 'Hi'}]
       )
       print(response.choices[0].message.content)
   asyncio.run(test())
   "
   ```

5. **Frontend Console**:
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests

---

## Known Issues & Solutions

### Fixed Issues

✅ **Issue 1**: Config.js null pointer exception
**Status**: Fixed
**Solution**: Removed references to non-existent keyword-weight elements

✅ **Issue 2**: Chat API 404
**Status**: Fixed
**Solution**: Changed to absolute import, added traceback printing

✅ **Issue 3**: Infinite loop in Memories tab
**Status**: Fixed
**Solution**: Stringify filters to create stable dependency

✅ **Issue 4**: Windows emoji encoding error
**Status**: Fixed
**Solution**: Replaced emojis with [OK] and [WARNING] text

✅ **Issue 5**: Foreign key violation
**Status**: Fixed
**Solution**: Auto-create user before memory creation

---

### Current Limitations

1. **Graph View**: Placeholder only, not implemented
2. **Config Save**: Frontend sends updates but backend doesn't persist to file
3. **WebSocket**: Implemented but not actively used
4. **Memory Collections**: Created but not fully utilized
5. **Graph Relationships**: Stored but no UI visualization

---

### Future Improvements

1. **Add retry logic** for OpenAI API calls
2. **Implement connection pooling** for database
3. **Add caching** for embeddings (avoid regenerating)
4. **Implement graph visualization** using D3.js or similar
5. **Add WebSocket real-time updates** for multi-user scenarios
6. **Persist configuration changes** to config file
7. **Add pagination** for large memory lists
8. **Implement memory deduplication** (detect and merge similar memories)
9. **Add memory versioning** (track edits over time)
10. **Implement memory pruning** (auto-delete old task memories)

---

## Performance Considerations

### Backend Performance

**OpenAI API Calls**:
- **Bottleneck**: External API latency (~500ms-2s per call)
- **Optimization**: Batch operations where possible
- **Cost Tracking**: Enable with `enable_cost_tracking=True` in config

**Database Queries**:
- **Vector Search**: pgvector is fast for <100k memories, consider indexing for more
- **JSONB Queries**: Create GIN index on metadata column for faster category filtering
- **Connection Pooling**: SQLAlchemy handles this automatically

**Fact Extraction**:
- **Current**: Sequential fact processing
- **Improvement**: Could parallelize categorization + embedding generation

**Recommended Indexes**:
```sql
-- Speed up vector similarity searches
CREATE INDEX memories_embedding_idx ON memories
USING ivfflat (embedding vector_cosine_ops);

-- Speed up category searches
CREATE INDEX memories_metadata_gin_idx ON memories
USING gin (metadata);

-- Speed up user queries
CREATE INDEX memories_user_id_idx ON memories (user_id);

-- Speed up temporal searches
CREATE INDEX memories_created_at_idx ON memories (created_at DESC);
```

---

### Frontend Performance

**React Rendering**:
- **Memoization**: Use `useMemo` for expensive computations
- **Virtual Scrolling**: Implement for large memory lists (>100 items)
- **Lazy Loading**: Load memories in chunks as user scrolls

**API Calls**:
- **Debouncing**: Debounce search input to avoid excessive API calls
- **Caching**: Consider caching memories client-side
- **Optimistic Updates**: Update UI before server confirmation (delete memory)

**Bundle Size**:
- Current: All components loaded on page mount
- **Improvement**: Code-split each tab component

---

## Metrics to Monitor

1. **Memory Count**: Track growth over time
2. **Token Usage**: Monitor OpenAI API costs
3. **Search Latency**: Measure query response times
4. **Fact Extraction Rate**: Facts per message
5. **Embedding Generation Time**: ms per embedding
6. **Database Query Time**: Identify slow queries
7. **Error Rate**: Track API failures
8. **User Engagement**: Messages per session

---

## File Change Log

All major code changes are documented in `BUG_FIXES.md` and this document.

**Last Major Changes**:
- 2025-11-19: Foreign key fix (auto-create users)
- 2025-11-19: Infinite loop fix (stringify filters)
- 2025-11-19: Chat API import fix
- 2025-11-19: Windows emoji fix
- 2025-11-19: Initial integration (frontend + backend)

---

## Additional Resources

- **Setup Guide**: `EXPERIMENTAL_SETUP.md`
- **Bug Fixes**: `BUG_FIXES.md`
- **Main Project Docs**: `docs/ARCHITECTURE.md`, `docs/SETUP.md`
- **CLAUDE.md**: Project instructions for Claude AI

---

**End of Technical Documentation**
