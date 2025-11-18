# Epic 4: Narrative Engine

**Epic Goal:** Create a living narrative system that generates personalized stories adapting to real-world user progress, with pre-planned hidden quests that unlock based on achievements.

**Architecture Components:** Narrative service, LangGraph narrative agent, PostgreSQL JSONB for scenario templates, ARQ worker for quest unlocking

### Story 4.1: Create Comprehensive Narrative State Schema and Scenario Templates

**⚠️ COMPREHENSIVE SYSTEM:** This narrative state must be far more extensive than typical story systems - it tracks the entire world state including locations, events, persons, and items.

As a **developer**,  
I want **a flexible, comprehensive schema for narrative scenarios and dynamic world state**,  
So that **we can support multiple themes and maintain story consistency across all narrative elements**.

**Acceptance Criteria:**

**Given** the database is set up  
**When** I create narrative infrastructure  
**Then** the following tables exist:

- `scenario_templates` (id, name, theme, narrative_arc JSONB, character_prompts JSONB, hidden_quests JSONB, time_rules JSONB, world_schema JSONB)
- `narrative_states` (id, user_id FK, scenario_id FK, current_chapter INT, unlocked_quests ARRAY, story_progress JSONB, world_state JSONB, created_at, updated_at)

**And** the `world_state` JSONB tracks comprehensive narrative elements:

```json
{
  "locations": {
    "arena": {
      "discovered": true,
      "description": "...",
      "npcs_present": ["Lyra", "Thorne"]
    },
    "observatory": { "discovered": false, "unlock_condition": "..." }
  },
  "events": [
    {
      "event_id": "first_meeting_lyra",
      "occurred_at": "2025-11-01",
      "impact": "relationship+1"
    }
  ],
  "persons": {
    "Lyra": {
      "relationship_level": 3,
      "last_interaction": "...",
      "knows_about": ["user_craft_goals"]
    },
    "Thorne": { "relationship_level": 1, "status": "neutral" }
  },
  "items": {
    "essence": 450,
    "titles": ["The Persistent", "The Relentless"],
    "artifacts": [
      { "id": "medallion_of_craft", "acquired_at": "...", "description": "..." }
    ]
  },
  "world_time": {
    "current_act": 1,
    "current_chapter": 3,
    "days_in_story": 45
  }
}
```

**And** at least one comprehensive scenario template is seeded:

- **Modern Reality**: Contemporary alter-ego journey with realistic characters
- Defines 3 acts with progression triggers
- Includes 3-5 hidden quest templates
- Defines all possible locations, persons, items, and event types

