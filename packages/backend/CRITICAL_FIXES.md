# Critical Fixes Required

## Bug #1: ToolExecution Dictionary Access (MUST FIX)

**Severity**: HIGH - Will cause runtime errors
**Files Affected**: `app/agents/state.py`, `app/agents/graph.py`

### The Problem

`ToolExecution` is a Pydantic BaseModel, but code tries to access it as a dictionary:

```python
# state.py:268 - WRONG
return any(exec["tool_name"] == tool_name for exec in executions)

# state.py:275 - WRONG
if exec["tool_name"] == tool_name and exec["success"]:
    return exec["output"]
```

This will raise `TypeError: 'ToolExecution' object is not subscriptable`

### The Fix

Change all dictionary access to attribute access:

```python
# state.py:268 - CORRECT
return any(exec.tool_name == tool_name for exec in executions)

# state.py:275 - CORRECT
if exec.tool_name == tool_name and exec.success:
    return exec.output
```

### How to Fix

1. Open `app/agents/state.py`
2. Line 268: Change `exec["tool_name"]` → `exec.tool_name`
3. Line 275-276: Change `exec["tool_name"]`, `exec["success"]`, `exec["output"]` → attributes
4. Search for any other dictionary access of `ToolExecution` instances

### Alternative: Convert to Dict

If you prefer to keep dictionary access, modify how ToolExecutions are stored:

```python
# In graph.py when creating ToolExecution
execution = ToolExecution(
    tool_name=tool_name,
    input_data=input_data,
    output=result.result if result.success else None,
    success=result.success,
    error=result.error
)

# Store as dict instead of model:
state["tool_executions"] = [*state.get("tool_executions", []), execution.model_dump()]
```

But this loses type safety, so attribute access is preferred.

---

## Bug #2: Thread Safety in Global Singleton (SHOULD FIX)

**Severity**: MEDIUM - Potential race conditions
**File**: `app/agents/tools/tool_store.py:230-236`

### The Problem

Global singleton without async lock protection:

```python
_global_tool_store: Optional[ToolStore] = None

def get_tool_store() -> ToolStore:
    global _global_tool_store
    if _global_tool_store is None:  # Race condition here
        _global_tool_store = ToolStore()
        _initialize_default_tools()
    return _global_tool_store
```

Multiple concurrent calls could create multiple instances.

### The Fix

Add async lock:

```python
from asyncio import Lock

_tool_store_lock = Lock()
_global_tool_store: Optional[ToolStore] = None

async def get_tool_store() -> ToolStore:
    global _global_tool_store
    if _global_tool_store is None:
        async with _tool_store_lock:
            # Double-check pattern
            if _global_tool_store is None:
                _global_tool_store = ToolStore()
                _initialize_default_tools()
    return _global_tool_store
```

**Note**: This makes `get_tool_store()` async, so all callers must `await` it.

### Better Alternative: Dependency Injection

For FastAPI integration, use dependency injection instead:

```python
# In app/core/dependencies.py
from functools import lru_cache
from app.agents.tools import ToolStore, CalculatorTool

@lru_cache()
def get_tool_store() -> ToolStore:
    """FastAPI dependency for tool store"""
    store = ToolStore()
    store.register_tool(CalculatorTool())
    return store
```

Then in routes:
```python
from fastapi import Depends
from app.core.dependencies import get_tool_store

@router.post("/agent/run")
async def run_agent(
    request: AgentRequest,
    tool_store: ToolStore = Depends(get_tool_store)
):
    agent = GoalDrivenAgent()
    agent.tool_store = tool_store
    return await agent.run(request.text)
```

---

## Quick Test to Verify Bug #1

Run this to reproduce the error:

```python
# test_bug.py
import asyncio
from app.agents.state import StateManager, ToolExecution

async def test_tool_execution_access():
    # Create state with ToolExecution
    state = StateManager.create_initial_state("test")

    execution = ToolExecution(
        tool_name="calculator",
        input_data={"operation": "add"},
        success=True
    )

    state["tool_executions"] = [execution]

    # This will FAIL with current code:
    result = StateManager.was_tool_used(state, "calculator")
    print(f"Was tool used: {result}")

if __name__ == "__main__":
    asyncio.run(test_tool_execution_access())
```

Expected error:
```
TypeError: 'ToolExecution' object is not subscriptable
```

After fix, should print:
```
Was tool used: True
```

---

## Testing After Fixes

Run the test suite:

```bash
cd packages/backend
poetry run pytest tests/test_agents/ -v
```

All tests should pass after fixing Bug #1.
