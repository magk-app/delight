# Novel Pattern Designs

### Pattern 1: Living Narrative Engine

**Purpose:** Generate personalized stories that adapt to real-world user progress, with pre-planned narrative beats that unlock based on user actions.

**Architecture:**

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

**Implementation:**

- **Service:** `backend/app/services/narrative_service.py`
- **Agent:** `backend/app/agents/narrative_agent.py` (LangGraph state machine)
- **Database:** `narrative_states` table (user_id, chapter, hidden_quests JSON)
- **Workers:** `backend/app/workers/quest_generator.py` (pre-generates 3-5 hidden quests at story start)

**Data Flow:**

1. User starts story → Narrative service generates 3-5 hidden quests, stores in DB
2. User completes missions → Trigger monitor (ARQ worker) checks conditions
3. Condition met → Hidden quest unlocks, narrative content served
4. User progresses → Story state advances, new chapters unlock

**Scenario Template Storage:**

Multiple narrative scenarios (Modern Reality, Medieval Fantasy, etc.) are stored using PostgreSQL JSONB for flexibility and dynamic generation:

```sql
CREATE TABLE scenario_templates (
  id UUID PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  theme VARCHAR(50) NOT NULL,  -- 'modern', 'medieval', 'scifi', etc.
  narrative_arc JSONB NOT NULL,  -- Chapter structure, story beats, act progression
  character_prompts JSONB NOT NULL,  -- Personality definitions for each character
  hidden_quests JSONB NOT NULL,  -- Pre-planned surprises with trigger conditions
  time_rules JSONB,  -- Zone availability by time (optional overrides)
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scenario_theme ON scenario_templates(theme);
```

**Template Structure Example:**

```json
{
  "narrative_arc": {
    "act_1": {
      "title": "Arrival",
      "chapters": ["The Journey Begins", "First Steps"],
      "progression_trigger": {"missions_completed": 5}
    },
    "act_2": {...},
    "act_3": {...}
  },
  "character_prompts": {
    "eliza": "You are Eliza, a wise and empathetic guide...",
    "lyra": "You are Lyra, master artisan of the Guild..."
  },
  "hidden_quests": [
    {
      "id": "relentless_achievement",
      "trigger": {"streak_days": 20, "attribute": "craft"},
      "title": "The Relentless",
      "narrative": "...",
      "rewards": {"essence": 500, "title": "The Relentless"}
    }
  ]
}
```

This approach allows:

- Easy addition of new scenarios without code changes
- User-specific narrative customization
- Version control for narrative content
- Dynamic template selection based on user preferences

---

### Pattern 2: Multi-Character AI System

**Purpose:** Manage multiple AI characters (Eliza, Lyra, Thorne, Elara) with distinct personalities, relationship levels, and character-initiated interactions.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ Character Orchestration Layer                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Eliza Agent  │  │ Lyra Agent   │  │ Thorne Agent │  │
│  │ (Protagonist)│  │ (Craft)      │  │ (Health)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                              │
│                   ┌────────▼────────┐                    │
│                   │ Character State │                    │
│                   │ - Personality   │                    │
│                   │ - Relationship  │                    │
│                   │ - Conversation  │                    │
│                   │   History       │                    │
│                   └─────────────────┘                    │
│                            │                              │
│                   ┌────────▼────────┐                    │
│                   │ Initiation      │                    │
│                   │ Scheduler       │                    │
│                   │ (ARQ)           │                    │
│                   └─────────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

- **Agents:** `backend/app/agents/eliza_agent.py`, `backend/app/agents/character_agents.py`
- **Service:** `backend/app/services/character_service.py`
- **Database:** `characters` table (personality JSON, relationship_level INT)
- **Memory:** Separate PostgreSQL vector tables per character for conversation history
- **Scheduler:** `backend/app/workers/character_initiator.py` (proactive character interactions)

**Character-Initiated Flow:**

1. ARQ scheduler checks user activity patterns (e.g., 2 weeks of Craft focus)
2. Character service selects appropriate character (e.g., Elara for Growth)
3. Character agent generates proactive message with context
4. User receives notification: "Elara seeks you in the Observatory"
5. Conversation starts with character's personality and relationship level

---

### Pattern 3: Time-Aware World State

**Purpose:** World state (zone availability, character presence) changes based on real-world time, with user-configurable overrides.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ World State Service                                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────┐           │
│  │ Time Rules Engine                         │           │
│  │ - Default: Arena closes 9pm, opens 6am   │           │
│  │ - User Override: Custom productive hours │           │
│  │ - Timezone: User's local time            │           │
│  └──────────────────────────────────────────┘           │
│                            │                              │
│         ┌──────────────────┼──────────────────┐          │
│         │                  │                  │          │
│    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐    │
│    │ Arena   │      │Observatory│     │  Commons  │    │
│    │(Health) │      │ (Growth)  │     │(Connection)│    │
│    └─────────┘      └───────────┘     └───────────┘    │
│         │                  │                  │          │
│    ┌────▼──────────────────▼──────────────────▼────┐    │
│    │ World State Cache (Redis)                      │    │
│    │ - Zone availability                            │    │
│    │ - Character presence                           │    │
│    │ - Time-based events                            │    │
│    └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

- **Service:** `backend/app/services/world_service.py`
- **Database:** `user_preferences` table (timezone, custom_hours JSON)
- **Cache:** Redis for world state (TTL: 15 minutes)
- **Frontend:** WebSocket connection for real-time world state updates + fallback polling

---
