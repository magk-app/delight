# Railway Deployment Guide for Experimental Web Server

This guide explains how to deploy the experimental web server to Railway.

## Prerequisites

- Railway account (sign up at https://railway.app)
- Railway CLI installed (optional, for local testing)
- GitHub repository connected to Railway

## Quick Deploy

1. **Connect Repository to Railway**

   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the configuration

2. **Set Root Directory**

   - In Railway project settings, set the **Root Directory** to: `packages/backend/experiments/web`
   - This tells Railway where to find the deployment files

3. **Configure Environment Variables**

   - Go to your Railway service → Variables tab
   - Add the following required variables:
     ```
     DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
     PORT=8001  # Railway will auto-set this, but you can override
     CORS_ORIGINS=https://your-frontend-domain.com,https://your-railway-domain.railway.app
     OPENAI_API_KEY=sk-...  # If using AI features
     CLERK_SECRET_KEY=sk_test_...  # If using authentication
     ```

4. **Add PostgreSQL Service (if needed)**

   - In Railway, click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` variable
   - The app will use this automatically

5. **Deploy**
   - Railway will automatically build and deploy when you push to your main branch
   - Or click "Deploy" in the Railway dashboard

## Configuration Files

This directory contains the following Railway configuration files:

- **`railway.json`** - Railway deployment configuration
- **`Procfile`** - Process definition for Railway
- **`nixpacks.toml`** - Nixpacks build configuration
- **`runtime.txt`** - Python version specification
- **`railway_start.sh`** - Startup script (optional, for custom startup logic)

## Environment Variables

### Required

- `DATABASE_URL` - PostgreSQL connection string (Railway auto-provides if you add PostgreSQL service)
- `PORT` - Server port (Railway auto-sets, but defaults to 8001)

### Optional

- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `CLERK_SECRET_KEY` - Clerk authentication secret key
- `RAILWAY_PUBLIC_DOMAIN` - Railway will auto-set this, used for CORS
- `HOST` - Server host (defaults to 0.0.0.0)

## Build Process

Railway will:

1. Detect Python project
2. Install Poetry dependencies from `packages/backend/pyproject.toml`
3. Run the start command: `poetry run python -m experiments.web.dashboard_server`

## Health Check

The server exposes a health check endpoint at `/health`:

```bash
curl https://your-railway-app.railway.app/health
```

## Troubleshooting

### Build Fails

- Check that `packages/backend/pyproject.toml` exists
- Verify Poetry is installed (Railway auto-installs)
- Check build logs in Railway dashboard

### Server Won't Start

- Verify `PORT` environment variable is set (Railway auto-sets this)
- Check that `DATABASE_URL` is correct if using database
- Review startup logs in Railway dashboard

### Database Connection Issues

- Ensure PostgreSQL service is added to Railway project
- Verify `DATABASE_URL` is correctly formatted
- Check that database migrations have run (if needed)

### CORS Errors

- Add your frontend domain to `CORS_ORIGINS`
- Railway domain is auto-added if `RAILWAY_PUBLIC_DOMAIN` is set

## Local Testing

To test the Railway configuration locally:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run locally with Railway environment
railway run bash packages/backend/experiments/web/railway_start.sh
```

## Production Checklist

- [ ] Environment variables configured
- [ ] PostgreSQL service added (if using database)
- [ ] CORS origins set correctly
- [ ] Health check endpoint responding
- [ ] Database migrations run (if needed)
- [ ] API keys and secrets configured
- [ ] Custom domain configured (optional)
