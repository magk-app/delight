# Epic 1: User Onboarding & Foundation

**Epic Goal:** Establish the technical foundation and user authentication system that enables all subsequent features. This epic sets up the monorepo structure, deployment pipeline, core backend/frontend infrastructure, and basic user onboarding flow.

**Architecture Components:** Next.js 15, FastAPI, PostgreSQL + pgvector, Docker, deployment pipeline, auth system

### Story 1.1: Initialize Monorepo Structure and Core Dependencies

As a **developer**,  
I want **a properly structured monorepo with backend, frontend, and shared packages**,  
So that **the team can work efficiently with proper tooling and dependency management**.

**Acceptance Criteria:**

**Given** I am setting up a new development environment  
**When** I run the initialization commands  
**Then** the monorepo structure is created with:

- `packages/frontend/` with Next.js 15 + TypeScript + Tailwind
- `packages/backend/` with FastAPI + Poetry + async SQLAlchemy
- `packages/shared/` for TypeScript types
- Docker Compose for local PostgreSQL + Redis
- Root package.json with workspace configuration

**And** all core dependencies are installed:

- Frontend: Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui, @clerk/nextjs
- Backend: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL driver (asyncpg), Pydantic, Alembic, clerk-backend-sdk
- AI: LangChain, LangGraph, langchain-postgres, pgvector, transformers (for emotion detection)
- Infrastructure: ARQ, Redis, Sentry

**And** development servers can start successfully:

- `pnpm dev` (frontend at localhost:3000)
- `poetry run uvicorn main:app --reload` (backend at localhost:8000)

**Prerequisites:** None (first story)

**Technical Notes:**

- Use `npx create-next-app@latest` with App Router + TypeScript
- Install Clerk: `npm install @clerk/nextjs`
- Use Poetry for Python dependency management
- Install Clerk backend SDK: `poetry add clerk-backend-sdk`
- Install emotion detection model: `poetry add transformers torch`
- Install pgvector extension in Docker PostgreSQL container
- See Architecture doc lines 29-50 for exact initialization commands

---

### Story 1.2: Set Up Database Schema and Migrations

As a **developer**,  
I want **a versioned database schema with migration tooling**,  
So that **schema changes are tracked and can be applied consistently across environments**.

**Acceptance Criteria:**

**Given** the monorepo is initialized  
**When** I set up the database system  
**Then** Alembic is configured for migrations in `backend/app/db/migrations/`

**And** initial schema includes core tables:

- `users` (id UUID PRIMARY KEY, clerk_user_id VARCHAR UNIQUE, email, timezone, created_at, updated_at)
  - NOTE: clerk_user_id is the primary identifier from Clerk; passwords/sessions managed by Clerk
- `user_preferences` (user_id FK, custom_hours JSONB, theme, communication_preferences JSONB)

**And** pgvector extension is enabled in PostgreSQL

**And** I can run migrations successfully:

- `alembic upgrade head` applies all migrations
- `alembic downgrade -1` rolls back successfully

**Prerequisites:** Story 1.1 (monorepo structure)

**Technical Notes:**

