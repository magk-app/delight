# Goal-Driven State Transitions and Tool-Aware Processing

This document describes the implementation of goal-driven AI agents using LangGraph, demonstrating state-driven decision making and tool-aware processing.

## Overview

The implementation provides a framework for building AI agents that:

1. **Maintain goal-oriented state** - Track what the user wants, what's been done, and what's needed
2. **Make tool-aware decisions** - Know what tools do, when to use them, and avoid redundancy
3. **Follow structured workflows** - Progress through well-defined states with clear transitions
4. **Handle uncertainty** - Ask clarifying questions when information is missing
5. **Track progress** - Monitor iterations, tool usage, and confidence levels

## Architecture

### Core Components

```
app/agents/
├── tools/
│   ├── base.py           # Base tool interface and abstractions
│   ├── calculator.py     # Example calculator tool
│   ├── tool_store.py     # Tool registry and execution manager
│   └── __init__.py
├── state.py              # State management and transitions
├── graph.py              # LangGraph implementation
└── __init__.py
```

### Component Responsibilities

**Tool Store** (`tools/tool_store.py`):
- Central registry for all available tools
- Manages tool discovery and selection
- Tracks tool execution history
- Validates tool prerequisites against state

**State Manager** (`state.py`):
- Defines agent states and valid transitions
- Manages the information "blackboard"
- Tracks goal progress and completion
- Prevents invalid state transitions

**Goal-Driven Agent** (`graph.py`):
- Implements LangGraph workflow
- Routes between states based on context
- Executes tools and processes results
- Synthesizes final responses

## State Machine

### States

The agent progresses through these states:

1. **INITIALIZE** - Parse user request and identify goal
2. **PLANNING** - Create execution plan
3. **CLARIFYING** - Ask user for missing information
4. **TOOL_SELECTION** - Choose appropriate tools
5. **TOOL_EXECUTION** - Execute selected tools
6. **ANALYSIS** - Process tool outputs
7. **SYNTHESIS** - Combine information into response
8. **COMPLETION** - Task finished
9. **ERROR** - Handle errors

### State Transitions

Valid transitions are explicitly defined to ensure logical flow:

```
INITIALIZE → [PLANNING, CLARIFYING, ERROR]
PLANNING → [CLARIFYING, TOOL_SELECTION, SYNTHESIS, ERROR]
TOOL_SELECTION → [TOOL_EXECUTION, CLARIFYING, ERROR]
TOOL_EXECUTION → [ANALYSIS, ERROR]
ANALYSIS → [TOOL_SELECTION, SYNTHESIS, CLARIFYING, ERROR]
SYNTHESIS → [COMPLETION, ANALYSIS, ERROR]
ERROR → [CLARIFYING, COMPLETION]
COMPLETION → [terminal]
```

### The Information Blackboard

The `GraphState` serves as a shared "blackboard" where:
- **Goal information** is stored and tracked
- **Tool outputs** are shared across nodes
- **Required vs. available information** is monitored
- **Execution history** is maintained

This enables:
- Tools to share data without redundant fetches
- Decision logic to check if information is available
- Progress tracking across iterations

## Tool System

### Tool Interface

All tools inherit from `BaseTool` and implement:

```python
class BaseTool(ABC):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def category(self) -> ToolCategory: ...

    @property
    def input_schema(self) -> type[ToolInput]: ...

    @property
    def required_context(self) -> List[str]: ...

    @property
    def provides_context(self) -> List[str]: ...

    async def execute(self, input_data: ToolInput, context: Dict) -> ToolOutput: ...
```

### Tool Awareness Features

**Prerequisites**: Tools declare what context they need

```python
@property
def required_context(self) -> List[str]:
    return ["user_id", "calculation_params"]
```

**Provides**: Tools declare what they add to state

```python
@property
def provides_context(self) -> List[str]:
    return ["calculation_result", "formula"]
```

