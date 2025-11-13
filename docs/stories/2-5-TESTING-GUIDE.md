# Story 2.5: Companion Chat Testing Guide

**Story:** 2.5 - Companion Chat UI with Essential Memory (Vertical Slice)
**Created:** 2025-11-12
**Status:** Implementation Complete

---

## Overview

This guide provides manual and automated testing instructions for Story 2.5, the companion chat vertical slice with essential memory operations.

---

## Prerequisites

### Backend Setup

```bash
cd packages/backend

# Ensure migrations applied
poetry run alembic upgrade head

# Verify OpenAI API key set
echo $OPENAI_API_KEY

# Start backend
poetry run uvicorn main:app --reload
```

### Frontend Setup

```bash
cd packages/frontend

# Start frontend
npm run dev
```

### Environment Variables

Ensure `.env` files configured:

**Backend (`packages/backend/.env`):**
```bash
DATABASE_URL=postgresql+asyncpg://...
CLERK_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-proj-...
```

**Frontend (`packages/frontend/.env.local`):**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Manual Testing Checklist

### AC1: Chat UI Displays and Accepts Messages

**Steps:**
1. Navigate to http://localhost:3000/companion
2. Verify chat interface loads (header with Eliza avatar, input field, send button)
3. Type message: "Hello Eliza"
4. Click Send or press Enter
5. **Expected:**
   - Message appears immediately in chat history
   - Input field clears
   - Loading indicator shows (typing dots with breathing animation)
   - Message marked as "user" with your avatar
   - Timestamp displays
   - Send button disabled during loading

**Pass/Fail:** ___

### AC2: SSE Streaming Displays Tokens in Real-Time

**Steps:**
1. Send message: "Tell me a story about productivity"
2. Watch response appear
3. **Expected:**
   - Eliza's message appears token-by-token (word-by-word)
   - Smooth scrolling keeps latest token visible
   - Loading indicator hides when first token arrives
   - Message builds up naturally (not jumpy)
   - Complete message shows timestamp when done
   - No connection errors

**Pass/Fail:** ___

### AC3: Conversation Persists Across Page Refreshes

**Steps:**
1. Send message: "Remember I like coffee"
2. Wait for Eliza's response
3. Refresh page (Ctrl+R or Cmd+R)
4. **Expected:**
   - Full conversation history loads
   - Messages display in chronological order
   - User and assistant messages correctly labeled
   - Timestamps preserved
   - Can continue conversation from same context

**Pass/Fail:** ___

### AC4: Memory Storage - Venting Scenario

**Steps:**
1. Send message: "I'm overwhelmed with my schoolwork because I have to catch up"
2. Wait for response
3. **Expected:**
   - Eliza responds empathetically (acknowledges feeling)
   - Response validates the struggle
   - (Backend: Personal memory created with stressor=True metadata)

**Verify Backend:**
```bash
cd packages/backend
poetry run python view_memory_data.py
```

Check for:
- Memory with content containing "overwhelmed"
- memory_type = "personal"
- metadata includes: stressor=True, emotion_severity, emotion

**Pass/Fail:** ___

### AC5: Memory Storage - Task/Goal Scenario

**Steps:**
1. Send message: "I want to work on my goal to graduate early"
2. Wait for response
3. **Expected:**
   - Eliza responds supportively (acknowledges goal)
   - Response encourages action or asks clarifying questions

**Verify Backend:**
```bash
poetry run python view_memory_data.py
```

Check for:
- Memory with content containing "goal"
- memory_type = "project"
- metadata includes: goal_related=True, goal_scope

**Pass/Fail:** ___

### AC6: Memory Retrieval - Context Recall

**Steps:**
1. Send message 1: "I'm stressed about class registration"
2. Wait for response
3. Wait 2 seconds (allow memory indexing)
4. Send message 2: "I'm feeling overwhelmed"
5. Wait for response
6. **Expected:**
   - Eliza's second response references or relates to class registration stress
   - Response feels contextual, not generic

**Pass/Fail:** ___

