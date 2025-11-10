# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Delight** is an emotionally intelligent AI companion platform that transforms overwhelming goals into achievable daily missions. The system combines AI coaching, narrative world-building, and structured progress tracking to help users maintain momentum on difficult ambitions.

**Tech Stack:**
- **Frontend:** Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **Backend:** Python 3.11+ + FastAPI + SQLAlchemy 2.0 (async) + Alembic
- **Database:** Supabase (managed PostgreSQL 16+ with pgvector extension)
- **Authentication:** Clerk (managed auth service)
- **AI/LLM:** OpenAI GPT-4o-mini (chat/personas), GPT-4o (narrative), text-embedding-3-small
- **Background Jobs:** ARQ (async Redis queue)
- **Real-time:** Server-Sent Events (AI streaming), WebSocket (world state)

---

## Repository Structure

```
delight/
├── packages/
│   ├── frontend/           # Next.js 15 App Router application
│   │   ├── src/
│   │   │   ├── app/         # Pages and routes
│   │   │   ├── components/  # React components (ui/, companion/, missions/)
│   │   │   └── lib/         # API client, hooks, utilities
│   │   └── package.json     # Frontend dependencies
│   │
│   ├── backend/            # FastAPI application
│   │   ├── app/
│   │   │   ├── api/v1/      # REST endpoints
│   │   │   ├── models/      # SQLAlchemy models
│   │   │   ├── schemas/     # Pydantic schemas
│   │   │   ├── services/    # Business logic
│   │   │   ├── agents/      # LangGraph AI agents
│   │   │   ├── workers/     # ARQ background jobs
│   │   │   ├── db/          # Database session, migrations
│   │   │   └── core/        # Config, dependencies, security
│   │   ├── pyproject.toml   # Poetry dependencies
│   │   ├── alembic.ini      # Alembic configuration
│   │   └── main.py          # FastAPI app entry
│   │
│   └── shared/             # Shared TypeScript types
│       └── types/
│
├── docs/                   # Project documentation
│   ├── ARCHITECTURE.md      # Technical architecture and ADRs
│   ├── SETUP.md             # Detailed setup instructions
│   ├── epics.md             # Epic and story breakdown
│   ├── sprint-status.yaml   # Current sprint status
│   ├── tech-spec-epic-1.md  # Technical specifications
│   └── stories/             # Story documentation
│
├── docker-compose.yml      # Local PostgreSQL + Redis (optional)
├── Makefile                # Development commands
└── pnpm-workspace.yaml     # Monorepo configuration
```

---

## Common Development Commands

### Setup

```bash
# Install all dependencies (run from root)
make install

# Or manually:
pnpm install                        # Root + frontend
cd packages/backend && poetry install  # Backend
```

### Development Servers

```bash
# Start both frontend + backend (from root)
make dev

# Or start separately:
make dev:frontend  # Next.js on http://localhost:3000
make dev:backend   # FastAPI on http://localhost:8000

# Backend in specific terminal
cd packages/backend
poetry run uvicorn main:app --reload
```

### Database Management

```bash
cd packages/backend

# Apply migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision -m "description" --autogenerate

# Rollback last migration
poetry run alembic downgrade -1

# Test database connection
poetry run python scripts/test_db_connection.py
```

### Testing

```bash
# Backend tests
cd packages/backend
poetry run pytest                    # Run all tests
poetry run pytest -v --cov=app       # With coverage
poetry run pytest tests/test_auth.py # Specific file

# Frontend E2E tests
cd packages/frontend
npm run test:e2e        # Headless mode
npm run test:e2e:ui     # With Playwright UI
```

### Code Quality

```bash
# Backend linting and formatting
cd packages/backend
poetry run ruff check .     # Lint
poetry run black .          # Format
poetry run mypy app         # Type check

# Frontend linting
cd packages/frontend
npm run lint                # ESLint
```

### Infrastructure Modes

```bash
# Use cloud-managed services (Supabase + Upstash) - Recommended
make cloud-dev

# Use local Docker services (PostgreSQL + Redis)
make local
make stop  # Stop local services
```

---

## Architecture Highlights

### Database Strategy

- **Provider:** Supabase (managed PostgreSQL with pgvector pre-installed)
- **ORM:** SQLAlchemy 2.0 with async support (asyncpg driver)
- **Migrations:** Alembic for version-controlled schema changes
- **Key Design:**
  - UUID primary keys (PostgreSQL `gen_random_uuid()`)
  - Clerk `clerk_user_id` as authoritative user identifier
  - JSONB columns for flexible data (custom_hours, communication_preferences)
  - Timestamps with timezone (`TIMESTAMP WITH TIME ZONE`)
  - pgvector extension for semantic memory (Epic 2)

### Authentication

