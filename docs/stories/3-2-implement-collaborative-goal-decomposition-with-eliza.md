# Story 3.2: Implement Collaborative Goal Decomposition with Eliza

**Story ID:** 3.2
**Epic:** 3 - Goal & Mission Management
**Status:** drafted
**Priority:** P0 (Core Productivity Loop)
**Estimated Effort:** 12-14 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18
**Updated:** 2025-11-18

---

## User Story

**As a** user,
**I want** Eliza to help me break down big goals into actionable steps,
**So that** abstract ambitions become concrete plans.

---

## Context

### Problem Statement

Overwhelming goals paralyze users. "Be healthier" or "Improve my career" feel impossibly large without a clear path forward. Story 3.2 builds Eliza's collaborative decomposition capability - a guided conversation that transforms vague aspirations into structured milestone plans and actionable micro-quests.

This story extends Eliza's LangGraph agent (Story 2.3) with a specialized `goal_decomposition` node that:
1. **Explores the "Why"**: Understanding user motivation drives better decomposition
2. **Identifies Constraints**: Time, resources, dependencies shape realistic plans
3. **Proposes Milestones**: 3-7 major steps that chunk the goal into manageable phases
4. **Generates Micro-Quests**: Small (10-30 min) actions linked to each milestone
5. **Iterates with User**: Collaborative refinement, not top-down prescription

### Why This Approach?

**From Architecture (ARCHITECTURE.md):**

LangGraph's stateful agent pattern enables multi-turn conversations where Eliza:
- ✅ **Remembers Context**: Goal details, user responses, constraints discussed
- ✅ **Iterates Naturally**: "That milestone feels too big" → agent refines without losing state
- ✅ **Structured Output**: Uses LangChain's structured output parsing for consistent quest format
- ✅ **Integrates Memory**: Queries 3-tier memory for user patterns, preferences, past successes

**From Product Brief:**

Collaborative decomposition respects user agency:
- **NOT**: "Here are 5 steps you must follow"
- **YES**: "I'm thinking we could try... does this resonate with you?"

This aligns with the emotional intelligence principle: Eliza coaches, doesn't command.

### Dependencies

- **Prerequisite Stories:**
  - 2.3 (Eliza Agent with LangGraph) ✅ Required - Extends existing agent
  - 2.4 (Companion Chat API with SSE) ✅ Required - Conversation interface
  - 3.1 (Goal Data Models and CRUD APIs) ✅ Complete - Goal records to decompose

- **Epic 3 Context:** This story **enables**:
  - Story 3.3: Mission system uses generated quests from decomposition
  - Epic 5: Progress tracking shows milestone completion rates

- **External Dependencies:**
  - OpenAI GPT-4o-mini API for LLM reasoning
  - LangChain structured output for quest parsing

### Technical Background

**Goal Decomposition Patterns (by Goal Type):**

**Abstract Goals** ("Be more confident"):
1. **Exploration Phase**: "What does confidence mean to you?" "What situations trigger self-doubt?"
2. **Root Cause Analysis**: Identify specific blockers (public speaking, social anxiety, impostor syndrome)
3. **Progressive Milestones**: Start small, build gradually (journal → small talk → presentations)
4. **Reflection Quests**: Many abstract goals need introspection missions

**Concrete Goals** ("Run half-marathon by June 15"):
1. **Capability Assessment**: Current fitness level, training experience
2. **Timeline Calculation**: Weeks until target → training phases (base, build, taper)
3. **Structured Milestones**: Week 1-4 (base building), Week 5-8 (increase mileage), etc.
4. **Training Quests**: Specific workouts with duration/distance

---

## Acceptance Criteria

### AC1: Eliza Initiates Goal Decomposition Conversation

**Given** I've created a goal (Story 3.1)
**When** I ask Eliza "Help me plan my goal: [goal title]"
**Then** Eliza recognizes this as a decomposition request and enters `goal_decomposition` conversation mode

**And** Eliza responds with:
- Acknowledgment of the goal
- Opening question about my "why" (motivation)
- Warm, collaborative tone

**Example Interaction:**
```
User: "Help me plan my goal: Graduate early from Georgia Tech"

Eliza: "I'd love to help you work toward graduating early! 🎓 That's an ambitious goal.
Before we dive into the how, I'm curious - what's driving this for you? Is it wanting to
start your career sooner, financial reasons, or something else? Understanding your 'why'
will help us create a plan that truly fits."
```