**Validation**: Tool store checks prerequisites before execution

```python
can_execute, reason = tool_store.check_tool_prerequisites(
    "calculator",
    state_context
)
```

**Execution Tracking**: All executions are logged with metadata

```python
{
    "tool_name": "calculator",
    "success": True,
    "execution_time": 0.003,
    "result": 8.0,
    "metadata": {"formula": "5 + 3 = 8"}
}
```

## Example: Calculator Tool

The calculator tool demonstrates key concepts:

```python
class CalculatorTool(BaseTool):
    name = "calculator"
    category = ToolCategory.COMPUTATION

    # Declares what it provides to state
    provides_context = ["last_calculation_result"]

    async def execute(self, input_data, context):
        # Validates inputs
        # Handles edge cases (division by zero, negative sqrt)
        # Returns structured output
        return ToolOutput(
            success=True,
            result=8.0,
            metadata={"formula": "5 + 3 = 8"}
        )
```

## Goal-Driven Decisions

### How Goals Drive Behavior

1. **Goal Parsing**: User request → structured Goal object

```python
goal = Goal(
    description="Perform calculation: add 5 and 3",
    required_info=["operands", "operation"],
    completion_criteria="Calculation result obtained"
)
```

2. **Information Tracking**: Compare required vs. available

```python
state["required_information"] = ["operands", "operation"]
state["available_information"] = {"operands": [5, 3], "operation": "add"}

# Decision logic
if StateManager.has_required_information(state):
    # Proceed with execution
else:
    # Ask for clarification
```

3. **Tool Selection**: Find tools that help achieve goal

```python
tools = tool_store.find_tools_for_goal(
    goal.description,
    state["available_information"]
)
```

4. **Progress Checking**: Determine if goal is achieved

```python
if StateManager.is_goal_achieved(state):
    transition_to(AgentState.SYNTHESIS)
else:
    transition_to(AgentState.TOOL_SELECTION)
```

### Avoiding Redundancy

The agent tracks tool usage to avoid redundant calls:

```python
if not StateManager.was_tool_used(state, "calculator"):
    # Use the tool
else:
    # Reuse previous result
    result = StateManager.get_tool_result(state, "calculator")
```

## Routing Logic

Each state has conditional routing based on context:

```python
def _route_from_analysis(state: GraphState) -> str:
    """Route based on confidence and information availability"""

    if state["confidence"] > 0.7:
        return "synthesis"  # High confidence → create response

    elif not StateManager.has_required_information(state):
        return "tool_selection"  # Need more data → use tools

    elif state["iterations"] > 10:
        return "synthesis"  # Prevent infinite loops

    else:
        return "synthesis"  # Try to synthesize with what we have
```

## Running the Agent

### Basic Usage

```python
from app.agents.graph import GoalDrivenAgent

agent = GoalDrivenAgent()

result = await agent.run("calculate 5 + 3")

print(result)
# {
#     "success": True,
#     "response": "Goal: Perform calculation\nTool Results:\n  - calculator: 8.0",
#     "iterations": 6,
#     "tool_executions": 1,
#     "confidence": 0.9,
#     "error": None
# }
```

### Execution Flow

For request "calculate 5 + 3":

1. **INITIALIZE**: Parse goal, identify "calculation" task
2. **PLANNING**: Create plan: gather info → use calculator → synthesize
3. **TOOL_SELECTION**: Select calculator tool (matches goal)
4. **TOOL_EXECUTION**: Execute calculator with operands
5. **ANALYSIS**: Check result, confidence = 0.9
6. **SYNTHESIS**: Combine tool output into response
7. **COMPLETION**: Return result to user

## Testing

### Test Structure

```
tests/test_agents/
├── test_tool_store.py    # Tool system tests
├── test_state.py         # State management tests
└── test_graph.py         # Integration tests
```

### Running Tests

```bash
cd packages/backend
poetry run pytest tests/test_agents/ -v
```

