# Epic Technical Specification: Narrative Engine

Date: 2025-11-18
Author: Jack
Epic ID: 4
Status: Draft

---

## Overview

Epic 4 implements the Narrative Engine, a living storytelling system that generates personalized narratives adapting to real-world user progress. This epic creates a fundamentally different narrative experience where story progression is driven by actual achievements, not scripted sequences. The system combines AI-generated story beats, pre-planned hidden quests with trigger conditions, and comprehensive world state tracking to maintain consistency across locations, events, characters, and items.

The narrative engine enables Delight to transform productivity tracking into an emotionally resonant journey where users see their efforts building toward something meaningful. By combining OpenAI GPT-4o's superior narrative writing quality with LangGraph's stateful orchestration and PostgreSQL JSONB's flexible world state management, we create a scalable foundation for multiple narrative themes (Modern Reality, Medieval Fantasy, Sci-Fi, etc.) while maintaining strict story consistency.

## Objectives and Scope

### In Scope

1. **Comprehensive narrative state schema** (Story 4.1):
   - `scenario_templates` table with JSONB for narrative arcs, character prompts, hidden quests, time rules, world schema
   - `narrative_states` table with JSONB for comprehensive world state (locations, events, persons, items)
   - World state tracking for all narrative elements to enforce story consistency
   - Seed data for at least one complete scenario template (Modern Reality with 3 acts)

2. **Narrative generation agent with LangGraph** (Story 4.2):
   - LangGraph state machine with nodes: assess_progress, select_beat, generate_content, check_unlocks
   - Integration with user mission history, streaks, value focus
   - OpenAI GPT-4o for premium narrative writing quality (~2-3 beats per week per user)
   - Story consistency validation against scenario template rules

3. **Pre-planned hidden quest system** (Story 4.3):
   - Hidden quests with trigger conditions (e.g., 20-day streak, 50 missions completed)
   - ARQ worker for nightly trigger condition checking
   - Quest unlock notifications via in-app alerts and Eliza messages
   - Integration with mission system for "Special" quest treatment

4. **Story viewing interface (MVP)** (Story 4.4):
   - Beautiful book-like UI with serif typography and theme-appropriate styling
   - Chapter navigation and act progression indicators
   - Story beat display (newest first) with fade-in animations
   - API for fetching user's complete narrative history

5. **Character-initiated story events (Future)** (Story 4.5):
   - System for narrative characters to proactively contact users
   - Integration with nudge system infrastructure (Epic 7 dependency)
   - Strategic timing based on optimal engagement times

6. **Branching narratives based on user choices (Future)** (Story 4.6):
   - Decision point system within story beats
   - Choice tracking in narrative state
   - Consequence propagation to future story generation

7. **Lore economy and unlockable content (Future)** (Story 4.7):
   - Essence currency system for unlocking lore
   - Codex interface for character backstories and world history
   - Achievement-based unlocking mechanism

### Out of Scope (Deferred to Later)

- **Multiple scenario templates beyond Modern Reality** (post-MVP expansion)
- **User-created narrative scenarios** (advanced feature, requires moderation)
- **AI-generated visual assets** for story beats (requires image generation integration)
- **Audio narration** for story content (requires text-to-speech integration)
- **Multiple endings system** (mentioned in epics.md but deferred)
- **Community story sharing** (requires moderation and social features)

## System Architecture Alignment

This epic implements Pattern 1 (Living Narrative Engine) from `architecture.md`:

### Technology Stack Decisions

- **Narrative Service**: `backend/app/services/narrative_service.py` - Business logic for story generation
- **Narrative Agent**: `backend/app/agents/narrative_agent.py` - LangGraph state machine
- **Database**: PostgreSQL with JSONB for flexible world state (no schema migrations for new scenarios)
- **LLM**: OpenAI GPT-4o for narrative generation (premium quality, $2.50/$10 per 1M tokens)
- **Background Jobs**: ARQ workers for hidden quest unlocking
- **Frontend**: Next.js pages under `/narrative` route with Framer Motion animations

### Infrastructure Constraints

- **Cost target**: ~$0.02/user/day for narrative generation (within overall $0.50 target)
  - GPT-4o used sparingly: ~2-3 story beats per week per user
  - ~2K tokens per beat × $10/1M output tokens = $0.02
  - Significantly less frequent than chat interactions (GPT-4o-mini)
