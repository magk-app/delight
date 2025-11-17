# Delight Backend Configuration & Operations

This runbook captures the environment variables, secrets, and runtime assumptions for `packages/backend` as inspected on 2025-11-12.

## Environment Variables

Source files:
- Pydantic settings (`packages/backend/app/core/config.py`)
- Template (`packages/backend/.env.example`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | Postgres connection string; converted to `postgresql+asyncpg://` automatically |
| `CLERK_SECRET_KEY` | ✅ | Backend-only key for session verification |
| `CLERK_WEBHOOK_SECRET` | ✅ | Svix signing secret for `/api/v1/webhooks/clerk` |
| `ENVIRONMENT` | Optional (`development` default) |
| `INFRA_MODE` | Optional (`cloud-dev` vs `local` guidance in `.env.example`) |
| `REDIS_URL` | Optional today (Redis ping TODO for Story 2.1) |
| `OPENAI_API_KEY` | Future epics (LangChain/LangGraph pipelines) |
| `SENTRY_DSN` | Optional observability |
| `CORS_ORIGINS` | Defaults to localhost + 127.0.0.1 |

### Secrets Handling
- Never commit `.env`; only `.env.example` is tracked.
- Clerk publishable keys (`NEXT_PUBLIC_*`) belong in the frontend, not here.
- Webhook secret comes from Clerk → Webhooks → Signing Secret panel.

## Local Development

```bash
cd packages/backend
poetry install
poetry run uvicorn main:app --reload
```

Supporting commands:
- `poetry run pytest` – backend unit/integration tests.
- `poetry run alembic upgrade head` – apply migrations once `DATABASE_URL` points at a live database.

## Deployment Notes

- **Docker:** `packages/backend/Dockerfile` builds a slim python:3.11 image, installs Poetry dependencies, then runs `uvicorn main:app --host 0.0.0.0 --port 8000`.
- **CORS:** Configured via FastAPI middleware (`main.py`). Update `CORS_ORIGINS` or extend the middleware if you add more frontend domains.
- **Health Probes:** `/api/v1/health` is safe to expose for readiness/liveness checks. When `ENVIRONMENT=test`, it returns mocked results.
- **Webhooks:** Ensure `CLERK_WEBHOOK_SECRET` matches the environment-specific endpoint. The handler currently logs `user.deleted` as “not yet implemented,” so consider a feature flag before wiring production deletes.
- **Async DB Driver:** All connections should use asyncpg; the helper `Settings.async_database_url` rewrites `postgresql://` automatically.

## Future Enhancements

- Add Redis connectivity checks (Story 2.1) and update this doc with failover expectations.
- Document ARQ worker deployment once background jobs (memory pruning, mission orchestration) ship.
- Record production runbooks (Mintlify or Ops doc) after the Clerk promotion checklist in `docs/runbook/TODO-CLERK-PRODUCTION-SETUP.md` is completed.
