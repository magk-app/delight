# Story 3.6: Implement Adaptive Quest Generation Worker

**Story ID:** 3.6
**Epic:** 3 - Goal & Mission Management
**Status:** drafted
**Priority:** Future (Post-MVP Enhancement)
**Estimated Effort:** 10-12 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18
**Updated:** 2025-11-18

---

## User Story

**As a** user,
**I want** new missions to be generated automatically based on my patterns,
**So that** I don't run out of things to work on.

---

## Context

### Problem Statement

Goal decomposition (Story 3.2) creates an initial mission pool. But missions get completed, and users need fresh quests aligned with their goals. Story 3.6 implements the **Adaptive Quest Generator** - an ARQ background worker that:
- Monitors mission queue levels
- Analyzes user completion patterns (time of day, energy preferences, value categories)
- Generates new missions using Eliza's LangGraph agent
- Ensures diversity (doesn't flood queue with one goal's missions)

This keeps the productivity loop running without manual intervention.

### Dependencies

- **Prerequisites:**
  - 3.3 (Mission System) ✅ Complete - Missions infrastructure
  - 2.3 (Eliza Agent) ✅ Complete - Agent for quest generation
  - Epic 1: ARQ worker infrastructure

---

## Acceptance Criteria

### AC1: Quest Generator Worker Runs Nightly

**Given** ARQ is configured
**When** the scheduled job runs (2:00 AM daily)
**Then** the `generate_adaptive_quests` worker executes

**And** it checks each active user's mission queue:
- Count pending missions (status = `pending`)
- If count < 5 → trigger generation for this user
- If count >= 5 → skip (queue healthy)

**And** worker logs execution metrics:
- Users processed
- Missions generated
- Errors encountered

### AC2: Worker Analyzes User Completion Patterns

**Given** a user needs new missions
**When** the worker analyzes their patterns
**Then** it queries:

**Completion Patterns:**
- Most productive time of day (when missions completed)
- Preferred mission duration (average actual_minutes)
- Energy level distribution (low/medium/high completion rates)
- Value category balance (which categories need more missions)
- Goals with recent activity (prioritize active goals)

**Query Example:**
```sql
SELECT
  EXTRACT(HOUR FROM completed_at) as completion_hour,
  AVG(actual_minutes) as avg_duration,
  value_category,
  energy_level,
  COUNT(*) as completions
FROM mission_sessions ms
JOIN missions m ON ms.mission_id = m.id
WHERE ms.user_id = :user_id
  AND ms.status = 'completed'
  AND ms.completed_at > NOW() - INTERVAL '30 days'
GROUP BY completion_hour, value_category, energy_level;
```

**And** pattern analysis informs quest generation prompts

### AC3: Worker Queries Eliza Agent for Quest Ideas

**Given** user patterns are analyzed
**When** the worker generates quests
**Then** it calls Eliza's goal decomposition node (Story 3.2) with context:

**Generation Prompt:**
```
Generate 3-5 new micro-quests for user {user_name} based on their active goals and patterns:

Active Goals:
- {goal_1_title} (type: {type}, category: {category})
- {goal_2_title} ...

User Patterns (last 30 days):
- Most productive time: {completion_hour}
- Preferred duration: {avg_duration} minutes
- Energy distribution: {energy_stats}
- Value categories: {category_distribution}

Requirements:
- Generate quests aligned with active goals
- Vary energy levels (30% low, 50% medium, 20% high)
- Balance value categories (prioritize underrepresented)
- Keep quests small (10-30 minutes)
- Sequence logically within goals

Output format: {structured_quest_schema}
```

**And** Eliza agent returns structured quest proposals (Pydantic schema)

### AC4: Generated Quests Are Diverse and Balanced

**Given** the worker generates quests
**When** quests are created
**Then** they follow diversity rules:

**Diversity Constraints:**
- **Max 2 quests per goal** per generation run (prevents flooding)
- **Value category balance**: If health=0 pending, craft=0, growth=3, connection=2 → prioritize health/craft
- **Energy variety**: Mix of low/medium/high (not all high-energy)
- **Time variety**: Mix of durations (10min, 20min, 30min)

