# Story 4.2: Build Narrative Generation Agent with LangGraph

**Story ID:** 4.2
**Epic:** 4 - Narrative Engine
**Status:** drafted
**Priority:** P0 (Core Narrative Generation)
**Estimated Effort:** 12-16 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18

---

## User Story

**As a** developer,
**I want** an AI agent that generates personalized story beats using LangGraph,
**So that** users experience adaptive narratives tied to their real actions.

---

## Context

### Problem Statement

The Narrative Engine requires intelligent story generation that adapts to user progress while maintaining strict consistency. This story creates the core AI agent that:

1. **Analyzes user progress** (missions, streaks, value focus) to inform narrative direction
2. **Selects appropriate story beats** based on chapter progression and user context
3. **Generates high-quality narrative content** using OpenAI GPT-4o
4. **Validates story consistency** against scenario template world schema
5. **Updates world state** with new events, discoveries, and relationship changes

**Critical Requirement:** Story consistency is paramount. The agent must NEVER reference items users haven't acquired, locations they haven't discovered, or knowledge characters don't possess. Validation failures trigger regeneration with stricter constraints.

### Why This Approach?

**From Architecture (ADR-009: GPT-4o for Narrative, lines 1170-1211):**

We use GPT-4o (not GPT-4o-mini) for narrative generation because:

- ✅ **Superior Writing Quality**: Narrative requires premium storytelling, not just functional text
- ✅ **Story Consistency**: Better at following complex consistency rules
- ✅ **Emotional Resonance**: Creates more engaging, immersive story beats
- ✅ **Cost-Effective at Low Frequency**: ~2-3 beats/week/user = ~$0.02/user/day (within budget)

**From Tech Spec (tech-spec-epic-4.md lines 182-362):**

The LangGraph agent implements a stateful story generation pipeline:

- **assess_progress** → Analyze user achievements
- **select_beat** → Choose narrative arc template
- **generate_content** → GPT-4o creates personalized story
- **validate_consistency** → Check against world state
- **check_unlocks** → Determine hidden quest triggers
- **update_state** → Save beat and world state changes

**Why LangGraph?**

From `architecture.md` ADR-003 (lines 991-1010):

- Stateful agent orchestration perfect for narrative flows
- Visual debugging in LangGraph Studio
- Built-in streaming support for future real-time generation
- Structured state management prevents inconsistencies

### Dependencies

- **Prerequisite Stories:**
  - 4.1 (Narrative State Schema) ✅ Must be complete
  - 2.1 (PostgreSQL setup) ✅ Complete
  - Database with scenario_templates and narrative_states tables

- **Epic 4 Context:** This story **enables**:
  - Story 4.3: Hidden quest unlocking (uses check_unlocks node)
  - Story 4.4: Story viewing UI (displays generated beats)
  - Story 4.6: Branching narratives (uses decision tracking)

- **External Dependencies:**
  - OpenAI API access (`OPENAI_API_KEY`)
  - LangGraph and LangChain installed (`poetry add langgraph`)

### Technical Background from Epic 4 Design Documents

**From Tech Spec (lines 182-362):**

Complete agent architecture with:

- LangGraph state machine with 6 nodes
- GPT-4o prompt engineering for story beats
- Consistency validation rules
- World state update logic

**From Epics (epics.md lines 1000-1041):**

Requirements specify:

- Uses scenario template context
- Incorporates real user data (goals, missions, streaks)
- Generates 200-400 word story beats
- Includes emotional tone and character dialogue
- Optional quest unlock capability

---

## Acceptance Criteria

### AC1: Narrative Agent Created with LangGraph State Machine

**Given** LangGraph is installed
**When** I initialize the narrative agent
**Then** a LangGraph StateGraph exists with nodes:

- `assess_progress` (Input Node)
- `select_beat` (Decision Node)
- `generate_content` (LLM Node)
- `validate_consistency` (Validation Node)
- `check_unlocks` (Unlock Detection Node)
- `update_state` (Output Node)

**And** edges connect nodes in logical flow:

```
assess_progress → select_beat → generate_content → validate_consistency
                                                    ↓
                                            (if valid) → check_unlocks → update_state
                                                    ↓
                                        (if invalid) → generate_content (retry)
```

**And** agent state schema is defined with TypedDict

**Verification:**

```python
from app.agents.narrative_agent import create_narrative_agent

agent = create_narrative_agent()
assert "assess_progress" in agent.nodes
assert "generate_content" in agent.nodes
assert "validate_consistency" in agent.nodes
```

### AC2: Assess Progress Node Analyzes User Achievements