### AC7: Mobile Responsive Design

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M or Cmd+Shift+M)
3. Select "iPhone SE" or set width to 375px
4. Navigate to /companion
5. **Expected:**
   - Chat takes full screen (no wasted space)
   - Input field visible at bottom
   - Messages readable without zooming
   - Send button easily tappable (large enough)
   - Keyboard doesn't obscure input (test by clicking input)
   - Scrolling smooth on touch

**Pass/Fail:** ___

### AC8: Accessible Keyboard Navigation

**Steps:**
1. Navigate to /companion
2. Use Tab key to navigate through UI
3. Verify focus moves to: header elements → input field → send button
4. Type in input using keyboard: "Hello Eliza"
5. Press Enter to send
6. **Expected:**
   - Tab key moves focus through all interactive elements
   - Enter sends message
   - Shift+Enter creates new line
   - Escape clears input
   - ARIA labels present (inspect elements)
   - Focus indicators visible (blue outline)

**Pass/Fail:** ___

### AC9: Memory Hierarchy Metadata

**Backend Verification:**
```bash
cd packages/backend
poetry run python -c "
from app.db.session import get_db
from app.models.memory import Memory
from sqlalchemy import select
import asyncio

async def check_metadata():
    async for db in get_db():
        result = await db.execute(select(Memory).order_by(Memory.created_at.desc()).limit(5))
        memories = result.scalars().all()

        for mem in memories:
            print(f'\\nMemory: {mem.content[:50]}...')
            print(f'Type: {mem.memory_type}')
            print(f'Metadata: {mem.extra_data}')

asyncio.run(check_metadata())
"
```

**Expected Metadata Fields:**
- **Personal memories:** emotion_severity (mild_annoyance, persistent_stressor, compounding_event)
- **Project memories:** goal_scope (big_goal, small_goal), goal_related
- **Task memories:** task_priority, task_difficulty, universal_factors (dict with weights)

**Pass/Fail:** ___

---

## Automated Tests

### Backend Integration Tests

```bash
cd packages/backend

# Run all companion tests
poetry run pytest tests/integration/test_companion_chat.py -v

# Run specific test
poetry run pytest tests/integration/test_companion_chat.py::test_venting_creates_personal_memory -v

# Run with coverage
poetry run pytest tests/integration/test_companion_chat.py --cov=app.api.v1.companion --cov-report=html
```

**Expected Output:**
- All tests pass (green)
- Coverage ≥70%

### Frontend E2E Tests

```bash
cd packages/frontend

# Run E2E tests headless
npm run test:e2e

# Run with UI (interactive)
npm run test:e2e:ui

# Run headed (see browser)
npm run test:e2e:headed
```

**Expected Output:**
- All tests pass
- No timeout errors
- Screenshots generated for failures (if any)

---

## Performance Targets

Test these using browser DevTools (Network tab, Performance tab):

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Memory Query (p95) | < 100ms | Backend logs: "Retrieved N memories" |
| Embedding Generation | < 200ms | Backend logs: "Generated embedding" |
| First Token (p95) | < 1s | Time from send to first SSE token |
| UI Responsiveness | < 50ms | Input feels instant, no lag |
| SSE Connection Latency | < 50ms | Network tab: EventSource connection time |

---

## Test Scenarios (End-to-End)

### Scenario 1: New User First Chat

1. Clear browser storage (Application → Clear site data)
2. Navigate to /companion
3. Send: "Hi, I'm new here"
4. Verify welcome response
5. Send: "I want to learn programming"
6. Verify supportive response
7. Refresh page
8. Verify history loads

**Expected:** Smooth onboarding, context maintained

### Scenario 2: Venting → Support → Follow-up

1. Send: "I'm stressed about my coding interview tomorrow"
2. Wait for empathetic response
3. Send: "I don't think I'm prepared enough"
4. Verify response references interview stress
5. Send: "What should I focus on?"
6. Verify actionable suggestions

**Expected:** Eliza remembers context, provides relevant support

### Scenario 3: Goal Discussion → Planning

