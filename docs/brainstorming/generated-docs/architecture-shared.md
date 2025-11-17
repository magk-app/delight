# Shared Types Architecture (@delight/shared)

Captured 2025-11-12 from `packages/shared`.

## Executive Summary

`@delight/shared` is a private pnpm workspace package that exports TypeScript types consumed by both the Next.js frontend and any Node/TypeScript tooling on the backend. It keeps API payloads and DTOs consistent across parts of the monorepo.

## Technology Stack

- **Language:** TypeScript 5.3
- **Build:** None (type-only package). `tsconfig.json` enforces strict compilation, and `package.json` exposes `index.ts` as both `main` and `types`.
- **Scripts:** `pnpm --filter @delight/shared type-check`.

## Architecture Pattern

Simple barrel export:
- `types/` – Place individual `.ts` files for DTOs (mission payloads, memory summaries, etc.).
- `index.ts` – Re-exports everything for import as `@delight/shared`.

## Data & API Alignment

- Future memory/mission DTOs should live here to stay in sync between React components and FastAPI clients.
- When generating OpenAPI/TypeScript clients, extend this package instead of duplicating interfaces.

## Development Workflow

1. Add new type definitions under `types/`.
2. Update `index.ts` to re-export modules.
3. Run `pnpm --filter @delight/shared type-check`.
4. Consumers (frontend, tooling) import via workspace alias.

## Testing Strategy

Type-level only. Integrate with `tsc --noEmit` or add unit tests once the package hosts runtime helpers.
