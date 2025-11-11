# Codex Development Environment Setup Guide

This guide helps you configure a Codex development environment for the Delight monorepo, supporting both frontend (Next.js) and backend (FastAPI) development.

## Important: One Environment for Monorepo

**You only need ONE Codex environment for this monorepo**, even though it contains both frontend and backend packages.

- **One environment** = One workspace that contains the entire repository
- The monorepo structure (`packages/frontend/` and `packages/backend/`) lives within that single environment
- You configure environment variables for **both** frontend and backend in the same environment
- You can run both services from the same environment (using different terminals or `pnpm dev` which runs both concurrently)

**Why one environment?**

- Codex environments are tied to repositories, not individual packages
- The monorepo is one repository, so it gets one environment
- Both frontend and backend share the same workspace and can access each other's code
- This is actually ideal for monorepo development!

## Quick Configuration Summary

### Container Image

- **Select:** `universal` (Ubuntu 24.04 based)
- **Workspace Directory:** `/workspace/delight` (default, or edit as needed)

### Setup Script

- **Mode:** `Automatic` (recommended)
- The automatic setup will detect and install dependencies for both frontend (pnpm) and backend (poetry)

### Container Caching

- **Enable:** `On` (recommended for faster subsequent starts)

### Agent Internet Access

- **Enable:** `On` (required for npm/pnpm, poetry, and API calls)

---

## Environment Variables

**Add ALL of these environment variables in the SAME Codex environment configuration panel.** Since this is a monorepo, both frontend and backend variables go in the same environment.

### Required for Backend

```bash
# Infrastructure Mode (choose one)
INFRA_MODE=cloud-dev
# or
INFRA_MODE=local

# Database Configuration
# For cloud-dev: Use Supabase connection string
DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
# For local: Use Docker PostgreSQL (if running locally)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight

# Authentication (Clerk)
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...

# Redis (optional but recommended)
REDIS_URL=redis://localhost:6379
# or for cloud: redis://default:[password]@[host]:6379

# AI/LLM (optional for MVP)
OPENAI_API_KEY=sk-...

# Environment
ENVIRONMENT=development

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Required for Frontend

```bash
# Clerk Authentication (Public Key - safe for browser)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

# Clerk Secret Key (for Next.js middleware - server-side only)
CLERK_SECRET_KEY=sk_test_...

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important Notes:**

- **All variables go in ONE environment** - Don't create separate environments for frontend/backend
- Codex environment variables are available to all processes in the workspace
- The frontend will read from `.env.local` if it exists, otherwise from environment variables
- The backend reads from `.env` if it exists, otherwise from environment variables
- You can create `.env.local` and `.env` files in the workspace if you prefer file-based config

---

## Secrets Configuration

Add these as **Secrets** (not environment variables) in Codex:

1. **CLERK_SECRET_KEY** - Your Clerk secret key (starts with `sk_test_` or `sk_live_`)
2. **CLERK_WEBHOOK_SECRET** - Your Clerk webhook signing secret (starts with `whsec_`)
3. **DATABASE_URL** - Your database connection string (if using cloud-dev mode)
4. **OPENAI_API_KEY** - Your OpenAI API key (starts with `sk-`)
5. **REDIS_URL** - Your Redis connection URL (if using cloud Redis)

**Why Secrets?** These contain sensitive credentials that should be encrypted and not exposed in logs or environment variable listings.

---

## Setup Script Configuration

### Option 1: Automatic (Recommended)

The automatic setup will:

1. Detect `pnpm-lock.yaml` in the root and install Node.js dependencies
2. Detect `pyproject.toml` in `packages/backend/` and install Python dependencies with Poetry
3. Run any post-install scripts

**Configuration:**

- **Mode:** `Automatic`
- No additional script needed

### Option 2: Manual Setup Script

If you prefer manual control, use this setup script:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up Delight development environment..."

# Install root dependencies
echo "📦 Installing root dependencies..."
pnpm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd packages/frontend
pnpm install
cd ../..

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd packages/backend
poetry install
cd ../..

# Verify installations
echo "✅ Verifying installations..."
node --version
pnpm --version
python3 --version
poetry --version

