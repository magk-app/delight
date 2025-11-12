# Delight Project Overview

Generated 2025-11-12 for rapid onboarding and AI-assisted reference.

## Executive Summary

Delight is an AI-powered self-improvement companion that blends narrative coaching, mission planning, and persistent memory. The current codebase delivers the foundational auth flows (Clerk), backend scaffolding (FastAPI + pgvector), and Epic 2 planning docs for the companion memory system.

## Tech Stack Snapshot

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15 (App Router), React 19, Tailwind CSS, Clerk |
| Backend | FastAPI, SQLAlchemy 2 (async), Postgres + pgvector, Redis (planned), LangChain/LangGraph |
| Shared | TypeScript type library (`@delight/shared`) |
| Tooling | pnpm workspaces, Poetry, Playwright, Pytest, BMAD workflows |

## Repository Structure

- `packages/frontend` – Next.js UI, Clerk auth pages, dashboard shell.
- `packages/backend` – FastAPI service, REST APIs, data models, migrations, tests.
- `packages/shared` – Type-only workspace for shared DTOs.
- `docs/` – Extensive documentation (epics, stories, runbooks, architecture, security).
- `bmad/` – BMAD agents + workflows powering the documentation automation.

## Key Documents

- [Architecture – Frontend](architecture-frontend.md)
- [Architecture – Backend](architecture-backend.md)
- [Architecture – Shared Types](architecture-shared.md)
- [API Contracts – Backend](api-contracts-backend.md)
- [Data Models – Backend](data-models-backend.md)
- [UI Component Inventory](component-inventory.md)
- [Development Guide](development-guide.md)
- [Deployment Overview](deployment-overview.md)
- [Integration Architecture](integration-architecture.md)

## Getting Started

1. Follow `development-guide.md` to install dependencies, configure `.env` files, and start the dev servers.
2. Review `api-contracts-backend.md` + `ui-components-frontend.md` to understand existing surface area.
3. Dive into Epic 2 docs (`docs/epic-2/`) for the companion memory roadmap.

## Next Milestones

- Implement mission/memory APIs in FastAPI.
- Render companion chat + memory timelines in the dashboard.
- Wire LangGraph-based story flow as described in Epic 2 planning.
