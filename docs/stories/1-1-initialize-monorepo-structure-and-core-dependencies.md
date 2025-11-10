# Story 1.1: Initialize Monorepo Structure and Core Dependencies

Status: ready-for-dev

## Story

As a **developer**,
I want **a properly structured monorepo with backend, frontend, and shared packages with all core dependencies installed**,
so that **the team can work efficiently with proper tooling, dependency management, and can start both development servers successfully**.

## Acceptance Criteria

### AC1: Monorepo Structure Created

**Given** I am setting up a new development environment
**When** I run the initialization commands
**Then** the monorepo structure is created with:

- `packages/frontend/` with Next.js 15 + TypeScript + Tailwind
- `packages/backend/` with FastAPI + Poetry + async SQLAlchemy
- `packages/shared/` for TypeScript types
- Docker Compose for local PostgreSQL + Redis (or Upstash configuration)
- Root package.json with pnpm workspace configuration

[Source: docs/epics/epic-1-user-onboarding-foundation.md#Story-1.1, docs/tech-spec-epic-1.md#AC1]

### AC2: Core Dependencies Installed

**Given** the monorepo structure exists
**When** all dependencies are installed
**Then** all core dependencies are present:

**Frontend dependencies:**

- Next.js 15, React 19, TypeScript, Tailwind CSS
- shadcn/ui components, @radix-ui components
- @clerk/nextjs for authentication
- framer-motion for animations
- class-variance-authority, clsx, tailwind-merge for styling utilities

**Backend dependencies:**

- FastAPI, Uvicorn (with standard extras)
- SQLAlchemy 2.0 (with asyncio extras), asyncpg (PostgreSQL driver)
- Pydantic 2.5+, pydantic-settings
- Alembic (for migrations)
- clerk-backend-sdk (authentication)
- redis, arq (job queue)
- sentry-sdk (with FastAPI extras)

**AI/ML dependencies (Backend):**

- LangChain, LangGraph
- langchain-postgres, pgvector
- transformers, torch (for emotion detection with cardiffnlp/roberta)

[Source: docs/tech-spec-epic-1.md#AC2, docs/tech-spec-epic-1.md#Dependencies]

### AC3: Development Servers Start Successfully

**Given** all dependencies are installed
**When** I start the development servers
**Then**:

- Frontend starts successfully: `pnpm dev` (http://localhost:3000)
- Backend starts successfully: `poetry run uvicorn main:app --reload` (http://localhost:8000)
- PostgreSQL is accessible (Supabase managed or Docker local)
- Redis is accessible (Upstash or Docker local)
- Health check endpoint responds: `GET http://localhost:8000/api/v1/health`

[Source: docs/tech-spec-epic-1.md#AC1, docs/tech-spec-epic-1.md#AC6]

### AC4: Environment Configuration Complete

**Given** the monorepo is initialized
**When** I review the environment setup
**Then**:

- `.env.example` files exist for both frontend and backend
- Required environment variables documented:
  - DATABASE_URL (Supabase connection string)
  - REDIS_URL (Upstash or local Redis)
  - CLERK_PUBLISHABLE_KEY (frontend)
  - CLERK_SECRET_KEY (backend)
  - OPENAI_API_KEY (for future AI features)
  - SENTRY_DSN (optional, for error tracking)
- `.env` files are in `.gitignore`
- README.md contains setup instructions

[Source: docs/tech-spec-epic-1.md#AC6, docs/architecture/project-structure.md]

## Tasks / Subtasks

### Task 1: Initialize Monorepo Root (AC: #1)

- [ ] Create root `package.json` with pnpm workspace configuration
  ```json
  {
    "name": "delight",
    "private": true,
    "workspaces": ["packages/*"]
  }
  ```
- [ ] Create `.gitignore` with standard Node/Python exclusions
- [ ] Create `README.md` with project overview and setup instructions
- [ ] Create `packages/` directory structure

### Task 2: Initialize Frontend Package (AC: #1, #2)

- [ ] Run `npx create-next-app@latest packages/frontend` with options:
  - TypeScript: Yes
  - ESLint: Yes
  - Tailwind CSS: Yes
  - App Router: Yes
  - Turbopack: No (stable build)
  - Import alias: `@/*`
- [ ] Install shadcn/ui: `npx shadcn-ui@latest init`
- [ ] Install Clerk: `pnpm add @clerk/nextjs`
- [ ] Install additional dependencies:
  ```bash
  pnpm add framer-motion class-variance-authority clsx tailwind-merge
  ```
- [ ] Create basic directory structure in `src/app/`:
  - `(auth)/` (auth routes)
  - `(world)/` (world zones)
  - `companion/` (chat interface)
  - `missions/` (mission views)
  - `progress/` (analytics dashboard)
- [ ] Create `.env.example` with `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- [ ] Test: `pnpm dev` starts successfully on port 3000

### Task 3: Initialize Backend Package (AC: #1, #2)

- [ ] Create `packages/backend/` directory
- [ ] Initialize Poetry: `cd packages/backend && poetry init`
  - Python version: ^3.11
  - Name: delight-backend
- [ ] Install FastAPI stack:
  ```bash
  poetry add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings
  ```
- [ ] Install authentication:
  ```bash
  poetry add clerk-backend-sdk
  ```
- [ ] Install infrastructure:
  ```bash
  poetry add redis arq sentry-sdk[fastapi]
  ```
- [ ] Install AI/ML dependencies:
  ```bash
  poetry add langchain langgraph langchain-postgres pgvector transformers torch
  ```
- [ ] Install dev dependencies:
  ```bash
  poetry add --group dev pytest pytest-asyncio httpx ruff black mypy
  ```
- [ ] Create basic directory structure in `app/`:
  - `api/v1/` (API routes)
  - `core/` (config, security, dependencies)
  - `models/` (SQLAlchemy models)
  - `schemas/` (Pydantic schemas)
  - `services/` (business logic)
  - `agents/` (LangGraph agents)
  - `workers/` (ARQ background jobs)
  - `db/` (database setup, migrations)
- [ ] Create `main.py` with basic FastAPI app and health check endpoint
- [ ] Create `.env.example` with required variables
- [ ] Test: `poetry run uvicorn main:app --reload` starts on port 8000

### Task 4: Initialize Shared Package (AC: #1)

- [ ] Create `packages/shared/` directory
- [ ] Create `package.json`:
  ```json
  {
    "name": "@delight/shared",
    "version": "0.1.0",
    "main": "index.ts",
    "types": "index.ts"
  }
  ```
- [ ] Create `types/` directory for shared TypeScript types
- [ ] Create `index.ts` barrel export file
- [ ] Create placeholder type files:
  - `user.ts`
  - `mission.ts`
  - `character.ts`
  - `narrative.ts`
  - `progress.ts`

### Task 5: Set Up Infrastructure (AC: #1, #3)

- [ ] Create `docker-compose.yml` with services:
  - Redis (redis:7-alpine) on port 6379 (OPTIONAL - only if not using Upstash)
  - Note: PostgreSQL via Supabase (no Docker container needed)
- [ ] Document Supabase setup in README:
  - Create project at supabase.com
  - Get DATABASE_URL from project settings
  - Enable pgvector extension (pre-installed in Supabase)
- [ ] Document Upstash Redis setup in README (optional alternative to Docker):
  - Create project at upstash.com
  - Get REDIS_URL from project settings
- [ ] Create health check utility to verify connections
- [ ] Test: Infrastructure services are accessible

### Task 6: Configure Development Environment (AC: #4)

- [ ] Create `packages/frontend/.env.example`:
  ```
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```
- [ ] Create `packages/backend/.env.example`:
  ```
  DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
  REDIS_URL=redis://localhost:6379
  CLERK_SECRET_KEY=sk_test_...
  OPENAI_API_KEY=sk-...
  SENTRY_DSN=https://...
  ENVIRONMENT=development
  ```
- [ ] Update root `.gitignore` to exclude `.env` files
- [ ] Document setup steps in README.md:
  1. Prerequisites (Node.js 20+, Python 3.11+, pnpm, Poetry)
  2. Clone repository
  3. Install dependencies
  4. Configure environment variables (Supabase, Clerk, etc.)
  5. Start development servers
- [ ] Create `Makefile` or scripts for common commands:
  - `dev-frontend`: Start frontend dev server
  - `dev-backend`: Start backend dev server
  - `install`: Install all dependencies
  - `lint`: Run linters

### Task 7: Implement Health Check Endpoint (AC: #3)

- [ ] Create `packages/backend/app/api/v1/health.py`:

  ```python
  from fastapi import APIRouter, status
  from sqlalchemy import text
  from app.core.dependencies import get_db

  router = APIRouter()

  @router.get("/health")
  async def health_check():
      # Check database connection
      # Check Redis connection
      # Return status
      return {
          "status": "healthy",
          "database": "connected",
          "redis": "connected",
          "timestamp": datetime.utcnow().isoformat()
      }
  ```

- [ ] Register health check route in `main.py`
- [ ] Test: `curl http://localhost:8000/api/v1/health` returns 200 OK

### Task 8: Testing (All ACs)

- [ ] Verify root workspace: `pnpm --version` shows pnpm is installed
- [ ] Verify frontend build: `cd packages/frontend && pnpm build` succeeds
- [ ] Verify backend tests run: `cd packages/backend && poetry run pytest` (even if no tests yet)
- [ ] Verify linting: Frontend `pnpm lint`, Backend `poetry run ruff check .`
- [ ] Verify both servers start simultaneously without port conflicts
- [ ] Verify health check endpoint returns healthy status
- [ ] Verify shared types can be imported in frontend
- [ ] Document test results in story completion notes

## Dev Notes

### Architecture Patterns and Constraints

**Technology Stack:**

- **Frontend:** Next.js 15 with App Router, React Server Components, TypeScript, Tailwind CSS
- **Backend:** FastAPI with async SQLAlchemy 2.0, providing REST APIs and SSE streaming
- **Database:** Supabase (managed PostgreSQL 16+ with pgvector extension pre-installed)
- **Authentication:** Clerk (managed auth service) - handles passwords, sessions, OAuth, magic links
- **Job Queue:** ARQ + Redis for background workers
- **Monorepo:** pnpm workspaces for frontend/shared, Poetry for backend Python dependencies

[Source: docs/tech-spec-epic-1.md#Technology-Stack-Decisions]

**Infrastructure Constraints:**

- Cost target: <$0.50 per active user per day
- Development environment: Supabase (managed PostgreSQL), Upstash or Docker Redis
- Deployment: Containerized services (Docker) with environment-based configuration
- Observability: Sentry for error tracking, health check endpoints for uptime monitoring

[Source: docs/tech-spec-epic-1.md#Infrastructure-Constraints]

**Key Initialization Commands:**

Frontend:

```bash
npx create-next-app@latest packages/frontend --typescript --tailwind --app --eslint
cd packages/frontend
npx shadcn-ui@latest init
pnpm add @clerk/nextjs framer-motion class-variance-authority clsx tailwind-merge
```

Backend:

```bash
cd packages/backend
poetry init
poetry add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings clerk-backend-sdk redis arq sentry-sdk[fastapi] langchain langgraph langchain-postgres pgvector transformers torch
poetry add --group dev pytest pytest-asyncio httpx ruff black mypy
```

[Source: docs/tech-spec-epic-1.md#Technical-Notes (Story 1.1)]

### Project Structure Notes

Follow the canonical project structure defined in `docs/architecture/project-structure.md`:

**Frontend structure:**

- App Router pages in `src/app/` with route groups: `(auth)/`, `(world)/`, `companion/`, `missions/`, `progress/`
- Components in `src/components/` organized by feature: `ui/`, `companion/`, `missions/`, `world/`, `narrative/`
- Utilities in `src/lib/`: `api/`, `hooks/`, `utils/`, `themes/`

**Backend structure:**

- API routes in `app/api/v1/`: `companion.py`, `missions.py`, `narrative.py`, `progress.py`, `world.py`
- Core configuration in `app/core/`: `config.py`, `security.py`, `dependencies.py`
- SQLAlchemy models in `app/models/`
- Pydantic schemas in `app/schemas/`
- Business logic in `app/services/`
- LangGraph agents in `app/agents/`
- ARQ workers in `app/workers/`
- Database setup in `app/db/`: `base.py`, `migrations/`

**Shared types:**

- All TypeScript interfaces in `packages/shared/types/`
- Re-exported through `packages/shared/index.ts` for clean imports

[Source: docs/architecture/project-structure.md]

### Database Setup: Supabase Instead of Docker

**Important:** This project uses **Supabase** (managed PostgreSQL) instead of local Docker PostgreSQL.

**Rationale:**

- Supabase provides PostgreSQL 16+ with pgvector extension pre-installed
- No local Docker PostgreSQL setup needed
- Free tier: 500MB database (sufficient for MVP)
- Built-in connection pooling, backups, and observability
- Production-ready from day one (no migration from dev to prod database)

**Setup Steps:**

1. Create Supabase project at https://supabase.com
2. Get `DATABASE_URL` from Project Settings → Database → Connection String (URI mode)
3. Format: `postgresql+asyncpg://postgres:[password]@[host]:5432/postgres`
4. Add to `packages/backend/.env`
5. Verify pgvector extension: Already enabled by default in Supabase

**Redis Options:**

- **Option 1 (Recommended):** Upstash Redis (serverless, free tier)
  - Create project at https://upstash.com
  - Get `REDIS_URL` from project settings
  - No local Docker needed
- **Option 2:** Docker Redis (local development)
  - Use `docker-compose.yml` with redis:7-alpine
  - Suitable for fully offline development

[Source: docs/tech-spec-epic-1.md#Technology-Stack-Decisions, docs/tech-spec-epic-1.md#Infrastructure-Constraints]

### Authentication Setup (Clerk)

While full Clerk integration happens in Story 1.3, this story includes:

- Installing `@clerk/nextjs` (frontend) and `clerk-backend-sdk` (backend)
- Adding Clerk environment variables to `.env.example` files
- No actual authentication code yet - just dependencies

Story 1.3 will implement:

- Clerk webhook endpoint for user sync
- `get_current_user` FastAPI dependency
- Frontend `<ClerkProvider>` and middleware

[Source: docs/tech-spec-epic-1.md#Story-1.3, docs/epics/epic-1-user-onboarding-foundation.md#Story-1.3]

### AI/ML Dependencies Note

**Emotion Detection (Story 2.6):**

- Installing `transformers` and `torch` in this story
- Model: cardiffnlp/roberta (open source, self-hosted)
- Used for detecting user emotional state in companion chat
- Will be implemented in Epic 2, but dependencies installed now

**LLM Infrastructure (Epic 2+):**

- LangChain, LangGraph: Agent orchestration framework
- langchain-postgres: Memory store with pgvector
- OpenAI API (GPT-4o-mini for chat, GPT-4o for narrative)
- Local LLM support (Ollama, vLLM) planned post-MVP

[Source: docs/tech-spec-epic-1.md#AI/LLM-Infrastructure, docs/tech-spec-epic-1.md#Dependencies]

### Testing Strategy

**For this story (Story 1.1):**

- Focus on integration testing (services start successfully)
- Verify health check endpoint returns correct status
- Verify linters run without errors
- Verify builds complete successfully

**Future stories will add:**

- Unit tests: Jest (frontend), pytest (backend)
- Integration tests: Database operations, API endpoints
- E2E tests: Playwright (after UI components exist)

**CI/CD (Story 1.5):**

- Linting: ESLint (frontend), Ruff + Black (backend)
- Testing: Jest, pytest
- Coverage target: 70%+ for core logic

[Source: docs/tech-spec-epic-1.md#Test-Strategy-Summary]

### Performance Targets

While full performance optimization happens later, keep in mind:

- API Response Time (p95): < 500ms
- Page Load Time (First Contentful Paint): < 1.5s
- Server Cold Start: < 5s

These targets inform dependency choices (async SQLAlchemy, React Server Components, etc.)

[Source: docs/tech-spec-epic-1.md#Performance]

### Security Considerations

**Environment Variables:**

- NEVER commit `.env` files (enforced by `.gitignore`)
- Use `.env.example` as templates
- Production secrets in deployment platform secret manager

**Dependency Security:**

- Run `pnpm audit` and `poetry check` regularly
- Dependabot configured in Story 1.5 for automated updates
- Sentry for runtime error monitoring

[Source: docs/tech-spec-epic-1.md#Security]

### References

- [Epic 1 Story 1.1 Requirements](docs/epics/epic-1-user-onboarding-foundation.md#Story-1.1)
- [Epic 1 Technical Specification](docs/tech-spec-epic-1.md)
- [Acceptance Criteria AC1-AC6](docs/tech-spec-epic-1.md#Acceptance-Criteria-Authoritative)
- [Technology Stack Details](docs/tech-spec-epic-1.md#Technology-Stack-Decisions)
- [Project Structure](docs/architecture/project-structure.md)
- [Dependencies (Frontend/Backend/Shared)](docs/tech-spec-epic-1.md#Dependencies)
- [Infrastructure Constraints](docs/tech-spec-epic-1.md#Infrastructure-Constraints)
- [Test Strategy](docs/tech-spec-epic-1.md#Test-Strategy-Summary)
- [Security Architecture](docs/tech-spec-epic-1.md#Security)
- [Performance Requirements](docs/tech-spec-epic-1.md#Performance)

## Dev Agent Record

### Context Reference

- `docs/stories/1-1-initialize-monorepo-structure-and-core-dependencies.context.xml` - Technical context with documentation artifacts, dependencies, constraints, interfaces, and testing standards

### Agent Model Used

<!-- To be filled during development -->

### Debug Log References

<!-- To be added during development -->

### Completion Notes List

<!-- To be added during development -->

### File List

<!-- To be added during development -->
<!-- Format:
- NEW: path/to/file.ext - Description
- MODIFIED: path/to/file.ext - Description
- DELETED: path/to/file.ext - Description
-->

## Change Log

| Date       | Author | Change Description                     |
| ---------- | ------ | -------------------------------------- |
| 2025-11-10 | SM     | Story drafted with comprehensive specs |