### AC2: Eliza Explores Constraints and Context

**Given** Eliza is in goal decomposition mode
**When** I answer her initial questions
**Then** Eliza asks clarifying questions about constraints:

**Constraint Categories:**
- **Time**: "How much time can you dedicate per week?"
- **Resources**: "Do you have access to X?" (courses, mentors, equipment, etc.)
- **Dependencies**: "What needs to happen first?"
- **Current State**: "Where are you starting from?"

**And** Eliza uses my answers to inform milestone proposals

**Example Interaction:**
```
User: "I want to graduate early to start working and reduce student debt."

Eliza: "That makes a lot of sense. Let's figure out what's realistic. A few questions:
1. How many credits do you need to graduate, and how many do you have now?
2. What's your current course load capacity? (How many courses per semester feels manageable?)
3. Are there any prerequisite chains or required courses only offered certain semesters?
4. How are you balancing this with other commitments like work or internships?"
```

### AC3: Eliza Proposes 3-7 Milestone Steps

**Given** Eliza has gathered sufficient context
**When** she generates a decomposition plan
**Then** Eliza proposes 3-7 milestones that:

- Are **sequenced logically** (prerequisites before dependent steps)
- Are **time-bounded** (approximate duration or target completion)
- Are **concrete enough to measure** (not vague like "prepare more")
- **Match goal type** (abstract goals → exploratory milestones, concrete goals → structured milestones)

**And** Eliza presents milestones in a readable format with rationale

**Example Milestone Proposal:**
```
Eliza: "Based on what you've shared, here's a potential path to graduating in May 2026:

**Milestone 1** (Dec 2025): Course Planning & Registration
- Map remaining credits to available semesters
- Identify summer course options (if needed)
- Register for spring courses
Timeline: Complete by mid-December

**Milestone 2** (Jan-May 2026): Spring Semester Execution
- Complete 18 credits (6 courses)
- Maintain GPA above 3.0
- Set up study routines for heavier load
Timeline: 4 months

**Milestone 3** (May-Aug 2026): Summer Intensive (if needed)
- Take 2-3 courses to close credit gap
- Or use summer for internship if credits align
Timeline: 3 months

**Milestone 4** (Sep-Dec 2026): Final Semester Prep
- Ensure all degree requirements met
- Apply for graduation in May 2026
- Prepare for job search
Timeline: 4 months

Does this structure feel right to you? Any milestones that seem too aggressive or unclear?"
```

### AC4: Eliza Generates Micro-Quests for Each Milestone

**Given** Eliza has proposed milestones and I've approved them (or refined them)
**When** Eliza generates quest suggestions
**Then** each quest is structured with:

**Quest Fields:**
- `title`: Clear, actionable task (e.g., "Map remaining course credits")
- `description`: Detailed guidance on how to complete
- `estimated_minutes`: Realistic time estimate (10-30 min for micro-quests)
- `energy_level`: Low/Medium/High (matches task difficulty)
- `milestone_id`: Links quest to parent milestone
- `sequence_order`: Logical ordering within milestone

**And** quests are **small enough to start immediately** (no quest should feel overwhelming)

**And** quests are **sequenced logically** (earlier quests enable later ones)

**Example Quest Generation:**
```
Eliza: "Great! Let's start with Milestone 1. Here are some small quests to get momentum:

**Quest 1.1**: "List all remaining course requirements"
- Pull up your degree audit and list every course you still need
- Note credit hours for each
- Flag any with prerequisites or limited offering schedules
Estimated time: 15 minutes | Energy: Low

**Quest 1.2**: "Research spring course offerings"
- Check course catalog for spring 2026
- Identify which required courses are offered
- Note section availability and time conflicts
Estimated time: 20 minutes | Energy: Low

**Quest 1.3**: "Draft spring schedule (3 options)"
- Create 3 different schedule options (12, 15, 18 credits)
- Consider balance: hard courses spread across semester
- Check for time conflicts and commute logistics
Estimated time: 30 minutes | Energy: Medium

Would you like to start with Quest 1.1, or should we adjust anything?"
```

### AC5: User Can Approve, Modify, or Reject Suggestions

**Given** Eliza has proposed milestones and quests
**When** I provide feedback
**Then** Eliza:

- **Approval**: "Let's do it!" → Saves decomposition to database
- **Modification**: "Milestone 2 feels too aggressive" → Refines that milestone, re-proposes
- **Rejection**: "This doesn't match my situation" → Asks clarifying questions, starts over
- **Partial Approval**: "Milestones look good, but quest 1.3 is too long" → Adjusts specific quests

**And** Eliza maintains conversation state across multiple refinement rounds

**Example Refinement Interaction:**
```
User: "Milestone 2 seems really intense. 18 credits while working part-time might burn me out."

Eliza: "You're absolutely right to flag that. Let's adjust. A few options:

Option A: Reduce spring load to 15 credits, extend timeline by one semester
Option B: Keep 18 credits but identify 2-3 'easier' electives to balance the hard courses
Option C: Plan for a lighter summer (1 course) and shift credits there

What feels more sustainable to you?"
```

### AC6: Approved Decomposition is Saved to Database

**Given** I've approved the final decomposition plan
**When** Eliza confirms "Got it! I've saved your plan"
**Then** a `goal_decomposition` record is created with:

**Database Schema (`goal_decompositions` table):**
- `id`: UUID primary key
- `goal_id`: Foreign key to goals table
- `created_at`: Timestamp of decomposition
- `milestones`: JSONB array of milestone objects
- `generated_quests`: JSONB array of quest objects (not yet created as missions)
- `user_approved`: BOOLEAN (true if user explicitly approved)
- `decomposition_metadata`: JSONB (constraints discussed, user preferences, rationale)

**And** the JSONB structure is well-formed for future mission creation (Story 3.3)

**Example JSONB Structure:**
```json
{
  "milestones": [
    {
      "id": 1,
      "title": "Course Planning & Registration",
      "description": "Map remaining credits to available semesters...",
      "target_completion": "2025-12-15",
      "estimated_weeks": 2
    }
  ],
  "generated_quests": [
    {
      "milestone_id": 1,
      "title": "List all remaining course requirements",
      "description": "Pull up your degree audit...",
      "estimated_minutes": 15,
      "energy_level": "low",
      "sequence_order": 1
    }
  ],
  "decomposition_metadata": {
    "goal_type": "concrete",
    "constraints": {
      "time_per_week": "15 hours",
      "hard_deadline": "2026-05-15",
      "current_credits": 90,
      "required_credits": 120
    },
    "user_motivation": "Reduce student debt, start career sooner"
  }
}
```

### AC7: Decomposition Conversation Uses Structured Output Parsing

**Given** Eliza is generating milestones and quests
**When** the LLM responds
**Then** the response is parsed using LangChain's structured output tools

**And** the output matches a predefined Pydantic schema for consistency

**And** parsing failures are handled gracefully (Eliza asks for clarification if output is malformed)

**Schema Example:**
```python
class MilestoneProposal(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    target_completion: Optional[date] = None
    estimated_weeks: Optional[int] = None

class QuestProposal(BaseModel):
    milestone_id: int
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    estimated_minutes: int = Field(ge=5, le=120)  # 5 min to 2 hours
    energy_level: Literal["low", "medium", "high"]
    sequence_order: int

class GoalDecompositionOutput(BaseModel):
    milestones: list[MilestoneProposal]
    generated_quests: list[QuestProposal]
    rationale: str = Field(description="Brief explanation of decomposition strategy")
```

### AC8: Eliza Integrates User Memory for Personalized Decomposition

**Given** I have memory records from previous conversations (Story 2.2)
**When** Eliza decomposes a goal
**Then** she queries my memory for relevant context:

**Memory Queries:**
- **Personal Tier**: Work preferences, energy patterns, past successes
  - Example: "You mentioned you work best in the morning" → Schedule hard quests AM
- **Project Tier**: Related goals, previous decomposition patterns
  - Example: "Last time we broke down a goal, you preferred weekly milestones"
- **Task Tier**: Recent mission completions, struggle points
  - Example: "You've been crushing 20-minute quests lately, let's use that momentum"

**And** memory-informed decomposition feels personalized, not generic

**Example Memory Integration:**
```
Eliza: "I noticed from our past conversations that you tend to overcommit and then
feel overwhelmed. For this goal, let's build in buffer time - how about we plan for
15 credits in spring, which gives you breathing room, rather than maxing out at 18?"
```

---

## Tasks / Subtasks

### Task 1: Extend Eliza Agent with Goal Decomposition Node (AC: #1, #2, #3, #4)

