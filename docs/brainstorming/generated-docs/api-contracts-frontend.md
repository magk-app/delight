# Delight Frontend API Surface

Inspection date: 2025-11-12. The Next.js 15 app (`packages/frontend`) currently does not expose custom REST endpoints; all data access flows through the backend FastAPI service and Clerk’s hosted widgets.

## Runtime Contracts

| Consumer | Contract | Source |
|----------|----------|--------|
| Next.js middleware → Clerk | `clerkMiddleware` protects every route except `/`, `/sign-in`, `/sign-up`, and `/api/v1/webhooks/*`. Auth is enforced before hitting server components. | `src/middleware.ts` |
| Frontend → Backend | Uses relative fetches (`/api/v1/...`) once authenticated. Today only `/api/v1/users/me` is invoked from components, but the pattern is documented for future missions. | see `README.md` |
| Clerk widgets | `SignIn`, `SignUp`, `UserButton` components provide hosted UI and call Clerk APIs directly. | `src/app/layout.tsx`, `sign-in/`, `sign-up/` |

## Why no Next API routes yet?

- Core domain logic (memory service, missions, webhooks) lives in FastAPI for parity with LangGraph agents.
- The Next app is mostly marketing + auth shell, so server actions and API routes would be redundant until we add SSR helpers or streaming endpoints.
- `app/api` folder is intentionally empty—future stories can scaffold proxies or SSG helpers when needed.

## Integration Checklist for New Routes

When you do add an API route under `src/app/api/...`, mirror the backend doc structure:
1. Describe the handler signature (method, path, zod schema if used).
2. Note whether Clerk middleware already enforced auth or if you need server-side verification.
3. Link to the upstream FastAPI endpoint when it’s just a proxy to avoid drift.

Until then, refer to `api-contracts-backend.md` for the authoritative REST contract.