echo "✅ Setup complete!"
```

**Configuration:**

- **Mode:** `Manual`
- **Script:** Paste the above script into the setup script field

---

## Domain Allowlist

For cloud-dev mode, you may need to allowlist these domains:

### Common Dependencies (Recommended)

- `npmjs.org` - npm package registry
- `pypi.org` - Python package index
- `github.com` - Git repository access
- `supabase.com` - Database access (if using Supabase)
- `upstash.com` - Redis access (if using Upstash)
- `clerk.com` - Authentication service
- `openai.com` - AI API access

### Custom Domain Allowlist

If "Common dependencies" doesn't cover everything, add these manually:

```
npmjs.org
registry.npmjs.org
pypi.org
files.pythonhosted.org
github.com
raw.githubusercontent.com
supabase.com
*.supabase.co
upstash.com
*.upstash.io
clerk.com
*.clerk.accounts.dev
openai.com
api.openai.com
```

---

## Post-Setup Verification

After the environment initializes, verify everything is working:

```bash
# Check Node.js and pnpm
node --version  # Should be v20+
pnpm --version  # Should be 8.0+

# Check Python and Poetry
python3 --version  # Should be 3.11+
poetry --version

# Verify dependencies installed
cd packages/frontend && pnpm list --depth=0
cd ../backend && poetry show --tree | head -20

# Check environment variables are set
echo $DATABASE_URL
echo $CLERK_SECRET_KEY  # Should show value (if not using secrets)
```

---

## Starting Development Servers

Once setup is complete, you can start the development servers:

### Option 1: Start Both Together (Recommended)

```bash
# From workspace root
pnpm dev
```

This starts:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Option 2: Start Separately

**Terminal 1 - Frontend:**

```bash
cd packages/frontend
pnpm dev
```

**Terminal 2 - Backend:**

```bash
cd packages/backend
poetry run uvicorn main:app --reload
```

---

## Troubleshooting

### Issue: pnpm not found

**Solution:** The automatic setup should install pnpm. If not, run:

```bash
npm install -g pnpm
```

### Issue: Poetry not found

**Solution:** Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: Database connection fails

**Solution:**

- Verify `DATABASE_URL` is set correctly
- For cloud-dev: Ensure Supabase project is active and connection string is correct
- For local: Ensure Docker PostgreSQL is running (if using local mode)

### Issue: Clerk authentication fails

**Solution:**

- Verify `CLERK_SECRET_KEY` and `CLERK_WEBHOOK_SECRET` are set
- Check that keys match your Clerk dashboard
- Ensure `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is set for frontend

### Issue: Ports already in use

**Solution:** Codex may need to configure port forwarding. Check the Codex interface for port configuration options.

---

## Environment-Specific Notes

### Cloud-Dev Mode (Recommended for Codex)

Best for Codex since it doesn't require Docker:

```bash
INFRA_MODE=cloud-dev
DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
REDIS_URL=redis://default:[password]@[host]:6379  # Or use Upstash
```

**Services needed:**

- Supabase account (free tier: 500MB DB)
- Upstash Redis (free tier: 10K commands/day) OR Docker Redis
- Clerk account (free tier: 10K MAU)

### Local Mode

Requires Docker to be available in Codex (may not be supported):

```bash
INFRA_MODE=local
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight
REDIS_URL=redis://localhost:6379
```

**Note:** Check if Codex supports Docker before using local mode.

---

## Quick Reference Checklist

- [ ] Container image: `universal` selected
- [ ] Workspace directory: `/workspace/delight` (or custom)
- [ ] Setup script: `Automatic` enabled
- [ ] Container caching: `On`
- [ ] Agent internet access: `On`
- [ ] Environment variables added (backend + frontend)
- [ ] Secrets added (CLERK_SECRET_KEY, DATABASE_URL, etc.)
- [ ] Domain allowlist configured (if needed)
- [ ] Dependencies installed successfully
- [ ] Development servers start without errors

---

## Additional Resources

- **Full Setup Guide:** See [`docs/SETUP.md`](SETUP.md) for detailed local setup
- **Architecture:** See [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for system design
- **Quick Reference:** See [`docs/dev/QUICK-REFERENCE.md`](dev/QUICK-REFERENCE.md) for commands

---

## Getting Help

If you encounter issues:

1. Check the terminal output during initialization
2. Verify all environment variables are set correctly
3. Ensure secrets are configured (not just environment variables)
4. Check domain allowlist if API calls fail
5. Review the troubleshooting section above

For project-specific issues, check:

- Backend logs: Look for FastAPI startup messages
- Frontend logs: Check Next.js compilation output
- Database: Verify connection string format