- **Clerk** manages all authentication (OAuth, email/password, magic links, 2FA)
- Frontend: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (client-side)
- Frontend middleware: `CLERK_SECRET_KEY` (server-side Next.js middleware)
- Backend: `CLERK_SECRET_KEY` for session verification
- User sync: Clerk webhooks → backend creates/updates user records

### AI/LLM Strategy

- **GPT-4o-mini** for chat, personas, quest generation (~$0.03/user/day)
- **GPT-4o** for premium narrative generation (less frequent, higher quality)
- **text-embedding-3-small** for semantic memory (1536 dimensions)
- **cardiffnlp/roberta** open source model for emotion detection (self-hosted)
- **Future:** LangGraph agents orchestrate multi-character AI system

### Naming Conventions

**Backend (Python):**
- Modules/functions: `snake_case` (e.g., `companion_service.py`, `calculate_dci()`)
- Classes: `PascalCase` (e.g., `CompanionService`, `User`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_MISSION_DURATION`)

**Frontend (TypeScript):**
- Components/files: `PascalCase` (e.g., `MissionCard.tsx`)
- Functions/variables: `camelCase` (e.g., `useMission`, `calculateStreak`)
- Hooks: `camelCase` with `use` prefix (e.g., `useMission`)

**API Endpoints:**
- REST: `/api/v1/{resource}/{id?}` (e.g., `/api/v1/missions/123`)
- SSE: `/api/v1/sse/{stream_type}` (e.g., `/api/v1/sse/companion/stream`)

**Database:**
- Tables: `snake_case`, plural (e.g., `users`, `user_preferences`)
- Columns: `snake_case` (e.g., `clerk_user_id`, `created_at`)
- Foreign keys: `{table}_id` (e.g., `user_id`)

---

## Development Workflow (BMAD)

This project follows the **BMAD (Business-Managed Agile Development)** methodology:

### Story Development Process

1. **Select Story:** Check `docs/sprint-status.yaml` for next story with status `ready-for-dev`
2. **Read Story:** Review complete requirements in `docs/stories/{story-id}.md`
3. **Create Branch:** `git checkout -b story/{story-id}-short-description`
4. **Implement:** Follow acceptance criteria and tasks in story file
5. **Test:** Manual testing + automated tests (unit, integration, E2E as needed)
6. **Review:** Self-review checklist in story file
7. **Document:** Update README, API docs, create story summary
8. **Commit:** Detailed commit message with story ID, changes, test results
9. **Merge:** Merge to `main` after all acceptance criteria met
10. **Update Status:** Change story status to `done` in `docs/sprint-status.yaml`

### Key Resources

- **Developer Guide:** `docs/dev/BMAD-DEVELOPER-GUIDE.md` (comprehensive workflow guide)
- **Quick Reference:** `docs/dev/QUICK-REFERENCE.md` (command cheat sheet)
- **Architecture:** `docs/ARCHITECTURE.md` (technical decisions, ADRs)
- **Setup Guide:** `docs/SETUP.md` (environment setup, ~15 minutes)

### Current Sprint Status

Check `docs/sprint-status.yaml` for latest story statuses:
- **Epic 1:** User Onboarding & Foundation (in progress)
  - Story 1.1: ✅ Done (monorepo initialization)
  - Story 1.2: 🔄 In Progress (database schema and migrations)
  - Story 1.3: Backlog (Clerk authentication)
  - Story 1.4: Deferred (onboarding flow - after Epic 2)
  - Story 1.5: Backlog (deployment pipeline)

---

## Critical Implementation Patterns

### Async SQLAlchemy 2.0

All database operations must use async patterns:

```python
from sqlalchemy import select
from app.db.session import get_db

# FastAPI route
@router.get("/missions")
async def get_missions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Mission).where(Mission.user_id == user_id))
    missions = result.scalars().all()
    return missions
```

### Alembic Migrations with Async

Alembic `env.py` is configured for async SQLAlchemy. Key requirements:
- Import all models in `app/models/__init__.py`
- `target_metadata = Base.metadata` in `env.py`
- `run_migrations_online()` uses async engine with `asyncio.run()`

### Next.js App Router with Clerk

```typescript
// middleware.ts - Server-side auth protection
import { clerkMiddleware } from "@clerk/nextjs/server";
export default clerkMiddleware();

// Use CLERK_SECRET_KEY (without NEXT_PUBLIC_ prefix)
// This runs server-side only, never reaches browser
```

### Error Handling

**Backend:**
```python
from fastapi import HTTPException