- [ ] **1.1** Update `packages/backend/app/agents/eliza_agent.py` LangGraph state machine
- [ ] **1.2** Add `goal_decomposition` node to agent graph
- [ ] **1.3** Define state fields for decomposition:
  ```python
  class AgentState(TypedDict):
      messages: Annotated[list, add_messages]
      goal_id: Optional[str]
      goal_details: Optional[dict]  # Title, type, value_category
      decomposition_phase: str  # "explore_why", "gather_constraints", "propose_milestones", "generate_quests", "refine"
      milestones: Optional[list[dict]]
      generated_quests: Optional[list[dict]]
      user_feedback: Optional[str]
      memory_context: Optional[list[dict]]  # Retrieved from memory service
  ```
- [ ] **1.4** Implement `goal_decomposition` node with sub-phases:
  - `explore_why()`: Ask about motivation, understand deeper context
  - `gather_constraints()`: Time, resources, dependencies questions
  - `propose_milestones()`: Generate 3-7 milestone structure
  - `generate_quests()`: Create micro-quests linked to milestones
  - `refine_based_on_feedback()`: Handle user modifications
- [ ] **1.5** Add conditional edges for phase transitions:
  - User input → determine current phase → route to appropriate sub-node
- [ ] **1.6** Integrate memory queries in decomposition node:
  - Query personal memory for work patterns, preferences
  - Query project memory for related goals, past decompositions

### Task 2: Create Database Schema for Goal Decompositions (AC: #6)

- [ ] **2.1** Create Alembic migration: `alembic revision -m "create goal_decompositions table"`
- [ ] **2.2** Define `goal_decompositions` table:
  ```sql
  CREATE TABLE goal_decompositions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
      created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
      milestones JSONB NOT NULL,
      generated_quests JSONB NOT NULL,
      user_approved BOOLEAN NOT NULL DEFAULT FALSE,
      decomposition_metadata JSONB,
      CONSTRAINT fk_goal FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
  );
  CREATE INDEX idx_decompositions_goal ON goal_decompositions(goal_id);
  ```
- [ ] **2.3** Apply migration: `alembic upgrade head`

### Task 3: Create SQLAlchemy Model and Pydantic Schemas (AC: #6, #7)

- [ ] **3.1** Create `packages/backend/app/models/goal_decomposition.py`
- [ ] **3.2** Define `GoalDecomposition` model with JSONB columns for milestones/quests
- [ ] **3.3** Create `packages/backend/app/schemas/goal_decomposition.py`
- [ ] **3.4** Define Pydantic schemas for structured output:
  ```python
  class MilestoneProposal(BaseModel):
      id: int  # Milestone number (1, 2, 3, ...)
      title: str = Field(max_length=200)
      description: str = Field(max_length=1000)
      target_completion: Optional[date] = None
      estimated_weeks: Optional[int] = None

  class QuestProposal(BaseModel):
      milestone_id: int  # Links to MilestoneProposal.id
      title: str = Field(max_length=200)
      description: str = Field(max_length=1000)
      estimated_minutes: int = Field(ge=5, le=120)
      energy_level: Literal["low", "medium", "high"]
      sequence_order: int

  class DecompositionMetadata(BaseModel):
      goal_type: Literal["abstract", "concrete"]
      constraints: dict  # Flexible structure for time, resources, dependencies
      user_motivation: Optional[str] = None
      refinement_history: list[dict] = []  # Track user feedback iterations

  class GoalDecompositionOutput(BaseModel):
      milestones: list[MilestoneProposal]
      generated_quests: list[QuestProposal]
      rationale: str = Field(description="Why this decomposition structure")

  class GoalDecompositionResponse(BaseModel):
      id: UUID
      goal_id: UUID
      milestones: list[MilestoneProposal]
      generated_quests: list[QuestProposal]
      user_approved: bool
      decomposition_metadata: DecompositionMetadata
      created_at: datetime
  ```

### Task 4: Implement Structured Output Parsing with LangChain (AC: #7)

- [ ] **4.1** Install LangChain structured output tools: `poetry add langchain-openai`
- [ ] **4.2** Configure structured output chain:
  ```python
  from langchain.output_parsers import PydanticOutputParser
  from langchain.prompts import PromptTemplate

  parser = PydanticOutputParser(pydantic_object=GoalDecompositionOutput)
  prompt = PromptTemplate(
      template="...\n{format_instructions}\n...",
      input_variables=["goal_details", "user_constraints"],
      partial_variables={"format_instructions": parser.get_format_instructions()}
  )
  ```
