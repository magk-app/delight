# Conversational Chatbot with Memory

This is an AI chatbot that remembers everything you tell it and uses those memories to have personalized conversations with you.

## What This Does

1. **Remembers Everything**: Stores facts about you in a PostgreSQL database with semantic search
2. **Contextual Responses**: Retrieves relevant memories when you chat and uses them to respond
3. **Clean Memory Export**: Generates human-readable JSON files WITHOUT embeddings
4. **Real-time Visibility**: Shows you which memories it's using and creating
5. **Semantic Search**: Uses pgvector to find relevant memories based on meaning, not just keywords

## Features

- 🧠 **Semantic Memory**: Vector embeddings + pgvector for intelligent memory retrieval
- 💬 **Natural Conversations**: Powered by GPT-4o-mini
- 📝 **Automatic Fact Extraction**: Extracts and stores important facts from your messages
- 📊 **Memory Types**: Personal (preferences), Project (goals), Task (temporary)
- 🔍 **Smart Search**: Find memories by semantic similarity
- 💾 **Clean Exports**: JSON files without 1536-dimensional embedding arrays
- 📈 **Statistics**: Track usage, costs, and memory counts

## Architecture

```
┌─────────────────┐
│   You (User)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Chatbot (scripts/chatbot.py)     │
│   - Conversation management         │
│   - Display & CLI interface         │
└────────┬───────────────────┬────────┘
         │                   │
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  Memory Service  │  │ Embedding Service│
│  - CRUD ops      │  │ - OpenAI API     │
│  - Search        │  │ - Vector gen     │
│  - Export        │  │ - Cost tracking  │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     │
┌───────────────────────────────┴──────┐
│  PostgreSQL + pgvector (Supabase)    │
│  - memories table                    │
│  - 1536-dim embeddings               │
│  - Semantic similarity search        │
└──────────────────────────────────────┘
```

## Prerequisites

1. **PostgreSQL with pgvector** (Supabase recommended)
2. **Python 3.11+** with Poetry
3. **OpenAI API key**
4. **Migrations applied** (memory tables created)

## Setup

### 1. Install Dependencies

```bash
cd packages/backend
poetry install
```

This will install:
- `openai` - For GPT-4o-mini chat and text-embedding-3-small
- `rich` - For beautiful CLI output
- `sqlalchemy` + `asyncpg` - For async PostgreSQL access
- `pgvector` - For vector similarity search

### 2. Configure Environment

Make sure your `.env` file has:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-...

# Database (Supabase or local PostgreSQL with pgvector)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Optional: For Clerk auth (if using with API)
CLERK_SECRET_KEY=sk_test_...
```

### 3. Apply Database Migrations

```bash
poetry run alembic upgrade head
```

This creates the `memories` table with:
- `id` (UUID)
- `user_id` (UUID, foreign key to users)
- `memory_type` (ENUM: personal, project, task)
- `content` (TEXT)
- `embedding` (VECTOR(1536))
- `metadata` (JSONB)
- `created_at`, `accessed_at` (TIMESTAMP WITH TIME ZONE)

Plus HNSW index for fast similarity search.

### 4. Verify Database Connection

```bash
poetry run python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())"
```

You should see no errors.

## Usage

### Start the Chatbot

```bash
cd packages/backend
poetry run python scripts/chatbot.py
```

You'll see a welcome screen like this:

```
╭──────────────────────────────────────────────────────╮
│        Welcome to Memory Chatbot                     │
│                                                      │
│  I'm an AI assistant with access to your personal   │
│  memories stored in PostgreSQL.                     │
│                                                      │
│  What I can do:                                     │
│    💬 Have natural conversations with you           │
│    🧠 Remember facts about you                      │
│    🔍 Search memories using semantic similarity     │
│    📝 Create new memories from conversations        │
│    📊 Show you which memories I'm using             │
│    💾 Export clean JSON without embeddings          │
╰──────────────────────────────────────────────────────╯

User ID: 123e4567-e89b-12d3-a456-426614174000
Export directory: /path/to/memory_exports
```

### Chat Naturally

Just type your messages:

```
You: Hi! I'm studying computer science at Georgia Tech.

🔍 Searching PostgreSQL memories...
No relevant memories found

💭 Generating response using memories...

╭─────────────────────────────────────────╮
│ 🤖 Assistant                            │
│                                         │
│ Hello! It's great to meet you! How are │
│ you enjoying your computer science     │
│ program at Georgia Tech?                │
╰─────────────────────────────────────────╯

📝 Extracting facts from your message...

