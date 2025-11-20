# 🚀 Getting Started with the Experimental Memory System

Welcome to the experimental AI agent second brain system! This guide will help you get started quickly.

---

## 📋 What's Been Built

This experimental system implements a comprehensive **second brain memory architecture** with:

### ✅ Core Components (COMPLETE)

1. **Type Definitions** (`memory/types.py`)
   - Fact, SearchIntent, SearchResult, CategoryHierarchy
   - Enums for search strategies and fact types
   - Data models for all system components

2. **Embedding Service** (`memory/embedding_service.py`)
   - OpenAI text-embedding-3-small integration (1536-dim)
   - Batch processing with rate limiting
   - Cost tracking and optimization
   - Direct database storage integration

3. **Fact Extractor** (`memory/fact_extractor.py`)
   - **Multi-fact parsing from complex messages**
   - LLM-based extraction (GPT-4o-mini with structured output)
   - Confidence scoring and source tracking
   - Type classification (identity, preference, technical, etc.)

4. **Dynamic Categorizer** (`memory/categorizer.py`)
   - **Automatic hierarchical categorization** (4 levels)
   - LLM-based category generation
   - Embedding-based fact clustering
   - Consistent naming conventions

5. **Multi-Modal Search** (`memory/search_strategies.py`)
   - **6 search strategies:**
     - **Semantic**: Vector similarity (pgvector)
     - **Keyword**: BM25 full-text search
     - **Categorical**: Filter by auto-generated categories
     - **Temporal**: Time-based retrieval
     - **Graph**: Relationship traversal
     - **Hybrid**: Weighted combination
   - Unified SearchResult format
   - PostgreSQL/pgvector integration

6. **Smart Query Router** (`memory/search_router.py`)
   - **Intelligent query analysis**
   - Automatic search strategy selection
   - Parameter extraction (keywords, categories, dates)
   - Confidence scoring and fallback strategies

7. **Memory Service** (`memory/memory_service.py`)
   - **Complete orchestration layer**
   - Create memories from messages with fact extraction
   - 3-tier memory management (Personal/Project/Task)
   - Intelligent search with auto-routing
   - Comprehensive statistics tracking

8. **Database Layer** (`database/connection.py`)
   - Safe async database access
   - Read-only mode toggle
   - Connection validation
   - Database info utilities

---

## 🎯 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd packages/backend

# If not already installed
poetry install

# Add experimental dependencies
poetry add rich networkx matplotlib
```

### 2. Configure Environment

Ensure your `.env` has:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.xxx.supabase.co:5432/postgres
OPENAI_API_KEY=sk-proj-...

# Optional
ENVIRONMENT=development
```

### 3. Test Database Connection

```bash
poetry run python experiments/database/connection.py
```

Expected output:
```
🗄️  Database Information
========================
✅ Connection successful
Database:          postgres
PostgreSQL:        PostgreSQL 16.x...
pgvector:          ✅ Installed
Total Memories:    X
```

### 4. Run Complete Demo

```bash
poetry run python experiments/memory/examples/complete_demo.py
```

This demonstrates:
- ✅ Fact extraction from complex messages
- ✅ Automatic categorization
- ✅ Memory creation with embeddings
- ✅ All 6 search strategies
- ✅ Smart query routing
- ✅ Statistics and analytics

---

## 💡 Usage Examples

### Example 1: Create Memories with Fact Extraction

```python
import asyncio
import uuid
from experiments.database.connection import get_experiment_db
from experiments.memory.memory_service import MemoryService
from app.models.memory import MemoryType

async def create_memories():
    service = MemoryService()
    user_id = uuid.uuid4()  # Replace with actual user ID

    message = """
    I'm Jack, a software developer in San Francisco.
    Working on Delight AI app with Python and React.
    Launch goal is Q1 2025. I prefer TypeScript and async programming.
    """

    async with get_experiment_db() as db:
        memories = await service.create_memory_from_message(
            user_id=user_id,
            message=message,
            memory_type=MemoryType.PERSONAL,
            db=db,
            extract_facts=True,       # Extract discrete facts
            auto_categorize=True,      # Auto-categorize each fact
            generate_embeddings=True   # Generate embeddings
        )

        print(f"Created {len(memories)} memories!")
        for memory in memories:
            print(f"- {memory.content}")
            print(f"  Categories: {memory.metadata.get('categories')}")

asyncio.run(create_memories())
```