**Given** the narrative agent is initialized
**When** I invoke `assess_progress` node with user_id
**Then** the node queries and summarizes:

- Last 30 days of mission completions
- Current streak (overall and per-attribute: health, craft, growth, connection)
- Value focus distribution (percentage breakdown)
- Recent goal achievements or milestones

**And** outputs `user_progress_summary` dict with:

```python
{
    "missions_completed_30d": 45,
    "current_streak_days": 12,
    "streak_attribute": "craft",
    "value_distribution": {"health": 0.2, "craft": 0.5, "growth": 0.2, "connection": 0.1},
    "recent_achievements": ["20_day_streak_craft", "50_missions_completed"],
    "dominant_value": "craft"
}
```

**Verification:**

```python
state = {"user_id": "test-user", "scenario_id": "test-scenario"}
result = await assess_progress_node(state)
assert "missions_completed_30d" in result["user_progress_summary"]
assert "current_streak_days" in result["user_progress_summary"]
```

### AC3: Select Beat Node Chooses Appropriate Narrative Arc

**Given** user progress summary and current narrative state exist
**When** I invoke `select_beat` node
**Then** the node determines:

- If chapter progression trigger is met (advance chapter if yes)
- If act transition trigger is met (advance act if yes)
- Beat type: `progression`, `character_moment`, `hidden_quest_unlock`, or `milestone`
- Appropriate beat template from scenario.narrative_arc

**And** outputs:

```python
{
    "selected_beat_template": {...},
    "beat_type": "progression",
    "chapter_advanced": False,
    "act_advanced": False
}
```

**Verification:**

```python
# Test chapter progression
state = {
    "user_progress_summary": {"missions_completed_30d": 50},
    "current_narrative_state": {"current_chapter": 1},
    "scenario_template": {...}  # Contains progression triggers
}
result = await select_beat_node(state)
assert result["beat_type"] in ["progression", "character_moment", "hidden_quest_unlock", "milestone"]
```

### AC4: Generate Content Node Creates Story Beat with GPT-4o

**Given** beat template and user context are selected
**When** I invoke `generate_content` node
**Then** the node:

- Constructs GPT-4o prompt with:
  - Scenario theme and current chapter
  - User progress summary (achievements, streaks)
  - Current world state (locations discovered, characters met, relationships)
  - Beat template guidance
  - CRITICAL consistency rules
- Calls OpenAI GPT-4o API (model: `gpt-4o`, max_tokens: 800, temperature: 0.7)
- Parses JSON response into structured beat

**And** generated beat includes:

```python
{
    "title": "Lyra's Challenge",
    "text": "As you enter the Arena, Lyra awaits with a knowing smile...",  # 200-400 words
    "word_count": 287,
    "emotional_tone": "inspiring",
    "characters_involved": ["Lyra"],
    "world_state_changes": {
        "events_added": ["lyra_challenge_issued"],
        "relationship_changes": {"Lyra": 1},
        "items_added": [],
        "locations_discovered": []
    }
}
```

**And** LLM call is logged with token usage

**Verification:**

```python
state = {
    "selected_beat_template": {...},
    "user_progress_summary": {...},
    "current_world_state": {...},
    "scenario_template": {...}
}
result = await generate_content_node(state)
assert "generated_beat" in result
assert 200 <= result["generated_beat"]["word_count"] <= 400
assert result["generated_beat"]["emotional_tone"] in ["inspiring", "challenging", "reflective", "triumphant", "somber"]
```

### AC5: Validate Consistency Node Enforces Story Rules

**Given** a story beat is generated
**When** I invoke `validate_consistency` node
**Then** the node checks:

- All referenced items exist in world_state.items
- All referenced locations exist in world_state.locations (discovered=true)
- All referenced events exist in world_state.events
- Character knowledge is consistent (world_state.persons[character].knows_about)
- Relationship level changes are logical (max +1 per beat)

**And** returns validation result:

```python
{
    "validation_passed": True,  # or False
    "consistency_errors": []     # List of error messages if failed
}
```

**And** if validation fails, agent retries generate_content with stricter constraints (max 3 retries)

**Verification:**

```python
# Test invalid beat (references non-existent item)
state = {
    "generated_beat": {
        "text": "Lyra hands you the ancient medallion...",
        "world_state_changes": {"items_added": ["medallion_of_craft"]}
    },
    "current_world_state": {
        "items": {"artifacts": []}  # Medallion not acquired
    },
    "scenario_world_schema": {...}
}
result = await validate_consistency_node(state)
# Should fail if medallion is referenced but not in scenario or already acquired
```

