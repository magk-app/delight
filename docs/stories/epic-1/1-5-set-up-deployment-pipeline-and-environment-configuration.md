# Story 1.5: Set Up Deployment Pipeline and Environment Configuration

**Story ID:** 1.5
**Epic:** 1 - User Onboarding & Foundation
**Status:** backlog → drafted
**Priority:** P0 (Foundation)
**Estimated Effort:** 5-8 hours
**Assignee:** TBD
**Created:** 2025-11-11
**Updated:** 2025-11-11

---

## User Story

**As a** developer,
**I want** automated deployment and environment management with CI/CD pipeline,
**So that** we can deploy to staging/production with confidence and proper quality gates.

---

## Context

### Problem Statement

The Delight application has been developed locally but lacks a production deployment pipeline. Previous deployment attempts (visible in git history commits a467b4d through 983a8b3) included:
- Backend Dockerfile created for Railway deployment
- Manual migration strategy implemented
- Multiple deployment iterations with runtime fixes

However, these attempts lacked:
- **Automated CI/CD pipeline** for quality gates (linting, testing, building)
- **Frontend deployment configuration** (currently only backend Docker exists)
- **Health check endpoints** for monitoring and zero-downtime deployments
- **Proper environment management** with documented .env.example files
- **Comprehensive deployment documentation** for staging and production

### Dependencies

- **Prerequisite Stories:** 1.1 (monorepo), 1.2 (database), 1.3 (authentication)
- **External Services:** Vercel (frontend), Railway/Fly.io (backend), Supabase (database), Upstash (Redis)
- **Related Documentation:** `docs/architecture/deployment-architecture.md`, `docs/SETUP.md`

### Technical Background

Current deployment architecture (from docs/architecture/deployment-architecture.md):

**Experimental/Staging:**
- Frontend: Vercel (Next.js optimized)
- Backend: Railway or Fly.io (Docker containers)
- Database: Supabase (managed PostgreSQL with pgvector)
- Redis: Upstash (serverless Redis)

**Production:**
- Frontend: Vercel (edge network)
- Backend: AWS ECS/Fargate or Fly.io (auto-scaling)
- Database: AWS RDS PostgreSQL or Supabase
- Redis: AWS ElastiCache or Upstash
- Monitoring: Sentry (errors, performance), CloudWatch (infrastructure)

---

## Acceptance Criteria

### 1. CI/CD Pipeline (GitHub Actions)

**Given** code is pushed to the repository
**When** the CI/CD pipeline runs
**Then** the following checks execute automatically:

- **Linting**
  - ✅ Frontend: ESLint with Next.js config
  - ✅ Backend: Ruff (linter) and Black (formatter) checks
  - ❌ Pipeline fails if linting errors exist

- **Type Checking**
  - ✅ Frontend: TypeScript compilation check
  - ✅ Backend: mypy type checking (if applicable)

- **Testing**
  - ✅ Frontend: Jest unit tests (when added)
  - ✅ Backend: pytest with coverage report (≥70% target)
  - ✅ Integration tests for API endpoints
  - ❌ Pipeline fails if tests fail

- **Build Verification**
  - ✅ Frontend: `next build` succeeds
  - ✅ Backend: Docker image builds successfully
  - ✅ No build warnings or errors

**And** the pipeline provides clear feedback:
- ✅ Status badges in README
- ✅ PR comments with test results
- ✅ Build logs accessible for debugging

### 2. Environment Configuration

**Given** developers and ops teams need to configure environments
**When** they reference environment documentation
**Then** they find:

- ✅ **Frontend `.env.example`** in `packages/frontend/` with:
  ```bash
  # Clerk Authentication (Public - exposed to browser)
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

  # Clerk Authentication (Secret - server-side only)
  CLERK_SECRET_KEY=sk_test_...

  # API Configuration
  NEXT_PUBLIC_API_URL=http://localhost:8000

  # Environment
  NODE_ENV=development  # development | production
  ```

- ✅ **Backend `.env.example`** in `packages/backend/` with:
  ```bash
  # Database (Supabase)
  DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.xxx.supabase.co:5432/postgres

  # Redis (Upstash or local)
  REDIS_URL=redis://localhost:6379

  # Authentication (Clerk)
  CLERK_SECRET_KEY=sk_test_...
  CLERK_WEBHOOK_SECRET=whsec_...

  # AI/LLM
  OPENAI_API_KEY=sk-proj-...

  # Environment
  ENVIRONMENT=development  # development | staging | production

  # Infrastructure Mode
  INFRA_MODE=cloud-dev  # local | cloud-dev | production

  # Monitoring (Optional for dev)
  SENTRY_DSN=https://...@sentry.io/...

  # Security
  ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
  ```

