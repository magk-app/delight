# Architecture: Delight

**Date:** 2025-11-09  
**Author:** Winston (Architect) with Jack  
**Project:** Delight - Self-Improvement Companion Platform  
**Status:** Architecture Complete - Ready for Implementation

---

## Executive Summary

Delight is a self-improvement companion platform that blends emotionally-aware AI coaching with narrative world-building. The architecture is designed to support a **living narrative engine** where real-world goal achievement drives personalized story progression, multi-character AI interactions, and adaptive quest systems. The system prioritizes **premium AI experience** with a target operational cost of **$0.50/user/day** (pricing: $1/day subscription + pay-as-you-go for premium features).

**Key Architectural Approach:**

- **Frontend:** Next.js 15 + React 19 for modern, performant UI with streaming support
- **Backend:** FastAPI for async-first API layer optimized for AI orchestration
- **AI Layer:** LangGraph + LangChain for stateful multi-agent character system
- **Memory:** PostgreSQL with pgvector extension for unified vector + structured storage
- **Real-Time:** Hybrid SSE + HTTP for AI streaming and user actions, WebSocket for world state updates
- **Novel Patterns:** Living narrative engine, character-initiated interactions, pre-planned hidden quest system

---

## Project Initialization

**First Implementation Story:** Initialize monorepo structure and core dependencies

```bash
# Frontend initialization
cd packages/frontend
npx create-next-app@latest . --typescript --tailwind --app --eslint --src-dir

# Backend initialization
cd packages/backend
poetry init
poetry add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg pydantic-settings
poetry add langchain langgraph langchain-postgres pgvector
poetry add arq redis sentry-sdk
```

This establishes:

- Next.js 15 with App Router, TypeScript, Tailwind CSS
- FastAPI with async SQLAlchemy
- LangChain/LangGraph for AI orchestration
- PostgreSQL with pgvector extension for vector storage
- ARQ for background jobs
- Sentry for error tracking and observability

---

## Decision Summary

| Category               | Decision              | Version               | Affects Epics                     | Rationale                                  |
| ---------------------- | --------------------- | --------------------- | --------------------------------- | ------------------------------------------ |
| **Frontend Framework** | Next.js               | 15.x                  | All frontend epics                | React ecosystem, streaming support, SEO    |
| **UI Library**         | React                 | 19.x                  | All frontend epics                | Latest React features, Server Components   |
| **Component Library**  | shadcn/ui + Radix UI  | Latest                | UI components                     | Copy-paste components, theme customization |
| **Styling**            | Tailwind CSS          | Latest                | All frontend epics                | Utility-first, theme system support        |
| **Animation**          | Framer Motion         | Latest                | Character animations, transitions | Declarative, performant, React-native      |
| **Backend Framework**  | FastAPI               | Latest                | All backend epics                 | Async-first, AI ecosystem integration      |
| **AI Orchestration**   | LangGraph + LangChain | Latest                | Companion, Narrative Engine       | Stateful agents, multi-character support   |
| **Vector Storage**     | PostgreSQL pgvector   | PG 15+, pgvector 0.5+ | Memory, Companion                 | Unified storage, production-ready          |
| **Database**           | PostgreSQL            | 15+                   | All data persistence              | Production-ready, async support, pgvector  |
| **ORM**                | SQLAlchemy (async)    | 2.0+                  | Data models                       | Async support, mature ecosystem            |
| **Background Jobs**    | ARQ                   | Latest                | Quest generation, nudges          | Async-native, Redis-based                  |
| **Real-Time**          | SSE + WebSocket       | Native                | AI streaming, world updates       | SSE for AI, WebSocket for world state      |
| **File Storage**       | S3-compatible         | -                     | Evidence uploads                  | Scalable, cost-effective                   |
| **Observability**      | Sentry                | Latest                | Error tracking, performance       | Session replay, performance monitoring     |

---

## Project Structure

