# Delight Frontend State Management Notes

Context captured from `packages/frontend` on 2025-11-12 (Epic 2 prep).

## Current Approach

- **Auth as State:** Clerk drives the only meaningful state right now. `src/app/layout.tsx` wraps the tree with `ClerkProvider`, and middleware enforces auth for everything except public routes. `SignedIn/SignedOut` components gate header controls.
- **Server Components:** Landing, dashboard, and auth pages are Server Components (`export const dynamic = "force-dynamic"` for `/` and `/dashboard`) to keep Clerk session data fresh under the App Router.
- **No Client Stores Yet:** There is no Redux/Zustand/Context store because the UI is static placeholders. All interactive work is planned for Epic 2 (mission feed, memory cards, chat).

## Data Flow

1. User hits a protected route → `clerkMiddleware` verifies the session.
2. Once inside React, `SignedIn` renders `UserButton` or app chrome, and future components will fetch `/api/v1/users/me` using `fetch` from Server Components or RSC helpers.
3. Any additional data (memories, missions) will come from the FastAPI service; no duplication of backend state exists on the frontend.

## Guardrails for Future Work

- Keep Clerk as the single source of truth for identity; don’t store user records in local storage.
- When adding client interactions (chat, mission forms), prefer React server actions or lightweight hooks scoped to a component. Avoid global stores until we have multiple consumers.
- If we eventually add local caching, document it here (e.g., SWR/React Query configuration, context providers).

## Pending Stories

- Epic 2 Companion UI will introduce conversational state and memory timelines.
- Epic 3 (missions) may require optimistic updates; revisit this doc then with diagrams and store definitions.
