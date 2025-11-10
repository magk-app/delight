# Technology Stack Details

### Core Technologies

**Frontend:**

- **Next.js 15** - React framework with App Router, Server Components, streaming
- **React 19** - UI library with latest hooks (`useActionState`, `useOptimistic`)
- **TypeScript** - Type safety across frontend
- **Tailwind CSS** - Utility-first styling with theme system
- **shadcn/ui** - Accessible component primitives (Radix UI + Tailwind)
- **Framer Motion** - Animation library for character breathing, transitions

**Backend:**

- **FastAPI** - Async Python web framework
- **SQLAlchemy 2.0 (async)** - ORM with async support
- **PostgreSQL 15+** - Primary database
- **Pydantic** - Data validation and settings
- **Uvicorn** - ASGI server

**AI & Memory:**

- **LangGraph** - Stateful agent orchestration
- **LangChain** - LLM integration, memory abstractions
- **PostgreSQL pgvector** - Vector storage extension (unified with main DB)
- **OpenAI GPT-4o-mini** - Primary LLM for chat, personas, quest generation (cost-effective)
- **OpenAI GPT-4o** - Premium narrative generation (less frequent, higher quality)
- **cardiffnlp/twitter-roberta-base-emotion** - Open source emotion classification (7 emotions)

**Background Jobs:**

- **ARQ** - Async Redis queue
- **Redis** - Queue backend, caching

**Real-Time:**

- **Server-Sent Events (SSE)** - AI response streaming
- **HTTP REST** - User actions, CRUD operations

**File Storage:**

- **S3-compatible** (AWS S3, MinIO, etc.) - Evidence uploads

### Integration Points

1. **Frontend ↔ Backend:** REST API + SSE streaming

   - REST: `POST /api/v1/companion/chat`, `GET /api/v1/missions`
   - SSE: `GET /api/v1/sse/companion/stream` for token-by-token responses

2. **Backend ↔ AI:** LangGraph agents orchestrate LLM calls

   - Eliza agent: `backend/app/agents/eliza_agent.py`
   - Character agents: `backend/app/agents/character_agents.py`
   - Narrative agent: `backend/app/agents/narrative_agent.py`

3. **Backend ↔ Memory:** PostgreSQL pgvector for vector search, unified with structured data

   - Memory service: `backend/app/services/memory_service.py`
   - Vector collections: personal, project, task memories (stored in PostgreSQL tables with vector columns)

4. **Backend ↔ Background Jobs:** ARQ workers for async processing
   - Quest generation: `backend/app/workers/quest_generator.py`
   - Nudge scheduling: `backend/app/workers/nudge_scheduler.py`

---
