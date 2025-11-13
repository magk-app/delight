# Railway Deployment Checklist

## Problem Diagnosis

You're seeing **404 errors** on companion endpoints and sometimes **502 errors** when deploying to Railway. This checklist will help you identify and fix the issue.

## Step 1: Access Debug Endpoint

Once your Railway deployment starts (even if it's failing), try accessing:

```
https://YOUR-RAILWAY-URL/api/v1/health/debug
```

This will show you:
- ✅ Which environment variables are set
- ✅ Which Python packages loaded successfully
- ✅ Which API routes are registered
- ✅ Database connectivity status

**Example:** `https://backend-production-d69d.up.railway.app/api/v1/health/debug`

## Step 2: Environment Variables Checklist

Go to your Railway project → Variables tab and verify ALL of these are set:

### Required Variables

- [ ] **DATABASE_URL** - Supabase connection string
  ```
  postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
  ```

- [ ] **CLERK_SECRET_KEY** - From Clerk Dashboard → API Keys
  ```
  sk_test_...
  ```

- [ ] **CLERK_WEBHOOK_SECRET** - From Clerk Dashboard → Webhooks → Signing Secret
  ```
  whsec_...
  ```

- [ ] **CLERK_JWKS_URL** - From Clerk Dashboard → API Keys → Advanced
  ```
  https://YOUR-INSTANCE.clerk.accounts.dev/.well-known/jwks.json
  ```
  **⚠️ CRITICAL:** Without this, JWT verification will fail with 404

- [ ] **OPENAI_API_KEY** - From OpenAI Platform → API Keys
  ```
  sk-proj-...
  ```
  **⚠️ CRITICAL:** Without this, companion endpoints won't load (404s)

- [ ] **CORS_ORIGINS** - Your Vercel frontend URL (comma-separated)
  ```
  http://localhost:3000,https://delight-git-2-5-companion-chat-thejackluos-projects.vercel.app,https://YOUR-APP.vercel.app
  ```
  **⚠️ CRITICAL:** Without your Vercel URL, all API calls will be blocked by CORS

### Optional Variables

- [ ] **REDIS_URL** - Redis connection string (for background jobs)
  ```
  redis://default:[password]@[host]:6379
  ```

- [ ] **SENTRY_DSN** - Sentry error tracking (optional)

- [ ] **ENVIRONMENT** - Set to `production`

## Step 3: Verify Build Process

Check Railway build logs for these indicators:

### ✅ Good Signs

```
Installing dependencies from lock file
...
  - Installing openai (2.7.2)
  - Installing langchain (0.1.x)
...
```

### ❌ Bad Signs

```
ModuleNotFoundError: No module named 'openai'
PyJWKClientConnectionError: HTTP Error 404: Not Found
```

If you see `ModuleNotFoundError`, the dependency installation failed. Try:
1. Regenerate `poetry.lock`: `poetry lock --no-update`
2. Commit and push the updated lock file
3. Redeploy on Railway

## Step 4: Check Startup Logs

Railway startup logs should show:

### ✅ Good Startup

```
✅ Database connection established
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### ❌ Bad Startup

```
ModuleNotFoundError: No module named 'openai'
⚠️  Database connection failed: ...
PyJWKClientConnectionError: ...
```

## Step 5: Test Endpoints

After deployment, test these endpoints in order:

1. **Root endpoint** (should always work):
   ```
   curl https://YOUR-RAILWAY-URL/
   ```
   Expected: `{"name": "Delight API", "version": "0.1.0", ...}`

2. **Health check** (tests database):
   ```
   curl https://YOUR-RAILWAY-URL/api/v1/health
   ```
   Expected: `{"status": "healthy", "database": "connected", ...}`

3. **Debug endpoint** (shows configuration):
   ```
   curl https://YOUR-RAILWAY-URL/api/v1/health/debug
   ```
   Expected: Long JSON with imports, env_vars, routes

4. **Companion endpoints** (requires auth):
   ```
   curl https://YOUR-RAILWAY-URL/api/v1/companion/history \
     -H "Authorization: Bearer YOUR_CLERK_TOKEN"
   ```

## Step 6: Common Issues and Fixes

### Issue: 404 on all companion endpoints

**Cause:** `companion` module failed to import, likely due to missing `openai` package

**Fix:**
1. Check Railway build logs for `ModuleNotFoundError`
2. Verify `poetry.lock` includes `openai = "2.7.2"`
3. If missing, run locally: `poetry lock --no-update && poetry install`
4. Commit and push the updated `poetry.lock`

### Issue: JWT verification 404 error

**Cause:** `CLERK_JWKS_URL` not set or incorrect

**Fix:**
1. Go to Clerk Dashboard → API Keys → Advanced
2. Find "JWKS endpoint" URL
3. Add to Railway Variables:
   ```
   CLERK_JWKS_URL=https://YOUR-INSTANCE.clerk.accounts.dev/.well-known/jwks.json
   ```
4. Redeploy

### Issue: CORS errors (blocked by CORS policy)

**Cause:** `CORS_ORIGINS` doesn't include your Vercel URL

**Fix:**
1. Get your Vercel deployment URL (e.g., `https://delight-git-2-5-companion-chat-thejackluos-projects.vercel.app`)
2. Add to Railway Variables:
   ```
   CORS_ORIGINS=http://localhost:3000,https://YOUR-VERCEL-URL,https://YOUR-PRODUCTION-URL
   ```
3. Redeploy

### Issue: 502 Bad Gateway

**Cause:** App crashed during startup or took too long to respond

**Fix:**
1. Check Railway logs for Python traceback
2. Common causes:
   - Database connection failed (check `DATABASE_URL`)
   - Missing required env variable (check `OPENAI_API_KEY`, `CLERK_SECRET_KEY`)
   - Import error (check build logs)
3. Use `/api/v1/health/debug` to diagnose

### Issue: Railway builds but doesn't start

**Cause:** `CMD` in Dockerfile might be wrong, or port binding issue

**Fix:**
1. Verify `Dockerfile` has:
   ```dockerfile
   CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}
   ```
2. Railway automatically sets `PORT` environment variable
3. Check Railway settings → Deployment → Start Command (should be empty if using Dockerfile)

## Step 7: Verify Frontend Connection

Once backend is working, test from your Vercel frontend:

1. Open browser console on your Vercel app
2. Check Network tab for API calls
3. Look for:
   - **200 OK** responses = Good!
   - **404 Not Found** = Companion routes not registered (missing OpenAI)
   - **401 Unauthorized** = Clerk auth issue
   - **403 Forbidden** = CORS issue or Clerk token invalid
   - **502 Bad Gateway** = Backend crashed

## Quick Diagnostic Command

If Railway is deployed, run this in your browser console:

```javascript
fetch('https://YOUR-RAILWAY-URL/api/v1/health/debug')
  .then(r => r.json())
  .then(data => {
    console.log('=== ENVIRONMENT ===');
    console.log(data.env_vars);
    console.log('=== IMPORTS ===');
    console.log(data.imports);
    console.log('=== ROUTES ===');
    console.log(data.routes);
  });
```

This will show you exactly what's wrong.

## Emergency Fallback

If nothing works, try these nuclear options:

1. **Clear Railway cache:**
   - Railway Dashboard → Deployment → Settings → Reset to Clean State
   - Redeploy

2. **Regenerate poetry.lock:**
   ```bash
   cd packages/backend
   rm poetry.lock
   poetry lock
   git add poetry.lock
   git commit -m "fix: regenerate poetry.lock"
   git push
   ```

3. **Manual requirements.txt approach:**
   ```bash
   cd packages/backend
   poetry export -f requirements.txt --without-hashes --without dev -o requirements.txt
   git add requirements.txt
   git commit -m "fix: add requirements.txt for Railway"
   git push
   ```
   Update Dockerfile to use requirements.txt directly if poetry export fails.

## Success Criteria

Your deployment is working when:

- ✅ `/api/v1/health` returns `{"status": "healthy"}`
- ✅ `/api/v1/health/debug` shows all env vars with ✅
- ✅ `/api/v1/health/debug` shows `"companion": "✅ loaded (3 routes)"`
- ✅ Frontend can send messages to `/api/v1/companion/chat`
- ✅ SSE streaming works on `/api/v1/companion/stream/{id}`
- ✅ No CORS errors in browser console

## Next Steps After Successful Deployment

1. **Set up monitoring:** Configure Sentry DSN for error tracking
2. **Add health checks:** Configure Railway health check path to `/api/v1/health`
3. **Set up domains:** Add custom domain in Railway settings
4. **Configure auto-deploy:** Set up GitHub integration for auto-deployment

---

**Need Help?**

If you're still stuck after following this checklist:
1. Share the output of `/api/v1/health/debug`
2. Share Railway startup logs
3. Share Railway build logs
4. Share browser console errors when calling API