```
delight/
├── packages/
│   ├── frontend/                    # Next.js 15 application
│   │   ├── src/
│   │   │   ├── app/                 # App Router pages
│   │   │   │   ├── (auth)/          # Auth routes
│   │   │   │   ├── (world)/         # World/zone routes
│   │   │   │   │   ├── arena/
│   │   │   │   │   ├── observatory/
│   │   │   │   │   └── commons/
│   │   │   │   ├── companion/       # Eliza chat interface
│   │   │   │   ├── missions/        # Mission views
│   │   │   │   └── progress/        # Dashboard, DCI
│   │   │   ├── components/
│   │   │   │   ├── ui/              # shadcn/ui components
│   │   │   │   ├── companion/       # Eliza, character components
│   │   │   │   ├── missions/        # Mission cards, progress bars
│   │   │   │   ├── world/           # Zone components, time display
│   │   │   │   └── narrative/       # Story text, dialogue
│   │   │   ├── lib/
│   │   │   │   ├── api/             # API client, SSE handlers
│   │   │   │   ├── hooks/           # React hooks
│   │   │   │   ├── utils/           # Utilities
│   │   │   │   └── themes/          # Theme system (medieval, sci-fi, etc.)
│   │   │   └── types/               # TypeScript types
│   │   ├── public/                  # Static assets
│   │   ├── tailwind.config.ts       # Tailwind + theme config
│   │   └── package.json
│   │
│   ├── backend/                     # FastAPI application
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── companion.py # Eliza chat endpoints
│   │   │   │   │   ├── missions.py  # Mission CRUD
│   │   │   │   │   ├── narrative.py # Story generation
│   │   │   │   │   ├── progress.py  # DCI, analytics
│   │   │   │   │   └── world.py     # World state, zones
│   │   │   │   └── sse.py           # SSE streaming endpoints
│   │   │   ├── core/
│   │   │   │   ├── config.py        # Settings, env vars
│   │   │   │   ├── security.py      # Auth, JWT
│   │   │   │   └── dependencies.py  # FastAPI dependencies
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   │   ├── user.py
│   │   │   │   ├── mission.py
│   │   │   │   ├── character.py
│   │   │   │   ├── narrative.py
│   │   │   │   └── progress.py
│   │   │   ├── schemas/             # Pydantic schemas
│   │   │   │   └── ...
│   │   │   ├── services/
│   │   │   │   ├── companion_service.py    # Eliza orchestration
│   │   │   │   ├── narrative_service.py    # Story generation
│   │   │   │   ├── mission_service.py      # Quest logic
│   │   │   │   ├── memory_service.py       # Chroma integration
│   │   │   │   └── character_service.py    # Character AI
│   │   │   ├── agents/              # LangGraph agents
│   │   │   │   ├── eliza_agent.py   # Main companion agent
│   │   │   │   ├── character_agents.py # Lyra, Thorne, Elara
│   │   │   │   └── narrative_agent.py # Story generation agent
│   │   │   ├── workers/             # ARQ background jobs
│   │   │   │   ├── quest_generator.py
│   │   │   │   ├── nudge_scheduler.py
│   │   │   │   └── memory_consolidation.py
│   │   │   └── db/                  # Database setup
│   │   │       ├── base.py          # Base model, session
│   │   │       └── migrations/      # Alembic migrations
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── pyproject.toml           # Poetry dependencies
│   │   └── .env.example
│   │
│   └── shared/                      # Shared TypeScript types
│       └── types/
│           ├── mission.ts
│           ├── character.ts
│           ├── narrative.ts
│           └── progress.ts
│
├── docs/                            # Documentation
│   ├── architecture.md              # This file
│   ├── product-brief-Delight-2025-11-09.md
│   └── ux-design-specification.md
│
└── docker-compose.yml               # Local dev environment
```

---

## Epic to Architecture Mapping

| Epic                          | Architecture Component                                     | Location                                                                             |
| ----------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Companion & Memory**        | LangGraph agents (`eliza_agent.py`), Chroma memory service | `backend/app/agents/`, `backend/app/services/memory_service.py`                      |
| **Goal & Mission Management** | Mission service, PostgreSQL models                         | `backend/app/services/mission_service.py`, `backend/app/models/mission.py`           |
| **Narrative Engine**          | Narrative service, LangGraph narrative agent               | `backend/app/services/narrative_service.py`, `backend/app/agents/narrative_agent.py` |
| **Progress & Analytics**      | Progress service, DCI calculation                          | `backend/app/services/progress_service.py`, `frontend/src/app/progress/`             |
| **Nudge & Outreach**          | ARQ workers, scheduled jobs                                | `backend/app/workers/nudge_scheduler.py`                                             |
| **World State & Time**        | World service, time-aware state                            | `backend/app/services/world_service.py`, `backend/app/api/v1/world.py`               |
| **Evidence & Reflection**     | File upload service, S3 integration                        | `backend/app/services/evidence_service.py`                                           |
| **User Onboarding**           | Auth service, onboarding flow                              | `backend/app/core/security.py`, `frontend/src/app/(auth)/`                           |

