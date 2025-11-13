# Production Deployment Setup Guide

This guide walks you through configuring your Railway backend and Vercel frontend for production deployment.

## Overview

- **Backend**: Railway (`backend-production-d69d.up.railway.app`)
- **Frontend**: Vercel (`www.magk.app`)

## Step 1: Configure Railway Backend

### Environment Variables

Go to your Railway project → **Variables** tab and add/update:

```bash
# Database (from Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres

# Clerk Authentication
CLERK_SECRET_KEY=sk_live_...  # Production key from Clerk dashboard
CLERK_WEBHOOK_SECRET=whsec_...  # Webhook signing secret

# CORS Configuration (CRITICAL - includes your frontend domain)
CORS_ORIGINS=https://www.magk.app,https://magk.app,http://localhost:3000

# Environment
ENVIRONMENT=production
INFRA_MODE=cloud-dev

# AI/LLM
OPENAI_API_KEY=sk-...

# Optional: Redis (if using Upstash)
REDIS_URL=redis://default:[password]@[host]:6379

# Optional: Error Tracking
SENTRY_DSN=https://...
```

### Important Notes

1. **CORS_ORIGINS**: Must include your production frontend URL (`https://www.magk.app`) and any variants (`https://magk.app`). Keep `http://localhost:3000` for local development.

2. **CLERK_SECRET_KEY**: Use production keys (`sk_live_*`) in production, not test keys (`sk_test_*`).

3. **After updating variables**: Railway will automatically redeploy. Wait for deployment to complete.

## Step 2: Configure Vercel Frontend

### Environment Variables

Go to your Vercel project → **Settings** → **Environment Variables** and add/update:

```bash
# Clerk Authentication (Public Key - safe for browser)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...  # Production key

# Clerk Secret Key (for Next.js middleware - server-side only)
CLERK_SECRET_KEY=sk_live_...  # Production key

# API Configuration (CRITICAL - points to Railway backend)
NEXT_PUBLIC_API_URL=https://backend-production-d69d.up.railway.app

# Environment
NODE_ENV=production
```

### Important Notes

1. **NEXT_PUBLIC_API_URL**: Must match your Railway backend URL exactly (no trailing slash).

2. **CLERK Keys**: Use production keys (`pk_live_*` / `sk_live_*`) in production.

3. **Apply to**: Make sure these are set for **Production** environment (and optionally Preview/Development if you want different configs).

4. **After updating variables**: Redeploy your Vercel project (or it will auto-redeploy on next push).

## Step 3: Verify Clerk Configuration

### In Clerk Dashboard

1. **Switch to Production Environment**:
   - Go to https://dashboard.clerk.com
   - Select your app
   - Toggle to **Production** environment

2. **Register Domains**:
   - Settings → **Domains**
   - Add: `www.magk.app` and `magk.app`
   - Complete DNS verification

3. **Configure Allowed Origins**:
   - Settings → **Allowed Origins**
   - Add: `https://www.magk.app` and `https://magk.app`
   - Remove any unused test domains

4. **Set Up Webhooks** (if using):
   - Settings → **Webhooks**
   - Add endpoint: `https://backend-production-d69d.up.railway.app/api/v1/webhooks/clerk`
   - Subscribe to: `user.created`, `user.updated`, `user.deleted`
   - Copy the webhook signing secret to Railway `CLERK_WEBHOOK_SECRET`

## Step 4: Test the Connection

### 1. Test Backend Health

```bash
curl https://backend-production-d69d.up.railway.app/api/v1/health
```

Should return: `{"status": "healthy"}`

### 2. Test CORS from Browser Console

Open browser console on `https://www.magk.app` and run:

```javascript
fetch('https://backend-production-d69d.up.railway.app/api/v1/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

Should return the health check JSON without CORS errors.

### 3. Test Authentication Flow

1. Visit `https://www.magk.app`
2. Sign in with Clerk
3. Try using the companion chat feature
4. Check browser console for any errors

## Step 5: Troubleshooting

### 404 Errors on API Calls

**Symptom**: `Failed to load resource: 404` when calling `/api/v1/companion/chat` or `/api/v1/companion/history`

**Causes**:
1. **CORS not configured**: Check Railway `CORS_ORIGINS` includes your frontend URL
2. **Wrong API URL**: Verify `NEXT_PUBLIC_API_URL` in Vercel matches Railway URL exactly
3. **Backend not deployed**: Check Railway deployment logs

**Fix**:
- Verify `CORS_ORIGINS` in Railway includes `https://www.magk.app`
- Verify `NEXT_PUBLIC_API_URL` in Vercel is `https://backend-production-d69d.up.railway.app` (no trailing slash)
- Redeploy both services after changes

### CORS Errors

**Symptom**: `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Fix**:
- Add your frontend URL to Railway `CORS_ORIGINS` environment variable
- Format: `https://www.magk.app,https://magk.app,http://localhost:3000`
- Redeploy Railway backend

### Authentication Errors

**Symptom**: `401 Unauthorized` or Clerk errors

**Fix**:
- Verify Clerk keys match production environment
- Check Clerk dashboard → Domains includes `www.magk.app`
- Verify `CLERK_SECRET_KEY` in Railway matches Clerk dashboard production secret key

### Environment Variables Not Updating

**Fix**:
- Railway: Variables update automatically trigger redeploy (check deployment status)
- Vercel: After updating variables, trigger a redeploy manually or push a commit
- Both: Wait 1-2 minutes for deployment to complete

## Quick Reference

### Railway Backend URLs
- **Production**: `https://backend-production-d69d.up.railway.app`
- **API Docs**: `https://backend-production-d69d.up.railway.app/docs`
- **Health Check**: `https://backend-production-d69d.up.railway.app/api/v1/health`

### Vercel Frontend URLs
- **Production**: `https://www.magk.app`
- **Alternative**: `https://magk.app` (if configured)

### Key Environment Variables Summary

**Railway (Backend)**:
- `CORS_ORIGINS` = `https://www.magk.app,https://magk.app,http://localhost:3000`
- `CLERK_SECRET_KEY` = `sk_live_...`
- `DATABASE_URL` = Supabase connection string

**Vercel (Frontend)**:
- `NEXT_PUBLIC_API_URL` = `https://backend-production-d69d.up.railway.app`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = `pk_live_...`
- `CLERK_SECRET_KEY` = `sk_live_...`

---

**Last Updated**: After fixing CORS configuration in `main.py` to use environment variables.

