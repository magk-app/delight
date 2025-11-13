# Deployment Guide - Delight Platform

This guide covers deploying the Delight platform to production using Railway (backend) and Vercel (frontend).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Backend Deployment (Railway)](#backend-deployment-railway)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Environment Variables Reference](#environment-variables-reference)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ **Supabase Project** - Database with pgvector extension enabled
- ✅ **Clerk Account** - Authentication provider configured
- ✅ **Railway Account** - For backend deployment (free tier available)
- ✅ **Vercel Account** - For frontend deployment (free tier available)
- ✅ **OpenAI API Key** - For AI companion features (optional for MVP)
- ✅ **GitHub Repository** - Connected to Railway and Vercel

---

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│                 │      │                  │      │                 │
│  Vercel         │─────▶│  Railway         │─────▶│  Supabase       │
│  (Frontend)     │ HTTPS │  (Backend API)   │ SQL  │  (PostgreSQL)   │
│  Next.js 15     │      │  FastAPI         │      │  + pgvector     │
│                 │      │                  │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│  Clerk          │      │  OpenAI API      │
│  (Auth)         │      │  (LLM/Embeddings)│
└─────────────────┘      └──────────────────┘
```

**Key Points:**
- Frontend (Vercel) calls backend API via HTTPS
- Backend (Railway) connects to Supabase PostgreSQL
- Clerk handles all authentication (OAuth, sessions, webhooks)
- OpenAI provides AI companion features

---

## Backend Deployment (Railway)

### Step 1: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `delight` repository
4. Railway will auto-detect the monorepo structure

### Step 2: Configure Service Settings

**Important:** Railway needs to know this is a monorepo with backend in `packages/backend`.

1. Click on your Railway service
2. Go to **Settings** tab
3. Configure the following:

| Setting | Value | Notes |
|---------|-------|-------|
| **Root Directory** | `packages/backend` | Critical for monorepo |
| **Build Command** | Auto-detected (Nixpacks) | Uses Poetry |
| **Start Command** | `python -m uvicorn main:app --host 0.0.0.0 --port $PORT` | Must bind to Railway's $PORT |
| **Health Check Path** | `/api/v1/health` | Railway pings this endpoint |
| **Restart Policy** | On Failure (max 10 retries) | Auto-restart on crashes |

### Step 3: Set Environment Variables

Go to **Variables** tab and add these (all required unless marked optional):

#### Required Variables

```bash
# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres

# Authentication (Clerk)
CLERK_SECRET_KEY=sk_live_...
CLERK_WEBHOOK_SECRET=whsec_...

# CORS Configuration (CRITICAL!)
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://www.your-domain.com
```

#### Optional Variables

```bash
# OpenAI (for AI features - Story 2.3+)
OPENAI_API_KEY=sk-proj-...

# Redis (for background jobs - future)
REDIS_URL=redis://default:[PASSWORD]@[HOST]:6379

# Monitoring (optional)
SENTRY_DSN=https://...

# Environment
ENVIRONMENT=production
```

### Step 4: Get Values for Environment Variables

#### DATABASE_URL (Supabase)

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Project Settings** → **Database** → **Connection String**
4. Copy the **Connection string** (URI format)
5. **Important:** Change `postgresql://` to `postgresql+asyncpg://` for async support
6. Replace `[YOUR-PASSWORD]` with your actual database password

Example:
```
postgresql+asyncpg://postgres.xxxxx:secretpassword@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

#### CLERK_SECRET_KEY (Clerk)

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your application
3. Go to **API Keys** (left sidebar)
4. Copy the **Secret Key** (starts with `sk_live_...` for production or `sk_test_...` for development)
5. **Security:** Never use test keys in production!

#### CLERK_WEBHOOK_SECRET (Clerk)

1. In Clerk Dashboard, go to **Webhooks** (left sidebar)
2. Click **Add Endpoint**
3. Set URL to: `https://your-railway-url.up.railway.app/api/v1/webhooks/clerk`
4. Select events: `user.created`, `user.updated`, `user.deleted`
5. Click **Create**
6. Copy the **Signing Secret** (starts with `whsec_...`)

#### CORS_ORIGINS (Frontend URLs)

Format: Comma-separated list of allowed frontend URLs (no trailing slashes!)

**Production Example:**
```
CORS_ORIGINS=https://delight.vercel.app,https://www.delight.ai,https://delight-preview.vercel.app
```

**Include:**
- ✅ Production domain
- ✅ www subdomain (if using)
- ✅ Vercel preview deployments (for testing PRs)
- ✅ Localhost (for local development testing against production backend)

**Do NOT include:**
- ❌ Trailing slashes (`https://domain.com/` - wrong)
- ❌ Wildcards (`https://*.vercel.app` - not supported by FastAPI CORS)

### Step 5: Deploy

1. Railway auto-deploys on push to main branch
2. Or click **Deploy** button manually
3. Wait 5-10 minutes for initial deployment (PyTorch + dependencies are large)
4. Check **Deployments** tab for build logs

### Step 6: Verify Deployment

```bash
# Test health endpoint
curl https://your-app.up.railway.app/api/v1/health

# Expected response:
{"status": "healthy"}

# Test API docs (should show Swagger UI)
open https://your-app.up.railway.app/docs
```

---

## Frontend Deployment (Vercel)

### Step 1: Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Vercel auto-detects Next.js and monorepo structure

### Step 2: Configure Project Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Framework Preset** | Next.js | Auto-detected |
| **Root Directory** | `packages/frontend` | Critical for monorepo |
| **Build Command** | `npm run build` | Default is fine |
| **Output Directory** | `.next` | Default is fine |
| **Install Command** | `npm install` | Uses pnpm workspace |

### Step 3: Set Environment Variables

Go to **Settings** → **Environment Variables** and add:

#### Production Environment

```bash
# Clerk Authentication (PUBLIC - safe for browser)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...

# Clerk Authentication (SECRET - server-side only!)
CLERK_SECRET_KEY=sk_live_...

# Backend API URL (NO TRAILING SLASH!)
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

#### Preview Environment (optional)

If you want preview deployments to work:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=https://your-railway-staging.up.railway.app
```

### Step 4: Get Values for Environment Variables

#### NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

1. Go to [Clerk Dashboard](https://dashboard.clerk.com) → **API Keys**
2. Copy **Publishable Key** (starts with `pk_live_...` or `pk_test_...`)
3. **Note:** This is public and safe to expose in browser JavaScript

#### CLERK_SECRET_KEY

1. Same as backend - copy from Clerk Dashboard → **API Keys**
2. **Security:** This is used by Next.js middleware (server-side only)
3. Must match the environment (production `sk_live_` or test `sk_test_`)

#### NEXT_PUBLIC_API_URL

1. Get your Railway backend URL from Railway Dashboard
2. Format: `https://your-app.up.railway.app` (no trailing slash!)
3. **Important:** Do NOT include `/api/v1` - the frontend adds this automatically

### Step 5: Deploy

1. Click **Deploy** or push to main branch
2. Vercel builds and deploys in ~2-3 minutes
3. Check **Deployments** tab for build logs

### Step 6: Update Backend CORS

**Critical:** After deploying frontend, you must add the Vercel URL to backend CORS!

1. Go back to Railway Dashboard → Your backend service → **Variables**
2. Update `CORS_ORIGINS` to include your Vercel domain:

```bash
CORS_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com,http://localhost:3000
```

3. Railway will auto-redeploy with new CORS settings
4. Wait 2-3 minutes for deployment

---

## Post-Deployment Verification

### 1. Backend Health Check

```bash
curl https://your-railway-app.up.railway.app/api/v1/health
```

**Expected:** `{"status": "healthy"}`

**Troubleshooting:**
- ❌ **502 Bad Gateway**: Backend crashed - check Railway logs
- ❌ **404 Not Found**: Wrong URL or path
- ❌ **Timeout**: Backend is slow to start (check Railway logs)

### 2. Frontend Health Check

Visit: `https://your-vercel-app.vercel.app`

**Expected:** Homepage loads, no console errors

**Troubleshooting:**
- ❌ **500 Error**: Check Vercel function logs
- ❌ **CORS Errors**: Backend CORS_ORIGINS not configured correctly
- ❌ **API 404 Errors**: NEXT_PUBLIC_API_URL is wrong

### 3. Authentication Flow Test

1. Click **Sign Up** button
2. Create account with email/password
3. Verify redirect to dashboard
4. Check Railway logs for webhook delivery: `POST /api/v1/webhooks/clerk`

**Expected:** User created in database

**Troubleshooting:**
- ❌ **Clerk error**: Check Clerk environment (test vs live)
- ❌ **Webhook not received**: Check Clerk webhook configuration
- ❌ **Database error**: Check DATABASE_URL and Supabase connection

### 4. API Integration Test

Open browser console on frontend and check for:

```javascript
// Network tab should show:
GET https://your-railway-app.up.railway.app/api/v1/users/me → 200 OK

// No CORS errors like:
❌ Access to fetch blocked by CORS policy
```

---

## Troubleshooting

### Backend 502 Errors

**Symptoms:** Railway shows "deployed" but API returns 502

**Causes:**
1. Missing required environment variables
2. Database connection failure
3. Backend crash on startup
4. Out of memory (PyTorch + dependencies are large)

**Solutions:**

```bash
# 1. Check Railway logs
# Go to Railway → Deployments → View Logs
# Look for errors like:
❌ ValueError: DATABASE_URL is required
❌ ConnectionRefusedError: Cannot connect to database
❌ SIGKILL: Out of memory

# 2. Verify all required env vars are set
DATABASE_URL          ✅ Set and correct format?
CLERK_SECRET_KEY      ✅ Set and starts with sk_live_ or sk_test_?
CLERK_WEBHOOK_SECRET  ✅ Set and starts with whsec_?

# 3. Test database connection from Railway CLI
railway run python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())"

# 4. Check memory usage
# Railway free tier: 512MB RAM
# PyTorch alone: ~500MB
# Solution: Upgrade to Hobby plan ($5/mo for 1GB RAM)
```

### Frontend CORS Errors

**Symptoms:** Browser console shows:
```
Access to fetch at 'https://backend.railway.app/api/v1/...'
from origin 'https://frontend.vercel.app' has been blocked by CORS policy
```

**Causes:**
1. Backend `CORS_ORIGINS` doesn't include frontend URL
2. Frontend URL changed (redeployment)
3. CORS_ORIGINS has trailing slashes or typos

**Solutions:**

```bash
# 1. Check backend CORS_ORIGINS in Railway
# Must include exact frontend URL:
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# 2. Common mistakes:
❌ CORS_ORIGINS=https://your-app.vercel.app/  # Trailing slash
❌ CORS_ORIGINS=http://your-app.vercel.app    # HTTP instead of HTTPS
❌ CORS_ORIGINS=*.vercel.app                   # Wildcards not supported

# 3. After fixing, redeploy backend
# Railway auto-redeploys when you change env vars

# 4. Verify CORS is working
curl -H "Origin: https://your-app.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://your-railway-app.up.railway.app/api/v1/health
```

### OpenAI API Errors

**Symptoms:** Companion chat features return errors

**Causes:**
1. `OPENAI_API_KEY` not set in Railway
2. API key invalid or quota exceeded
3. Backend trying to use OpenAI before Story 2.3 is implemented

**Solutions:**

```bash
# 1. Check if OPENAI_API_KEY is set in Railway
# Go to Railway → Variables → Check OPENAI_API_KEY

# 2. Verify API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Expected: List of models
# If error: Key is invalid or quota exceeded

# 3. Check OpenAI usage
# Go to https://platform.openai.com/usage
# Verify you have remaining credits
```

### Database Connection Issues

**Symptoms:**
- Backend logs show `ConnectionRefusedError`
- Health check endpoint times out
- 502 errors on API calls

**Causes:**
1. `DATABASE_URL` format is incorrect
2. Supabase project paused (free tier inactivity)
3. Database password has special characters not URL-encoded

**Solutions:**

```bash
# 1. Verify DATABASE_URL format
# Correct: postgresql+asyncpg://postgres.xxx:[PASSWORD]@host:5432/postgres
# Wrong:   postgresql://...  (missing +asyncpg)
# Wrong:   postgres://...     (postgres not postgresql)

# 2. Check Supabase project status
# Go to Supabase Dashboard
# If project is paused, click "Restore" (free tier auto-pauses after 7 days inactivity)

# 3. URL-encode special characters in password
# If password has special chars like @, !, #:
# Use online URL encoder: https://www.urlencoder.org/
# Example: p@ssw0rd! → p%40ssw0rd%21

# 4. Test connection from Railway shell
railway shell
python -c "
from sqlalchemy import create_engine
engine = create_engine('YOUR_DATABASE_URL')
with engine.connect() as conn:
    print('✅ Connected!')
"
```

### Clerk Webhook Not Working

**Symptoms:**
- Users sign up in Clerk but don't appear in database
- Backend logs don't show webhook requests
- 401/403 errors on webhook endpoint

**Causes:**
1. Webhook URL is incorrect
2. Webhook secret doesn't match
3. Webhook events not configured

**Solutions:**

```bash
# 1. Verify webhook configuration in Clerk
# Go to Clerk Dashboard → Webhooks
# Check endpoint URL: https://your-railway-app.up.railway.app/api/v1/webhooks/clerk
# Check events selected: user.created, user.updated, user.deleted

# 2. Test webhook manually
# Clerk Dashboard → Webhooks → Your endpoint → Test
# Check Railway logs for incoming request

# 3. Verify webhook secret matches
# Clerk shows: whsec_abc123...
# Railway CLERK_WEBHOOK_SECRET should be: whsec_abc123...

# 4. Check Railway logs for webhook errors
# Go to Railway → Deployments → Logs
# Filter for: /api/v1/webhooks/clerk
# Look for signature verification errors
```

---

## Environment Variables Reference

### Backend (Railway)

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `DATABASE_URL` | ✅ Yes | `postgresql+asyncpg://postgres:pass@host:5432/db` | Must use `+asyncpg` driver |
| `CLERK_SECRET_KEY` | ✅ Yes | `sk_live_abc123...` | Backend auth verification |
| `CLERK_WEBHOOK_SECRET` | ✅ Yes | `whsec_abc123...` | Webhook signature validation |
| `CORS_ORIGINS` | ✅ Yes | `https://app.vercel.app,http://localhost:3000` | Comma-separated, no trailing slashes |
| `OPENAI_API_KEY` | ❌ No | `sk-proj-abc123...` | Required for Story 2.3+ (AI features) |
| `REDIS_URL` | ❌ No | `redis://default:pass@host:6379` | Required for background jobs (future) |
| `SENTRY_DSN` | ❌ No | `https://abc@sentry.io/123` | Error monitoring (optional) |
| `ENVIRONMENT` | ❌ No | `production` | Defaults to `development` |

### Frontend (Vercel)

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | ✅ Yes | `pk_live_abc123...` | Public key (safe for browser) |
| `CLERK_SECRET_KEY` | ✅ Yes | `sk_live_abc123...` | Server-side middleware auth |
| `NEXT_PUBLIC_API_URL` | ✅ Yes | `https://app.railway.app` | Backend URL (no trailing slash!) |

### Security Notes

- ✅ **NEXT_PUBLIC_** variables are exposed to browser (only use for public keys)
- ❌ **Never** put secret keys in `NEXT_PUBLIC_` variables
- ✅ **Rotate secrets** if accidentally exposed (Clerk, OpenAI, Database)
- ✅ **Use different keys** for preview/production environments
- ❌ **Never commit** `.env` files to Git (use `.env.example` instead)

---

## Production Checklist

Before launching to users:

### Backend (Railway)

- [ ] All required environment variables set
- [ ] `ENVIRONMENT=production`
- [ ] Health check endpoint returns 200
- [ ] Database migrations applied: `railway run alembic upgrade head`
- [ ] Clerk webhook receives and processes events
- [ ] API docs accessible: `/docs` endpoint
- [ ] CORS includes all production frontend URLs
- [ ] Sentry error tracking configured (recommended)
- [ ] Railway plan supports expected traffic (upgrade from free if needed)

### Frontend (Vercel)

- [ ] All required environment variables set
- [ ] `NEXT_PUBLIC_API_URL` points to production backend
- [ ] Custom domain configured (if applicable)
- [ ] HTTPS enforced (Vercel default)
- [ ] Authentication flow works end-to-end
- [ ] API calls succeed (no CORS errors)
- [ ] Clerk production keys used (not test keys)
- [ ] Analytics configured (Vercel Analytics, Google Analytics, etc.)

### Clerk

- [ ] Production instance created (not using test/development)
- [ ] OAuth providers configured (Google, GitHub, etc.)
- [ ] Email templates customized
- [ ] User metadata schema configured
- [ ] Webhook endpoint verified and active
- [ ] Production API keys distributed to Railway + Vercel

### Supabase

- [ ] Production project created (not using test/development)
- [ ] Database backups enabled (automatic on paid plans)
- [ ] pgvector extension enabled: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Connection pooling configured (recommended for production)
- [ ] Database password is strong and URL-encoded

---

## Deployment Workflow

### Initial Deployment

1. Set up Supabase project → Get `DATABASE_URL`
2. Set up Clerk app → Get `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET`
3. Deploy backend to Railway → Get backend URL
4. Configure Clerk webhook to point to Railway URL
5. Deploy frontend to Vercel → Get frontend URL
6. Update Railway `CORS_ORIGINS` with Vercel URL
7. Test end-to-end: Sign up → Check database → Check webhooks

### Continuous Deployment

**Automatic on every push to main:**
1. Push code to GitHub main branch
2. Railway auto-builds and deploys backend
3. Vercel auto-builds and deploys frontend
4. Both deployments complete in ~5 minutes
5. Verify with health checks

**Manual deployment:**
```bash
# Railway
railway up  # From packages/backend directory

# Vercel
vercel --prod  # From packages/frontend directory
```

---

## Cost Estimation

**Free Tier (MVP):**
- Railway: $0 (500 hours/month, 512MB RAM, 1GB storage)
- Vercel: $0 (100GB bandwidth, unlimited sites)
- Supabase: $0 (500MB database, 2GB bandwidth)
- Clerk: $0 (10,000 MAU)
- OpenAI: ~$5-10/month (GPT-4o-mini for companion chat)

**Total: ~$5-10/month** (only OpenAI API usage)

**Production (1000 users):**
- Railway Hobby: $5/month (1GB RAM, better uptime)
- Vercel Pro: $20/month (improved analytics, speed)
- Supabase Pro: $25/month (8GB database, daily backups)
- Clerk Pro: $25/month (10,000+ MAU)
- OpenAI: ~$50-100/month (increased API usage)

**Total: ~$125-175/month** for 1000 active users

---

## Next Steps

After successful deployment:

1. **Set up monitoring** - Configure Sentry for error tracking
2. **Enable analytics** - Vercel Analytics, Mixpanel, or PostHog
3. **Configure custom domain** - Point your domain to Vercel
4. **Set up staging environment** - Separate Railway/Vercel projects for testing
5. **Database backups** - Enable automatic backups in Supabase (Pro plan)
6. **CI/CD improvements** - Add automated tests before deployment
7. **Performance monitoring** - Railway metrics, Vercel speed insights

---

## Support Resources

**Railway:**
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Vercel:**
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

**Clerk:**
- Dashboard: https://dashboard.clerk.com
- Docs: https://clerk.com/docs
- Discord: https://clerk.com/discord

**Supabase:**
- Dashboard: https://supabase.com/dashboard
- Docs: https://supabase.com/docs
- Discord: https://discord.supabase.com

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
**Status:** Production-Ready ✅
