# Story 3.3: Build Mission/Quest System with Priority Triads

**Story ID:** 3.3
**Epic:** 3 - Goal & Mission Management
**Status:** drafted
**Priority:** P0 (Core Productivity Loop)
**Estimated Effort:** 14-16 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18
**Updated:** 2025-11-18

---

## User Story

**As a** user,
**I want** to see 3 prioritized missions each day,
**So that** I'm not overwhelmed and can choose what fits my current energy.

---

## Context

### Problem Statement

Long todo lists paralyze users. Seeing 47 pending tasks triggers analysis paralysis - "Where do I even start?" Story 3.3 implements Delight's core insight: **show 3 missions, not 30**.

The "priority triad" presents exactly 3 missions at a time:
- **High Priority**: Urgent + Important (deadline approaching, critical path)
- **Medium Priority**: Important but less urgent (significant progress, flexible timing)
- **Low Priority**: Easy win or exploratory (quick momentum, low energy needed)

This structure respects cognitive limits, reduces decision fatigue, and matches task to current energy state.

### Why This Approach?

**From Product Brief:**

The triad system implements research-backed principles:
- ✅ **Choice Architecture**: 3 options = manageable choice, prevents overwhelm
- ✅ **Energy Matching**: Users pick based on current state (tired → low energy quest)
- ✅ **Value Diversity**: Algorithm balances health/craft/growth/connection over time
- ✅ **Progress Visibility**: Completing 1 of 3 feels achievable, not 1 of 47

**From Architecture (ARCHITECTURE.md):**

Mission data model integrates with:
- Goals (Story 3.1): Missions link to parent goals via `goal_id` FK
- Memory (Story 2.2): Completed missions become task-tier memories
- Narrative (Epic 4): Mission completion unlocks narrative events

### Dependencies

- **Prerequisite Stories:**
  - 3.1 (Goal Data Models) ✅ Complete - Mission FK to goals
  - 3.2 (Goal Decomposition) ✅ Complete - Generated quests → missions

- **Epic 3 Context:** This story **enables**:
  - Story 3.4: Mission execution requires mission records
  - Story 3.5: Session notes link to mission sessions
  - Story 3.6: Quest generator creates new missions

- **External Dependencies:**
  - Clerk authentication for user_id
  - Database schema from Story 1.2

---

## Acceptance Criteria

### AC1: Mission Model Exists with Required Fields

**Given** the database migration is applied
**When** I inspect the database schema
**Then** a `missions` table exists with:

**Schema:**
- `id` (UUID, primary key)
- `goal_id` (UUID, FK to goals, nullable - missions can exist without goals)
- `user_id` (UUID, FK to users, not null)
- `title` (VARCHAR(200), not null)
- `description` (TEXT, nullable)
- `estimated_minutes` (INTEGER, not null, CHECK >= 5 AND <= 180)
- `energy_level` (VARCHAR(20), not null, CHECK: `low`, `medium`, `high`)
- `value_category` (VARCHAR(50), not null, CHECK: `health`, `craft`, `growth`, `connection`)
- `priority_score` (FLOAT, not null, default 0.0) - calculated by algorithm
- `status` (VARCHAR(20), not null, default `pending`, CHECK: `pending`, `in_progress`, `completed`, `deferred`, `archived`)
- `due_date` (DATE, nullable) - optional deadline
- `completed_at` (TIMESTAMP WITH TIME ZONE, nullable)
- `created_at` (TIMESTAMP WITH TIME ZONE, not null, default NOW())
- `updated_at` (TIMESTAMP WITH TIME ZONE, not null, default NOW())

**And** indexes exist on: `(user_id, status)`, `(user_id, priority_score DESC)`

### AC2: Priority Triad API Endpoint Returns 3 Missions

**Given** I have multiple pending missions
**When** I GET `/api/v1/missions/triad`
**Then** I receive exactly 3 missions:
- 1 high priority
- 1 medium priority
- 1 low priority (easy win)

**And** each mission includes:
- All mission fields (title, description, estimated_minutes, energy_level, value_category, priority_score)
- Parent goal details (if goal_id present): `{goal_id, goal_title, goal_type}`
- Time context: `due_date`, days until due

**And** the response indicates which tier each mission belongs to