**Output:**
```
Created 5 memories!
- Name is Jack
  Categories: ['personal', 'identity', 'name', 'jack']
- Software developer
  Categories: ['personal', 'profession', 'software_development']
- Based in San Francisco
  Categories: ['personal', 'location', 'city', 'san_francisco']
- Working on Delight AI app
  Categories: ['project', 'current_work', 'delight', 'ai']
- Tech stack includes Python
  Categories: ['technical', 'programming', 'languages', 'python']
```

### Example 2: Smart Search with Auto-Routing

```python
import asyncio
from experiments.database.connection import get_experiment_db
from experiments.memory.memory_service import MemoryService

async def smart_search():
    service = MemoryService()

    queries = [
        "What are my programming preferences?",  # → Semantic + Categorical
        "Python FastAPI",                         # → Keyword
        "What did I work on last week?",         # → Temporal
        "technical facts",                        # → Categorical
    ]

    async with get_experiment_db() as db:
        for query in queries:
            print(f"\nQuery: \"{query}\"")

            # Analyze query (see what strategy it would use)
            intent = await service.search_router.analyze_query(query)
            print(f"→ Strategy: {intent.strategy.value}")
            print(f"  Reasoning: {intent.explanation}")

            # Search
            results = await service.search_memories(
                user_id=user_id,
                query=query,
                db=db,
                auto_route=True,  # Automatically picks best strategy
                limit=5
            )

            print(f"  Found {len(results)} results")
            for result in results:
                print(f"    [{result.score:.2f}] {result.content}")

asyncio.run(smart_search())
```

### Example 3: Individual Component Testing

```python
# Test fact extraction only
from experiments.memory.fact_extractor import quick_extract

facts = await quick_extract("I love Python and work in SF")
for fact in facts:
    print(f"- {fact.content} ({fact.fact_type.value})")

# Test categorization only
from experiments.memory.categorizer import quick_categorize

categories = await quick_categorize("Prefers TypeScript over JavaScript")
print(f"Categories: {categories}")
# Output: ['personal', 'preferences', 'programming', 'typescript']

# Test embedding only
from experiments.memory.embedding_service import quick_embed

embedding = await quick_embed("Hello world")
print(f"Embedding dimension: {len(embedding)}")  # 1536
```

---

## 🧪 Testing Features

### Terminal Testing

All components have built-in test scripts:

```bash
# Test fact extraction
poetry run python experiments/memory/fact_extractor.py

# Test categorization
poetry run python experiments/memory/categorizer.py

# Test embedding service
poetry run python experiments/memory/embedding_service.py

# Test database connection
poetry run python experiments/database/connection.py

# Complete demo
poetry run python experiments/memory/examples/complete_demo.py
```

### Web UI Testing (Coming Soon)

The web interface for interactive testing will provide:
- Memory browser with tree view
- Interactive search with all strategies
- Embedding visualization (t-SNE)
- Graph visualization (D3.js)
- Live agent execution monitoring

To be built in `experiments/web/server.py`

---

## 📊 System Architecture

```
User Message
    ↓
MemoryService (orchestration)
    ↓
FactExtractor → [Extract discrete facts]
    ↓
DynamicCategorizer → [Auto-categorize facts]
    ↓
EmbeddingService → [Generate embeddings]
    ↓
PostgreSQL + pgvector [Store memories]
    ↓
SearchRouter (for retrieval)
    ↓
    ┌─────────┬─────────┬─────────┬─────────┬─────────┐
Semantic  Keyword  Categorical  Temporal   Graph    Hybrid
    └─────────┴─────────┴─────────┴─────────┴─────────┘
                         ↓
                   Search Results
```

---

## 🔍 Search Strategy Guide

### When to Use Each Strategy

| Strategy | Best For | Example Query |
|----------|----------|---------------|
| **Semantic** | Conceptual queries, paraphrasing | "What are my career goals?" |
| **Keyword** | Specific terms, exact phrases | "Python FastAPI" |
| **Categorical** | Topic/domain filtering | "show me technical facts" |
| **Temporal** | Time-based, recency queries | "What did I work on last week?" |
| **Graph** | Relationship, connected knowledge | "What's related to Delight project?" |
| **Hybrid** | Complex multi-faceted queries | "recent programming decisions" |

### Auto-Routing Examples

The Smart Query Router analyzes queries and automatically picks the best strategy:

