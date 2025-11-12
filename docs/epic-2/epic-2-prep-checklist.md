# Epic 2 Prep Checklist - Parallel Work While Code Review Runs

**Goal:** Prepare for Epic 2 development while Story 1.3 code review is in progress.

**Status:** ✅ Ready to start - All prerequisites from Epic 1 are complete

---

## ✅ Quick Wins (15-30 minutes each)

### 1. Verify Dependencies Are Installed

- [ ] Check LangChain/LangGraph versions in `pyproject.toml` (already installed ✅)
- [ ] Verify pgvector Python package: `poetry show pgvector`
- [ ] Verify transformers/torch: `poetry show transformers torch`
- [ ] Test OpenAI API key access (if you have one set up)

**Command:**

```bash
cd packages/backend
poetry show langchain langgraph langchain-postgres pgvector transformers torch
```

### 2. Verify pgvector Extension in Database

- [ ] Run verification script: `poetry run python scripts/verify_pgvector.py`
- [ ] Should show: ✅ pgvector extension is ENABLED

**Note:** Already enabled in migration 001, but good to verify.

### 3. Research & Documentation Review

- [ ] Read LangGraph quickstart: https://langchain-ai.github.io/langgraph/
- [ ] Review LangChain PostgresVectorStore docs: https://python.langchain.com/docs/integrations/vectorstores/pgvector
- [ ] Bookmark OpenAI embedding API docs: https://platform.openai.com/docs/guides/embeddings
- [ ] Review emotion model: https://huggingface.co/cardiffnlp/twitter-roberta-base-emotion-multilingual-latest

---

## 📋 Story Planning & Context (30-60 minutes)

### 4. Create Story 2.1 Draft File

- [ ] Create `docs/stories/2-1-set-up-postgresql-pgvector-and-memory-schema.md`
- [ ] Copy structure from Story 1.3 as template
- [ ] Fill in acceptance criteria from epic file
- [ ] Add technical notes about:
  - Memory table schema (memories, memory_collections)
  - Vector dimension (1536 for OpenAI text-embedding-3-small)
  - HNSW index creation
  - Enum types for memory_type

**Template location:** Use `docs/stories/1-3-integrate-clerk-authentication-system.md` as reference

### 5. Design Memory Schema (Planning)

- [ ] Sketch out `memories` table structure:
  ```sql
  - id UUID PRIMARY KEY
  - user_id UUID FK → users(id)
  - memory_type ENUM('personal', 'project', 'task')
  - content TEXT
  - embedding VECTOR(1536)
  - metadata JSONB
  - created_at TIMESTAMP
  - accessed_at TIMESTAMP
  ```
- [ ] Sketch out `memory_collections` table:
  ```sql
  - id UUID PRIMARY KEY
  - user_id UUID FK → users(id)
  - collection_type VARCHAR
  - name VARCHAR
  - description TEXT
  ```
- [ ] Plan indexes:
  - HNSW index on embedding for similarity search
  - Index on (user_id, memory_type) for filtering
  - Index on accessed_at for pruning queries

### 6. Research Embedding Generation Strategy

- [ ] Decide on embedding model: OpenAI `text-embedding-3-small` (1536 dim)
- [ ] Plan embedding generation:
  - Where: Backend service layer
  - When: On memory creation
  - Caching: Consider caching embeddings for identical content
- [ ] Estimate costs: ~$0.02 per 1M tokens (very cheap)

---

## 🏗️ Infrastructure Setup (Can start now)

### 7. Create Directory Structure

- [ ] Create `packages/backend/app/services/memory_service.py` (empty file for now)
- [ ] Create `packages/backend/app/agents/eliza_agent.py` (empty file for now)
- [ ] Create `packages/backend/app/services/emotion_service.py` (empty file for now)
- [ ] Create `packages/backend/app/models/memory.py` (empty file for now)
- [ ] Create `packages/backend/app/schemas/memory.py` (empty file for now)

**Command:**

```bash
cd packages/backend/app
touch services/memory_service.py services/emotion_service.py
touch agents/eliza_agent.py
touch models/memory.py schemas/memory.py
```

### 8. Set Up OpenAI API Key (If not done)

- [ ] Get OpenAI API key from https://platform.openai.com/api-keys
- [ ] Add to `packages/backend/.env`:
  ```bash
  OPENAI_API_KEY=sk-...
  ```
- [ ] Add to `packages/backend/.env.example`:
  ```bash
  OPENAI_API_KEY=sk-...  # Required for embeddings and LLM
  ```
- [ ] Update `packages/backend/app/core/config.py` to include:
  ```python
  OPENAI_API_KEY: str
  ```

### 9. Test Database Connection for Vector Operations

- [ ] Create test script: `packages/backend/scripts/test_vector_operations.py`
- [ ] Test basic vector operations:
  ```python
  # Test creating a vector column
  # Test similarity search query
  # Verify pgvector functions work
  ```

---

## 📚 Learning & Research (Background reading)

### 10. LangGraph Learning