- [ ] **4.3** Add error handling for malformed LLM outputs
- [ ] **4.4** Retry logic if parsing fails (up to 2 retries with refined prompts)

### Task 5: Create Goal Decomposition Service (AC: #5, #6, #8)

- [ ] **5.1** Create `packages/backend/app/services/goal_decomposition_service.py`
- [ ] **5.2** Implement `GoalDecompositionService` class:
  ```python
  class GoalDecompositionService:
      def __init__(self, db: AsyncSession, memory_service: MemoryService):
          self.db = db
          self.memory_service = memory_service

      async def create_decomposition(
          self, goal_id: UUID, milestones: list, quests: list, metadata: dict, user_approved: bool
      ) -> GoalDecomposition:
          """Save decomposition to database."""
          ...

      async def get_decomposition_by_goal(self, goal_id: UUID) -> Optional[GoalDecomposition]:
          """Retrieve existing decomposition for a goal."""
          ...

      async def update_decomposition(
          self, decomposition_id: UUID, milestones: list, quests: list, user_approved: bool
      ) -> GoalDecomposition:
          """Update decomposition after user refinement."""
          ...

      async def get_user_memory_for_decomposition(self, user_id: str, goal_details: dict) -> list[dict]:
          """Query memory service for relevant context."""
          # Query personal memory for preferences, patterns
          # Query project memory for related goals
          # Return as list of memory objects for agent context
          ...
  ```

### Task 6: Add Decomposition Triggers in Chat API (AC: #1)

- [ ] **6.1** Update Eliza chat endpoint to detect goal decomposition requests
- [ ] **6.2** Add intent detection patterns:
  - "Help me plan my goal: [title]"
  - "Break down my goal about [topic]"
  - "I need help with my [goal_type] goal"
- [ ] **6.3** When detected, fetch goal details from database (using goal_id or title search)
- [ ] **6.4** Initialize agent state with `decomposition_phase = "explore_why"`
- [ ] **6.5** Route to `goal_decomposition` node in LangGraph

### Task 7: Implement Frontend Modal/Page for Goal Planning (AC: #1-#6)

- [ ] **7.1** Create `packages/frontend/src/components/goals/GoalDecompositionModal.tsx`
- [ ] **7.2** Design modal/page with:
  - Goal details display (title, type, value_category)
  - Chat interface with Eliza (reuse companion chat component)
  - Visual milestone/quest preview as they're proposed
  - Approve/Modify/Reject buttons
  - Refinement feedback text area
- [ ] **7.3** Add modal trigger from goal detail page: "Plan this goal with Eliza" button
- [ ] **7.4** Stream Eliza's responses via SSE (Story 2.4 pattern)
- [ ] **7.5** Display milestones and quests in structured format (cards or accordion)
- [ ] **7.6** Save approved decomposition on user confirmation

### Task 8: Create Unit Tests (AC: All)

- [ ] **8.1** Create `packages/backend/tests/services/test_goal_decomposition_service.py`
- [ ] **8.2** Test service methods:
  - `test_create_decomposition()`: Saves to database correctly
  - `test_get_decomposition_by_goal()`: Retrieves existing decomposition
  - `test_update_decomposition()`: Updates milestones and quests
  - `test_get_user_memory_for_decomposition()`: Queries memory correctly
- [ ] **8.3** Create `packages/backend/tests/agents/test_eliza_decomposition_node.py`
- [ ] **8.4** Test agent node logic:
  - `test_explore_why_phase()`: Asks appropriate motivation questions
  - `test_gather_constraints_phase()`: Extracts constraint information
  - `test_propose_milestones_abstract_goal()`: Generates exploratory milestones
  - `test_propose_milestones_concrete_goal()`: Generates structured milestones
  - `test_generate_quests()`: Creates quests with correct fields
  - `test_refine_based_on_feedback()`: Handles user modifications
- [ ] **8.5** Mock LLM calls for deterministic testing
- [ ] **8.6** Target: 80%+ coverage for decomposition service and agent node

### Task 9: Integration Tests and Manual Testing (AC: All)

- [ ] **9.1** Create `packages/backend/tests/integration/test_goal_decomposition_flow.py`
- [ ] **9.2** Test end-to-end decomposition:
  - Create goal via API
  - Initiate decomposition conversation
  - Simulate multi-turn conversation (explore, constrain, propose, approve)
  - Verify decomposition saved correctly
