---
title: Quick Start
description: Get Delight up and running in 5 minutes
---

# Quick Start Guide

Get Delight running locally in just a few minutes.

## Prerequisites

- **Node.js** 20+ and **pnpm** 8+
- **Python** 3.11+ with **Poetry**
- **Supabase** account (free tier works)
- **Clerk** account (free tier works)
- **OpenAI API key**

## Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/delight.git
cd delight

# Install dependencies
pnpm install
cd packages/backend && poetry install
```

## Step 2: Environment Setup

Copy the example environment files:

```bash
# Backend
cp packages/backend/.env.example packages/backend/.env

# Frontend
cp packages/frontend/.env.example packages/frontend/.env.local
```

Fill in your environment variables:

**Backend (.env):**

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_key
CLERK_SECRET_KEY=your_clerk_secret
```

**Frontend (.env.local):**

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Step 3: Database Setup

Run migrations to set up your Supabase database:

```bash
cd packages/backend
poetry run python scripts/migrate.py
```

## Step 4: Start Development Servers

From the repository root:

```bash
# Start both frontend and backend
pnpm dev

# Or start them separately:
pnpm dev:frontend  # Runs on http://localhost:3000
pnpm dev:backend   # Runs on http://localhost:8000
```

## Step 5: Verify Installation

1. **Frontend**: Visit http://localhost:3000
2. **Backend API**: Visit http://localhost:8000/docs (FastAPI Swagger UI)
3. **Health Check**: Visit http://localhost:8000/health

## Next Steps

- Read the [Developer Guide](/dev/developer-guide) for detailed workflows
- Check out the [Architecture Overview](/architecture/overview) to understand the system
- Review [Epic 1](/epics/epic-1) to see what's being built

## Troubleshooting

### Port Already in Use

If port 3000 or 8000 is already in use, you can change them:

**Frontend**: Edit `packages/frontend/package.json` scripts
**Backend**: Edit `packages/backend/main.py` uvicorn port

### Poetry Issues

If Poetry isn't installed:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Database Connection Errors

- Verify your Supabase URL and keys are correct
- Ensure your Supabase project is active
- Check that migrations ran successfully

## Need Help?

- Check the [Development Guide](/dev/developer-guide) for detailed workflows
- Review [Architecture Docs](/architecture/overview) for system design
- Open an issue on [GitHub](https://github.com/your-org/delight/issues)

---

**Ready to build?** Check out the [Developer Guide](/dev/developer-guide) next!