- **Story consistency priority**: Most critical requirement - no inconsistent values, items, or events
- **Performance**: Story generation can be async (not real-time requirement)
- **Storage**: JSONB world state scales to thousands of tracked elements per user

### Narrative Architecture Components

**Pattern 1: Living Narrative Engine (from architecture.md lines 300-401)**

```
┌─────────────────────────────────────────────────────────┐
│ Narrative Service (LangGraph Agent)                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Story State Machine:                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Chapter 1│───▶│ Chapter 2│───▶│ Chapter 3│          │
│  └──────────┘    └──────────┘    └──────────┘          │
│       │                │                │                │
│       ▼                ▼                ▼                │
│  ┌──────────────────────────────────────────┐           │
│  │ Pre-Planned Hidden Quests (3-5 per story)│           │
│  │ - Trigger conditions (e.g., 20 missions) │           │
│  │ - Narrative content (pre-generated)      │           │
│  │ - Rewards (Essence, relationships, zones)│           │
│  └──────────────────────────────────────────┘           │
│                                                           │
│  Components:                                              │
│  - Narrative Agent (LangGraph): Generates story beats    │
│  - Story State DB (PostgreSQL): Tracks chapter, quests   │
│  - Trigger Monitor (ARQ): Checks conditions, unlocks     │
│  - Template System: Scenario-specific narrative vars     │
└─────────────────────────────────────────────────────────┘
```

## Detailed Design

### Services and Modules

| Service/Module | Responsibility | Inputs | Outputs | Owner/Location |
|---|---|---|---|---|
| **Narrative Service** | Orchestrates story generation, manages narrative state | User progress data, scenario template | Story beats, state updates | `backend/app/services/narrative_service.py` |
| **Narrative Agent (LangGraph)** | Stateful story generation with consistency validation | User context, current narrative state, scenario template | Generated story beat with metadata | `backend/app/agents/narrative_agent.py` |
| **Quest Generator Worker** | Monitors trigger conditions, unlocks hidden quests | User progress metrics, hidden quest templates | Quest unlock events | `backend/app/workers/quest_generator.py` |
| **Scenario Template Service** | Loads and validates scenario templates | Scenario ID or theme | Complete scenario configuration | `backend/app/services/scenario_service.py` |
| **Story API** | REST endpoints for story retrieval and updates | HTTP requests | JSON responses | `backend/app/api/v1/narrative.py` |
| **Story UI Components** | Beautiful story viewing interface | Story beats, chapter data | Rendered story experience | `frontend/src/app/narrative/` |

### Data Models and Contracts

#### Scenario Template Schema (PostgreSQL)

From `architecture.md` lines 351-401:

```sql
CREATE TABLE scenario_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  theme VARCHAR(50) NOT NULL,  -- 'modern', 'medieval', 'scifi', etc.
  narrative_arc JSONB NOT NULL,  -- Chapter structure, story beats, act progression
  character_prompts JSONB NOT NULL,  -- Personality definitions for each character
  hidden_quests JSONB NOT NULL,  -- Pre-planned surprises with trigger conditions
  time_rules JSONB,  -- Zone availability by time (optional overrides)
  world_schema JSONB NOT NULL,  -- Defines all possible locations, persons, items, events
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scenario_theme ON scenario_templates(theme);
```

**Narrative Arc Structure Example:**

```json
{
  "narrative_arc": {
    "act_1": {
      "title": "Awakening",
      "chapters": [
        {
          "number": 1,
          "title": "First Steps",
          "progression_trigger": {"missions_completed": 5}
        },
        {
          "number": 2,
          "title": "The Path Reveals Itself",
          "progression_trigger": {"missions_completed": 15, "streak_days": 7}
        }
      ]
    },
    "act_2": {
      "title": "Rising Challenge",
      "chapters": [
        {
          "number": 3,
          "title": "Facing Obstacles",
          "progression_trigger": {"missions_completed": 30}
        }
      ]
    },
    "act_3": {
      "title": "Transformation",
      "chapters": [
        {
          "number": 4,
          "title": "Mastery",
          "progression_trigger": {"missions_completed": 50, "streak_days": 20}
        }
      ]
    }
  }
}
```

**Hidden Quests Structure:**

