# Clerk Production Setup Guide

**Last Updated:** 2025-11-12  
**Status:** Production Ready  
**Related:** [Story 1.3 - Clerk Authentication](../stories/1-3-integrate-clerk-authentication-system.md)

---

## Overview

This guide walks you through switching Clerk authentication from **development/test mode** to **production mode**. Production mode uses live keys (`pk_live_` and `sk_live_`) instead of test keys (`pk_test_` and `sk_test_`), and provides separate user databases, enhanced security, and production-grade features.

### Key Differences: Test vs Production

| Feature                 | Test Mode               | Production Mode              |
| ----------------------- | ----------------------- | ---------------------------- |
| **Key Prefix**          | `pk_test_` / `sk_test_` | `pk_live_` / `sk_live_`      |
| **User Database**       | Shared test environment | Separate production database |
| **Domain Restrictions** | `clerk.accounts.dev`    | Your custom domain           |
| **Rate Limits**         | Lower limits            | Higher limits                |
| **Support**             | Community support       | Priority support             |
| **Billing**             | Free                    | Usage-based pricing          |

---

## Prerequisites

Before switching to production mode, ensure you have:

- ✅ Clerk account with an active application
- ✅ Production domain ready (e.g., `yourdomain.com`)
- ✅ Access to your deployment platform (Vercel, Railway, Fly.io, etc.)
- ✅ SSL certificate configured for your domain (HTTPS required)
- ✅ Backup of current environment variables

---

## Step-by-Step Setup

### Step 1: Get Production Keys from Clerk Dashboard

1. **Navigate to Clerk Dashboard**

   - Go to https://dashboard.clerk.com
   - Sign in to your account
   - Select your application

2. **Switch to Production Mode**

   - In the Clerk dashboard, look for the **environment toggle** (usually in the top-right or sidebar)
   - Switch from **"Test"** to **"Production"**
   - You may see a confirmation dialog - click **"Switch to Production"**

3. **Copy Production Keys**

   - Navigate to **API Keys** section (usually under **"Configure"** → **"API Keys"**)
   - Copy the following keys:
     - **Publishable Key** (starts with `pk_live_`)
     - **Secret Key** (starts with `sk_live_`)
     - **Webhook Secret** (if using webhooks, starts with `whsec_`)

   ⚠️ **Important:** Store these keys securely. You won't be able to view the secret key again after closing the dialog.

---

### Step 2: Configure Clerk Instance Settings

#### 2.1 Add Production Domain

1. In Clerk Dashboard → **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your production domain:
   - Primary domain: `yourdomain.com`
   - Subdomain (if applicable): `app.yourdomain.com`
4. Follow Clerk's DNS verification steps:
   - Add the provided DNS records to your domain registrar
   - Wait for DNS propagation (can take up to 24 hours, usually < 1 hour)
   - Clerk will verify automatically

#### 2.2 Configure Allowed Origins (CORS)

1. In Clerk Dashboard → **Settings** → **Allowed Origins**
2. Add your production frontend URLs:
   ```
   https://yourdomain.com
   https://www.yourdomain.com
   https://app.yourdomain.com
   ```
3. Remove any test/development URLs if they're no longer needed

#### 2.3 Configure Webhooks (if applicable)

If you're using Clerk webhooks:

1. In Clerk Dashboard → **Webhooks**
2. Create or update webhook endpoint:
   - **Endpoint URL:** `https://api.yourdomain.com/api/v1/webhooks/clerk`
   - **Events:** Select events you need (e.g., `user.created`, `user.updated`, `user.deleted`)
3. Copy the **Webhook Signing Secret** (starts with `whsec_`)

---

### Step 3: Update Frontend Environment Variables

#### For Vercel Deployment

1. **Navigate to Vercel Dashboard**

   - Go to https://vercel.com/dashboard
   - Select your project
   - Go to **Settings** → **Environment Variables**

2. **Update Environment Variables**

   For **Production** environment:

   ```bash
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

   For **Preview** environment (optional - keep test keys):

   ```bash
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   CLERK_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Redeploy Application**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on the latest deployment
   - Or push a new commit to trigger automatic deployment

#### For Other Frontend Hosting Platforms

Update environment variables in your platform's dashboard:

```bash
# Production environment variables
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

---

### Step 4: Update Backend Environment Variables

#### For Railway Deployment

1. **Navigate to Railway Dashboard**

   - Go to https://railway.app/dashboard
   - Select your backend service
   - Go to **Variables** tab

2. **Update Environment Variables**

   ```bash
   CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ENVIRONMENT=production
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Redeploy**
   - Railway automatically redeploys when variables change
   - Or manually trigger redeploy from the **Deployments** tab

