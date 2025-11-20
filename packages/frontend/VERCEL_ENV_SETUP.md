# Vercel Environment Variables Setup

This guide explains how to configure your Vercel frontend to connect to different backends in different environments.

## Overview

Your Delight app has **two separate backends**:

1. **Main Backend** (port 8000) - Production FastAPI backend

   - Used by: Main app features, dashboard, missions, etc.
   - Environment variable: `NEXT_PUBLIC_API_URL`

2. **Experimental Backend** (port 8001 / Railway) - Experimental web server
   - Used by: `/experimental` page, experimental chat interface
   - Environment variable: `NEXT_PUBLIC_EXPERIMENTAL_API_URL`

## Environment Variables

### Required Variables

Set these in your Vercel project settings:

#### For All Environments

```env
# Clerk Authentication (required)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...  # Production key
# or pk_test_... for preview/development

# Main Backend API (required)
NEXT_PUBLIC_API_URL=https://your-main-backend.railway.app
# or http://localhost:8000 for local dev

# Experimental Backend API (required for /experimental page)
NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://your-experimental-backend.railway.app
# or http://localhost:8001 for local dev
```

#### Optional (Server-Side Only)

```env
# Clerk Secret Key (for server-side operations)
CLERK_SECRET_KEY=sk_live_...  # Only needed for server-side API routes
```

## Setting Up in Vercel Dashboard

### Step 1: Go to Project Settings

1. Open your Vercel project dashboard
2. Click **Settings** → **Environment Variables**

### Step 2: Add Environment Variables

For each variable, you can set it for:

- **Production** - Your production domain
- **Preview** - All preview deployments (PRs, branches)
- **Development** - Local development (via Vercel CLI)

#### Example Configuration:

| Variable                            | Production                         | Preview                            | Development             |
| ----------------------------------- | ---------------------------------- | ---------------------------------- | ----------------------- |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_...`                      | `pk_test_...`                      | `pk_test_...`           |
| `NEXT_PUBLIC_API_URL`               | `https://main-backend.railway.app` | `https://main-backend.railway.app` | `http://localhost:8000` |
| `NEXT_PUBLIC_EXPERIMENTAL_API_URL`  | `https://experimental.railway.app` | `https://experimental.railway.app` | `http://localhost:8001` |

### Step 3: Deploy

After adding variables:

- **New deployments** will automatically use the new variables
- **Existing deployments** need to be redeployed to pick up changes

## Local Development Setup

Create `.env.local` in `packages/frontend/`:

```env
# Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

# Main Backend (local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Experimental Backend (local)
NEXT_PUBLIC_EXPERIMENTAL_API_URL=http://localhost:8001

# Optional: Server-side only
CLERK_SECRET_KEY=sk_test_...
```

## How It Works

### Main Backend (Port 8000)

Used by:

- Main API client (`src/lib/api/client.ts`)
- Dashboard, missions, user features
- Standard app functionality

Configuration:

- Environment variable: `NEXT_PUBLIC_API_URL`
- Default: `http://localhost:8000`

### Experimental Backend (Port 8001 / Railway)

Used by:

- Experimental page (`/experimental`)
- Experimental chat interface
- Memory visualization
- Analytics dashboard

Configuration:

- Environment variable: `NEXT_PUBLIC_EXPERIMENTAL_API_URL`
- Default: `http://localhost:8001`
- Production: Your Railway experimental backend URL

## Example: Different URLs for Different Environments

### Production (Vercel Production)

```env
NEXT_PUBLIC_API_URL=https://delight-api-production.railway.app
NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://delight-experimental.railway.app
```

### Preview/Staging (Vercel Preview)

```env
NEXT_PUBLIC_API_URL=https://delight-api-staging.railway.app
NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://delight-experimental-staging.railway.app
```

### Local Development

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_EXPERIMENTAL_API_URL=http://localhost:8001
```

## Testing

### Verify Environment Variables

1. **In Browser Console** (client-side):

   ```javascript
   console.log("Main API:", process.env.NEXT_PUBLIC_API_URL);
   console.log(
     "Experimental API:",
     process.env.NEXT_PUBLIC_EXPERIMENTAL_API_URL
   );
   ```

2. **In Server Component** (server-side):
   ```typescript
   // This will only work in server components
   console.log("Main API:", process.env.NEXT_PUBLIC_API_URL);
   console.log(
     "Experimental API:",
     process.env.NEXT_PUBLIC_EXPERIMENTAL_API_URL
   );
   ```

### Check API Connections

1. **Main Backend**: Visit `/dashboard` - should connect to main backend
2. **Experimental Backend**: Visit `/experimental` - should connect to experimental backend

## Troubleshooting

### "Cannot connect to backend" errors

1. **Check environment variables are set**:

   - Vercel Dashboard → Settings → Environment Variables
   - Make sure variables are set for the correct environment (Production/Preview)

2. **Verify URLs are correct**:

   - Check Railway dashboard for your backend URLs
   - Make sure URLs include `https://` (not `http://`) for production

3. **Check CORS settings**:

   - Make sure your Railway backends allow your Vercel domain
   - Add your Vercel domain to `CORS_ORIGINS` in Railway

4. **Redeploy after changes**:
   - Environment variable changes require a new deployment
   - Go to Vercel Dashboard → Deployments → Redeploy

### Experimental page not working

1. **Check `NEXT_PUBLIC_EXPERIMENTAL_API_URL` is set**:

   ```bash
   # In Vercel, check environment variables
   # Should be: https://your-experimental-backend.railway.app
   ```

2. **Verify Railway backend is running**:

   - Check Railway dashboard
   - Test health endpoint: `https://your-experimental-backend.railway.app/health`

3. **Check browser console**:
   - Look for CORS errors
   - Check network tab for failed requests

## Security Notes

- ✅ `NEXT_PUBLIC_*` variables are **safe** to expose in the browser
- ❌ Never use `NEXT_PUBLIC_*` prefix for secrets (API keys, tokens)
- ✅ Use non-prefixed variables for server-side secrets (e.g., `CLERK_SECRET_KEY`)

## Quick Reference

| Variable                            | Purpose                  | Example                            |
| ----------------------------------- | ------------------------ | ---------------------------------- |
| `NEXT_PUBLIC_API_URL`               | Main backend API         | `https://api.delight.app`          |
| `NEXT_PUBLIC_EXPERIMENTAL_API_URL`  | Experimental backend     | `https://experimental.delight.app` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk auth (public)      | `pk_live_...`                      |
| `CLERK_SECRET_KEY`                  | Clerk auth (server-only) | `sk_live_...`                      |
