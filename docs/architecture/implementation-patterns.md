# Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Conventions

**Backend (Python):**

- **Modules:** `snake_case` (e.g., `companion_service.py`, `mission_service.py`)
- **Classes:** `PascalCase` (e.g., `CompanionService`, `MissionModel`)
- **Functions:** `snake_case` (e.g., `generate_quest`, `calculate_dci`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_MISSION_DURATION`)

**Frontend (TypeScript):**

- **Components:** `PascalCase` (e.g., `MissionCard.tsx`, `ElizaChat.tsx`)
- **Files:** Match component name (e.g., `MissionCard.tsx`)
- **Hooks:** `camelCase` with `use` prefix (e.g., `useMission`, `useCompanion`)
- **Utils:** `camelCase` (e.g., `formatEssence`, `calculateStreak`)

**API Endpoints:**

- **REST:** `/api/v1/{resource}/{id?}` (e.g., `/api/v1/missions`, `/api/v1/missions/123`)
- **SSE:** `/api/v1/sse/{stream_type}` (e.g., `/api/v1/sse/companion/stream`)
- **Actions:** `POST /api/v1/{resource}/{action}` (e.g., `POST /api/v1/missions/start`)

**Database:**

- **Tables:** `snake_case`, plural (e.g., `missions`, `character_relationships`)
- **Columns:** `snake_case` (e.g., `user_id`, `created_at`)
- **Foreign Keys:** `{table}_id` (e.g., `mission_id`, `character_id`)
- **JSON columns:** Use `JSON` type (not `JSONB`) for flexible data structures

### Code Organization

**Backend Structure:**

```
app/
├── api/v1/          # API endpoints (thin controllers)
├── services/        # Business logic
├── agents/          # LangGraph agents
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
└── workers/         # ARQ background jobs
```

**Frontend Structure:**

```
src/
├── app/             # Next.js App Router pages
├── components/      # React components (organized by feature)
├── lib/             # Utilities, hooks, API client
└── types/           # TypeScript type definitions
```

**Testing:**

- **Backend:** `tests/` directory mirroring `app/` structure
- **Frontend:** `__tests__/` co-located with components, `e2e/` for Playwright

### Error Handling

**Backend:**

- Use FastAPI's `HTTPException` for API errors
- Custom exceptions: `DelightException` base class
- Error responses: `{"error": {"type": "...", "message": "...", "code": "..."}}`
- Log errors with context (user_id, request_id) using structured logging

**Frontend:**

- API errors: Display user-friendly messages via toast notifications (shadcn/ui)
- Network errors: Retry with exponential backoff
- Validation errors: Inline form errors

### Logging Strategy

**Backend:**

- **Library:** `structlog` for structured logging
- **Format:** JSON in production, human-readable in dev
- **Levels:** DEBUG (dev), INFO (production), ERROR (always)
- **Context:** Include `user_id`, `request_id`, `agent_name` in logs

**Frontend:**

- **Console:** Development only
- **Production:** Sentry for error tracking, performance monitoring, and user session replay

### Background Job Reliability

**Retry Strategy:**

- Quest generation: 3 retries with exponential backoff (2s, 4s, 8s)
- Nudge scheduling: 2 retries with 5s delay
- Character initiation: 3 retries with exponential backoff
- Memory consolidation: 5 retries (can run delayed without user impact)

**Dead Letter Queue:**

- Failed jobs after max retries go to Redis dead letter queue
- Admin dashboard shows failed jobs with retry button
- Critical failures (quest generation) trigger Sentry alert

**Job Monitoring:**

- Track job completion rate, average duration per job type
- Alert on queue depth > 1000 or job age > 5 minutes
- Dashboard for job status by type

---
