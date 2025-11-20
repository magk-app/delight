# 🧪 Experimental AI Agent System

**A comprehensive second brain system with hierarchical memory, intelligent fact extraction, and adaptive state management.**

Based on: "Hierarchical Memory and Adaptive State Management for an AI Agent" by Jack Luo (Nov 2025)

---

## 🎯 Purpose

This experimental playground implements:

- **📚 Second Brain Memory**: Intelligent fact extraction, dynamic categorization, multi-modal search
- **🧠 3-Tier Memory System**: Personal (long-term) → Project (domain) → Task (working)
- **🔍 Smart Search**: Semantic, keyword, categorical, temporal, and graph-based retrieval
- **🤖 Goal-Driven Agent**: Node-based workflow planning with LangGraph
- **📊 Visual Interface**: Web dashboard for memory browsing and agent execution tracking

**Status**: Experimental - Proven patterns will be extracted to main Delight app

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd packages/backend

# Install additional dependencies
poetry add rich networkx matplotlib jinja2 websockets

# Or use requirements file
poetry install
```

### 2. Configure Environment

```bash
# Ensure .env has:
# - DATABASE_URL (PostgreSQL with pgvector)
# - OPENAI_API_KEY

# Test connection
poetry run python experiments/database/connection.py
```

### 3. Initialize Memory System

```bash
# Generate embeddings for existing memories (if any)
poetry run python experiments/memory/embedding_service.py \
  --user-id <your-uuid> \
  --generate-all

# Or start fresh with test data
poetry run python experiments/database/test_data.py \
  --user-id <your-uuid> \
  --create-samples
```

### 4. Try the Interfaces

```bash
# Terminal visualization
poetry run python experiments/memory_util/visualizer.py --user-id <uuid>

# Interactive agent REPL
poetry run python experiments/cli/repl.py --user-id <uuid>

# Web dashboard
poetry run python experiments/web/server.py
# Open http://localhost:5000
```

---

## 🧠 Core Features

### 1. **Intelligent Fact Extraction**

Extract multiple facts from complex messages with automatic categorization:

```python
from experiments.memory.fact_extractor import FactExtractor

extractor = FactExtractor()

message = """
I'm Jack, a software developer based in San Francisco.
I'm working on an AI companion app called Delight using Python and React.
My goal is to launch by Q1 2025, and I prefer working late nights.
"""

facts = await extractor.extract_facts(message)
# Returns:
# [
#   Fact(content="Name is Jack", categories=["personal", "identity"]),
#   Fact(content="Software developer", categories=["personal", "profession"]),
#   Fact(content="Based in San Francisco", categories=["personal", "location"]),
#   Fact(content="Working on Delight app", categories=["project", "work"]),
#   Fact(content="Tech stack: Python, React", categories=["project", "technical"]),
#   Fact(content="Launch goal: Q1 2025", categories=["project", "timeline"]),
#   Fact(content="Prefers late night work", categories=["personal", "preferences"])
# ]

# Each fact is stored separately with embeddings and graph relationships
```

### 2. **Dynamic Categorization**

Facts are automatically categorized using LLM analysis:

```python
from experiments.memory.categorizer import DynamicCategorizer

categorizer = DynamicCategorizer()

fact = "I prefer using TypeScript over JavaScript"

categories = await categorizer.categorize(fact)
# Returns: ["preferences", "programming", "technical"]

# Categories are hierarchical:
# technical → programming → language_preferences → typescript
```

### 3. **Multi-Modal Search**

Multiple search strategies for fast retrieval:

```python
from experiments.memory.search_router import SearchRouter

router = SearchRouter()

# Smart routing based on query type
results = await router.search(
    user_id=user_id,
    query="What programming languages do I like?",
    auto_route=True  # Automatically picks best search strategy
)