- [ ] **9.3** Test structured output parsing with real LLM calls (integration test, not mocked)
- [ ] **9.4** Manual testing checklist:
  - [ ] Start decomposition from goal detail page
  - [ ] Complete full conversation with Eliza (explore why, constraints, milestones, quests)
  - [ ] Test refinement loop (modify milestone, Eliza re-proposes)
  - [ ] Approve final plan, verify saved to database
  - [ ] Check JSONB structure in database matches schema
  - [ ] Test with both abstract and concrete goals
  - [ ] Verify memory integration (Eliza references past preferences)

### Task 10: Documentation and Examples (AC: All)

- [ ] **10.1** Add docstrings to all service methods and agent nodes
- [ ] **10.2** Document structured output schemas with examples
- [ ] **10.3** Create example decomposition flows in `docs/API-TESTING-GUIDE.md`
- [ ] **10.4** Document conversation patterns for abstract vs. concrete goals
- [ ] **10.5** Add troubleshooting guide for structured output parsing failures

---

## Dev Notes

### Goal Decomposition Conversation Design

**Conversation Flow (Multi-Turn):**

**Phase 1: Explore Why (1-2 turns)**
- Eliza: "What's driving this goal for you?"
- User: "I want to start my career sooner and reduce debt"
- Eliza: "That makes sense. How urgent is this? Is May 2026 a hard deadline?"

**Phase 2: Gather Constraints (2-3 turns)**
- Eliza: "Let's figure out what's realistic. How many credits do you need?"
- User: "I need 30 more credits. I have 90 now."
- Eliza: "And how many courses per semester feels manageable?"
- User: "I've done 15 credits before, 18 might be pushing it."

**Phase 3: Propose Milestones (1 turn)**
- Eliza: Generates 3-7 milestones with rationale
- User: Reviews and provides feedback

**Phase 4: Refine Milestones (0-3 turns)**
- User: "Milestone 2 seems too intense"
- Eliza: Refines, re-proposes
- Repeat until approval

**Phase 5: Generate Quests (1 turn)**
- Eliza: Generates micro-quests for each milestone
- User: Reviews and approves

**Phase 6: Save & Confirm (1 turn)**
- Eliza: "I've saved your plan! Ready to start with Quest 1.1?"
- Database record created

**Total Turns**: 6-12 turns (flexible based on user input)

### Structured Output Prompting Strategy

**System Prompt for Decomposition Node:**

```python
DECOMPOSITION_SYSTEM_PROMPT = """
You are Eliza, an emotionally intelligent AI coach helping users break down goals
into manageable steps. Your role is to:

1. Understand the user's deeper motivation (the "why")
2. Identify realistic constraints (time, resources, dependencies)
3. Propose 3-7 milestone steps that chunk the goal into phases
4. Generate small micro-quests (10-30 min) for each milestone
5. Collaborate, not command - respect user agency

**Goal Type Strategies:**
- Abstract goals (e.g., "Be healthier"): Focus on exploration, introspection, incremental changes
- Concrete goals (e.g., "Run marathon"): Focus on structured training, measurable progress

**Quest Guidelines:**
- Keep quests small (5-30 minutes max)
- Sequence logically (earlier quests enable later ones)
- Vary energy levels (mix low/medium/high)
- Make them immediately actionable (no vague "prepare more")

{format_instructions}

Remember: You're coaching, not prescribing. Ask, propose, refine together.
"""
```

### Memory Integration Patterns

**Queries to Run During Decomposition:**

```python
# Query personal memory for user patterns
personal_memories = await memory_service.query_memories(
    user_id=user_id,
    query_text="work preferences energy patterns past successes",
    memory_types=[MemoryType.PERSONAL],
    limit=5
)

# Query project memory for related goals
project_memories = await memory_service.query_memories(
    user_id=user_id,
    query_text=f"{goal_title} {value_category}",
    memory_types=[MemoryType.PROJECT],
    limit=5
)

# Use memories to personalize decomposition
context_for_llm = f"""
User patterns from memory:
{format_memories(personal_memories)}

Related goals:
{format_memories(project_memories)}

Use this context to personalize the decomposition plan.
"""
```

### Abstract vs. Concrete Goal Examples

**Abstract Goal: "Be more confident"**