✨ New Memories Created
┌──────────────────────────────────────┬─────────┐
│ Memory                               │ Type    │
├──────────────────────────────────────┼─────────┤
│ User is studying computer science    │ PROJECT │
│ User attends Georgia Tech            │ PERSONAL│
└──────────────────────────────────────┴─────────┘

✓ Created 2 new memories in database
```

### Commands

Type `/help` at any time to see available commands:

- `/search <query>` - Search your memories semantically
- `/memories` - View all your memories
- `/stats` - Show statistics (memory counts, API usage, costs)
- `/export` - Export memories to clean JSON file
- `/clear` - Clear conversation history (keeps memories)
- `/exit` or `/quit` - Exit the chatbot

### Example: Search Memories

```
You: /search school and stress

🔍 Searching: "school and stress"

Search Results
┌───────┬────────┬──────────────────────────────────┐
│ Score │ Type   │ Content                          │
├───────┼────────┼──────────────────────────────────┤
│ 0.892 │ PROJECT│ User is studying computer science│
│ 0.834 │ PERSONAL│ Class registration causes anxiety│
│ 0.721 │ TASK   │ User prefers working in morning  │
└───────┴────────┴──────────────────────────────────┘
```

Even though you searched "stress", it found "anxiety" - that's semantic search!

### Example: View Memories

```
You: /memories

💾 Your Memories (12 total)

All Memories
┌─────────────────────┬──────────┬────────────────────────────────┐
│ Time                │ Type     │ Content                        │
├─────────────────────┼──────────┼────────────────────────────────┤
│ 2024-11-18 15:30:21 │ PERSONAL │ User prefers working mornings  │
│ 2024-11-18 15:28:14 │ PROJECT  │ User is studying CS at GT      │
│ 2024-11-18 15:25:03 │ PERSONAL │ User likes coffee              │
└─────────────────────┴──────────┴────────────────────────────────┘
```

### Example: Export Clean JSON

```
You: /export

📤 Exporting memories...
✓ Exported to: /path/to/memory_exports/memories_123e4567_clean.json

Total memories: 12
```

The exported JSON looks like this (NO embeddings!):

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "exported_at": "2024-11-18T15:35:42.123456",
  "total_memories": 12,
  "memories": [
    {
      "id": "abc123...",
      "content": "User is studying computer science",
      "memory_type": "project",
      "metadata": {
        "source_message": "I'm studying computer science at Georgia Tech",
        "created_at": "2024-11-18T15:28:14.123456"
      },
      "created_at": "2024-11-18T15:28:14.123456"
    }
  ]
}
```

No 1536-dimensional embedding arrays cluttering your view!

### Example: Statistics

```
You: /stats

╭─────────────────────────────────────────╮
│ 📊 Session Statistics                   │
│                                         │
│ Conversation:                           │
│   Messages Exchanged:  15               │
│   Memories Created:    12               │
│   Memories Retrieved:  23               │
│                                         │
│ Database Storage:                       │
│   Total Memories:      12               │
│   Personal Memories:   5                │
│   Project Memories:    4                │
│   Task Memories:       3                │
│   With Embeddings:     12               │
│                                         │
│ API Usage:                              │
│   Embedding Requests:  12               │
│   Total Tokens:        1,234            │
│   Cost (USD):          $0.0025          │
│                                         │
│ Export:                                 │
│   Directory: /path/to/memory_exports    │
╰─────────────────────────────────────────╯
```

## How It Works

### 1. You Send a Message

```
You: I love hiking on weekends
```

### 2. Chatbot Searches Memories

The chatbot:
1. Converts your message to a 1536-dim embedding using OpenAI `text-embedding-3-small`
2. Queries PostgreSQL with pgvector:
   ```sql
   SELECT *, 1 - (embedding <=> query_embedding) AS similarity
   FROM memories
   WHERE user_id = '...'
     AND (1 - (embedding <=> query_embedding)) >= 0.5
   ORDER BY similarity DESC
   LIMIT 5;
   ```
3. Returns top 5 most relevant memories

### 3. Chatbot Generates Response

Using the retrieved memories as context:

```python
system_prompt = """You are a helpful AI assistant.

Relevant memories about the user:
- [PERSONAL] User loves outdoor activities
- [PROJECT] User is training for a marathon
- [TASK] User went hiking last Saturday
"""
```

GPT-4o-mini uses this context to generate a personalized response.

### 4. Chatbot Extracts Facts

The chatbot asks GPT-4o-mini to extract facts:

```
Input: "I love hiking on weekends"
Output: ["User loves hiking", "User hikes on weekends"]
```

### 5. Chatbot Creates Memories

For each fact:
1. Determine memory type (PERSONAL for preferences)
2. Generate 1536-dim embedding
3. Store in PostgreSQL with metadata

