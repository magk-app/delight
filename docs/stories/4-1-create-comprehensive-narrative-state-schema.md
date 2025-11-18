# Story 4.1: Create Comprehensive Narrative State Schema and Scenario Templates

**Story ID:** 4.1
**Epic:** 4 - Narrative Engine
**Status:** drafted
**Priority:** P1 (Narrative Foundation)
**Estimated Effort:** 8-10 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18

---

## User Story

**As a** developer,
**I want** a flexible, comprehensive schema for narrative scenarios and dynamic world state,
**So that** we can support multiple themes and maintain story consistency across all narrative elements.

---

## Context

### Problem Statement

The Narrative Engine (Epic 4) requires a robust database foundation to track living, dynamic stories that adapt to user progress. Unlike static storytelling systems, Delight's narrative must track comprehensive world state including locations, events, persons, and items while enforcing strict consistency rules.

This story creates two critical schemas:

1. **Scenario Templates** (`scenario_templates` table): Reusable narrative frameworks defining acts, chapters, characters, hidden quests, and world rules for different themes (Modern Reality, Medieval Fantasy, Sci-Fi)

2. **Narrative State** (`narrative_states` table): Per-user dynamic world state tracking every discovered location, occurred event, character relationship, and acquired item

**Critical Requirement:** The world state must prevent inconsistencies - users cannot reference items not yet acquired, locations not yet discovered, or events that haven't occurred. This ensures story coherence across hundreds of generated narrative beats.

### Why This Approach?

**From Architecture (ADR Pattern 1: Living Narrative Engine, lines 300-401):**

We use PostgreSQL JSONB for world state instead of rigid relational tables because:

- ✅ **Flexibility**: New scenarios can add custom locations/items without schema migrations
- ✅ **Performance**: JSONB queries are fast with GIN indexes
- ✅ **Consistency**: Single source of truth for all world state in one document
- ✅ **Versioning**: Easy to track state changes over time
- ✅ **Schema Evolution**: Scenario templates can define different world schemas

**From Tech Spec (tech-spec-epic-4.md lines 45-180):**

The comprehensive world state tracks:

- **Locations**: discovered status, NPCs present, visit counts
- **Events**: chronological event history with impacts
- **Persons**: relationship levels, knowledge, dialogue unlocks
- **Items**: essence balance, titles, artifacts with lore
- **World Time**: current act/chapter, days in story
- **Decisions**: user choices and their consequences

### Dependencies

- **Prerequisite Stories:**
  - 1.2 (Database schema and migrations) ✅ Complete
  - PostgreSQL database with Alembic configured
  - SQLAlchemy 2.0 async models in place

- **Epic 4 Context:** This story **enables**:
  - Story 4.2: Narrative generation agent reads scenario templates and updates world state
  - Story 4.3: Hidden quest system uses trigger conditions from templates
  - Story 4.4: Story viewing UI displays narrative beats and world state
  - Story 4.6: Branching narratives track user decisions in world state

- **External Dependencies:** None (pure database schema and seed data)

### Technical Background from Epic 4 Design Documents

**From Tech Spec (lines 75-180):**

Complete schema design includes:

- Scenario template JSONB structure with narrative_arc, character_prompts, hidden_quests, time_rules, world_schema
- Narrative state JSONB with comprehensive world state tracking
- Consistency enforcement rules
- Seed data for "Modern Reality" scenario

**From Epics (epics.md lines 920-990):**

Requirements specify:

- Multi-theme support (medieval, sci-fi, modern)
- 3 acts with progression triggers
- 3-5 hidden quest templates per scenario
- Defines all possible locations, persons, items, event types
- **Critical**: No inconsistent values, items, or events allowed

---

## Acceptance Criteria

### AC1: Scenario Templates Table Created with Comprehensive JSONB Structure

**Given** the database is set up with Alembic
**When** I run the migration for scenario templates
**Then** the `scenario_templates` table exists with:

- `id` UUID PRIMARY KEY
- `name` VARCHAR(100) NOT NULL (e.g., "The Mirror's Edge")
- `theme` VARCHAR(50) NOT NULL (e.g., "modern", "medieval", "scifi")
- `narrative_arc` JSONB NOT NULL (acts, chapters, progression triggers)
- `character_prompts` JSONB NOT NULL (personality definitions for each character)
- `hidden_quests` JSONB NOT NULL (pre-planned surprises with trigger conditions)
- `time_rules` JSONB (zone availability by time, optional)
- `world_schema` JSONB NOT NULL (defines all possible locations, persons, items, events)
- `created_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- `updated_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()

