# Delight Frontend Deployment Guide

Snapshot from the 2025-11-12 rescan for the Next.js workspace (`packages/frontend`).

## Local Development

```bash
cd packages/frontend
pnpm install
pnpm dev        # http://localhost:3000
pnpm build && pnpm start   # Production preview
```

- Uses Next.js 15 App Router with React 19.
- Tailwind + PostCSS already configured (`tailwind.config.ts`, `postcss.config.js`).
- Playwright tests run via `pnpm test:e2e`.

## Environment Variables

Set these in `.env.local` for dev and via Vercel dashboard for hosted environments:

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Required for Clerk widgets and middleware |
| `CLERK_SECRET_KEY` | **Not used on the frontend** (backend-only). Do not leak secrets here. |
| `NEXT_PUBLIC_API_URL` | Base URL for FastAPI (e.g., `https://api.delight.com` in production) |

Refer to `docs/runbook/TODO-CLERK-PRODUCTION-SETUP.md` before flipping to live keys.

## Middleware & Routing

- `src/middleware.ts` runs on every request except static assets; it calls `clerkMiddleware` to gate routes.
- Public routes: `/`, `/sign-in`, `/sign-up`, `/api/v1/webhooks/*`.
- Everything else requires an authenticated session and will redirect through Clerk.

## Build Configuration

- `next.config.js` sets `reactStrictMode` and overrides `outputFileTracingRoot` to the monorepo root so Vercel (or any builder) tracks dependencies correctly.
- Experimental flag `serverActions.allowedOrigins = ["localhost:3000"]` is enabled for future server actions.
- `tailwind.config.ts` enumerates the App Router directories so tree-shaking works in production builds.

## Hosting Notes

- **Vercel:** Default target. Add the environment variables above and enable `Speed Insights` only if you plan to capture metrics (see personal runbook for the decision log).
- **Custom Deployments:** If you host elsewhere, ensure the adapter supports Next.js middleware (e.g., `@clerk/nextjs/server`) and streaming. Keep `outputFileTracingRoot` aligned with the repo root to avoid missing shared assets.
- **Static Assets:** Everything lives under `public/` (currently minimal). App Router handles metadata and head tags automatically.

## Future Work

- When mission/companion features arrive, document any required feature flags or server actions here.
- If you introduce Next API routes, cross-link them with `api-contracts-frontend.md`.