# Available strategies:
# - Semantic: Vector similarity (best for conceptual queries)
# - Keyword: BM25 full-text search (best for specific terms)
# - Categorical: Filter by auto-generated categories
# - Temporal: Time-based retrieval (recent, date range)
# - Graph: Relationship traversal (connected knowledge)
# - Hybrid: Combination of multiple strategies
```

**Search Routing Algorithm**:
```
Query Analysis:
├── Has specific keywords? → Keyword Search
├── Conceptual/abstract? → Semantic Search
├── Time-related? → Temporal Search
├── Relationship query? → Graph Traversal
└── Complex? → Hybrid Search (weighted combination)
```

### 4. **Graph-Based Knowledge Structure**

Memories are organized in a knowledge graph:

```
User Knowledge Graph
├── Personal
│   ├── Identity
│   │   ├── Name: Jack
│   │   └── Profession: Developer
│   ├── Preferences
│   │   ├── Work Schedule: Late nights
│   │   └── Languages: TypeScript, Python
│   └── Location: San Francisco
│
├── Projects
│   ├── Delight
│   │   ├── Description: AI companion app
│   │   ├── Tech Stack: [Python, React, PostgreSQL]
│   │   ├── Timeline: Launch Q1 2025
│   │   └── Related To: → Career Goals
│   └── Experiment
│       └── Context: Agent research
│
└── Current Task
    ├── Goal: Build memory system
    └── Working Context: [recent conversation]
```

**Graph Relationships**:
- `RELATED_TO`: General relationship
- `PART_OF`: Hierarchical relationship
- `SUPPORTS`: Evidence/reasoning link
- `CONTRADICTS`: Conflicting information
- `TEMPORAL_SEQUENCE`: Time-ordered events

### 5. **Node-Based Workflow Execution**

Visual, transparent agent execution:

```python
from experiments.agent.planner import WorkflowPlanner
from experiments.agent.executor import GoalDrivenExecutor

planner = WorkflowPlanner()
executor = GoalDrivenExecutor()

# Create plan
workflow = await planner.plan_workflow(
    goal="Research memory systems and create summary",
    constraints=["Use only 2024 sources", "Max 500 words"]
)

# Show plan to user
print(workflow.visualize())
# ┌─────────────────┐
# │ Understand Goal │
# └────────┬────────┘
#          ↓
# ┌────────────────────┐
# │  Plan Research     │
# └────────┬───────────┘
#          ↓
#     ┌────┴────┐
#     ↓         ↓
# ┌────────┐ ┌────────┐
# │Search  │ │Search  │  (Parallel)
# │Academic│ │Industry│
# └───┬────┘ └───┬────┘
#     └─────┬─────┘
#           ↓
#     ┌──────────┐
#     │Synthesize│
#     └─────┬────┘
#           ↓
#     ┌──────────┐
#     │  Verify  │
#     └─────┬────┘
#           ↓
#     ┌──────────┐
#     │  Output  │
#     └──────────┘

# Execute with milestone updates
result = await executor.execute_workflow(
    workflow,
    on_milestone=lambda node: print(f"✓ Completed: {node}")
)
```

---

## 📁 Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

**Key Components**:

```
experiments/
├── database/          # Safe DB connection, inspection, test data
├── memory/            # Fact extraction, embeddings, search, graph
├── memory_util/       # Visualization, analysis, export
├── agent/             # State management, planning, execution
├── web/               # Dashboard, memory browser, agent visualizer
└── cli/               # REPL, debugger, memory management
```

---

## 🛠️ Usage Examples

### Memory Management

```bash
# Create a complex memory with fact extraction
poetry run python experiments/cli/memory_cli.py create \
  --content "I'm launching my startup in Q1 2025. It's an AI app built with Python. I'm based in SF and prefer async programming." \
  --extract-facts \
  --auto-categorize

# This extracts multiple facts:
# ✓ Fact 1: "Launching startup Q1 2025" [project, timeline]
# ✓ Fact 2: "AI app" [project, domain]
# ✓ Fact 3: "Built with Python" [project, technical]
# ✓ Fact 4: "Based in SF" [personal, location]
# ✓ Fact 5: "Prefers async programming" [personal, preferences, technical]

# Search with smart routing
poetry run python experiments/cli/memory_cli.py search \
  --query "What do I prefer in programming?" \
  --auto-route