**And** an index exists on `theme` column for fast filtering

**Verification:**

```sql
\d scenario_templates
SELECT * FROM pg_indexes WHERE tablename = 'scenario_templates';
```

### AC2: Narrative States Table Created with Per-User World State Tracking

**Given** the database is set up
**When** I run the migration for narrative states
**Then** the `narrative_states` table exists with:

- `id` UUID PRIMARY KEY
- `user_id` UUID REFERENCES users(id) ON DELETE CASCADE
- `scenario_id` UUID REFERENCES scenario_templates(id)
- `current_act` INT NOT NULL DEFAULT 1
- `current_chapter` INT NOT NULL DEFAULT 1
- `unlocked_quests` UUID[] DEFAULT '{}' (array of hidden quest IDs)
- `story_progress` JSONB NOT NULL DEFAULT '{}' (decisions, milestones, beat history)
- `world_state` JSONB NOT NULL DEFAULT '{}' (comprehensive world state)
- `created_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- `updated_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- UNIQUE constraint on (user_id, scenario_id)

**And** indexes exist on `user_id` and `scenario_id` columns

**Verification:**

```sql
\d narrative_states
SELECT * FROM pg_indexes WHERE tablename = 'narrative_states';
```

### AC3: World State JSONB Structure Tracks All Narrative Elements

**Given** the narrative_states table exists
**When** I examine the world_state JSONB schema (from seed data or documentation)
**Then** the world_state structure includes:

**Locations:**
```json
{
  "locations": {
    "location_key": {
      "discovered": boolean,
      "discovered_at": timestamp,
      "description": string,
      "npcs_present": array,
      "visit_count": integer
    }
  }
}
```

**Events:**
```json
{
  "events": [
    {
      "event_id": string,
      "event_type": string,
      "occurred_at": timestamp,
      "location": string,
      "impact": object,
      "narrative_beat_id": string
    }
  ]
}
```

**Persons:**
```json
{
  "persons": {
    "character_name": {
      "relationship_level": integer (0-10),
      "relationship_label": string,
      "last_interaction": timestamp,
      "knows_about": array,
      "dialogue_unlocked": array,
      "gifted_items": array
    }
  }
}
```

**Items:**
```json
{
  "items": {
    "essence": integer,
    "titles": array,
    "active_title": string,
    "artifacts": [
      {
        "id": string,
        "name": string,
        "acquired_at": timestamp,
        "description": string,
        "lore_text": string,
        "source": string
      }
    ]
  }
}
```

**World Time:**
```json
{
  "world_time": {
    "current_act": integer,
    "current_chapter": integer,
    "days_in_story": integer,
    "story_started_at": timestamp
  }
}
```

**Decisions:**
```json
{
  "decisions": [
    {
      "decision_id": string,
      "chapter": integer,
      "prompt": string,
      "choice": string,
      "consequences": array
    }
  ]
}
```

### AC4: Scenario Template JSONB Structure Defines Complete Narrative Framework

**Given** the scenario_templates table exists
**When** I examine the JSONB schema (from seed data or documentation)
**Then** the narrative_arc structure includes:

**Acts and Chapters:**
```json
{
  "narrative_arc": {
    "act_1": {
      "title": string,
      "chapters": [
        {
          "number": integer,
          "title": string,
          "progression_trigger": {
            "missions_completed": integer,
            "streak_days": integer
          }
        }
      ]
    }
  }
}
```

**And** the hidden_quests structure includes:

```json
{
  "hidden_quests": [
    {
      "id": string,
      "trigger": object,
      "title": string,
      "narrative_context": string,
      "rewards": {
        "essence": integer,
        "title": string,
        "relationship_boost": object,
        "artifact": object
      },
      "time_limit_hours": integer or null,
      "narrative_significance": string
    }
  ]
}
```

**And** the world_schema defines all possible narrative elements:

```json
{
  "world_schema": {
    "locations": {...},
    "persons": {...},
    "items": {...},
    "event_types": {...}
  }
}
```