**And** quests are prioritized based on:
- Goal deadlines (urgent goals get more quests)
- Time since last mission for goal
- User's value category preferences (from patterns)

### AC5: Worker Triggers on Low Queue (On-Demand)

**Given** a user completes many missions in one day
**When** their pending mission count drops below 5
**Then** an on-demand generation job is triggered (in addition to nightly run)

**Implementation:**
- After mission completion, check pending count
- If < 5, enqueue `generate_adaptive_quests` ARQ job for this user
- Rate limit: Max 1 on-demand generation per user per 6 hours (prevent spam)

### AC6: Generated Quests Appear in Mission Pool

**Given** the worker generates quests
**When** missions are created
**Then** they appear in the user's pending mission pool

**And** they're eligible for triad selection (Story 3.3)

**And** priority scores are calculated (same algorithm as manual missions)

**And** missions link to parent goals (goal_id FK)

---

## Tasks / Subtasks

### Task 1: Create ARQ Worker (AC: #1, #5)

- [ ] **1.1** Create `packages/backend/app/workers/quest_generator.py`
- [ ] **1.2** Implement `generate_adaptive_quests_job(ctx, user_id=None)` async function:
  - If user_id provided: generate for single user (on-demand)
  - If user_id None: generate for all users with low queues (nightly)
- [ ] **1.3** Configure ARQ worker settings:
  ```python
  class WorkerSettings:
      cron_jobs = [
          cron(quest_generator.generate_adaptive_quests_job, hour=2, minute=0),  # 2 AM daily
      ]
  ```
- [ ] **1.4** Add retry configuration (3 attempts, exponential backoff)

### Task 2: Implement Pattern Analysis (AC: #2)

- [ ] **2.1** Create `app/services/user_pattern_service.py`
- [ ] **2.2** Implement `analyze_completion_patterns(user_id)` method:
  - Query mission_sessions for last 30 days
  - Calculate time-of-day distribution
  - Calculate average duration
  - Calculate energy level preferences
  - Calculate value category distribution
  - Identify goals with recent activity
- [ ] **2.3** Return structured pattern data for quest generation

### Task 3: Integrate Eliza Agent for Quest Generation (AC: #3)

- [ ] **3.1** Extend Eliza agent's goal_decomposition node
- [ ] **3.2** Add "adaptive quest generation" variant:
  - Takes user patterns as input
  - Takes active goals as context
  - Returns 3-5 quest proposals (not full decomposition)
- [ ] **3.3** Use structured output parsing (Pydantic schema)

### Task 4: Implement Diversity Rules (AC: #4)

- [ ] **4.1** Create `app/services/quest_diversity_service.py`
- [ ] **4.2** Implement diversity constraints:
  - Max quests per goal per run
  - Value category balancing algorithm
  - Energy level distribution enforcement
  - Time variety checks
- [ ] **4.3** Filter/adjust generated quests to meet constraints

### Task 5: Implement On-Demand Triggering (AC: #5)

- [ ] **5.1** Update `MissionService.complete_mission()`:
  - After completion, count pending missions
  - If < 5, enqueue on-demand generation job
  - Check rate limit (Redis: `quest_gen_last_run:{user_id}`)
- [ ] **5.2** Implement rate limiting (6-hour cooldown)

### Task 6: Create Admin Endpoint for Manual Triggering (Optional)

- [ ] **6.1** Add `POST /api/v1/admin/generate-quests/{user_id}` (admin-only)
- [ ] **6.2** Manually trigger generation for testing/support

### Task 7: Tests and Monitoring (AC: All)

- [ ] **7.1** Unit tests for pattern analysis
- [ ] **7.2** Unit tests for diversity rules
- [ ] **7.3** Integration test for full worker execution
- [ ] **7.4** Add logging and metrics (quests generated, execution time)
- [ ] **7.5** Add alerting if worker fails repeatedly

### Task 8: Documentation (AC: All)