### AC6: Check Unlocks Node Detects Hidden Quest Triggers

**Given** user progress summary is available
**When** I invoke `check_unlocks` node
**Then** the node:

- Iterates through scenario_template.hidden_quests
- Evaluates trigger conditions (e.g., `{"streak_days": 20, "attribute": "craft"}`)
- Filters out already unlocked quests (narrative_state.unlocked_quests)
- Identifies quests to unlock

**And** outputs:

```python
{
    "quests_to_unlock": ["relentless_achievement"],  # Quest IDs
    "unlock_notifications": [
        {
            "quest_id": "relentless_achievement",
            "title": "The Relentless",
            "narrative_context": "Your unwavering dedication to craft has awakened something ancient..."
        }
    ]
}
```

**Verification:**

```python
state = {
    "user_progress_summary": {"current_streak_days": 20, "streak_attribute": "craft"},
    "scenario_template": {
        "hidden_quests": [
            {"id": "relentless_achievement", "trigger": {"streak_days": 20, "attribute": "craft"}}
        ]
    },
    "current_unlocked_quests": []
}
result = await check_unlocks_node(state)
assert "relentless_achievement" in result["quests_to_unlock"]
```

### AC7: Update State Node Saves Beat and World State

**Given** beat is generated and validated
**When** I invoke `update_state` node
**Then** the node:

- Saves story beat to database (new row in `story_beats` table - create if needed)
- Updates `narrative_states.world_state` with changes:
  - Appends new events to world_state.events
  - Updates relationship levels in world_state.persons
  - Adds new items to world_state.items.artifacts
  - Marks new locations as discovered
- Updates `narrative_states.current_chapter` and `current_act` if advanced
- Adds unlocked quests to `narrative_states.unlocked_quests` array
- Creates notification for user

**And** returns:

```python
{
    "beat_id": "uuid",
    "updated_narrative_state": {...}
}
```

**Verification:**

```python
state = {
    "generated_beat": {...},
    "quests_to_unlock": ["relentless_achievement"],
    "world_state_changes": {"events_added": [...], "relationship_changes": {...}}
}
result = await update_state_node(state)
assert result["beat_id"] is not None

# Verify database updated
narrative_state = await db.get(NarrativeState, ...)
assert "relentless_achievement" in narrative_state.unlocked_quests
```

### AC8: Narrative Service Orchestrates Agent Execution

**Given** the narrative agent exists
**When** I call `narrative_service.generate_story_beat(user_id, trigger_type)`
**Then** the service:

- Loads scenario template for user
- Loads current narrative state
- Invokes LangGraph agent with initial state
- Awaits agent completion
- Returns generated beat ID and metadata

**And** handles errors gracefully:

- LLM API failures: Retry with exponential backoff
- Validation failures: Regenerate up to 3 times
- Database errors: Log and raise HTTPException

**Verification:**

```python
from app.services.narrative_service import NarrativeService

async with get_db() as db:
    service = NarrativeService(db)
    result = await service.generate_story_beat(
        user_id="test-user",
        trigger_type="milestone"
    )
    assert result["beat_id"] is not None
    assert result["world_state_updated"] is True
```

### AC9: Cost Per Beat Generation Meets Budget Target

**Given** the narrative agent is implemented
**When** I generate 100 story beats (test scenario)
**Then** the average cost per beat is:

- GPT-4o API cost: ~$0.02-0.05 per beat
  - Input tokens: ~800 tokens (context) × $2.50/1M = $0.002
  - Output tokens: ~500 tokens (story) × $10/1M = $0.005
  - Total per beat: ~$0.007

**And** total cost for user receiving 2-3 beats/week:

- Weekly cost: 2.5 beats × $0.007 = ~$0.018
- Daily cost: $0.018 / 7 = ~$0.0026/user/day (well under $0.50 budget)

**And** token usage is logged for monitoring

**Verification:**

```python
# Track token usage in tests
total_tokens = 0
total_cost = 0.0
for i in range(100):
    result = await narrative_service.generate_story_beat(test_user_id, "scheduled")
    total_tokens += result["token_usage"]["total_tokens"]
    total_cost += result["token_usage"]["estimated_cost"]

avg_cost_per_beat = total_cost / 100
assert avg_cost_per_beat < 0.05  # Under 5 cents per beat
```

---

## Tasks / Subtasks

### Task 1: Set Up LangGraph Dependencies (AC: #1)

