# Epic 3: Goal & Mission Management

**Epic Goal:** Enable users to create ambitious goals, decompose them collaboratively with Eliza, and work through adaptive micro-missions that respect their energy and time constraints.

**Architecture Components:** Mission service, PostgreSQL models, quest generation worker (ARQ), priority triage system

### Story 3.1: Create Goal Data Models and CRUD APIs

As a **user**,  
I want **to create and manage long-term goals**,  
So that **I have a clear vision of what I'm working toward**.

**Acceptance Criteria:**

**Given** I'm logged in  
**When** I create a new goal  
**Then** the goal is stored with:

- Title and description
- Goal type (abstract/concrete, MVP distinction)
- Value category (health/craft/growth/connection)
- Target completion date (optional)
- Status (active/paused/completed/archived)

**And** I can perform CRUD operations:

- `POST /api/v1/goals` - Create goal
- `GET /api/v1/goals` - List my goals
- `GET /api/v1/goals/{id}` - Get goal details
- `PATCH /api/v1/goals/{id}` - Update goal
- `DELETE /api/v1/goals/{id}` - Archive goal

**And** goals are linked to my user account

**Prerequisites:** Story 1.3 (authentication)

**Technical Notes:**

- Model: `backend/app/models/goal.py`
- Schema: `goals` table (id, user_id FK, title, description, goal_type, value_category, target_date, status, created_at, updated_at)
- Service: `backend/app/services/goal_service.py`
- Value categories align with Product Brief persona needs

---

### Story 3.2: Implement Collaborative Goal Decomposition with Eliza

As a **user**,  
I want **Eliza to help me break down big goals into actionable steps**,  
So that **abstract ambitions become concrete plans**.

**Acceptance Criteria:**

**Given** I've created a goal  
**When** I ask Eliza to help me plan  
**Then** Eliza initiates a collaborative decomposition conversation:

- Asks clarifying questions about my "why"
- Explores constraints (time, resources, dependencies)
- Proposes 3-7 milestone steps

**And** Eliza generates suggested micro-quests:

- Each quest is small (10-30 minutes)
- Quests are sequenced logically
- Energy/time estimates included

**And** I can approve, modify, or reject suggestions

**And** approved quests are saved as missions linked to the goal

**Prerequisites:** Story 2.4 (Eliza chat), Story 3.1 (goal models)

**Technical Notes:**

- Extend Eliza agent with goal decomposition node
- Use structured output parsing for quest suggestions
- Store decomposition in `goal_decompositions` table (goal_id FK, milestones JSONB, generated_quests JSONB)
- Frontend: modal or dedicated page for goal planning session

---

### Story 3.3: Build Mission/Quest System with Priority Triads

As a **user**,  
I want **to see 3 prioritized missions each day**,  
So that **I'm not overwhelmed and can choose what fits my current energy**.

**Acceptance Criteria:**

**Given** I have multiple active goals with missions  
**When** I open the missions view  
**Then** I see 3 missions presented as a "priority triad":

- High priority (urgent + important)
- Medium priority (important, less urgent)
- Low priority (easy win or exploratory)

**And** each mission shows:

- Title and description
- Estimated time (10min, 30min, 1hr)
- Energy level (low/medium/high)
- Value category icon (health/craft/growth/connection)
- Parent goal

**And** I can:

- Choose one mission to start
- Defer a mission to later
- Mark mission as completed

**And** the triad refreshes when I complete or defer missions

**Prerequisites:** Story 3.2 (missions generated)

**Technical Notes:**

- Model: `backend/app/models/mission.py`
- Schema: `missions` table (id, goal_id FK, user_id FK, title, description, estimated_minutes, energy_level, value_category, priority_score, status, created_at, completed_at)
- Prioritization algorithm considers: goal importance, time since last work, energy match, value diversity
- Frontend component: `MissionTriad.tsx`

---

### Story 3.4: Implement Mission Execution Flow with Timer

As a **user**,  
I want **to work on a mission with a gentle timer and focus support**,  
So that **I stay on track without feeling pressured**.

**Acceptance Criteria:**

**Given** I've selected a mission to work on  
**When** I start the mission  
**Then** a timer begins based on estimated duration

**And** the UI shows:

- Mission details prominently
- Timer (optional to hide)
- "I'm done" button (can complete early)
- "Extend time" option if I need more

**And** when the timer ends:

- Gentle notification (no aggressive alarm)
- Prompt to mark as complete or extend
- Option to log actual time spent

**And** when I complete the mission:

- Celebration animation
- Streak updated (if applicable)
- Eliza offers encouragement
- Next mission suggestion appears

**Prerequisites:** Story 3.3 (mission triads)

**Technical Notes:**

- Frontend: `MissionExecutor.tsx` component
- Store session data in `mission_sessions` table (mission_id FK, started_at, completed_at, actual_minutes, notes)
- Use browser timer (Notification API for gentle alerts)
- Post-completion: update mission status, trigger analytics event

---

### Story 3.5: Add Mission Session Notes and Reflection

As a **user**,  
I want **to capture quick notes during or after a mission**,  
So that **I can track learnings and progress details**.

**Acceptance Criteria:**

**Given** I'm working on or just completed a mission  
**When** I add notes  
**Then** notes are saved to the mission session

**And** notes become memory entries:

- Stored in task-tier memory (30-day retention)
- Eliza can recall them in future conversations

**And** I can view past mission notes:

- In mission history
- In goal progress view

**Prerequisites:** Story 3.4 (mission execution), Story 2.2 (memory service)

**Technical Notes:**

- Add `notes` TEXT field to `mission_sessions` table
- Automatically create task memory from notes after mission completion
- Frontend: expandable text area in mission completion modal

---

### Story 3.6: Implement Adaptive Quest Generation Worker (Future)

As a **user**,  
I want **new missions to be generated automatically based on my patterns**,  
So that **I don't run out of things to work on**.

**Acceptance Criteria:**

**Given** I'm actively working on goals  
**When** my mission queue drops below 5 pending missions  
**Then** ARQ worker triggers quest generation

**And** the worker:

- Analyzes my completion patterns (time of day, duration, value categories)
- Queries Eliza agent for new quest ideas
- Generates 3-5 new missions aligned with active goals
- Prioritizes based on goal deadlines and value diversity

**And** generated missions appear in my mission pool

**Prerequisites:** Story 3.3 (missions), Story 2.3 (Eliza agent)

**Technical Notes:**

- Worker: `backend/app/workers/quest_generator.py`
- Schedule: runs nightly + on-demand when queue low
- Uses LangGraph agent with goal context and user patterns
- Ensures diversity: don't generate all missions for one goal

---

### Story 3.7: Add Collaborative Goals and Guild Missions (Future)

As a **user**,  
I want **to work on goals with friends or accountability pods**,  
So that **we support each other and share progress**.

**Acceptance Criteria:**

**Given** I'm in an accountability pod or guild  
**When** we create a shared goal  
**Then** all pod members can:

- See the shared goal
- Contribute missions toward it
- View each other's progress
- Celebrate milestones together

**And** guild missions are available:

- Special quests that require multiple people
- Reward points go to the guild
- Unlocks shared rewards or lore

**Prerequisites:** Story 3.3 (missions), Future multiplayer system

**Technical Notes:**

- Schema: `shared_goals` table (goal_id FK, pod_id FK, member_contributions JSONB)
- Schema: `pods` table (id, name, members ARRAY, created_at)
- Requires notification system to alert pod members
- Future Epic 6 (world/multiplayer) dependency

---