**Response Example:**
```json
{
  "high_priority": {
    "id": "uuid1",
    "title": "Review chapter 5 for calculus midterm",
    "description": "...",
    "estimated_minutes": 30,
    "energy_level": "high",
    "value_category": "growth",
    "priority_score": 0.92,
    "due_date": "2025-11-20",
    "days_until_due": 2,
    "goal": {
      "id": "goal_uuid",
      "title": "Graduate early from Georgia Tech",
      "type": "concrete"
    },
    "status": "pending"
  },
  "medium_priority": { ... },
  "low_priority": { ... }
}
```

### AC3: Prioritization Algorithm Works Correctly

**Given** I have missions with varying attributes
**When** the triad endpoint calculates priority scores
**Then** the algorithm considers:

**Priority Factors:**
1. **Goal Importance** (30% weight): Abstract goals = higher weight (need more work)
2. **Urgency** (25% weight): Days until due_date (sooner = higher)
3. **Time Since Last Work** (20% weight): Goal hasn't been touched in 7 days = boost
4. **Energy Match** (15% weight): Current time of day vs. energy_level (morning = high energy tasks boosted)
5. **Value Diversity** (10% weight): If health missions completed recently, boost craft/growth/connection

**And** priority_score is normalized to 0.0-1.0 range

**Algorithm Pseudocode:**
```python
def calculate_priority_score(mission, user_context):
    score = 0.0

    # Goal Importance (30%)
    if mission.goal_type == "abstract":
        score += 0.30 * 1.0  # Full weight
    elif mission.goal_type == "concrete":
        score += 0.30 * 0.7  # Reduced weight
    else:
        score += 0.30 * 0.5  # No goal link

    # Urgency (25%)
    if mission.due_date:
        days_until_due = (mission.due_date - today).days
        urgency = max(0, 1 - (days_until_due / 30))  # 0 days = 1.0, 30+ days = 0.0
        score += 0.25 * urgency

    # Time Since Last Work (20%)
    days_since_last = get_days_since_last_mission_for_goal(mission.goal_id)
    recency_boost = min(1.0, days_since_last / 7)  # 7+ days = full boost
    score += 0.20 * recency_boost

    # Energy Match (15%)
    current_hour = datetime.now().hour
    energy_match = calculate_energy_match(current_hour, mission.energy_level)
    score += 0.15 * energy_match

    # Value Diversity (10%)
    recent_categories = get_recent_completed_categories(user_id, days=7)
    if mission.value_category not in recent_categories[:2]:  # Not in top 2 recent
        score += 0.10 * 1.0  # Full diversity boost

    return min(1.0, score)  # Cap at 1.0
```

### AC4: Triad Refreshes After Mission Status Changes

**Given** I've completed or deferred a mission from the current triad
**When** I request the triad again (GET `/api/v1/missions/triad`)
**Then** the triad updates with a new mission to replace the completed/deferred one

**And** the algorithm recalculates priority scores based on updated context

**And** I don't see the same missions repeatedly (completed/deferred missions excluded)

### AC5: Mission List API Endpoint Works

**Given** I have created missions
**When** I GET `/api/v1/missions`
**Then** I receive a paginated list of all my missions

**And** I can filter by:
- `status`: `pending`, `in_progress`, `completed`, `deferred`, `archived`
- `value_category`: `health`, `craft`, `growth`, `connection`
- `goal_id`: Show missions for specific goal
- `energy_level`: `low`, `medium`, `high`

**And** results are sorted by `priority_score DESC` by default

**Example Request:**
```bash
GET /api/v1/missions?status=pending&value_category=health&limit=20
```

### AC6: CRUD Operations Work for Missions

**Given** I'm authenticated
**When** I use mission endpoints
**Then** I can:

- **Create Mission**: `POST /api/v1/missions`
  - Manually create missions (in addition to generated ones from Story 3.2)
  - Title, description, estimated_minutes, energy_level, value_category required
  - goal_id optional (can have standalone missions)

- **Get Mission**: `GET /api/v1/missions/{id}`
  - Retrieve single mission details
  - Returns 404 if not found or belongs to another user

- **Update Mission**: `PATCH /api/v1/missions/{id}`
  - Update fields (title, description, estimated_minutes, energy_level, due_date)
  - Cannot update id, user_id, created_at

- **Defer Mission**: `POST /api/v1/missions/{id}/defer`
  - Changes status to `deferred` (removed from active triad)
  - Can specify defer_until date

- **Complete Mission**: `POST /api/v1/missions/{id}/complete`
  - Changes status to `completed`, sets `completed_at` timestamp
  - Handled primarily by Story 3.4, but endpoint exists

