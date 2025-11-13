# Delight - Development Environment Setup

**Complete setup guide from zero to running dev servers in ~15 minutes**

Last Updated: 2025-11-10

---

## 📋 **Prerequisites**

Before starting, ensure you have these installed:

| Requirement | Version | Install Link                                 |
| ----------- | ------- | -------------------------------------------- |
| **Node.js** | 20.x+   | https://nodejs.org                           |
| **Python**  | 3.11+   | https://www.python.org/downloads             |
| **Poetry**  | Latest  | https://python-poetry.org/docs/#installation |
| **pnpm**    | 8.x+    | `npm install -g pnpm`                        |
| **Git**     | Latest  | https://git-scm.com                          |

**No Docker required!** We use managed services (Supabase, Upstash) for databases.

---

## ⚡ **Quick Start (15 Minutes)**

### **Step 1: Clone Repository (1 min)**

```bash
git clone https://github.com/yourusername/delight.git
cd delight
```

### **Step 2: Install Dependencies (3 min)**

```bash
# Install frontend dependencies
pnpm install

# Install backend dependencies
cd packages/backend
poetry install
cd ../..
```

### **Step 3: Set Up Supabase (5 min)**

1. **Create Account & Project**

   - Go to https://app.supabase.com
   - Click **"New Project"**
   - Name: `delight-dev` (or your choice)
   - Database Password: **Save this somewhere safe!**
   - Region: Choose closest to you
   - Click **"Create new project"** (takes ~2 minutes)

2. **Enable pgvector Extension**

   - In Supabase dashboard, go to **SQL Editor**
   - Click **"New Query"**
   - Run this command:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
   - Click **"Run"**

