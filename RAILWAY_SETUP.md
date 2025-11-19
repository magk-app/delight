# Railway Setup for Experimental Web Server

## Problem

Railway was detecting the root `package.json` and trying to use Railpack (Node.js packer) instead of Nixpacks (Python packer).

## Solution

Root-level configuration files have been added to force Railway to use Nixpacks:

- **`railway.json`** (root) - Forces Nixpacks builder and points to Python backend
- **`nixpacks.toml`** (root) - Nixpacks build configuration
- **`runtime.txt`** (root) - Python version specification

## Deployment Steps

1. **In Railway Dashboard:**

   - Deploy from GitHub repository (root level)
   - **DO NOT set a Root Directory** - Railway should build from repository root
   - The root `railway.json` will force Nixpacks to be used

2. **Add Environment Variables:**

   - `DATABASE_URL` - PostgreSQL connection (add PostgreSQL service for auto-config)
   - `PORT` - Auto-set by Railway
   - `CORS_ORIGINS` - Your frontend domains
   - `OPENAI_API_KEY` - If using AI features
   - `CLERK_SECRET_KEY` - If using authentication

3. **Add PostgreSQL Service (if needed):**
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will auto-create `DATABASE_URL` variable

## How It Works

1. Railway detects root `railway.json` → Uses Nixpacks builder
2. Nixpacks reads root `nixpacks.toml` → Installs Python 3.11 and Poetry
3. Build command: `cd packages/backend && poetry install --no-dev`
4. Start command: `cd packages/backend && poetry run python -m experiments.web.dashboard_server`

## Files Structure

```
/
├── railway.json          # Root config - forces Nixpacks
├── nixpacks.toml         # Root build config
├── runtime.txt           # Python version
├── package.json          # Node.js config (ignored by Railway due to railway.json)
└── packages/
    └── backend/
        └── experiments/
            └── web/
                ├── dashboard_server.py  # The actual server
                ├── railway.json         # Alternative config (if using subdirectory)
                └── nixpacks.toml        # Alternative config (if using subdirectory)
```

## Troubleshooting

**If Railway still uses Railpack:**

- Check that `railway.json` exists at root
- Verify `nixpacks.toml` exists at root
- Make sure Root Directory is NOT set in Railway settings

**If build fails:**

- Check that `packages/backend/pyproject.toml` exists
- Verify Poetry dependencies are correct
- Check build logs in Railway dashboard
