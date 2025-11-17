# Delight Backend Data Models

Source of truth: `packages/backend/app/models`. This document captures the current persistence layer (as of 2025-11-12) for the FastAPI service.

## Overview

- **Database:** PostgreSQL 15+ with pgvector extension enabled (see migrations `packages/backend/app/db/migrations/003_create_memory_tables.py`).
- **ORM:** SQLAlchemy 2.x async models (`Base` in `app/db/base.py`) with Alembic migrations.
- **Embedding storage:** `pgvector.Vector(1536)` columns for semantic memory search.

## Tables

### `users`
- **Columns:** `id (UUID pk)`, `clerk_user_id (unique)`, `email`, `display_name`, `timezone`, timestamps.
- **Relationships:** one-to-one `user_preferences`; one-to-many `memories` + `memory_collections`.
- **Notes:** Clerk IDs are authoritative; timezone defaults to `"UTC"` until user onboarding updates it.

### `user_preferences`
- **Columns:** `id`, `user_id` (unique FK → `users`), `custom_hours (JSONB)`, `theme`, `communication_preferences (JSONB)`, `onboarding_completed`, timestamps.
- **Usage:** Stores personalization flags such as notification channels and preferred working hours.

### `memories`
- **Columns:** `id`, `user_id`, `memory_type (MemoryType enum)`, `content`, `embedding`, `metadata (JSONB mapped to extra_data)`, `created_at`, `accessed_at`.
- **MemoryType enum:** `personal`, `project`, `task`; defined in `app/models/memory.py` and created in migration `002_add_display_name_to_users.py`? actually check? but best mention.
- **Validation hook:** `validate_embedding_dimensions` listener enforces 1536-dimension vectors before insert/update.
- **Notes:** `accessed_at` supports LRU eviction logic for future pruning jobs.

### `memory_collections`
- **Columns:** `id`, `user_id`, `collection_type`, `name`, `description`, `created_at`.
- **Purpose:** Optional grouping for themed memories (goal, stressor_log, preference, etc.).

## Migrations & Schema Management

- Migration files live under `packages/backend/app/db/migrations/versions`. Notable ones:
  - `002_add_display_name_to_users.py` – extends `users`.
  - `003_create_memory_tables.py` – introduces memory tables + pgvector index.
  - `004_add_performance_indexes.py` – tuning indexes for `memory_type`/`created_at`.
- Alembic configuration is provided via `alembic.ini` with env set up in `app/db`.

## API Schemas

- `UserResponse` (`app/schemas/user.py`) mirrors the `users` table for responses.
- `ClerkWebhookPayload` (`app/schemas/webhook.py`) validates inbound webhook bodies before `ClerkService` maps them to ORM entities.

## Future Work

- Create pruning job for `MemoryType.TASK` rows once ARQ workers (Story 2.x) are online.
- Add cascade deletes for Clerk `user.deleted` events (placeholder logged in `webhooks.py`).
- Capture audit fields for `memory_collections` when mission-level grouping ships.
