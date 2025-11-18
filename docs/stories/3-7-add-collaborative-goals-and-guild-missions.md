# Story 3.7: Add Collaborative Goals and Guild Missions

**Story ID:** 3.7
**Epic:** 3 - Goal & Mission Management
**Status:** drafted
**Priority:** Future (Multiplayer Feature)
**Estimated Effort:** 16-20 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18
**Updated:** 2025-11-18

---

## User Story

**As a** user,
**I want** to work on goals with friends or accountability pods,
**So that** we support each other and share progress.

---

## Context

### Problem Statement

Solo goal pursuit can feel lonely. Story 3.7 adds multiplayer collaboration through:
- **Shared Goals**: Pod members work toward common objectives
- **Guild Missions**: Special quests requiring multiple participants
- **Shared Progress**: Celebrate milestones together
- **Accountability**: Mutual support and encouragement

This transforms Delight from solo productivity tool to collaborative growth platform.

### Dependencies

- **Prerequisites:**
  - 3.3 (Mission System) ✅ Complete - Individual missions infrastructure
  - Epic 6: World state and multiplayer system (pods, notifications)
  - Real-time notifications for pod member updates

**Note:** This is a future feature requiring multiplayer infrastructure from Epic 6.

---

## Acceptance Criteria

### AC1: Pod/Guild System Exists

**Given** multiplayer infrastructure is built (Epic 6)
**When** I create or join a pod
**Then** I can see pod members and shared goals

**Pod Schema (`pods` table):**
- `id` (UUID)
- `name` (VARCHAR)
- `description` (TEXT)
- `members` (ARRAY of user_ids)
- `pod_type` (ENUM: `accountability_pod`, `guild`, `study_group`)
- `created_at`, `updated_at`

### AC2: Shared Goals Can Be Created

**Given** I'm in a pod
**When** I create a shared goal
**Then** all pod members can see and contribute to it

**Shared Goal Schema (`shared_goals` table):**
- `id` (UUID)
- `goal_id` (UUID FK to goals)
- `pod_id` (UUID FK to pods)
- `member_contributions` (JSONB: {user_id: {missions_completed, time_contributed}})
- `created_by` (user_id)
- `created_at`

**And** shared goals appear in pod dashboard

**And** members receive notification: "New shared goal: [title]"

### AC3: Members Can Contribute Missions to Shared Goals

**Given** a shared goal exists
**When** I complete a mission linked to this goal
**Then** my contribution is recorded in `member_contributions`

**And** pod members see updated progress

**And** leaderboard shows top contributors (optional: can be toggled private)

### AC4: Guild Missions Require Multiple Participants

**Given** a guild mission exists
**When** members work on it
**Then** progress aggregates across all participants

**Guild Mission Schema (extends `missions`):**
- `is_guild_mission` (BOOLEAN)
- `required_participants` (INTEGER, e.g., 3)
- `participant_contributions` (JSONB: {user_id: completion_status})

**Example Guild Mission:**
- Title: "Team Sprint: 10 hours of collective study"
- Required: 3 members
- Progress: Member A (3 hrs), Member B (4 hrs), Member C (3 hrs) = 10/10 hrs → Complete!

### AC5: Shared Rewards and Celebration

**Given** a shared goal or guild mission is completed
**When** the milestone is reached
**Then** all contributors receive:
- Shared celebration notification
- Pod achievement badge (visible in profile)
- Optional: Unlock shared narrative events (Epic 4 integration)

**And** celebration includes contributor breakdown

---

## Tasks / Subtasks

### Task 1: Create Pod/Guild Schema (AC: #1)

- [ ] **1.1** Create `pods` table migration
- [ ] **1.2** Create `shared_goals` table migration
- [ ] **1.3** Extend `missions` table with guild fields
- [ ] **1.4** Apply migrations

### Task 2: Implement Pod Service (AC: #1, #2)

- [ ] **2.1** Create `app/services/pod_service.py`
- [ ] **2.2** Methods: create_pod, join_pod, leave_pod, get_pod_members

### Task 3: Implement Shared Goal Service (AC: #2, #3)

- [ ] **3.1** Create `app/services/shared_goal_service.py`
- [ ] **3.2** Methods: create_shared_goal, record_contribution, get_shared_goal_progress

### Task 4: Implement Guild Mission Logic (AC: #4)

- [ ] **4.1** Extend `MissionService` with guild mission handling
- [ ] **4.2** Aggregate participant contributions
- [ ] **4.3** Mark guild mission complete when requirements met

