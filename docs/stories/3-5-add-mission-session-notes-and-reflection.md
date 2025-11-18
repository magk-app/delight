# Story 3.5: Add Mission Session Notes and Reflection

**Story ID:** 3.5
**Epic:** 3 - Goal & Mission Management
**Status:** drafted
**Priority:** P1 (Engagement Driver)
**Estimated Effort:** 6-8 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18
**Updated:** 2025-11-18

---

## User Story

**As a** user,
**I want** to capture quick notes during or after a mission,
**So that** I can track learnings and progress details.

---

## Context

### Problem Statement

Missions aren't just about completion - they generate insights. "I struggled with X," "This approach worked well," "Next time try Y." Story 3.5 captures these micro-learnings so they inform future work and become part of Eliza's memory.

Notes become task-tier memories (Story 2.2), enabling Eliza to reference: "Last time you mentioned this was challenging - how's it going now?"

### Dependencies

- **Prerequisites:**
  - 3.4 (Mission Execution) ✅ Complete - Notes field exists, needs UI
  - 2.2 (Memory Service) ✅ Complete - Stores notes as task memories

---

## Acceptance Criteria

### AC1: Notes Field Available During Mission Execution

**Given** I'm working on a mission (Story 3.4)
**When** I expand the notes section
**Then** I see a text area with placeholder: "Capture any learnings, struggles, or ideas..."

**And** notes auto-save every 30 seconds (draft state)

**And** character count shown: "0 / 1000 characters"

### AC2: Notes Prompted at Completion

**Given** I mark a mission complete
**When** the completion modal appears (Story 3.4 celebration)
**Then** I see a notes prompt:
- "Any reflections on this mission?" (optional, can skip)
- Text area with current draft notes (if any)
- Quick prompts: "What went well?" | "What was hard?" | "Next time..."

**And** I can:
- Add/edit notes before completing
- Skip notes (proceed without)
- Completion happens either way (notes optional)

### AC3: Notes Saved to Mission Session

**Given** I've added notes during or after a mission
**When** I complete the mission
**Then** notes are saved to `mission_sessions.notes` field

**And** notes are visible in mission history (AC5)

### AC4: Notes Become Task-Tier Memories

**Given** I've completed a mission with notes
**When** the mission is marked complete
**Then** a task memory is created:

**Memory Content:**
```
Mission: [mission title]
Completed: [date]
Notes: [user notes]
Goal: [goal title if linked]
Time: [actual_minutes] minutes
```

**Memory Metadata:**
```json
{
  "memory_type": "task",
  "mission_id": "uuid",
  "goal_id": "uuid",  // if linked
  "value_category": "health",
  "session_duration_minutes": 25
}
```

**And** memory is queryable by Eliza in future conversations

### AC5: Mission History Shows Notes

**Given** I've completed missions with notes
**When** I view mission history (`/missions/history`)
**Then** I see a list of completed missions with:
- Mission title
- Completion date
- Actual time spent
- **Notes** (expandable preview)
- Parent goal (if linked)

**And** I can filter by:
- Date range
- Goal
- Value category

**And** I can search notes content (full-text search)

### AC6: Goal Progress View Shows Mission Notes

**Given** I'm viewing a goal's progress (`/goals/{id}/progress`)
**When** I see the list of completed missions for this goal
**Then** each mission shows its notes (if any)

**And** notes help track progress narrative:
- "Week 1: Struggled with pacing"
- "Week 3: Getting easier!"
- "Week 5: Felt great today"

---

## Tasks / Subtasks

### Task 1: Add Notes UI to Mission Executor (AC: #1)

