# Railway Deployment - Experimental Web Server

## Summary

All Railway configuration files have been created in this directory (`packages/backend/experiments/web`) to deploy the experimental web server to Railway.

## Files Created

1. **`railway.json`** - Railway deployment configuration
2. **`Procfile`** - Process definition for Railway
3. **`nixpacks.toml`** - Nixpacks build configuration
4. **`runtime.txt`** - Python version specification (3.11)
5. **`railway_start.sh`** - Optional startup script
6. **`RAILWAY_DEPLOYMENT.md`** - Complete deployment guide

## Changes Made to `dashboard_server.py`

- ✅ Updated to read `PORT` from environment (Railway requirement)
- ✅ Updated to read `HOST` from environment (defaults to 0.0.0.0)
- ✅ CORS configuration now reads from `CORS_ORIGINS` environment variable
- ✅ Automatically adds Railway domain to CORS if `RAILWAY_PUBLIC_DOMAIN` is set

## Quick Start

1. **In Railway Dashboard:**

   - Set **Root Directory** to: `packages/backend/experiments/web`
   - Add PostgreSQL service (if using database)
   - Configure environment variables (see `RAILWAY_DEPLOYMENT.md`)

2. **Deploy:**
   - Railway will automatically detect and use the configuration files
   - The server will start on the port Railway provides

## Environment Variables Needed

### Required

- `DATABASE_URL` - PostgreSQL connection (auto-provided if you add PostgreSQL service)
- `PORT` - Server port (auto-set by Railway)

### Recommended

- `CORS_ORIGINS` - Comma-separated allowed origins
- `OPENAI_API_KEY` - For AI features
- `CLERK_SECRET_KEY` - For authentication

## Testing Locally

```bash
# Set environment variables
export PORT=8001
export DATABASE_URL=postgresql+asyncpg://...

# Run the server
cd packages/backend
poetry run python -m experiments.web.dashboard_server
```

## Health Check

Once deployed, check health at:

```
https://your-railway-app.railway.app/health
```

## Notes

- All paths in configuration files are relative to `packages/backend/experiments/web`
- The build process navigates to `packages/backend` to run Poetry
- The server automatically handles Railway's PORT environment variable
- CORS is configured to work with Railway domains automatically
