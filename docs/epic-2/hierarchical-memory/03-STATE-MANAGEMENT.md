# State Management and Goal-Driven Transitions

**Date:** 2025-11-18
**Epic:** Epic 2 - Companion & Memory System
**Purpose:** Design goal-driven state transitions and tool-aware processing for Delight's AI agents

---

## Table of Contents

1. [Overview](#overview)
2. [State Machine Architecture](#state-machine-architecture)
3. [Eliza Agent State Flow](#eliza-agent-state-flow)
4. [Tool-Aware Processing](#tool-aware-processing)
5. [Cross-Epic State Integration](#cross-epic-state-integration)
6. [State Persistence](#state-persistence)
7. [Error Handling and Recovery](#error-handling-and-recovery)

---

## Overview

Delight's AI agents use **goal-driven state machines** to maintain context, orchestrate tools, and make intelligent decisions that progress users toward their goals. The state management system ensures the AI doesn't just react randomly, but follows a coherent workflow aligned with user objectives.

### Core Principles

1. **Goal-Oriented**: Every state transition moves toward completing user goals
2. **Tool-Aware**: State logic knows what tools/services are available and when to use them
3. **Context-Preserving**: State carries conversation history, retrieved memories, and intermediate results
4. **Transparent**: Users can see the AI's current state and reasoning process
5. **Recoverable**: System can gracefully handle errors and resume from last good state

### State Management Across Epics

| Epic | State Management Role | Key States |
|------|----------------------|-----------|
| **Epic 2: Companion & Memory** | Core implementation | `receive_input` → `recall_context` → `reason` → `respond` → `store_memory` |
| **Epic 3: Goal & Mission** | Mission workflow states | `goal_created` → `decompose` → `generate_quests` → `mission_active` → `completed` |
| **Epic 4: Narrative Engine** | Story progression states | `assess_progress` → `select_beat` → `generate_content` → `check_unlocks` |
| **Epic 5: Progress & Analytics** | Analytics calculation states | `collect_data` → `calculate_dci` → `generate_insights` → `create_highlight_reel` |
| **Epic 6: World State & Time** | Zone availability states | `check_time` → `apply_rules` → `update_zones` → `broadcast_changes` |
| **Epic 7: Nudge & Outreach** | Nudge scheduling states | `detect_dropoff` → `select_channel` → `generate_message` → `schedule_send` |

---

## State Machine Architecture

### LangGraph State Machine

Delight uses **LangGraph** for stateful AI agent orchestration. LangGraph provides:
- **Typed state**: Type-safe state management with Pydantic models
- **Node-based workflow**: Each node is a processing step
- **Conditional edges**: Branching logic based on state
- **Tool integration**: Easy tool/function calling from nodes
- **Checkpointing**: Save and resume state across sessions

### State Machine Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ ELIZA AGENT STATE MACHINE (LangGraph)                        │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │ USER INPUT   │
                    │ (External)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ RECEIVE_INPUT│
                    │              │
                    │ - Parse msg  │
                    │ - Detect     │
                    │   emotion    │
                    │ - Extract    │
                    │   intent     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │RECALL_CONTEXT│
                    │              │
                    │ - Query      │
                    │   memories   │
                    │ - Get goal   │
                    │   context    │
                    │ - Retrieve   │
                    │   history    │
                    └──────┬───────┘
                           │
                           ├──────────────────┐
                           │                  │
                    ┌──────▼───────┐   ┌─────▼──────┐
                    │    REASON    │   │ CLARIFY    │
                    │              │   │            │
                    │ - Analyze    │   │ - Need more│
                    │   context    │   │   info     │
                    │ - Plan       │   │ - Ask      │
                    │   response   │   │   question │
                    │ - Decide     │   └─────┬──────┘
                    │   actions    │         │
                    └──────┬───────┘         │
                           │                 │
                           │◄────────────────┘
                           │
                    ┌──────▼───────┐
                    │   RESPOND    │
                    │              │
                    │ - Generate   │
                    │   response   │
                    │ - Stream     │
                    │   tokens     │
                    │ - Invoke     │
                    │   tools      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ STORE_MEMORY │
                    │              │
                    │ - Extract    │
                    │   learnings  │
                    │ - Update     │
                    │   memories   │
                    │ - Update     │
                    │   state      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │     END      │
                    └──────────────┘
```

---

## Eliza Agent State Flow

### State Definition (Pydantic Model)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class ElizaState(BaseModel):
    """State for Eliza agent (LangGraph)."""

    # Input
    messages: list[dict] = Field(default_factory=list)
    user_input: str = ""
    user_id: str = ""
    session_id: str = ""

    # Context
    current_goal_id: Optional[str] = None
    current_mission_id: Optional[str] = None
    emotional_state: dict = Field(default_factory=dict)  # From emotion detection
    retrieved_memories: dict = Field(default_factory=dict)  # Personal/Project/Task

    # Reasoning
    intent: str = ""  # 'question', 'goal_discussion', 'reflection', etc.
    needs_clarification: bool = False
    clarification_question: str = ""
    planned_actions: list[str] = Field(default_factory=list)

    # Response
    response_text: str = ""
    tool_outputs: dict = Field(default_factory=dict)

    # Metadata
    current_node: str = "receive_input"
    error: Optional[str] = None
    timestamp: str = ""
```

### Node Implementations

#### Node 1: Receive Input

```python
from app.services.emotion_service import detect_emotion

async def receive_input_node(state: ElizaState) -> ElizaState:
    """
    Parse user message and detect emotional state.

    Goals:
    - Understand what user is asking/sharing
    - Detect emotional state for empathetic response
    - Extract intent for next steps
    """

    # Detect emotion (cardiffnlp/roberta model)
    emotions = await detect_emotion(state.user_input)
    state.emotional_state = emotions

    # Extract intent using LLM
    intent_prompt = f"""
    Classify the user's intent from this message:
    "{state.user_input}"

    Intent categories:
    - question: Asking for information
    - goal_discussion: Talking about goals/progress
    - reflection: Sharing thoughts/feelings
    - mission_request: Wants a mission/task
    - small_talk: Casual conversation

    Intent:"""

    intent = await call_llm(intent_prompt, model="gpt-4o-mini", max_tokens=20)
    state.intent = intent.strip().lower()

    # Update node tracker
    state.current_node = "recall_context"

    return state
```

#### Node 2: Recall Context

```python
from app.services.memory_service import retrieve_relevant_memories

async def recall_context_node(state: ElizaState) -> ElizaState:
    """
    Query memories and gather context.

    Goals:
    - Retrieve relevant personal/project/task memories
    - Get current goal context if applicable
    - Build comprehensive context for reasoning
    """

    # Query memories from all tiers
    memories = await retrieve_relevant_memories(
        db=db,
        user_id=state.user_id,
        query=state.user_input,
        context={
            "goal_id": state.current_goal_id,
            "mission_id": state.current_mission_id,
            "emotional_state": state.emotional_state
        }
    )

    state.retrieved_memories = {
        "personal": [m.content for m in memories["personal"]],
        "project": [m.content for m in memories["project"]],
        "task": [m.content for m in memories["task"]]
    }

    # Decide next step
    if needs_more_info(state):
        state.current_node = "clarify"
        state.needs_clarification = True
    else:
        state.current_node = "reason"
        state.needs_clarification = False

    return state

def needs_more_info(state: ElizaState) -> bool:
    """Check if we need to ask clarifying questions."""

    # If user mentions goal but no goal context retrieved
    if "goal" in state.user_input.lower() and not state.retrieved_memories["project"]:
        return True

    # If emotional state suggests overwhelm but no clear ask
    if state.emotional_state.get("sadness", 0) > 0.7 and state.intent == "reflection":
        return True

    return False
```

#### Node 3: Reason

```python
async def reason_node(state: ElizaState) -> ElizaState:
    """
    Analyze context and plan response.

    Goals:
    - Determine best response strategy
    - Plan which tools to invoke
    - Decide if action needed (create mission, update goal, etc.)
    """

    # Build reasoning prompt with full context
    reasoning_prompt = f"""
    You are Eliza, an empathetic AI companion helping users achieve their goals.

    User's message: "{state.user_input}"
    Intent: {state.intent}
    Emotional state: {state.emotional_state.get('dominant_emotion', 'neutral')}

    Relevant memories:
    - Personal: {state.retrieved_memories['personal'][:3]}
    - Project: {state.retrieved_memories['project'][:5]}
    - Task: {state.retrieved_memories['task'][:5]}

    Current goal: {state.current_goal_id or "None"}

    Based on this context:
    1. What's the best way to respond empathetically?
    2. Should we take any actions (create mission, adjust goal, suggest break)?
    3. What tools/services do we need (mission_service, goal_service, etc.)?

    Plan:"""

    plan = await call_llm(reasoning_prompt, model="gpt-4o-mini", max_tokens=300)

    # Extract planned actions
    state.planned_actions = extract_actions_from_plan(plan)

    state.current_node = "respond"
    return state

def extract_actions_from_plan(plan: str) -> list[str]:
    """Parse planned actions from LLM response."""

    actions = []

    # Simple keyword extraction (could use structured output)
    if "create mission" in plan.lower():
        actions.append("create_mission")
    if "update goal" in plan.lower():
        actions.append("update_goal")
    if "suggest break" in plan.lower():
        actions.append("suggest_break")

    return actions
```

#### Node 4: Respond

```python
async def respond_node(state: ElizaState) -> ElizaState:
    """
    Generate response and execute actions.

    Goals:
    - Create empathetic, contextual response
    - Execute planned actions via tools
    - Stream response to user
    """

    # Execute tools if needed
    if "create_mission" in state.planned_actions:
        mission = await mission_service.create_mission(
            user_id=state.user_id,
            goal_id=state.current_goal_id,
            # ... mission details
        )
        state.tool_outputs["mission_created"] = mission.id

    # Generate response with full context
    response_prompt = f"""
    You are Eliza. Respond empathetically to the user.

    User: "{state.user_input}"
    Emotional state: {state.emotional_state}
    Context: {state.retrieved_memories}
    Actions taken: {state.tool_outputs}

    Respond naturally, acknowledging emotions and referencing relevant memories.
    If mission created, mention it encouragingly.

    Response:"""

    # Stream response (SSE)
    response = await call_llm_streaming(
        response_prompt,
        model="gpt-4o-mini",
        max_tokens=500
    )

    state.response_text = response

    state.current_node = "store_memory"
    return state
```

#### Node 5: Store Memory

```python
from app.services.memory_service import create_memory

async def store_memory_node(state: ElizaState) -> ElizaState:
    """
    Extract learnings and update memories.

    Goals:
    - Identify important information to remember
    - Update personal/project/task memories
    - Consolidate conversation context
    """

    # Extract learnings using LLM
    learning_prompt = f"""
    From this conversation, extract key information to remember:

    User: "{state.user_input}"
    Eliza: "{state.response_text}"
    Emotional state: {state.emotional_state}

    What should we remember long-term (personal memory)?
    What's relevant to current goal (project memory)?
    What's specific to today's context (task memory)?

    Format:
    Personal: [statement or "none"]
    Project: [statement or "none"]
    Task: [statement or "none"]
    """

    learnings = await call_llm(learning_prompt, model="gpt-4o-mini", max_tokens=200)
    parsed = parse_learnings(learnings)

    # Create memories
    if parsed["personal"]:
        await create_memory(
            db=db,
            user_id=state.user_id,
            content=parsed["personal"],
            memory_type="personal",
            metadata={"conversation_id": state.session_id},
            tags=["conversation", state.emotional_state.get("dominant_emotion", "neutral")]
        )

    if parsed["project"] and state.current_goal_id:
        await create_memory(
            db=db,
            user_id=state.user_id,
            content=parsed["project"],
            memory_type="project",
            metadata={"goal_id": state.current_goal_id},
            tags=["goal_progress", state.current_goal_id]
        )

    if parsed["task"] and state.current_mission_id:
        await create_memory(
            db=db,
            user_id=state.user_id,
            content=parsed["task"],
            memory_type="task",
            metadata={"mission_id": state.current_mission_id},
            tags=["mission_context", state.current_mission_id]
        )

    state.current_node = "end"
    return state

def parse_learnings(text: str) -> dict:
    """Parse LLM output into structured learnings."""

    lines = text.strip().split("\n")
    result = {"personal": None, "project": None, "task": None}

    for line in lines:
        if line.startswith("Personal:"):
            content = line.replace("Personal:", "").strip()
            if content.lower() != "none":
                result["personal"] = content
        elif line.startswith("Project:"):
            content = line.replace("Project:", "").strip()
            if content.lower() != "none":
                result["project"] = content
        elif line.startswith("Task:"):
            content = line.replace("Task:", "").strip()
            if content.lower() != "none":
                result["task"] = content

    return result
```

---

## Tool-Aware Processing

### Available Tools

Eliza agent has access to various tools/services:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `memory_service` | Query/create memories | Retrieve personal preferences |
| `mission_service` | Create/update missions | Generate new quest for user |
| `goal_service` | Manage goals | Update goal status, decompose goal |
| `emotion_service` | Detect emotions | Understand user's emotional state |
| `narrative_service` | Generate story beats | Create narrative content for milestone |
| `progress_service` | Calculate analytics | Get DCI score, streak info |
| `world_service` | Check zone availability | Verify if Arena is open |

### Tool Selection Logic

```python
def select_tools(state: ElizaState) -> list[str]:
    """Decide which tools to use based on intent and context."""

    tools = []

    # Always use memory service
    tools.append("memory_service")

    # Intent-based tool selection
    if state.intent == "goal_discussion":
        tools.extend(["goal_service", "mission_service"])

    if state.intent == "mission_request":
        tools.extend(["mission_service", "world_service"])

    # Emotion-based tool selection
    if state.emotional_state.get("sadness", 0) > 0.7:
        tools.append("progress_service")  # Show progress to encourage

    if state.emotional_state.get("joy", 0) > 0.8:
        tools.append("narrative_service")  # Celebrate with story beat

    # Context-based tool selection
    if state.current_goal_id:
        tools.append("goal_service")

    return tools
```

### Tool Invocation Patterns

**Sequential (dependent)**:
```python
# Must happen in order
goal = await goal_service.get_goal(goal_id)  # First
missions = await mission_service.get_missions(goal.id)  # Then
```

**Parallel (independent)**:
```python
# Can happen simultaneously
emotion, memories, progress = await asyncio.gather(
    emotion_service.detect(user_input),
    memory_service.retrieve(user_id, query),
    progress_service.get_dci(user_id)
)
```

---

## Cross-Epic State Integration

### Epic 3: Goal & Mission Management

**State Flow**: Goal Creation → Decomposition → Mission Generation

```python
# In Eliza agent, when user creates goal
if state.intent == "create_goal":
    # Create goal (Epic 3)
    goal = await goal_service.create_goal(
        user_id=state.user_id,
        title=extract_goal_title(state.user_input),
        description=state.user_input
    )

    # Store in project memory (Epic 2)
    await create_memory(
        user_id=state.user_id,
        content=f"User created goal: {goal.title}. Reason: {goal.description}",
        memory_type="project",
        metadata={"goal_id": goal.id}
    )

    # Trigger decomposition workflow (Epic 3)
    await trigger_goal_decomposition(goal.id)

    # Update state
    state.current_goal_id = goal.id
    state.tool_outputs["goal_created"] = goal.id
```

### Epic 4: Narrative Engine

**State Flow**: Progress Assessment → Story Beat Generation → Memory Update

```python
# In narrative agent, when generating story beat
async def narrative_generation_state_flow(user_id: str, goal_id: str):
    """Generate personalized narrative beat."""

    # ASSESS_PROGRESS node
    progress = await progress_service.get_goal_progress(user_id, goal_id)
    missions_completed = progress["missions_completed"]
    streak = progress["streak_days"]

    # Retrieve project memory for story consistency
    memories = await memory_service.retrieve(
        user_id, query="story narrative", goal_id=goal_id
    )

    # SELECT_BEAT node
    beat_type = select_narrative_beat(missions_completed, streak, memories)

    # GENERATE_CONTENT node
    story_text = await generate_story_with_llm(
        user_id, goal_id, beat_type, progress, memories
    )

    # CHECK_UNLOCKS node
    unlocks = check_hidden_quest_triggers(progress)

    # Store narrative in project memory
    await create_memory(
        user_id=user_id,
        content=story_text,
        memory_type="project",
        metadata={"goal_id": goal_id, "story_beat": beat_type},
        tags=["narrative", "chapter_progress"]
    )

    return {"story": story_text, "unlocks": unlocks}
```

### Epic 5: Progress & Analytics

**State Flow**: Data Collection → DCI Calculation → Insight Generation

```python
# In progress service, daily DCI calculation
async def calculate_dci_state_flow(user_id: str):
    """Calculate Daily Consistency Index."""

    # COLLECT_DATA node
    streak = await get_user_streak(user_id)
    mission_completion = await get_mission_completion_rate(user_id, days=7)
    engagement = await get_engagement_depth(user_id, days=7)

    # CALCULATE_DCI node
    dci_score = weighted_average(streak, mission_completion, engagement)

    # GENERATE_INSIGHTS node (query task memories for patterns)
    task_memories = await memory_service.get_task_memories(user_id, days=30)
    insights = await analyze_patterns_with_llm(task_memories)

    # Store insights in personal memory
    await create_memory(
        user_id=user_id,
        content=f"DCI Insight: {insights}",
        memory_type="personal",
        metadata={"dci_score": dci_score, "date": today()},
        tags=["analytics", "insight"]
    )

    # CREATE_HIGHLIGHT_REEL node (if milestone)
    if dci_score >= 0.8 and streak >= 7:
        await create_highlight_reel(user_id)

    return {"dci": dci_score, "insights": insights}
```

### Epic 6: World State & Time

**State Flow**: Time Check → Rule Application → Zone Update → Broadcast

```python
# In world service, time-aware state updates
async def update_world_state_flow(user_id: str):
    """Update zone availability based on time rules."""

    # CHECK_TIME node
    user_time = await get_user_local_time(user_id)
    productive_hours = await get_user_productive_hours(user_id)

    # APPLY_RULES node
    zone_availability = apply_time_rules(user_time, productive_hours)

    # UPDATE_ZONES node
    await update_zone_cache(user_id, zone_availability)

    # BROADCAST_CHANGES node (WebSocket)
    await broadcast_world_update(user_id, zone_availability)

    # Store in personal memory if preference learned
    if is_new_pattern(user_time, productive_hours):
        await create_memory(
            user_id=user_id,
            content=f"User active at {user_time}, outside usual hours",
            memory_type="personal",
            tags=["activity_pattern", "time_preference"]
        )

    return zone_availability
```

### Epic 7: Nudge & Outreach

**State Flow**: Dropoff Detection → Channel Selection → Message Generation → Schedule

```python
# In nudge scheduler, when user inactive
async def nudge_state_flow(user_id: str):
    """Generate and schedule compassionate nudge."""

    # DETECT_DROPOFF node
    last_activity = await get_last_activity(user_id)
    days_inactive = (datetime.now() - last_activity).days

    if days_inactive < 2:
        return  # No nudge needed

    # Retrieve personal memory for personalization
    preferences = await memory_service.get_personal_preferences(user_id)
    recent_goals = await memory_service.get_project_memories(
        user_id, query="active goal", limit=1
    )

    # SELECT_CHANNEL node
    channel = select_nudge_channel(days_inactive, preferences)

    # GENERATE_MESSAGE node
    message = await generate_nudge_with_llm(
        user_id, days_inactive, recent_goals, preferences
    )

    # SCHEDULE_SEND node
    optimal_time = calculate_optimal_send_time(user_id, preferences)
    await schedule_nudge(user_id, channel, message, optimal_time)

    # Store in task memory
    await create_memory(
        user_id=user_id,
        content=f"Nudge scheduled: {days_inactive} days inactive",
        memory_type="task",
        tags=["nudge", channel]
    )
```

---

## State Persistence

### Checkpointing with LangGraph

LangGraph supports **state checkpointing** for long-running workflows:

```python
from langgraph.checkpoint import MemorySaver

# Create checkpointer
checkpointer = MemorySaver()

# Build graph with checkpointing
graph = StateGraph(ElizaState)
graph.add_node("receive_input", receive_input_node)
graph.add_node("recall_context", recall_context_node)
# ... more nodes

compiled_graph = graph.compile(checkpointer=checkpointer)

# Run with checkpoint
config = {"configurable": {"thread_id": session_id}}
result = await compiled_graph.ainvoke(initial_state, config)

# Resume from checkpoint later
resumed = await compiled_graph.ainvoke(updated_state, config)
```

### Database State Storage

For cross-session persistence:

```sql
CREATE TABLE agent_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,  -- 'eliza', 'narrative', 'mission'
    state_data JSONB NOT NULL,
    current_node VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_states_user_session ON agent_states(user_id, session_id);
```

```python
async def save_agent_state(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    state: ElizaState
):
    """Persist agent state to database."""

    agent_state = AgentState(
        user_id=user_id,
        session_id=session_id,
        agent_type="eliza",
        state_data=state.dict(),
        current_node=state.current_node
    )

    db.add(agent_state)
    await db.commit()

async def load_agent_state(
    db: AsyncSession,
    user_id: str,
    session_id: str
) -> ElizaState:
    """Load agent state from database."""

    stmt = select(AgentState).where(
        AgentState.user_id == user_id,
        AgentState.session_id == session_id
    )
    result = await db.execute(stmt)
    agent_state = result.scalar_one_or_none()

    if agent_state:
        return ElizaState(**agent_state.state_data)
    else:
        return ElizaState(user_id=user_id, session_id=session_id)
```

---

## Error Handling and Recovery

### Error Types

1. **Tool Failures**: Service unavailable, API timeout
2. **LLM Errors**: Rate limit, invalid response, parsing error
3. **Memory Errors**: Vector search timeout, embedding generation failed
4. **State Errors**: Invalid transition, missing required context

### Recovery Strategies

```python
async def safe_node_execution(
    node_func: callable,
    state: ElizaState,
    max_retries: int = 3
) -> ElizaState:
    """Execute node with error handling and retries."""

    for attempt in range(max_retries):
        try:
            return await node_func(state)

        except ToolFailureError as e:
            # Tool failed, try without tool
            logger.warning(f"Tool failed: {e}. Continuing without tool.")
            state.tool_outputs["error"] = str(e)
            return state

        except LLMError as e:
            # LLM error, retry with backoff
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                # Fallback to template response
                state.response_text = get_fallback_response(state.intent)
                state.error = str(e)
                return state

        except MemoryError as e:
            # Memory retrieval failed, continue without memories
            logger.error(f"Memory error: {e}. Using empty context.")
            state.retrieved_memories = {"personal": [], "project": [], "task": []}
            return state

        except Exception as e:
            # Unknown error, log and gracefully fail
            logger.exception(f"Unexpected error in {node_func.__name__}: {e}")
            state.error = f"Internal error: {str(e)}"
            state.current_node = "end"
            return state

    # Max retries exceeded
    state.error = "Max retries exceeded"
    state.current_node = "end"
    return state
```

### Graceful Degradation

```python
def get_fallback_response(intent: str) -> str:
    """Provide fallback response when AI fails."""

    fallbacks = {
        "question": "I'm having trouble processing that right now. Could you rephrase your question?",
        "goal_discussion": "I'd love to help with your goal, but I'm experiencing a temporary issue. Let's try again in a moment.",
        "reflection": "Thank you for sharing that with me. I'm here to listen.",
        "mission_request": "I'm working on generating a mission for you. This might take a moment."
    }

    return fallbacks.get(intent, "I'm here to help, but I'm experiencing a temporary issue. Please try again.")
```

---

## Summary

Delight's state management system provides:

✅ **Goal-driven workflows** that align with user objectives
✅ **Tool-aware processing** that knows when to use each service
✅ **Cross-epic integration** for cohesive user experience
✅ **State persistence** for continuity across sessions
✅ **Robust error handling** with graceful degradation

**Key Takeaways**:
1. Every state transition has a purpose (moving toward goal completion)
2. State carries context (memories, tools, intermediate results)
3. Tools are selected based on intent, emotion, and context
4. State integrates across all epics for unified experience
5. Error recovery ensures system never leaves user stranded

**Next**: Read `04-RETRIEVAL-STRATEGY.md` for graph-based hierarchical retrieval implementation.

---

**Last Updated**: 2025-11-18
**Status**: Design Specification
**Maintainer**: Jack & Delight Team