---

## Technology Stack Details

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
- **OpenAI/Anthropic** - LLM providers (configurable)

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

## Novel Pattern Designs

### Pattern 1: Living Narrative Engine

**Purpose:** Generate personalized stories that adapt to real-world user progress, with pre-planned narrative beats that unlock based on user actions.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ Narrative Service (LangGraph Agent)                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Story State Machine:                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Chapter 1│───▶│ Chapter 2│───▶│ Chapter 3│          │
│  └──────────┘    └──────────┘    └──────────┘          │
│       │                │                │                │
│       ▼                ▼                ▼                │
│  ┌──────────────────────────────────────────┐           │
│  │ Pre-Planned Hidden Quests (3-5 per story)│           │
│  │ - Trigger conditions (e.g., 20 missions) │           │
│  │ - Narrative content (pre-generated)      │           │
│  │ - Rewards (Essence, relationships, zones)│           │
│  └──────────────────────────────────────────┘           │
│                                                           │
│  Components:                                              │
│  - Narrative Agent (LangGraph): Generates story beats    │
│  - Story State DB (PostgreSQL): Tracks chapter, quests   │
│  - Trigger Monitor (ARQ): Checks conditions, unlocks     │
│  - Template System: Scenario-specific narrative vars     │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

- **Service:** `backend/app/services/narrative_service.py`
- **Agent:** `backend/app/agents/narrative_agent.py` (LangGraph state machine)
- **Database:** `narrative_states` table (user_id, chapter, hidden_quests JSON)
- **Workers:** `backend/app/workers/quest_generator.py` (pre-generates 3-5 hidden quests at story start)

**Data Flow:**

1. User starts story → Narrative service generates 3-5 hidden quests, stores in DB
2. User completes missions → Trigger monitor (ARQ worker) checks conditions
3. Condition met → Hidden quest unlocks, narrative content served
4. User progresses → Story state advances, new chapters unlock

**Scenario Template Storage:**

Multiple narrative scenarios (Modern Reality, Medieval Fantasy, etc.) are stored using PostgreSQL JSONB for flexibility and dynamic generation:

```sql
CREATE TABLE scenario_templates (
  id UUID PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  theme VARCHAR(50) NOT NULL,  -- 'modern', 'medieval', 'scifi', etc.
  narrative_arc JSONB NOT NULL,  -- Chapter structure, story beats, act progression
  character_prompts JSONB NOT NULL,  -- Personality definitions for each character
  hidden_quests JSONB NOT NULL,  -- Pre-planned surprises with trigger conditions
  time_rules JSONB,  -- Zone availability by time (optional overrides)
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scenario_theme ON scenario_templates(theme);
```

**Template Structure Example:**

```json
{
  "narrative_arc": {
    "act_1": {
      "title": "Arrival",
      "chapters": ["The Journey Begins", "First Steps"],
      "progression_trigger": {"missions_completed": 5}
    },
    "act_2": {...},
    "act_3": {...}
  },
  "character_prompts": {
    "eliza": "You are Eliza, a wise and empathetic guide...",
    "lyra": "You are Lyra, master artisan of the Guild..."
  },
  "hidden_quests": [
    {
      "id": "relentless_achievement",
      "trigger": {"streak_days": 20, "attribute": "craft"},
      "title": "The Relentless",
      "narrative": "...",
      "rewards": {"essence": 500, "title": "The Relentless"}
    }
  ]
}
```

This approach allows:

- Easy addition of new scenarios without code changes
- User-specific narrative customization
- Version control for narrative content
- Dynamic template selection based on user preferences

---

### Pattern 2: Multi-Character AI System

**Purpose:** Manage multiple AI characters (Eliza, Lyra, Thorne, Elara) with distinct personalities, relationship levels, and character-initiated interactions.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ Character Orchestration Layer                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Eliza Agent  │  │ Lyra Agent   │  │ Thorne Agent │  │
│  │ (Protagonist)│  │ (Craft)      │  │ (Health)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                              │
│                   ┌────────▼────────┐                    │
│                   │ Character State │                    │
│                   │ - Personality   │                    │
│                   │ - Relationship  │                    │
│                   │ - Conversation  │                    │
│                   │   History       │                    │
│                   └─────────────────┘                    │
│                            │                              │
│                   ┌────────▼────────┐                    │
│                   │ Initiation      │                    │
│                   │ Scheduler       │                    │
│                   │ (ARQ)           │                    │
│                   └─────────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