**And** environment-specific configurations:
- ✅ Development: Local or cloud-dev mode, verbose logging
- ✅ Staging: Cloud services, moderate logging, Sentry enabled
- ✅ Production: Optimized builds, minimal logging, full monitoring

### 3. Health Check Endpoints

**Given** the backend API is deployed
**When** monitoring systems or load balancers query health endpoints
**Then** they receive accurate status information:

- ✅ **Basic Health Check** (`GET /api/v1/health`)
  ```json
  {
    "status": "healthy",  // healthy | degraded | unhealthy
    "timestamp": "2025-11-11T12:34:56Z",
    "version": "0.1.0"
  }
  ```

- ✅ **Detailed Health Check** (`GET /api/v1/health/detailed`)
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-11-11T12:34:56Z",
    "version": "0.1.0",
    "checks": {
      "database": {
        "status": "connected",
        "response_time_ms": 12
      },
      "redis": {
        "status": "connected",
        "response_time_ms": 3
      },
      "clerk": {
        "status": "configured"
      }
    }
  }
  ```

**And** health checks are used for:
- ✅ Container orchestration (Railway, Fly.io) readiness probes
- ✅ Load balancer health checks
- ✅ Uptime monitoring (UptimeRobot, Checkly, etc.)

### 4. Deployment Configuration

**Given** the application needs to be deployed
**When** deployment is triggered
**Then** the following configurations exist:

#### Backend Deployment

- ✅ **Dockerfile** in `packages/backend/` (restore and improve from git history a467b4d)
  - Multi-stage build for smaller image size
  - Poetry for dependency management
  - Health check command included
  - Port configurable via PORT env var
  - No migrations in startup (run manually)

- ✅ **`.dockerignore`** to exclude:
  - `__pycache__`, `*.pyc`, `.pytest_cache`
  - `.env`, `.env.*` (secrets)
  - `tests/`, `docs/`
  - `.git/`, `.github/`

#### Frontend Deployment

- ✅ **Vercel Configuration** (`vercel.json` or dashboard setup)
  - Environment variables configured
  - Build command: `pnpm build`
  - Output directory: `.next`
  - Node version: 20.x
  - Next.js 15 compatibility ensured

- ✅ **Alternative: Frontend Dockerfile** (if not using Vercel)
  - Node 20 Alpine base image
  - Multi-stage build (dependencies → build → production)
  - Standalone output for minimal image size

### 5. Deployment Process Documentation

**Given** team members need to deploy the application
**When** they follow deployment documentation
**Then** they can successfully deploy to:

- ✅ **Local Development** (Makefile commands already exist)
  - `make local`: Start local Docker services
  - `make cloud-dev`: Use managed services (Supabase, Upstash)
  - `make dev`: Start development servers

- ✅ **Staging Environment**
  - Manual deploy: `git push staging main`
  - Automatic: PR merged to `develop` branch triggers deploy
  - Environment: `staging` with Supabase/Upstash
  - Health checks pass before marking deploy successful

- ✅ **Production Environment**
  - Manual deploy: Tag release, `git push production v1.0.0`
  - Automatic: PR merged to `main` triggers deploy (future)
  - Blue-green or rolling deployment strategy
  - Automated rollback on health check failure
  - Database migrations run manually with documented process

### 6. Secrets Management

**Given** sensitive configuration needs to be stored
**When** deploying to different environments
**Then** secrets are managed securely:

- ✅ **Local Development**
  - `.env` files (gitignored)
  - `.env.example` checked into git as template

- ✅ **Staging/Production**
  - Platform-specific secret management:
    - Vercel: Environment Variables dashboard
    - Railway/Fly.io: `flyctl secrets` or Railway dashboard
    - GitHub Actions: Repository secrets

- ✅ **Never Committed**
  - Actual `.env` files with real secrets
  - API keys, database passwords, JWT secrets
  - `.gitignore` includes: `.env`, `.env.local`, `.env.*.local`

---

## Technical Implementation Details

### File Structure

```
delight/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # NEW: Main CI/CD pipeline
│       ├── deploy-backend.yml        # NEW: Backend deployment
│       ├── deploy-frontend.yml       # NEW: Frontend deployment (optional)
│       ├── claude-code-review.yml    # Existing
│       └── claude.yml                # Existing
│
├── packages/
│   ├── frontend/
│   │   ├── .env.example              # NEW: Frontend env template
│   │   ├── .dockerignore             # NEW: Docker ignore (if using Docker)
│   │   ├── Dockerfile                # NEW: Frontend container (optional)
│   │   └── vercel.json               # NEW: Vercel config (if using Vercel)
│   │
│   └── backend/
│       ├── .env.example              # NEW: Backend env template
│       ├── .dockerignore             # RESTORE: From git history
│       ├── Dockerfile                # RESTORE & IMPROVE: From git history a467b4d
│       └── app/
│           └── api/
│               └── v1/
│                   └── health.py     # NEW: Health check endpoints
│
├── docs/
│   ├── DEPLOYMENT.md                 # NEW: Deployment guide
│   └── SETUP.md                      # UPDATE: Add deployment section
│
└── README.md                         # UPDATE: Add deployment badges
```

### GitHub Actions CI Pipeline (`.github/workflows/ci.yml`)

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      # Setup Node for frontend
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      # Setup Python for backend
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # Install dependencies
      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install frontend dependencies
        run: cd packages/frontend && pnpm install

      - name: Install Poetry
        run: pip install poetry

      - name: Install backend dependencies
        run: cd packages/backend && poetry install

      # Linting
      - name: Lint frontend
        run: cd packages/frontend && pnpm lint

      - name: Lint backend
        run: |
          cd packages/backend
          poetry run ruff check .
          poetry run black --check .

      # Type checking
      - name: TypeScript check
        run: cd packages/frontend && pnpm tsc --noEmit

      # Testing
      - name: Test backend
        run: cd packages/backend && poetry run pytest -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          REDIS_URL: redis://localhost:6379
          CLERK_SECRET_KEY: test_key
          ENVIRONMENT: testing

      # Build verification
      - name: Build frontend
        run: cd packages/frontend && pnpm build

      - name: Build backend Docker image
        run: |
          cd packages/backend
          docker build -t delight-backend:${{ github.sha }} .

      # Upload coverage
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./packages/backend/coverage.xml
          flags: backend
```