3. **Get Connection String**
   - Go to **Project Settings → Database**
   - Find **"Connection string"** section
   - Select **"Transaction mode"** (recommended)
   - Copy the connection string (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`)
   - Replace `[YOUR-PASSWORD]` with your actual database password

### **Step 4: Set Up Clerk Authentication (3 min)**

1. **Create Account & Application**

   - Go to https://clerk.com
   - Sign up or log in
   - Click **"Create Application"**
   - Name: `Delight Dev`
   - Enable providers: **Email**, **Google**, **GitHub** (optional)

2. **Get API Keys**

   - In Clerk dashboard, go to **API Keys**
   - Copy **"Publishable Key"** (starts with `pk_test_`)
   - Copy **"Secret Key"** (starts with `sk_test_`)

3. **Set Up Webhooks (for local development)**
   - ⚠️ **You'll need ngrok running** (see Step 7)
   - After starting ngrok, go to **Webhooks** in Clerk dashboard
   - Add endpoint: `https://YOUR_NGROK_URL/api/v1/webhooks/clerk`
   - Subscribe to: `user.created`, `user.updated`
   - Copy **Signing Secret** (starts with `whsec_`) → add to backend `.env` as `CLERK_WEBHOOK_SECRET`
   - 📖 **Full guide:** See `docs/dev/1-3-WEBHOOK-SETUP-GUIDE.md`

### **Step 5: Set Up OpenAI API (2 min)**

1. **Create Account & API Key**
   - Go to https://platform.openai.com
   - Sign up or log in
   - Add payment method (required, but MVP costs ~$0.03/day)
   - Go to **API Keys** section
   - Click **"Create new secret key"**
   - **Copy immediately** (you won't see it again!)
   - Save as: `sk-proj-...` or similar

### **Step 6: Configure Environment Variables (1 min)**

**Backend Configuration:**

```bash
# Create backend .env file
cd packages/backend
cp .env.example .env

# Edit packages/backend/.env with your values:
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
CLERK_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-proj-...
REDIS_URL=redis://localhost:6379/0  # Or use Upstash (see Optional Services below)
```

**Frontend Configuration:**

```bash
# Create frontend .env.local file
cd ../frontend
cp .env.local.example .env.local

# Edit packages/frontend/.env.local with your values:
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Step 7: Start Development Servers**

**⚠️ IMPORTANT: For Authentication Testing, You Need ngrok!**

If you're testing user signup or authentication, you need ngrok running to receive Clerk webhooks:

**Terminal 1 - Backend:**

```bash
cd packages/backend
poetry run uvicorn app.main:app --reload
```

**Terminal 2 - ngrok (REQUIRED for webhooks!):**

```bash
# Install ngrok first: https://ngrok.com/download
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update Clerk webhook URL: https://YOUR_NGROK_URL/api/v1/webhooks/clerk
```

**Terminal 3 - Frontend:**

```bash
cd packages/frontend
pnpm dev
```

### **Step 8: Verify Everything Works ✅**

Open these URLs in your browser:

- **Frontend:** http://localhost:3000
  - Should see: Delight homepage
- **Backend API:** http://localhost:8000/docs
  - Should see: FastAPI Swagger UI

**Congratulations! 🎉 Your development environment is ready!**

---

## 🔧 **Optional Services**

### **Redis (Background Jobs)**

**Option A: Use Upstash (Recommended for MVP)**

- Free tier: 10K commands/day
- Go to https://upstash.com
- Create Redis database
- Copy connection string to `REDIS_URL`

**Option B: Local Docker**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 🆘 **Troubleshooting**

### **Problem: Backend won't connect to database**

```bash
# Verify connection string
echo $DATABASE_URL
# Should output: postgresql://postgres:...@db...supabase.co:5432/postgres

# Test connection manually
cd packages/backend
poetry run python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); print('✅ Connected!'); conn.close()"
```

**Solution:** Double-check password in DATABASE_URL matches Supabase project password

### **Problem: Port already in use**

```bash
# Windows - Find what's using port 8000
netstat -ano | findstr :8000

# Mac/Linux
lsof -i :8000

# Kill the process or use different port:
poetry run uvicorn app.main:app --reload --port 8001
```

### **Problem: `poetry install` fails**

```bash
# Clear cache and retry
poetry cache clear pypi --all
poetry install
```

### **Problem: Frontend won't compile**

```bash
# Clear Next.js cache
cd packages/frontend
rm -rf .next
pnpm install
pnpm dev
```

### **Problem: Clerk authentication not working**

**Check:**

1. API keys are correct in `.env` and `.env.local`
2. Publishable key starts with `pk_test_`
3. Secret key starts with `sk_test_`
4. No extra spaces in environment variables

### **Still stuck?**

1. Check `docs/dev/BMAD-DEVELOPER-GUIDE.md` for detailed troubleshooting
2. Review architecture decisions in `docs/ARCHITECTURE.md`
3. Ask in project Discord/Slack

---

## 📚 **Next Steps**

Now that your environment is set up:

1. **Read the workflow:** `docs/dev/BMAD-DEVELOPER-GUIDE.md`
2. **Check sprint status:** `docs/sprint-status.yaml`
3. **Pick your first story:** Look for stories marked `ready-for-dev`
4. **Optional:** Run `@bmad/bmm/workflows/story-context` for implementation guidance

---

## 📊 **Environment Health Check**

Run this checklist to verify everything:

```bash
# ✅ Backend health
cd packages/backend
poetry run python -c "print('✅ Python environment OK')"

# ✅ Frontend health
cd packages/frontend
pnpm --version && echo "✅ pnpm OK"

# ✅ Database connection
cd packages/backend
poetry run python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); print('✅ Database OK'); conn.close()"

# ✅ Backend starts
poetry run uvicorn app.main:app --reload &
sleep 5
curl http://localhost:8000/docs && echo "✅ Backend OK"

# ✅ Frontend starts
cd ../frontend
pnpm dev &
sleep 10
curl http://localhost:3000 && echo "✅ Frontend OK"
```

---

## 💡 **Pro Tips**

1. **Use separate terminal tabs** for backend, frontend, and commands
2. **Keep .env files secure** - never commit them to Git
3. **Supabase dashboard** is great for debugging database issues
4. **API costs** are ~$0.03/user/day - very affordable for development
5. **Hot reload works** - edit code and see changes immediately

---

## 🔐 **Security Reminders**

- ✅ `.env` files are in `.gitignore` (never commit secrets!)
- ✅ Use test API keys for development (Clerk provides `pk_test_` and `sk_test_`)
- ✅ Rotate API keys if accidentally exposed
- ✅ Keep Supabase database password in password manager

---

## 📖 **Related Documentation**

- **Architecture Overview:** `docs/ARCHITECTURE.md`
- **Development Workflow:** `docs/dev/BMAD-DEVELOPER-GUIDE.md`
- **Quick Reference:** `docs/dev/QUICK-REFERENCE.md`
- **Documentation Index:** `docs/INDEX.md`

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**Maintainer:** Delight Team