- Use SQLAlchemy 2.0 declarative base with async support
- Install pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;`
- Store migrations in `backend/app/db/migrations/`
- Base models in `backend/app/models/base.py`

---

### Story 1.3: Integrate Clerk Authentication System

As a **new user**,  
I want **to register and log in securely with multiple options**,  
So that **my data is protected and I can use social login or email authentication**.

**Acceptance Criteria:**

**Given** the database schema is set up and Clerk is configured  
**When** I navigate to the app  
**Then** I see the Clerk authentication UI with options to:

- Sign up with email/password
- Sign in with Google OAuth
- Sign in with GitHub OAuth
- Use magic link authentication

**And** when I complete authentication  
**Then** a user record is created in our database with my Clerk user ID

**And** when I make authenticated requests to the backend  
**Then** the backend validates my Clerk session and grants access to protected endpoints

**And** when I log out  
**Then** my Clerk session is invalidated across all devices

**And** the authentication UI matches our app's theme (medieval/modern)

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- **Frontend:** Use `@clerk/nextjs` with App Router middleware
  - Wrap app in `<ClerkProvider>`
  - Protect routes with `middleware.ts` for authentication
  - Use `<SignIn>` and `<SignUp>` components or build custom UI
- **Backend:** Use `clerk-backend-sdk` for session verification
  - Create FastAPI dependency: `get_current_user()` that verifies Clerk session tokens
  - On first authentication, create user record in DB using Clerk webhook
- **Clerk Configuration:**
  - Set up Clerk project at clerk.com
  - Configure OAuth providers (Google, GitHub)
  - Set up webhook endpoint: `POST /api/v1/webhooks/clerk` (user.created, user.updated, user.deleted)
  - Store Clerk API keys in environment variables
- **User Sync:** When Clerk webhook fires for `user.created`, create corresponding user in our DB:

  ```python
  users.create(
      clerk_user_id=clerk_event.data.id,
      email=clerk_event.data.email_addresses[0].email_address,
      timezone="UTC"  # default, updated in onboarding
  )
  ```

- **Cost:** Free tier: 10,000 MAU, then $25/1000 MAU
- **Security:** Clerk handles password hashing, session management, 2FA, breach detection

---

### Story 1.4: Create User Onboarding Flow (MVP)

**⚠️ NOTE:** This story will be moved to later in the development sequence (after Epic 2: Companion & Memory System is complete). Rationale: Onboarding should showcase actual app features, which need to exist first.

As a **new user**,  
I want **a guided onboarding experience**,  
So that **I understand Delight's purpose and can set my initial preferences**.

**Acceptance Criteria:**

**Given** I have just registered  
**When** I complete the onboarding flow  
**Then** I see 3 onboarding screens:

1. Welcome screen explaining Delight's companion concept
2. Timezone and productive hours selection
3. Communication preferences (in-app, email, SMS opt-in)

**And** my preferences are saved to the database

**And** after completion, I am redirected to the companion chat interface

**And** if I close the app mid-onboarding  
**Then** I resume from my last completed step on next login

**Prerequisites:** Story 1.3 (authentication system)

**Technical Notes:**

- Frontend: `frontend/src/app/(auth)/onboarding/` with 3 step pages
- Backend: `POST /api/v1/users/preferences` endpoint
- Store onboarding progress in `user_preferences.onboarding_completed` boolean
- Use React state management for multi-step form
- Mobile-responsive design with Tailwind

---

### Story 1.5: Set Up Deployment Pipeline and Environment Configuration

As a **developer**,  
I want **automated deployment and environment management**,  
So that **we can deploy to staging/production with confidence**.

**Acceptance Criteria:**

**Given** the application is ready for deployment  
**When** I push to the main branch  
**Then** CI/CD pipeline runs:

- Lints frontend (ESLint) and backend (Ruff/Black)
- Runs frontend tests (Jest)
- Runs backend tests (pytest)
- Builds Docker images for backend and frontend
- Deploys to staging environment

**And** environment variables are properly configured:

- `.env.example` files exist for frontend and backend
- Secrets are managed securely (not committed to git)
- Different configs for dev/staging/production

**And** health check endpoints are available:

- `GET /api/v1/health` returns 200 with system status
- Frontend and backend can connect to database and Redis

**Prerequisites:** Stories 1.1-1.4 (all foundation components)

**Technical Notes:**

- Use GitHub Actions or similar CI/CD
- Docker Compose for local dev, separate Dockerfiles for production
- Environment variables: DATABASE_URL, REDIS_URL, JWT_SECRET, LLM_API_KEY
- Health check includes database connection test
- Consider Railway/Render/Fly.io for MVP hosting

---
