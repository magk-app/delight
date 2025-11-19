# 🐛 Bug Fixes - Experimental Dashboard

## Issues Fixed

### 1. ❌ Chat API Returning 404
**Problem:** `POST /api/chat/message HTTP/1.1" 404 Not Found`

**Root Cause:**
- Relative import `.chat_api` failed silently
- Router was never included in the FastAPI app
- No error message shown

**Fix:**
- Changed to absolute import `chat_api`
- Added traceback printing for debugging
- Chat router now loads properly

**How to verify:**
```bash
# Restart backend server
cd packages/backend
poetry run python experiments/web/dashboard_server.py

# Look for this in output:
✅ Chat API enabled
✅ Real ChatService loaded with OpenAI + PostgreSQL
```

---

### 2. ❌ Infinite Loop - Maximum Update Depth Exceeded
**Problem:** Console error `Maximum update depth exceeded`

**Root Cause:**
```typescript
// ❌ BAD - filters object creates new reference every render
const refresh = useCallback(async () => {
  const data = await experimentalAPI.getMemories(filters);
  setMemories(data);
}, [filters]); // filters is a new object every time!

useEffect(() => {
  refresh(); // Runs every render -> infinite loop!
}, [refresh]);
```

**The Loop:**
1. Component renders with filters object
2. `useCallback` sees filters changed (new object reference)
3. Creates new `refresh` function
4. `useEffect` sees `refresh` changed
5. Calls `refresh()`
6. Sets state → component re-renders
7. Go to step 1 → **INFINITE LOOP** 🔄

**Fix:**
```typescript
// ✅ GOOD - stringify filters to create stable reference
const filtersString = JSON.stringify(filters || {});

const refresh = useCallback(async () => {
  const parsedFilters = JSON.parse(filtersString);
  const data = await experimentalAPI.getMemories(parsedFilters);
  setMemories(data);
}, [filtersString]); // Only changes when filter VALUES change
```

**How to verify:**
1. Go to http://localhost:3000/experimental
2. Click "Memories" tab
3. No console errors
4. Page loads smoothly without freezing

---

### 3. ✅ Fallback to Mock Chat
**Improvement:** If dependencies aren't available, use mock instead of crashing

**Added:**
```python
try:
    # Try to load real chat service
    from openai import AsyncOpenAI
    chat_service = ChatService()  # Real AI
    print("✅ Real ChatService loaded")
except ImportError:
    # Fall back to mock
    chat_service = MockChatService()  # Echo responses
    print("⚠️  Using MockChatService")
```

---

## Testing Steps

### Test Chat API

**Step 1:** Restart backend
```bash
cd packages/backend
poetry run python experiments/web/dashboard_server.py
```

**Step 2:** Check startup logs
```
✅ Chat API enabled  ← Should see this
✅ Real ChatService loaded with OpenAI + PostgreSQL
```

**Step 3:** Test chat endpoint
```bash
curl -X POST http://localhost:8001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

Should return JSON (not 404):
```json
{
  "response": "...",
  "memories_retrieved": [],
  "memories_created": [],
  "timestamp": "..."
}
```

---

### Test Frontend No Infinite Loop

**Step 1:** Start frontend
```bash
cd packages/frontend
npm run dev
```

**Step 2:** Open http://localhost:3000/experimental

**Step 3:** Open browser console (F12)

**Step 4:** Click "Memories" tab

**Expected:** ✅ No errors, no freezing

**Before fix:** ❌ Console spam with "Maximum update depth exceeded"

---

### Test Full Chat Flow

**With both servers running:**

1. Go to http://localhost:3000/experimental
2. Click "Chat" tab
3. Type: "I love hiking"
4. Press Enter

**Expected:**
- ✅ Loading indicator appears
- ✅ AI responds
- ✅ Shows "Memories Created"
- ✅ No 404 errors in console

---

## Summary

| Issue | Status | Impact |
|-------|--------|--------|
| Chat API 404 | ✅ Fixed | Chat now works |
| Infinite loop | ✅ Fixed | Memories tab loads |
| Mock fallback | ✅ Added | Works without full setup |

All critical bugs resolved! 🎉

---

## Still TODO (Not Bugs)

- Config save functionality (old Python dashboard)
- WebSocket real-time updates
- Graph view for memories

These are features, not bugs. The core chat + memory system now works!