```json
{
  "hidden_quests": [
    {
      "id": "relentless_achievement",
      "trigger": {"streak_days": 20, "attribute": "craft"},
      "title": "The Relentless",
      "narrative_context": "Your unwavering dedication to craft has awakened something ancient...",
      "rewards": {
        "essence": 500,
        "title": "The Relentless",
        "relationship_boost": {"Lyra": 2}
      },
      "time_limit_hours": null,
      "narrative_significance": "Unlocks deeper Lyra dialogue"
    },
    {
      "id": "century_milestone",
      "trigger": {"missions_completed": 100},
      "title": "The Hundred Steps",
      "narrative_context": "A century of actions completed. The world takes notice.",
      "rewards": {
        "essence": 1000,
        "artifact": {
          "id": "medallion_of_persistence",
          "description": "A shimmering medallion that grows warmer with each completed mission"
        }
      },
      "time_limit_hours": 72,
      "narrative_significance": "Major story milestone, triggers Act 2 transition"
    }
  ]
}
```

**World Schema Structure (Defines All Possible Narrative Elements):**

```json
{
  "world_schema": {
    "locations": {
      "arena": {
        "name": "The Arena",
        "description": "A vast open space where craft and health converge",
        "default_availability": true,
        "unlock_condition": null,
        "possible_npcs": ["Lyra", "Thorne"]
      },
      "observatory": {
        "name": "The Observatory",
        "description": "A contemplative space high above, where growth takes root",
        "default_availability": false,
        "unlock_condition": {"chapter_reached": 2},
        "possible_npcs": ["Elara"]
      }
    },
    "persons": {
      "Lyra": {
        "full_name": "Lyra, Master of Craft",
        "role": "Craft mentor",
        "personality_traits": ["artistic", "poetic", "patient"],
        "relationship_levels": {
          "0": "Unknown",
          "1-2": "Acquaintance",
          "3-5": "Ally",
          "6-8": "Trusted Friend",
          "9-10": "Soul Companion"
        }
      },
      "Thorne": {
        "full_name": "Thorne, Guardian of Vitality",
        "role": "Health mentor",
        "personality_traits": ["direct", "practical", "challenging"],
        "relationship_levels": {
          "0": "Unknown",
          "1-2": "Sparring Partner",
          "3-5": "Comrade",
          "6-8": "Trusted Ally",
          "9-10": "Battle-Forged Bond"
        }
      }
    },
    "items": {
      "essence": {
        "type": "currency",
        "description": "The crystallized form of effort and achievement",
        "max_balance": null
      },
      "titles": {
        "type": "collection",
        "examples": ["The Persistent", "The Relentless", "Master of Craft"],
        "display_rules": "User chooses active title"
      },
      "artifacts": {
        "type": "collection",
        "definition": "Special items earned through hidden quests or milestones",
        "properties": ["id", "name", "description", "acquired_at", "lore_text"]
      }
    },
    "event_types": {
      "first_meeting": {
        "description": "Initial encounter with a character",
        "tracked_fields": ["character_id", "occurred_at", "location"]
      },
      "relationship_milestone": {
        "description": "Significant relationship progression",
        "tracked_fields": ["character_id", "new_level", "milestone_type"]
      },
      "zone_unlock": {
        "description": "New location becomes accessible",
        "tracked_fields": ["location_id", "unlock_trigger"]
      }
    }
  }
}
```

#### Narrative State Schema (PostgreSQL)

From `epics.md` lines 920-969:

```sql
CREATE TABLE narrative_states (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  scenario_id UUID REFERENCES scenario_templates(id),
  current_act INT NOT NULL DEFAULT 1,
  current_chapter INT NOT NULL DEFAULT 1,
  unlocked_quests UUID[] DEFAULT '{}',  -- Array of hidden quest IDs
  story_progress JSONB NOT NULL DEFAULT '{}',  -- Decisions, milestones, beat history
  world_state JSONB NOT NULL DEFAULT '{}',  -- Complete world state (see below)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(user_id, scenario_id)
);

CREATE INDEX idx_narrative_user ON narrative_states(user_id);
CREATE INDEX idx_narrative_scenario ON narrative_states(scenario_id);
```

**Complete World State Structure:**

From `epics.md` lines 932-969:

