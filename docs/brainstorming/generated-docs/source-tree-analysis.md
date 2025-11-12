# Delight Source Tree Analysis

Generated during the 2025-11-12 exhaustive scan. Highlights focus on the PNPM monorepo structure and the three primary parts (frontend, backend, shared types).

```
(local) github software/delight/
├── docs/                           # Human + AI-facing documentation hub
│   ├── index.md                    # Navigation index (auto-generated)
│   ├── runbook/                    # Operational checklists (Clerk, Mintlify, personal todos)
│   ├── epic-2/                     # Companion memory system briefs + LangGraph notes
│   └── ...                         # Stories, architecture, security, etc.
├── packages/
│   ├── frontend/                   # Next.js 15 app (Part: web)
│   │   ├── src/app/                # App Router pages + components
│   │   │   ├── layout.tsx          # ClerkProvider + global header
│   │   │   ├── page.tsx            # Public landing page
│   │   │   ├── dashboard/          # Authenticated shell
│   │   │   └── sign-{in,up}/       # Clerk-hosted auth routes
│   │   ├── middleware.ts           # Route protection via Clerk middleware
│   │   ├── next.config.js          # Monorepo-aware Next config (outputFileTracingRoot)
│   │   └── tailwind.config.ts      # Design tokens + content globs
│   ├── backend/                    # FastAPI service (Part: backend)
│   │   ├── app/api/v1/             # Health, users, webhooks routers
│   │   ├── app/core/               # Settings + clerk auth
│   │   ├── app/models/             # SQLAlchemy models (users, memories, etc.)
│   │   ├── app/db/                 # Session + Alembic migrations
│   │   ├── app/services/           # ClerkService and future domain services
│   │   ├── tests/                  # Pytest suites (integration + helpers)
│   │   └── main.py                 # FastAPI app + CORS setup
│   └── shared/                     # TypeScript type library (Part: library)
│       ├── index.ts                # Barrel exports for shared types
│       └── types/                  # Type definitions consumed by frontend/backend
├── bmad/                           # BMAD agent + workflow runtime
│   ├── core/                       # Master agents, config, workflows (document-project, party-mode, etc.)
│   └── bmm/                        # Method workflows (status, document-project, etc.)
├── package.json                    # Workspace root (pnpm)
├── pnpm-workspace.yaml             # Declares packages/frontend|backend|shared
├── docker-compose.yml              # Future infra scaffolding (db/redis stubs)
└── Makefile                        # Placeholder for automation hooks
```

## Integration Touchpoints

- `packages/frontend` ➜ `packages/backend`: Calls REST APIs at `/api/v1/*` once authenticated.
- `packages/backend` ➜ Clerk/Svix: Handles user lifecycle webhooks and session validation.
- `packages/frontend` & `packages/backend` ➜ `packages/shared`: Consume shared TypeScript types through workspace imports.

## Critical Directories Summary

| Directory | Reason |
|-----------|--------|
| `packages/frontend/src/app` | App Router entry points, future companion UI. |
| `packages/backend/app/api/v1` | All public API contracts documented in `api-contracts-backend.md`. |
| `packages/backend/app/models` | Persistence layer for users/memories. |
| `packages/backend/app/db/migrations` | Schema evolution (users + memory tiers). |
| `docs/epic-2` | Planning artifacts for the memory/companion epic referenced by the user. |
| `docs/runbook` | Operational side quests runbooks added during this workflow. |