# Always use HTTPException for API errors
raise HTTPException(status_code=404, detail="Mission not found")
```

**Frontend:**
```typescript
// Use try-catch with user-friendly error messages
try {
  const data = await api.getMissions();
} catch (error) {
  toast.error("Failed to load missions. Please try again.");
}
```

---

## Environment Variables

### Backend (`packages/backend/.env`)

```bash
# Database (Supabase connection string)
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.xxx.supabase.co:5432/postgres

# Authentication
CLERK_SECRET_KEY=sk_test_...

# AI/LLM
OPENAI_API_KEY=sk-proj-...

# Optional: Redis (for background jobs)
REDIS_URL=redis://localhost:6379  # or Upstash URL

# Environment
ENVIRONMENT=development
```

### Frontend (`packages/frontend/.env.local`)

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...  # Public (client-side)
CLERK_SECRET_KEY=sk_test_...                   # Secret (server-side middleware)

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Security Note:**
- `NEXT_PUBLIC_*` variables are exposed to browser (client-side)
- Variables without `NEXT_PUBLIC_` are server-side only (middleware, server components)
- Never commit `.env` files (already in `.gitignore`)

---

## Testing Strategy

### Backend Testing

```bash
# Run all tests with coverage
cd packages/backend
poetry run pytest -v --cov=app --cov-report=html

# Test structure
tests/
├── unit/           # Individual function tests
├── integration/    # API + DB + service tests
└── conftest.py     # Fixtures and test configuration
```

### Frontend Testing

```bash
# E2E tests with Playwright
cd packages/frontend
npm run test:e2e        # Headless
npm run test:e2e:ui     # Interactive UI

# Test structure
tests/
├── e2e/                    # End-to-end flows
├── support/fixtures/       # Test data factories
└── support/helpers/        # Testing utilities
```

### Testing Checklist

- ✅ All acceptance criteria tested manually
- ✅ Unit tests for critical functions (≥70% backend coverage)
- ✅ Integration tests for API endpoints + DB
- ✅ E2E tests for complete user flows
- ✅ Error handling and edge cases covered

---

## Common Issues & Solutions

### Database Connection Errors

```bash
# Verify Supabase connection string
echo $DATABASE_URL  # Should start with postgresql+asyncpg://

# Test connection manually
cd packages/backend
poetry run python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())"

# Re-run migrations
poetry run alembic upgrade head
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
poetry run uvicorn main:app --reload --port 8001
```

### Migration Not Detecting Models

```bash
# Ensure all models imported in app/models/__init__.py
# Alembic's autogenerate only detects models registered with Base.metadata

# Force regenerate migration
poetry run alembic revision -m "description" --autogenerate
```

---

## Important Links

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Supabase Dashboard:**
- Database: Table Editor, SQL Editor, Query Performance
- Connection string: Project Settings → Database

**Clerk Dashboard:**
- Users, OAuth providers, webhooks
- API keys: Developers → API Keys

**External Docs:**
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs
- Supabase: https://supabase.com/docs
- Clerk: https://clerk.com/docs
- SQLAlchemy: https://docs.sqlalchemy.org/en/20/
- Alembic: https://alembic.sqlalchemy.org

---

## Key Design Decisions (ADRs)

### ADR-007: Clerk for Authentication
**Rationale:** Reduces 2-3 stories of development, provides OAuth/2FA/magic links out-of-the-box, SOC 2 compliant, free tier sufficient for MVP.

### ADR-009: GPT-4o-mini as Primary LLM
**Rationale:** 80% cheaper than GPT-4o ($0.15/$0.60 vs $2.50/$10 per 1M tokens), fast responses, meets $0.50/user/day cost target (~$0.03 actual).

### ADR-010: Supabase for Managed PostgreSQL
**Rationale:** pgvector pre-installed, zero local setup, free tier sufficient for MVP (500MB DB), automatic backups, production-ready scalability.

### ADR-004: PostgreSQL pgvector for Vector Storage
**Rationale:** Unified storage (vectors + structured data), production-ready, no separate service needed, ACID guarantees, excellent LangChain integration.

---

## Notes for Claude Code Instances

1. **Always check `docs/sprint-status.yaml`** before starting work to understand current story status
2. **Read the complete story file** in `docs/stories/` before implementation
3. **Follow BMAD workflow** documented in `docs/dev/BMAD-DEVELOPER-GUIDE.md`
4. **Use async patterns** for all database operations (SQLAlchemy 2.0)
5. **Test acceptance criteria** manually and write automated tests
6. **Update documentation** when adding new features or env vars
7. **Never commit secrets** - use environment variables
8. **Follow naming conventions** - snake_case (Python), camelCase (TypeScript)
9. **Clerk handles auth** - don't implement custom JWT/password logic
10. **Supabase is primary DB** - pgvector comes pre-installed, just verify it's enabled

---

**Last Updated:** 2025-11-10
**Version:** 1.0.0
**Maintained By:** Jack & Delight Team
