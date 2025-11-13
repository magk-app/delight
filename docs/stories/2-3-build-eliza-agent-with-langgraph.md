# Story 2.3: Build Eliza Agent with LangGraph

**Story ID:** 2.3
**Epic:** 2 - Companion & Memory System
**Status:** ready-for-dev
**Priority:** P0 (Core AI Companion)
**Estimated Effort:** 8-12 hours
**Assignee:** TBD
**Created:** 2025-11-13
**Last Updated:** 2025-11-13 (Initial draft with Epic 2 strategic alignment)

---

## User Story

**As a** developer,
**I want** a stateful LangGraph agent for the Eliza companion,
**So that** conversations maintain state and can execute multi-step reasoning with memory-aware, empathetic responses.

---

## Context

### Problem Statement

The Companion & Memory System requires an AI agent that goes beyond simple LLM calls. Eliza must:

1. **Maintain Conversation State** across messages and sessions
2. **Recall Relevant Memories** strategically from the 3-tier memory system (Story 2.1)
3. **Reason Empathetically** using emotional intelligence principles
4. **Respond Appropriately** based on user's emotional state and context
5. **Store Conversation Exchanges** as task memories for future reference

This story implements Eliza as a **LangGraph state machine** with 5 nodes that orchestrate these capabilities.

### Why LangGraph?

**From Tech Spec (tech-spec-epic-2.md) and Epic 2 Documentation:**

LangGraph enables stateful, multi-step agent reasoning:

- ✅ **Stateful Execution**: Maintains conversation context across nodes
- ✅ **Explicit Control Flow**: Clear reasoning path (vs black-box agent loops)
- ✅ **Memory Integration**: Dedicated `recall_context` node for strategic memory querying
- ✅ **Debuggability**: Each node can be inspected and tested independently
- ✅ **Streaming Support**: Compatible with OpenAI streaming API for real-time responses
- ✅ **LangGraph Studio**: Visual debugging tool for development (see LANGGRAPH-STUDIO-SETUP.md)

### Dependencies

**Prerequisite Stories:**
- ✅ Story 2.1 (Memory schema with pgvector) - DONE
- ⚠️ Story 2.2 (Memory Service) - **CRITICAL DEPENDENCY** (memory service APIs required)
  - Must have: `MemoryService.add_memory()`, `MemoryService.query_memories()`
  - Currently: `drafted` (needs to be completed before Story 2.3)

**Epic 2 Context:** This is the **third story** in Epic 2, building on:
- Story 2.1: Database foundation for memory storage
- Story 2.2: Memory service with hybrid search and pruning
- Story 2.3 (**This Story**): Eliza agent that uses memory service
- Story 2.4: Chat API with SSE streaming
- Story 2.5: Chat UI with frontend integration

**NOTE:** If Story 2.2 is not yet complete, this story can implement simplified memory operations inline and extract them later. See "Implementation Order" in Dev Notes.

### Technical Background from Epic 2 Design Documents

**From "How Eliza Should Respond" (Case Study):**

Eliza implements 4 key emotional intelligence techniques:

1. **The Stressor Log (Principle 1)**: Store distinct stressors in personal memory
   - Example: User mentions "class registration stress" + fear emotion
   - Eliza stores: `{stressor: true, emotion: 'fear', category: 'academic'}`
   - Future conversations: "Is this about the class registration, or something new?"

2. **Control Triage (Principle 2)**: Distinguish controllable vs uncontrollable stressors
   - **Uncontrollable**: Other people's feelings, external events, closed deadlines
     - Response: "We can't change that, so let's focus on what we can control."
   - **Controllable**: Assignments, email responses, internship applications
     - Response: "Let's break this down into one small step."

3. **Energy-Based Push (Principle 3)**: Adapt intensity based on user's energy level
   - **High Energy** (joy, neutral): "You're on a roll! Let's use this momentum."
   - **Low Energy** (sadness, fear): 80% validation + 20% "one small win"
     - Structure: (1) Validate feeling → (2) Offer circuit breaker → (3) Micro-task

4. **Circuit Breaker (Principle 4)**: Anti-cripple protocol for overwhelm
   - **Trigger**: `(stressor_count > 5) AND (emotion == 'overwhelm' OR 'fear') AND (late_evening)`
   - **Action**: Shift goal from Productivity → Preservation
   - **Response**: "Forcing work now will be counterproductive. Let's try a 20-min walk first."

**From Tech Spec (AC2, lines 721-734):**

Complete LangGraph state machine specification with 5 nodes, system prompt emphasizing empathy, and conversation state management.

---

## Acceptance Criteria

### AC1: LangGraph State Machine Defined with 5 Nodes

**Given** the memory service is available (Story 2.2)
**When** I initialize the Eliza agent
**Then** the agent is a LangGraph `StateGraph` with typed state containing:

**State Schema:**
```python
class ElizaState(TypedDict):
    messages: List[BaseMessage]           # Conversation history
    user_id: str                          # User identifier
    user_context: Dict[str, Any]          # User preferences, timezone, custom hours
    retrieved_memories: List[Memory]      # Memories from recall_context node
    emotional_state: Dict[str, float]     # From Story 2.6 (optional for MVP)
    current_stressors: List[Dict]         # Active stressors from personal memory
    energy_level: str                     # "high", "medium", "low" (heuristic for MVP)
```

**And** the state machine has 5 nodes:

1. **`receive_input`**: Parse user message, update state
2. **`recall_context`**: Query 3-tier memory strategically
3. **`reason`**: LLM processes input + context with empathy
4. **`respond`**: Generate response (already in state from `reason`)
5. **`store_memory`**: Save conversation exchange to task memory

