# Epic Technical Specification: User Onboarding & Foundation

Date: 2025-11-10
Author: Jack
Epic ID: 1
Status: Draft

---

## Overview

Epic 1 establishes the technical foundation for Delight, a self-improvement companion platform that pairs emotionally intelligent AI coaching with structured progress systems. This epic delivers the core infrastructure—monorepo structure, authentication, database, and deployment pipeline—that all subsequent features depend on.

The foundation aligns with the Product Brief's vision of creating "software that feels seamlessly supportive and ruthlessly effective" by establishing a robust, scalable architecture using modern tools (Next.js 15, FastAPI, PostgreSQL with pgvector, Clerk authentication) that can support the emotionally aware companion, mission management, and narrative systems planned for future epics.

## Objectives and Scope

### In Scope

1. **Monorepo initialization** with proper workspace structure for frontend (Next.js 15), backend (FastAPI), and shared packages
2. **Core dependency installation** including:
   - Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui, Clerk authentication
   - Backend: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL drivers, Pydantic, Alembic, Clerk backend SDK
   - AI Foundation: LangChain, LangGraph, langchain-postgres, pgvector, transformers
   - Infrastructure: ARQ (async job queue), Redis, Sentry
3. **Database schema and migrations** including core user tables, pgvector extension setup, Alembic configuration
4. **Clerk authentication integration** with OAuth providers (Google, GitHub), magic links, webhook sync to local user database
5. **Deployment pipeline** with CI/CD (linting, testing, Docker builds), environment configuration, health check endpoints
6. **Development environment** with Docker Compose for PostgreSQL + Redis, local development servers

### Out of Scope (Deferred to Later Epics)

- **User onboarding flow UI** (Story 1.4 - moved after Epic 2 to showcase actual features)
- **Business logic** for goals, missions, or AI companions (Epic 2-3)
- **Production hosting setup** (MVP will use Railway/Render/similar platform)
- **Advanced monitoring/observability** beyond basic health checks (post-MVP)

## System Architecture Alignment

This epic implements the foundational layer of the architecture defined in `architecture.md`:

### Technology Stack Decisions

- **Frontend**: Next.js 15 with App Router, React Server Components, TypeScript, Tailwind CSS
- **Backend**: FastAPI with async SQLAlchemy 2.0, providing REST APIs and SSE streaming
- **Database**: PostgreSQL 16+ with pgvector extension for vector embeddings (1536 dimensions for OpenAI text-embedding-3-small)
- **Authentication**: Clerk (managed auth service) handling passwords, sessions, OAuth, magic links
- **Job Queue**: ARQ + Redis for background workers (quest generation, nudges, world state updates)
- **Monorepo**: pnpm workspaces for frontend/shared, Poetry for backend Python dependencies

### Infrastructure Constraints

- **Cost target**: <$0.10 per active user per day (guides infrastructure choices)
- **Development environment**: Docker Compose for local PostgreSQL + Redis
- **Deployment**: Containerized services (Docker) with environment-based configuration
- **Observability**: Sentry for error tracking, health check endpoints for uptime monitoring

## Detailed Design

### Services and Modules

| Service/Module                    | Responsibility                                                 | Inputs                      | Outputs                     | Owner/Location                        |
| --------------------------------- | -------------------------------------------------------------- | --------------------------- | --------------------------- | ------------------------------------- |
| **Frontend (Next.js)**            | User interface, client-side routing, SSR/RSC                   | User actions, API responses | Rendered UI, API requests   | `packages/frontend/`                  |
| **Backend API Gateway (FastAPI)** | REST API endpoints, request validation, response serialization | HTTP requests               | JSON responses, SSE streams | `packages/backend/app/main.py`        |
| **Database Service**              | Data persistence, schema management, migrations                | SQL queries via SQLAlchemy  | Query results               | PostgreSQL container                  |
| **Auth Service (Clerk)**          | User authentication, session management, OAuth                 | Login attempts, tokens      | Session tokens, webhooks    | External (Clerk)                      |
| **Auth Middleware**               | Session validation, user context injection                     | Clerk session tokens        | Validated user object       | `packages/backend/app/auth/`          |
| **Migration System (Alembic)**    | Schema versioning, migration application                       | Migration scripts           | Database schema changes     | `packages/backend/app/db/migrations/` |
| **Health Check Service**          | System status monitoring                                       | Internal checks             | Health status JSON          | `packages/backend/app/health/`        |

