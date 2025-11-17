# Delight Integration Architecture

Documenting cross-part communication paths identified on 2025-11-12.

## Parts & Responsibilities

| Part | Location | Role |
|------|----------|------|
| Frontend (web) | `packages/frontend` | Next.js 15 UI, Clerk-hosted auth, mission/companion dashboard |
| Backend (api) | `packages/backend` | FastAPI service, persistence, Clerk webhooks |
| Shared types | `packages/shared` | TypeScript type definitions consumed by both |

## Data & Control Flows

1. **User Authentication**
   - Frontend renders Clerk components (`SignIn`, `SignUp`, `UserButton`).
   - `clerkMiddleware` protects every route except `/`, `/sign-in`, `/sign-up`, `/api/v1/webhooks/*`.
   - Authenticated requests carry Clerk session tokens; backend verifies them via `get_current_user`.

2. **Frontend → Backend REST Calls**
   - Base URL: `/api/v1/*` (See `api-contracts-backend.md`).
   - Current usage: `GET /api/v1/users/me` for profile data, `/api/v1/health` for monitoring.
   - Future usage: mission retrieval, memory APIs, LangGraph actions.

3. **Clerk → Backend Webhooks**
   - Endpoint: `POST /api/v1/webhooks/clerk`.
   - Verifies Svix headers, calls `ClerkService.create_or_update_user`, persists to Postgres.
   - Planned: handle `user.deleted` + session revocation events.

4. **Shared Types**
   - `packages/shared/index.ts` exports types for API contracts and will house mission/memory DTOs.
   - Frontend imports via pnpm workspace alias; backend can transpile types for validation or docs generation.

5. **External Services**
   - **Postgres + pgvector:** Backend persistence + memory embeddings.
   - **Redis (planned):** ARQ workers and mission queues (Story 2.x).
   - **OpenAI / LangChain / LangGraph:** Referenced in dependencies but not wired yet; expect backend-only usage for AI orchestration.

## Authentication & Authorization

- Clerk is the identity provider for both UI and API.
- Backend trusts Clerk session tokens via `CLERK_SECRET_KEY` and validates webhook signatures via `CLERK_WEBHOOK_SECRET`.
- No role-based authorization yet; treat future admin endpoints accordingly.

## Integration Risks / TODOs

- Add explicit frontend fetch clients once backend exposes mission/memory routes so we avoid ad-hoc fetch calls.
- Implement Redis connectivity + ARQ workers before enabling long-running mission orchestration.
- Document shared DTOs in `packages/shared` as soon as Companion Chat (Epic 2.5) lands to keep FE/BE aligned.
