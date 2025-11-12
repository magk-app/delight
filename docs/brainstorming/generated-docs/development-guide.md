# Delight Development Setup

Unified reference for bootstrapping the monorepo (captured 2025-11-12). Use this alongside the deeper guides in `docs/dev/SETUP.md` and `docs/dev/BMAD-DEVELOPER-GUIDE.md`.

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Node.js | >= 20.0.0 | Enforced via `package.json` engines |
| pnpm | >= 8.0.0 | Workspace manager for frontend + shared packages |
| Python | 3.11.x | FastAPI service + Poetry virtualenv |
| Poetry | 1.7+ | Manages backend dependencies (`pyproject.toml`) |
| PostgreSQL | 16 (pgvector ready) | Use Docker compose or Supabase |
| Redis | 7 | Needed for future ARQ workers; optional today |

## Repository Bootstrap

```bash
# install JS deps
pnpm install

# install backend deps
cd packages/backend
poetry install
```

Environment files:
- Copy `.env.example` → `.env` inside `packages/backend`.
- For the frontend, create `packages/frontend/.env.local` with `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `NEXT_PUBLIC_API_URL`.

## Running Everything

Monorepo helper scripts live in the root `package.json`:

```bash
# Run frontend (Next dev) + backend (uvicorn) concurrently
pnpm dev

# Individual targets
pnpm dev:frontend
pnpm dev:backend  # wraps poetry + uvicorn
```

Frontend runs on http://localhost:3000; backend on http://127.0.0.1:8000.

## Testing & QA

| Command | Description |
|---------|-------------|
| `pnpm test:frontend` | Frontend unit tests (if configured) |
| `pnpm test:e2e` | Playwright suite under `packages/frontend/tests` |
| `poetry run pytest` | Backend unit + integration tests |
| `pnpm lint` | Next lint + Ruff check |
| `pnpm lint:fix` | Next lint --fix + Ruff + Black |

## Environment Services (Docker)

`docker-compose.yml` provides local Postgres + Redis:

```bash
docker compose up postgres redis
```

- Postgres credentials: `postgres/postgres`, DB `delight`.
- Redis: default port 6379.
- Pgvector extension is enabled in Story 1.2 migrations; run Alembic after the container starts.

## Contribution Workflow

- Follow `docs/dev/CONTRIBUTING.md` for PR expectations (code style, testing, CI).
- Use BMAD workflow commands (`workflow-status`, `workflow-init`, etc.) to stay aligned with the method track.
- Keep documentation changes in sync with code; new features should update `docs/index.md` and relevant runbooks.