- [ ] **1.1** Update `pyproject.toml`: Add `langgraph = "^0.1.0"` and `langchain-openai = "^0.1.0"`
- [ ] **1.2** Run `poetry install`
- [ ] **1.3** Verify imports: `from langgraph.graph import StateGraph, END`
- [ ] **1.4** Create `app/agents/__init__.py` if not exists

### Task 2: Define Agent State Schema (AC: #1)

- [ ] **2.1** Create `app/agents/narrative_agent.py`
- [ ] **2.2** Define `NarrativeAgentState` TypedDict:
  - user_id, scenario_id, trigger_type
  - user_progress_summary, selected_beat_template, beat_type
  - generated_beat, validation_passed, consistency_errors
  - quests_to_unlock, world_state_changes
  - beat_id, updated_narrative_state
- [ ] **2.3** Add type hints for all state fields

### Task 3: Implement Assess Progress Node (AC: #2)

- [ ] **3.1** Create `assess_progress` async function
- [ ] **3.2** Query user's missions (last 30 days):
  - Use Mission model (Epic 3 dependency - mock if not available)
  - Count total missions completed
  - Calculate value distribution (health/craft/growth/connection percentages)
- [ ] **3.3** Query user's current streak:
  - Use Progress model or calculate from missions
  - Identify streak attribute (dominant value)
- [ ] **3.4** Identify recent achievements:
  - Check for milestone patterns (20-day streak, 50 missions, etc.)
- [ ] **3.5** Return user_progress_summary dict
- [ ] **3.6** Add error handling and logging

### Task 4: Implement Select Beat Node (AC: #3)

- [ ] **4.1** Create `select_beat` async function
- [ ] **4.2** Load scenario template and current narrative state
- [ ] **4.3** Check chapter progression trigger:
  - Compare user progress to scenario.narrative_arc[act][chapter].progression_trigger
  - Advance chapter if trigger met
- [ ] **4.4** Check act transition trigger:
  - Advance act if last chapter of act completed
- [ ] **4.5** Determine beat type:
  - `progression` if chapter/act advanced
  - `milestone` if significant achievement
  - `character_moment` for relationship building
  - `hidden_quest_unlock` if quest unlocked
- [ ] **4.6** Select appropriate beat template from scenario
- [ ] **4.7** Return selected_beat_template, beat_type, advancement flags

### Task 5: Implement Generate Content Node (AC: #4, #9)

- [ ] **5.1** Create `generate_content` async function
- [ ] **5.2** Construct GPT-4o prompt:
  - System message: "You are a master storyteller..."
  - Scenario context: name, theme, current chapter
  - User context: progress summary, achievements
  - World state context: discovered locations, characters met, relationships
  - Beat template guidance
  - CRITICAL consistency rules (items, locations, character knowledge)
  - JSON response format specification
- [ ] **5.3** Call OpenAI API:
  - Model: `gpt-4o`
  - Max tokens: 800
  - Temperature: 0.7
  - Response format: JSON
- [ ] **5.4** Parse JSON response:
  - Extract title, text, emotional_tone, characters_involved, world_state_changes
  - Calculate word_count
- [ ] **5.5** Log token usage for cost tracking:
  - Input tokens, output tokens, total tokens
  - Estimated cost (using pricing: $2.50/$10 per 1M tokens)
- [ ] **5.6** Return generated_beat
- [ ] **5.7** Add retry logic for API failures (exponential backoff, 3 attempts)

### Task 6: Implement Validate Consistency Node (AC: #5)

- [ ] **6.1** Create `validate_consistency` async function
- [ ] **6.2** Validate item references:
  - Check all items mentioned in beat.text exist in world_state.items or scenario.world_schema.items
  - Verify items in world_state_changes.items_added are valid per schema
- [ ] **6.3** Validate location references:
  - Check all locations mentioned exist in world_state.locations (discovered=true)
  - Verify new locations in world_state_changes.locations_discovered are valid per schema
- [ ] **6.4** Validate event references:
  - Ensure no circular dependencies in events
  - Verify event types match scenario.world_schema.event_types
- [ ] **6.5** Validate character knowledge:
  - Check characters can only reference things in world_state.persons[character].knows_about
- [ ] **6.6** Validate relationship changes:
  - Ensure relationship level changes are ≤ 1 per beat
  - Verify relationship levels stay within 0-10 range
- [ ] **6.7** Return validation_passed (bool) and consistency_errors (list)
- [ ] **6.8** Add detailed error messages for debugging

### Task 7: Implement Check Unlocks Node (AC: #6)

