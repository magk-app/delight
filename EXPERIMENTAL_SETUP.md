# 🧪 Experimental Chat Dashboard Setup

This guide shows you how to run the **full working chat interface** with AI memory integration.

## 📍 What's Where

### Two Separate Dashboards

1. **Main Dashboard** (http://localhost:3000/dashboard)
   - Simple placeholder UI
   - Won't conflict with other branches
   - Has a link to the experimental lab

2. **Experimental Lab** (http://localhost:3000/experimental) ⭐
   - **Full working chat with AI**
   - PostgreSQL persistent memory
   - Real-time memory visualization
   - Analytics and configuration

## 🚀 How to Run

### Step 1: Start the Backend (Experimental Server)

Open a terminal:

```bash
cd packages/backend
poetry run python experiments/web/dashboard_server.py
```

You should see:
```
================================================================================
🧪 Experimental Agent Dashboard
================================================================================
📊 Dashboard: http://0.0.0.0:8001
📚 API Docs: http://0.0.0.0:8001/docs
...
✅ Chat API enabled
================================================================================
```

**Important:** Look for `✅ Chat API enabled` - if you see this, the chat will work!

### Step 2: Start the Frontend (Next.js)

Open **another terminal**:

```bash
cd packages/frontend
npm run dev
```

You should see:
```
▲ Next.js 15.5.6
- Local:        http://localhost:3000
```

### Step 3: Open the Experimental Lab

Navigate to: **http://localhost:3000/experimental**

You should see:
- 🟢 Green dot = Backend connected (ready to chat!)
- 🔴 Red dot = Backend offline (follow the on-screen instructions)

## 💬 Using the Chat

1. Click the **Chat** tab
2. Type a message and press Enter
3. Watch as the AI:
   - Searches memories for relevant context
   - Generates a personalized response
   - Extracts facts from your message
   - Creates new memories

### Example Conversation

```
You: I love hiking in the mountains on weekends

AI: That sounds wonderful! I'll remember that you enjoy hiking...

🧠 Memories Retrieved: (none yet - first message)
✨ Memories Created:
  - User enjoys hiking in mountains
  - User hikes on weekends
```

```
You: What do I like to do?

AI: Based on what you've told me, you love hiking in the mountains
on weekends!

🧠 Memories Retrieved:
  - User enjoys hiking in mountains (score: 0.89)
  - User hikes on weekends (score: 0.85)
```

## 📊 Other Features

### Memories Tab
- Browse all stored memories
- Filter by type (personal, project, task, fact)
- Search by content
- Delete individual memories
- See categories automatically assigned to each memory

### Analytics Tab
- Total memories count
- Token usage and costs (OpenAI API)
- Memory distribution by type
- Top categories

### Config Tab
- Change AI models (GPT-4o-mini, GPT-4o, etc.)
- Adjust search similarity threshold
- Configure fact extraction settings
- Set hybrid search weights

## 🔧 Technical Details

### What's Running

**Backend (port 8001):**
- FastAPI server
- Chat API endpoint: `POST /api/chat/message`
- Memory management APIs
- Analytics APIs
- Configuration APIs

**Frontend (port 3000):**
- Next.js App Router
- React components for chat/memories/analytics
- API client connects to backend
- Real-time health checking

**Database:**
- PostgreSQL (via Supabase or local)
- Stores memories with embeddings
- Uses pgvector for semantic search

**AI:**
- OpenAI GPT-4o-mini for chat
- text-embedding-3-small for embeddings
- Fact extraction from messages
- Automatic categorization

## 🐛 Troubleshooting

### Backend shows "Using mock storage and analytics"
This is okay for basic testing, but for full functionality:
- Make sure your `.env` has `DATABASE_URL` set
- Check that PostgreSQL is accessible

### Chat returns error "Failed to connect to backend"
1. Make sure backend is running (Step 1)
2. Check that you see `✅ Chat API enabled` in backend logs
3. Verify CORS is working (check browser console for errors)

### "Import errors" in backend
```bash
cd packages/backend
poetry install  # Reinstall dependencies
```

### Port already in use
```bash
# Backend on different port
poetry run uvicorn experiments.web.dashboard_server:app --port 8002

# Update frontend API client baseUrl to match
```

## 📁 File Structure

```
packages/
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── dashboard/page.tsx          # Simple placeholder
│       │   └── experimental/page.tsx       # Full chat interface ⭐
│       ├── components/experimental/
│       │   ├── ChatInterface.tsx           # Chat UI
│       │   ├── MemoryVisualization.tsx     # Memory browser
│       │   ├── AnalyticsDashboard.tsx      # Analytics
│       │   └── ConfigurationPanel.tsx      # Config
│       └── lib/
│           ├── api/experimental-client.ts  # API client
│           └── hooks/useExperimentalAPI.ts # React hooks
└── backend/
    └── experiments/
        └── web/
            ├── dashboard_server.py         # Main FastAPI app
            └── chat_api.py                 # Chat endpoint ⭐
```

## 🎯 What Makes It "Experimental"

This is called "experimental" because:
- It's isolated from the main dashboard (no merge conflicts!)
- Uses the experimental agent features (from `experimental-agent` branch)
- Full PostgreSQL integration (not just UI mockups)
- Real AI chat with persistent memory
- Can be tested without affecting main dashboard development

## ⚡ Quick Commands

```bash
# Terminal 1 - Backend
cd packages/backend && poetry run python experiments/web/dashboard_server.py

# Terminal 2 - Frontend
cd packages/frontend && npm run dev

# Then open: http://localhost:3000/experimental
```

## 🔗 API Endpoints

Once backend is running, check out:
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health
- Chat Health: http://localhost:8001/api/chat/health

Enjoy experimenting! 🧪
