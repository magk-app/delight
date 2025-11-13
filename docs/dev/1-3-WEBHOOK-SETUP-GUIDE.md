# Webhook Setup Guide - Story 1.3

## ⚠️ REMINDER: Don't Forget ngrok!

**Before testing authentication or user creation, make sure ngrok is running!**

```bash
# Terminal 1: Backend
cd packages/backend
poetry run uvicorn main:app --reload

# Terminal 2: ngrok (REQUIRED for webhooks!)
ngrok http 8000
```

**Why this matters:**

- Webhooks only fire on **new signups**, not logins
- Without ngrok, Clerk can't reach your local backend
- Users won't be created via webhooks (but lazy user creation will still work)
- **Temporary ngrok URLs expire after 2 hours** - use reserved domain to avoid this!

## Problem

Clerk webhooks cannot reach `http://localhost:8000` because it's not publicly accessible from the internet.

## Solution: Use ngrok

### Step 1: Install ngrok

**Windows:**

1. Download from https://ngrok.com/download
2. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok\`)
3. Add to PATH or use full path

**Or via Chocolatey:**

```bash
choco install ngrok
```

### Step 2: Create ngrok Account (Free)

1. Go to https://dashboard.ngrok.com/signup
2. Sign up (free tier is sufficient)
3. Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
4. Run: `ngrok config add-authtoken YOUR_AUTH_TOKEN`

### Step 3: Start Your Backend

```bash
cd C:\Users\Jack Luo\Desktop\(local) github software\delight\packages\backend
poetry run uvicorn main:app --reload
```

Keep this terminal running. Backend should be on `http://localhost:8000`

### Step 4: Start ngrok Tunnel

**Option A: Temporary Domain (Expires in 2 hours)**

Open a NEW terminal:

```bash
# Windows Command Prompt:
ngrok http 8000

# Or if ngrok.exe is in a specific folder:
C:\ngrok\ngrok.exe http 8000
```

You'll see output like:

```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy that HTTPS URL** (e.g., `https://abc123.ngrok.io`)

⚠️ **Note:** This URL expires after 2 hours. You'll need to restart ngrok and update Clerk webhook URL.

**Option B: Reserved Domain (Permanent - Recommended for Dev)**

For a permanent domain that doesn't expire, use ngrok's reserved domains:

1. **Get Reserved Domain (Free):**

   - Go to https://dashboard.ngrok.com/cloud-edge/domains
   - Click **"New Domain"**
   - Choose **"Reserved Domain"** (free tier)
   - Pick a name (e.g., `delight-dev`)
   - Copy the domain (e.g., `delight-dev.ngrok-free.app`)

2. **Start ngrok with Reserved Domain:**

```bash
# Use your reserved domain name
ngrok http --domain=delight-dev.ngrok-free.app 8000

# Or if ngrok.exe is in a specific folder:
C:\ngrok\ngrok.exe http --domain=delight-dev.ngrok-free.app 8000
```

You'll see output like:

```
Forwarding  https://delight-dev.ngrok-free.app -> http://localhost:8000
```

**Benefits of Reserved Domain:**

- ✅ **Never expires** - same URL every time
- ✅ **No need to update Clerk** - set webhook URL once
- ✅ **Free tier available** - no cost for development
- ✅ **Consistent development** - easier to share with team

**Note:** Reserved domains are limited on free tier (usually 1 domain). For production, use a real domain or paid ngrok plan.

### Step 5: Configure Clerk Webhook with ngrok URL

1. Go to https://dashboard.clerk.com
2. Select your "Delight Development" app
3. Click **"Webhooks"** in left sidebar
4. Click on your existing endpoint (or "Add Endpoint" if none exists)
5. Change the URL to: `https://YOUR_NGROK_URL/api/v1/webhooks/clerk`
   - Example: `https://abc123.ngrok.io/api/v1/webhooks/clerk`
6. Subscribe to events: `user.created`, `user.updated`
7. Save
8. Copy the **Signing Secret** (starts with `whsec_`)

### Step 6: Update Backend .env

Make sure your `.env` has the webhook secret:

```bash
CLERK_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
```

Restart your backend if you changed this.

### Step 7: Test the Webhook Flow

#### Option A: Sign Up a New Test User

1. Go to http://localhost:3000
2. Sign up with a NEW email (e.g., `test2@example.com`)
3. Watch your backend terminal - you should see:
   ```
   INFO: User synced: user_2xxx123 (user.created)
   ```
4. Check Supabase Table Editor → `users` table
5. You should see the new user!

#### Option B: Send Test Webhook from Clerk

1. In Clerk dashboard → Webhooks → Your endpoint
2. Click "Testing" tab
3. Select event type: `user.created`
4. Click "Send Example"
5. Check backend logs for webhook received message
6. Check Supabase for the test user

### Step 8: Verify in Supabase

```sql
-- In Supabase SQL Editor:
SELECT clerk_user_id, email, display_name, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

You should see users with `clerk_user_id` starting with "user\_"

## Troubleshooting

### Webhook Still Not Received

**Check ngrok is running:**

- Open http://localhost:4040 (ngrok web interface)
- You should see requests coming in when you sign up

**Check Clerk webhook logs:**

- Clerk Dashboard → Webhooks → Your endpoint → "Logs" tab
- Look for failed deliveries with error messages

**Check backend logs:**

- Should see: `POST /api/v1/webhooks/clerk` requests
- If you see 400 errors, check CLERK_WEBHOOK_SECRET is correct

### Common Errors

**"Invalid webhook signature"**

- Your CLERK_WEBHOOK_SECRET doesn't match Clerk's signing secret
- Copy the secret again from Clerk dashboard
- Update `.env` and restart backend

**404 Not Found**

- Webhook URL is wrong
- Should be: `https://YOUR_NGROK_URL/api/v1/webhooks/clerk`
- Make sure `/api/v1/webhooks/clerk` is at the end

**ngrok session expired**

- **Temporary domains** expire after 2 hours
- **Solution:** Use a reserved domain (see Step 4 Option B) or restart ngrok and update Clerk webhook URL
- **Reserved domains never expire** - recommended for development

## Production Deployment

For production, you won't need ngrok. Your deployed backend will have a real public URL:

- Railway: `https://your-app.railway.app/api/v1/webhooks/clerk`
- Vercel: `https://your-app.vercel.app/api/v1/webhooks/clerk`
- AWS/GCP: `https://api.yourcompany.com/api/v1/webhooks/clerk`

Update Clerk webhooks to use your production URL when you deploy.

## Quick Reference

```bash
# Terminal 1: Backend
cd packages/backend
poetry run uvicorn main:app --reload

# Terminal 2: ngrok (temporary domain - expires in 2 hours)
ngrok http 8000

# OR use reserved domain (permanent - recommended)
ngrok http --domain=delight-dev.ngrok-free.app 8000

# Then update Clerk webhook URL to ngrok URL
```

**Pro Tip:** Use a reserved domain to avoid updating Clerk webhook URL every 2 hours!

## Verification Checklist

- [ ] ngrok running and showing HTTPS URL
- [ ] Clerk webhook URL updated to ngrok URL
- [ ] CLERK_WEBHOOK_SECRET in backend .env
- [ ] Backend running on localhost:8000
- [ ] Sign up new user → backend logs show webhook received
- [ ] Supabase users table has new record with clerk_user_id