#### For Fly.io Deployment

1. **Update Secrets via CLI**

   ```bash
   flyctl secrets set \
     CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
     CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
     ENVIRONMENT=production \
     CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

2. **Verify Secrets**

   ```bash
   flyctl secrets list
   ```

3. **Redeploy**
   ```bash
   flyctl deploy
   ```

#### For Other Backend Hosting Platforms

Update environment variables in your platform's dashboard:

```bash
# Production environment variables
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=postgresql+asyncpg://...  # Your production database
REDIS_URL=redis://...  # Your production Redis
```

---

### Step 5: Verify Configuration

#### 5.1 Check Key Prefixes

Verify that your production environment is using live keys:

**Frontend Check:**

- Open your production site in a browser
- Open browser DevTools → Console
- Check for Clerk initialization logs
- Verify no "developer mode" warnings appear

**Backend Check:**

- Check your backend logs for Clerk initialization
- Look for: `Initializing Clerk JWKS client with URL: https://api.clerk.com/.well-known/jwks.json`
- Verify no test mode warnings

#### 5.2 Test Authentication Flow

1. **Sign Up Flow**

   - Visit your production site
   - Click "Sign Up"
   - Create a new account
   - Verify email (if email verification is enabled)
   - Confirm you can access protected routes

2. **Sign In Flow**

   - Sign out
   - Sign in with the account you just created
   - Verify session persists across page refreshes

3. **Protected Routes**
   - Navigate to protected routes (e.g., `/dashboard`)
   - Verify you're redirected to sign-in if not authenticated
   - Verify you can access protected routes when authenticated

#### 5.3 Verify Webhooks (if applicable)

1. **Check Webhook Delivery**

   - In Clerk Dashboard → **Webhooks** → **Recent Deliveries**
   - Create a test user or update an existing user
   - Verify webhook events are being delivered successfully
   - Check your backend logs for webhook processing

2. **Test Webhook Endpoint**
   ```bash
   # Test webhook endpoint manually (optional)
   curl -X POST https://api.yourdomain.com/api/v1/webhooks/clerk \
     -H "Content-Type: application/json" \
     -H "svix-id: test-id" \
     -H "svix-timestamp: $(date +%s)" \
     -H "svix-signature: test-sig" \
     -d '{"type":"user.created","data":{"id":"test_user"}}'
   ```

---

## Environment Variable Reference

### Frontend Production Variables

```bash
# Clerk Authentication (Production)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# API Configuration
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Environment
NODE_ENV=production
```

### Backend Production Variables

```bash
# Clerk Authentication (Production)
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Environment Configuration
ENVIRONMENT=production
INFRA_MODE=cloud-dev  # or production

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database & Services
DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
REDIS_URL=redis://default:[password]@[host]:6379

# Other Services
OPENAI_API_KEY=sk-...
SENTRY_DSN=https://...
```

---

## Troubleshooting

### Issue: "Developer Mode" Banner Still Appears

**Symptoms:** You see a "Developer Mode" banner on your production site.

**Solutions:**

1. Verify you're using `pk_live_` keys (not `pk_test_`)
2. Clear browser cache and hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
3. Check that environment variables are set correctly in your deployment platform
4. Verify the deployment actually picked up the new environment variables (check deployment logs)

### Issue: Authentication Fails in Production

**Symptoms:** Users can't sign in or sign up in production.

**Solutions:**

1. **Check Domain Configuration**

   - Verify your domain is added in Clerk Dashboard → Settings → Domains
   - Ensure DNS records are correctly configured
   - Wait for DNS propagation (can take up to 24 hours)

2. **Check CORS Configuration**

   - Verify `CORS_ORIGINS` includes your production frontend URL
   - Check browser console for CORS errors
   - Ensure URLs match exactly (including `https://` and trailing slashes)

3. **Check Key Configuration**

   - Verify `CLERK_SECRET_KEY` matches the production secret key
   - Ensure keys are not accidentally mixed (test keys in production or vice versa)
   - Check backend logs for authentication errors

4. **Check Webhook Configuration** (if using webhooks)
   - Verify webhook URL is correct: `https://api.yourdomain.com/api/v1/webhooks/clerk`
   - Check webhook signing secret matches
   - Review webhook delivery logs in Clerk Dashboard

### Issue: Users Created in Test Mode Don't Exist in Production