### Test Coverage

**Tool Store Tests** (`test_tool_store.py`):
- Calculator operations (add, subtract, multiply, divide, sqrt, abs)
- Error handling (division by zero, negative sqrt)
- Tool registration and discovery
- Execution tracking and history
- Prerequisites checking

**State Tests** (`test_state.py`):
- State transition validation
- Information tracking
- Goal achievement checking
- Tool usage tracking
- Complete workflow scenarios

**Integration Tests** (`test_graph.py`):
- End-to-end agent execution
- Node-level testing
- Routing logic validation
- Multiple request handling
- Redundancy avoidance

## Key Design Decisions

### 1. Explicit State Transitions

**Why**: Prevents invalid workflows and ensures predictable behavior

```python
# Invalid transition raises error
StateManager.transition_to(
    state,
    AgentState.COMPLETION,  # Can't go directly from INITIALIZE
    "Skip to end"
)
# ValueError: Invalid state transition
```

### 2. Tool Prerequisites & Provides

**Why**: Enables the agent to reason about tool usage

```python
# Agent can ask: "Do I have what this tool needs?"
can_use, reason = tool.can_execute(state_context)

# Agent knows: "What will I get if I use this tool?"
if "calculation_result" in tool.provides_context:
    # This tool will give me the result I need
```

### 3. Shared State Blackboard

**Why**: Enables information sharing without coupling

```python
# Tool A writes
state["available_information"]["user_preferences"] = {...}

# Tool B reads (no direct dependency on Tool A)
prefs = state["available_information"].get("user_preferences")
```

### 4. Iteration Limits

**Why**: Prevents infinite loops in edge cases

```python
if state["iterations"] > 10:
    # Force progress to completion
    return "synthesis"
```

## Extending the System

### Adding a New Tool

1. Create tool class inheriting from `BaseTool`
2. Implement required properties and `execute` method
3. Register in tool store initialization

```python
# app/agents/tools/search_tool.py
class SearchTool(BaseTool):
    name = "web_search"
    category = ToolCategory.DATA_RETRIEVAL
    required_context = ["search_query"]
    provides_context = ["search_results"]

    async def execute(self, input_data, context):
        # Implementation
        pass

# Register
def _initialize_default_tools():
    store = get_tool_store()
    store.register_tool(CalculatorTool())
    store.register_tool(SearchTool())  # Add here
```

### Adding a New State

1. Add to `AgentState` enum
2. Define valid transitions in `StateManager.VALID_TRANSITIONS`
3. Add node to graph and routing logic

```python
# state.py
class AgentState(str, Enum):
    # ... existing states
    VALIDATION = "validation"

# Add transitions
VALID_TRANSITIONS = {
    AgentState.SYNTHESIS: [
        AgentState.VALIDATION,  # New transition
        AgentState.COMPLETION
    ],
    AgentState.VALIDATION: [AgentState.COMPLETION, AgentState.ANALYSIS]
}

# graph.py
workflow.add_node("validation", self._validation_node)
workflow.add_conditional_edges("validation", self._route_from_validation)
```

## Best Practices

### 1. Design Tools as Pure Functions

Tools should be stateless and deterministic when possible:

```python
# Good: Pure, deterministic
async def execute(self, input_data, context):
    return input_data["a"] + input_data["b"]

# Avoid: Stateful, side-effects
async def execute(self, input_data, context):
    self.counter += 1  # Stateful
    requests.post(...)  # External side-effect
```

### 2. Validate Tool Inputs Thoroughly

Use Pydantic schemas to catch errors early:

```python
class CalculatorInput(ToolInput):
    operation: Literal["add", "subtract", ...]
    operand1: float
    operand2: Optional[float] = None
```

### 3. Provide Clear Error Messages

Help the agent (and humans) understand what went wrong:

```python
if operand2 == 0:
    return ToolOutput(
        success=False,
        error="Cannot divide by zero. Provide a non-zero divisor."
    )
```