- **Agents:** `backend/app/agents/eliza_agent.py`, `backend/app/agents/character_agents.py`
- **Service:** `backend/app/services/character_service.py`
- **Database:** `characters` table (personality JSON, relationship_level INT)
- **Memory:** Separate PostgreSQL vector tables per character for conversation history
- **Scheduler:** `backend/app/workers/character_initiator.py` (proactive character interactions)

**Character-Initiated Flow:**

1. ARQ scheduler checks user activity patterns (e.g., 2 weeks of Craft focus)
2. Character service selects appropriate character (e.g., Elara for Growth)
3. Character agent generates proactive message with context
4. User receives notification: "Elara seeks you in the Observatory"
5. Conversation starts with character's personality and relationship level

---

### Pattern 3: Time-Aware World State

**Purpose:** World state (zone availability, character presence) changes based on real-world time, with user-configurable overrides.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ World State Service                                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────┐           │
│  │ Time Rules Engine                         │           │
│  │ - Default: Arena closes 9pm, opens 6am   │           │
│  │ - User Override: Custom productive hours │           │
│  │ - Timezone: User's local time            │           │
│  └──────────────────────────────────────────┘           │
│                            │                              │
│         ┌──────────────────┼──────────────────┐          │
│         │                  │                  │          │
│    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐    │
│    │ Arena   │      │Observatory│     │  Commons  │    │
│    │(Health) │      │ (Growth)  │     │(Connection)│    │
│    └─────────┘      └───────────┘     └───────────┘    │
│         │                  │                  │          │
│    ┌────▼──────────────────▼──────────────────▼────┐    │
│    │ World State Cache (Redis)                      │    │
│    │ - Zone availability                            │    │
│    │ - Character presence                           │    │
│    │ - Time-based events                            │    │
│    └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

- **Service:** `backend/app/services/world_service.py`
- **Database:** `user_preferences` table (timezone, custom_hours JSON)
- **Cache:** Redis for world state (TTL: 15 minutes)
- **Frontend:** WebSocket connection for real-time world state updates + fallback polling

---

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Conventions

**Backend (Python):**