### Health Check Implementation (`packages/backend/app/api/v1/health.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis import asyncio as aioredis
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

from app.db.session import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])

class HealthStatus(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str = "0.1.0"

class ServiceCheck(BaseModel):
    status: Literal["connected", "disconnected", "configured", "error"]
    response_time_ms: int | None = None
    error: str | None = None

class DetailedHealthStatus(HealthStatus):
    checks: dict[str, ServiceCheck]

@router.get("", response_model=HealthStatus)
async def basic_health_check():
    """Basic health check for load balancers and uptime monitoring."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0"
    )

@router.get("/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with service status."""
    checks = {}
    overall_status = "healthy"

    # Database check
    try:
        start = datetime.utcnow()
        await db.execute(text("SELECT 1"))
        response_time = int((datetime.utcnow() - start).total_seconds() * 1000)
        checks["database"] = ServiceCheck(
            status="connected",
            response_time_ms=response_time
        )
    except Exception as e:
        checks["database"] = ServiceCheck(
            status="error",
            error=str(e)
        )
        overall_status = "unhealthy"

    # Redis check
    try:
        start = datetime.utcnow()
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        response_time = int((datetime.utcnow() - start).total_seconds() * 1000)
        checks["redis"] = ServiceCheck(
            status="connected",
            response_time_ms=response_time
        )
        await redis.close()
    except Exception as e:
        checks["redis"] = ServiceCheck(
            status="error",
            error=str(e)
        )
        overall_status = "degraded"  # Redis failure is degraded, not unhealthy

    # Clerk check (just verify it's configured)
    try:
        if settings.CLERK_SECRET_KEY:
            checks["clerk"] = ServiceCheck(status="configured")
        else:
            checks["clerk"] = ServiceCheck(
                status="error",
                error="CLERK_SECRET_KEY not configured"
            )
            overall_status = "degraded"
    except Exception as e:
        checks["clerk"] = ServiceCheck(
            status="error",
            error=str(e)
        )
        overall_status = "degraded"

    return DetailedHealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="0.1.0",
        checks=checks
    )
```

### Improved Dockerfile (`packages/backend/Dockerfile`)

```dockerfile
# Multi-stage build for smaller production image

# Stage 1: Builder
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip setuptools wheel poetry poetry-plugin-export

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Export dependencies to requirements.txt
RUN poetry config virtualenvs.create false && \
    poetry export -f requirements.txt -o requirements.txt --without-hashes --without dev

# Stage 2: Production
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from builder
COPY --from=builder /app/requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Environment variables
ENV PORT=8000
EXPOSE 8000

# Start application (no migrations - run manually)
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

### Environment File Templates