# Visualize memory graph
poetry run python experiments/memory_util/visualizer.py \
  --user-id <uuid> \
  --mode graph \
  --depth 2
```

### Agent Interaction

```bash
# Interactive REPL
poetry run python experiments/cli/repl.py --user-id <uuid>

> You: What projects am I working on?
>
> Eliza: [Planning workflow...]
>        [Searching project memories...]
>        [Graph traversal: Projects node...]
>
>        Based on your memories, you're working on:
>
>        1. **Delight** - An AI companion app
>           - Tech: Python, React, PostgreSQL
>           - Goal: Launch Q1 2025
>           - Related: Your career goals in AI
>
>        2. **Experiment** - Agent research
>           - Focus: Memory systems
>           - Related: Delight project
>
>        [Memory retrieval: 5 memories, 0.8s]
>        [Workflow: 4 nodes executed]

# Step-through debugger
poetry run python experiments/cli/workflow_debugger.py \
  --goal "Analyze my work patterns" \
  --step-by-step
```

### Web Dashboard

```bash
# Start server
poetry run python experiments/web/server.py

# Features:
# - Memory browser with hierarchical tree view
# - Graph visualization (force-directed layout)
# - Live agent execution monitoring
# - Memory editing and categorization
# - Search with all modes (semantic, keyword, etc.)
# - Embedding visualization (t-SNE projection)
```

---

## 🔍 Search Strategies Explained

### 1. **Semantic Search** (Vector Similarity)

Best for: Conceptual queries, paraphrasing, related ideas

```python
query = "What are my career goals?"
# Finds memories like:
# - "Want to build successful AI startup"
# - "Launch Delight and raise Series A"
# - "Long-term: Lead AI research team"
```

**Algorithm**:
1. Embed query using OpenAI text-embedding-3-small
2. Compute cosine similarity with all memory embeddings
3. Return top-k with similarity > threshold

### 2. **Keyword Search** (BM25)

Best for: Specific terms, names, exact phrases

```python
query = "Python FastAPI"
# Finds memories containing exact keywords
```

**Algorithm**:
1. Tokenize query
2. BM25 scoring across memory content
3. Rank by relevance

### 3. **Categorical Search**

Best for: Filtering by topic, type, domain

```python
query = "Show me all programming preferences"
# Filters: categories IN ["preferences", "programming"]
```

**Algorithm**:
1. Map query to categories (using LLM or rules)
2. Filter memories by matching categories
3. Optionally rank by recency or importance

### 4. **Temporal Search**

Best for: Time-based queries, recent events

```python
query = "What did I work on last week?"
# Filters: created_at BETWEEN last_week
```

**Algorithm**:
1. Extract time expressions from query
2. Convert to date range
3. Filter by timestamp

### 5. **Graph Traversal**

Best for: Relationship queries, connected knowledge

```python
query = "What's related to my Delight project?"
# Traverses: Delight → Tech Stack, Timeline, Goals
```

**Algorithm**:
1. Find root node (entity in query)
2. BFS/DFS traversal up to max_depth
3. Return connected memories

### 6. **Hybrid Search**

Best for: Complex queries requiring multiple strategies

```python
query = "Recent programming decisions for my AI project"
# Combines: Temporal + Categorical + Semantic
```

**Algorithm**:
1. Run multiple searches in parallel
2. Weighted combination of scores
3. Re-rank using cross-encoder (optional)

---

## 🎨 Visualization Features

### Terminal (Rich)

```bash
poetry run python experiments/memory_util/visualizer.py --user-id <uuid>
```

**Output**:
```
🧠 Memory Structure
├── 👤 Personal (245 memories)
│   ├── 🏷️  Identity (12)
│   ├── 🏷️  Preferences (34)
│   ├── 🏷️  Skills (67)
│   └── 🏷️  Location (8)
├── 📁 Projects (156 memories)
│   ├── 📂 Delight (89)
│   │   ├── 🏷️  Technical (34)
│   │   ├── 🏷️  Timeline (12)
│   │   └── 🏷️  Goals (15)
│   └── 📂 Experiment (67)
└── 📝 Tasks (23 memories)
    └── 🏷️  Current (23)

