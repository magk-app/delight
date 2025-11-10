# Story 1.1: Initialize Monorepo Structure and Core Dependencies

Status: ready-for-dev

## Story

As a **developer**,
I want **a properly structured monorepo with backend, frontend, and shared packages**,
so that **the team can work efficiently with proper tooling and dependency management**.

## Acceptance Criteria

1. **Directory Structure Created**

   - **Given** I am setting up a new development environment
   - **When** I clone the repository and run setup commands
   - **Then** the following structure exists:
     - `packages/frontend/` - Next.js 15 application with App Router, TypeScript, Tailwind CSS
     - `packages/backend/` - FastAPI application with Poetry dependency management
     - `packages/shared/` - TypeScript shared types
     - `docker-compose.yml` - PostgreSQL and Redis service definitions at root
     - Root `package.json` with pnpm workspace configuration

2. **Frontend Dependencies Installed**

   - **Given** the frontend directory exists
   - **When** I run `pnpm install` in the project root
   - **Then** all frontend dependencies are installed:
     - Next.js 15.x
     - React 19.x
     - TypeScript 5.3+
     - Tailwind CSS 3.4+
     - @clerk/nextjs 5.0+
     - shadcn/ui base components (Radix UI primitives)
     - Framer Motion 11.0+

3. **Backend Dependencies Installed**

   - **Given** the backend directory exists
   - **When** I run `poetry install` in `packages/backend/`
   - **Then** all backend dependencies are installed:
     - FastAPI 0.109+
     - Uvicorn 0.27+ (with standard extras)
     - SQLAlchemy 2.0+ (with asyncio extras)
     - asyncpg 0.29+
     - Alembic 1.13+
     - Pydantic 2.5+
     - clerk-backend-sdk 0.3+
     - LangChain 0.1+
     - LangGraph 0.0.20+
     - langchain-postgres 0.0.3+
     - pgvector 0.2.4+
     - transformers 4.36+ (for emotion detection)
     - torch 2.1+
     - ARQ 0.26+
     - Redis 5.0+
     - sentry-sdk 1.40+ (with fastapi extras)

4. **Docker Compose Environment Works**

   - **Given** the docker-compose.yml file is configured
   - **When** I run `docker-compose up -d`
   - **Then**:
     - PostgreSQL 16+ container starts successfully on port 5432
     - Redis 7+ container starts successfully on port 6379
     - Both services are accessible from host machine
     - PostgreSQL includes pgvector extension capability

5. **Development Servers Start Successfully**

   - **Given** all dependencies are installed and Docker services are running
   - **When** I start the frontend with `pnpm dev` (from root or frontend directory)
   - **Then**:
     - Frontend server starts at `http://localhost:3000`
     - Next.js compiles successfully
     - No critical errors in console
   - **And When** I start the backend with `poetry run uvicorn main:app --reload` (from backend directory)
   - **Then**:
     - Backend server starts at `http://localhost:8000`
     - FastAPI application initializes successfully
     - No critical errors in console
     - API documentation available at `http://localhost:8000/docs` (Swagger UI)

6. **Environment Configuration Setup**
   - **Given** the repository includes `.env.example` files
   - **When** I copy them to `.env` files
   - **Then**:
     - Frontend `.env.local` includes: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `NEXT_PUBLIC_API_URL`
     - Backend `.env` includes: `DATABASE_URL`, `REDIS_URL`, `CLERK_SECRET_KEY`, `SENTRY_DSN` (placeholder), `OPENAI_API_KEY` (placeholder)
     - `.gitignore` excludes all `.env` files (except `.env.example`)

## Tasks / Subtasks

