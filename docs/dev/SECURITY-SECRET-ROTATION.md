# Emergency: Rotate Exposed Clerk Webhook Secret

**Status:** 🔴 **IMMEDIATE ACTION REQUIRED**  
**Date:** December 7, 2025  
**Issue:** Clerk webhook secret exposed in GitHub repository

## What Happened

The Clerk webhook signing secret `whsec_xSPnZzquPpSQuqjptNW7Z5KrOSVCQsaK` was accidentally committed to the repository in documentation files. GitHub Secret Scanning detected this exposure.

## Why This Matters

An exposed webhook secret allows attackers to:
- Send forged webhook events to your backend
- Create/modify user accounts without authorization
- Bypass webhook signature verification

## Immediate Actions (Do This Now)

### Step 1: Revoke the Exposed Secret in Clerk

1. **Go to Clerk Dashboard:**
   - Navigate to https://dashboard.clerk.com
   - Select your "Delight Development" application

2. **Navigate to Webhooks:**
   - Click **"Webhooks"** in the left sidebar
   - You should see your existing webhook endpoint

3. **Rotate or Delete the Endpoint:**
   
   **Option A - Rotate Secret (Recommended):**
   - Click on your webhook endpoint
   - Click **"Rotate Signing Secret"** button
   - **⚠️ IMPORTANT:** Copy the new secret immediately (you won't see it again!)
   - Save the new secret securely
   
   **Option B - Delete and Recreate:**
   - Click **"Delete"** on the existing endpoint
   - Click **"Add Endpoint"** to create a new one
   - Continue to Step 2

### Step 2: Create New Webhook Endpoint (If Deleted)

1. Click **"Add Endpoint"** in Clerk Dashboard → Webhooks

2. **Configure the endpoint:**
   - **Endpoint URL:** 
     - For local development: `https://YOUR_NGROK_URL.ngrok.io/api/v1/webhooks/clerk`
     - For production: `https://your-domain.com/api/v1/webhooks/clerk`
   - **Description:** "Delight User Sync"
   - **Events to subscribe:**
     - ✅ `user.created`
     - ✅ `user.updated`

3. Click **"Create"**

4. **Copy the Signing Secret:**
   - It will look like: `whsec_abc123xyz...`
   - **⚠️ Keep this secret safe!** You'll need it for the next step

### Step 3: Update Your Local Environment

1. **Open your backend `.env` file:**
   ```bash
   # Location: C:\Users\Jack Luo\Desktop\(local) github software\(o) magk\delight\packages\backend\.env
   ```

2. **Update the secret:**
   ```bash
   # Replace the old secret with the NEW one from Clerk
   CLERK_WEBHOOK_SECRET=whsec_YOUR_NEW_SECRET_HERE
   ```

3. **Save the file**

### Step 4: Restart Your Backend

```bash
cd packages/backend
poetry run uvicorn main:app --reload
```

The backend will now use the new webhook secret.

### Step 5: Test Webhook Functionality

**Option A - Quick Test (Clerk Dashboard):**

1. In Clerk Dashboard → Webhooks → Your endpoint
2. Click **"Testing"** tab
3. Select event type: `user.created`
4. Click **"Send Example"**
5. Check your backend logs - should see: `INFO: User synced: user_xxx (user.created)`

**Option B - Real User Test:**

1. Go to http://localhost:3000
2. Sign up with a new test email (e.g., `test-$(date +%s)@example.com`)
3. Check backend logs for webhook event
4. Verify user appears in Supabase `users` table

### Step 6: Close the GitHub Security Alert

1. **Go to GitHub:**
   - Navigate to your repository
   - Click **"Security"** tab
   - Click **"Secret scanning alerts"**

2. **Close the alert:**
   - Click on alert #2 (Stripe/Clerk Webhook Secret)
   - Click **"Close as"** → **"Revoked"**
   - Add comment: "Secret rotated via Clerk Dashboard. New secret configured in local .env (not committed)."

### Step 7: Verify the Fix

Run this command to ensure no secrets remain in the repo:

```bash
git grep -i "whsec_" --exclude-dir=node_modules --exclude-dir=.venv
```

**Expected result:** No results (or only `whsec_[REDACTED_FROM_REPOSITORY]`)

If you find any remaining instances:
- Replace with `whsec_...` or `whsec_[REDACTED]`
- Never commit real webhook secrets

## Production Environment

If you have a production deployment, you must also:

1. **Create a separate production webhook endpoint:**
   - Use your production domain URL
   - Generate a NEW secret (different from development)
   - Configure in your production environment variables

2. **Update production environment variables:**
   - Railway/Vercel/Cloud: Update `CLERK_WEBHOOK_SECRET` in platform dashboard
   - Use the production webhook secret (not the development one)

3. **Test production webhooks:**
   - Create a test user in production
   - Verify webhook delivery in Clerk logs
   - Verify user sync to production database

## Verification Checklist

- [ ] Old webhook secret revoked/rotated in Clerk Dashboard
- [ ] New webhook secret copied from Clerk
- [ ] `packages/backend/.env` updated with new secret
- [ ] Backend restarted successfully
- [ ] Webhook test successful (user.created event received)
- [ ] GitHub security alert closed as "Revoked"
- [ ] No remaining secrets in repository: `git grep "whsec_"`
- [ ] Production webhook updated (if applicable)

## Prevention for the Future

### ✅ Best Practices

1. **Never commit `.env` files** - They're already in `.gitignore`
2. **Never include real secrets in documentation** - Use placeholders like `whsec_...`
3. **Use environment variable examples** - Create `.env.example` with fake values
4. **Review before committing** - Check diffs for secrets: `git diff --staged`
5. **Use pre-commit hooks** - Install `detect-secrets` or `git-secrets`

### 🔒 Recommended Tools

**Pre-commit Hook for Secret Detection:**

```bash
# Install detect-secrets
pip install detect-secrets

# Scan repository
detect-secrets scan

# Add to pre-commit hook (optional)
cat << 'EOF' > .git/hooks/pre-commit
#!/bin/bash
detect-secrets-hook --baseline .secrets.baseline
EOF
chmod +x .git/hooks/pre-commit
```

**GitHub Secret Scanning (Already Enabled):**
- ✅ You have this enabled - it caught the leak!
- Keep it enabled for future protection

## Repository Changes Made

The following files were updated to remove the exposed secret:

1. **`docs/stories/epic-1/1-3-integrate-clerk-authentication-system.md`**
   - Redacted secret: `whsec_xSPnZzquPpSQuqjptNW7Z5KrOSVCQsaK` → `whsec_[REDACTED_FROM_REPOSITORY]`
   - Added security note about rotation requirement

2. **Created new security guides:**
   - `docs/dev/CLERK-WEBHOOK-SETUP.md` - Comprehensive webhook setup guide
   - `docs/dev/SECURITY-SECRET-ROTATION.md` - This emergency rotation guide

## Need Help?

**If you encounter any issues:**

1. **Backend won't start:**
   - Check `.env` file has correct variable name: `CLERK_WEBHOOK_SECRET`
   - No spaces around the `=` sign
   - Secret starts with `whsec_`

2. **Webhooks not working:**
   - Verify webhook URL matches your ngrok URL (for local dev)
   - Check Clerk Dashboard → Webhooks → Logs for delivery failures
   - Check backend logs for signature verification errors

3. **GitHub alert won't close:**
   - Make sure you've committed the changes that redact the secret
   - Push changes to GitHub: `git push origin main`
   - Then close the alert as "Revoked"

**References:**
- Clerk Webhooks: https://clerk.com/docs/integrations/webhooks/overview
- Webhook Setup Guide: `docs/dev/1-3-WEBHOOK-SETUP-GUIDE.md`
- General Setup: `docs/dev/CLERK-WEBHOOK-SETUP.md`

## Timeline

- **2025-12-07:** Secret detected by GitHub Secret Scanning
- **2025-12-07:** Secret redacted from repository
- **2025-12-07:** Security guides created
- **[TODO]:** Secret rotated in Clerk Dashboard (action required by you)
- **[TODO]:** New secret configured in local .env
- **[TODO]:** GitHub alert closed

---

**Status:** ⏳ Awaiting your action to rotate the secret in Clerk Dashboard