```json
{
  "locations": {
    "arena": {
      "discovered": true,
      "discovered_at": "2025-11-01T10:00:00Z",
      "description": "A vast open space...",
      "npcs_present": ["Lyra", "Thorne"],
      "visit_count": 23
    },
    "observatory": {
      "discovered": false,
      "unlock_condition": "chapter_2_reached"
    }
  },
  "events": [
    {
      "event_id": "first_meeting_lyra",
      "event_type": "first_meeting",
      "occurred_at": "2025-11-01T10:15:00Z",
      "location": "arena",
      "impact": {"relationship_change": {"Lyra": 1}},
      "narrative_beat_id": "beat-uuid-123"
    },
    {
      "event_id": "relationship_milestone_lyra_ally",
      "event_type": "relationship_milestone",
      "occurred_at": "2025-11-10T14:30:00Z",
      "character": "Lyra",
      "new_level": 3,
      "milestone_type": "became_ally"
    }
  ],
  "persons": {
    "Lyra": {
      "relationship_level": 3,
      "relationship_label": "Ally",
      "last_interaction": "2025-11-17T09:00:00Z",
      "knows_about": ["user_craft_goals", "user_struggles_with_consistency"],
      "dialogue_unlocked": ["craft_mastery_path", "dealing_with_setbacks"],
      "gifted_items": ["sketch_from_lyra"]
    },
    "Thorne": {
      "relationship_level": 1,
      "relationship_label": "Sparring Partner",
      "last_interaction": "2025-11-05T16:00:00Z",
      "knows_about": ["user_health_goals"],
      "dialogue_unlocked": ["basic_training"],
      "gifted_items": []
    }
  },
  "items": {
    "essence": 450,
    "titles": ["The Persistent", "The Relentless"],
    "active_title": "The Relentless",
    "artifacts": [
      {
        "id": "medallion_of_craft",
        "name": "Medallion of Craft",
        "acquired_at": "2025-11-10T14:30:00Z",
        "description": "A bronze medallion etched with intricate patterns",
        "lore_text": "Crafted by Lyra herself, this medallion represents...",
        "source": "hidden_quest_relentless"
      }
    ]
  },
  "world_time": {
    "current_act": 1,
    "current_chapter": 3,
    "days_in_story": 45,
    "story_started_at": "2025-10-03T00:00:00Z"
  },
  "decisions": [
    {
      "decision_id": "choice_mentor_focus",
      "chapter": 1,
      "prompt": "Focus on Craft with Lyra or Health with Thorne?",
      "choice": "craft",
      "consequences": ["stronger_lyra_relationship", "delayed_thorne_introduction"]
    }
  ]
}
```

**Critical Consistency Rules:**

From `epics.md` line 990:

- Cannot reference items not yet acquired
- Cannot reference locations not yet discovered
- Cannot reference events that haven't occurred
- Character knowledge must be consistent (can't know things not yet revealed)
- Relationship levels must progress logically (can't jump from 1 to 5)

#### Story Beat Schema

```json
{
  "id": "beat-uuid-123",
  "user_id": "user-uuid",
  "scenario_id": "scenario-uuid",
  "chapter": 3,
  "act": 1,
  "beat_type": "progression",  // 'progression', 'character_moment', 'hidden_quest_unlock', 'milestone'
  "content": {
    "title": "Lyra's Challenge",
    "text": "As you enter the Arena, Lyra awaits with a knowing smile...",
    "word_count": 287,
    "emotional_tone": "inspiring",
    "characters_involved": ["Lyra"]
  },
  "world_state_changes": {
    "events_added": ["lyra_challenge_issued"],
    "relationship_changes": {"Lyra": 1},
    "items_added": [],
    "locations_discovered": []
  },
  "metadata": {
    "generated_by": "narrative_agent_v1",
    "llm_model": "gpt-4o",
    "generation_tokens": 650,
    "user_context_used": {
      "recent_missions": 5,
      "current_streak": 12,
      "dominant_value": "craft"
    }
  },
  "created_at": "2025-11-17T10:00:00Z"
}
```

### API Contracts

**Narrative Service API:**

```python
# GET /api/v1/narrative/story
# Returns user's complete narrative history

{
  "scenario": {
    "id": "uuid",
    "name": "Modern Reality",
    "theme": "modern"
  },
  "current_state": {
    "act": 1,
    "chapter": 3,
    "days_in_story": 45
  },
  "story_beats": [
    {
      "id": "beat-uuid",
      "chapter": 3,
      "title": "Lyra's Challenge",
      "text": "...",
      "created_at": "2025-11-17T10:00:00Z",
      "characters_involved": ["Lyra"]
    }
  ],
  "unlocked_quests": [
    {
      "quest_id": "relentless_achievement",
      "title": "The Relentless",
      "unlocked_at": "2025-11-15T08:00:00Z",
      "status": "completed"
    }
  ],
  "world_state": {
    "locations_discovered": ["arena", "commons"],
    "characters_met": ["Eliza", "Lyra"],
    "essence_balance": 450,
    "active_title": "The Relentless"
  }
}
```

```python
# POST /api/v1/narrative/generate-beat
# Triggers story beat generation (called by ARQ worker or on-demand)

Request:
{
  "user_id": "uuid",
  "trigger_type": "milestone",  // 'milestone', 'scheduled', 'manual'
  "context": {
    "recent_achievements": ["20_day_streak_craft"]
  }
}

Response:
{
  "beat_id": "uuid",
  "content": {...},
  "world_state_updated": true,
  "quests_unlocked": 1
}
```

```python
# GET /api/v1/narrative/hidden-quests
# Returns user's hidden quests (unlocked and locked)

{
  "unlocked": [
    {
      "id": "relentless_achievement",
      "title": "The Relentless",
      "narrative_context": "...",
      "rewards": {...},
      "unlocked_at": "2025-11-15T08:00:00Z",
      "completed_at": "2025-11-16T12:00:00Z"
    }
  ],
  "progress_hints": [
    "Complete 100 missions to unlock a century milestone",
    "Maintain a 30-day streak to discover an ancient secret"
  ]
}
```

### Narrative Generation Flow (LangGraph)

From `epics.md` lines 1000-1041 and `architecture.md` Pattern 1:

**LangGraph State Machine Nodes:**

1. **assess_progress** (Input Node):
   - Inputs: `user_id`, `trigger_type`, `generation_context`
   - Queries:
     - User's mission completion history (last 30 days)
     - Current streaks (overall, per-attribute)
     - Value focus distribution (health/craft/growth/connection percentages)
     - Recent goal achievements
   - Outputs: `user_progress_summary`

2. **select_beat** (Decision Node):
   - Inputs: `user_progress_summary`, `current_narrative_state`, `scenario_template`
   - Logic:
     - Check if chapter progression trigger met
     - Check if act transition trigger met
     - Determine beat type: progression, character_moment, hidden_quest_unlock, milestone
     - Select appropriate narrative arc template from scenario
   - Outputs: `selected_beat_template`, `beat_type`

3. **generate_content** (LLM Node):
   - Inputs: `selected_beat_template`, `user_progress_summary`, `current_world_state`, `character_prompts`
   - LLM Prompt Structure:
     ```
     You are a master storyteller creating a personalized narrative beat.

     Scenario: {scenario.name} ({scenario.theme})
     Current Chapter: {chapter} - {chapter_title}
     Beat Type: {beat_type}

     User Context:
     - Recent missions: {missions_completed_list}
     - Current streak: {streak_days} days (focus: {dominant_attribute})
     - Recent achievements: {achievements}

     Current World State:
     - Locations discovered: {locations}
     - Characters met: {characters}
     - Relationship levels: {relationships}
     - Recent events: {last_5_events}

     Beat Template: {beat_template}

     CRITICAL CONSISTENCY RULES:
     - Do NOT reference items user hasn't acquired: {items_not_acquired}
     - Do NOT reference locations user hasn't discovered: {locations_not_discovered}
     - Maintain character knowledge consistency: {character_knowledge_limits}

     Generate a story beat (200-400 words) that:
     1. Reflects the user's real progress and achievements
     2. Maintains strict consistency with world state
     3. Advances the narrative arc naturally
     4. Creates emotional resonance
     5. Sets up future story possibilities

     Return JSON:
     {
       "title": "...",
       "text": "...",
       "emotional_tone": "...",
       "characters_involved": [...],
       "world_state_changes": {...}
     }
     ```
   - Model: OpenAI GPT-4o (premium quality)
   - Max tokens: 800 (200-400 words ≈ 500-800 tokens)
   - Temperature: 0.7 (creative but consistent)
   - Outputs: `generated_beat`

4. **check_unlocks** (Validation + Unlock Node):
   - Inputs: `user_progress_summary`, `hidden_quests_template`, `current_unlocked_quests`
   - Logic:
     - For each hidden quest in template:
       - If not already unlocked AND trigger conditions met:
         - Add to unlock queue
         - Generate unlock notification
   - Outputs: `quests_to_unlock`, `updated_narrative_state`

5. **validate_consistency** (Validation Node):
   - Inputs: `generated_beat`, `current_world_state`, `scenario_world_schema`
   - Validation Checks:
     - All referenced items exist in world_state.items
     - All referenced locations exist in world_state.locations.discovered
     - All referenced events exist in world_state.events
     - Character knowledge is consistent
     - Relationship level changes are logical (max +1 per beat)
   - Outputs: `validation_passed`, `consistency_errors`
   - Error Handling: If validation fails, regenerate with stricter constraints

6. **update_state** (Output Node):
   - Inputs: `generated_beat`, `world_state_changes`, `quests_to_unlock`
   - Actions:
     - Save story beat to database
     - Update narrative_states.world_state with changes
     - Update narrative_states.unlocked_quests if applicable
     - Update narrative_states.current_chapter/act if progressed
     - Create notification for user
   - Outputs: `beat_id`, `updated_state`

**Agent State Schema:**

```python
from typing import TypedDict, List, Dict, Any

class NarrativeAgentState(TypedDict):
    user_id: str
    scenario_id: str
    trigger_type: str

    # Node outputs
    user_progress_summary: Dict[str, Any]
    selected_beat_template: Dict[str, Any]
    beat_type: str
    generated_beat: Dict[str, Any]
    quests_to_unlock: List[str]
    validation_passed: bool
    consistency_errors: List[str]

    # Final output
    beat_id: str
    updated_narrative_state: Dict[str, Any]
```

### Testing Strategy

**Unit Testing:**

- Scenario template validation (JSONB structure correctness)
- Hidden quest trigger condition evaluation
- World state consistency checks
- Narrative beat parsing and storage

**Integration Testing:**

- End-to-end story beat generation flow
- LangGraph agent execution with mock LLM
- Hidden quest unlocking worker
- API endpoint responses

**Consistency Testing (Critical):**

From `epics.md` line 1037-1040:

- Generate 100 story beats for test user
- Verify no items referenced before acquisition
- Verify no locations referenced before discovery
- Verify character knowledge consistency
- Verify relationship level progression logic
- Verify event chronology consistency

**LLM Testing:**

- Cost per beat generation (target: <$0.05)
- Generation time (target: <10 seconds)
- Consistency validation pass rate (target: >95% without regeneration)
- Emotional tone diversity (prevent repetitive writing)

**User Experience Testing:**

- Story beat readability and engagement
- Chapter progression feels natural
- Hidden quest unlocks feel rewarding
- Character interactions feel consistent

### Implementation Patterns

**Naming Conventions:**

- Services: `narrative_service.py`, `scenario_service.py`
- Agents: `narrative_agent.py`
- Workers: `quest_generator.py` (extend for hidden quests)
- Models: `narrative.py` (contains ScenarioTemplate, NarrativeState, StoryBeat)
- Frontend: `narrative/page.tsx`, `StoryBeat.tsx`, `ChapterNav.tsx`

**Error Handling:**

- LLM generation failures: Retry with exponential backoff (3 attempts)
- Consistency validation failures: Regenerate with stricter constraints
- Worker failures: ARQ retry with dead letter queue
- API errors: Return user-friendly messages

**Performance Optimization:**

- Cache scenario templates in Redis (rarely change)
- Lazy-load story beats (paginate frontend display)
- Async story generation (doesn't block user interaction)
- JSONB indexing for world_state queries

**Security:**

- User can only access their own narrative state
- Scenario templates are read-only for users
- Hidden quest templates hidden from API responses (no spoilers)

## Integration Points

**Epic 2 (Companion & Memory):**

- Eliza references narrative progress in conversations
- Memory service stores narrative context in project-tier memories
- Character relationship levels influence Eliza's tone

**Epic 3 (Goal & Mission Management):**

- Mission completions trigger narrative progression
- Hidden quests appear as "Special" missions
- Quest rewards include Essence currency

**Epic 5 (Progress & Analytics):**

- Streak tracking feeds into narrative progression triggers
- Milestone achievements unlock hidden quests
- DCI score influences narrative tone (struggling vs thriving)

**Epic 6 (World State & Time):**

- Zone unlocking tied to narrative progression
- Character presence in zones based on relationship levels
- Time-aware narrative events

**Epic 7 (Nudge & Outreach):**

- Character-initiated story events use nudge infrastructure
- Story beat notifications via in-app alerts
- Optimal timing for narrative progression notifications

## Technical References

**Source Documents:**

- **Epics File**: `docs/epics.md` (lines 906-1246: Epic 4 complete breakdown)
- **Architecture**: `docs/ARCHITECTURE.md` (lines 300-401: Pattern 1 Living Narrative Engine)
- **Architecture**: `docs/ARCHITECTURE.md` (lines 1032-1041: GPT-4o narrative model decision)
- **Product Brief**: `docs/product-brief-Delight-2025-11-09.md` (narrative vision and user needs)

**Technical Documentation:**

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **OpenAI GPT-4o**: https://platform.openai.com/docs/models/gpt-4o
- **PostgreSQL JSONB**: https://www.postgresql.org/docs/current/datatype-json.html
- **Framer Motion**: https://www.framer.com/motion/

**AI/LLM Strategy:**

From `architecture.md` lines 1170-1211:

- **Model**: GPT-4o for narrative generation (premium quality)
- **Cost**: $2.50/$10 per 1M tokens (input/output)
- **Frequency**: ~2-3 story beats per week per user
- **Budget Impact**: ~$0.02/user/day (within $0.50 target)
- **Rationale**: Narrative requires superior writing quality and story consistency
- **Alternative**: GPT-4o-mini tested but quality insufficient for immersive storytelling

## Implementation Notes

**Story Order:**

1. **Story 4.1**: Database schema and seed data (foundation)
2. **Story 4.2**: Narrative agent (core generation logic)
3. **Story 4.3**: Hidden quest system (engagement driver)
4. **Story 4.4**: Story viewing UI (user-facing feature)
5. **Stories 4.5-4.7**: Future enhancements (post-MVP)

**Estimated Timeline:**

- Story 4.1: 8-10 hours (comprehensive schema, seed data, migrations)
- Story 4.2: 12-16 hours (LangGraph agent, LLM integration, consistency validation)
- Story 4.3: 6-8 hours (trigger detection, worker, notifications)
- Story 4.4: 8-10 hours (UI components, API, animations)
- **Total MVP**: 34-44 hours

**Risk Mitigation:**

- **Risk**: GPT-4o consistency issues (references non-existent items)
  - **Mitigation**: Strict validation layer, regenerate on failure, comprehensive prompts
- **Risk**: JSONB world state becomes too large (>1MB per user)
  - **Mitigation**: Periodic archiving of old events, pagination for retrieval
- **Risk**: Hidden quest triggers too easy/hard to unlock
  - **Mitigation**: Telemetry on unlock rates, adjustable trigger thresholds
- **Risk**: Narrative feels generic despite personalization
  - **Mitigation**: A/B testing different prompt strategies, user feedback surveys

## Future Enhancements (Post-Epic)

- **Multiple scenario templates**: Medieval Fantasy, Sci-Fi Odyssey, etc.
- **User-created scenarios**: Community-generated narrative templates (with moderation)
- **AI-generated visual assets**: Story beat illustrations with DALL-E
- **Audio narration**: Text-to-speech for story beats
- **Multiple endings**: Different story conclusions based on user choices
- **Collaborative narratives**: Shared story arcs for accountability pods

---

**Last Updated:** 2025-11-18
**Version:** 1.0.0
**Status:** Ready for Story Creation

---

## Appendix: Modern Reality Scenario Example

**Scenario Name:** "The Mirror's Edge"

**Theme:** Contemporary alter-ego journey with realistic characters

**Narrative Arc:**

- **Act 1 - Awakening** (Chapters 1-2): User discovers their potential through small wins
- **Act 2 - Challenge** (Chapters 3-4): Obstacles emerge, relationships deepen
- **Act 3 - Transformation** (Chapter 5-6): Mastery achieved, identity transformed

**Characters:**

- **Eliza**: Ever-present companion and guide (not narrative character - distinction from Story 2.7)
- **Lyra**: Art gallery owner, craft mentor, poetic and patient
- **Thorne**: Personal trainer, health mentor, direct and challenging
- **Elara**: University professor, growth mentor, contemplative and wise

**Hidden Quests (Seed Data):**

1. **The Relentless** (Trigger: 20-day streak, craft focus)
2. **Century Milestone** (Trigger: 100 missions completed)
3. **The Balanced Path** (Trigger: Equal missions across all 4 values for 14 days)
4. **Night Owl's Discovery** (Trigger: 30 missions completed after 10pm)
5. **The Unseen Observer** (Trigger: 50 reflection notes written)

This scenario provides foundation for Stories 4.1-4.4, demonstrating comprehensive world-building without fantasy elements (Modern Reality theme).
