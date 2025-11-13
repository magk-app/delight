# Delight Backend API

FastAPI backend for the Delight AI companion platform.

## Quick Start

```bash
# Install dependencies
poetry install

# Start development server
poetry run uvicorn main:app --reload
```

Visit:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
app/
├── api/v1/         # API routes
│   └── health.py   # Health check endpoint
├── core/           # Configuration and dependencies
├── models/         # SQLAlchemy database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── agents/         # LangGraph AI agents
├── workers/        # ARQ background jobs
└── db/             # Database setup and migrations
```

## Development

```bash
# Run tests
poetry run pytest

# Lint code
poetry run ruff check .

# Format code
poetry run black .

# Type check
poetry run mypy .
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

- **INFRA_MODE**: `cloud-dev` or `local`
- **DATABASE_URL**: PostgreSQL connection string
- **REDIS_URL**: Redis connection string
- **CLERK_SECRET_KEY**: Clerk authentication secret
- **CLERK_WEBHOOK_SECRET**: Clerk webhook validation secret
- **OPENAI_API_KEY**: OpenAI API key
- **CORS_ORIGINS**: Comma-separated list of allowed frontend URLs

See `.env.example` for detailed configuration instructions.

## Deployment

This backend is designed to deploy to **Railway**.

### Quick Deployment Checklist

1. **Set Root Directory:** `packages/backend` in Railway settings
2. **Configure Environment Variables:**
   - `DATABASE_URL` - Supabase PostgreSQL URL (with `+asyncpg`)
   - `CLERK_SECRET_KEY` - From Clerk Dashboard
   - `CLERK_WEBHOOK_SECRET` - From Clerk Webhooks
   - `CORS_ORIGINS` - Your Vercel frontend URL (no trailing slash!)
3. **Railway auto-deploys** on push to main branch

### Common Deployment Issues

**502 Bad Gateway:**
- Check Railway logs for startup errors
- Verify all required environment variables are set
- Ensure DATABASE_URL uses `postgresql+asyncpg://` format

**CORS Errors:**
- Update `CORS_ORIGINS` in Railway to include your Vercel domain
- Format: `https://your-app.vercel.app,http://localhost:3000`
- No trailing slashes, no wildcards

**Database Connection Fails:**
- Verify DATABASE_URL format: `postgresql+asyncpg://user:pass@host:5432/db`
- URL-encode special characters in password
- Check Supabase project is active (not paused)

### Full Deployment Guide

See [docs/DEPLOYMENT.md](../../docs/DEPLOYMENT.md) for comprehensive deployment instructions covering:
- Railway configuration and environment variables
- Vercel frontend setup
- Clerk webhook configuration
- Database migrations
- Troubleshooting guide