- **Archive Mission**: `DELETE /api/v1/missions/{id}`
  - Soft delete (status = `archived`)

### AC7: Frontend Mission Triad Component Displays Correctly

**Given** I'm logged in and have pending missions
**When** I navigate to the missions view (`/missions`)
**Then** I see 3 mission cards displayed as a triad

**And** each card shows:
- **Priority Badge**: "High Priority", "Important", or "Quick Win" (color-coded)
- **Title**: Clear, actionable task name
- **Estimated Time**: "15 min", "30 min", "1 hour" with clock icon
- **Energy Level**: Icon indicator (battery for low, lightning for high, etc.)
- **Value Category**: Icon (heart=health, paintbrush=craft, book=growth, people=connection)
- **Parent Goal**: "(part of: Graduate early)" if linked to goal
- **Due Date**: "Due in 2 days" if deadline exists

**And** each card has action buttons:
- **Start Mission** (primary CTA, routes to Story 3.4 mission executor)
- **Defer** (secondary, shows defer modal)
- **More Options** (dropdown: Edit, Archive)

### AC8: Mission Creation from Goal Decomposition Works

**Given** I've approved a goal decomposition (Story 3.2)
**When** the system converts generated_quests to missions
**Then** mission records are created with:

- Fields populated from quest data (title, description, estimated_minutes, energy_level)
- `goal_id` linked to parent goal
- `value_category` inherited from parent goal
- `status` set to `pending`
- `priority_score` calculated by algorithm
- Sequence preserved (quest with `sequence_order=1` created first)

**And** missions appear in the pending mission pool for triad selection

---

## Tasks / Subtasks

### Task 1: Create Database Migration (AC: #1)

- [ ] **1.1** Create migration: `alembic revision -m "create missions table"`
- [ ] **1.2** Define missions table schema with all fields
- [ ] **1.3** Add CHECK constraints for enums and value ranges
- [ ] **1.4** Add foreign keys with appropriate CASCADE rules
- [ ] **1.5** Add indexes: `(user_id, status)`, `(user_id, priority_score DESC)`, `(goal_id)`
- [ ] **1.6** Add trigger for auto-updating `updated_at` timestamp
- [ ] **1.7** Apply migration: `alembic upgrade head`

### Task 2: Create SQLAlchemy Model and Pydantic Schemas (AC: #1, #6)

- [ ] **2.1** Create `packages/backend/app/models/mission.py`
- [ ] **2.2** Define `Mission` model with all fields and relationships
- [ ] **2.3** Create `packages/backend/app/schemas/mission.py`
- [ ] **2.4** Define request/response schemas:
  - `MissionCreate`, `MissionUpdate`, `MissionResponse`
  - `MissionTriadResponse` (high/medium/low priority structure)
  - `MissionListResponse` with pagination

### Task 3: Implement Priority Calculation Algorithm (AC: #3)

- [ ] **3.1** Create `packages/backend/app/services/mission_priority_service.py`
- [ ] **3.2** Implement `calculate_priority_score()` method:
  - Goal importance factor (30%)
  - Urgency factor based on due_date (25%)
  - Time since last work on goal (20%)
  - Energy match to current time (15%)
  - Value diversity boost (10%)
- [ ] **3.3** Implement helper methods:
  - `get_days_since_last_mission_for_goal(goal_id)`
  - `calculate_energy_match(current_hour, energy_level)`
  - `get_recent_completed_categories(user_id, days=7)`
- [ ] **3.4** Add unit tests for priority calculation edge cases

### Task 4: Create Mission Service (AC: #2-#8)

- [ ] **4.1** Create `packages/backend/app/services/mission_service.py`
- [ ] **4.2** Implement `MissionService` class with methods:
  - `create_mission(user_id, mission_data)`: Create new mission
  - `get_user_missions(user_id, filters, pagination)`: List missions
  - `get_mission_by_id(user_id, mission_id)`: Single mission
  - `update_mission(user_id, mission_id, updates)`: Update mission
  - `defer_mission(user_id, mission_id, defer_until)`: Defer mission
  - `complete_mission(user_id, mission_id)`: Mark complete
  - `archive_mission(user_id, mission_id)`: Soft delete
  - `get_priority_triad(user_id)`: **Core method** - returns 3 missions