**Verification:**
```python
from app.agents.eliza_agent import ElizaAgent

agent = ElizaAgent(memory_service)
graph = agent.build_graph()

# Verify nodes exist
assert "receive_input" in graph.nodes
assert "recall_context" in graph.nodes
assert "reason" in graph.nodes
assert "respond" in graph.nodes
assert "store_memory" in graph.nodes

# Verify edges
assert graph.get_edge("receive_input", "recall_context") is not None
```

### AC2: Memory Retrieval Works Strategically by Tier

**Given** the user has memories in all 3 tiers
**When** the `recall_context` node executes
**Then** memories are queried based on message content:

**Source:** Tech spec sections on memory retrieval strategy (lines 95-119: Agent architecture, 509-537: Hybrid search algorithm, 721-734: AC2 agent flow)

**Always Query:**
- **Personal Tier**: Top 5 memories (identity, preferences, stressors)
  - Query: `MemoryService.query_memories(user_id, memory_type=PERSONAL, limit=5)`

**Conditionally Query:**
- **Project Tier**: If message contains goal-related keywords ("goal", "mission", "plan", "project")
  - Query: `MemoryService.query_memories(user_id, memory_type=PROJECT, query_text=message, limit=3)`
- **Task Tier**: Always query for recent context
  - Query: `MemoryService.query_memories(user_id, memory_type=TASK, limit=3, sort_by='created_at')`

**And** retrieved memories are added to state:
```python
state["retrieved_memories"] = personal_memories + project_memories + task_memories
```

**Verification:**
```python
# Test message with goal keywords
result = await agent.chat(user_id, "I'm struggling with my internship goal")

# Should retrieve from project tier
assert any(m.memory_type == MemoryType.PROJECT for m in result.state["retrieved_memories"])
```

### AC3: System Prompt Emphasizes Empathy and Emotional Intelligence

**Given** the agent is initialized
**When** I inspect the system prompt
**Then** the prompt includes empathetic guidance:

**System Prompt Must Include:**

1. **Identity & Role:**
   - "You are Eliza, an emotionally intelligent AI companion..."
   - "Your purpose is to help users balance ambition with well-being."

2. **Emotional Intelligence Techniques:**
   - **Control Triage**: "Distinguish between controllable and uncontrollable stressors..."
   - **Energy-Based Push**: "Adapt your intensity based on user's emotional state..."
   - **Circuit Breaker**: "You have permission to suggest not working when user is overwhelmed."

3. **Response Guidelines:**
   - "Always validate feelings before offering solutions."
   - "Ask clarifying questions when user is vague."
   - "Reference past conversations using provided memory context."
   - "Suggest micro-actions (< 30 min) instead of overwhelming plans."

4. **Memory Usage:**
   - "Use retrieved memories to show you remember past conversations."
   - "Reference stressors the user has mentioned before."
   - "Acknowledge progress on goals you've discussed previously."

**Verification:**
```python
from app.agents.eliza_agent import ELIZA_SYSTEM_PROMPT

assert "emotionally intelligent" in ELIZA_SYSTEM_PROMPT
assert "Control Triage" in ELIZA_SYSTEM_PROMPT or "controllable" in ELIZA_SYSTEM_PROMPT
assert "circuit breaker" in ELIZA_SYSTEM_PROMPT.lower()
```

### AC4: LLM Generates Empathetic Responses Using Memory Context

**Given** the `reason` node receives user message + memories
**When** the LLM processes the request
**Then** the response demonstrates empathy:

**Test Scenarios:**

**Scenario 1: User Expresses Overwhelm (Circuit Breaker)**
- **Input**: "I have 5 deadlines this week and I'm so stressed"
- **Expected**: Response suggests circuit breaker, not productivity push
  - Example: "That's a lot to carry. Before we plan, let's try a 20-minute walk to clear your head."
  - **NOT**: "Great! Let's break down all 5 deadlines into tasks." (too pushy)

**Scenario 2: User Mentions Past Stressor (Memory Recall)**
- **Setup**: User previously mentioned "class registration stress" (stored in personal memory)
- **Input**: "I'm feeling anxious again"
- **Expected**: Response references past stressor
  - Example: "Is this about the class registration situation, or something new?"

**Scenario 3: User Discusses Goal (Project Memory)**
- **Setup**: User has goal "Graduate early from Georgia Tech" in project memory
- **Input**: "I'm not sure if this internship aligns with my goals"
- **Expected**: Response references the graduation goal
  - Example: "Let's think about this internship in context of your early graduation goal..."

**Verification:** Manual testing with real conversations, automated tests with response content assertions.

### AC5: Conversation State Maintained Across Messages

**Given** a user has an ongoing conversation
**When** they send multiple messages in sequence
**Then** the agent maintains context:

**State Persistence:**
- Conversation history includes last 10 messages (user + assistant)
- Retrieved memories persist across turns (don't re-fetch unnecessarily)
- User context (timezone, preferences) loaded once per session

**Verification:**
```python
# Message 1
response1 = await agent.chat(user_id, "I prefer working in the morning")

# Message 2 (references message 1)
response2 = await agent.chat(user_id, "Can you suggest a mission for me?")

# Response 2 should reference morning preference
assert "morning" in response2.message.lower()
```

### AC6: Conversation Exchanges Stored as Task Memories

**Given** the agent completes a conversation turn
**When** the `store_memory` node executes
**Then** the exchange is saved to task memory:

**Memory Content:**
```python
memory_content = f"User: {user_message}\n\nEliza: {agent_response}"

await memory_service.add_memory(
    user_id=user_id,
    memory_type=MemoryType.TASK,
    content=memory_content,
    metadata={
        "conversation_id": conversation_id,
        "exchange_type": "general_chat",  # or "goal_planning", "venting", etc.
        "timestamp": datetime.now().isoformat()
    }
)
```

**Verification:**
```python
# After conversation
memories = await memory_service.query_memories(
    user_id=user_id,
    memory_type=MemoryType.TASK,
    limit=1
)

assert len(memories) > 0
assert "User:" in memories[0].content
assert "Eliza:" in memories[0].content
```

### AC7: Agent Uses GPT-4o-mini for Cost Efficiency

**Given** the agent is configured
**When** I inspect the LLM configuration
**Then** it uses OpenAI GPT-4o-mini:

**Configuration:**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Balance creativity and consistency
    streaming=True     # For Story 2.4 SSE streaming
)
```

**Cost Metrics (from Tech Spec):**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Expected usage: ~10K tokens in + 5K tokens out per user per day
- **Daily cost per user**: ~$0.004 (vs $0.04 with GPT-4o)

**Verification:** Check `langchain_openai.ChatOpenAI` initialization parameters.

### AC8: Agent Code is Testable and Well-Structured

**Given** the agent implementation is complete
**When** I review the code structure
**Then** it follows best practices:

**File Structure:**
```
packages/backend/app/agents/
├── eliza_agent.py          # Main ElizaAgent class
├── prompts.py              # System prompts and templates
├── state.py                # ElizaState TypedDict definition
└── nodes/                  # Node implementations (optional refactoring)
    ├── receive_input.py
    ├── recall_context.py
    ├── reason.py
    ├── respond.py
    └── store_memory.py