### Task 5: Create Pod Dashboard UI (AC: #1, #2, #3)

- [ ] **5.1** Create `app/pods/[id]/page.tsx`
- [ ] **5.2** Display: members, shared goals, guild missions, leaderboard

### Task 6: Implement Notifications (AC: #2, #3, #5)

- [ ] **6.1** Notify pod members on shared goal creation
- [ ] **6.2** Notify on milestone completion
- [ ] **6.3** Daily digest: "Your pod completed 15 missions this week!"

### Task 7: Add Shared Rewards (AC: #5)

- [ ] **7.1** Create pod achievement system
- [ ] **7.2** Unlock shared narrative events (Epic 4 integration)

### Task 8: Tests and Documentation (AC: All)

- [ ] **8.1** Unit tests for pod and shared goal services
- [ ] **8.2** Integration tests for contribution tracking
- [ ] **8.3** Documentation for pod features

---

## Dev Notes

### Pod Types

**Accountability Pod:**
- 2-5 members
- Shared goals with mutual support
- Weekly check-ins
- Privacy: Members only (not public)

**Guild:**
- 5-20 members
- Guild missions requiring teamwork
- Leaderboards and achievements
- Can be public (open to join)

**Study Group:**
- 3-10 members
- Focus on growth/learning goals
- Resource sharing (notes, materials)
- Time-boxed (e.g., semester, bootcamp duration)

### Contribution Tracking

```python
# Record contribution when member completes mission
async def record_contribution(shared_goal_id, user_id, mission):
    shared_goal = await db.get(SharedGoal, shared_goal_id)

    # Update member_contributions JSONB
    contributions = shared_goal.member_contributions or {}
    user_contrib = contributions.get(user_id, {"missions_completed": 0, "time_contributed": 0})

    user_contrib["missions_completed"] += 1
    user_contrib["time_contributed"] += mission_session.actual_minutes

    contributions[user_id] = user_contrib
    shared_goal.member_contributions = contributions

    await db.commit()

    # Notify pod members
    await notify_pod_members(shared_goal.pod_id, f"{user_name} completed a mission for {goal_title}!")
```

### Guild Mission Completion Logic

```python
async def check_guild_mission_completion(guild_mission):
    """Check if guild mission requirements met."""
    participants = guild_mission.participant_contributions
    completed_count = sum(1 for status in participants.values() if status == "completed")

    if completed_count >= guild_mission.required_participants:
        # Mark guild mission complete
        guild_mission.status = "completed"
        guild_mission.completed_at = datetime.now()

        # Notify all participants
        await notify_participants(guild_mission, "Guild mission complete! 🎉")

        # Award shared rewards
        await award_guild_achievement(guild_mission)
```

### Privacy and Permissions

**Privacy Levels:**
- **Private Pod**: Members only, invite-required
- **Public Guild**: Anyone can join, contributions visible
- **Anonymous Contributions**: Option to hide individual contributions (show aggregate only)

**Permissions:**
- Pod creator = admin (can invite, remove members)
- All members can create shared goals
- Guild missions require admin approval

### Integration with Epic 4 (Narrative)

**Shared Narrative Events:**
- Guild completing epic-level goal → unlock shared story chapter
- All members get access to special narrative content
- "Your guild discovered the Hidden Library together!"

### Integration with Epic 6 (World State)

**Pod Zones in the World:**
- Guilds can have designated meeting zones (Commons)
- Real-time presence: See pod members online in world
- Shared rituals: Guild meditation sessions, study halls

### References

**Source Documents:**
- **Epics**: `docs/epics.md` (lines 871-903: Story 3.7 requirements)
- **Epic 6**: World state and multiplayer infrastructure

---

## Definition of Done

- [ ] ✅ Pod and shared goal schemas created
- [ ] ✅ Pod service implemented
- [ ] ✅ Shared goal service implemented
- [ ] ✅ Guild mission logic working
- [ ] ✅ Pod dashboard UI created
- [ ] ✅ Notifications implemented
- [ ] ✅ Shared rewards system working
- [ ] ✅ Privacy controls in place
- [ ] ✅ All acceptance criteria verified
- [ ] ✅ Tests passing
- [ ] ✅ Documentation complete
- [ ] ✅ Story status updated to `done`

---

**Last Updated:** 2025-11-18
**Story Status:** drafted (Future - requires Epic 6)
**Next Steps:** Implement after Epic 6 multiplayer infrastructure complete