- [ ] **Task 1: Initialize Root Workspace Structure** (AC: #1)

  - [ ] Create root `package.json` with pnpm workspaces configuration
  - [ ] Add `pnpm-workspace.yaml` defining workspace packages
  - [ ] Create `.gitignore` with node_modules, .env, Python cache, etc.
  - [ ] Create basic `README.md` with setup instructions

- [ ] **Task 2: Initialize Frontend Package** (AC: #1, #2)

  - [ ] Run `npx create-next-app@latest` in `packages/frontend` with flags: `--typescript --tailwind --app --eslint --src-dir`
  - [ ] Install Clerk: `pnpm add @clerk/nextjs`
  - [ ] Install shadcn/ui dependencies: `@radix-ui/react-*`, `class-variance-authority`, `clsx`, `tailwind-merge`
  - [ ] Install Framer Motion: `pnpm add framer-motion`
  - [ ] Create `.env.local.example` with Clerk keys placeholders
  - [ ] Configure `next.config.js` with API proxy (if needed)

- [ ] **Task 3: Initialize Backend Package** (AC: #1, #3)

  - [ ] Create `packages/backend/` directory
  - [ ] Run `poetry init` with Python 3.11+ requirement
  - [ ] Add FastAPI dependencies: `poetry add fastapi uvicorn[standard]`
  - [ ] Add database dependencies: `poetry add sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings`
  - [ ] Add AI dependencies: `poetry add langchain langgraph langchain-postgres pgvector`
  - [ ] Add infrastructure dependencies: `poetry add arq redis sentry-sdk[fastapi] clerk-backend-sdk`
  - [ ] Add emotion detection dependencies: `poetry add transformers torch`
  - [ ] Add dev dependencies: `poetry add --group dev pytest pytest-asyncio httpx ruff black mypy`
  - [ ] Create basic `app/main.py` with FastAPI app initialization
  - [ ] Create `.env.example` with database URL, Redis URL, API keys placeholders

- [ ] **Task 4: Create Shared Types Package** (AC: #1)

  - [ ] Create `packages/shared/` directory
  - [ ] Create `package.json` with name `@delight/shared`
  - [ ] Create `index.ts` as main barrel export file
  - [ ] Create `types/` directory for TypeScript interfaces (empty for now)

- [ ] **Task 5: Configure Docker Compose** (AC: #4)

  - [ ] Create `docker-compose.yml` at project root
  - [ ] Add PostgreSQL 16 service with pgvector extension image: `postgres:16-alpine` + extension command
  - [ ] Configure PostgreSQL environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - [ ] Add Redis 7 service: `redis:7-alpine`
  - [ ] Map ports: PostgreSQL → 5432, Redis → 6379
  - [ ] Add volumes for data persistence

- [ ] **Task 6: Verify Development Environment** (AC: #5, #6)

  - [ ] Start Docker Compose: `docker-compose up -d`
  - [ ] Verify PostgreSQL connection: `psql` or similar database client
  - [ ] Verify Redis connection: `redis-cli ping`
  - [ ] Start frontend server and access `http://localhost:3000`
  - [ ] Start backend server and access `http://localhost:8000/docs`
  - [ ] Verify FastAPI Swagger UI loads correctly

- [ ] **Task 7: Create Setup Documentation** (AC: #6)

  - [ ] Update `README.md` with:
    - Prerequisites (Node.js 20+, Python 3.11+, Poetry, pnpm, Docker)
    - Setup commands for each package
    - Environment variable configuration steps
    - How to start development servers
  - [ ] Create `docs/DEVELOPMENT.md` with developer guide
  - [ ] Document common setup issues and solutions

- [ ] **Task 8: Manual Testing** (AC: All)
  - [ ] Test on fresh clone: Clone repo, follow README, verify all servers start
  - [ ] Test with no Docker: Attempt without Docker, verify clear error messages
  - [ ] Test frontend hot reload: Edit a component, verify browser updates
  - [ ] Test backend hot reload: Edit an endpoint, verify server reloads
  - [ ] Test environment variable loading: Change a variable, verify it's picked up

## Dev Notes

### Architecture Constraints

From [Tech Spec Epic 1, Section: Technology Stack Decisions]:

- **Frontend Framework:** Next.js 15 with App Router (React Server Components), TypeScript, Tailwind CSS
- **Backend Framework:** FastAPI with async SQLAlchemy 2.0
- **Database:** PostgreSQL 16+ with pgvector extension (vector dimension: 1536 for OpenAI embeddings)
- **Authentication:** Clerk managed service (eliminates need for custom JWT implementation)
- **AI Layer:** LangGraph + LangChain for stateful multi-agent system
- **Emotion Detection:** `cardiffnlp/twitter-roberta-base-emotion-multilingual-latest` (open source, self-hosted)
- **Background Jobs:** ARQ (async Redis queue)
- **Monorepo:** pnpm workspaces for frontend/shared, Poetry for backend Python dependencies

### Project Structure Notes

From [Architecture, Section: Project Structure]:

**Expected directory layout:**

```
delight/
├── packages/
│   ├── frontend/                    # Next.js 15 application
│   │   ├── src/
│   │   │   ├── app/                 # App Router pages
│   │   │   │   ├── (auth)/          # Auth routes (future)
│   │   │   │   ├── (world)/         # World/zone routes (future)
│   │   │   │   ├── companion/       # Eliza chat (future)
│   │   │   │   └── page.tsx         # Home page
│   │   │   ├── components/
│   │   │   │   └── ui/              # shadcn/ui components (future)
│   │   │   ├── lib/
│   │   │   │   ├── api/             # API client (future)
│   │   │   │   ├── hooks/           # React hooks (future)
│   │   │   │   └── utils/           # Utilities
│   │   │   └── types/               # TypeScript types
│   │   ├── public/                  # Static assets
│   │   ├── tailwind.config.ts       # Tailwind config
│   │   └── package.json
│   │
│   ├── backend/                     # FastAPI application
│   │   ├── app/
│   │   │   ├── api/                 # API routes (future)
│   │   │   ├── core/                # Config, dependencies (future)
│   │   │   ├── models/              # SQLAlchemy models (future)
│   │   │   └── main.py              # FastAPI app entry
│   │   ├── pyproject.toml           # Poetry dependencies
│   │   └── .env.example
│   │
│   └── shared/                      # Shared TypeScript types
│       └── types/
│           └── index.ts
│
├── docs/                            # Documentation
│   ├── architecture.md              # Architecture document
│   ├── tech-spec-epic-1.md          # Epic 1 technical spec
│   └── epics.md                     # Epic breakdown
│
├── docker-compose.yml               # Local dev environment
├── package.json                     # Root workspace config
├── pnpm-workspace.yaml              # pnpm workspace definition
└── README.md                        # Main setup guide
```

**Important:** This story creates the structure and installs dependencies only. Actual application logic (routes, models, services) will be implemented in subsequent stories.

### Testing Strategy

From [Tech Spec Epic 1, Section: Test Strategy Summary]:

**For this story:**

- **Manual Testing:** Primary focus for infrastructure setup
  - Verify all services start without errors
  - Check documentation is accurate (fresh clone test)
  - Test hot reload functionality
  - Verify environment variable loading

**Future stories will add:**

- Frontend unit tests: Jest + React Testing Library
- Backend unit tests: pytest + httpx
- Integration tests: Database + API tests

### Cost Considerations

From [Architecture, Section: Cost Management]:

- **LLM Operational Target:** $0.50/user/day
  - GPT-4o-mini (primary): $0.15/$0.60 per 1M tokens
  - GPT-4o (narrative only): $2.50/$10 per 1M tokens
  - Emotion detection: Self-hosted (free after infrastructure)
- **Clerk Authentication:** Free tier: 10,000 MAU, then $25/1,000 MAU
- **Database:** Connection pooling required, pgvector indexes on vector columns

### References

- [Source: tech-spec-epic-1.md#Detailed-Design] - Service modules, data models, API contracts
- [Source: tech-spec-epic-1.md#Dependencies-and-Integrations] - Complete dependency list with versions
- [Source: architecture.md#Technology-Stack-Details] - Core technology decisions
- [Source: architecture.md#Project-Structure] - Expected directory layout
- [Source: architecture.md#ADR-007] - Clerk authentication decision rationale
- [Source: architecture.md#ADR-008] - Open source emotion detection model selection
- [Source: architecture.md#ADR-009] - GPT-4o-mini as primary LLM decision
- [Source: epics.md#Story-1.1] - Original story definition with acceptance criteria

## Dev Agent Record

### Context Reference

- [Story Context XML](./1-1-initialize-monorepo-structure-and-core-dependencies.context.xml)

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent_