### Data Models and Contracts

#### Core User Schema (PostgreSQL)

```sql
-- Users table (synced from Clerk via webhook)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,  -- Primary identifier from Clerk
    email VARCHAR(255) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences (extended profile data)
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    custom_hours JSONB,  -- {start: "09:00", end: "17:00", timezone: "America/Los_Angeles"}
    theme VARCHAR(50) DEFAULT 'modern',
    communication_preferences JSONB,  -- {email: true, sms: false, in_app: true}
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable pgvector extension (for future AI memory)
CREATE EXTENSION IF NOT EXISTS vector;
```

#### SQLAlchemy Models

```python
# packages/backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    preferences = relationship("UserPreferences", back_populates="user", uselist=False)

class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    custom_hours = Column(JSONB)
    theme = Column(String(50), default='modern')
    communication_preferences = Column(JSONB)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="preferences")
```

#### API Contracts

```typescript
// packages/shared/types/user.ts
export interface User {
  id: string;
  clerk_user_id: string;
  email: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  id: string;
  user_id: string;
  custom_hours?: {
    start: string;
    end: string;
    timezone: string;
  };
  theme: "modern" | "medieval" | "sci-fi";
  communication_preferences?: {
    email: boolean;
    sms: boolean;
    in_app: boolean;
  };
  onboarding_completed: boolean;
}
```

### APIs and Interfaces

#### Authentication Endpoints

```
POST /api/v1/webhooks/clerk
Description: Clerk webhook receiver for user lifecycle events
Request Body: ClerkWebhookEvent (signed by Clerk)
Response: 200 OK / 400 Bad Request
Events: user.created, user.updated, user.deleted
```

#### User Preferences Endpoints

```
GET /api/v1/users/me
Description: Get current authenticated user
Auth: Required (Clerk session)
Response: User object with preferences

PATCH /api/v1/users/preferences
Description: Update user preferences
Auth: Required (Clerk session)
Request Body: Partial<UserPreferences>
Response: Updated UserPreferences object
```

#### Health Check Endpoints

```
GET /api/v1/health
Description: System health status
Auth: None
Response: {
  status: "healthy" | "degraded" | "unhealthy",
  database: "connected" | "disconnected",
  redis: "connected" | "disconnected",
  timestamp: ISO8601
}
```

#### FastAPI Dependency for Authentication

```python
# packages/backend/app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_sdk import Clerk

clerk = Clerk(api_key=settings.CLERK_SECRET_KEY)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate Clerk session token and return user object."""
    try:
        # Verify session token with Clerk
        session = clerk.sessions.verify_session(
            credentials.credentials
        )

        # Fetch user from local database
        result = await db.execute(
            select(User).where(User.clerk_user_id == session.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )

        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

### Workflows and Sequencing

#### User Registration Flow

```
1. User clicks "Sign Up" in frontend
   → Frontend: Redirect to Clerk SignUp component

2. User completes registration (email/password or OAuth)
   → Clerk: Creates user account, generates session

3. Clerk sends webhook: user.created
   → Backend: POST /api/v1/webhooks/clerk
   → Backend: Create User record in PostgreSQL
   → Backend: Create default UserPreferences record

4. Frontend receives session from Clerk
   → Frontend: Store session in cookies/localStorage
   → Frontend: Redirect to /companion (deferred onboarding)

5. Subsequent authenticated requests
   → Frontend: Include Clerk session token in Authorization header
   → Backend: Validate token via get_current_user dependency
