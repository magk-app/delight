# Codex Setup - Quick Reference Card

Copy-paste ready configuration for Codex environment setup.

## ⚠️ Important: One Environment for Monorepo

**You only need ONE Codex environment** for this monorepo (even though it has frontend + backend). Both packages share the same workspace and environment variables.

## Container Configuration

- **Container Image:** `universal`
- **Workspace Directory:** `/workspace/delight`
- **Setup Script:** `Automatic`
- **Container Caching:** `On`
- **Agent Internet Access:** `On`

---

## Environment Variables (Add These)

### Backend Variables

```bash
INFRA_MODE=cloud-dev
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres
CLERK_SECRET_KEY=sk_test_[YOUR-KEY]
CLERK_WEBHOOK_SECRET=whsec_[YOUR-SECRET]
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-[YOUR-KEY]
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Variables

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_[YOUR-KEY]
CLERK_SECRET_KEY=sk_test_[YOUR-KEY]
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Secrets (Add These as Secrets, Not Env Vars)

1. `CLERK_SECRET_KEY` = `sk_test_...`
2. `CLERK_WEBHOOK_SECRET` = `whsec_...`
3. `DATABASE_URL` = `postgresql+asyncpg://...`
4. `OPENAI_API_KEY` = `sk-...`
5. `REDIS_URL` = `redis://...` (if using cloud Redis)

---

## Domain Allowlist

Select: **"Common dependencies"** (recommended)

Or manually add:

```
npmjs.org
pypi.org
github.com
supabase.com
*.supabase.co
clerk.com
*.clerk.accounts.dev
openai.com
api.openai.com
```

---

## After Setup - Verify

```bash
# Check versions
node --version    # Should be v20+
pnpm --version    # Should be 8.0+
python3 --version # Should be 3.11+
poetry --version

# Start development
pnpm dev
```

**Access:**

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Where to Get Keys

- **Clerk:** https://dashboard.clerk.com → Your App → API Keys
- **Supabase:** https://supabase.com → Project Settings → Database
- **OpenAI:** https://platform.openai.com/api-keys
- **Upstash:** https://upstash.com → Redis Database → REST URL

---

**Full Guide:** See [`docs/CODEX_SETUP.md`](CODEX_SETUP.md) for detailed instructions.