- [ ] **8.1** Document quest generation algorithm
- [ ] **8.2** Document diversity rules and rationale
- [ ] **8.3** Document troubleshooting guide for worker failures

---

## Dev Notes

### Pattern Analysis Example

**User Completion Patterns (Last 30 Days):**
```json
{
  "completion_hours": {
    "9": 8,   // 8 missions completed at 9 AM
    "10": 12,
    "14": 5,
    "19": 3
  },
  "avg_duration_minutes": 22,
  "energy_distribution": {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.2
  },
  "value_category_distribution": {
    "health": 10,
    "craft": 5,
    "growth": 12,
    "connection": 3
  },
  "active_goals": [
    {"id": "uuid1", "title": "Graduate early", "recent_missions": 8},
    {"id": "uuid2", "title": "Run half-marathon", "recent_missions": 6}
  ]
}
```

**Generation Strategy:**
- Focus on morning quests (9-10 AM preference)
- Average 20-25 minute duration
- 50% medium energy, 30% low, 20% high
- Boost connection quests (underrepresented at 10%)
- Balance between Graduate and Run goals

### Diversity Algorithm Pseudocode

```python
def apply_diversity_rules(proposed_quests, user_patterns, existing_pending):
    # 1. Limit quests per goal
    quest_counts_by_goal = Counter(q.goal_id for q in proposed_quests)
    filtered = [q for q in proposed_quests if quest_counts_by_goal[q.goal_id] <= 2]

    # 2. Balance value categories
    pending_categories = Counter(m.value_category for m in existing_pending)
    underrepresented = [cat for cat, count in pending_categories.items() if count < 2]

    # Boost quests in underrepresented categories
    scored_quests = []
    for quest in filtered:
        score = 1.0
        if quest.value_category in underrepresented:
            score += 0.5  # Boost underrepresented
        scored_quests.append((quest, score))

    # Sort by score and take top 5
    sorted_quests = sorted(scored_quests, key=lambda x: x[1], reverse=True)
    return [q for q, score in sorted_quests[:5]]
```

### Rate Limiting Implementation

```python
# In MissionService.complete_mission()
async def check_and_trigger_quest_generation(user_id: str):
    # Check pending count
    pending_count = await db.execute(
        select(func.count(Mission.id))
        .where(and_(Mission.user_id == user_id, Mission.status == "pending"))
    ).scalar()

    if pending_count >= 5:
        return  # Queue healthy

    # Check rate limit (Redis)
    last_run_key = f"quest_gen_last_run:{user_id}"
    last_run = await redis.get(last_run_key)

    if last_run:
        last_run_time = datetime.fromisoformat(last_run)
        if datetime.now() - last_run_time < timedelta(hours=6):
            return  # Rate limited

    # Trigger generation
    await arq_pool.enqueue_job(
        "generate_adaptive_quests_job",
        user_id=user_id
    )

    # Update rate limit
    await redis.setex(last_run_key, timedelta(hours=6), datetime.now().isoformat())
```

### References

**Source Documents:**
- **Epics**: `docs/epics.md` (lines 840-869: Story 3.6 requirements)
- **Story 2.3**: Eliza agent (quest generation integration)
- **Story 3.3**: Mission prioritization (applies to generated quests)

---

## Definition of Done

- [ ] ✅ ARQ worker created and configured
- [ ] ✅ Nightly cron job working (2 AM)
- [ ] ✅ Pattern analysis implemented
- [ ] ✅ Eliza agent integration working
- [ ] ✅ Diversity rules implemented and tested
- [ ] ✅ On-demand triggering working
- [ ] ✅ Rate limiting in place
- [ ] ✅ Generated quests appear in mission pool
- [ ] ✅ All acceptance criteria verified
- [ ] ✅ Tests passing
- [ ] ✅ Monitoring and logging added
- [ ] ✅ Documentation complete
- [ ] ✅ Story status updated to `done`

---

**Last Updated:** 2025-11-18
**Story Status:** drafted (Future)
**Next Steps:** Implement worker, test pattern analysis, validate quest quality