### 6. Database Storage

The `memories` table now has:

```
id                                   | abc123...
user_id                              | 123e4567...
memory_type                          | personal
content                              | User loves hiking
embedding                            | [0.123, -0.456, ..., 0.789]  (1536 floats)
metadata                             | {"source_message": "I love hiking...", ...}
created_at                           | 2024-11-18 15:30:21+00
accessed_at                          | 2024-11-18 15:30:21+00
```

### 7. Export Clean Version

When you run `/export`, the service:
1. Fetches all memories for your user
2. Serializes to JSON **WITHOUT** the embedding vectors
3. Saves to `memory_exports/memories_{user_id}_clean.json`

Result: Human-readable JSON you can actually read!

## Memory Types

The chatbot automatically categorizes memories:

| Type | Description | Example | Pruning |
|------|-------------|---------|---------|
| **PERSONAL** | Identity, preferences, emotions | "User prefers working in morning" | Never |
| **PROJECT** | Goals, plans, milestones | "User is studying for finals" | 90 days |
| **TASK** | Mission details, conversation context | "Completed 20-min walk yesterday" | 30 days |

This 3-tier architecture ensures:
- Important personal facts are never deleted
- Project-related info sticks around for 90 days
- Temporary task info is pruned after 30 days (implemented in future pruning job)

## API Costs

Using OpenAI:

### Embeddings (text-embedding-3-small)
- **Cost**: $0.02 per 1M tokens
- **Typical message**: ~50 tokens
- **Example**: 100 messages = ~5,000 tokens = **$0.0001**

### Chat (GPT-4o-mini)
- **Input**: $0.15 per 1M tokens
- **Output**: $0.60 per 1M tokens
- **Typical conversation**: ~500 input + 200 output tokens
- **Example**: 100 messages = **$0.02**

**Total cost for 100 messages**: ~$0.02

## Files Created

```
packages/backend/
├── app/
│   └── services/
│       ├── embedding_service.py      # OpenAI embedding generation
│       └── memory_service.py         # Memory CRUD + search
├── scripts/
│   └── chatbot.py                    # Main chatbot CLI
├── memory_exports/                   # Created on first export
│   └── memories_{user_id}_clean.json # Clean export without embeddings
└── CHATBOT_README.md                 # This file
```

## Troubleshooting

### "Database connection failed"

**Fix:**
1. Check `DATABASE_URL` in `.env`
2. Verify Supabase is accessible
3. Run migrations: `poetry run alembic upgrade head`

### "OpenAI API error"

**Fix:**
1. Check `OPENAI_API_KEY` in `.env`
2. Verify API key is valid: https://platform.openai.com/api-keys
3. Check your OpenAI usage limits

### "No module named 'rich'"

**Fix:**
```bash
poetry install
```

### "Table 'memories' doesn't exist"

**Fix:**
```bash
poetry run alembic upgrade head
```

### "Embedding dimension mismatch"

This should never happen if using `text-embedding-3-small` with 1536 dimensions.

If you see this:
1. Check the model in `embedding_service.py` is `text-embedding-3-small`
2. Verify the dimension in the migration is `1536`

## Advanced Usage

### Custom User ID

```python
chatbot = MemoryChatbot(user_id=uuid.UUID("your-user-id-here"))
```

### Programmatic Access

```python
from app.db.session import async_session_maker
from app.services.memory_service import MemoryService

async with async_session_maker() as db:
    service = MemoryService(db)

    # Create memory
    memory = await service.create_memory(
        user_id=user_id,
        content="User loves Python",
        memory_type=MemoryType.PERSONAL
    )

    # Search
    results = await service.search_semantic(
        user_id=user_id,
        query_text="What does the user like?",
        limit=5
    )

    for memory, score in results:
        print(f"{score:.2f}: {memory.content}")
```

### Export via Service

```python
json_export = await service.export_memories(
    user_id=user_id,
    include_embeddings=False  # Clean version
)
print(json_export)
```

## Next Steps

1. **API Integration**: Add REST endpoints to `app/api/v1/memory.py`
2. **Frontend**: Create React UI for memory visualization
3. **Memory Pruning**: Implement 30/90 day pruning jobs
4. **Memory Collections**: Group related memories (goals, stressors, etc.)
5. **Advanced Search**: Filter by type, date range, metadata

## Questions?

Check the main docs:
- [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) - Technical architecture
- [SETUP.md](../../docs/SETUP.md) - Environment setup
- [CLAUDE.md](../../CLAUDE.md) - Project overview

Enjoy your memory-enhanced chatbot! 🧠💬