**Symptoms:** Users who signed up during development can't sign in to production.

**Explanation:** This is expected behavior. Test mode and production mode use separate user databases.

**Solutions:**

1. **Option 1: Migrate Users** (if needed)

   - Export users from test environment via Clerk API
   - Import to production environment (requires custom script)
   - Note: This is complex and may not preserve all user data

2. **Option 2: Ask Users to Re-register** (recommended)
   - Users sign up again in production
   - This is the simplest and most reliable approach

### Issue: Webhooks Not Working in Production

**Symptoms:** User creation/updates aren't syncing to your database.

**Solutions:**

1. **Verify Webhook Configuration**

   - Check webhook URL is accessible: `https://api.yourdomain.com/api/v1/webhooks/clerk`
   - Verify webhook signing secret matches
   - Check webhook events are enabled in Clerk Dashboard

2. **Check Backend Logs**

   - Look for webhook processing errors
   - Verify webhook endpoint is receiving requests
   - Check for signature validation errors

3. **Test Webhook Endpoint**
   - Use Clerk Dashboard → Webhooks → Test Endpoint
   - Or manually test with curl (see Step 5.3 above)

---

## Security Best Practices

### ✅ Do's

- ✅ **Use separate keys for test and production**
- ✅ **Never commit production keys to git**
- ✅ **Use environment variables for all secrets**
- ✅ **Enable HTTPS for all production endpoints**
- ✅ **Regularly rotate webhook secrets**
- ✅ **Monitor webhook delivery failures**
- ✅ **Use least-privilege access for Clerk API keys**
- ✅ **Enable Clerk's security features** (MFA, rate limiting, etc.)

### ❌ Don'ts

- ❌ **Don't use test keys in production**
- ❌ **Don't expose secret keys in frontend code**
- ❌ **Don't hardcode keys in source code**
- ❌ **Don't share keys between team members via insecure channels**
- ❌ **Don't use the same keys for multiple environments**
- ❌ **Don't ignore webhook delivery failures**

---

## Migration Checklist

Use this checklist when migrating from test to production:

- [ ] **Clerk Dashboard**

  - [ ] Switched to Production mode in Clerk Dashboard
  - [ ] Copied production publishable key (`pk_live_...`)
  - [ ] Copied production secret key (`sk_live_...`)
  - [ ] Copied production webhook secret (`whsec_...`)
  - [ ] Added production domain to Clerk
  - [ ] Configured DNS records for domain verification
  - [ ] Updated allowed origins (CORS)
  - [ ] Configured webhook endpoint (if applicable)

- [ ] **Frontend Deployment**

  - [ ] Updated `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to production key
  - [ ] Updated `CLERK_SECRET_KEY` to production key
  - [ ] Updated `NEXT_PUBLIC_API_URL` to production API URL
  - [ ] Set `NODE_ENV=production`
  - [ ] Redeployed frontend

- [ ] **Backend Deployment**

  - [ ] Updated `CLERK_SECRET_KEY` to production key
  - [ ] Updated `CLERK_WEBHOOK_SECRET` to production secret
  - [ ] Set `ENVIRONMENT=production`
  - [ ] Updated `CORS_ORIGINS` to include production domain
  - [ ] Redeployed backend

- [ ] **Verification**
  - [ ] Verified no "developer mode" banner appears
  - [ ] Tested sign-up flow
  - [ ] Tested sign-in flow
  - [ ] Tested protected routes
  - [ ] Verified webhooks working (if applicable)
  - [ ] Checked backend logs for errors
  - [ ] Checked browser console for errors

---

## Additional Resources

- [Clerk Production Checklist](https://clerk.com/docs/deployments/overview)
- [Clerk Domain Configuration](https://clerk.com/docs/deployments/domains)
- [Clerk Webhooks Guide](https://clerk.com/docs/integrations/webhooks/overview)
- [Clerk Security Best Practices](https://clerk.com/docs/security/overview)
- [Delight Webhook Setup Guide](../WEBHOOK-SETUP-GUIDE.md)
- [Story 1.3 - Clerk Authentication](../stories/1-3-integrate-clerk-authentication-system.md)

---

## Support

If you encounter issues not covered in this guide:

1. Check [Clerk Documentation](https://clerk.com/docs)
2. Review [Clerk Status Page](https://status.clerk.com)
3. Contact Clerk Support (if on a paid plan)
4. Check Delight project issues/PRs for similar problems

---

**Last Updated:** 2025-11-12  
**Maintained By:** Delight Development Team