- [ ] Watch LangGraph intro video (if available)
- [ ] Read LangGraph state management docs
- [ ] Understand StateGraph pattern for Eliza agent
- [ ] Plan agent nodes:
  - `receive_input`
  - `recall_context`
  - `reason`
  - `respond`
  - `store_memory`

### 11. Memory Architecture Deep Dive

- [ ] Review 3-tier memory system:
  - Personal: Long-term identity, preferences
  - Project: Goals, plans, progress
  - Task: Short-term actions (pruned after 30 days)
- [ ] Understand hybrid search:
  - Vector similarity (semantic)
  - Time-weighted recency
  - Access frequency
- [ ] Plan time decay function: `score * (1 + log(1 + days_since_access)^-1)`

### 12. Emotion Detection Research

- [ ] Review Hugging Face model card
- [ ] Test model locally (optional):
  ```python
  from transformers import pipeline
  emotion_classifier = pipeline(
      "text-classification",
      model="cardiffnlp/twitter-roberta-base-emotion-multilingual-latest"
  )
  result = emotion_classifier("I'm feeling great today!")
  ```
- [ ] Plan integration points:
  - When: In `receive_input` node
  - Where: Update user_preferences table
  - How: Store emotion scores in JSONB

---

## 🎨 Frontend Prep (For Story 2.5)

### 13. Research SSE Streaming in Next.js

- [ ] Review Next.js Server-Sent Events docs
- [ ] Plan frontend hook: `useSSE()` or use existing library
- [ ] Research chat UI libraries:
  - shadcn/ui components
  - Framer Motion for animations
  - React hooks for message state

### 14. Design Chat UI Mockup (Mental/Notes)

- [ ] Plan component structure:
  - `CompanionChat.tsx` - Main chat container
  - `MessageList.tsx` - Scrollable message history
  - `MessageInput.tsx` - Input field with send button
  - `TypingIndicator.tsx` - Loading state
- [ ] Plan animations:
  - Breathing effect (idle state)
  - Message fade-in
  - Typing indicator pulse

---

## 🔧 Environment & Tooling

### 15. Set Up Development Environment

- [ ] Ensure Redis is running (for ARQ workers later):
  ```bash
  # Check if Redis is in docker-compose.yml
  docker-compose up redis -d
  ```
- [ ] Verify database connection works
- [ ] Test Alembic migrations still work: `poetry run alembic current`

### 16. Create Epic 2 Branch (After code review merges)

- [ ] Branch name: `epic-2-companion-memory-system`
- [ ] Or per-story branches: `2-1-pgvector-memory-schema`
- [ ] Update `docs/sprint-status.yaml` when starting

---

## 📝 Documentation Prep

### 17. Review Architecture Docs

- [ ] Read `docs/architecture/data-architecture.md`
- [ ] Review memory system patterns
- [ ] Understand how Epic 2 fits into overall architecture

### 18. Create Epic 2 Context File (Optional)

- [ ] Create `docs/stories/epic-2-context.md` with:
  - Key decisions
  - Dependencies
  - Technical notes
  - Open questions

---

## ⚡ Quick Test Scripts (Optional)

### 19. Create Test Embedding Script

- [ ] Create `packages/backend/scripts/test_embeddings.py`:

  ```python
  from openai import OpenAI
  client = OpenAI()

  response = client.embeddings.create(
      model="text-embedding-3-small",
      input="Hello, world!"
  )
  print(f"Embedding dimension: {len(response.data[0].embedding)}")
  # Should be 1536
  ```

### 20. Test pgvector Queries

- [ ] Create `packages/backend/scripts/test_pgvector.py`:
  ```python
  # Test creating a test table with vector column
  # Test similarity search query
  # Verify HNSW index creation
  ```

---

## 🎯 Priority Order

**Do First (While Review Runs):**

1. ✅ Verify dependencies (5 min)
2. ✅ Verify pgvector extension (2 min)
3. ✅ Create directory structure (5 min)
4. ✅ Set up OpenAI API key (10 min)
5. ✅ Create Story 2.1 draft (30 min)

**Do Next (If Review Takes Longer):** 6. Design memory schema (30 min) 7. Research LangGraph (1 hour) 8. Test embedding generation (15 min)

**Background Reading (Anytime):**

- LangGraph docs
- Memory architecture patterns
- Emotion detection model

---

## ✅ Completion Criteria

You're ready to start Epic 2 when:

- [ ] Story 1.3 is merged to main
- [ ] Story 2.1 draft file exists
- [ ] Directory structure created
- [ ] OpenAI API key configured
- [ ] pgvector verified working
- [ ] Basic understanding of LangGraph

---

## 📌 Notes

- **pgvector is already enabled** in migration 001, so Story 2.1 is mostly about creating tables
- **Dependencies are already installed** in pyproject.toml
- **Epic 2 doesn't depend on Story 1.3** for database/auth setup, but Story 2.4 (chat API) will need auth
- **You can start Story 2.1 immediately** after code review merges

---

**Last Updated:** 2025-11-11
**Status:** Ready for parallel prep work