- [ ] **7.1** Create `check_unlocks` async function
- [ ] **7.2** Load scenario.hidden_quests and narrative_state.unlocked_quests
- [ ] **7.3** For each hidden quest:
  - Check if already unlocked (skip if yes)
  - Evaluate trigger condition against user_progress_summary
  - Add to unlock queue if trigger met
- [ ] **7.4** Create unlock notifications for each quest to unlock
- [ ] **7.5** Return quests_to_unlock list and unlock_notifications

### Task 8: Implement Update State Node (AC: #7)

- [ ] **8.1** Create `update_state` async function
- [ ] **8.2** Create StoryBeat model (if not exists):
  - id, user_id, scenario_id, chapter, act, beat_type
  - content JSONB (title, text, emotional_tone, etc.)
  - world_state_changes JSONB
  - metadata JSONB (llm_model, token_usage, etc.)
  - created_at
- [ ] **8.3** Save story beat to database
- [ ] **8.4** Update narrative_state.world_state:
  - Append events to world_state.events
  - Update relationship levels in world_state.persons
  - Add items to world_state.items.artifacts
  - Mark locations as discovered
- [ ] **8.5** Update chapter/act if advanced
- [ ] **8.6** Add unlocked quests to narrative_state.unlocked_quests
- [ ] **8.7** Update narrative_state.updated_at timestamp
- [ ] **8.8** Commit database transaction
- [ ] **8.9** Create user notification (in-app or queue for later)
- [ ] **8.10** Return beat_id and updated_narrative_state

### Task 9: Assemble LangGraph State Machine (AC: #1)

- [ ] **9.1** Create `create_narrative_agent()` function
- [ ] **9.2** Initialize StateGraph with NarrativeAgentState schema
- [ ] **9.3** Add nodes:
  - assess_progress
  - select_beat
  - generate_content
  - validate_consistency
  - check_unlocks
  - update_state
- [ ] **9.4** Add edges:
  - START → assess_progress
  - assess_progress → select_beat
  - select_beat → generate_content
  - generate_content → validate_consistency
  - validate_consistency → check_unlocks (if valid)
  - validate_consistency → generate_content (if invalid, conditional edge with retry count)
  - check_unlocks → update_state
  - update_state → END
- [ ] **9.5** Add conditional edge for validation retry:
  - Max 3 retries, then fail with error
- [ ] **9.6** Compile graph
- [ ] **9.7** Return compiled agent

### Task 10: Create Narrative Service (AC: #8)

- [ ] **10.1** Create `app/services/narrative_service.py`
- [ ] **10.2** Implement `NarrativeService` class:
  - __init__(db: AsyncSession, openai_api_key: str)
- [ ] **10.3** Implement `generate_story_beat()` method:
  - Load scenario template for user
  - Load current narrative state (or create if first beat)
  - Build initial agent state
  - Invoke LangGraph agent
  - Return result with beat_id, world_state_updated, token_usage
- [ ] **10.4** Add error handling:
  - HTTPException for API errors
  - Logging for debugging
  - Retry logic for transient failures
- [ ] **10.5** Add helper methods:
  - `_load_user_scenario()`: Load scenario for user
  - `_load_narrative_state()`: Load or create narrative state
  - `_build_agent_state()`: Construct initial state for agent

### Task 11: Create Unit Tests (AC: All)

- [ ] **11.1** Create `tests/agents/test_narrative_agent.py`
- [ ] **11.2** Test each node independently:
  - assess_progress: Mock mission queries, verify summary
  - select_beat: Test chapter progression logic
  - generate_content: Mock OpenAI API, verify prompt structure
  - validate_consistency: Test validation rules with invalid beats
  - check_unlocks: Test trigger evaluation logic
  - update_state: Test database updates
- [ ] **11.3** Test agent end-to-end with mocked LLM
- [ ] **11.4** Test error handling and retries
- [ ] **11.5** Test token usage logging and cost calculation

### Task 12: Create Integration Tests (AC: #8, #9)

- [ ] **12.1** Create `tests/integration/test_narrative_service.py`
- [ ] **12.2** Test complete story beat generation:
  - Create test user with mission history
  - Create test scenario template (Modern Reality)
  - Generate multiple story beats
  - Verify world state updates correctly
  - Verify chapter progression
- [ ] **12.3** Test hidden quest unlocking
- [ ] **12.4** Test consistency validation with real GPT-4o
- [ ] **12.5** Measure token usage and cost (AC9)
- [ ] **12.6** Test error scenarios (API failures, invalid scenarios)

### Task 13: Create API Endpoints (AC: #8)

