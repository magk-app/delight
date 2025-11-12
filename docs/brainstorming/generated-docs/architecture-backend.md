# Backend Architecture (FastAPI)

Generated 2025-11-12 from `packages/backend`.

## Executive Summary

The backend is a FastAPI 0.109+ service that exposes REST endpoints for health checks, authenticated user data, and Clerk webhooks. It persists user + memory data in Postgres (pgvector enabled) and will host LangGraph/LangChain workflows as Epic 2 develops the companion memory system.

## Technology Stack

- **Language:** Python 3.11
- **Framework:** FastAPI + Uvicorn
- **Persistence:** PostgreSQL 16 with pgvector, SQLAlchemy 2 async ORM, Alembic migrations
- **Background Jobs:** Redis + ARQ (dependencies already present)
- **AI:** LangChain, LangGraph, OpenAI SDK (wired once missions/chat are enabled)
- **Testing:** Pytest + pytest-asyncio, HTTPX

## Architecture Pattern

Layered service:

1. **Routers (`app/api/v1`)** – REST endpoints with dependency injection.
2. **Core/Services (`app/core`, `app/services`)** – Auth helpers, Clerk sync logic.
3. **Data Layer (`app/models`, `app/db`)** – SQLAlchemy models, session factory, migrations.
4. **Workers (future)** – ARQ tasks for mission orchestration and memory pruning.

## Data Architecture

See `data-models-backend.md` for tables. Highlights:
- `users` keyed by `clerk_user_id`.
- `user_preferences` storing JSONB settings + onboarding flags.
- `memories` table with pgvector(1536) embeddings and tiered `MemoryType`.
- `memory_collections` optional grouping for future mission/memory features.

## API Design

Documented in `api-contracts-backend.md`. Current endpoints:
- `GET /api/v1/health` – system probe.
- `GET /api/v1/users/me` – authenticated profile.
- `POST /api/v1/webhooks/clerk` – Svix-verified webhook handler.
The router structure makes it easy to add `/api/v1/memories`, `/api/v1/missions`, etc., with shared dependencies.

## Component Overview

- **ClerkService (`app/services/clerk_service.py`)** – Upserts user data from webhook payloads.
- **Clerk auth dependency (`app/core/clerk_auth.py`)** – Verifies session tokens.
- **Health check** – Aggregates DB + Redis status, with TODO for real Redis ping.
- **Webhooks router** – Handles signature validation and logging.

## Source Tree

Key folders:
- `app/api/v1` – routers.
- `app/models` – ORM definitions.
- `app/db/migrations` – schema history (003 introduces memories + pgvector).
- `tests/` – integration suites (auth, webhooks) plus helper fixtures.
See `source-tree-analysis.md` for the annotated monorepo tree.

## Development Workflow

Steps summarized in `development-guide.md`. TL;DR:
- `poetry install`
- Copy `.env.example` → `.env`
- `poetry run uvicorn main:app --reload`
- Tests via `poetry run pytest`
- Lint via `pnpm lint` (root script) or `poetry run ruff check`

## Deployment Architecture

- Containerized via `packages/backend/Dockerfile`.
- Configured with `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET`, `DATABASE_URL`, optional `REDIS_URL`, `SENTRY_DSN`.
- Healthed by `/api/v1/health`.
- Migrations applied separately via Alembic CLI or bootstrap job.
- Refer to `deployment-overview.md` for the checklist.

## Testing Strategy

- **Unit/Integration:** Pytest with async support (`tests/integration` covers auth + webhooks).
- **E2E:** Trigger Clerk webhook test events against `/api/v1/webhooks/clerk`.
- **Monitoring:** Add Sentry DSN + logs once mission flows ship.