Latest Search: "programming preferences"
┌─────────┬──────────┬─────────────────────────────┐
│  Score  │   Type   │         Content             │
├─────────┼──────────┼─────────────────────────────┤
│  0.923  │ Personal │ Prefer TypeScript over JS   │
│  0.887  │ Personal │ Love async/await patterns   │
│  0.854  │ Project  │ Using FastAPI for backend   │
└─────────┴──────────┴─────────────────────────────┘
```

### Web Dashboard

**Memory Browser**:
- Hierarchical tree view (collapsible)
- Search bar with strategy selector
- Filter by type, category, date range
- Edit/delete memories
- View embeddings (t-SNE 2D projection)

**Graph Visualizer**:
- Force-directed layout (D3.js)
- Node colors by category
- Edge thickness by relationship strength
- Interactive: hover for details, click to expand

**Agent Execution Monitor**:
- Real-time workflow graph
- Node highlighting during execution
- State inspection at each step
- Tool call details
- Milestone notifications

---

## ⚙️ Configuration

Edit `experiments/config.py` or set environment variables:

```python
# Memory limits
MAX_PERSONAL_MEMORIES = 10000
MAX_PROJECT_MEMORIES = 5000
MAX_TASK_MEMORIES = 100

# Fact extraction
MAX_FACTS_PER_MESSAGE = 20
AUTO_CATEGORIZE = True

# Search
SIMILARITY_THRESHOLD = 0.7
HYBRID_SEARCH_WEIGHT_VECTOR = 0.7  # 70% vector, 30% keyword

# Agent
MAX_PARALLEL_TASKS = 5
MAX_SEQUENTIAL_DEPTH = 10
REQUIRE_USER_APPROVAL = False  # Approve plans before execution

# Safety
READ_ONLY_MODE = False  # Enable for testing without DB writes
WARN_BEFORE_EXPENSIVE_OPERATIONS = True
```

---

## 🔒 Safety Features

1. **Read-Only Mode**: Test without database writes
2. **Cost Tracking**: Monitor OpenAI API usage
3. **Rate Limiting**: Prevent runaway API calls
4. **Confirmation Prompts**: Warn before bulk operations
5. **Transaction Rollback**: Automatic on errors
6. **Test User Isolation**: Separate test data
7. **Audit Logs**: Track all memory operations

---

## 🚧 Current Status

**Implemented**:
- ✅ Directory structure
- ✅ Configuration system
- ✅ Architecture documentation

**In Progress** (Subagents working):
- 🔄 Memory system (fact extraction, categorization, search)
- 🔄 Database layer (connection, safety, test data)
- 🔄 Agent core (state, planner, executor)
- 🔄 Web interface (server, visualizations)
- 🔄 CLI tools (REPL, debugger)

**Planned**:
- 📋 Integration testing
- 📋 Performance benchmarking
- 📋 Export proven patterns to main app

---

## 🎯 Next Steps

1. **Try fact extraction**: Create a complex memory and see auto-categorization
2. **Test search strategies**: Compare semantic vs keyword vs hybrid
3. **Visualize memory graph**: See knowledge structure
4. **Chat with Eliza**: Test agent with memory integration
5. **Debug workflows**: Step through agent execution
6. **Browse web dashboard**: Interactive memory management

---

## 📚 Further Reading

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed system design
- [Medium Article](https://thejackluo8.medium.com/hierarchical-memory-and-adaptive-state-management-for-an-ai-agent-f99a50562837) - Original paper
- Main app: `docs/tech-spec-epic-2.md` - Production memory system design

---

## 🤝 Contributing

This is an experimental system. Feel free to:
- Add new search strategies
- Improve categorization algorithms
- Build new visualization features
- Optimize graph traversal
- Create new agent tools

**Workflow**:
1. Create feature in experiments/
2. Test thoroughly
3. Extract to main app if proven valuable

---

**Happy experimenting!** 🚀
