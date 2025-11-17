# Delight Deployment Overview

High-level runbook tying together frontend + backend deployment considerations (2025-11-12 rescan).

## Backend (FastAPI)

- **Containerization:** `packages/backend/Dockerfile` builds a Poetry-based image and launches `uvicorn main:app --host 0.0.0.0 --port 8000`.
- **Environment:** Requires `DATABASE_URL`, `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET`, optional `REDIS_URL`, `OPENAI_API_KEY`, `SENTRY_DSN`. See `config-backend.md` for details.
- **Migrations:** Run `poetry run alembic upgrade head` before deploying the API. Pgvector must be enabled on the target Postgres instance.
- **Health checks:** Point readiness/liveness probes to `/api/v1/health`.
- **Webhooks:** Register `POST /api/v1/webhooks/clerk` with Clerk; keep Svix signing secret synced per environment.
- **Scaling:** Stateless; can run multiple replicas behind a load balancer as long as all instances share the same Postgres + Redis.

## Frontend (Next.js)

- **Target:** Vercel or any platform that supports Next.js 15 App Router + middleware.
- **Build:** `pnpm --filter frontend build`.
- **Runtime settings:** Provide `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `NEXT_PUBLIC_API_URL`. See `deployment-frontend.md` for more context.
- **Auth middleware:** Ensure the host supports Edge/Node middleware; otherwise convert `clerkMiddleware` to a server-side guard.

## Shared Infrastructure

- **Docker Compose (local):** `docker-compose.yml` spins up Postgres 16 + Redis 7 for developers. Not intended for production.
- **CI/CD:** GitHub workflows are currently focused on Claude code review automation. When adding build/test pipelines, drop definitions in `.github/workflows/` and document them here.
- **Monitoring:** Sentry DSN env variable is ready but optional; tie it into both frontend + backend once you need error traces.

## Deployment Checklist

1. Align secrets/env vars with the target environment (Backend `.env`, Vercel dashboard, secret manager, etc.).
2. Run tests (`pnpm test`, `poetry run pytest`) locally or in CI before promoting changes.
3. Apply Alembic migrations against the production Postgres database.
4. Verify Clerk production promotion steps (`docs/runbook/TODO-CLERK-PRODUCTION-SETUP.md`).
5. Smoke test:
   - Frontend landing page + Clerk sign-in.
   - `GET /api/v1/health` (should include real DB status).
   - `GET /api/v1/users/me` with a live session.
   - `POST /api/v1/webhooks/clerk` using Clerk’s “Send test event.”