- [ ] **13.1** Create `app/api/v1/narrative.py`
- [ ] **13.2** Implement `POST /api/v1/narrative/generate-beat`:
  - Request: user_id, trigger_type, context (optional)
  - Response: beat_id, content preview, world_state_updated, quests_unlocked
- [ ] **13.3** Implement `GET /api/v1/narrative/story`:
  - Returns user's complete narrative history (beats, world state, etc.)
- [ ] **13.4** Add authentication middleware (Clerk session validation)
- [ ] **13.5** Add rate limiting (prevent abuse of expensive GPT-4o calls)
- [ ] **13.6** Add Pydantic request/response schemas

### Task 14: Documentation (AC: All)

- [ ] **14.1** Document LangGraph agent architecture in code
- [ ] **14.2** Document consistency validation rules
- [ ] **14.3** Document GPT-4o prompt engineering strategy
- [ ] **14.4** Create `docs/epic-4/NARRATIVE-AGENT-GUIDE.md`:
  - How agent works
  - How to test agent
  - How to debug validation failures
  - How to monitor costs
- [ ] **14.5** Update API documentation with narrative endpoints
- [ ] **14.6** Add docstrings to all functions

---

## Dev Notes

### LangGraph Agent Architecture

**From Tech Spec (tech-spec-epic-4.md lines 182-362):**

The agent implements a multi-stage pipeline ensuring quality and consistency:

1. **Data Collection** (assess_progress): Gather real user data
2. **Decision Making** (select_beat): Determine story direction
3. **Content Creation** (generate_content): GPT-4o writes story
4. **Quality Control** (validate_consistency): Enforce rules
5. **Reward Detection** (check_unlocks): Identify hidden quests
6. **State Persistence** (update_state): Save everything

**Critical Design Pattern:**

The validation → generation feedback loop ensures consistency. If GPT-4o generates inconsistent content, we regenerate with stricter constraints rather than accepting flawed stories.

```python
# Conditional edge for retry
def should_retry(state):
    if not state["validation_passed"]:
        if state.get("retry_count", 0) < 3:
            state["retry_count"] = state.get("retry_count", 0) + 1
            return "generate_content"  # Retry
        else:
            raise ValueError("Max retries exceeded - consistency validation failed")
    return "check_unlocks"  # Continue
```

### GPT-4o Prompt Engineering

**Prompt Structure for Story Generation:**

```python
system_prompt = """You are a master storyteller creating a personalized narrative beat for a self-improvement companion app.

CRITICAL RULES FOR STORY CONSISTENCY:
1. NEVER reference items the user hasn't acquired. Available items: {available_items}
2. NEVER reference locations the user hasn't discovered. Discovered locations: {discovered_locations}
3. Characters can only know what they've learned. {character_name} knows: {character_knowledge}
4. Relationship levels change gradually (max +1 per beat).

You are creating a {beat_type} beat for Chapter {chapter} of a {scenario_theme} story.

USER CONTEXT:
- Recent missions: {missions_summary}
- Current streak: {streak_days} days (focus: {streak_attribute})
- Dominant value: {dominant_value}
- Recent achievements: {achievements}

WORLD STATE:
- Locations discovered: {locations}
- Characters met: {characters}
- Relationship with {primary_character}: Level {relationship_level}
- Recent events: {last_5_events}

BEAT TEMPLATE GUIDANCE:
{beat_template_text}

Generate a story beat (200-400 words) that:
1. Reflects the user's REAL progress (mention their {dominant_value} focus or {streak_days}-day streak naturally)
2. Maintains STRICT consistency (follow the critical rules above)
3. Advances the narrative arc toward Chapter {next_chapter}
4. Creates emotional resonance (tone: {target_emotional_tone})
5. Sets up future story possibilities

Return JSON format:
{
  "title": "Beat title (3-7 words)",
  "text": "Story beat text (200-400 words)",
  "emotional_tone": "inspiring|challenging|reflective|triumphant|somber",
  "characters_involved": ["CharacterName"],
  "world_state_changes": {
    "events_added": [{"event_id": "...", "event_type": "...", "impact": {...}}],
    "relationship_changes": {"CharacterName": 1},  // Max +1 or -1
    "items_added": [],  // Only if beat explicitly gives item
    "locations_discovered": []  // Only if beat explicitly mentions discovering new location
  }
}
"""
```

**Cost Optimization:**

- Use `max_tokens: 800` to cap costs while allowing 200-400 word stories
- Use `temperature: 0.7` for creative but consistent output
- Cache scenario templates and character prompts in prompt to reduce input tokens

### Consistency Validation Rules

**From Epics (epics.md line 990):**