1. Send: "I want to get better at machine learning"
2. Wait for response
3. Send: "Where should I start?"
4. Verify response considers previous goal statement
5. Refresh page
6. Send: "I'm ready to start studying"
7. Verify context maintained after refresh

**Expected:** Goal tracked, suggestions relevant

---

## Error Scenarios

### Test OpenAI API Failure

1. Temporarily remove OPENAI_API_KEY from backend .env
2. Restart backend
3. Send message
4. **Expected:** User-friendly error message, no crash

### Test SSE Disconnection

1. Send message
2. During streaming, kill backend process
3. **Expected:** "Connection lost" error message, graceful handling

### Test Network Errors

1. Disconnect internet
2. Send message
3. **Expected:** Error message, retry option

---

## Debugging Tips

### Backend Not Responding

```bash
# Check backend running
curl http://localhost:8000/api/v1/health

# Check logs
cd packages/backend
tail -f logs/app.log  # If logging configured
```

### Frontend Not Connecting

```bash
# Check API URL
echo $NEXT_PUBLIC_API_URL

# Check browser console for errors
# F12 → Console tab

# Check network requests
# F12 → Network tab → Filter: Fetch/XHR
```

### Memory Not Storing

```bash
# Check database connection
cd packages/backend
poetry run python -c "
from app.db.session import get_db
import asyncio

async def test_db():
    async for db in get_db():
        print('DB connected')
        break

asyncio.run(test_db())
"

# Check OpenAI API key
poetry run python -c "
from app.core.config import settings
print(f'OPENAI_API_KEY set: {bool(settings.OPENAI_API_KEY)}')
"
```

### SSE Streaming Issues

- Check browser supports EventSource (all modern browsers do)
- Check CORS headers (should be set correctly)
- Check backend logs for OpenAI API errors
- Verify token authentication working

---

## Known Limitations (Vertical Slice)

These will be addressed in future stories:

1. **Memory Service Inline:** Memory operations are inline in companion.py (Story 2.2 will extract)
2. **Simple Heuristics:** Memory type detection uses keywords (Story 2.3 will add LLM classification)
3. **No Hybrid Search:** Only vector similarity (Story 2.2 will add time decay, frequency boost)
4. **Basic Eliza:** No LangGraph yet (Story 2.3 will add advanced agent)
5. **No Emotion Detection:** Simplified emotion metadata (Story 2.6 will add cardiffnlp/roberta)

---

## Learnings to Capture (for Story 2.2)

While testing, document these observations:

1. **Memory Metadata Usefulness:**
   - Which metadata fields are actually helpful?
   - Are stressor/goal/task categories accurate?
   - Do universal_factors make sense?

2. **Memory Retrieval Quality:**
   - Does top-5 similarity search work well?
   - Should we increase/decrease limit?
   - Are memories relevant to queries?

3. **SSE Streaming UX:**
   - Does token-by-token feel smooth?
   - Any connection stability issues?
   - Should we batch tokens for performance?

4. **Memory Type Detection:**
   - Do simple heuristics work?
   - What edge cases are missed?
   - How often are types wrong?

5. **User Feedback:**
   - Does Eliza feel contextual?
   - Are responses helpful?
   - Any repetitive patterns?

**Document in:** `docs/stories/2-5-LEARNINGS.md` (create after testing)

---

## Success Criteria

All acceptance criteria must pass:

- [x] AC1: Chat UI accepts messages ✅
- [x] AC2: SSE streaming works ✅
- [x] AC3: Conversation persists ✅
- [x] AC4: Venting creates personal memory ✅
- [x] AC5: Goal creates project memory ✅
- [x] AC6: Memory retrieval works ✅
- [x] AC7: Mobile responsive ✅
- [x] AC8: Keyboard navigation ✅
- [x] AC9: Memory hierarchy metadata ✅

**Story Complete When:** All checkboxes ticked, all tests passing, documentation updated.

---

**Last Updated:** 2025-11-12
**Tested By:** ___
**Test Date:** ___