```

#### Database Migration Workflow

```
1. Developer creates migration
   → Terminal: alembic revision -m "Add users table"
   → Generated: packages/backend/app/db/migrations/versions/xxx_add_users_table.py

2. Developer implements upgrade/downgrade
   → Edit migration file with SQLAlchemy operations

3. Apply migration (local dev)
   → Terminal: alembic upgrade head
   → PostgreSQL: Schema updated

4. CI/CD pipeline (deployment)
   → Docker build includes migrations
   → Container startup runs: alembic upgrade head
   → Deployment proceeds if migrations succeed
```

#### Development Server Startup

```
1. Start infrastructure
   → Terminal: docker-compose up -d
   → Containers: PostgreSQL (port 5432), Redis (port 6379)

2. Start backend
   → Terminal: cd packages/backend && poetry run uvicorn main:app --reload
   → Server: http://localhost:8000
   → Automatic: Apply pending migrations on startup

3. Start frontend
   → Terminal: cd packages/frontend && pnpm dev
   → Server: http://localhost:3000
   → Proxy: API requests forwarded to localhost:8000
```

## Non-Functional Requirements

### Performance

| Metric                                      | Target              | Rationale                                        |
| ------------------------------------------- | ------------------- | ------------------------------------------------ |
| **API Response Time (p95)**                 | < 500ms             | Maintain responsive UX for all CRUD operations   |
| **Database Query Time (p95)**               | < 100ms             | Ensure efficient database interactions           |
| **Page Load Time (First Contentful Paint)** | < 1.5s              | Modern web performance standard                  |
| **Server Cold Start**                       | < 5s                | Acceptable for serverless/container environments |
| **Migration Execution**                     | < 30s per migration | Minimize deployment downtime                     |

### Security

1. **Authentication & Authorization**

   - All authentication handled by Clerk (OAuth 2.0, OIDC compliant)
   - Session tokens verified on every protected API request
   - No passwords stored in Delight database (Clerk handles)
   - Clerk provides: breach detection, 2FA, session management

2. **Data Protection**

   - Environment variables for all secrets (DATABASE_URL, CLERK_SECRET_KEY, etc.)
   - `.env` files excluded from git via `.gitignore`
   - Production secrets stored in deployment platform secret manager
   - Database connections use TLS in production

3. **API Security**

   - CORS configured to allow only known origins (frontend domain)
   - Clerk webhook signatures verified to prevent spoofing
   - Input validation via Pydantic models on all endpoints
   - Rate limiting on public endpoints (future: implement rate limiter middleware)

4. **Dependency Security**
   - Regular dependency updates via Dependabot
   - `poetry check` and `pnpm audit` in CI pipeline
   - Sentry for runtime error monitoring and alerting

### Reliability/Availability

1. **Database Reliability**

   - PostgreSQL connection pooling (SQLAlchemy async engine)
   - Graceful degradation: show cached data if database unavailable
   - Automated backups (daily) via hosting provider
   - Point-in-time recovery capability

2. **Service Availability**

   - Health check endpoint monitored by deployment platform
   - Automatic container restart on crash
   - Zero-downtime deployments via rolling updates
   - Target uptime: 99.5% (MVP), 99.9% (post-MVP)

3. **Error Handling**

   - All API errors return structured JSON with error codes
   - Frontend displays user-friendly error messages
   - Sentry captures exceptions with context (user ID, request details)
   - Failed migrations halt deployment (prevent partial schema state)

4. **Third-Party Dependencies**
   - Clerk: 99.99% SLA, fallback to session cache if verification slow
   - Deployment platform health checks ensure service recovery

### Observability

1. **Logging**

   - Structured JSON logs (timestamp, level, message, context)
   - Log levels: DEBUG (dev), INFO (staging), WARNING/ERROR (production)
   - Logs include request_id for tracing across services
   - Sensitive data (emails, tokens) masked in logs

2. **Metrics**

   - Health check endpoint exposes: database status, Redis status, uptime
   - Application metrics: request count, response time, error rate
   - Infrastructure metrics: CPU, memory, disk usage (platform-provided)

3. **Error Tracking**

   - Sentry integration captures all unhandled exceptions
   - Frontend errors include: stack trace, user context, browser info
   - Backend errors include: stack trace, request details, database state

4. **Tracing (Future)**
   - OpenTelemetry instrumentation for request tracing
   - Trace across frontend → backend → database
   - Trace storage in dedicated APM (post-MVP: DataDog, New Relic)

## Dependencies and Integrations

### Frontend Dependencies (packages/frontend/package.json)

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@clerk/nextjs": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "framer-motion": "^11.0.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/react": "^19.0.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.2.0"
  }
}
```