### AC5: At Least One Complete Scenario Template is Seeded (Modern Reality)

**Given** the scenario_templates table exists and migrations have run
**When** I query scenario templates
**Then** at least one scenario exists with:

- Name: "The Mirror's Edge" (or similar)
- Theme: "modern"
- 3 acts defined in narrative_arc
- At least 5 chapters across all acts
- 3-5 hidden quest templates
- Complete world_schema with:
  - At least 3 locations (arena, observatory, commons)
  - At least 3 characters (Lyra, Thorne, Elara)
  - Item definitions (essence, titles, artifacts)
  - At least 3 event types

**And** each chapter has valid progression triggers

**And** each hidden quest has valid trigger conditions

**Verification:**

```sql
SELECT name, theme,
       jsonb_array_length(narrative_arc->'act_1'->'chapters') as act1_chapters,
       jsonb_array_length(narrative_arc->'act_2'->'chapters') as act2_chapters,
       jsonb_array_length(narrative_arc->'act_3'->'chapters') as act3_chapters,
       jsonb_array_length(hidden_quests) as hidden_quest_count
FROM scenario_templates
WHERE theme = 'modern';
```

### AC6: Scenario Template Supports Multiple Themes for Future Expansion

**Given** the scenario_templates table exists
**When** I insert scenario templates with different themes
**Then** the schema accommodates:

- `theme = 'modern'` (Modern Reality)
- `theme = 'medieval'` (Medieval Fantasy)
- `theme = 'scifi'` (Sci-Fi Odyssey)
- Custom themes with different world_schema structures

**And** I can query scenarios by theme efficiently using the index

**Verification:**

```sql
-- Should work without errors
INSERT INTO scenario_templates (name, theme, narrative_arc, character_prompts, hidden_quests, world_schema)
VALUES ('Test Medieval', 'medieval', '{}', '{}', '[]', '{}');

SELECT name FROM scenario_templates WHERE theme = 'medieval';
```

### AC7: Critical Consistency Rules Documented in Schema/Code

**Given** the narrative state schema is implemented
**When** I review the database models and seed data
**Then** consistency rules are documented:

- Cannot reference items not yet acquired
- Cannot reference locations not yet discovered
- Cannot reference events that haven't occurred
- Character knowledge must be consistent (can't know things not yet revealed)
- Relationship levels must progress logically (can't jump from 1 to 5)

**And** these rules are enforced in code comments or database constraints where applicable

### AC8: SQLAlchemy Models Created for Scenario Templates and Narrative States

**Given** the migration is complete
**When** I review the models
**Then** SQLAlchemy models exist:

- `ScenarioTemplate` in `backend/app/models/narrative.py`
- `NarrativeState` in `backend/app/models/narrative.py`

**And** models include:

- Proper type hints for all fields
- JSONB fields mapped correctly
- Relationships defined (narrative_states → scenario_templates FK)
- Helper methods for common operations (e.g., `get_current_chapter_data()`)

**Verification:**

```python
from app.models.narrative import ScenarioTemplate, NarrativeState
from app.db.session import get_db

async with get_db() as db:
    scenario = await db.get(ScenarioTemplate, scenario_id)
    assert scenario.narrative_arc is not None
    assert scenario.theme in ['modern', 'medieval', 'scifi']
```

---

## Tasks / Subtasks

### Task 1: Create Alembic Migration for Scenario Templates Table (AC: #1, #4)

- [ ] **1.1** Create migration file: `alembic revision -m "add_scenario_templates_table"`
- [ ] **1.2** Define `scenario_templates` table with all columns (id, name, theme, narrative_arc, character_prompts, hidden_quests, time_rules, world_schema, created_at, updated_at)
- [ ] **1.3** Add index on `theme` column: `CREATE INDEX idx_scenario_theme ON scenario_templates(theme)`
- [ ] **1.4** Add table comment documenting JSONB structure
- [ ] **1.5** Test migration: `alembic upgrade head`
- [ ] **1.6** Test rollback: `alembic downgrade -1`

### Task 2: Create Alembic Migration for Narrative States Table (AC: #2, #3)

- [ ] **2.1** Create migration file: `alembic revision -m "add_narrative_states_table"`
- [ ] **2.2** Define `narrative_states` table with all columns
- [ ] **2.3** Add foreign key constraints to `users` and `scenario_templates`
- [ ] **2.4** Add UNIQUE constraint on (user_id, scenario_id)
- [ ] **2.5** Add indexes on `user_id` and `scenario_id`
- [ ] **2.6** Add table comments documenting world_state and story_progress JSONB structures
- [ ] **2.7** Test migration and rollback

### Task 3: Create SQLAlchemy Models (AC: #8)

- [ ] **3.1** Create `backend/app/models/narrative.py`
- [ ] **3.2** Implement `ScenarioTemplate` model:
  - All fields with proper types
  - JSONB fields: narrative_arc, character_prompts, hidden_quests, time_rules, world_schema
  - Timestamps with default NOW()
  - Type hints for Python 3.11+
- [ ] **3.3** Implement `NarrativeState` model:
  - All fields with proper types
  - JSONB fields: story_progress, world_state
  - Array field: unlocked_quests (UUID[])
  - Foreign key relationships
  - UNIQUE constraint on (user_id, scenario_id)
- [ ] **3.4** Add helper methods:
  - `get_current_chapter_data()` returns chapter info from narrative_arc
  - `get_character_data(character_name)` returns character info from world_state.persons
  - `has_discovered_location(location_key)` checks world_state.locations
  - `has_acquired_item(item_id)` checks world_state.items.artifacts
- [ ] **3.5** Add model to `__init__.py` for Alembic autogenerate

### Task 4: Create Modern Reality Scenario Seed Data (AC: #5)

- [ ] **4.1** Create seed script: `backend/app/db/seeds/scenario_templates.py`
- [ ] **4.2** Define "The Mirror's Edge" scenario:
  - Name, theme, created_at
  - narrative_arc with 3 acts:
    - Act 1 "Awakening": 2 chapters
    - Act 2 "Challenge": 2 chapters
    - Act 3 "Transformation": 2 chapters
  - Each chapter with title and progression_trigger
- [ ] **4.3** Define character_prompts for:
  - Lyra (Craft mentor): personality traits, role, background
  - Thorne (Health mentor): personality traits, role, background
  - Elara (Growth mentor): personality traits, role, background
- [ ] **4.4** Define hidden_quests array (3-5 quests):
  - "The Relentless": trigger {streak_days: 20, attribute: "craft"}
  - "Century Milestone": trigger {missions_completed: 100}
  - "The Balanced Path": trigger {equal_value_distribution: 14 days}
  - "Night Owl's Discovery": trigger {missions_after_10pm: 30}
  - "The Unseen Observer": trigger {reflection_notes_written: 50}
- [ ] **4.5** Define world_schema:
  - locations: arena, observatory, commons (with unlock conditions)
  - persons: Lyra, Thorne, Elara (with relationship levels)
  - items: essence, titles, artifacts (with properties)
  - event_types: first_meeting, relationship_milestone, zone_unlock
- [ ] **4.6** Add seed execution to migration or separate script

### Task 5: Create Pydantic Schemas for API (AC: #8)

- [ ] **5.1** Create `backend/app/schemas/narrative.py`
- [ ] **5.2** Define `ScenarioTemplateResponse` schema:
  - id, name, theme
  - Exclude sensitive fields (hidden_quests details)
  - Include summary data (act count, chapter count)
- [ ] **5.3** Define `NarrativeStateResponse` schema:
  - current_act, current_chapter, days_in_story
  - world_state (full or filtered)
  - unlocked_quests (IDs only, no spoilers)
- [ ] **5.4** Define `WorldStateResponse` schema:
  - locations_discovered: list
  - characters_met: list
  - essence_balance: int
  - active_title: str
  - artifacts: list (with details)

### Task 6: Document JSONB Structures and Consistency Rules (AC: #7)

- [ ] **6.1** Create `backend/app/models/narrative.py` docstrings:
  - Document world_state JSONB structure
  - Document narrative_arc JSONB structure
  - Document hidden_quests JSONB structure
- [ ] **6.2** Create `docs/epic-4/NARRATIVE-STATE-SCHEMA.md`:
  - Complete world_state schema with examples
  - Consistency rules documentation
  - Example queries for common operations
- [ ] **6.3** Add inline comments to models explaining consistency rules
- [ ] **6.4** Create JSON schema files (optional):
  - `backend/app/schemas/json/world_state.schema.json`
  - `backend/app/schemas/json/narrative_arc.schema.json`

### Task 7: Create Unit Tests for Models (AC: #8)

- [ ] **7.1** Create `backend/tests/models/test_narrative.py`
- [ ] **7.2** Test `ScenarioTemplate` model:
  - Create scenario with valid JSONB
  - Query by theme
  - Validate JSONB structure parsing
- [ ] **7.3** Test `NarrativeState` model:
  - Create narrative state with initial world_state
  - Update world_state (add location, add event, update relationship)
  - Validate UNIQUE constraint on (user_id, scenario_id)
  - Test helper methods
- [ ] **7.4** Test consistency validation (if implemented as model methods):
  - Test has_discovered_location()
  - Test has_acquired_item()
  - Test relationship_level progression logic

### Task 8: Create Integration Tests for Seed Data (AC: #5)

- [ ] **8.1** Create `backend/tests/integration/test_scenario_seed.py`
- [ ] **8.2** Test Modern Reality scenario exists after seed
- [ ] **8.3** Validate narrative_arc structure:
  - 3 acts with correct titles
  - Chapters with progression triggers
- [ ] **8.4** Validate hidden_quests structure:
  - At least 3 quests
  - Each quest has id, trigger, title, rewards
- [ ] **8.5** Validate world_schema completeness:
  - Locations defined
  - Characters defined
  - Items defined
  - Event types defined
- [ ] **8.6** Test querying by theme

---

## Dev Notes

### Comprehensive World State Architecture

**From Tech Spec (tech-spec-epic-4.md lines 75-180):**

The world_state JSONB is the single source of truth for all narrative elements. Unlike traditional storytelling systems with static scripts, this dynamic state tracks every discovery, event, and relationship change.

**Key Design Principles:**

1. **Single Document**: All narrative state in one JSONB document (not spread across tables)
2. **Chronological Events**: events array preserves exact order of occurrences
3. **Relationship Progression**: persons object tracks relationship levels with history
4. **Discovery Tracking**: locations track discovered status and timestamp
5. **Item Acquisition**: items.artifacts array maintains acquisition chronology

**Consistency Enforcement Strategy:**

From `epics.md` line 990:

- **Validation Layer**: Story generation agent validates all references before creating beats
- **Schema Constraints**: world_schema in scenario template defines what's possible
- **Event Chronology**: events array ensures temporal consistency
- **Knowledge Tracking**: persons[].knows_about prevents character omniscience

**Example World State Evolution:**

```json
// Day 1: User starts story
{
  "locations": {
    "commons": {"discovered": true, "discovered_at": "2025-11-01", "npcs_present": ["Eliza"]}
  },
  "events": [],
  "persons": {},
  "items": {"essence": 0, "titles": [], "artifacts": []},
  "world_time": {"current_act": 1, "current_chapter": 1, "days_in_story": 0}
}

// Day 5: User completes 5 missions, discovers Arena, meets Lyra
{
  "locations": {
    "commons": {"discovered": true, ...},
    "arena": {"discovered": true, "discovered_at": "2025-11-05", "npcs_present": ["Lyra"], "visit_count": 1}
  },
  "events": [
    {"event_id": "arena_discovered", "occurred_at": "2025-11-05T10:00:00Z", ...},
    {"event_id": "first_meeting_lyra", "occurred_at": "2025-11-05T10:15:00Z", ...}
  ],
  "persons": {
    "Lyra": {"relationship_level": 1, "knows_about": ["user_craft_focus"]}
  },
  "items": {"essence": 75, "titles": [], "artifacts": []},
  "world_time": {"current_act": 1, "current_chapter": 1, "days_in_story": 5}
}
```

### Scenario Template Architecture

**From Tech Spec (tech-spec-epic-4.md lines 45-75):**

Scenario templates are reusable narrative frameworks. The JSONB structure allows complete flexibility for different themes without schema migrations.

**Template Components:**

1. **narrative_arc**: Acts and chapters with progression logic
2. **character_prompts**: LLM personality prompts for each character
3. **hidden_quests**: Pre-planned surprises with trigger conditions
4. **time_rules**: Optional zone availability overrides
5. **world_schema**: Defines all possible narrative elements (master schema)

**Modern Reality Scenario Design:**

From Appendix in tech-spec-epic-4.md:

- **Theme**: Contemporary alter-ego journey (no fantasy elements)
- **Characters**: Lyra (artist), Thorne (trainer), Elara (professor)
- **Acts**: Awakening → Challenge → Transformation
- **Hidden Quests**: 5 quests targeting different achievement patterns
- **Locations**: Arena (craft/health), Observatory (growth), Commons (connection)

**Multi-Theme Strategy:**

Each theme can have completely different world_schema:

- **Modern**: Realistic locations (gym, library, café)
- **Medieval**: Fantasy locations (arena, guild hall, mystic tower)
- **Sci-Fi**: Futuristic locations (training deck, observatory, commons hall)

### Hidden Quests Trigger System

**From Tech Spec (tech-spec-epic-4.md, Hidden Quests Structure):**

Hidden quests use flexible trigger conditions evaluated by ARQ worker (Story 4.3):

**Trigger Types:**

1. **Streak-based**: `{"streak_days": 20, "attribute": "craft"}`
2. **Mission count**: `{"missions_completed": 100}`
3. **Balance**: `{"equal_value_distribution": 14}`  // Equal missions across all values for 14 days
4. **Time-based**: `{"missions_after_10pm": 30}`
5. **Reflection**: `{"reflection_notes_written": 50}`

**Reward Types:**

- `essence`: Currency for lore unlocking (Story 4.7)
- `title`: User title like "The Relentless"
- `relationship_boost`: Increase character relationship level
- `artifact`: Special item with lore_text

**Time Limits:**

- `time_limit_hours: null` → No time limit
- `time_limit_hours: 72` → Must complete within 72 hours of unlock

### Database Performance Considerations

**JSONB Indexing Strategy:**

```sql
-- Fast theme queries
CREATE INDEX idx_scenario_theme ON scenario_templates(theme);

-- Fast user queries
CREATE INDEX idx_narrative_user ON narrative_states(user_id);

-- Fast scenario lookups
CREATE INDEX idx_narrative_scenario ON narrative_states(scenario_id);

-- JSONB queries (if needed, add later):
-- CREATE INDEX idx_world_state_locations ON narrative_states USING GIN ((world_state->'locations'));
```

**Query Performance:**

- Scenario template queries: <10ms (small table, indexed)
- Narrative state queries: <50ms (JSONB parsing)
- World state updates: <100ms (JSONB update operation)

**Storage Estimates:**

- Scenario template: ~50-100KB per template (JSONB)
- Narrative state: ~10-50KB per user (grows with events)
- For 10K users: ~100-500MB total (very manageable)

### Learnings from Previous Stories

**From Story 2.1 (Memory Schema):**

- JSONB fields work well for flexible data
- Use `metadata` alias for JSONB (SQLAlchemy reserved keyword handling)
- GIN indexes for JSONB queries when needed
- Document JSONB structure thoroughly in code comments

**From Story 1.2 (Database Schema):**

- Alembic migrations with async SQLAlchemy 2.0 patterns
- UUID primary keys with gen_random_uuid()
- TIMESTAMP WITH TIME ZONE for all timestamps
- Foreign key ON DELETE CASCADE for user data cleanup

### Project Structure Notes

**New Files Created:**

```
packages/backend/
├── app/
│   ├── models/
│   │   └── narrative.py                    # NEW: ScenarioTemplate, NarrativeState models
│   ├── schemas/
│   │   └── narrative.py                    # NEW: Pydantic schemas for API
│   ├── db/
│   │   ├── migrations/
│   │   │   └── versions/
│   │   │       ├── XXX_add_scenario_templates_table.py    # NEW: Migration
│   │   │       └── XXX_add_narrative_states_table.py      # NEW: Migration
│   │   └── seeds/
│   │       └── scenario_templates.py       # NEW: Seed data for Modern Reality
└── tests/
    ├── models/
    │   └── test_narrative.py               # NEW: Model unit tests
    └── integration/
        └── test_scenario_seed.py           # NEW: Seed data validation
```

**Documentation Created:**

```
docs/
└── epic-4/
    └── NARRATIVE-STATE-SCHEMA.md           # NEW: Complete schema documentation
```

### Relationship to Epic 4 Stories

This story (4.1) **enables**:

- **Story 4.2 (Narrative Agent)**: Reads scenario templates, updates narrative state
- **Story 4.3 (Hidden Quests)**: Uses hidden_quests from templates, checks trigger conditions
- **Story 4.4 (Story UI)**: Displays narrative state (chapters, characters, items)
- **Story 4.6 (Branching Narratives)**: Stores user decisions in story_progress

**Dependencies Flow:**

```
Story 4.1 (Narrative Schema) ← THIS STORY
    ↓ (provides database foundation)
Story 4.2 (Narrative Agent)
    ↓ (generates story beats)
Story 4.3 (Hidden Quests)
    ↓ (unlocks surprises)
Story 4.4 (Story UI)
    = Living Narrative Experience! 📖
```

### References

**Source Documents:**

- **Epic 4 Tech Spec**: `docs/tech-spec-epic-4.md` (Complete schema design, lines 45-180)
- **Epics File**: `docs/epics.md` (Story 4.1 requirements, lines 912-990)
- **Architecture**: `docs/ARCHITECTURE.md` (Pattern 1: Living Narrative Engine, lines 300-401)
- **Architecture**: `docs/ARCHITECTURE.md` (JSONB decision, lines 1063-1085 ADR-006)

**Technical Documentation:**

- **PostgreSQL JSONB**: https://www.postgresql.org/docs/current/datatype-json.html
- **JSONB Functions**: https://www.postgresql.org/docs/current/functions-json.html
- **SQLAlchemy JSONB**: https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.JSON
- **Alembic Migrations**: https://alembic.sqlalchemy.org/en/latest/

---

## Definition of Done

- [ ] ✅ `scenario_templates` table created with all columns and index
- [ ] ✅ `narrative_states` table created with all columns and indexes
- [ ] ✅ SQLAlchemy models created: `ScenarioTemplate`, `NarrativeState`
- [ ] ✅ Helper methods implemented on models
- [ ] ✅ Pydantic schemas created for API responses
- [ ] ✅ Modern Reality scenario seeded with complete data:
  - 3 acts, 6 chapters with progression triggers
  - 3 character prompts (Lyra, Thorne, Elara)
  - 5 hidden quests with trigger conditions
  - Complete world_schema (locations, persons, items, event_types)
- [ ] ✅ JSONB structures documented in code and separate docs
- [ ] ✅ Consistency rules documented
- [ ] ✅ Unit tests pass for models and JSONB operations
- [ ] ✅ Integration tests pass for seed data validation
- [ ] ✅ Migration can be rolled back successfully
- [ ] ✅ No secrets committed
- [ ] ✅ Code follows async SQLAlchemy 2.0 patterns
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline

- **Task 1** (Scenario Templates Migration): 1 hour
- **Task 2** (Narrative States Migration): 1 hour
- **Task 3** (SQLAlchemy Models): 2 hours
- **Task 4** (Modern Reality Seed Data): 2.5 hours
- **Task 5** (Pydantic Schemas): 1 hour
- **Task 6** (Documentation): 1.5 hours
- **Task 7** (Unit Tests): 1 hour
- **Task 8** (Integration Tests): 1 hour

**Total:** 11 hours (within 8-10 hour estimate with efficient execution)

### Risk Mitigation

**Risk:** JSONB structure becomes too complex or inconsistent

- **Mitigation**: Clear documentation, JSON schema validation (optional), comprehensive examples
- **Impact**: Medium (can refactor JSONB structure in future migration)

**Risk:** Seed data has errors (invalid progression triggers, missing fields)

- **Mitigation**: Integration tests validate all seed data, manual review of Modern Reality scenario
- **Impact**: High (breaks story generation if triggers invalid)

**Risk:** World state grows too large (>1MB per user)

- **Mitigation**: Monitor world_state size, implement archiving strategy for old events if needed
- **Impact**: Low (JSONB handles large documents well, archiving is straightforward)

**Risk:** Multiple themes create schema inconsistencies

- **Mitigation**: Each theme defines its own world_schema, validation layer enforces schema
- **Impact**: Medium (isolated to specific scenarios)

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Create context file, then implement migrations, models, and seed data