**And** scenario templates support multiple themes (medieval, sci-fi, etc.) for future expansion

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- See Architecture doc Pattern 1 (Living Narrative Engine) for schema details
- JSONB structure allows flexibility without schema migrations for new scenarios
- **World State Management:** Each narrative generation reads and updates world_state
- **Consistency Enforcement:** Narrative agent validates all changes against scenario template rules
- Index on `narrative_states.user_id` and `scenario_templates.theme`
- Seed script: `backend/app/db/seeds/scenario_templates.py`
- **Critical:** World state must prevent inconsistencies (e.g., can't reference items not yet acquired, locations not yet discovered)

---

### Story 4.2: Build Narrative Generation Agent with LangGraph

As a **developer**,  
I want **an AI agent that generates personalized story beats**,  
So that **users experience adaptive narratives tied to their real actions**.

**Acceptance Criteria:**

**Given** the scenario templates exist  
**When** I initialize the narrative agent  
**Then** the agent is a LangGraph state machine with nodes:

- `assess_progress`: Analyzes user mission completions, streaks, value focus
- `select_beat`: Chooses appropriate story beat based on progress
- `generate_content`: LLM creates personalized narrative text
- `check_unlocks`: Determines if hidden quests should unlock

**And** the agent uses:

- Scenario template context
- User's mission history
- Current chapter/act state
- Character relationship levels

**And** generated content includes:

- Story text (200-400 words)
- Emotional tone
- Character dialogue
- Optional quest unlock

**Prerequisites:** Story 4.1 (narrative schema), Story 2.3 (LangGraph setup)

**Technical Notes:**

- Agent: `backend/app/agents/narrative_agent.py`
- Uses scenario template as base context
- Incorporates real user data (goals, completed missions, streaks)
- **LLM:** OpenAI GPT-4o (premium model for high-quality narrative writing)
  - Cost: $2.50/$10 per 1M tokens (input/output)
  - Rationale: Narrative generation requires superior writing quality and story consistency
  - Less frequent than chat interactions (~2-3 story beats per week per user)
  - Budget impact: ~$0.02/user/day (within $0.50 target)
- **Story Consistency Priority:** Most important theme - ensure no inconsistent values, items, or events
  - Agent maintains strict adherence to scenario template rules
  - Validates against previous story beats before generation
  - Tracks all narrative elements (locations, items, events, character states) in JSONB
- Output format: structured JSON with text, metadata, unlock flags

---

### Story 4.3: Implement Pre-Planned Hidden Quest System

As a **user**,  
I want **to discover surprise quests that unlock when I hit milestones**,  
So that **my journey feels rewarding and full of delightful discoveries**.

**Acceptance Criteria:**

**Given** I'm working through my story  
**When** I complete a trigger condition (e.g., 20-day streak, 50 missions)  
**Then** a hidden quest unlocks

**And** I receive a notification:

- In-app alert with story context
- Message from Eliza explaining the quest
- Quest appears in my mission pool marked as "Special"

**And** hidden quests have:

- Unique rewards (Essence points, titles, relationship boosts)
- Narrative significance (advances story arc)
- Time limits (optional, creates urgency)

**And** the ARQ worker checks trigger conditions:

- Runs nightly
- Checks all active users' progress against scenario hidden_quests
- Unlocks quests when conditions met

**Prerequisites:** Story 4.1 (narrative schema), Story 3.3 (missions)

**Technical Notes:**

- Worker: `backend/app/workers/quest_generator.py` (extend for hidden quests)
- Trigger examples: `{"streak_days": 20, "attribute": "craft"}`, `{"missions_completed": 50}`
- Store unlocked quests in `narrative_states.unlocked_quests` ARRAY
- Frontend: special UI treatment for hidden/special quests

---

### Story 4.4: Create Story Viewing Interface (MVP)

As a **user**,  
I want **to read my personalized story as it unfolds**,  
So that **I feel like my efforts are building toward something meaningful**.

**Acceptance Criteria:**

**Given** narrative content has been generated  
**When** I open the story view  
**Then** I see:

- Current chapter/act title
- Latest story beat (newest at top)
- Previous beats in chronological order
- Visual indicators for act progression

**And** the interface feels immersive:

- Beautiful typography (serif font for story text)
- Theme-appropriate styling (based on scenario)
- Fade-in animations for new beats
- Option to listen (text-to-speech, future)

**And** I can:

- Navigate between chapters
- Bookmark favorite moments
- Share story highlights (opt-in)

**Prerequisites:** Story 4.2 (narrative generation)

**Technical Notes:**

- Frontend: `frontend/src/app/narrative/page.tsx`
- Component: `StoryBeat.tsx`, `ChapterNav.tsx`
- API: `GET /api/v1/narrative/story` returns all story beats
- Use Framer Motion for smooth transitions
- Store read progress in session

---

### Story 4.5: Implement Character-Initiated Story Events (Future)

As a **user**,  
I want **characters to reach out to me with story developments**,  
So that **the narrative feels alive and characters have agency**.

**Acceptance Criteria:**

**Given** I've progressed through several story chapters  
**When** a narrative trigger occurs  
**Then** a character initiates contact:

- Push notification or email (if opted in)
- In-app message: "Lyra has a message for you"
- Character shares story development when I open

**And** character-initiated events include:

- Story revelations
- Relationship milestones
- Warnings or advice
- Celebration of achievements

**And** events are scheduled strategically:

- Based on optimal engagement times
- Not during user-designated quiet hours
- Spaced appropriately (not spammy)

**Prerequisites:** Story 4.2 (narrative agent), Story 2.7 (character personas), Story 7.2 (nudge system)

**Technical Notes:**

- Worker: `backend/app/workers/character_initiator.py`
- Uses nudge system infrastructure (Epic 7)
- Stores pending events in `narrative_events` table
- Frontend: special treatment for character-initiated messages in companion interface

---

### Story 4.6: Add Branching Narratives Based on User Choices (Future)

As a **user**,  
I want **my choices to influence the story direction**,  
So that **the narrative feels personalized and consequential**.

**Acceptance Criteria:**

**Given** I'm at a story decision point  
**When** Eliza or another character presents choices  
**Then** I can select from 2-3 meaningful options:

- Different value focus (health vs craft vs growth)
- Risk vs safety approach
- Solo vs collaborative path

**And** my choice:

- Is stored in narrative state
- Influences future story beats
- Affects character relationships
- May unlock different hidden quests

**And** the narrative agent:

- Tracks decision history
- Generates content consistent with past choices
- Creates story coherence across branches

**Prerequisites:** Story 4.2 (narrative agent), Story 4.4 (story interface)

**Technical Notes:**

- Extend scenario templates with branch points
- Store choices in `narrative_states.story_progress.decisions` JSONB
- Narrative agent queries decision history when generating beats
- Frontend: choice modal with consequence preview

---

### Story 4.7: Implement Lore Economy and Unlockable Content (Future)

As a **user**,  
I want **to unlock deeper lore and world-building through consistent effort**,  
So that **long-term commitment feels rewarding beyond just streaks**.

**Acceptance Criteria:**

**Given** I've been consistent for weeks/months  
**When** I earn Essence points (narrative currency)  
**Then** I can unlock:

- Extended character backstories
- World history codex entries
- Alternate scenario themes
- Cosmetic customizations (avatars, themes)

**And** lore is presented beautifully:

- Codex interface with categories
- Illustrated entries (future: AI-generated art)
- Audio narration (future)

**And** Essence is earned through:

- Hidden quest completions
- Streak milestones
- Goal achievements
- Story chapter completions

**Prerequisites:** Story 4.3 (hidden quests), Story 5.1 (progress tracking)

**Technical Notes:**

- Schema: `lore_entries` table (id, scenario_id FK, category, title, content, unlock_cost, rarity)
- Schema: `user_unlocks` table (user_id FK, lore_entry_id FK, unlocked_at)
- Track Essence in `user_preferences.essence_balance`
- Frontend: codex interface similar to game wikis

---