### Backend Dependencies (packages/backend/pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.25"}
asyncpg = "^0.29.0"
alembic = "^1.13.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
clerk-backend-sdk = "^0.3.0"
redis = "^5.0.1"
arq = "^0.26.0"
sentry-sdk = {extras = ["fastapi"], version = "^1.40.0"}
langchain = "^0.1.0"
langgraph = "^0.0.20"
langchain-postgres = "^0.0.3"
pgvector = "^0.2.4"
transformers = "^4.36.0"
torch = "^2.1.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.23.0"
httpx = "^0.26.0"
ruff = "^0.1.11"
black = "^23.12.0"
mypy = "^1.8.0"
```

### Shared Types (packages/shared/package.json)

```json
{
  "name": "@delight/shared",
  "version": "0.1.0",
  "main": "index.ts",
  "types": "index.ts"
}
```

### Infrastructure Dependencies

- **PostgreSQL**: Version 16+ (Docker: postgres:16-alpine)
- **Redis**: Version 7+ (Docker: redis:7-alpine)
- **Docker**: Version 24+ for containerization
- **pnpm**: Version 8+ for frontend workspace management
- **Poetry**: Version 1.7+ for backend dependency management

### External Service Integrations

1. **Clerk Authentication**

   - Integration: Clerk JavaScript SDK (frontend), Clerk Backend SDK (backend)
   - Configuration: Clerk Publishable Key (public), Clerk Secret Key (backend only)
   - Webhook endpoint: `POST /api/v1/webhooks/clerk` with signature verification
   - Cost: Free tier (10,000 MAU), then $25/1,000 MAU

2. **Sentry Error Tracking**
   - Integration: Sentry SDK (frontend + backend)
   - Configuration: Sentry DSN, environment tags
   - Cost: Free tier (5,000 errors/month), then $26/month

## Acceptance Criteria (Authoritative)

### AC1: Monorepo Structure Initialized

- **Given** a new development environment
- **When** repository is cloned and setup commands executed
- **Then**:
  - Directory structure exists: `packages/frontend/`, `packages/backend/`, `packages/shared/`
  - Root `package.json` with pnpm workspace configuration
  - Backend `pyproject.toml` with Poetry dependencies
  - Docker Compose file with PostgreSQL and Redis services
  - All services start successfully: `pnpm dev` (frontend), `poetry run uvicorn main:app --reload` (backend)

### AC2: Database Schema and Migrations Working

- **Given** PostgreSQL is running via Docker Compose
- **When** Alembic migrations are applied (`alembic upgrade head`)
- **Then**:
  - `users` table exists with correct schema (id, clerk_user_id, email, timezone, timestamps)
  - `user_preferences` table exists with foreign key to users
  - `pgvector` extension is enabled
  - `alembic_version` table tracks migration history
  - `alembic downgrade -1` successfully rolls back last migration

### AC3: Clerk Authentication Integrated

- **Given** Clerk project configured with OAuth providers
- **When** user registers or logs in via frontend
- **Then**:
  - Clerk SignUp/SignIn components render correctly
  - User can authenticate with email/password, Google OAuth, or GitHub OAuth
  - Clerk webhook fires on user.created event
  - Backend receives webhook and creates user record in local database
  - User record includes clerk_user_id, email, and default timezone
  - Subsequent authenticated API requests include valid Clerk session token
  - Backend validates token and returns user object via `get_current_user` dependency

### AC4: User Preferences CRUD Working

- **Given** authenticated user session
- **When** user updates preferences via `PATCH /api/v1/users/preferences`
- **Then**:
  - Request validates Clerk session token
  - Preferences saved to `user_preferences` table
  - Response returns updated preferences object
  - `GET /api/v1/users/me` returns user with preferences

### AC5: Deployment Pipeline Configured

- **Given** code pushed to main branch
- **When** CI/CD pipeline executes
- **Then**:
  - Frontend linting passes (ESLint)
  - Backend linting passes (Ruff, Black)
  - Frontend tests pass (if any exist)
  - Backend tests pass (if any exist)
  - Docker images build successfully for frontend and backend
  - Health check endpoint (`GET /api/v1/health`) returns 200 OK
  - Services can connect to PostgreSQL and Redis
  - Deployment to staging environment succeeds

### AC6: Development Environment Reproducible

- **Given** new developer clones repository
- **When** following setup instructions in README
- **Then**:
  - Docker Compose starts PostgreSQL and Redis
  - Backend dependencies install via `poetry install`
  - Frontend dependencies install via `pnpm install`
  - Environment variables configured from `.env.example` files
  - Both services start and communicate successfully
  - Health check returns healthy status
  - Developer can make authenticated requests to backend

## Traceability Mapping

| AC  | Spec Section                           | Components/APIs                                                                  | Test Idea                                                                  |
| --- | -------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| AC1 | Services and Modules, Dependencies     | Monorepo structure, package.json, pyproject.toml, docker-compose.yml             | Test: Run `pnpm dev` and `poetry run uvicorn`, verify both servers respond |
| AC2 | Data Models, Workflows (Migration)     | Alembic, PostgreSQL schema, SQLAlchemy models                                    | Test: Run migrations up and down, query tables, verify pgvector extension  |
| AC3 | APIs (Auth), Workflows (Registration)  | Clerk webhooks, `POST /api/v1/webhooks/clerk`, get_current_user dependency       | Test: Mock Clerk webhook, verify user created; test token validation       |
| AC4 | APIs (User Preferences), Data Models   | `GET /api/v1/users/me`, `PATCH /api/v1/users/preferences`, UserPreferences model | Test: Authenticated PATCH request, verify database update, GET to confirm  |
| AC5 | NFR (Reliability), APIs (Health Check) | CI/CD pipeline, health check endpoint, Docker builds                             | Test: Health check returns 200; verify database and Redis connections      |
| AC6 | NFR (Reliability), Dependencies        | Docker Compose, environment configuration, README                                | Test: Fresh checkout, run setup script, verify all services start          |

## Risks, Assumptions, Open Questions

### Risks

1. **Risk**: Clerk dependency creates vendor lock-in

   - **Mitigation**: Clerk provides standard OAuth/OIDC, migration path exists to self-hosted auth
   - **Impact**: Medium (migration effort if needed)

2. **Risk**: pgvector installation may fail on some PostgreSQL versions

   - **Mitigation**: Use PostgreSQL 16+ which has better pgvector support; Docker image ensures consistency
   - **Impact**: Low (controlled via Docker)

3. **Risk**: Next.js 15 App Router is relatively new, may have bugs

   - **Mitigation**: Monitor Next.js issues, have fallback to Pages Router if critical issues arise
   - **Impact**: Low (mature framework, active community)

4. **Risk**: Poetry dependency resolution can be slow on first install

   - **Mitigation**: Use `poetry install --no-root` in CI, cache dependencies
   - **Impact**: Low (one-time cost per developer)

5. **Risk**: Alembic migrations could fail mid-deployment
   - **Mitigation**: Test migrations on staging first, use transactions where possible, have rollback plan
   - **Impact**: High (would block deployment)

### Assumptions

1. **Assumption**: Developers have Docker installed and configured

   - **Validation**: Document Docker as prerequisite in README

2. **Assumption**: Clerk free tier (10,000 MAU) sufficient for MVP

   - **Validation**: Monitor usage, plan for paid tier if growth exceeds

3. **Assumption**: Single-region deployment acceptable for MVP (no multi-region)

   - **Validation**: Confirmed by cost constraints, can expand post-MVP

4. **Assumption**: PostgreSQL on managed hosting (Railway/Render) sufficient for performance

   - **Validation**: Load testing after MVP to confirm

5. **Assumption**: Developers comfortable with TypeScript, Python, async/await patterns
   - **Validation**: Team skill assessment, provide learning resources if needed

### Open Questions

1. **Question**: Should we use Railway, Render, or Fly.io for MVP hosting?

   - **Decision Needed**: Compare pricing, PostgreSQL support, deployment ease
   - **Timeline**: Before Story 1.5 (deployment pipeline)

2. **Question**: What's the backup strategy for PostgreSQL data?

   - **Decision Needed**: Daily automated backups vs continuous replication
   - **Timeline**: During Story 1.5 setup

3. **Question**: Should frontend and backend share a single repository or separate repos?

   - **Decision**: Single monorepo (current approach) - confirmed
   - **Rationale**: Easier for solo dev, shared types, atomic commits

4. **Question**: Do we need API versioning from day one (/api/v1)?
   - **Decision**: Yes, include from start for future compatibility
   - **Rationale**: Low cost, prevents breaking changes later

## Test Strategy Summary

### Test Levels

1. **Unit Tests**

   - **Frontend**: React component tests (Jest + React Testing Library)
   - **Backend**: FastAPI route tests (pytest + httpx)
   - **Target Coverage**: 70%+ for core logic (models, utilities)

2. **Integration Tests**

   - Database integration: Test SQLAlchemy models with real PostgreSQL (test database)
   - API integration: Test end-to-end request flows with test client
   - Clerk webhook integration: Mock webhook payloads, verify user creation

3. **System Tests**
   - Health check returns correct status
   - Migration up/down works without errors
   - Docker Compose environment starts all services

### Test Frameworks

- **Frontend**: Jest, React Testing Library, Playwright (future E2E)
- **Backend**: pytest, pytest-asyncio, httpx (async test client)
- **Database**: pytest fixtures with transactional rollback
- **Linting**: ESLint (frontend), Ruff + Black (backend)

### Critical Test Scenarios

1. **User Registration Flow**

   - Test: User signs up via Clerk → webhook creates user in DB
   - Expected: User record exists with clerk_user_id

2. **Authentication Dependency**

   - Test: Valid token passes `get_current_user`, invalid token returns 401
   - Expected: Dependency correctly validates and rejects tokens

3. **Migration Reversibility**

   - Test: Apply migration → downgrade → re-apply
   - Expected: Database schema matches, no orphaned data

4. **Health Check Accuracy**

   - Test: Database down → health check returns "unhealthy"
   - Expected: Endpoint accurately reflects service status

5. **Environment Configuration**
   - Test: Missing required env vars → app fails to start with clear error
   - Expected: Early validation prevents silent failures

### Continuous Integration

- **Pre-commit**: Linting via ESLint, Ruff
- **CI Pipeline**:
  1. Install dependencies
  2. Run linters (fail on warnings)
  3. Run unit tests (fail if coverage < 70%)
  4. Run integration tests
  5. Build Docker images
  6. Deploy to staging (if on main branch)

### Manual Testing Checklist (Story 1.3)

- [ ] Sign up with email/password
- [ ] Sign up with Google OAuth
- [ ] Sign up with GitHub OAuth
- [ ] Verify user created in local database
- [ ] Make authenticated API request
- [ ] Log out and verify session invalidated
- [ ] Update user preferences via API
- [ ] Verify preferences persisted in database

---

**Epic 1 Technical Specification Complete**

This specification provides the technical blueprint for implementing the foundation of Delight. All subsequent epics depend on this infrastructure being solid and well-tested.

**Next Step**: Use the `create-story` workflow to draft Story 1.1 (Initialize Monorepo Structure).
