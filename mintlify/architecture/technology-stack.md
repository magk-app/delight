---
title: Technology Stack
description: Detailed breakdown of technologies, frameworks, and tools used in Delight
---

# Technology Stack Details

## Core Technologies

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.x | React framework with App Router, Server Components, streaming |
| **React** | 19.x | UI library with latest hooks (`useActionState`, `useOptimistic`) |
| **TypeScript** | Latest | Type safety across frontend |
| **Tailwind CSS** | Latest | Utility-first styling with theme system |
| **shadcn/ui** | Latest | Accessible component primitives (Radix UI + Tailwind) |
| **Framer Motion** | Latest | Animation library for character breathing, transitions |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | Latest | Async Python web framework |
| **SQLAlchemy** | 2.0+ (async) | ORM with async support |
| **PostgreSQL** | 15+ | Primary database |
| **Pydantic** | Latest | Data validation and settings |
| **Uvicorn** | Latest | ASGI server |
| **Alembic** | Latest | Database migrations |

### AI & Memory

| Technology | Version | Purpose |
|------------|---------|---------|
| **LangGraph** | Latest | Stateful agent orchestration |
| **LangChain** | Latest | LLM integration, memory abstractions |
| **pgvector** | 0.5+ | Vector storage extension (unified with main DB) |
| **OpenAI GPT-4o-mini** | Latest | Primary LLM for chat, personas, quest generation (cost-effective) |
| **OpenAI GPT-4o** | Latest | Premium narrative generation (less frequent, higher quality) |
| **text-embedding-3-small** | Latest | Text embeddings for semantic search (1536 dimensions) |
| **cardiffnlp/roberta** | Latest | Open source emotion classification (7 emotions) |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Supabase** | Managed PostgreSQL with pgvector pre-installed |
| **Clerk** | Managed authentication (OAuth, 2FA, magic links) |
| **ARQ** | Async Redis queue for background jobs |
| **Redis** | Queue backend, caching |
| **S3-compatible** | Evidence uploads (AWS S3, MinIO, etc.) |
| **Sentry** | Error tracking and performance monitoring |

## Integration Points

### 1. Frontend ↔ Backend

- **REST API:** Standard CRUD operations
  - `POST /api/v1/companion/chat`
  - `GET /api/v1/missions`
  - `POST /api/v1/missions/{id}/complete`

- **SSE (Server-Sent Events):** Token-by-token AI streaming
  - `GET /api/v1/sse/companion/stream`

### 2. Backend ↔ AI Layer

LangGraph agents orchestrate LLM calls:

- **Eliza agent:** `backend/app/agents/eliza_agent.py`
- **Character agents:** `backend/app/agents/character_agents.py`
- **Narrative agent:** `backend/app/agents/narrative_agent.py`

### 3. Backend ↔ Memory

PostgreSQL pgvector for vector search, unified with structured data:

- **Memory service:** `backend/app/services/memory_service.py`
- **Vector collections:** Personal, project, task memories (stored in PostgreSQL tables with vector columns)

### 4. Backend ↔ Background Jobs

ARQ workers for async processing:

- **Quest generation:** `backend/app/workers/quest_generator.py`
- **Nudge scheduling:** `backend/app/workers/nudge_scheduler.py`

## Development Tools

- **Poetry:** Python dependency management
- **pnpm:** Frontend package management (monorepo support)
- **Docker Compose:** Local development (PostgreSQL + Redis)
- **pytest:** Backend testing
- **Playwright:** Frontend E2E testing
- **GitHub Actions:** CI/CD automation

## Why These Choices?

See [Architecture Decision Records](/architecture/decision-records) for detailed rationale behind each technology choice.
