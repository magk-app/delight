# Testing Eliza Agent via Swagger UI

Since LangGraph Studio has CORS issues, use the **Swagger UI** instead - it works perfectly!

## 1. Start the Server

```bash
cd packages/backend
poetry run langgraph dev
```

## 2. Open Swagger UI

```
http://127.0.0.1:2024/docs
```

## 3. Test the Eliza Graph

### Step 1: List Available Assistants

**Endpoint:** `GET /assistants`

Click "Try it out" → "Execute"

**Expected Response:**
```json
[
  {
    "assistant_id": "eliza",
    "graph_id": "eliza",
    "config": {...}
  }
]
```

### Step 2: Create a Thread (Conversation)

**Endpoint:** `POST /threads`

Click "Try it out" → "Execute"

**Expected Response:**
```json
{
  "thread_id": "some-uuid-here",
  "created_at": "2025-11-18T17:33:00Z"
}
```

Copy the `thread_id` - you'll need it!

### Step 3: Send a Message to Eliza

**Endpoint:** `POST /threads/{thread_id}/runs`

1. Click "Try it out"
2. Paste your `thread_id` from Step 2
3. In the request body, use:

```json
{
  "assistant_id": "eliza",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": "Hello, I'm feeling overwhelmed with my schoolwork"
      }
    ]
  }
}
```

4. Click "Execute"

**Expected Response:**
```json
{
  "run_id": "some-run-id",
  "thread_id": "your-thread-id",
  "status": "pending",
  ...
}
```

### Step 4: Get the Response

**Endpoint:** `GET /threads/{thread_id}/runs/{run_id}`

1. Click "Try it out"
2. Paste `thread_id` and `run_id`
3. Click "Execute"

**Expected Response:**
```json
{
  "status": "success",
  "output": {
    "messages": [
      {
        "role": "user",
        "content": "Hello, I'm feeling overwhelmed with my schoolwork"
      },
      {
        "role": "assistant",
        "content": "I hear you're feeling overwhelmed with schoolwork. That's a really common feeling, especially when there's a lot on your plate..."
      }
    ]
  }
}
```

## 4. Verify Agent Behavior

### Test 1: Emotion Detection

**Input:**
```json
{
  "assistant_id": "eliza",
  "input": {
    "messages": [{"role": "user", "content": "I'm stressed about exams"}]
  }
}
```

**Expected:** Eliza detects "fear" emotion (stress keywords) and responds empathetically

### Test 2: Neutral Conversation

**Input:**
```json
{
  "assistant_id": "eliza",
  "input": {
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
  }
}
```

**Expected:** Eliza responds with warm greeting (neutral emotion detected)

### Test 3: Multi-Turn Conversation

Use the same `thread_id` for multiple runs to maintain conversation history:

**Message 1:**
```json
{"messages": [{"role": "user", "content": "I'm working on my goals"}]}
```

**Message 2 (same thread_id):**
```json
{"messages": [{"role": "user", "content": "Can you help me?"}]}
```

**Expected:** Second response has context from first message

## 5. Debug with State Inspector

The API response includes the full state after each node:

```json
{
  "status": "success",
  "output": {
    "messages": [...],
    "retrieved_memories": [],
    "emotional_state": {
      "dominant": "fear",
      "intensity": 0.7,
      "triggers": ["stress", "overwhelm"]
    }
  }
}
```

You can see:
- ✅ What memories were retrieved (currently empty - mocked)
- ✅ Detected emotional state
- ✅ Full conversation history
- ✅ Agent's reasoning

## Benefits Over Cloud Studio

✅ **No CORS issues** - runs locally
✅ **No account required** - works immediately
✅ **Full API testing** - all endpoints available
✅ **Request/Response inspection** - see exactly what's happening
✅ **Easy debugging** - clear error messages

## Next: Integrate with Frontend

Once tested via Swagger, integrate into your chat API:

```python
from app.agents.eliza_agent import ElizaAgent

agent = ElizaAgent()

# In your chat endpoint
async for token in agent.generate_response_stream(
    user_message="Hello",
    conversation_history=[],
):
    yield token  # Stream to frontend via SSE
```

**Pro Tip:** Test all agent behavior in Swagger first before building the chat UI!