- [ ] **1.1** Update `MissionExecutor.tsx` component
- [ ] **1.2** Add expandable notes section below timer
- [ ] **1.3** Implement auto-save (every 30s) to draft state (localStorage)
- [ ] **1.4** Add character counter (max 1000 chars)
- [ ] **1.5** Style as unobtrusive (doesn't distract from mission)

### Task 2: Add Notes to Completion Modal (AC: #2)

- [ ] **2.1** Update `MissionCompletionCelebration.tsx`
- [ ] **2.2** Add notes prompt with quick reflection templates
- [ ] **2.3** Pre-fill with draft notes if any
- [ ] **2.4** Allow skip (continue without notes)
- [ ] **2.5** Save notes before marking mission complete

### Task 3: Create Task Memory from Notes (AC: #4)

- [ ] **3.1** Update `MissionSessionService.complete_session()`
- [ ] **3.2** After completion, call `MemoryService.add_memory()`:
  ```python
  if session.notes:
      await memory_service.add_memory(
          user_id=user_id,
          memory_type=MemoryType.TASK,
          content=f"Mission: {mission.title}\nCompleted: {session.completed_at}\nNotes: {session.notes}",
          metadata={
              "mission_id": str(mission.id),
              "goal_id": str(mission.goal_id) if mission.goal_id else None,
              "value_category": mission.value_category,
              "session_duration_minutes": session.actual_minutes
          }
      )
  ```
- [ ] **3.3** Test memory creation and retrieval

### Task 4: Create Mission History Page (AC: #5)

- [ ] **4.1** Create `packages/frontend/src/app/missions/history/page.tsx`
- [ ] **4.2** Fetch completed missions with notes
- [ ] **4.3** Display in timeline or list format
- [ ] **4.4** Add filters: date range, goal, value category
- [ ] **4.5** Add search: full-text search on notes content
- [ ] **4.6** Style notes preview (expand/collapse)

### Task 5: Add Notes to Goal Progress View (AC: #6)

- [ ] **5.1** Update `packages/frontend/src/app/goals/[id]/progress/page.tsx` (create if doesn't exist)
- [ ] **5.2** Show completed missions for goal with notes
- [ ] **5.3** Display as progress narrative

### Task 6: Add API Endpoints (AC: All)

- [ ] **6.1** Update `app/api/v1/missions.py`:
  - `GET /missions/history`: List completed missions with notes, filters
  - `GET /missions/{id}/notes`: Get notes for specific mission
  - `PATCH /sessions/{id}/notes`: Update notes (for auto-save)

### Task 7: Tests and Documentation (AC: All)

- [ ] **7.1** Test notes save/retrieve
- [ ] **7.2** Test memory creation from notes
- [ ] **7.3** Test full-text search on notes
- [ ] **7.4** Document note-taking best practices for users

---

## Dev Notes

### Notes as Task Memories

**30-Day Retention:**
Task memories (Story 2.2) are pruned after 30 days. This means:
- Recent mission notes available to Eliza for 1 month
- After 30 days, notes remain in `mission_sessions` table but not in memory
- Important patterns should surface in personal/project memory through conversation

**Query Example:**
```python
# Eliza queries recent mission notes
task_memories = await memory_service.query_memories(
    user_id=user_id,
    query_text="recent mission notes learnings",
    memory_types=[MemoryType.TASK],
    limit=10
)
```

### Note Templates (Quick Prompts)

Suggested quick prompts to help users reflect:
- "What went well?"
- "What was challenging?"
- "What would I do differently next time?"
- "New insight or idea:"

These reduce friction for users unsure what to write.

### Full-Text Search Implementation

```sql
-- Add GIN index for full-text search on notes
CREATE INDEX idx_mission_sessions_notes_search ON mission_sessions USING GIN(to_tsvector('english', notes));

-- Search query
SELECT ms.*, m.title
FROM mission_sessions ms
JOIN missions m ON ms.mission_id = m.id
WHERE to_tsvector('english', ms.notes) @@ plainto_tsquery('english', 'struggled pacing')
  AND ms.user_id = :user_id
ORDER BY ms.completed_at DESC;
```

### References

**Source Documents:**
- **Epics**: `docs/epics.md` (lines 807-837: Story 3.5 requirements)
- **Story 2.2**: Memory service (task-tier integration)
- **Story 3.4**: Mission execution (notes field exists)

---

## Definition of Done

- [ ] ✅ Notes UI added to mission executor
- [ ] ✅ Auto-save working
- [ ] ✅ Completion modal includes notes prompt
- [ ] ✅ Notes saved to mission_sessions table
- [ ] ✅ Task memories created from notes
- [ ] ✅ Mission history page created
- [ ] ✅ Goal progress view shows notes
- [ ] ✅ Full-text search working
- [ ] ✅ All acceptance criteria verified
- [ ] ✅ Tests passing
- [ ] ✅ Documentation complete
- [ ] ✅ Story status updated to `done`

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Add notes UI, test memory integration, validate search