**Frontend `.env.example`:**
```bash
# ================================
# Clerk Authentication
# ================================
# Public key (exposed to browser - safe)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Secret key (server-side only - NEVER expose to browser)
CLERK_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ================================
# API Configuration
# ================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# ================================
# Environment
# ================================
NODE_ENV=development  # development | production
```

**Backend `.env.example`:**
```bash
# ================================
# Database (Supabase)
# ================================
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.xxx.supabase.co:5432/postgres

# ================================
# Redis (Upstash or Local)
# ================================
REDIS_URL=redis://localhost:6379
# For Upstash: rediss://default:[password]@[region].upstash.io:6379

# ================================
# Authentication (Clerk)
# ================================
CLERK_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ================================
# AI/LLM (OpenAI)
# ================================
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ================================
# Environment Configuration
# ================================
ENVIRONMENT=development  # development | staging | production
INFRA_MODE=cloud-dev    # local | cloud-dev | production

# ================================
# Monitoring (Optional)
# ================================
SENTRY_DSN=https://[key]@[org].ingest.sentry.io/[project]

# ================================
# Security
# ================================
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# ================================
# Server Configuration
# ================================
PORT=8000
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

---

## Testing Strategy

### Pre-Deployment Testing

1. **Local Build Verification**
   ```bash
   # Frontend
   cd packages/frontend
   pnpm build
   pnpm start  # Verify production build works

   # Backend Docker
   cd packages/backend
   docker build -t delight-backend:test .
   docker run -p 8000:8000 --env-file .env delight-backend:test
   curl http://localhost:8000/api/v1/health
   ```

2. **CI Pipeline Testing**
   - Create PR to trigger CI checks
   - Verify all linting passes
   - Verify all tests pass
   - Verify builds succeed

3. **Health Check Testing**
   ```bash
   # Start backend
   cd packages/backend
   poetry run uvicorn main:app --reload

   # Test health endpoints
   curl http://localhost:8000/api/v1/health
   curl http://localhost:8000/api/v1/health/detailed

   # Expected: {"status": "healthy", ...}
   ```

### Staging Deployment Testing

1. **Deploy to Staging**
   - Push to `develop` branch
   - Verify automatic deployment triggers
   - Monitor deployment logs

2. **Smoke Tests**
   - ✅ Health checks return healthy status
   - ✅ Frontend loads successfully
   - ✅ Can authenticate with Clerk
   - ✅ API endpoints respond correctly
   - ✅ Database connection works
   - ✅ Redis connection works

3. **Integration Tests**
   - Run E2E Playwright tests against staging
   - Verify authentication flow
   - Verify API integration

---

## Implementation Tasks

### Phase 1: Environment Configuration (1-2 hours)

- [ ] Create `packages/frontend/.env.example`
- [ ] Create `packages/backend/.env.example`
- [ ] Update `.gitignore` to include `.env*` patterns
- [ ] Document environment variables in `docs/SETUP.md`

### Phase 2: Health Check Endpoints (1 hour)

- [ ] Create `packages/backend/app/api/v1/health.py`
- [ ] Implement basic health check endpoint
- [ ] Implement detailed health check with service status
- [ ] Add health check route to FastAPI app
- [ ] Test health checks locally

### Phase 3: Docker Configuration (1-2 hours)

- [ ] Restore `packages/backend/Dockerfile` from git (a467b4d)
- [ ] Improve Dockerfile with multi-stage build
- [ ] Add health check to Dockerfile
- [ ] Create/restore `packages/backend/.dockerignore`
- [ ] Test Docker build locally
- [ ] (Optional) Create frontend Dockerfile if not using Vercel

### Phase 4: CI/CD Pipeline (2-3 hours)

- [ ] Create `.github/workflows/ci.yml`
- [ ] Add linting jobs (frontend ESLint, backend Ruff/Black)
- [ ] Add testing jobs (backend pytest with coverage)
- [ ] Add build verification (frontend build, backend Docker build)
- [ ] Test CI pipeline with PR
- [ ] Add status badges to README

### Phase 5: Deployment Setup (1-2 hours)

- [ ] Configure Vercel project for frontend
  - [ ] Connect GitHub repository
  - [ ] Set environment variables
  - [ ] Configure build settings
- [ ] Configure backend deployment (Railway/Fly.io)
  - [ ] Connect repository or set up Docker deployment
  - [ ] Set environment variables
  - [ ] Configure health check endpoint
  - [ ] Set PORT environment variable
- [ ] Test staging deployment
- [ ] Document deployment process

### Phase 6: Documentation (30 minutes)

- [ ] Create `docs/DEPLOYMENT.md` with:
  - [ ] Deployment architecture overview
  - [ ] Environment setup instructions
  - [ ] Manual deployment steps
  - [ ] Troubleshooting guide
- [ ] Update `docs/SETUP.md` with deployment section
- [ ] Update README with deployment badges and links

---

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **CI pipeline fails in production** | High | Medium | Test pipeline thoroughly in PR before merge; have rollback plan |
| **Environment variables misconfigured** | High | Medium | Use .env.example as template; document all variables clearly |
| **Health checks don't reflect true status** | Medium | Low | Test health checks with intentional failures (disconnect DB, etc.) |
| **Docker build fails in CI** | Medium | Low | Test Docker build locally first; use docker-compose for integration tests |
| **Deployment secrets leaked** | Critical | Low | Never commit .env files; use platform secret management; audit .gitignore |
| **Frontend/backend version mismatch** | Medium | Medium | Use version tags; deploy frontend and backend together; test integration |

---

## Definition of Done

- [ ] ✅ All acceptance criteria met and manually tested
- [ ] ✅ CI/CD pipeline runs successfully on PR
- [ ] ✅ All linting checks pass (frontend + backend)
- [ ] ✅ All tests pass with ≥70% backend coverage
- [ ] ✅ Frontend builds successfully in CI
- [ ] ✅ Backend Docker image builds successfully in CI
- [ ] ✅ Environment templates (`.env.example`) created for frontend and backend
- [ ] ✅ Health check endpoints implemented and tested
- [ ] ✅ Staging deployment successful and verified
- [ ] ✅ Documentation complete (`DEPLOYMENT.md` created, `SETUP.md` updated)
- [ ] ✅ README updated with deployment badges and links
- [ ] ✅ Code review completed and approved
- [ ] ✅ No secrets committed to repository (verified with git log)
- [ ] ✅ Deployment rollback procedure documented and tested
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Notes

### Learnings from Previous Deployment Attempts

From git history analysis (commits a467b4d → 983a8b3):

1. **Manual migrations strategy worked** - Don't run migrations in Dockerfile startup
2. **Railway deployment attempted** - Consider continuing with Railway or switch to Fly.io
3. **Multiple runtime fixes needed** - Emphasizes importance of proper CI/CD testing
4. **Database connection errors** - Need robust health checks and error handling

### Why Manual Migrations?

Running migrations automatically on startup can cause:
- **Race conditions** with multiple container instances
- **Failed deployments** if migration fails
- **Downtime** during long-running migrations

Best practice: Run migrations as separate deployment step before scaling up new containers.

### Cost Considerations

- **Vercel**: Free tier sufficient for MVP (100GB bandwidth, unlimited requests)
- **Railway**: $5/month credits, pay-as-you-go (~$10-20/month for MVP)
- **Fly.io**: Free tier 3 VMs, pay-as-you-go after (~$5-15/month for MVP)
- **Supabase**: Free tier 500MB DB (sufficient for MVP)
- **Upstash**: Free tier 10,000 commands/day (sufficient for MVP)

**Estimated monthly cost:** $0-30 for staging, $20-50 for production MVP.

### Future Enhancements (Post-Story)

- [ ] Automated database backups with restoration testing
- [ ] Blue-green deployment strategy
- [ ] Automated rollback on failed health checks
- [ ] Performance monitoring (response times, error rates)
- [ ] Log aggregation (Logtail, Papertrail)
- [ ] Automated security scanning (Snyk, Dependabot)
- [ ] Infrastructure as Code (Terraform, Pulumi)
- [ ] Preview deployments for PRs

---

## References

- **Architecture**: `docs/architecture/deployment-architecture.md`
- **Setup Guide**: `docs/SETUP.md`
- **Epic 1 Tech Spec**: `docs/tech-spec-epic-1.md`
- **Git History**: Commits a467b4d (latest deployment), 983a8b3 (Docker introduction)
- **CLAUDE.md**: Project guidelines and development workflow

---

## Story Context

This story is part of Epic 1: User Onboarding & Foundation. It completes the foundation infrastructure needed before moving to Epic 2 (Companion & Memory System). Without deployment capability, we cannot iterate with real users or validate the system in production-like environments.

Completion of this story enables:
- **Continuous delivery** of new features to staging/production
- **Quality gates** ensuring code quality before deployment
- **Confidence** in deployment process through automation
- **Monitoring** of system health in production
- **Faster iteration** with real user feedback

---

**Last Updated:** 2025-11-11
**Story Status:** backlog → drafted (ready for review)
**Next Steps:** SM review → story-context workflow → ready-for-dev