- [ ] **4.3** Implement `get_priority_triad()` logic:
  - Query all pending missions for user
  - Calculate priority score for each using `MissionPriorityService`
  - Sort by priority score descending
  - Select top mission as high priority
  - Select mid-range mission as medium priority
  - Select low-priority (or low energy) mission as low/easy win
  - Return structured triad response

### Task 5: Create Mission Conversion from Goal Decomposition (AC: #8)

- [ ] **5.1** Add method to `MissionService`:
  ```python
  async def create_missions_from_decomposition(
      self, user_id: str, goal_id: UUID, decomposition: GoalDecomposition
  ) -> list[Mission]:
      """Convert generated_quests from decomposition to mission records."""
      missions = []
      for quest in decomposition.generated_quests:
          mission = Mission(
              user_id=user_id,
              goal_id=goal_id,
              title=quest["title"],
              description=quest["description"],
              estimated_minutes=quest["estimated_minutes"],
              energy_level=quest["energy_level"],
              value_category=goal.value_category,  # Inherit from goal
              status="pending"
          )
          # Calculate initial priority score
          mission.priority_score = await priority_service.calculate_priority_score(mission)
          self.db.add(mission)
          missions.append(mission)
      await self.db.commit()
      return missions
  ```
- [ ] **5.2** Trigger mission creation after decomposition approval (Story 3.2)

### Task 6: Create API Endpoints (AC: #2, #4, #5, #6)

- [ ] **6.1** Create `packages/backend/app/api/v1/missions.py`
- [ ] **6.2** Implement endpoints:
  - `GET /missions/triad`: Get priority triad (3 missions)
  - `GET /missions`: List all missions with filters
  - `GET /missions/{id}`: Get single mission
  - `POST /missions`: Create mission manually
  - `PATCH /missions/{id}`: Update mission
  - `POST /missions/{id}/defer`: Defer mission
  - `POST /missions/{id}/complete`: Complete mission (Story 3.4 extends this)
  - `DELETE /missions/{id}`: Archive mission
- [ ] **6.3** Register router in API v1 module
- [ ] **6.4** Add Clerk authentication dependency to all endpoints

### Task 7: Create Frontend Mission Triad Component (AC: #7)

- [ ] **7.1** Create `packages/frontend/src/components/missions/MissionTriad.tsx`
- [ ] **7.2** Design triad layout:
  - 3-column grid on desktop, vertical stack on mobile
  - Visual distinction for high/medium/low priority (colors, badges)
- [ ] **7.3** Create `MissionCard.tsx` component:
  - Display all mission fields (title, time, energy, category, goal)
  - Priority badge with color coding
  - Action buttons (Start, Defer, More Options)
- [ ] **7.4** Create missions page: `packages/frontend/src/app/missions/page.tsx`
- [ ] **7.5** Implement mission list view (below triad):
  - Paginated list of all pending missions
  - Filters: status, category, goal, energy level
  - Sort options
- [ ] **7.6** Add API client methods in `lib/api/missions.ts`:
  - `getTriad()`, `getMissions()`, `createMission()`, `updateMission()`, `deferMission()`, `completeMission()`

### Task 8: Create Unit Tests (AC: All)

- [ ] **8.1** Create `tests/services/test_mission_service.py`
- [ ] **8.2** Test CRUD operations
- [ ] **8.3** Create `tests/services/test_mission_priority_service.py`
- [ ] **8.4** Test priority algorithm:
  - Goal importance factor
  - Urgency calculation
  - Time since last work
  - Energy matching
  - Value diversity
- [ ] **8.5** Test triad selection algorithm
- [ ] **8.6** Test mission creation from decomposition

### Task 9: Integration Tests (AC: All)

- [ ] **9.1** Create `tests/api/test_missions_api.py`
- [ ] **9.2** Test all API endpoints end-to-end
- [ ] **9.3** Test triad refresh after completion/defer
- [ ] **9.4** Test authorization (user can only access own missions)

### Task 10: Documentation (AC: All)

- [ ] **10.1** Document priority algorithm in code comments
- [ ] **10.2** Add API examples to `docs/API-TESTING-GUIDE.md`
- [ ] **10.3** Document mission lifecycle (created → pending → in_progress → completed)
- [ ] **10.4** Add docstrings to all service methods

---

## Dev Notes

### Priority Triad Selection Algorithm Details

**High Priority Mission:**
- Top 3 missions by priority_score
- Filter for: due_date within 7 days OR priority_score > 0.8
- Select highest scoring

