# LangGraph Studio Setup Guide

**Purpose:** Visual debugging and testing of the Eliza AI agent using LangGraph Studio.

---

## Quick Start (5 minutes)

### 1. Prerequisites

- **Poetry installed** (backend dependency manager)
- **OpenAI API key** configured in `packages/backend/.env`
- **Backend dependencies installed**: `poetry install`

### 2. Start LangGraph Studio

```bash
# Navigate to backend package
cd packages/backend

# Start Studio server
poetry run langgraph dev

# Opens at: http://localhost:8123
```

### 3. What You'll See

**Visual Graph:**
- `recall_context` → `analyze_emotion` → `generate_response`
- Click nodes to inspect code
- See state transitions in real-time

**Test Interface:**
- Send test messages to Eliza
- See retrieved memories (currently mocked)
- Monitor token usage per node
- Debug state at each step

---

## Architecture Decision

### Why `langgraph.json` is in `packages/backend/`

LangGraph Studio is a **backend development tool** for debugging the Eliza agent. Following monorepo best practices:

- ✅ **Backend tools live in backend package** (pytest, ruff, langgraph-cli)
- ✅ **Frontend tools live in frontend package** (next, playwright, eslint)
- ✅ **Run from respective directories** (`cd packages/backend && poetry run ...`)

This keeps the architecture clean and consistent.

### File Structure

```
packages/backend/
├── langgraph.json          # Studio config (lives here with other backend tools)
├── pyproject.toml          # Poetry dependencies (includes langgraph-cli)
├── app/
│   └── agents/
│       └── eliza_agent.py  # LangGraph agent implementation
└── .env                    # OpenAI API key (required)
```

---

## Configuration

**`langgraph.json` (packages/backend/langgraph.json):**

```json
{
  "dependencies": ["."],                        // Current directory (backend)
  "graphs": {
    "eliza": "app.agents.eliza_agent:graph"    // Path to compiled graph
  },
  "env": ".env"                                 // Environment variables
}
```

**Key paths are relative to `packages/backend/`** since config lives there.

---

## Eliza Agent Architecture

### State Machine

```python
ElizaState = {
    "messages": List[BaseMessage],           # Conversation history
    "retrieved_memories": List[Memory],      # Vector search results
    "emotional_state": Dict,                 # Detected emotions
    "user_context": Dict                     # Additional context
}
```

### Node Flow

1. **`recall_context`**: Query memories via vector similarity
   - Currently: Returns empty list (mock)
   - Future (Story 2.3): Integrates with MemoryService

2. **`analyze_emotion`**: Detect emotional state
   - Currently: Simple keyword detection (MVP)
   - Future (Story 2.6): cardiffnlp/roberta emotion model

3. **`generate_response`**: Generate empathetic response
   - Model: GPT-4o-mini (streaming)
   - Context: System prompt + memories + emotions + history

---

## Usage Examples

### Test Basic Response

**Input in Studio:**
```
Hello, I'm new here
```

**Expected Flow:**
1. `recall_context`: Returns [] (no memories yet)
2. `analyze_emotion`: Detects neutral (intensity: 0.3)
3. `generate_response`: Warm greeting from Eliza

### Test Emotion Detection

**Input:**
```
I'm feeling overwhelmed with my schoolwork
```

**Expected Flow:**
1. `recall_context`: Returns [] (mock)
2. `analyze_emotion`: Detects "fear" (intensity: 0.7)
   - Keywords: "overwhelmed"
   - Triggers: ["stress", "overwhelm"]
3. `generate_response`: Empathetic response acknowledging stress

### Test Memory Context (Future)

Once MemoryService is integrated (Story 2.3):

**Message 1:**
```
I'm stressed about class registration
```

**Message 2:**
```
I'm feeling anxious
```

**Expected:**
- `recall_context` retrieves Message 1 via vector similarity
- Eliza references past conversation: "I remember you mentioned stress about class registration..."

---

## Development Workflow

### 1. Test Agent Logic in Studio

```bash
cd packages/backend
poetry run langgraph dev
# Open http://localhost:8123
# Send test messages
# Inspect state at each node
```

### 2. Iterate on Agent Code

```python
# Edit app/agents/eliza_agent.py
# Studio auto-reloads on file changes
# Test changes immediately in browser
```

### 3. Add Memory Integration (Story 2.3)

```python
# In _recall_context() node:
if self.memory_service:
    memories = await self.memory_service.query_memories(
        user_id=user_id,
        query_text=last_message,
        limit=5
    )
    state["retrieved_memories"] = memories
```

### 4. Deploy to Production

Once tested in Studio:
- Integrate agent into FastAPI chat endpoint
- Use `agent.generate_response_stream()` for SSE streaming
- Production endpoint: `POST /api/v1/companion/chat`

---

## Troubleshooting

### Issue: `langgraph: command not found`

**Solution:**
```bash
cd packages/backend
poetry install  # Ensure langgraph-cli is installed
poetry run langgraph --version  # Verify
```

### Issue: `Path 'langgraph.json' does not exist`

**Solution:** Make sure you run from `packages/backend/` directory:
```bash
cd packages/backend  # Must run from here
poetry run langgraph dev
```

### Issue: `Cannot import ChatOpenAI`

**Solution:**
```bash
cd packages/backend
poetry add langchain-openai  # Install missing dependency
```

### Issue: `OpenAI API key not found`

**Solution:** Add to `packages/backend/.env`:
```bash
OPENAI_API_KEY=sk-proj-...
```

---

## Next Steps

After testing in Studio:

**Story 2.3 (Build Eliza Agent with LangGraph):**
- Replace mock memory retrieval with real MemoryService
- Add sophisticated memory retrieval strategies
- Integrate emotion detection model

**Story 2.4 (Companion Chat API with SSE):**
- Integrate agent into `/api/v1/companion/chat` endpoint
- Stream responses via Server-Sent Events
- Add conversation persistence

**Story 2.6 (Emotional State Detection):**
- Replace keyword detection with cardiffnlp/roberta model
- Add emotion intensity scoring
- Track emotional state over time

---

## Benefits of Studio Testing

1. **Visual Debugging**: See exactly which node fails and why
2. **State Inspection**: View state transformations at each step
3. **Fast Iteration**: Test changes without full API integration
4. **Token Monitoring**: Track costs before production
5. **Early Validation**: Catch agent logic issues before UI development

**Pro Tip:** Use Studio to test agent behavior before building the chat UI (Story 2.5) - saves hours of debugging!

---

**Last Updated:** 2025-11-18
**Related Stories:** 2.3 (Build Eliza Agent), 2.5 (Chat UI)
**Documentation:** https://langchain-ai.github.io/langgraph/tutorials/
