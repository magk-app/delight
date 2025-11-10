# Story 1.3: Integrate Clerk Authentication System

Status: ready-for-dev

## Story

As a **new Delight user**,
I want **to authenticate with email/password, Google, GitHub, or magic links through a trustworthy flow that feels native to Delight’s narrative world**, 
so that **my sensitive data stays secure while I move from first touch into the companion experience without friction**.

### Narrative & Experience Goals
- **First impression matters:** Authentication is the very first in-product ritual, so it must mirror the emotionally supportive tone described in the product brief while keeping the “modern warmth” visual language defined by UX. [Source: docs/product-brief-Delight-2025-11-09.md#Executive-Summary, docs/ux-design-specification.md#Visual-Design-System]
- **Seamless bridge into the world:** Completing sign-in should feel like crossing into the story zones (Arena, Observatory, Commons) rather than hitting a generic SaaS screen, so Clerk theming must pick up the active scenario palette and typography. [Source: docs/ux-design-specification.md#Flow-1-Enhanced-Onboarding---Deep-Narrative-Hook]
- **Trust before delight:** Delight promises to be ruthlessly effective *and* compassionate; delivering secure auth with social options is the first proof that the platform respects users’ time, privacy, and effort. [Source: docs/product-brief-Delight-2025-11-09.md#Core-Vision]

### Requirements Context Summary
- Epic 1 explicitly calls for a Clerk-powered authentication layer with email/password, Google, GitHub, and magic link support, plus automatic user creation in our database and theme alignment. [Source: docs/epics/epic-1-user-onboarding-foundation.md#Story-1.3-Integrate-Clerk-Authentication-System]
- The technical specification mandates `<ClerkProvider>` wrapping the Next.js App Router, route protection via `middleware.ts`, a signed `POST /api/v1/webhooks/clerk` endpoint, and a FastAPI dependency that validates every protected request. [Source: docs/tech-spec-epic-1.md#APIs-and-Interfaces]
- Architecture and project-structure guidelines determine exactly where frontend auth routes, backend dependencies, and shared types should live so future stories can build on the same scaffolding. [Source: docs/architecture/project-structure.md]
- UX flows show authentication feeding directly into expanded onboarding narratives, so Story 1.3 must include hooks for scenario selection without blocking auth MVP scope. [Source: docs/ux-design-specification.md#Flow-1-Enhanced-Onboarding---Deep-Narrative-Hook]

### Scope & Constraints
**In scope**
1. Clerk-hosted sign-in/sign-up routes under `packages/frontend/src/app/(auth)/`, styled via theme tokens matching the active scenario.
2. App Router middleware that enforces authentication on `/companion`, `/missions`, `/world`, `/progress`, `/api` routes while allowing `/story`, `/docs`, `/health`, and static assets.
3. Backend session verification via `clerk-backend-sdk`, plus webhook ingestion that upserts `users`/`user_preferences` rows and syncs deletions.
4. Local/CI configuration updates documenting `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET`, and URLs for webhook signature validation.
5. Manual + automated tests covering each auth surface, webhook sync, API protection, and logout.

**Out of scope** (captured for later stories)
- The multi-step onboarding ritual (Story 1.4) and narrative cutscenes. Provide stub navigation for now.
- Deep RBAC/multi-tenant support; everyone is a basic user for Epic 1.
- Advanced session analytics; log basic events for observability but defer dashboards.

## Acceptance Criteria

### AC1 – Multi-channel Authentication Surfaces
**Given** a user opens `/sign-in` or `/sign-up`, **when** the Clerk component renders, **then** it must expose email/password, Google OAuth, GitHub OAuth, and magic link options, all fully functional. [Source: docs/epics/epic-1-user-onboarding-foundation.md#Story-1.3-Integrate-Clerk-Authentication-System]

### AC2 – Delight-Themed Experience & Narrative Bridge
Clerk UI must inherit Delight’s active scenario palette, typography, and copy so users immediately feel they are in the companion world; theme tokens derive from the UX specification’s “Modern Warmth” plus scenario overlays, and success states funnel users toward the Arena/Observatory entry points. [Source: docs/ux-design-specification.md#Visual-Design-System]

### AC3 – Secure Backend Session Verification
All protected FastAPI routes must depend on a shared `get_current_user` that verifies Clerk session tokens via `clerk-backend-sdk`, fetches the matching `User` record (creating it if missing), and returns HTTP 401 for expired/invalid sessions, with pytest coverage for positive and negative cases. [Source: docs/tech-spec-epic-1.md#APIs-and-Interfaces]

### AC4 – Webhook-driven User Sync & Idempotency
`POST /api/v1/webhooks/clerk` must validate Clerk signatures, handle `user.created`, `user.updated`, and `user.deleted`, upsert `users` + `user_preferences` records transactionally, and log outcomes using structured logging so we can audit identity events. [Source: docs/tech-spec-epic-1.md#APIs-and-Interfaces]

### AC5 – Session Lifecycle & Logout Hygiene
Logging out from the frontend (or via Clerk dashboard) must invalidate the session across all devices; authenticated pages should redirect signed-out visitors to `/sign-in`, while signed-in users are redirected away from auth routes. [Source: docs/epics/epic-1-user-onboarding-foundation.md#Story-1.3-Integrate-Clerk-Authentication-System]

### AC6 – Database Consistency Across Events
Every authentication event must ensure `users.clerk_user_id` remains unique, default timezone + notification preferences are initialized, and deletions cascade to `user_preferences`, matching Story 1.2’s schema. [Source: docs/tech-spec-epic-1.md#Data-Models-and-Contracts, docs/stories/1-2-set-up-database-schema-and-migrations.md#Acceptance-Criteria]

### AC7 – Telemetry, Logging, and Alertability
Auth flows must emit structured logs (Clerk event type, user id, result) and basic metrics so `/api/v1/health` and Sentry can surface auth outages; failures should never leak secrets. [Source: docs/architecture.md#Logging-Strategy]

### AC8 – Documentation & Evidence
`.env.example` files, README, and docs must list all Clerk variables and setup steps; the story deliverable must include manual/automated test evidence covering each auth surface plus webhook sync. [Source: docs/tech-spec-epic-1.md#Manual-Testing-Checklist-(Story-1.3)]

## Derived Success Metrics
- ≥90% of pilot users reach authenticated state on first attempt (tracked via Clerk analytics + internal logs).
- ≥80% of auth requests render Delight-themed UI variants (no fallback to default Clerk theme).
- Zero unauthenticated requests reach mission/progress APIs in manual penetration tests.

## Feature Breakdown & User Flows

### Flow 1 – First-time Sign-up (Email/Magic Link)
1. User lands on `/sign-up` from marketing site or deep link. Clerk renders Delight-themed component seeded with scenario copy (“Enter the Arena”). [Source: docs/ux-design-specification.md#Flow-1-Enhanced-Onboarding---Deep-Narrative-Hook]
2. User selects email/password **or** “Send me a magic link”. Clerk handles verification, while analytics log `auth.method=email` or `magic_link`. [Source: docs/tech-spec-epic-1.md#APIs-and-Interfaces]
3. On success, Clerk fires `user.created`, triggering our webhook to create `User` + `UserPreferences` with default timezone `UTC`, theme `modern`, and notifications on. [Source: docs/epics/epic-1-user-onboarding-foundation.md#Technical-Notes]
4. Frontend receives session token, stores Clerk session, and redirects to `/choose-scenario` (stub) or `/companion` if scenario already selected. Transition uses same ambient cues as described in UX spec (foggy SF morning, guild hall, etc.). [Source: docs/ux-design-specification.md#Flow-1-Enhanced-Onboarding---Deep-Narrative-Hook]
5. Mission surfaces remain locked until webhook confirms database row creation; fallback UI shows “Preparing your guild ledger…” state to avoid race conditions.

### Flow 2 – Social Login (Google/GitHub)
1. User hits `/sign-in?method=google`. Clerk-managed OAuth pop-up handles consent; on return Clerk session is ready.
2. Webhook consumes `user.created` (first time) or `user.updated` (subsequent), syncing email + profile image URL (if we later display avatars).
3. Backend `get_current_user` receives the Clerk session on first API call (e.g., `/api/v1/missions`), verifies it, and attaches `request.state.user`.
4. Audit log entry recorded (`event: social_login`, `provider: google`, `user_id: clerk_user_id`).

### Flow 3 – Logout & Session Expiry
1. User clicks “Sign out” from header avatar menu; `clerk.signOut` invalidates tokens across devices.
2. Clerk raises `session.ended` (optional) which we can listen to later; for now we rely on client redirect to `/sign-in`.
3. Middleware detects missing session on protected routes and 307-redirects to `/sign-in?redirect_url=<previous>`.
4. `/api/v1/health` reports `auth: connected` by pinging Clerk’s status endpoint every 60s and caching the result.

### Flow 4 – Account Deletion
1. User deletes account in Clerk dashboard (or we receive admin request).
2. Clerk emits `user.deleted` webhook; backend soft-deletes `User` record, cascades to `user_preferences`, and schedules eventual hard-delete (future).
3. Logs denote `deletion_reason`, `initiated_by`, and confirm database cleanup to satisfy privacy requirements. [Source: docs/product-brief-Delight-2025-11-09.md#Security-Metrics]

## Data & API Contracts

### Database Entities
| Table | Key Columns | Notes |
| ----- | ----------- | ----- |
| `users` | `id UUID`, `clerk_user_id VARCHAR UNIQUE`, `email VARCHAR`, `timezone`, `created_at`, `updated_at` | Created via Clerk webhook; `clerk_user_id` is authoritative. [Source: docs/stories/1-2-set-up-database-schema-and-migrations.md#Acceptance-Criteria] |
| `user_preferences` | `id UUID`, `user_id UUID UNIQUE`, `custom_hours JSONB`, `theme`, `communication_preferences JSONB`, `onboarding_completed` | Seeded with defaults; future onboarding updates fields. |
| `auth_webhook_events` (new optional) | `id UUID`, `clerk_event_id`, `event_type`, `processed_at`, `status`, `error` | Ensures idempotency and audit trail. |

### Backend Interfaces
| Endpoint | Method | Description | Auth | Handler |
| -------- | ------ | ----------- | ---- | ------- |
| `/api/v1/webhooks/clerk` | POST | Receives Clerk events, validates signature, upserts rows | Signature header + secret | `app/api/v1/webhooks.py` |
| `/api/v1/missions/*` | GET/POST | Existing mission APIs now require Clerk session | Bearer Clerk session | `get_current_user` dependency |
| `/api/v1/progress/*` | GET | Progress dashboards; ensures persona-level privacy | Bearer Clerk session | Shared dependency |

### Frontend Contracts
- `SignedIn` content component receives `user: { clerkId, email, timezone }` from `useUser()`; fallback to skeleton if not yet loaded.
- `SignedOut` fallback links to `/sign-in` with `redirect_url` query param so users return to their previous zone.

## Risk & Mitigation Matrix

| Risk | Impact | Likelihood | Mitigation |
| ---- | ------ | ---------- | ---------- |
| Misconfigured webhook secret allows spoofing | High | Medium | Use Clerk SDK signature helper, enforce timestamp skew ≤ 5 minutes, log and alert on failures. |
| Duplicate `User` rows due to race between webhook and first authenticated request | Medium | Medium | Upsert using `clerk_user_id` uniqueness constraint plus transaction-level retry. |
| Social provider outage blocks login | Medium | Low | Ensure email + magic link remain available; display helpful status message. |
| Theming divergence between Clerk UI and Delight App Router | Low | Medium | Centralize theme tokens in `delightTheme`, write visual regression snapshots via Playwright. |
| Secrets leaked via logs/tests | High | Low | Mask tokens, enforce `.env` loading through `pydantic-settings`, add lint rule preventing `CLERK_*` strings from being committed. |

## Manual Test Matrix

| Scenario | Steps | Expected Result | Status Evidence |
| -------- | ----- | --------------- | --------------- |
| Email sign-up | `/sign-up` → email/password → verify | User row created, redirected into companion lobby | Screenshot + DB query |
| Magic link sign-in | `/sign-in` → magic link | Email sent (Clerk test), login complete, webhook logs event | Clerk dashboard log |
| Google OAuth | `/sign-in?method=google` | OAuth success, backend API call returns 200 with user context | Playwright trace |
| GitHub OAuth | Same as Google | Same as Google | Playwright trace |
| Authenticated API call | `GET /api/v1/missions` with valid token | HTTP 200, JSON includes missions | HTTPX test |
| Unauthorized API call | Remove `Authorization` header | HTTP 401 with `detail: \"Not authenticated\"` | Pytest |
| Logout | Click logout button | Redirect to `/sign-in`, `useUser()` returns null | Screenshot/log |
| Account deletion | Delete via Clerk dashboard | `users` row soft-deleted, preferences removed | SQL + logs |

## Dependencies & Tooling
- `@clerk/nextjs` (frontend) and `clerk-backend-sdk` (backend) pinned per tech spec to ensure API parity. [Source: docs/tech-spec-epic-1.md#Dependencies-and-Integrations]
- Supabase (managed PostgreSQL) remains the source of truth for user data; ensure DATABASE_URL is configured before running migrations. [Source: docs/architecture.md#ADR-010-Supabase-for-Managed-PostgreSQL]
- Playwright, pytest-asyncio, and structured logging stack (structlog + Sentry) must be in sync with existing tooling from Stories 1.1/1.2.\n\n## Rollout & Monitoring Plan\n1. **Development** – Use Clerk test environment keys; run Playwright + pytest suites per commit.\n2. **Staging** – Deploy with staging Clerk instance, enabling webhook secret rotation tests. Monitor Sentry for auth errors.\n3. **Production** – Enable rate limiting on webhook endpoint (FastAPI middleware) and set up Sentry alert if failure rate >1% over 5 minutes.\n4. **Post-launch** – Review Clerk analytics + internal logs to confirm ≥90% success rate; interview pilot users about experience smoothness.
## Tasks / Subtasks

### 1. Frontend Integration & Theming (AC1, AC2, AC5)
- [ ] Install `@clerk/nextjs` and wrap `packages/frontend/src/app/layout.tsx` with `<ClerkProvider appearance={{ baseTheme: activeTheme }}>` pulling tokens from scenario context. [Source: docs/ux-design-specification.md#Visual-Design-System]
- [ ] Add `/sign-in` and `/sign-up` routes in `src/app/(auth)/` rendering `<SignIn/>` / `<SignUp/>`, plus optional modal entry points for narrative continuity.
- [ ] Implement `src/middleware.ts` to gate `/companion`, `/missions`, `/world`, `/progress`, `/api` routes while allowing static/marketing pages.
- [ ] Guard top-level navigation with `<SignedIn>` / `<SignedOut>` components so users see context-aware CTAs.
- [ ] Add logout button (e.g., in header avatar menu) calling `await clerk.signOut({ redirectUrl: '/sign-in' })`.
- [ ] Theme snippet example:
  ```tsx
  // packages/frontend/src/app/layout.tsx
  import { ClerkProvider } from '@clerk/nextjs';
  import { delightTheme } from '@/lib/theme/delight-theme';

  export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
      <ClerkProvider
        publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
        appearance={{
          baseTheme: delightTheme,
          variables: {
            colorPrimary: 'var(--arena-amber)',
            fontFamily: 'var(--delight-sans)'
          }
        }}
      >
        {children}
      </ClerkProvider>
    );
  }
  ```

### 2. Backend Session Dependency & Route Protection (AC3, AC5)
- [ ] Add `packages/backend/app/auth/dependencies.py` with `get_current_user` that:
  1. Extracts the Bearer token (Clerk session) from `Authorization` header.
  2. Calls `clerk.sessions.verify_session(token)`.
  3. Fetches or creates the `User` record via Async SQLAlchemy.
  4. Raises `HTTPException(status_code=401)` on verification failure.
- [ ] Inject dependency into mission, narrative, progress, and companion routers.
- [ ] Create pytest-asyncio tests that mock Clerk verification to cover allowed/denied requests.
- [ ] Update `/api/v1/health` to include Clerk availability (cached ping) so we don’t regress Story 1.2’s action items.

### 3. Webhook Processing & Database Sync (AC4, AC6)
- [ ] Build `packages/backend/app/api/v1/webhooks.py` with `POST /api/v1/webhooks/clerk` that validates signatures using `CLERK_WEBHOOK_SECRET`.
- [ ] Implement handlers:
  - `user.created`: upsert `User`, seed `UserPreferences` with defaults.
  - `user.updated`: sync email/timezone/preferences.
  - `user.deleted`: soft-delete `User`, cascade to preferences.
- [ ] Ensure all DB operations run inside a single async transaction to keep rows consistent.
- [ ] Log each event via `structlog` with `event_type`, `clerk_user_id`, `result`.
- [ ] Provide idempotency by keying operations on `clerk_event.id` stored in a processed-events table or Redis TTL list.

### 4. End-to-End Testing & Tooling (AC3–AC8)
- [ ] Extend frontend Playwright suite with flows for email signup, Google, GitHub, and magic link (use Clerk test users).
- [ ] Add backend pytest coverage for webhook endpoint (valid signature, replay attack, invalid payload).
- [ ] Document manual test plan aligning with the tech-spec checklist (sign up via each method, verify DB rows, exercise logout).
- [ ] Capture logs showing webhook success and paste excerpts into PR/story evidence.

### 5. Documentation, Env Config, and Ops (AC7, AC8)
- [ ] Update `packages/frontend/.env.example` and `packages/backend/.env.example` with Clerk publishable/secret/webhook keys plus explanatory comments.
- [ ] Enhance `README.md` and `docs/SETUP.md` with Clerk signup steps, webhook URL configuration, and how to run local tunneling (e.g., `clerk dev` or `ngrok`).
- [ ] Add runbooks to `docs/dev/BMAD-DEVELOPER-GUIDE.md` describing how to rotate keys and audit auth logs.

## Dependencies & Tooling
- `@clerk/nextjs` (frontend) and `clerk-backend-sdk` (backend) pinned per tech spec to ensure API parity. [Source: docs/tech-spec-epic-1.md#Dependencies-and-Integrations]
- Supabase (managed PostgreSQL) remains the source of truth for user data; ensure DATABASE_URL is configured before running migrations. [Source: docs/architecture.md#ADR-010-Supabase-for-Managed-PostgreSQL]
- Playwright, pytest-asyncio, and structured logging stack (structlog + Sentry) must stay in sync with Stories 1.1/1.2 tooling.

## Rollout & Monitoring Plan
1. **Development** – Use Clerk test environment keys; run Playwright + pytest suites per commit.
2. **Staging** – Deploy with staging Clerk instance, enabling webhook secret rotation tests. Monitor Sentry for auth errors.
3. **Production** – Enable rate limiting on webhook endpoint (FastAPI middleware) and set up Sentry alert if failure rate >1% over 5 minutes.
4. **Post-launch** – Review Clerk analytics + internal logs to confirm ≥90% success rate; interview pilot users about experience smoothness.

## Reference Implementations & Code Snippets

### Next.js Middleware Protection
```ts
// packages/frontend/src/middleware.ts
import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  publicRoutes: ['/', '/sign-in', '/sign-up', '/docs(.*)', '/health'],
  ignoredRoutes: ['/api/public/(.*)'],
  afterAuth(auth, req) {
    if (!auth.userId && !auth.isPublicRoute) {
      const url = new URL('/sign-in', req.url);
      url.searchParams.set('redirect_url', req.nextUrl.pathname);
      return Response.redirect(url);
    }
  }
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
};
```

### FastAPI Dependency
```python
# packages/backend/app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from clerk_backend_sdk import Clerk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer()
clerk = Clerk(api_key=settings.CLERK_SECRET_KEY)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        session = clerk.sessions.verify_session(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired Clerk session'
        ) from exc

    result = await db.execute(select(User).where(User.clerk_user_id == session.user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            clerk_user_id=session.user_id,
            email=session.user.primary_email_address.email_address,
            timezone=session.user.primary_email_address.timezone or 'UTC'
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
```

### Webhook Signature Validation
```python
# packages/backend/app/api/v1/webhooks.py
from clerk_backend_sdk import Clerk
clerk = Clerk(api_key=settings.CLERK_SECRET_KEY)

@router.post('/clerk', status_code=204)
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    signature = request.headers.get('Clerk-Signature')
    event = clerk.webhooks.verify(
        payload=payload,
        signature=signature,
        secret=settings.CLERK_WEBHOOK_SECRET
    )
    await process_clerk_event(event, db)
```

## Environment Configuration Checklist

| Variable | Location | Purpose |
| -------- | -------- | ------- |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `packages/frontend/.env.example` | Allows Clerk components to initialize on the client. |
| `CLERK_SECRET_KEY` | `packages/backend/.env.example` | Used by backend SDK for session/webhook validation. |
| `CLERK_WEBHOOK_SECRET` | Backend env | Validates webhook signatures. |
| `CLERK_SIGN_IN_URL` / `CLERK_SIGN_UP_URL` | Optional overrides | Useful for localized routes or branded domains. |
| `SUPABASE_DATABASE_URL` | Backend env | Required for user upsert logic. |
| `SENTRY_DSN` | Both envs | To trace auth failures end to end. |

Add these variables to onboarding docs and CI secrets; block merges when envs are missing by extending the preflight check introduced in Story 1.1. [Source: docs/stories/1-1-initialize-monorepo-structure-and-core-dependencies.md#Tasks-/-Subtasks]

## Observability & Alerting
- **Structured Logs:** Use `structlog` context of `{event_type, clerk_user_id, result, correlation_id}` for every webhook + login event. [Source: docs/architecture.md#Logging-Strategy]
- **Sentry Breadcrumbs:** Tag events with `component: 'auth'` and `provider: 'google'|'github'|'email'` to isolate issues quickly.
- **Metrics:** Expose counters such as `auth_logins_total{method='google'}` and `auth_failures_total{reason='invalid_signature'}` (Prometheus-friendly labels).
- **Alerts:** Trigger PagerDuty/Sentry when failure counts exceed thresholds or when Clerk status endpoint reports degraded service for >5 minutes.

## Future Work & Hand-offs
- **Story 1.4 (Onboarding Flow):** Will hook into the `onboarding_completed` flag seeded here; leave TODOs where the onboarding wizard will mount after authentication.
- **Epic 2 Memory System:** Requires Clerk IDs for memory ownership; confirm GraphQL/REST layers expose `clerk_user_id`.
- **Mobile Clients:** Document how React Native or Expo clients should reuse Clerk so we avoid divergent identity stacks.

## AC ↔ Task Traceability

| AC # | Key Deliverables | Related Tasks/Subtasks | Test Coverage |
| ---- | ---------------- | ---------------------- | ------------- |
| AC1 | `/sign-in`, `/sign-up` with four auth modalities | Frontend integration tasks 1–3 | Playwright `auth.spec.ts` scenarios |
| AC2 | Themed Clerk UI, narrative copy | Frontend theming task + UX tokens | Visual regression snapshots |
| AC3 | `get_current_user` dependency, route guards | Backend dependency + router updates | pytest `test_auth_dependency.py` |
| AC4 | Webhook endpoint, signature validation, DB upsert | Webhook processing tasks | pytest webhook suite + logs |
| AC5 | Logout + middleware redirects | Frontend logout + middleware tasks | Playwright logout test |
| AC6 | Consistent DB state, unique `clerk_user_id` | Webhook upsert + DB transaction tasks | SQL assertions in tests |
| AC7 | Logging, metrics, alerting | Observability + logging tasks | Manual log inspection + Sentry |
| AC8 | Docs, `.env.example`, evidence | Documentation tasks | PR checklist & attachments |

## Rollback Plan
1. **Frontend** – Feature-flag Clerk enforcement (`NEXT_PUBLIC_ENABLE_CLERK=0`) to temporarily fall back to the static marketing landing if the auth service degrades.
2. **Backend** – Keep the pre-Clerk JWT middleware behind a toggle so we can redeploy the previous container if Clerk suffers a prolonged outage; keep database migrations unchanged to simplify rollback.
3. **Database** – Because webhook upserts are idempotent, restoring from a Supabase point-in-time snapshot will recover from accidental data corruption.
4. **Monitoring** – Tie rollback triggers to Sentry/PagerDuty alerts plus manual QA verification.

## Compliance & Privacy Checklist
- [ ] Document the data flow (Clerk → Webhook → PostgreSQL) in `docs/architecture/security-architecture.md`.
- [ ] Ensure we can honor GDPR “right to be forgotten” by locating rows via `clerk_user_id`. [Source: docs/product-brief-Delight-2025-11-09.md#Security-Metrics]
- [ ] Mask PII in logs except for hashed Clerk IDs and redacted emails.
- [ ] Store Clerk secrets exclusively in the platform secret manager; never commit `.env` with real keys.
- [ ] Confirm webhook endpoints are exposed only over TLS (enforced by hosting provider configuration).

## Localization & Accessibility Notes
- Clerk components inherit Delight’s typography and palette; maintain WCAG AA contrast for both modern and fantasy themes. [Source: docs/ux-design-specification.md#Visual-Design-System]
- Provide localized copy hooks (English default) so future translations can swap strings without touching logic.
- Magic-link instructions must expose ARIA labels and focus states for keyboard/screen-reader users.
- When social providers fail, fall back to descriptive text and iconography that do not rely solely on color cues (supporting color-vision deficiencies).

## Development Timeline & Milestones

| Week | Milestone | Description |
| ---- | --------- | ----------- |
| Week 1 | Frontend scaffolding | Install Clerk SDK, wrap layout, add auth routes, theme components, stub tests. |
| Week 1 (end) | Backend skeleton | Add `get_current_user`, protect APIs, scaffold webhook endpoint, seed fixtures. |
| Week 2 | Webhook + DB validation | Finish upsert logic, idempotency store, structured logs, Supabase verification. |
| Week 2 (mid) | Playwright + pytest suites | Implement auth flows, webhook tests, health-check coverage. |
| Week 2 (end) | Documentation & env updates | Update READMEs, `.env.example`, runbooks, attach evidence. |
| Week 3 | Hardening & sign-off | Run manual checklist, fix issues, prepare for `story-context` workflow. |

## QA Checklist
- [ ] Playwright suite passes in CI with `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` pointing to test project.
- [ ] pytest suite covers auth dependency, webhook, and unauthorized access paths.
- [ ] Manual test evidence gathered for every auth method plus logout/deletion.
- [ ] Logs show no plaintext secrets and include event metadata.
- [ ] `/api/v1/health` displays accurate auth/database status.
- [ ] Accessibility audit (Lighthouse/axe) runs on `/sign-in` and `/sign-up`.

## Operational Runbook (Excerpt)
1. **Rotate Clerk secrets:** Generate new keys in Clerk dashboard → update secret manager → redeploy backend → rotate publishable key on frontend.
2. **Handle webhook failures:** Check Sentry alert → inspect logs for `event_id` → replay event by fetching from Clerk dashboard if needed.
3. **Emergency disable social provider:** Use Clerk dashboard to temporarily disable Google/GitHub; ensure email/magic links remain available.
4. **Audit access:** Quarterly, export Clerk audit log and compare against Supabase `auth_webhook_events` to ensure parity.

## Glossary
- **Clerk Session Token:** JWT issued by Clerk that proves user authentication.
- **Magic Link:** Passwordless email-based authentication method that logs the user in after clicking a secure link.
- **Scenario Theme:** UX-defined palette/typography representing Modern Reality, Medieval Fantasy, etc.
- **Essence:** In-universe reward currency; auth success should mention it subtly to maintain narrative continuity. [Source: docs/product-brief-Delight-2025-11-09.md#MVP-Scope]

## Threat Model Highlights

| Asset | Threat | Severity | Mitigation |
| ----- | ------ | -------- | ---------- |
| Session tokens | Token theft via XSS/logging | High | HttpOnly cookies, never logging tokens, use CSP from Story 1.1. |
| Webhook endpoint | Replay or forged events | High | Verify signatures + timestamps, store processed IDs, short timeout. |
| User database | Unauthorized row creation | Medium | Unique `clerk_user_id`, use DB transactions and row-level logging. |
| OAuth flows | Provider outage | Medium | Keep email/magic links active, display helpful UI messaging. |
| Secrets | Accidental leakage in repo | High | `.env.example` only, CI secret scanning, git hooks. |

## API Error Catalog
- `401 Not authenticated` – Missing/invalid Clerk session; frontend should redirect to `/sign-in`.
- `401 Invalid webhook signature` – Logged with `severity=error`, triggers alert if frequency > 5/min.
- `409 Duplicate user` – Should be rare; indicates race before webhook processed. Auto-resolve using upsert but log for investigation.
- `503 Clerk unavailable` – Health endpoint returns degraded status; middleware shows friendly error message.

## Testing Artifacts to Produce
- Playwright video and trace files for each auth method.
- pytest coverage report highlighting new auth modules.
- Supabase SQL export proving `users` and `user_preferences` rows exist for each test user.
- Log excerpts demonstrating webhook success and failure handling.
- Screenshot of `/api/v1/health` JSON showing `auth: \"connected\"`.

## Acceptance Criteria Evidence Plan

| AC | Evidence to Capture | Storage Location |
| -- | ------------------- | ---------------- |
| AC1 | Playwright recordings of email + social logins | `packages/frontend/tests/e2e/artifacts/` |
| AC2 | Screenshots showing themed Clerk UI variants | `docs/stories/evidence/1-3/` |
| AC3 | pytest log proving `get_current_user` denies invalid tokens | CI artifacts + validation report |
| AC4 | Webhook logs + DB snapshot showing upserts | `docs/stories/evidence/1-3/webhook-log.md` |
| AC5 | Video/screenshot of logout redirect and middleware guard | Evidence folder |
| AC6 | SQL output from Supabase verifying unique constraint + preferences row | Stored with DB evidence |
| AC7 | Sentry dashboard screenshot showing auth breadcrumbs | Evidence folder |
| AC8 | README diff, `.env.example` diff, validation report | Repo + docs/stories/validation-report-*.md |

## Dev ↔ QA Hand-off Checklist
- [ ] Story status `drafted` with validation report attached.
- [ ] Feature flag docs specify how to disable Clerk quickly.
- [ ] QA has access to the Clerk test project and Supabase staging database.
- [ ] All automated tests green and attached to PR summary.
- [ ] Manual checklist completed with timestamps, tester initials, and links to evidence.

## Release Readiness Checklist
- [ ] `docs/stories/validation-report-*.md` updated with latest checklist results.
- [ ] Sprint board card linked to evidence folder and tagged with “auth”.
- [ ] Observability dashboards (Sentry, logging) updated with new filters/widgets.
- [ ] Runbook stored in `docs/dev/BMAD-DEVELOPER-GUIDE.md` and referenced in PR.
- [ ] Stakeholders (product, design, QA) sign off asynchronously in PR comments.

## Dev Notes

### Architecture Patterns & Constraints
- Follow the monorepo layout defined in the architecture doc: frontend auth lives in `packages/frontend/src/app/(auth)/`, backend auth services in `packages/backend/app/auth/`, and shared types exported through `packages/shared/index.ts` to avoid deep relative imports. [Source: docs/architecture/project-structure.md]
- Clerk is the authoritative identity provider per ADR-007, so Delight should not store passwords or implement custom token logic; all session checks go through Clerk’s APIs. [Source: docs/architecture.md#ADR-007-Clerk-for-Authentication]
- Observability must leverage the structured logging plan (Clerk event metadata, request IDs) and Sentry instrumentation already defined for Epic 1. [Source: docs/architecture.md#Logging-Strategy]

### Learnings from Previous Story (1.2)
- **New capabilities to reuse:** Story 1.2 delivered async SQLAlchemy models (`packages/backend/app/models/user.py`) and migrations with pgvector enabled, so Story 1.3 should reuse these models rather than introducing new declarative bases. [Source: docs/stories/1-2-set-up-database-schema-and-migrations.md#Dev-Agent-Record]
- **Architectural deviations:** Senior review flagged duplicate declarative bases and missing Alembic imports; when adding auth models or hooks, import everything through `app.db.base` to keep metadata unified. [Source: docs/stories/1-2-set-up-database-schema-and-migrations.md#Senior-Developer-Review-(AI)]
- **Technical debt:** `/api/v1/health` still returns mock data, and pytest fixtures use SQLite. When adding auth dependencies, consider addressing the health-endpoint TODO and prefer PostgreSQL-compatible fixtures. [Source: docs/stories/1-2-set-up-database-schema-and-migrations.md#Senior-Developer-Review-(AI)]
- **New files to reference:** Database connection utilities (`packages/backend/app/db/session.py`), Alembic migrations, and the `scripts/test_db_connection.py` script can help seed and verify Clerk webhooks.

### Review Follow-ups & Outstanding Risks
1. **Alembic metadata gap:** Ensure auth-related models (if any) import `Base` from `app.db.base` to keep autogenerate working. [Source: docs/stories/1-2-set-up-database-schema-and-migrations.md#Senior-Developer-Review-(AI)]
2. **Health endpoint truthfulness:** Incorporate real database + Clerk checks into `/api/v1/health` so AC6 from Story 1.2 remains satisfied.
3. **Testing backend with PostgreSQL:** Update or extend pytest fixtures to hit a PostgreSQL DB (or Supabase test project) when verifying Clerk webhooks; SQLite won’t catch JSONB/UUID edge cases.

### Testing & Observability Guidance
- Follow the manual testing checklist from the tech spec (email/Google/GitHub/magic link, DB verification, logout). [Source: docs/tech-spec-epic-1.md#Manual-Testing-Checklist-(Story-1.3)]
- Playwright should rely on Clerk’s test environment to avoid touching production users; capture HAR files for regression triage.
- Backend tests should mock Clerk endpoints but also include at least one integration test hitting Clerk’s staging API to validate signature logic (flagged and skipped in CI if keys missing).
- Send auth logs to Sentry with `fingerprint: ['auth', eventType]` so ops can correlate outages quickly. [Source: docs/architecture.md#Observability]

### Security & Privacy Considerations
- Never log raw tokens or magic-link secrets; mask them before logging.
- Ensure webhook signature validation uses the official Clerk SDK helper and rejects mismatched timestamps (replay protection).
- Obey the data-minimization principle: store only Clerk user ID, primary email, timezone, and preference toggles—Clerk handles passwords, MFA, and breach detection. [Source: docs/epics/epic-1-user-onboarding-foundation.md#Story-1.3-Integrate-Clerk-Authentication-System]

### Project Structure Notes
- Frontend auth routes belong in `packages/frontend/src/app/(auth)/`; UI utilities live in `src/components/auth/` or `src/lib/theme/` per the architecture guide. [Source: docs/architecture/project-structure.md]
- Backend auth dependencies reside in `packages/backend/app/auth/`, with routers under `app/api/v1/`. Keep webhook handlers in their own module to avoid bloating the core API router.
- Shared TypeScript types for `AuthenticatedUser` should be exported from `packages/shared/types/user.ts` to keep mission/companion clients consistent.

### References
- docs/epics/epic-1-user-onboarding-foundation.md — Story-level acceptance criteria and technical notes for Story 1.3.
- docs/tech-spec-epic-1.md — Detailed architecture, manual testing checklist, and auth expectations.
- docs/product-brief-Delight-2025-11-09.md — Vision, personas, and emotional goals for onboarding/auth.
- docs/architecture.md — ADR-007 (Clerk), logging strategy, observability, and security posture.
- docs/architecture/project-structure.md — Required folder/modules layout for frontend/backend/shared packages.
- docs/ux-design-specification.md — Authentication flow, theming, and narrative transitions that this story must honor.
- docs/stories/1-2-set-up-database-schema-and-migrations.md — Previous story learnings, file list, and senior review action items.

## Change Log

| Date       | Author | Change Description                               |
| ---------- | ------ | ------------------------------------------------ |
| 2025-11-10 | SM     | Draft expanded with full ACs, tasks, and context |

## Dev Agent Record

### Context Reference
- docs/stories/1-3-integrate-clerk-authentication-system.context.xml

### Agent Model Used
OpenAI GPT-5 (Codex)

### Debug Log References
- Pending – populate during implementation.

### Completion Notes List
- Pending – add once development completes.

### File List
- Pending – list actual files added/modified during implementation.