```
Milestones:
1. Self-Awareness (2 weeks): Understand confidence triggers
2. Small Experiments (3 weeks): Practice low-stakes interactions
3. Gradual Exposure (4 weeks): Increase social challenge level
4. Habit Formation (ongoing): Regular social practice

Quests (Milestone 1):
- Q1.1: "Journal about recent confidence dips" (10 min, low energy)
- Q1.2: "List 3 situations where you felt confident" (10 min, low energy)
- Q1.3: "Identify one recurring confidence blocker" (15 min, medium energy)
```

**Concrete Goal: "Run half-marathon by June 15, 2026"**

```
Milestones:
1. Base Building (Weeks 1-4): Build aerobic base, run 3x/week
2. Mileage Increase (Weeks 5-8): Add 10% weekly, long run on weekends
3. Tempo & Speed (Weeks 9-12): Add faster paces, maintain mileage
4. Taper & Race Prep (Weeks 13-14): Reduce volume, maintain sharpness

Quests (Milestone 1):
- Q1.1: "Run 2 miles at easy pace" (25 min, medium energy)
- Q1.2: "Cross-train: 20-minute bike or swim" (20 min, medium energy)
- Q1.3: "Complete first long run: 4 miles" (45 min, medium-high energy)
```

### Handling Edge Cases

**User Provides Unrealistic Goals:**
- Eliza: "That timeline seems really tight. Let's talk about what's truly feasible given your constraints. Would you be open to adjusting the target date or scope?"

**User Says "I don't know" to Constraint Questions:**
- Eliza: "No worries! Let's start with a flexible plan. We can adjust as we learn more about what works for you."

**LLM Generates Milestones > 7:**
- Service layer validation: If > 7 milestones, prompt LLM again with "reduce to 3-7 key milestones"

**User Modifies During Quest Generation:**
- State machine loops back to `propose_milestones` phase with updated context

### Integration with Story 3.3 (Mission System)

**From Decomposition to Missions:**

After decomposition approval, quests in `generated_quests` JSONB can be converted to Mission records (Story 3.3):

```python
# In Story 3.3: Mission creation from decomposition
decomposition = await goal_decomposition_service.get_decomposition_by_goal(goal_id)

for quest in decomposition.generated_quests:
    mission = Mission(
        goal_id=goal_id,
        user_id=user_id,
        title=quest["title"],
        description=quest["description"],
        estimated_minutes=quest["estimated_minutes"],
        energy_level=quest["energy_level"],
        value_category=goal.value_category,  # Inherit from parent goal
        priority_score=calculate_priority(quest),  # Story 3.3 algorithm
        status="pending"
    )
    db.add(mission)
```

This creates the mission pool that Story 3.3 uses for priority triads.

### References

**Source Documents:**
- **Epics File**: `docs/epics.md` (lines 685-719: Story 3.2 requirements)
- **Architecture**: `docs/ARCHITECTURE.md` (LangGraph agents, structured output)
- **Story 2.3**: Eliza agent with LangGraph (extends this agent)
- **Story 2.2**: Memory service (integrates for personalization)
- **Story 3.1**: Goal models (decomposition links to goals)

**Technical Documentation:**
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LangChain Structured Output**: https://python.langchain.com/docs/modules/model_io/output_parsers/
- **Pydantic**: https://docs.pydantic.dev/latest/

---

## Definition of Done

- [ ] ✅ `goal_decompositions` table created via Alembic migration
- [ ] ✅ `GoalDecomposition` model and Pydantic schemas created
- [ ] ✅ Eliza agent extended with `goal_decomposition` node
- [ ] ✅ Decomposition conversation works across all phases (explore, constrain, propose, generate, refine)
- [ ] ✅ Structured output parsing implemented with error handling
- [ ] ✅ Memory integration working (Eliza queries personal/project memories)
- [ ] ✅ `GoalDecompositionService` created with save/retrieve/update methods
- [ ] ✅ Frontend modal/page for goal planning completed
- [ ] ✅ Approve/modify/reject flow working
- [ ] ✅ Approved decompositions saved to database with correct JSONB structure
- [ ] ✅ Unit tests created with 80%+ coverage
- [ ] ✅ Integration tests validate full conversation flow
- [ ] ✅ Manual testing completed for both abstract and concrete goals
- [ ] ✅ All acceptance criteria verified
- [ ] ✅ Documentation and examples added
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Implement tasks 1-10, test with real goals, validate memory integration