```python
# The router automatically analyzes these queries:
"What are my programming preferences?"
→ Hybrid (semantic: 0.6, categorical: 0.4)
  Reasoning: Conceptual query requiring understanding + category filtering

"Python FastAPI TypeScript"
→ Keyword
  Reasoning: Specific technical terms, best matched with keyword search

"What did I work on last week?"
→ Temporal
  Reasoning: Clear temporal expression

"Show me all technical facts"
→ Categorical
  Reasoning: Explicit category filtering request
```

---

## 💰 Cost Estimation

Based on typical usage with GPT-4o-mini and text-embedding-3-small:

| Operation | Cost (per 1000) |
|-----------|----------------|
| Fact Extraction (10 facts/message) | ~$0.001 |
| Categorization (per fact) | ~$0.0005 |
| Embedding Generation | ~$0.00002 |
| **Total per complex message** | **~$0.015** |

**Daily usage estimate**: ~100 messages/day = $1.50/day = $45/month

Track actual costs using:
```python
service.print_statistics()  # Shows token usage and costs
```

---

## 🚀 Next Steps

### Immediate (Ready to Use)

1. ✅ **Run the demo** - See all features in action
2. ✅ **Create test memories** - Use your own data
3. ✅ **Try different searches** - Test all 6 strategies
4. ✅ **View statistics** - Track usage and costs

### Coming Soon

1. **Web Interface** (`experiments/web/`)
   - Memory browser with visualization
   - Interactive search interface
   - Real-time agent monitoring
   - Graph visualization

2. **CLI REPL** (`experiments/cli/repl.py`)
   - Conversational memory interaction
   - Interactive agent testing
   - Memory management commands

3. **Agent Core** (`experiments/agent/`)
   - LangGraph integration
   - Node-based workflow planning
   - Goal-driven execution
   - Eliza character implementation

4. **Production Integration**
   - Extract proven patterns to main app
   - Optimize for scale
   - Add caching and performance tuning

### Build Your Own

Use this system to build:
- **AI Agents** with long-term memory
- **Chatbots** with contextual recall
- **Personal Assistants** with knowledge graphs
- **Research Tools** with smart search
- **Knowledge Bases** with auto-organization

---

## 📚 Documentation

- **Architecture**: `experiments/ARCHITECTURE.md` - System design and principles
- **README**: `experiments/README.md` - Feature overview and examples
- **This Guide**: `experiments/GETTING_STARTED.md` - Quick start guide
- **Code Docs**: Comprehensive docstrings in all modules

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test connection
poetry run python experiments/database/connection.py

# Check pgvector
# Should show "pgvector: ✅ Installed"

# If not installed, run in Supabase SQL editor:
CREATE EXTENSION IF NOT EXISTS vector;
```

### OpenAI API Errors

```bash
# Verify API key in .env
echo $OPENAI_API_KEY

# Test with simple request
poetry run python -c "
from openai import OpenAI
client = OpenAI()
print(client.models.list())
"
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd packages/backend

# Check Python path
poetry run python -c "import sys; print('\\n'.join(sys.path))"

# Should include: .../packages/backend
```

---

## 💡 Tips & Best Practices

### 1. Fact Extraction

- **Best**: Complex messages with multiple discrete facts
- **Avoid**: Single-fact messages (use extract_facts=False)
- **Optimal**: 3-10 facts per message

### 2. Categorization

- **Consistent**: Categories are hierarchical (4 levels max)
- **Format**: lowercase, underscores for multi-word
- **Example**: `personal/preferences/programming/typescript`

### 3. Search

- **Start with auto-routing**: Let the system pick the strategy
- **Override when needed**: Use specific strategy for known query types
- **Combine strategies**: Use hybrid for complex queries

### 4. Memory Types

- **Personal**: Long-term user facts (preferences, identity)
- **Project**: Project-scoped knowledge
- **Task**: Short-term working memory (cleared regularly)

---

## 🎉 Success! What's Next?

You now have a complete experimental second brain system running!

**Explore**:
- Experiment with different messages
- Try all search strategies
- Build your own agents using this memory
- Visualize knowledge graphs
- Track your personal knowledge

**Build**:
- Web interface for interactive testing
- CLI REPL for conversational access
- LangGraph agents with memory integration
- Custom visualizations
- Production deployment

**Share**:
- Extract patterns to main Delight app
- Document learnings and insights
- Contribute improvements
- Build new features

---

**Happy experimenting!** 🧪🧠✨

For questions or issues, check the codebase documentation or create an issue.
