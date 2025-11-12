# Delight Backend API Contracts

Generated from `packages/backend/app/api/v1` during the 2025-11-12 full rescan. All routes below are served from the FastAPI app defined in `packages/backend/main.py` with the base prefix `/api/v1`.

## Summary Table

| Method | Path | Auth | Handler | Notes |
|--------|------|------|---------|-------|
| GET | `/health` | Public | `app/api/v1/health.py:health_check` | Aggregated health probe; hits DB + Redis when ENVIRONMENT != test |
| GET | `/users/me` | Clerk session (Bearer) | `app/api/v1/users.py:get_current_user_profile` | Returns the authenticated user record |
| POST | `/webhooks/clerk` | Svix signature header | `app/api/v1/webhooks.py:clerk_webhook_handler` | Clerk lifecycle webhooks → DB sync |

Base OpenAPI + docs live at `/docs`, `/redoc`, and `/openapi.json`.

## Route Details

### GET `/api/v1/health`
- **Source:** `packages/backend/app/api/v1/health.py`
- **Description:** Computes a `healthy/degraded/unhealthy` status by testing the Postgres connection (async engine) and, once implemented, Redis.
- **Auth:** None. Intended for uptime monitors and load-balancer health checks.
- **Response example:**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "timestamp": "2025-11-12T22:00:00Z"
  }
  ```
- **Story hooks:** Story 1.1 shipped mock responses; Story 1.2 enables real DB tests; Story 2.1 will replace the hard-coded Redis “connected” placeholder with an actual ping.

### GET `/api/v1/users/me`
- **Source:** `packages/backend/app/api/v1/users.py`
- **Description:** Demonstrates how all protected endpoints should pull `Depends(get_current_user)` from `app/core/clerk_auth.py`. Returns the `UserResponse` schema.
- **Auth:** Requires a valid Clerk session cookie or token; FastAPI dependency raises 401/403 when missing.
- **Payload:** None.
- **Response fields:** `id`, `clerk_user_id`, `email`, `display_name`, `timezone`, `created_at`, `updated_at`.
- **Usage:** Enables the Next.js dashboard to display authenticated profile data and is the template for future protected APIs.

### POST `/api/v1/webhooks/clerk`
- **Source:** `packages/backend/app/api/v1/webhooks.py`
- **Description:** Entry point for Clerk user lifecycle webhooks. Validates Svix headers (`svix-id`, `svix-timestamp`, `svix-signature`) using `settings.CLERK_WEBHOOK_SECRET`, then syncs identities via `ClerkService`.
- **Auth:** Svix HMAC signature; requests without headers fail fast with HTTP 400.
- **Body:** Clerk webhook payload (`type`, `data`, `object="event"`). Accepts `user.created`, `user.updated`, and `user.deleted`.
- **Side effects:** Creates or updates `users` + `user_preferences` rows; logs unimplemented deletions for later stories.
- **Failure modes:** Signature mismatch → 400; invalid payload → 400; downstream DB/logic errors → 500.

## Pending & Planned Routes

The architecture (`app/api/v1/__init__.py`) is already partitioned so new routers drop in cleanly. Upcoming Story 2.x items include mission APIs, memory retrieval, and Clerk session management hooks. When those land, extend this document with method summaries, example payloads, and links to their acceptance criteria.
