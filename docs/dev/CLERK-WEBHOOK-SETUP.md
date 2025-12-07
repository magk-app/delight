# Clerk Webhook Secret Setup - Security Guide

## ⚠️ Security Warning

**NEVER commit webhook secrets to git!** This guide shows you how to properly configure the `CLERK_WEBHOOK_SECRET` environment variable.

## Quick Setup Steps

### 1. Revoke the Old Secret (If Exposed)

If you accidentally committed a webhook secret:

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your "Delight Development" app
3. Navigate to **Webhooks** in the left sidebar
4. Click on your existing webhook endpoint
5. Click **"Rotate Secret"** or **"Delete"** and create a new one

### 2. Create/Get New Webhook Secret

#### Option A: Create New Webhook Endpoint

1. In Clerk Dashboard → **Webhooks**
2. Click **"Add Endpoint"**
3. Enter your webhook URL:
   - **Local Development (with ngrok):** `https://YOUR_NGROK_URL.ngrok.io/api/v1/webhooks/clerk`
   - **Production:** `https://your-domain.com/api/v1/webhooks/clerk`
4. Subscribe to events:
   - ✅ `user.created`
   - ✅ `user.updated`
5. Click **"Create"**
6. **Copy the Signing Secret** (starts with `whsec_`)

#### Option B: Rotate Existing Secret

1. In Clerk Dashboard → **Webhooks** → Select your endpoint
2. Click **"Rotate Signing Secret"**
3. Copy the new secret immediately

### 3. Update Your Local Environment

**Backend `.env` file:**

```bash
# Location: packages/backend/.env
CLERK_WEBHOOK_SECRET=whsec_YOUR_NEW_SECRET_HERE
```

**Important:**
- Replace `whsec_YOUR_NEW_SECRET_HERE` with the actual secret from Clerk
- This file is already in `.gitignore` and will NOT be committed
- Never share this secret in documentation, chat logs, or screenshots

### 4. Restart Your Backend

```bash
cd packages/backend
poetry run uvicorn main:app --reload
```

### 5. Test the Webhook

Follow the testing guide in `docs/dev/1-3-WEBHOOK-SETUP-GUIDE.md` to verify:
- Webhook receives events from Clerk
- Signature validation passes
- Users are synced to your database

## Environment Variable Template

**Backend `.env.example`** (safe to commit):

```bash
# Clerk Authentication
CLERK_SECRET_KEY=sk_test_...  # Get from Clerk Dashboard → API Keys
CLERK_WEBHOOK_SECRET=whsec_...  # Get from Clerk Dashboard → Webhooks → Signing Secret
```

**Your actual `.env`** (NEVER commit):

```bash
CLERK_SECRET_KEY=sk_test_abc123xyz...
CLERK_WEBHOOK_SECRET=whsec_def456uvw...
```

## Security Best Practices

### ✅ DO:
- Store secrets in `.env` files (ignored by git)
- Use environment variables in CI/CD (GitHub Secrets, Railway secrets, etc.)
- Rotate secrets if accidentally exposed
- Use different secrets for development and production

### ❌ DON'T:
- Commit `.env` files to git
- Include real secrets in documentation or code comments
- Share secrets in screenshots or chat logs
- Hardcode secrets in source code
- Use the same secret across multiple environments

## Production Deployment

### Railway / Vercel / Cloud Platform

1. Add environment variables in your platform's dashboard:
   - `CLERK_SECRET_KEY=sk_live_...` (use live key, not test key)
   - `CLERK_WEBHOOK_SECRET=whsec_...` (create separate prod webhook endpoint)

2. In Clerk Dashboard, create a **separate webhook endpoint** for production:
   - URL: `https://your-production-domain.com/api/v1/webhooks/clerk`
   - Events: `user.created`, `user.updated`
   - Use the production signing secret in your deployment environment

### Never Reuse Development Secrets in Production!

## Troubleshooting

### "Invalid webhook signature" Error

**Cause:** Your `CLERK_WEBHOOK_SECRET` doesn't match the one in Clerk Dashboard.

**Fix:**
1. Go to Clerk Dashboard → Webhooks → Your endpoint
2. Copy the **current** Signing Secret
3. Update your `.env` file
4. Restart your backend

### Secret Not Loading

**Check:**
1. `.env` file is in `packages/backend/` directory
2. No typos in variable name (must be `CLERK_WEBHOOK_SECRET`)
3. No extra spaces before/after the `=` sign
4. Backend was restarted after changing `.env`

### Still Seeing Old Secret in Code

**Fix:**
```bash
# Search for any remaining instances
git grep "whsec_" --exclude-dir=node_modules --exclude-dir=.venv

# Remove from git history if found (advanced - be careful!)
# git filter-repo or BFG Repo-Cleaner
```

## Need Help?

- Clerk Webhooks Docs: https://clerk.com/docs/integrations/webhooks/overview
- Webhook Setup Guide: `docs/dev/1-3-WEBHOOK-SETUP-GUIDE.md`
- Story 1.3 Documentation: `docs/stories/epic-1/1-3-integrate-clerk-authentication-system.md`

## Verification Checklist

- [ ] Old webhook secret revoked in Clerk Dashboard
- [ ] New webhook endpoint created (or secret rotated)
- [ ] New secret copied to `packages/backend/.env`
- [ ] `.env` file confirmed in `.gitignore`
- [ ] Backend restarted
- [ ] Webhook test successful (user.created event received)
- [ ] No secrets found in git history: `git log -p | grep "whsec_"`