- **Modules:** `snake_case` (e.g., `companion_service.py`, `mission_service.py`)
- **Classes:** `PascalCase` (e.g., `CompanionService`, `MissionModel`)
- **Functions:** `snake_case` (e.g., `generate_quest`, `calculate_dci`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_MISSION_DURATION`)

**Frontend (TypeScript):**

- **Components:** `PascalCase` (e.g., `MissionCard.tsx`, `ElizaChat.tsx`)
- **Files:** Match component name (e.g., `MissionCard.tsx`)
- **Hooks:** `camelCase` with `use` prefix (e.g., `useMission`, `useCompanion`)
- **Utils:** `camelCase` (e.g., `formatEssence`, `calculateStreak`)

**API Endpoints:**

- **REST:** `/api/v1/{resource}/{id?}` (e.g., `/api/v1/missions`, `/api/v1/missions/123`)
- **SSE:** `/api/v1/sse/{stream_type}` (e.g., `/api/v1/sse/companion/stream`)
- **Actions:** `POST /api/v1/{resource}/{action}` (e.g., `POST /api/v1/missions/start`)

**Database:**

- **Tables:** `snake_case`, plural (e.g., `missions`, `character_relationships`)
- **Columns:** `snake_case` (e.g., `user_id`, `created_at`)
- **Foreign Keys:** `{table}_id` (e.g., `mission_id`, `character_id`)
- **JSON columns:** Use `JSON` type (not `JSONB`) for flexible data structures

### Code Organization

**Backend Structure:**

```
app/
├── api/v1/          # API endpoints (thin controllers)
├── services/        # Business logic
├── agents/          # LangGraph agents
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
└── workers/         # ARQ background jobs
```

**Frontend Structure:**

```
src/
├── app/             # Next.js App Router pages
├── components/      # React components (organized by feature)
├── lib/             # Utilities, hooks, API client
└── types/           # TypeScript type definitions
```

**Testing:**

- **Backend:** `tests/` directory mirroring `app/` structure
- **Frontend:** `__tests__/` co-located with components, `e2e/` for Playwright

### Error Handling

**Backend:**

- Use FastAPI's `HTTPException` for API errors
- Custom exceptions: `DelightException` base class
- Error responses: `{"error": {"type": "...", "message": "...", "code": "..."}}`
- Log errors with context (user_id, request_id) using structured logging

**Frontend:**

- API errors: Display user-friendly messages via toast notifications (shadcn/ui)
- Network errors: Retry with exponential backoff
- Validation errors: Inline form errors

### Logging Strategy

**Backend:**

- **Library:** `structlog` for structured logging
- **Format:** JSON in production, human-readable in dev
- **Levels:** DEBUG (dev), INFO (production), ERROR (always)
- **Context:** Include `user_id`, `request_id`, `agent_name` in logs

**Frontend:**

- **Console:** Development only
- **Production:** Sentry for error tracking, performance monitoring, and user session replay

### Background Job Reliability

**Retry Strategy:**

- Quest generation: 3 retries with exponential backoff (2s, 4s, 8s)
- Nudge scheduling: 2 retries with 5s delay
- Character initiation: 3 retries with exponential backoff
- Memory consolidation: 5 retries (can run delayed without user impact)

**Dead Letter Queue:**

- Failed jobs after max retries go to Redis dead letter queue
- Admin dashboard shows failed jobs with retry button
- Critical failures (quest generation) trigger Sentry alert

**Job Monitoring:**

- Track job completion rate, average duration per job type
- Alert on queue depth > 1000 or job age > 5 minutes
- Dashboard for job status by type

---

## Data Architecture

### Core Models

**User:**

- `id`, `email`, `password_hash`, `timezone`, `theme_preference`, `created_at`

**Mission:**

- `id`, `user_id`, `title`, `description`, `duration_minutes`, `essence_reward`, `attribute_type` (Growth/Health/Craft/Connection), `status` (pending/active/completed), `created_at`, `completed_at`

**Character:**

- `id`, `name` (Eliza, Lyra, Thorne, Elara), `personality_prompt`, `attribute_focus`, `scenario` (medieval, sci-fi, etc.)

**Character Relationship:**

- `id`, `user_id`, `character_id`, `relationship_level` (0-10), `last_interaction_at`

**Narrative State:**

- `id`, `user_id`, `scenario`, `current_chapter`, `hidden_quests` (JSON), `story_progress` (JSON)

**Progress:**

- `id`, `user_id`, `date`, `dci_score`, `missions_completed`, `streak_days`, `essence_earned`

### Relationships

- User → Missions (1:N)
- User → Character Relationships (1:N)
- User → Narrative State (1:1)
- User → Progress (1:N, daily records)
- Mission → Evidence (1:N, optional photos/notes)

### Vector Storage (PostgreSQL pgvector)

**Tables with Vector Columns:**

- `personal_memories` - Personal context, emotional state (user_id, content, embedding vector(1536))
- `project_memories` - Goal-related memories (user_id, content, embedding vector(1536))
- `task_memories` - Mission-specific context (user_id, mission_id, content, embedding vector(1536))
- `character_conversations` - Per-character chat history (user_id, character_id, message, embedding vector(1536))

---

## API Contracts

### Companion Chat

**POST** `/api/v1/companion/chat`

```json
{
  "message": "How are you today?",
  "context": {
    "current_mission_id": 123,
    "emotional_state": "stressed"
  }
}
```

**Response (SSE Stream):**

```
data: {"type": "token", "content": "I"}
data: {"type": "token", "content": " 'm"}
data: {"type": "token", "content": " here"}
data: {"type": "complete", "message_id": "abc123"}
```

### Missions

**GET** `/api/v1/missions?status=active`

```json
{
  "missions": [
    {
      "id": 123,
      "title": "Morning Arena Session",
      "duration_minutes": 20,
      "essence_reward": 15,
      "attribute_type": "Health",
      "status": "active"
    }
  ]
}
```

**POST** `/api/v1/missions/start`

```json
{
  "mission_id": 123
}
```

### World State

**GET** `/api/v1/world/state`

```json
{
  "current_time": "2025-11-09T14:30:00Z",
  "zones": {
    "arena": { "available": true, "closes_at": "21:00" },
    "observatory": { "available": true },
    "commons": { "available": false, "opens_at": "12:00" }
  },
  "characters_present": ["Eliza", "Lyra"]
}
```

---

## Security Architecture

**Authentication:**

- JWT tokens (access + refresh)
- Password hashing: bcrypt
- Session management: Redis

**Authorization:**

- User-scoped data access (users can only access their own missions, progress)
- Role-based: User, Admin (future)

**Data Protection:**

- Encryption at rest: Database encryption (PostgreSQL)
- Encryption in transit: HTTPS/TLS
- Evidence uploads: S3 with signed URLs, user-only access

**Privacy:**

- Opt-in for any tracking (tab monitoring, etc.)
- User data export/deletion: GDPR-compliant endpoints

---

## Performance Considerations

**Frontend:**

- Code splitting: Next.js automatic
- Image optimization: `next/image` with AVIF
- Caching: Static pages cached, dynamic with revalidation
- Bundle size: Target < 200KB initial JS

**Backend:**

- Database: Connection pooling (SQLAlchemy), indexes on foreign keys
- Caching: Redis for world state, user sessions (15min TTL)
- AI calls: Rate limiting, token caching where possible
- Background jobs: ARQ workers scale horizontally

**Cost Management (Target: $0.50/user/day):**

- LLM calls: Premium models for primary interactions, monitor token usage per user
- Vector storage: PostgreSQL pgvector (unified database, no separate service)
- Database: Connection pooling, efficient indexing on vector columns
- Caching: Redis for narrative templates, character prompts, world state
- Monitoring: Track LLM costs per user in real-time, implement soft limits

---

## Deployment Architecture

**Experimental Version:**

- **Frontend:** Vercel (Next.js optimized)
- **Backend:** Railway or Fly.io (Docker containers)
- **Database:** Railway PostgreSQL with pgvector or Supabase (has pgvector support)
- **Redis:** Upstash (serverless Redis)
- **File Storage:** S3-compatible (AWS S3 or MinIO)

**Production Version:**

- **Frontend:** Vercel (edge network)
- **Backend:** AWS ECS/Fargate or Fly.io (auto-scaling)
- **Database:** AWS RDS PostgreSQL with pgvector extension (managed)
- **Redis:** AWS ElastiCache or Upstash
- **File Storage:** AWS S3
- **Monitoring:** Sentry (errors, performance, session replay), CloudWatch for infrastructure

---

## Documentation

### Mintlify Documentation Platform

Delight uses **Mintlify** for developer and user documentation:

**Structure:**

```
docs/
├── mint.json              # Mintlify configuration
├── introduction.md        # Getting started
├── quickstart.md          # Quick setup guide
├── api-reference/         # API documentation
├── architecture/          # System design docs
└── guides/                # Feature guides
```

**Setup:**

```bash
npm install -g mintlify
mintlify dev  # Run docs locally at localhost:3000
```

**Benefits:**

- Interactive API documentation
- Beautiful, searchable interface
- Versioned documentation
- Code examples with syntax highlighting
- OpenAPI spec integration

---

## Development Environment

### Prerequisites

- **Node.js:** 20.x+
- **Python:** 3.11+
- **Poetry:** Latest
- **PostgreSQL:** 15+ (or Docker)
- **Redis:** 7+ (or Docker)
- **Docker:** (optional, for local services)
- **Mintlify CLI:** For documentation development

### Setup Commands

```bash
# Clone repository
git clone <repo-url>
cd delight

# Frontend setup
cd packages/frontend
npm install
npm run dev  # http://localhost:3000

# Backend setup
cd packages/backend
poetry install
poetry run uvicorn app.main:app --reload  # http://localhost:8000

# Database setup
poetry run alembic upgrade head

# Redis (Docker)
docker run -d -p 6379:6379 redis:7

# Environment variables
cp packages/backend/.env.example packages/backend/.env
# Edit .env with your keys
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Next.js 15 + React 19 for Frontend

**Decision:** Use Next.js 15 with React 19 for the frontend framework.

**Rationale:**

- React ecosystem provides extensive component libraries and community support
- Next.js 15 offers streaming support for AI responses (SSE)
- Server Components reduce client bundle size
- App Router provides excellent routing for zone-based navigation

**Alternatives Considered:**

- SvelteKit (better animation performance, smaller ecosystem)
- SolidJS (best performance, smallest ecosystem)

**Consequences:**

- Larger initial bundle than Svelte/Solid
- Need to optimize animations with Framer Motion
- Benefit from massive React ecosystem

---

### ADR-002: FastAPI for Backend

**Decision:** Use FastAPI as the backend framework.

**Rationale:**

- Async-first architecture perfect for AI streaming
- Excellent LangChain/LangGraph integration
- Automatic OpenAPI documentation
- Python ecosystem for AI/ML libraries

**Alternatives Considered:**

- Django Ninja (more structure, less async flexibility)
- Litestar (faster, smaller ecosystem)

**Consequences:**

- Need to add background jobs separately (ARQ)
- More manual setup than Django, but more flexibility

---

### ADR-003: LangGraph + LangChain for AI Orchestration

**Decision:** Use LangGraph for stateful agent orchestration, LangChain for LLM integration.

**Rationale:**

- LangGraph's state machine model perfect for character personalities and narrative flows
- Multi-agent support for Eliza + character system
- Built-in memory abstractions
- Streaming support for token-by-token responses

**Alternatives Considered:**

- Vanilla LangChain (simpler, less structured for stateful agents)
- Custom orchestration (full control, more work)

**Consequences:**

- Learning curve for graph paradigm
- Framework dependency, but provides structure for complex AI workflows

---

### ADR-004: PostgreSQL pgvector for Vector Storage

**Decision:** Use PostgreSQL with pgvector extension for vector storage.

**Rationale:**

- Unified storage: vectors + structured data in single database
- Production-ready from day one, no migration needed
- Excellent LangChain integration (langchain-postgres)
- Reduces operational complexity (one database instead of two)
- ACID guarantees for vector operations

**Alternatives Considered:**

- Chroma (simpler initially, but requires separate service or embedded mode)
- Qdrant (best vector performance, adds operational overhead)

**Consequences:**

- Need PostgreSQL 15+ with pgvector extension installed
- Slightly more complex initial setup than embedded Chroma
- Better scalability and production-readiness long-term

---

### ADR-005: Hybrid SSE + WebSocket + HTTP for Real-Time

**Decision:** Use Server-Sent Events (SSE) for AI streaming, WebSocket for world state updates, HTTP for user actions.

**Rationale:**

- SSE perfect for one-way token streaming from AI
- WebSocket for bidirectional world state (zone availability, character presence)
- Eliminates polling delay (previously 15min), provides instant updates
- HTTP for user actions is standard and simple
- Graceful degradation: WebSocket failures fall back to polling

**Alternatives Considered:**

- Pure WebSocket (full-duplex everywhere, more complex state management)
- Pure polling (simpler, 15min latency for world changes)
- SSE only (no bidirectional communication)

**Consequences:**

- Need to manage WebSocket connections and reconnection logic
- Better UX with real-time world state changes
- Fallback to polling ensures reliability

---

### ADR-006: JSON vs JSONB for Flexible Schemas

**Decision:** Use `JSON` type (not `JSONB`) for flexible data structures in PostgreSQL.

**Rationale:**

- Simpler storage model for complex nested structures
- Preserves exact JSON formatting and key order
- Adequate performance for our use case (personality configs, quest data)

**Alternatives Considered:**

- JSONB (better performance, indexable, but binary format)
- Fully normalized tables (rigid, hard to evolve for AI-generated content)

**Consequences:**

- Slightly slower queries on JSON fields (acceptable trade-off)
- Cannot create GIN indexes on JSON columns (only JSONB supports this)
- Simpler mental model for developers
- Note: Can migrate to JSONB later if performance becomes an issue

---

## Revision History

### 2025-11-10: Architecture Validation Updates

**Changes made based on validation feedback:**

1. **Cost Model Updated:** Changed from $0.10/user/day to $0.50/user/day operational target, with $1/day subscription pricing + pay-as-you-go model
2. **Vector Storage Migration:** Switched from Chroma (embedded) to PostgreSQL pgvector for unified storage and production-readiness
3. **Observability Solidified:** Confirmed Sentry for error tracking, performance monitoring, and session replay
4. **Background Job Reliability:** Added retry strategies, dead letter queue, and monitoring dashboard specifications
5. **Real-Time Architecture Enhanced:** Added WebSocket for world state updates (alongside SSE for AI streaming) to eliminate polling delays
6. **Data Type Standardization:** Standardized on JSON type (not JSONB) for flexible schema columns with documented trade-offs

**Impact:**

- Eliminates future migration from Chroma → production vector DB
- Clearer cost expectations and monitoring requirements
- Better real-time user experience for world state changes
- Production-ready from day one

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_  
_Date: 2025-11-09_  
_Updated: 2025-11-10_  
_For: Jack_