**Medium Priority Mission:**
- Missions ranked 4-10 by priority_score
- Important but not urgent
- Good progress drivers without pressure

**Low Priority / Easy Win Mission:**
- Look for low energy missions (energy_level = "low")
- OR missions with estimated_minutes <= 15
- Provides quick momentum, reduces activation energy

**Edge Cases:**
- If <3 missions pending: Return what's available (1-2 missions)
- If no low-energy missions: Use lowest priority_score mission as easy win
- If all missions have same priority: Randomize to add variety

### Value Diversity Tracking

Track completed missions by value_category over rolling 7-day window:

```python
async def get_recent_completed_categories(user_id: str, days: int = 7) -> list[str]:
    """Get value categories of recently completed missions, most frequent first."""
    cutoff_date = datetime.now() - timedelta(days=days)
    result = await db.execute(
        select(Mission.value_category, func.count(Mission.id).label("count"))
        .where(
            and_(
                Mission.user_id == user_id,
                Mission.status == "completed",
                Mission.completed_at >= cutoff_date
            )
        )
        .group_by(Mission.value_category)
        .order_by(desc("count"))
    )
    return [row.value_category for row in result]
```

If user has completed 5 health missions, 2 craft missions in past week:
- Health missions get NO diversity boost (0.0)
- Craft missions get PARTIAL diversity boost (0.05)
- Growth/Connection missions get FULL diversity boost (0.10)

### Energy Level Matching

**Time-of-Day Energy Patterns (Default):**
- Morning (6am-12pm): High energy preferred (match = 1.0 for high, 0.7 for medium, 0.3 for low)
- Afternoon (12pm-6pm): Medium energy preferred (match = 0.7 for high, 1.0 for medium, 0.8 for low)
- Evening (6pm-12am): Low energy preferred (match = 0.3 for high, 0.7 for medium, 1.0 for low)
- Night (12am-6am): Low energy only (match = 0.0 for high, 0.3 for medium, 1.0 for low)

**Future Enhancement (Story 2.2 integration):**
- Query user's memory for personalized energy patterns
- Learn "I work best in the morning" → boost high energy tasks 6-10am for this user
- Detect crash times → avoid high energy missions during those hours

### Mission Status Lifecycle

```
pending → in_progress → completed
   ↓           ↓
deferred    deferred
   ↓           ↓
archived    archived
```

- **pending**: Available for selection in triad
- **in_progress**: User started mission (Story 3.4)
- **completed**: Mission finished, recorded in progress tracking
- **deferred**: User chose to skip for now (re-enters pending pool after defer_until date)
- **archived**: Soft deleted, excluded from queries (user changed mind, mission no longer relevant)

### Integration with Goal Decomposition (Story 3.2)

After user approves decomposition:

```python
# In Story 3.2 completion handler
decomposition = await goal_decomposition_service.create_decomposition(...)
missions = await mission_service.create_missions_from_decomposition(
    user_id=user_id,
    goal_id=goal_id,
    decomposition=decomposition
)
# Now user has mission pool ready for triads
```

This creates the initial mission pool. Story 3.6 (quest generator) will add more missions over time.

### References

**Source Documents:**
- **Epics File**: `docs/epics.md` (lines 722-762: Story 3.3 requirements)
- **Architecture**: `docs/ARCHITECTURE.md` (Mission service, priority systems)
- **Story 3.1**: Goal models (missions link to goals)
- **Story 3.2**: Goal decomposition (generates missions)

---

## Definition of Done

- [ ] ✅ `missions` table created with all fields and constraints
- [ ] ✅ `Mission` model and schemas created
- [ ] ✅ Priority calculation algorithm implemented and tested
- [ ] ✅ Mission service created with CRUD methods
- [ ] ✅ `get_priority_triad()` method working correctly
- [ ] ✅ Mission conversion from decomposition working
- [ ] ✅ All API endpoints implemented and tested
- [ ] ✅ Frontend mission triad component completed
- [ ] ✅ Mission cards display all required information
- [ ] ✅ Triad refreshes after status changes
- [ ] ✅ Authorization enforced (users see only their missions)
- [ ] ✅ Unit tests with 80%+ coverage
- [ ] ✅ Integration tests validate full flow
- [ ] ✅ All acceptance criteria verified
- [ ] ✅ Documentation complete
- [ ] ✅ Story status updated to `done` in sprint-status.yaml

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Implement tasks 1-10, test priority algorithm, validate triad selection
