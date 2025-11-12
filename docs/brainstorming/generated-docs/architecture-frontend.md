# Frontend Architecture (Next.js)

Generated 2025-11-12 from `packages/frontend`.

## Executive Summary

The frontend is a Next.js 15 App Router application that hosts Delight’s marketing page, Clerk-authenticated dashboard shell, and future Companion UI. It relies on Clerk for identity, Tailwind for styling, and will call the FastAPI backend for mission and memory data.

## Technology Stack

- **Language:** TypeScript (ES2022 target)
- **Framework:** Next.js 15 (App Router) + React 19
- **Styling:** Tailwind CSS with custom tokens + `class-variance-authority`
- **Auth:** Clerk (`@clerk/nextjs`)
- **Testing:** Playwright E2E suite under `packages/frontend/tests`

## Architecture Pattern

Isomorphic React app using Server Components for shell pages and Clerk middleware for route protection. App Router organizes UI by route folders (`src/app/…`), while middleware intercepts requests for auth enforcement.

## Data Architecture

No local persistence yet. All state is ephemeral and driven by Clerk sessions or future fetches to `/api/v1` endpoints. Component props will eventually map to shared DTOs from `@delight/shared`.

## API Design

No Next API routes (`src/app/api`) exist yet. All network calls will hit the backend via `NEXT_PUBLIC_API_URL`. See `api-contracts-frontend.md` for current contracts and the middleware allowlist.

## Component Overview

- **Root Layout (`src/app/layout.tsx`)** – Wraps everything in `ClerkProvider`, renders header with `SignedIn/SignedOut` toggles.
- **Landing Page (`src/app/page.tsx`)** – Marketing hero + feature cards.
- **Dashboard (`src/app/dashboard/page.tsx`)** – Authenticated shell with placeholder cards for progress, missions, companion.
- **Auth Pages (`src/app/sign-{in,up}/[[...]]/page.tsx`)** – Hosted Clerk components.
- **Middleware (`src/middleware.ts`)** – Public route matcher and `clerkMiddleware` invocation.
See `ui-components-frontend.md` for the inventory.

## Source Tree

- `src/app/` – All pages + layout.
- `src/middleware.ts` – Request-level auth.
- `globals.css`, `tailwind.config.ts` – Styling foundation.
- `tests/` – Playwright specs (auth smoke tests, example scenarios).
- Additional shared components will live in `src/components/` when introduced.

## Development Workflow

Summarized in `development-guide.md`:
1. `pnpm install`
2. Create `.env.local` with `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` + `NEXT_PUBLIC_API_URL`
3. `pnpm dev`
4. Run Playwright via `pnpm test:e2e`

## Deployment Architecture

- Hosted on Vercel or any platform that supports middleware.
- Build command: `pnpm --filter frontend build`
- Runtime env: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `NEXT_PUBLIC_API_URL`
- Refer to `deployment-frontend.md` + `deployment-overview.md` for details.

## Testing Strategy

- **Playwright (`packages/frontend/tests`)** – Auth smoke tests, example flows.
- **Unit tests** – Run via `pnpm test` (once suites are added).
- **Manual checks** – Ensure Clerk modals and middleware paths behave before releasing.