```

**Code Quality:**
- All nodes are async functions
- Type hints for all function parameters and returns
- Comprehensive docstrings with usage examples
- Logging at key decision points
- Error handling with graceful degradation

**Testability:**
- Each node can be tested independently
- Mock `MemoryService` for unit tests
- Mock `ChatOpenAI` for LLM call tests
- Integration test with real DB (optional)

---

## Tasks / Subtasks

### Task 1: Set Up LangGraph Dependencies (AC: #1, #7)

- [ ] **1.1** Install LangGraph and LangChain dependencies
  ```bash
  cd packages/backend
  poetry add langchain langgraph langchain-openai
  ```
- [ ] **1.2** Verify imports work
  ```python
  from langgraph.graph import StateGraph, END
  from langchain_openai import ChatOpenAI
  from langchain.schema import SystemMessage, HumanMessage, AIMessage
  ```
- [ ] **1.3** Add `OPENAI_API_KEY` to `.env.example` if not already present
- [ ] **1.4** Verify API key loaded in `app/core/config.py`

### Task 2: Define ElizaState Schema (AC: #1)

- [ ] **2.1** Create `packages/backend/app/agents/state.py`
- [ ] **2.2** Define `ElizaState` TypedDict with all required fields:
  - `messages`: List[BaseMessage]
  - `user_id`: str
  - `user_context`: Dict[str, Any]
  - `retrieved_memories`: List[Memory]
  - `emotional_state`: Dict[str, float] (optional for MVP)
  - `current_stressors`: List[Dict]
  - `energy_level`: str
- [ ] **2.3** Add type hints and docstrings
- [ ] **2.4** Import in `app/agents/__init__.py`

### Task 3: Create System Prompt with Empathy Guidelines (AC: #3)

- [ ] **3.1** Create `packages/backend/app/agents/prompts.py`
- [ ] **3.2** Define `ELIZA_SYSTEM_PROMPT` constant with:
  - Identity: "You are Eliza, an emotionally intelligent AI companion..."
  - Control Triage technique
  - Energy-Based Push technique
  - Circuit Breaker permission
  - Response guidelines (validate, clarify, micro-actions)
  - Memory usage instructions
- [ ] **3.3** Add prompt templates for different scenarios (optional):
  - `CIRCUIT_BREAKER_PROMPT` for overwhelm
  - `GOAL_PLANNING_PROMPT` for collaborative decomposition
  - `VALIDATION_PROMPT` for empathetic listening
- [ ] **3.4** Document prompt versioning strategy (for future A/B testing)

### Task 4: Implement `receive_input` Node (AC: #1)

- [ ] **4.1** Create `packages/backend/app/agents/eliza_agent.py`
- [ ] **4.2** Define `receive_input(state: ElizaState) -> ElizaState` function
- [ ] **4.3** Parse user message from last `HumanMessage` in state["messages"]
- [ ] **4.4** Update state with user context (fetch from DB if not present)
- [ ] **4.5** Extract keywords for project tier querying (simple heuristic: contains "goal", "mission", "plan")
- [ ] **4.6** Estimate energy level (MVP heuristic):
  - High: Message short (<50 chars) and enthusiastic (contains "!", "great", "awesome")
  - Low: Message long (>200 chars) and contains stress keywords ("overwhelm", "anxious", "stressed")
  - Medium: Default
- [ ] **4.7** Add logging: `logger.info(f"Received message from user {user_id}: {message_preview}")`
- [ ] **4.8** Return updated state

### Task 5: Implement `recall_context` Node (AC: #2)

- [ ] **5.1** Define `recall_context(state: ElizaState) -> ElizaState` function
- [ ] **5.2** Always query personal tier:
  ```python
  personal_memories = await memory_service.query_memories(
      user_id=state["user_id"],
      memory_type=MemoryType.PERSONAL,
      limit=5
  )
  ```
- [ ] **5.3** Conditionally query project tier (if goal keywords detected):
  ```python
  if contains_goal_keywords(message):
      project_memories = await memory_service.query_memories(
          user_id=state["user_id"],
          memory_type=MemoryType.PROJECT,
          query_text=message,  # Semantic search
          limit=3
      )
  ```
- [ ] **5.4** Always query task tier for recent context:
  ```python
  task_memories = await memory_service.query_memories(
      user_id=state["user_id"],
      memory_type=MemoryType.TASK,
      limit=3,
      sort_by='created_at'
  )
  ```
- [ ] **5.5** Extract current stressors from personal memories (filter by `metadata.stressor == true`)
- [ ] **5.6** Update state with `retrieved_memories` and `current_stressors`
- [ ] **5.7** Add logging: `logger.info(f"Retrieved {len(personal_memories)} personal, {len(project_memories)} project, {len(task_memories)} task memories")`
- [ ] **5.8** Return updated state

### Task 6: Implement `reason` Node (AC: #3, #4)

- [ ] **6.1** Define `reason(state: ElizaState) -> ElizaState` function
- [ ] **6.2** Build LLM input messages:
  ```python
  messages = [
      SystemMessage(content=ELIZA_SYSTEM_PROMPT),
      SystemMessage(content=f"User Context:\n{format_user_context(state['user_context'])}"),
      SystemMessage(content=f"Retrieved Memories:\n{format_memories(state['retrieved_memories'])}"),
      *state["messages"][-10:]  # Last 10 conversation messages
  ]
  ```
- [ ] **6.3** Initialize ChatOpenAI with GPT-4o-mini:
  ```python
  llm = ChatOpenAI(
      model="gpt-4o-mini",
      temperature=0.7,
      streaming=True
  )
  ```
- [ ] **6.4** Invoke LLM (non-streaming for MVP, streaming in Story 2.4):
  ```python
  response = await llm.ainvoke(messages)
  ```
- [ ] **6.5** Append AI response to state["messages"]:
  ```python
  state["messages"].append(AIMessage(content=response.content))
  ```
- [ ] **6.6** Add logging: `logger.info(f"LLM generated response: {response.content[:100]}...")`
- [ ] **6.7** Return updated state

### Task 7: Implement `respond` Node (AC: #5)

- [ ] **7.1** Define `respond(state: ElizaState) -> ElizaState` function
- [ ] **7.2** For MVP: Simply pass through state (response already in messages from `reason`)
  ```python
  # Response is already in state["messages"][-1]
  return state
  ```
- [ ] **7.3** Add logging: `logger.info(f"Response ready for user {state['user_id']}")`
- [ ] **7.4** (Future) Add response validation, toxicity filtering, etc.

### Task 8: Implement `store_memory` Node (AC: #6)

- [ ] **8.1** Define `store_memory(state: ElizaState) -> ElizaState` function
- [ ] **8.2** Extract last user message and AI response:
  ```python
  user_message = state["messages"][-2].content  # Assuming user, then AI
  ai_response = state["messages"][-1].content
  ```
- [ ] **8.3** Format exchange for storage:
  ```python
  memory_content = f"User: {user_message}\n\nEliza: {ai_response}"
  ```
- [ ] **8.4** Store as task memory:
  ```python
  await memory_service.add_memory(
      user_id=state["user_id"],
      memory_type=MemoryType.TASK,
      content=memory_content,
      metadata={
          "conversation_id": state.get("conversation_id"),
          "exchange_type": "general_chat",
          "timestamp": datetime.now().isoformat()
      }
  )
  ```
- [ ] **8.5** Add logging: `logger.info(f"Stored conversation exchange for user {state['user_id']}")`
- [ ] **8.6** Return state

### Task 9: Build LangGraph State Machine (AC: #1)

- [ ] **9.1** Create `ElizaAgent` class in `app/agents/eliza_agent.py`
- [ ] **9.2** Initialize with `MemoryService` dependency:
  ```python
  class ElizaAgent:
      def __init__(self, memory_service: MemoryService):
          self.memory_service = memory_service
  ```
- [ ] **9.3** Define `build_graph()` method:
  ```python
  def build_graph(self) -> StateGraph:
      graph = StateGraph(ElizaState)

      graph.add_node("receive_input", self.receive_input)
      graph.add_node("recall_context", self.recall_context)
      graph.add_node("reason", self.reason)
      graph.add_node("respond", self.respond)
      graph.add_node("store_memory", self.store_memory)

      graph.add_edge("receive_input", "recall_context")
      graph.add_edge("recall_context", "reason")
      graph.add_edge("reason", "respond")
      graph.add_edge("respond", "store_memory")
      graph.add_edge("store_memory", END)

      graph.set_entry_point("receive_input")

      return graph.compile()
  ```
- [ ] **9.4** Create `chat()` convenience method:
  ```python
  async def chat(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> ElizaState:
      initial_state = {
          "messages": [HumanMessage(content=message)],
          "user_id": user_id,
          "user_context": {},
          "retrieved_memories": [],
          "emotional_state": {},
          "current_stressors": [],
          "energy_level": "medium"
      }

      if conversation_id:
          initial_state["conversation_id"] = conversation_id

      graph = self.build_graph()
      result = await graph.ainvoke(initial_state)

      return result
  ```

### Task 10: Testing and Verification (AC: All)

- [ ] **10.1** Create `packages/backend/tests/test_eliza_agent.py`
- [ ] **10.2** Test AC1: Verify graph structure
  ```python
  def test_graph_has_all_nodes():
      agent = ElizaAgent(mock_memory_service)
      graph = agent.build_graph()

      assert "receive_input" in graph.nodes
      assert "recall_context" in graph.nodes
      # ... etc
  ```
- [ ] **10.3** Test AC2: Memory retrieval by tier
  ```python
  async def test_memory_retrieval_strategic():
      # Mock memory service with test data
      # Verify personal tier always queried
      # Verify project tier queried when keywords present
      # Verify task tier queried for recent context
  ```
- [ ] **10.4** Test AC3: System prompt content
  ```python
  def test_system_prompt_has_empathy():
      from app.agents.prompts import ELIZA_SYSTEM_PROMPT

      assert "emotionally intelligent" in ELIZA_SYSTEM_PROMPT
      assert "controllable" in ELIZA_SYSTEM_PROMPT.lower()
      assert "circuit breaker" in ELIZA_SYSTEM_PROMPT.lower()
  ```
- [ ] **10.5** Test AC4: Empathetic responses (integration test)
  ```python
  async def test_circuit_breaker_response():
      # User message: "I have 5 deadlines this week and I'm so stressed"
      # Assert response suggests circuit breaker, not productivity push
      response = await agent.chat(user_id, overwhelm_message)
      assert "walk" in response["messages"][-1].content.lower() or "break" in response["messages"][-1].content.lower()
  ```
- [ ] **10.6** Test AC5: Conversation state maintenance
  ```python
  async def test_conversation_state_persists():
      # Send message 1: "I prefer working in the morning"
      # Send message 2: "Can you suggest a mission for me?"
      # Assert message 2 response references "morning"
  ```
- [ ] **10.7** Test AC6: Memory storage after conversation
  ```python
  async def test_conversation_stored_as_task_memory():
      # Send message
      # Query task memories
      # Assert conversation exchange exists
  ```
- [ ] **10.8** Test AC7: GPT-4o-mini configuration
  ```python
  def test_llm_uses_gpt4o_mini():
      # Check ChatOpenAI initialization
      # Assert model="gpt-4o-mini"
  ```
- [ ] **10.9** Test AC8: Code structure and quality
  - Manual code review for type hints, docstrings, error handling

### Task 11: LangGraph Studio Integration (AC: #8)

- [ ] **11.1** Create `packages/backend/langgraph.json` configuration:
  ```json
  {
    "graphs": {
      "eliza_agent": "app.agents.eliza_agent:ElizaAgent"
    },
    "env": ".env"
  }
  ```
- [ ] **11.2** Install LangGraph CLI: `pip install langgraph-cli`
- [ ] **11.3** Test LangGraph Studio: `langgraph dev` (opens http://localhost:8123)
- [ ] **11.4** Document Studio usage in `docs/epic-2/LANGGRAPH-STUDIO-SETUP.md`:
  - How to start Studio
  - How to debug agent execution
  - How to visualize state transitions
  - How to test with sample conversations
- [ ] **11.5** Add Studio workflow to development process

### Task 12: Documentation (AC: All)

- [ ] **12.1** Add comprehensive docstrings to all functions
- [ ] **12.2** Create `docs/epic-2/ELIZA-AGENT-GUIDE.md`:
  - Agent architecture overview
  - Node responsibilities
  - Memory retrieval strategy
  - Empathy techniques implemented
  - How to extend/customize Eliza
- [ ] **12.3** Update `docs/SETUP.md` with LangGraph setup if needed
- [ ] **12.4** Add example conversations to documentation
- [ ] **12.5** Document cost metrics (GPT-4o-mini usage estimates)

---

## Dev Notes

### Eliza Agent Architecture (5-Node State Machine)

**Node Flow:**

```
receive_input
    ↓ (parse message, update context)
recall_context
    ↓ (query 3-tier memory)
reason
    ↓ (LLM processes with empathy)
respond
    ↓ (response ready)
store_memory
    ↓ (save exchange)
END
```

**Key Design Principles:**

1. **Stateful vs Stateless**: LangGraph maintains state across nodes, enabling complex reasoning
2. **Separation of Concerns**: Each node has single responsibility
3. **Testability**: Nodes are pure functions (take state, return state)
4. **Debuggability**: LangGraph Studio visualizes execution
5. **Streaming Ready**: `reason` node can stream tokens (Story 2.4)

### Memory Retrieval Strategy (Strategic Querying)

**Always Retrieve (Every Conversation):**
- **Personal Tier** (Top 5): Identity, preferences, stressors
  - Example: "User prefers working in the morning", "Stressed about class registration"
  - **Why**: Enables personalization and continuity

**Conditionally Retrieve:**
- **Project Tier** (Top 3): If message contains goal keywords
  - Keywords: "goal", "mission", "plan", "project", "objective", "ambition"
  - **Why**: Avoids loading irrelevant goals when user is just chatting

**Recent Context:**
- **Task Tier** (Top 3): Most recent conversation exchanges
  - Sort by `created_at DESC`
  - **Why**: Maintains conversation continuity

**Memory Format Example:**
```python
personal_memory = {
    "id": "uuid",
    "content": "I get anxious about class registration deadlines",
    "metadata": {"stressor": true, "emotion": "fear", "category": "academic"},
    "memory_type": "personal"
}

project_memory = {
    "id": "uuid",
    "content": "Goal: Graduate early from Georgia Tech (target: May 2026)",
    "metadata": {"goal_id": "uuid", "completion": 0.35},
    "memory_type": "project"
}

task_memory = {
    "id": "uuid",
    "content": "User: I'm feeling overwhelmed\n\nEliza: Let's take a 20-minute walk first...",
    "metadata": {"conversation_id": "uuid", "exchange_type": "circuit_breaker"},
    "memory_type": "task"
}
```

### Emotional Intelligence Implementation

**From "How Eliza Should Respond" Case Study:**

#### 1. The Stressor Log (In Personal Memory)

**When User Mentions Stressor:**
- Extract distinct problems from message
- Store each in personal memory with metadata:
  ```python
  {
      "stressor": true,
      "emotion": "fear",  # From Story 2.6, or heuristic for MVP
      "category": "academic",
      "intensity": 0.8
  }
  ```

**In Future Conversations:**
- Retrieve stressors from personal memory
- Reference in response: "Is this about the class registration, or something new?"
- Track which stressors have been resolved

#### 2. Control Triage (In System Prompt)

**System Prompt Guidance:**
> "When user describes stressors, distinguish:
> - **Controllable**: Assignments, email responses, internship applications
>   - Push gently: 'Let's break this into one small step.'
> - **Uncontrollable**: Other people's feelings, closed deadlines, external events
>   - Guide to acceptance: 'We can't change that. Let's focus on what we can control.'"

**LLM Reasoning:** GPT-4o-mini will apply this pattern based on prompt instruction

#### 3. Energy-Based Push (Using `energy_level` State)

**MVP Heuristic (Proposed Implementation - Refined in Story 2.6):**

**Note:** This is a proposed MVP implementation subject to testing and refinement. Story 2.6 will replace with emotion detection model.

```python
def estimate_energy_level(message: str, emotional_state: Dict) -> str:
    # High: Short, enthusiastic messages
    if len(message) < 50 and any(word in message.lower() for word in ["great", "awesome", "yes", "!"]):
        return "high"

    # Low: Long messages with stress keywords
    if len(message) > 200 and any(word in message.lower() for word in ["overwhelm", "anxious", "stressed", "tired"]):
        return "low"

    return "medium"
```

**System Prompt Adaptation:**
> "Adapt your intensity:
> - **High Energy** (joy, neutral): 'You're on a roll! Let's use this momentum.'
> - **Low Energy** (sadness, fear): 80% validation + 20% 'one small win'
>   - Structure: (1) Validate → (2) Offer circuit breaker → (3) Micro-task"

#### 4. Circuit Breaker Protocol (Anti-Cripple)

**Trigger Conditions (In System Prompt):**
> "If user exhibits overwhelm indicators:
> - `stressor_count > 5` (from retrieved memories)
> - `emotion == 'overwhelm' OR 'fear'`
> - Time: Late evening (after 8pm user's local time)
>
> **Then**: Primary goal shifts from Productivity → Preservation
> **Response**: 'Forcing work now will be counterproductive. Let's try [activity from memory] first.'"

**Example Response:**
```
User: "I have 5 deadlines, a broken relationship, and I can't sleep."

Eliza (Circuit Breaker):
"That's a lot to carry. Before we plan any work, let's pause. You mentioned you enjoy evening walks. Let's schedule a 20-minute walk right now. We can talk about the deadlines after that, if you still want to."
```

### LangGraph State Machine Design Patterns

**Pattern 1: Typed State (Best Practice)**

```python
from typing import TypedDict, List
from langchain.schema import BaseMessage

class ElizaState(TypedDict):
    messages: List[BaseMessage]
    user_id: str
    # ... other fields
```

**Why TypedDict?**
- Type checking at development time
- Auto-completion in IDEs
- Clear state schema documentation

**Pattern 2: Async Nodes (Required for DB Calls)**

```python
async def recall_context(state: ElizaState) -> ElizaState:
    memories = await memory_service.query_memories(...)
    state["retrieved_memories"] = memories
    return state
```

**Why Async?**
- Memory service uses async SQLAlchemy
- Non-blocking LLM calls (Story 2.4 streaming)
- Better performance under load

**Pattern 3: Conditional Edges (Future Enhancement)**

```python
def should_trigger_circuit_breaker(state: ElizaState) -> str:
    if len(state["current_stressors"]) > 5 and state["energy_level"] == "low":
        return "circuit_breaker_node"
    return "reason"

graph.add_conditional_edges(
    "recall_context",
    should_trigger_circuit_breaker,
    {
        "circuit_breaker_node": "circuit_breaker_node",
        "reason": "reason"
    }
)
```

**Why Conditional?**
- Enables dynamic flow based on state
- Can bypass `reason` node for emergency responses
- Better separation of empathy logic

### LangGraph Studio Integration (Visual Debugging)

**Setup (from LANGGRAPH-STUDIO-SETUP.md):**

1. **Install CLI:**
   ```bash
   pip install langgraph-cli
   ```

2. **Create `langgraph.json`:**
   ```json
   {
     "graphs": {
       "eliza_agent": "app.agents.eliza_agent:ElizaAgent"
     },
     "env": ".env"
   }
   ```

3. **Start Studio:**
   ```bash
   langgraph dev
   # Opens http://localhost:8123
   ```

**Studio Features:**
- **Graph Visualization**: See all nodes and edges
- **State Inspection**: View state at each node
- **Step-by-Step Execution**: Debug node-by-node
- **Message History**: See conversation flow
- **Memory Queries**: Inspect retrieved memories
- **LLM Calls**: View prompts and responses

**Use Cases:**
- Debug why agent didn't retrieve expected memories
- Test empathy patterns with sample conversations
- Verify state transitions
- Optimize prompt engineering

### GPT-4o-mini vs GPT-4o Decision (Cost Optimization)

**From Tech Spec (ADR-009):**

**GPT-4o-mini:**
- **Cost**: $0.15/$0.60 per 1M tokens (input/output)
- **Quality**: Sufficient for empathetic conversations (tested in production systems)
- **Speed**: Faster than GPT-4o (~200ms vs ~500ms first token)
- **Use Case**: Chat, goal planning, emotional responses

**GPT-4o:**
- **Cost**: $2.50/$10 per 1M tokens (80% more expensive)
- **Quality**: Superior writing, better for complex narratives
- **Use Case**: Story generation (Story 4.2), premium features

**Daily Cost Breakdown (Per User):**
- Chat: 10K tokens in + 5K tokens out = $0.001 + $0.003 = **$0.004/day**
- Embedding: 2K tokens/day = $0.00004 (negligible)
- **Total Epic 2**: ~$0.004/user/day (**well within $0.50 target**)

**When to Use GPT-4o:**
- Narrative generation (Story 4.2)
- Complex multi-step reasoning (future)
- User explicitly requests "premium" mode (future monetization)

### Prompt Engineering Strategy

**System Prompt Components:**

1. **Identity & Purpose** (sets tone)
2. **Empathy Techniques** (control triage, energy-based push, circuit breaker)
3. **Response Guidelines** (validate, clarify, micro-actions)
4. **Memory Usage** (reference past, acknowledge progress)

**Few-Shot Examples (Optional Enhancement):**

```python
ELIZA_SYSTEM_PROMPT = """
You are Eliza, an emotionally intelligent AI companion...

[Empathy techniques...]

**Example Conversations:**

User: "I'm overwhelmed with 5 deadlines."
Eliza: "That's a lot to carry. Before we plan, let's try a 20-minute walk first."

User: "I'm not sure if I can do this."
Eliza: "Tell me more—what specifically feels hardest right now?"

[End examples]
"""
```

**Versioning for A/B Testing (Future):**
- Store prompt versions in database
- Track which version user sees
- Measure quality metrics (user satisfaction, conversation length, goal completion)

### Implementation Order (Vertical Slice vs Horizontal)

**⚠️ STRATEGIC NOTE:** Tech spec was revised 2025-11-12 to recommend **vertical slice approach** (Story 2.5 before 2.2/2.3). See `tech-spec-epic-2.md` lines 27-71 for rationale.

**Option A: Vertical Slice (Recommended per Tech Spec Revision)**

Complete Stories 2.5 → 2.2 → 2.3 in sequence:
- Story 2.5: Chat UI with essential memory (inline operations)
- Story 2.2: Memory service extraction (refactor from 2.5)
- Story 2.3: Eliza agent with LangGraph (uses extracted service)

**Benefits:**
- Working chat sooner (see memory in action immediately)
- Test empathy patterns in browser right away
- Validate architecture before committing to service layer
- Faster feedback loop, lower risk

**Option B: Horizontal (Original Plan - This Story Was Written For)**

Complete Stories 2.2 → 2.3 → 2.4 → 2.5:
- Story 2.2: Memory service (without seeing it work)
- Story 2.3: Eliza agent (this story)
- Story 2.4: Chat API
- Story 2.5: Frontend UI

**Benefits:**
- Cleaner separation of concerns from the start
- Story 2.3 depends on Story 2.2 memory service APIs

**Current Status:** Story 2.3 is written for **Option B** (assumes Story 2.2 is complete). If following **Option A** (vertical slice), defer Story 2.3 until after Story 2.5 and 2.2 are complete, or implement simplified memory operations inline and refactor later.

**Recommendation:** Follow tech spec revision (Option A) for lower risk. This story remains valid but may be implemented later in sequence.

### Learnings from Previous Story (2.1: Memory Schema)

**From Story 2.1 Dev Agent Record:**

1. **SQLAlchemy Reserved Keywords**: Avoid using `metadata` as attribute name
   - Solution: Use `extra_data` with column mapping
   - **Impact on Story 2.3**: Memory retrieval returns `extra_data`, not `metadata`

2. **Async Patterns Required**: All database operations must use async/await
   - **Impact**: All nodes must be async functions
   - Example: `async def recall_context(state: ElizaState) -> ElizaState:`

3. **HNSW Index Ready**: Vector similarity search optimized for < 100ms p95
   - **Impact**: Memory retrieval will be fast (no performance concerns)

4. **Test Data Cleanup**: No automatic cleanup between test runs
   - **Impact**: Test script should use unique user IDs or cleanup manually

5. **Migration 003 & 004**: Two separate migrations for memory tables
   - Migration 003: Core tables
   - Migration 004: Performance indexes
   - **Impact**: Both must be applied before Story 2.3

### Project Structure Notes

**New Files Created:**

```
packages/backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py          # NEW: Export ElizaAgent
│   │   ├── eliza_agent.py       # NEW: Main agent class with nodes
│   │   ├── state.py             # NEW: ElizaState TypedDict
│   │   └── prompts.py           # NEW: System prompts
│   └── tests/
│       └── test_eliza_agent.py  # NEW: Agent tests
├── langgraph.json               # NEW: LangGraph Studio config
└── docs/epic-2/
    └── ELIZA-AGENT-GUIDE.md     # NEW: Agent documentation
```

**Modified Files:**
```
packages/backend/
├── app/
│   ├── agents/
│   │   └── __init__.py          # UPDATE: Import ElizaAgent, ElizaState
├── .env.example                 # UPDATE: Add OPENAI_API_KEY if missing
└── pyproject.toml               # UPDATE: Add langchain, langgraph dependencies
```

### Relationship to Epic 2 Stories

This story (2-3) **builds on**:
- **Story 2-1**: Uses `memories` table with pgvector for memory retrieval
- **Story 2-2**: Depends on `MemoryService.add_memory()`, `MemoryService.query_memories()`
  - **⚠️ CRITICAL**: Story 2.2 must be completed first (or memory operations implemented inline)

This story (2-3) **enables**:
- **Story 2-4 (Chat API)**: Chat API calls `ElizaAgent.chat()` to generate responses
- **Story 2-5 (Chat UI)**: Frontend consumes chat API with streaming
- **Story 2-6 (Emotion Detection)**: Emotion service updates `state["emotional_state"]`, refining energy-based push

**Dependencies Flow:**
```
Story 2-1 (Memory Schema) ✅ DONE
    ↓
Story 2-2 (Memory Service) ⏳ DRAFTED (critical dependency)
    ↓
Story 2-3 (Eliza Agent) ⬅️ THIS STORY
    ↓
Story 2-4 (Chat API)
    ↓
Story 2-5 (Chat UI)
    = Working AI Companion! 🎉
```

### References

**Source Documents:**
- **Epic 2 Tech Spec**: `docs/tech-spec-epic-2.md` (lines 95-119: Agent architecture, lines 721-734: AC2)
- **Epics File**: `docs/epics.md` (lines 386-424: Story 2.3 requirements)
- **How Eliza Should Respond**: `docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md` (Emotional intelligence techniques)
- **Implementation Guide**: `docs/epic-2/2-1-to-2-5-implementation-guide (draft).md` (LangGraph setup, agent patterns)
- **LangGraph Studio Setup**: `docs/epic-2/LANGGRAPH-STUDIO-SETUP.md` (Visual debugging)
- **Implementation Strategy**: `docs/epic-2/IMPLEMENTATION-STRATEGY.md` (Phased approach)

**Technical Documentation:**
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LangChain**: https://python.langchain.com/docs/get_started/introduction
- **OpenAI GPT-4o-mini**: https://platform.openai.com/docs/models/gpt-4o-mini
- **LangGraph Studio**: https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/

---

## Definition of Done

- [ ] ✅ LangGraph and LangChain dependencies installed
- [ ] ✅ `ElizaState` TypedDict defined with all required fields
- [ ] ✅ `ELIZA_SYSTEM_PROMPT` created with empathy techniques
- [ ] ✅ All 5 nodes implemented (`receive_input`, `recall_context`, `reason`, `respond`, `store_memory`)
- [ ] ✅ LangGraph state machine built with proper edges
- [ ] ✅ `ElizaAgent.chat()` convenience method works
- [ ] ✅ Memory retrieval queries personal tier always, project/task conditionally
- [ ] ✅ ChatOpenAI configured with GPT-4o-mini model
- [ ] ✅ Conversation exchanges stored as task memories
- [ ] ✅ All acceptance criteria manually verified
- [ ] ✅ Unit tests created and passing (mock LLM + memory service)
- [ ] ✅ Integration tests with real DB passing (optional but recommended)
- [ ] ✅ LangGraph Studio configuration working
- [ ] ✅ Code follows async SQLAlchemy 2.0 patterns
- [ ] ✅ Type hints and docstrings for all functions
- [ ] ✅ No secrets committed (OPENAI_API_KEY in .env only)
- [ ] ✅ Documentation updated (agent guide, setup notes)
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline

- **Task 1-2** (Dependencies + State Schema): 1 hour
- **Task 3** (System Prompt): 2 hours (research empathy patterns, test variations)
- **Task 4-8** (5 Nodes): 3 hours (1 hour for recall_context, reason; 30min each for others)
- **Task 9** (Build Graph): 1 hour
- **Task 10** (Testing): 2-3 hours (unit + integration tests)
- **Task 11** (LangGraph Studio): 1 hour
- **Task 12** (Documentation): 1 hour

**Total:** 11-12 hours (aligns with story estimate)

### Risk Mitigation

**Risk:** Story 2.2 (Memory Service) not yet complete
**Mitigation:** Implement simplified memory operations inline in Story 2.3, extract to service later; or wait for Story 2.2 completion

**Risk:** GPT-4o-mini responses not empathetic enough
**Mitigation:** Extensive prompt engineering; A/B test with GPT-4o if quality issues; few-shot examples in system prompt

**Risk:** LangGraph state not persisting across conversation turns
**Mitigation:** Test conversation state management thoroughly; store conversation history in database (Story 2.4); limit history to last 10 messages

**Risk:** Memory retrieval too slow (> 100ms)
**Mitigation:** HNSW index already optimized (Story 2.1); limit queries (max 5 personal + 3 project + 3 task); cache user context

**Risk:** Circuit breaker logic not triggering correctly
**Mitigation:** Manual testing with overwhelm scenarios; conditional edges if needed; refine prompt instructions

### Future Enhancements (Post-Story)

- [ ] Add conditional edges for circuit breaker (bypass `reason` for emergency responses)
- [ ] Implement conversation branching (goal planning vs venting vs reflection)
- [ ] Add prompt versioning and A/B testing
- [ ] Optimize memory retrieval (cache frequent queries)
- [ ] Add conversation summarization for long histories (> 10 messages)
- [ ] Integrate emotion detection (Story 2.6) to refine energy-based push
- [ ] Add character switching (Story 2.7) for different personas

---

**Last Updated:** 2025-11-13
**Story Status:** drafted
**Next Steps:** Wait for Story 2.2 completion OR implement inline memory operations → Run `story-context` workflow → mark `ready-for-dev`

## Dev Agent Record

### Context Reference

- Context file: `docs/stories/2-3-build-eliza-agent-with-langgraph.context.xml`
- Generated: 2025-11-13
- Includes: Epic 2 tech spec, emotional intelligence design, implementation strategy, LangGraph Studio setup, memory models, test patterns

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

### Completion Notes List

### File List