**Rule 1: Item References**

```python
def validate_item_references(beat_text, world_state, scenario_schema):
    """Ensure no items referenced unless acquired or defined in schema."""
    all_valid_items = set(scenario_schema["items"].keys())
    acquired_items = {item["id"] for item in world_state["items"]["artifacts"]}

    # Extract item mentions from beat text (simple keyword matching)
    mentioned_items = extract_item_mentions(beat_text)

    for item in mentioned_items:
        if item not in all_valid_items:
            return False, f"Invalid item referenced: {item} (not in scenario schema)"
        if item not in acquired_items and item not in ["essence", "titles"]:  # Currency/titles always available
            return False, f"Item referenced before acquisition: {item}"

    return True, None
```

**Rule 2: Location References**

```python
def validate_location_references(beat_text, world_state, scenario_schema):
    """Ensure no locations referenced unless discovered."""
    discovered_locations = {
        loc_key for loc_key, loc_data in world_state["locations"].items()
        if loc_data.get("discovered", False)
    }

    mentioned_locations = extract_location_mentions(beat_text)

    for location in mentioned_locations:
        if location not in scenario_schema["locations"]:
            return False, f"Invalid location: {location} (not in scenario schema)"
        if location not in discovered_locations:
            return False, f"Location referenced before discovery: {location}"

    return True, None
```

**Rule 3: Character Knowledge**

```python
def validate_character_knowledge(beat_text, characters_involved, world_state):
    """Ensure characters only reference things they know."""
    for character in characters_involved:
        character_data = world_state["persons"].get(character, {})
        knows_about = set(character_data.get("knows_about", []))

        # Extract what character discusses in beat
        character_references = extract_character_dialogue(beat_text, character)

        for reference in character_references:
            if reference not in knows_about:
                return False, f"{character} references {reference} but shouldn't know about it yet"

    return True, None
```

**Rule 4: Relationship Progression**

```python
def validate_relationship_changes(world_state_changes, current_world_state):
    """Ensure relationship levels change gradually."""
    for character, change in world_state_changes.get("relationship_changes", {}).items():
        if abs(change) > 1:
            return False, f"Relationship change too large for {character}: {change} (max ±1)"

        current_level = current_world_state["persons"].get(character, {}).get("relationship_level", 0)
        new_level = current_level + change

        if new_level < 0 or new_level > 10:
            return False, f"Relationship level out of range for {character}: {new_level}"

    return True, None
```

### Cost Tracking and Monitoring

**From AC9:**

Token usage must be logged for every generation:

```python
# In generate_content node
response = await openai_client.chat.completions.create(...)

token_usage = {
    "input_tokens": response.usage.prompt_tokens,
    "output_tokens": response.usage.completion_tokens,
    "total_tokens": response.usage.total_tokens,
    "estimated_cost": (
        response.usage.prompt_tokens * 0.0000025 +  # $2.50 per 1M input tokens
        response.usage.completion_tokens * 0.00001   # $10 per 1M output tokens
    )
}

# Log for monitoring
logger.info(f"GPT-4o generation complete", extra={
    "user_id": state["user_id"],
    "beat_type": state["beat_type"],
    "token_usage": token_usage
})

# Store in beat metadata
state["generated_beat"]["metadata"] = {
    "llm_model": "gpt-4o",
    "token_usage": token_usage,
    "generation_time": time.time() - start_time
}
```

**Monitoring Alerts:**

- Alert if cost per beat > $0.10 (indicates prompt bloat)
- Alert if validation failure rate > 20% (indicates consistency issues)
- Alert if generation time > 30 seconds (indicates API issues)

### Learnings from Previous Stories

**From Story 2.3 (Eliza Agent - assumed complete for Epic 2):**

- LangGraph agents benefit from clear state schemas
- Async patterns throughout (all nodes are async functions)
- Error handling at node level and graph level
- Streaming support can be added later (not needed for narrative beats)

**From Story 4.1 (Narrative Schema):**

- world_state JSONB structure is comprehensive
- scenario_templates define all possible narrative elements
- Consistency rules are documented
- Seed data provides Modern Reality scenario

### Project Structure Notes

**New Files Created:**

```
packages/backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── narrative_agent.py              # NEW: LangGraph agent
│   ├── services/
│   │   └── narrative_service.py            # NEW: Orchestration service
│   ├── models/
│   │   └── narrative.py                    # UPDATE: Add StoryBeat model
│   ├── schemas/
│   │   └── narrative.py                    # UPDATE: Add beat schemas
│   └── api/v1/
│       └── narrative.py                     # NEW: Narrative endpoints
└── tests/
    ├── agents/
    │   └── test_narrative_agent.py         # NEW: Agent unit tests
    └── integration/
        └── test_narrative_service.py       # NEW: Service integration tests
```

