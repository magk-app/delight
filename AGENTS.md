# Repository Guidelines

## Project Structure & Module Organization
Delight is a monorepo rooted in `packages/`, with workspace folders for `backend` (FastAPI services), `frontend` (Next.js UI), `ai-agent`, `game-engine`, and `shared` types. Docs, briefs, and workflow outputs live under `docs/`, while BMAD workflow assets reside in `bmad/`. Keep migrations, fixtures, and storyboards beside the feature that owns them so reviewers can trace context, and re-export shared modules through `packages/shared/index.ts` barrels to avoid deep relative paths.

## Build, Test, and Development Commands
- `cd packages/backend && poetry install` — resolve Python deps; follow with `poetry run uvicorn main:app --reload` for the FastAPI gateway.
- `cd packages/frontend && pnpm install` — install the Next.js toolchain; use `pnpm dev` to run the UI at http://localhost:3000.
- Backend tests: `cd packages/backend && poetry run pytest`.
- Frontend unit tests: `cd packages/frontend && pnpm test`; Playwright E2E: `pnpm test:e2e`.
Copy `.env.example` files before starting services so configuration mismatches surface early.

## Coding Style & Naming Conventions
Backend code follows PEP 8 with 4-space indentation, snake_case modules (`quest_service.py`), and type annotations on public APIs. Frontend adopts ESLint + Prettier defaults, PascalCase components (`ProgressCard.tsx`), camelCase hooks/utils, and Tailwind classes inline. Keep comments purposeful—explain why orchestration choices exist instead of restating logic.

## Testing Guidelines
Mirror backend tests in `packages/backend/tests/` and frontend unit specs in `packages/frontend/__tests__/`; e2e specs sit in `packages/frontend/e2e/`. Align fixtures with narrative scenarios recorded in `docs/` so AI and quest mechanics remain verifiable. Every feature should land with at least a smoke test covering the primary user path plus the supporting command output in the PR description.

## Commit & Pull Request Guidelines
Use short, imperative commit subjects under ~60 characters (`package json setup`, `basic partitioning of docs`). Pull requests need a concise summary, linked issue or roadmap reference, and local test evidence (command + result). Include screenshots or GIFs for UI changes and request review from the owning domain lead before merging to `main`; keep drafts open until tests pass.

## Security & Configuration Tips
Never commit `.env` files; copy from the provided examples and document new keys in `README.md`. Secrets for agents in `bmad/` belong in your secret manager, not in manifests. Scrub user-identifiable data from logs or demos, and store sanitized story content under `docs/stories/`.