### 4. Track Execution Metadata

Include useful debugging information:

```python
return ToolOutput(
    success=True,
    result=8.0,
    metadata={
        "formula": "5 + 3 = 8",
        "execution_time": 0.003,
        "operation": "add"
    }
)
```

### 5. Design Goals with Clear Completion Criteria

Make it easy to determine when a goal is achieved:

```python
goal = Goal(
    description="Calculate user's total expenses",
    required_info=["expense_list"],
    completion_criteria="Sum calculated and formatted"
)
```

## Performance Considerations

### Tool Store Caching

The tool store tracks execution history to enable result reuse:

```python
# First request: execute tool
result1 = await agent.run("calculate 5 + 3")  # Executes calculator

# If state preserved: reuse result
if StateManager.was_tool_used(state, "calculator"):
    result = StateManager.get_tool_result(state, "calculator")
```

### Iteration Limits

Prevent runaway execution with iteration caps:

```python
if state["iterations"] > 10:
    # Force conclusion
    return "completion"
```

### Parallel Tool Execution (Future Enhancement)

Current implementation executes tools sequentially. Could be enhanced:

```python
# Sequential (current)
for tool in selected_tools:
    await execute_tool(tool)

# Parallel (future)
results = await asyncio.gather(*[
    execute_tool(tool) for tool in selected_tools
])
```

## Future Enhancements

### 1. LLM Integration for Goal Parsing

Replace simple keyword matching with LLM-based understanding:

```python
def _parse_goal(self, user_request: str) -> Goal:
    # Use LLM to understand intent and extract goal structure
    response = await llm.complete(
        f"Parse this request into a goal: {user_request}"
    )
    return Goal.parse_obj(response)
```

### 2. Dynamic Tool Input Generation

Use LLM to generate appropriate tool inputs:

```python
def _generate_tool_input(self, state, tool_name):
    # Use LLM to determine correct parameters
    return await llm.complete(
        f"Generate {tool_name} input for: {state['goal']}"
    )
```

### 3. Semantic Tool Discovery

Use embeddings to match goals with tools:

```python
goal_embedding = embed(goal.description)
tool_embeddings = {name: embed(tool.description) for name, tool in tools}
# Find most similar tools
```

### 4. Sub-Goal Decomposition

Break complex goals into sub-goals:

```python
goal = Goal(
    description="Calculate monthly budget",
    sub_goals=[
        Goal(description="Sum income"),
        Goal(description="Sum expenses"),
        Goal(description="Calculate difference")
    ]
)
```

### 5. Confidence-Based Retry

Retry with different approaches when confidence is low:

```python
if state["confidence"] < 0.5 and not state["retry_attempted"]:
    # Try alternative approach
    return "alternative_planning"
```

## Troubleshooting

### Agent Gets Stuck in Loop

**Symptom**: Iterations keep increasing without reaching completion

**Solution**: Check routing logic and iteration limits

```python
# Add debug logging
def _route_from_analysis(state):
    print(f"Iteration {state['iterations']}, confidence {state['confidence']}")
    # ... routing logic
```

### Tools Not Being Selected

**Symptom**: No tools selected despite relevant goal

**Solution**: Check `find_tools_for_goal` logic and tool descriptions

```python
# Ensure tool description matches goal keywords
description = "Performs mathematical operations like add, multiply, divide"
```

### Prerequisites Always Failing

**Symptom**: Tools never execute due to missing prerequisites

**Solution**: Verify required context is being populated

```python
# Ensure previous steps populate context
state["available_information"][required_key] = value
```

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Pydantic Models](https://docs.pydantic.dev/latest/)

## Related Documentation

- `/docs/ARCHITECTURE.md` - Overall system architecture
- `/docs/tech-spec-epic-2.md` - AI agents specification
- `/packages/backend/README.md` - Backend development guide