**Documentation Created:**

```
docs/
└── epic-4/
    └── NARRATIVE-AGENT-GUIDE.md            # NEW: Agent architecture guide
```

### Relationship to Epic 4 Stories

This story (4.2) **enables**:

- **Story 4.3 (Hidden Quests)**: Uses check_unlocks node output
- **Story 4.4 (Story UI)**: Displays generated story beats
- **Story 4.6 (Branching Narratives)**: Extends generate_content with decision prompts

**Dependencies Flow:**

```
Story 4.1 (Narrative Schema)
    ↓ (provides templates and state)
Story 4.2 (Narrative Agent) ← THIS STORY
    ↓ (generates beats)
Story 4.3 (Hidden Quests)
    ↓ (unlocks surprises)
Story 4.4 (Story UI)
    = Living Narrative Experience! 📖
```

### References

**Source Documents:**

- **Epic 4 Tech Spec**: `docs/tech-spec-epic-4.md` (Agent architecture, lines 182-362)
- **Epics File**: `docs/epics.md` (Story 4.2 requirements, lines 1000-1041)
- **Architecture**: `docs/ARCHITECTURE.md` (ADR-003 LangGraph, lines 991-1010)
- **Architecture**: `docs/ARCHITECTURE.md` (ADR-009 GPT-4o, lines 1170-1211)

**Technical Documentation:**

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **OpenAI GPT-4o**: https://platform.openai.com/docs/models/gpt-4o
- **LangChain**: https://python.langchain.com/docs/get_started/introduction

---

## Definition of Done

- [ ] ✅ LangGraph agent created with 6 nodes (assess, select, generate, validate, check_unlocks, update)
- [ ] ✅ All nodes implemented and tested independently
- [ ] ✅ Agent state schema defined with TypedDict
- [ ] ✅ GPT-4o integration working with proper prompts
- [ ] ✅ Consistency validation enforces all rules
- [ ] ✅ Hidden quest detection functional
- [ ] ✅ World state updates correctly
- [ ] ✅ StoryBeat model created and migrations run
- [ ] ✅ NarrativeService orchestrates agent execution
- [ ] ✅ API endpoints created for story generation
- [ ] ✅ Token usage logged and cost meets budget (<$0.05/beat)
- [ ] ✅ Unit tests pass (all nodes, error handling)
- [ ] ✅ Integration tests pass (end-to-end generation, consistency)
- [ ] ✅ Documentation complete (agent guide, API docs)
- [ ] ✅ No secrets committed
- [ ] ✅ Code follows async patterns
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline

- **Task 1-2** (Setup and State Schema): 1 hour
- **Task 3** (Assess Progress): 1.5 hours
- **Task 4** (Select Beat): 1.5 hours
- **Task 5** (Generate Content + Cost Tracking): 3 hours
- **Task 6** (Validate Consistency): 2.5 hours
- **Task 7** (Check Unlocks): 1 hour
- **Task 8** (Update State): 2 hours
- **Task 9** (Assemble Agent): 1 hour
- **Task 10** (Narrative Service): 1.5 hours
- **Task 11** (Unit Tests): 2 hours
- **Task 12** (Integration Tests): 2 hours
- **Task 13** (API Endpoints): 1.5 hours
- **Task 14** (Documentation): 1.5 hours

**Total:** 22 hours (higher than estimate due to complexity - adjust to 18 hours with efficient execution)

### Risk Mitigation

**Risk:** GPT-4o generates inconsistent content frequently (>20% failure rate)

- **Mitigation**: Comprehensive prompts with explicit examples, stricter validation, retry with added constraints
- **Impact**: High (degrades user experience, increases costs due to retries)

**Risk:** Token costs exceed budget ($0.05/beat target)

- **Mitigation**: Monitor token usage, optimize prompts, cache scenario context, set max_tokens limit
- **Impact**: Medium (can optimize prompts to reduce costs)

**Risk:** Generation time too slow (>10 seconds)

- **Mitigation**: Async processing, background generation, cache frequently accessed data
- **Impact**: Low (narrative beats not real-time, async acceptable)

**Risk:** LangGraph agent crashes or hangs

- **Mitigation**: Comprehensive error handling, timeout limits, dead letter queue for failed generations
- **Impact**: Medium (retry mechanism mitigates)

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Create context file, then implement LangGraph agent with comprehensive testing
