---
title: Development Setup
description: Complete environment setup guide for Delight developers
---

# Development Setup

Complete guide to setting up your Delight development environment.

## Prerequisites

- **Node.js** 20+ and **pnpm** 8+
- **Python** 3.11+ with **Poetry**
- **Supabase** account (free tier works)
- **Clerk** account (free tier works)
- **OpenAI API key**

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-org/delight.git
cd delight

# Install dependencies
pnpm install
cd packages/backend && poetry install
```

## Environment Configuration

### Backend Setup

1. Copy the example environment file:

```bash
cp packages/backend/.env.example packages/backend/.env
```

2. Fill in your environment variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_key
CLERK_SECRET_KEY=your_clerk_secret
```

### Frontend Setup

1. Copy the example environment file:

```bash
cp packages/frontend/.env.example packages/frontend/.env.local
```

2. Fill in your environment variables:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Database Setup

Run migrations to set up your Supabase database:

```bash
cd packages/backend
poetry run python scripts/migrate.py
```

## Running the Application

### Start Both Services

From the repository root:

```bash
pnpm dev
```

This starts:

- Frontend on http://localhost:3000
- Backend API on http://localhost:8000

### Start Services Separately

```bash
# Frontend only
pnpm dev:frontend

# Backend only
pnpm dev:backend
```

## Verification

1. **Frontend**: Visit http://localhost:3000
2. **Backend API Docs**: Visit http://localhost:8000/docs (FastAPI Swagger UI)
3. **Health Check**: Visit http://localhost:8000/health

## Development Workflow

See the [Developer Guide](/dev/developer-guide) for:

- Story development workflow
- Code quality standards
- Testing guidelines
- Commit conventions

## Troubleshooting

### Port Already in Use

Change ports in:

- Frontend: `packages/frontend/package.json` scripts
- Backend: `packages/backend/main.py` uvicorn configuration

### Poetry Not Installed

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Database Connection Errors

- Verify Supabase URL and keys
- Ensure Supabase project is active
- Check migrations ran successfully

## Next Steps

- Read the [Developer Guide](/dev/developer-guide)
- Check the [Quick Reference](/dev/quick-reference) for commands
- Review [Contributing Guidelines](/dev/contributing)
