# Story 3.4: Implement Mission Execution Flow with Timer

**Story ID:** 3.4
**Epic:** 3 - Goal & Mission Management
**Status:** drafted
**Priority:** P0 (Core Productivity Loop)
**Estimated Effort:** 10-12 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18
**Updated:** 2025-11-18

---

## User Story

**As a** user,
**I want** to work on a mission with a gentle timer and focus support,
**So that** I stay on track without feeling pressured.

---

## Context

### Problem Statement

Mission selection (Story 3.3) gets users to the starting line. Story 3.4 helps them cross the finish line with a supportive execution experience that:
- **Gentle Timer**: Awareness without anxiety (not a countdown bomb)
- **Early Completion**: "I'm done" button respects actual completion time
- **Time Extension**: Flexibility when tasks run long
- **Celebration**: Positive reinforcement builds momentum

The execution flow transforms "I should do this" into "I DID this."

### Why This Approach?

**From Product Brief:**

Traditional productivity apps use aggressive timers (BEEP! TIME'S UP!). Delight uses gentle notifications because:
- ✅ **Reduces Anxiety**: Soft nudges, not alarms
- ✅ **Respects Reality**: Tasks don't always fit estimates
- ✅ **Celebrates Progress**: Completion animation = dopamine hit
- ✅ **Momentum Building**: Eliza's encouragement → next mission suggestion

**From Architecture:**

Browser-based timer (no backend complexity) with:
- Notification API for gentle alerts
- Local storage for session persistence (if user refreshes mid-mission)
- `mission_sessions` table tracks actual time spent vs. estimated

---

## Acceptance Criteria

### AC1: Mission Executor Component Displays Mission Details

**Given** I click "Start Mission" from the triad (Story 3.3)
**When** the mission executor view opens
**Then** I see:

**Mission Details (Prominent):**
- Title (large, readable)
- Description (expandable if long)
- Estimated time with icon
- Energy level indicator
- Value category icon
- Parent goal (if linked): "Part of: [goal title]"

**Timer Display:**
- Countdown or count-up timer (user preference)
- Progress bar showing time elapsed
- Optional to hide/minimize timer (reduces pressure)

**Action Buttons:**
- **I'm Done** (primary CTA, always visible)
- **Extend Time** (+5 min, +10 min, +15 min quick options)
- **Pause** (stops timer, mission remains in_progress)
- **Abandon** (returns to triad, mission back to pending - confirms first)

### AC2: Timer Starts Automatically When Mission Begins

**Given** I start a mission
**When** the executor loads
**Then** the timer begins counting based on `estimated_minutes`

**And** mission status changes to `in_progress` (API call)

**And** a `mission_session` record is created with:
- `mission_id` (FK)
- `user_id`
- `started_at` (timestamp)
- `estimated_minutes` (from mission)
- `actual_minutes` (null until completion)
- `status` (`in_progress`)

### AC3: Gentle Notification When Timer Ends

**Given** the timer reaches the estimated duration
**When** time expires
**Then** a gentle notification appears:

**Notification Content:**
- ✨ Soft visual indicator (pulsing glow, not flashing red)
- 🔔 Optional browser notification (if permission granted): "Time's up! Ready to mark this complete?"
- **No aggressive sounds** (no alarms, beeps, or urgent noises)
- Timer continues counting (shows overtime: "+5 min")

**And** the "I'm Done" button is highlighted/pulsing

**And** user can:
- Mark complete immediately
- Extend time (adds to timer, resets notification)
- Continue working (timer keeps running, no interruption)

### AC4: Early Completion Works

**Given** I finish before the estimated time
**When** I click "I'm Done"
**Then** the mission is marked complete immediately

**And** actual time spent is recorded (started_at to now)

**And** I see the completion flow (AC5)

**Example:**
- Estimated: 30 minutes
- Started: 10:00 AM
- Completed: 10:20 AM
- Actual time: 20 minutes (saved to mission_session)

### AC5: Completion Flow Celebrates Success

**Given** I mark a mission as complete
**When** the completion API call succeeds
**Then** I see a celebration sequence:

**Celebration Elements:**
1. **Animation**: Confetti or particle effect (Framer Motion)
2. **Progress Update**:
   - Streak updated (if applicable - Story 5.1 integration)
   - Mission count: "15 missions completed this week!"
   - Goal progress: "3 of 10 milestones done" (if linked to goal)
3. **Eliza's Encouragement**: Quick message
   - "Nice work! You're building momentum 💪"
   - "That's your 3rd mission this week - you're crushing it!"
   - Personalized based on context (memory integration)
4. **Next Suggestion**: Show next mission from triad
   - "Ready for another? Here's a quick one: [low-priority mission]"
   - "Take a break" option (dismisses, returns to dashboard)

**And** mission status changes to `completed`

**And** `completed_at` timestamp recorded

**And** `mission_session` updated with:
- `actual_minutes` calculated
- `status` = `completed`

### AC6: Time Extension Works Smoothly

**Given** I need more time for the mission
**When** I click "Extend Time"
**Then** I see quick options:
- +5 minutes
- +10 minutes
- +15 minutes
- Custom (input field)

**And** when I select an extension, the timer adjusts

**And** the extension is logged in `mission_session.time_extensions` JSONB:
```json
{
  "time_extensions": [
    {"added_minutes": 10, "timestamp": "2025-11-18T10:30:00Z", "reason": "user_requested"}
  ]
}
```

**And** notification is reset (won't trigger until new extended time)

### AC7: Pause and Resume Works

**Given** I need to step away mid-mission
**When** I click "Pause"
**Then** the timer stops counting

**And** mission status remains `in_progress` (not back to pending)

**And** pause timestamp is recorded

**When** I click "Resume"
**Then** timer continues from where it paused

**And** total pause time is tracked (excluded from actual_minutes calculation)

### AC8: Session Persistence Works Across Page Refreshes

**Given** I'm working on a mission and refresh the page
**When** the page reloads
**Then** the mission executor state is restored:

- Mission details displayed
- Timer continues from last known state
- Elapsed time is calculated correctly (started_at to now, minus pauses)
- In-progress status preserved

**Implementation:** Use localStorage or React Query cache to store:
- `mission_id`
- `session_id`
- `started_at`
- `pause_timestamps` array

### AC9: Abandon Mission Confirmation Works

**Given** I decide not to complete a mission mid-execution
**When** I click "Abandon"
**Then** I see a confirmation dialog:
- "Are you sure you want to abandon this mission?"
- "Your progress won't be saved."
- **Confirm Abandon** / **Cancel** buttons

**When** I confirm
**Then** mission status returns to `pending`

**And** mission_session status set to `abandoned`

**And** I return to the missions triad view

---

## Tasks / Subtasks

### Task 1: Create Mission Session Database Schema (AC: #2, #5, #6, #7, #9)

- [ ] **1.1** Create migration: `alembic revision -m "create mission_sessions table"`
- [ ] **1.2** Define `mission_sessions` table:
  ```sql
  CREATE TABLE mission_sessions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
      user_id VARCHAR NOT NULL REFERENCES users(clerk_user_id),
      started_at TIMESTAMP WITH TIME ZONE NOT NULL,
      completed_at TIMESTAMP WITH TIME ZONE,
      estimated_minutes INTEGER NOT NULL,
      actual_minutes INTEGER,  -- Calculated on completion
      pause_timestamps JSONB DEFAULT '[]'::jsonb,  -- [{paused_at, resumed_at}]
      time_extensions JSONB DEFAULT '[]'::jsonb,   -- [{added_minutes, timestamp}]
      notes TEXT,  -- Story 3.5 adds note-taking
      status VARCHAR(20) NOT NULL DEFAULT 'in_progress',  -- in_progress, completed, abandoned
      created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
  );
  CREATE INDEX idx_sessions_mission ON mission_sessions(mission_id);
  CREATE INDEX idx_sessions_user ON mission_sessions(user_id);
  ```
- [ ] **1.3** Apply migration

### Task 2: Create SQLAlchemy Model and Schemas (AC: All)

- [ ] **2.1** Create `app/models/mission_session.py`
- [ ] **2.2** Define `MissionSession` model
- [ ] **2.3** Create `app/schemas/mission_session.py`
- [ ] **2.4** Define schemas: `MissionSessionCreate`, `MissionSessionUpdate`, `MissionSessionResponse`

### Task 3: Create Mission Session Service (AC: #2, #5, #6, #7, #9)

- [ ] **3.1** Create `app/services/mission_session_service.py`
- [ ] **3.2** Implement methods:
  - `start_session(mission_id, user_id)`: Create session, mark mission in_progress
  - `complete_session(session_id, actual_minutes)`: Mark complete, update mission
  - `pause_session(session_id)`: Record pause timestamp
  - `resume_session(session_id)`: Record resume timestamp
  - `extend_session(session_id, added_minutes)`: Log extension
  - `abandon_session(session_id)`: Mark abandoned, reset mission to pending
  - `get_active_session(user_id)`: Get current in_progress session (for restoration)

### Task 4: Update Mission API Endpoints (AC: #2, #5)

- [ ] **4.1** Update `app/api/v1/missions.py`
- [ ] **4.2** Add session management endpoints:
  - `POST /missions/{id}/start`: Start session
  - `POST /sessions/{id}/complete`: Complete session
  - `POST /sessions/{id}/pause`: Pause timer
  - `POST /sessions/{id}/resume`: Resume timer
  - `POST /sessions/{id}/extend`: Extend time
  - `POST /sessions/{id}/abandon`: Abandon mission
  - `GET /sessions/active`: Get active session for current user

### Task 5: Create Mission Executor Frontend Component (AC: #1, #2, #3, #4, #5, #6, #7, #8, #9)

- [ ] **5.1** Create `packages/frontend/src/components/missions/MissionExecutor.tsx`
- [ ] **5.2** Implement timer logic:
  - Browser-based countdown/countup timer
  - useEffect hook for timer updates (every second)
  - Calculate time remaining or overtime
- [ ] **5.3** Implement gentle notification:
  - Visual indicator when time expires (pulsing, glow effect)
  - Request browser notification permission
  - Send notification with Notification API
  - No aggressive sounds
- [ ] **5.4** Implement UI elements:
  - Mission details display
  - Timer display (large, readable)
  - Progress bar
  - Action buttons (Done, Extend, Pause, Abandon)
- [ ] **5.5** Handle early completion (AC4)
- [ ] **5.6** Implement time extension modal (AC6)
- [ ] **5.7** Implement pause/resume functionality (AC7)
- [ ] **5.8** Add session persistence (localStorage or React Query) (AC8)
- [ ] **5.9** Add abandon confirmation dialog (AC9)

### Task 6: Create Completion Celebration Component (AC: #5)

- [ ] **6.1** Create `packages/frontend/src/components/missions/MissionCompletionCelebration.tsx`
- [ ] **6.2** Implement celebration sequence:
  - Confetti animation (use `react-confetti` or Framer Motion particles)
  - Progress stats display
  - Eliza's encouragement message (query from backend)
  - Next mission suggestion
- [ ] **6.3** Add Eliza encouragement API:
  - `POST /api/v1/companion/encourage` with mission context
  - Returns personalized message based on memory
- [ ] **6.4** Add "Take a Break" vs. "Next Mission" options

### Task 7: Create Mission Executor Page Route (AC: All)

- [ ] **7.1** Create `packages/frontend/src/app/missions/[id]/execute/page.tsx`
- [ ] **7.2** Route from triad "Start Mission" button to `/missions/{id}/execute`
- [ ] **7.3** Fetch mission details on page load
- [ ] **7.4** Restore active session if refreshed (AC8)
- [ ] **7.5** Handle navigation away (warn if mission in progress)

### Task 8: Add Browser Notification Permission Request (AC: #3)

- [ ] **8.1** Add notification permission request on first mission start
- [ ] **8.2** Store permission preference in user settings
- [ ] **8.3** Gracefully degrade if permission denied (visual-only notifications)

### Task 9: Create Unit Tests (AC: All)

- [ ] **9.1** Test `MissionSessionService` methods
- [ ] **9.2** Test time calculations (actual_minutes with pauses/extensions)
- [ ] **9.3** Test session state transitions

### Task 10: Integration Tests (AC: All)

- [ ] **10.1** Test full execution flow:
  - Start → Wait → Complete
  - Start → Pause → Resume → Complete
  - Start → Extend → Complete
  - Start → Abandon
- [ ] **10.2** Test session restoration after page refresh

### Task 11: Documentation (AC: All)

- [ ] **11.1** Document timer implementation
- [ ] **11.2** Document session persistence strategy
- [ ] **11.3** Add user guide for mission execution

---

## Dev Notes

### Timer Implementation Details

**Browser-Based Timer:**
```typescript
const [timeElapsed, setTimeElapsed] = useState(0); // seconds
const [isPaused, setIsPaused] = useState(false);

useEffect(() => {
  if (isPaused) return;

  const interval = setInterval(() => {
    setTimeElapsed(prev => prev + 1);
  }, 1000);

  return () => clearInterval(interval);
}, [isPaused]);

const estimatedSeconds = mission.estimated_minutes * 60;
const timeRemaining = estimatedSeconds - timeElapsed;
const isOvertime = timeRemaining < 0;
```

**Gentle Notification:**
```typescript
// When timer expires
if (timeRemaining === 0 && !notificationShown) {
  // Visual notification (always shown)
  setShowGentleNotification(true);

  // Browser notification (if permitted)
  if (Notification.permission === "granted") {
    new Notification("Mission Time Complete ✨", {
      body: "Ready to mark this mission as complete?",
      icon: "/icons/mission-complete.png",
      silent: true,  // No sound!
    });
  }

  setNotificationShown(true);
}
```

### Actual Time Calculation

```python
def calculate_actual_minutes(session: MissionSession) -> int:
    """Calculate actual work time, excluding pauses."""
    total_elapsed = (session.completed_at - session.started_at).total_seconds() / 60

    # Subtract pause durations
    pause_total = 0
    for pause in session.pause_timestamps:
        if "paused_at" in pause and "resumed_at" in pause:
            paused = datetime.fromisoformat(pause["paused_at"])
            resumed = datetime.fromisoformat(pause["resumed_at"])
            pause_total += (resumed - paused).total_seconds() / 60

    actual_minutes = total_elapsed - pause_total
    return round(actual_minutes)
```

### Session Persistence Strategy

Store in localStorage:
```typescript
interface SessionState {
  missionId: string;
  sessionId: string;
  startedAt: string;  // ISO timestamp
  pauseTimestamps: Array<{pausedAt: string, resumedAt?: string}>;
}

// Save on state changes
localStorage.setItem('active_mission_session', JSON.stringify(sessionState));

// Restore on page load
const restored = localStorage.getItem('active_mission_session');
if (restored) {
  const state = JSON.parse(restored);
  // Recalculate elapsed time from startedAt
  const elapsedMs = Date.now() - new Date(state.startedAt).getTime();
  setTimeElapsed(Math.floor(elapsedMs / 1000));
}
```

### Celebration Eliza Encouragement

```python
# In companion service
async def generate_encouragement(user_id: str, mission: Mission, session: MissionSession):
    """Generate personalized encouragement after mission completion."""
    # Query memory for context
    memories = await memory_service.query_memories(
        user_id, "recent missions completed streaks", limit=5
    )

    # Count recent completions
    recent_count = await count_missions_completed_this_week(user_id)

    # Generate context-aware message
    if recent_count == 1:
        return "Great start! First mission of the week complete 🎉"
    elif recent_count >= 10:
        return f"Wow! {recent_count} missions this week - you're on fire! 🔥"
    elif session.actual_minutes < mission.estimated_minutes:
        return f"Nice! You finished {mission.estimated_minutes - session.actual_minutes} minutes early ⚡"
    else:
        return "Another one done! Keep the momentum going 💪"
```

### Integration with Story 3.5 (Notes)

Mission session notes (Story 3.5) will use the `notes` TEXT field in `mission_sessions` table. Story 3.4 includes the field but doesn't expose it in the UI yet. Story 3.5 adds:
- Notes text area in completion modal
- Save notes before marking complete
- Display notes in mission history

### References

**Source Documents:**
- **Epics**: `docs/epics.md` (lines 765-805: Story 3.4 requirements)
- **Story 3.3**: Mission triads (execution starts from "Start Mission" button)
- **Product Brief**: Gentle vs. aggressive timers

---

## Definition of Done

- [ ] ✅ `mission_sessions` table created
- [ ] ✅ Mission session service implemented
- [ ] ✅ Mission executor component created
- [ ] ✅ Timer works (countdown/countup, accurate)
- [ ] ✅ Gentle notification implemented (no aggressive sounds)
- [ ] ✅ Early completion works
- [ ] ✅ Time extension works
- [ ] ✅ Pause/resume works
- [ ] ✅ Session persistence works across refreshes
- [ ] ✅ Abandon confirmation works
- [ ] ✅ Completion celebration implemented
- [ ] ✅ Eliza encouragement integrated
- [ ] ✅ Next mission suggestion displayed
- [ ] ✅ All acceptance criteria verified
- [ ] ✅ Unit and integration tests passing
- [ ] ✅ Documentation complete
- [ ] ✅ Story status updated to `done`

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Implement execution flow, test timer accuracy, validate celebration experience
