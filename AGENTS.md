# Repository Guidelines

## Project Structure & Module Organization
Delight is a monorepo anchored in `packages/`, with workspaces for `backend` (FastAPI services), `frontend` (Next.js UI), `ai-agent` (LLM orchestration), `game-engine` (XP/quest logic), and `shared` (cross-cutting types). Architecture notes belong in `ARCHITECTURE.md` and `docs/`, while agent prompt assets stay in `bmad/`. Store migrations, fixtures, and storyboards beside the owning feature so reviewers can trace context quickly.

## Build, Test, and Development Commands
- `cd packages/backend && poetry install` — resolve Python dependencies.
- `poetry run uvicorn main:app --reload` — run the FastAPI gateway with auto-reload.
- `cd packages/frontend && pnpm install` — install the Next.js toolchain (Node 18+, pnpm).
- `pnpm dev` — serve the web client at `http://localhost:3000`.
Run backend and frontend in parallel; copy `.env.example` files before starting either service so configuration mismatches surface early.

## Coding Style & Naming Conventions
Backend code follows PEP 8, 4-space indentation, snake_case modules (`quest_service.py`), and type-annotated public APIs. Frontend files use ESLint + Prettier defaults, PascalCase components (`ProgressCard.tsx`), camelCase hooks/utilities, and Tailwind classes defined inline. Shared modules should re-export through `index.ts` barrels to discourage deep relative imports. Keep comments purposeful—explain why orchestration decisions exist rather than what the code already states.

## Testing Guidelines
Place backend tests in `packages/backend/tests/` and execute with `poetry run pytest` as suites land. Frontend unit tests live in `packages/frontend/__tests__/` (Vitest), and end-to-end specs under `packages/frontend/e2e/` (Playwright) executed via `pnpm test` and `pnpm test:e2e`. Mirror narrative scenarios from `docs/` when writing fixtures so AI and quest mechanics stay verifiable. Every feature should merge with at least a smoke test covering the primary user path.

## Commit & Pull Request Guidelines
History uses short, imperative commits (`package json setup`, `basic partitioning of docs`), so keep subjects under ~60 characters and scoped to the package touched. Pull requests must ship with a concise summary, linked issue or roadmap item, local test evidence (command + result), and screenshots/GIFs for UI changes. Request review from the owning domain lead before merging to `main`; drafts are encouraged until tests pass.

## Configuration & Security Tips
Do not commit `.env` files; copy from the provided examples and document new keys in `README.md`. Secrets consumed by agents in `bmad/` belong in your secret manager, not the manifests. Scrub user-identifiable data from logs or demos and store sanitized story content in `docs/stories/`.
