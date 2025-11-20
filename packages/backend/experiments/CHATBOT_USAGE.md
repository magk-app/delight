# Conversational Chatbot with PostgreSQL Memory

## Overview

This chatbot is a complete conversational AI that stores and retrieves memories from PostgreSQL using semantic search with pgvector. It uses the experimental memory system with fact extraction, categorization, and intelligent search routing.

## Features

- 🧠 **PostgreSQL Memory Storage**: All memories stored in PostgreSQL with pgvector embeddings
- 💬 **Natural Conversations**: Powered by GPT-4o-mini with memory context
- 📝 **Automatic Fact Extraction**: Extracts discrete facts from your messages using LLM
- 🏷️ **Auto-Categorization**: Hierarchical categorization of facts (4 levels)
- 🔍 **Semantic Search**: Intelligent search routing (semantic, keyword, categorical, temporal, graph, hybrid)
- 📊 **Real-time Visibility**: Shows which memories are retrieved and created
- 💾 **3-Tier Memory**: Personal (never pruned), Project (90d), Task (30d)

## Prerequisites

1. **PostgreSQL with pgvector extension**

   - Database must have pgvector installed
   - Memory tables must be created (run migrations)

2. **Environment Variables**

   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
   OPENAI_API_KEY=sk-proj-...
   ```

3. **Dependencies**
   ```bash
   cd packages/backend
   poetry install
   ```

## Usage

### Run the Chatbot

```bash
cd packages/backend
poetry run python experiments/cli/chatbot.py
```

### Commands

- **Just chat!** - Type naturally to have conversations
- `/search <query>` - Search memories semantically
- `/memories` - View all your memories
- `/stats` - Show statistics (DB counts, API usage, costs)
- `/clear` - Clear conversation history
- `/help` - Show help
- `/exit` - Exit

### Example Conversation

```
You: I'm studying computer science at Georgia Tech

🔍 Searching memories...
No relevant memories found

💭 Generating response...
🤖 Assistant: That's great! How are you enjoying your CS program?

📝 Extracting facts from your message...
✨ New Memories Created
┌───────────────────────────────────┬──────────────────────────────┐
│ Content                           │ Categories                   │
├───────────────────────────────────┼──────────────────────────────┤
│ User is studying computer science │ personal → education → cs    │
│ User attends Georgia Tech         │ personal → location → school │
└───────────────────────────────────┴──────────────────────────────┘
✓ Created 2 new memories in PostgreSQL
```

### Search Example

```
You: /search programming

🔍 Searching: "programming"

Search Results
┌────────┬──────────┬──────────────────────────────────┐
│ Score  │ Type     │ Content                          │
├────────┼──────────┼──────────────────────────────────┤
│ 0.892  │ PERSONAL │ Prefers TypeScript over JS       │
│ 0.821  │ PROJECT  │ Using FastAPI for backend        │
└────────┴──────────┴──────────────────────────────────┘
```

## How It Works

1. **Memory Retrieval**: When you send a message, the chatbot:

   - Generates an embedding for your message
   - Searches PostgreSQL for relevant memories using semantic similarity
   - Uses intelligent routing to select the best search strategy

2. **Response Generation**:

   - Builds context from retrieved memories
   - Sends to GPT-4o-mini with memory context
   - Generates personalized response

3. **Memory Creation**:
   - Extracts discrete facts from your message using LLM
   - Categorizes each fact hierarchically
   - Generates embeddings for semantic search
   - Stores in PostgreSQL with metadata

## Architecture

The chatbot uses the experimental memory system:

- **MemoryService** (`experiments/memory/memory_service.py`): Orchestrates fact extraction, categorization, and search
- **FactExtractor**: Extracts multiple facts from complex messages
- **DynamicCategorizer**: Hierarchical categorization (4 levels)
- **SearchRouter**: Intelligent search strategy selection
- **EmbeddingService**: OpenAI embedding generation

## Database Schema

Memories are stored in:

- `memory_collections`: Collections grouped by type (Personal/Project/Task)
- `memories`: Individual memories with:
  - `content`: Human-readable text
  - `embedding`: 1536-dim vector (pgvector)
  - `metadata`: JSONB with categories, fact types, etc.

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
poetry run python experiments/database/connection.py
```

### No Memories Found

- Check that migrations have been run
- Verify user_id exists in database
- Try creating a memory manually first

### OpenAI API Errors

- Verify `OPENAI_API_KEY` is set correctly
- Check API quota/limits
- Review error messages in console

## Cost Estimates

- **Embeddings**: ~$0.02 per 1M tokens (text-embedding-3-small)
- **Chat**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens (gpt-4o-mini)
- **Fact Extraction**: ~$0.15 per 1M tokens (gpt-4o-mini)
- **Categorization**: ~$0.15 per 1M tokens (gpt-4o-mini)

Typical conversation: ~$0.01-0.05 per message (depending on message length and facts extracted)

## Next Steps

- Add REST API endpoints for memory management
- Create React UI for memory visualization
- Implement automatic memory pruning (30/90 day lifecycle)
- Add memory collections for grouping related memories
- Export memories to clean JSON (without embeddings)
