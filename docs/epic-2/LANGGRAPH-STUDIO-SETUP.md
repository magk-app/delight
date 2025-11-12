# LangGraph Studio Web - Quick Setup Guide

**Purpose**: Visual debugging and testing of Eliza agent before production

---

## Quick Start (5 minutes)

### 1. Install LangGraph CLI

```bash
cd packages/backend
poetry add langgraph-cli
```

### 2. Create Studio Config

**Create `langgraph.json` in project root**:

```json
{
  "dependencies": ["."],
  "graphs": {
    "eliza": "app.agents.eliza_agent:graph"
  },
  "env": ".env"
}
```

### 3. Export Graph for Studio

**Update `app/agents/eliza_agent.py`**:

```python
from langgraph.graph import StateGraph

class ElizaAgent:
    def __init__(self, memory_service=None):
        self.memory_service = memory_service
        self.llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        # ... your graph building code ...
        return graph.compile()

# Export for Studio (can use None for memory_service in Studio)
def get_graph():
    agent = ElizaAgent(memory_service=None)
    return agent.graph

# For Studio
graph = get_graph()
```

### 4. Run Studio

```bash
langgraph dev
```

**Opens**: `http://localhost:8123`

### 5. Test Your Agent

- **Visual Flow**: See agent nodes and edges
- **State Inspection**: View state at each step
- **Debug Mode**: Step through execution
- **Input Testing**: Test with different messages
- **Token Monitoring**: See token usage per node

---

## Studio Features

### Visual Graph Editor
- See all nodes and connections
- Click nodes to inspect code
- View state transitions

### State Inspector
- See state at each step
- Inspect `messages`, `retrieved_memories`, `emotional_state`
- Debug state mutations

### Input/Output Testing
- Test with sample messages
- See full response
- Monitor token usage
- Test error cases

### Debug Mode
- Step through execution
- Pause at each node
- Inspect intermediate states
- Catch bugs early

---

## Testing Workflow

### 1. Test Simple Agent First
```python
# Start with agent that has no memory
# Verify basic flow works
```

### 2. Add Memory Gradually
```python
# Add mock memory service
# Test recall_context node
# Verify memory retrieval works
```

### 3. Test Real Memory
```python
# Connect to real MemoryService
# Test with actual database
# Verify accuracy
```

---

## Common Issues

### Issue: Graph not found
**Solution**: Check `langgraph.json` path matches your graph export

### Issue: Import errors
**Solution**: Ensure all dependencies in `pyproject.toml` are installed

### Issue: State not updating
**Solution**: Check node return values (must return updated state)

---

## Best Practices

1. **Start Simple**: Test agent without memory first
2. **Add Complexity Gradually**: Add memory, then emotion, then streaming
3. **Test Edge Cases**: Empty inputs, long messages, errors
4. **Monitor Tokens**: Watch token usage per node
5. **Debug State**: Inspect state at each step

---

## Example Test Cases

### Test 1: Basic Response
```
Input: "Hello"
Expected: Warm greeting from Eliza
```

### Test 2: Memory Recall
```
Input: "What did we talk about yesterday?"
Expected: References past conversation from memory
```

### Test 3: Emotional Support
```
Input: "I'm feeling overwhelmed"
Expected: Empathetic response, offers support
```

### Test 4: Goal Discussion
```
Input: "I want to work on my goals"
Expected: Queries project memories, discusses goals
```

---

**Pro Tip**: Use Studio to test agent logic before integrating with frontend - saves hours of debugging!


