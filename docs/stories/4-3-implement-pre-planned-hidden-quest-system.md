# Story 4.3: Implement Pre-Planned Hidden Quest System

**Story ID:** 4.3
**Epic:** 4 - Narrative Engine
**Status:** drafted
**Priority:** P1 (Engagement Driver)
**Estimated Effort:** 6-8 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18

---

## User Story

**As a** user,
**I want** to discover surprise quests that unlock when I hit milestones,
**So that** my journey feels rewarding and full of delightful discoveries.

---

## Context

### Problem Statement

Pre-planned hidden quests create delightful surprises that reward consistent effort and specific achievement patterns. Unlike standard missions, hidden quests:

1. **Remain secret** until unlock conditions are met (no spoilers)
2. **Trigger automatically** based on user behavior (streaks, mission counts, patterns)
3. **Provide unique rewards** (Essence, titles, artifacts, relationship boosts)
4. **Create narrative significance** (advance story, unlock dialogue, discover zones)

This story implements the detection system that monitors user progress nightly, evaluates trigger conditions from scenario templates, and unlocks quests with in-app notifications.

### Why This Approach?

**From Epics (epics.md lines 1049-1093):**

Hidden quests solve the "predictability problem" in goal-tracking apps. Users know they're working toward something, but don't know WHAT or WHEN it will unlock. This creates:

- ✅ **Intrinsic motivation**: Surprise > expectation
- ✅ **Pattern diversity**: Different quests reward different behaviors
- ✅ **Narrative integration**: Quests have story significance, not just badges
- ✅ **Replayability**: Users wonder "what else is hidden?"

**From Tech Spec (tech-spec-epic-4.md, Hidden Quests Structure):**

Trigger types support diverse achievement patterns:

- Streak-based: Reward consistency (e.g., 20-day streak in craft)
- Count-based: Reward volume (e.g., 100 missions completed)
- Balance-based: Reward variety (e.g., equal focus across all values for 14 days)
- Time-based: Reward specific patterns (e.g., 30 missions after 10pm)
- Reflection-based: Reward thoughtfulness (e.g., 50 reflection notes written)

### Dependencies

- **Prerequisite Stories:**
  - 4.1 (Narrative Schema) ✅ hidden_quests in scenario_templates
  - 4.2 (Narrative Agent) ✅ check_unlocks node
  - ARQ worker infrastructure (Epic 1) ✅ Background job system

- **Epic 4 Context:** This story **uses**:
  - Story 4.2: check_unlocks node output for quest IDs
  - Story 4.1: scenario_templates.hidden_quests for trigger definitions
  - Story 3.X (Missions): Mission completion data for trigger evaluation

- **External Dependencies:**
  - Redis for ARQ queue
  - Mission and Progress models from Epic 3

---

## Acceptance Criteria

### AC1: ARQ Worker Checks Trigger Conditions Nightly

**Given** ARQ worker is configured
**When** the scheduled job runs (daily at 2:00 AM)
**Then** the worker:

- Queries all active users with narrative_states
- For each user, loads their scenario template
- Evaluates all hidden quest triggers against user progress
- Unlocks quests when conditions are met
- Logs unlock events

**And** the worker runs reliably:

- Retries on failure (3 attempts, exponential backoff)
- Logs completion with unlock counts
- Alerts on errors via logging

**Verification:**

```python
# In app/workers/quest_generator.py
from arq import cron

class WorkerSettings:
    cron_jobs = [
        cron(hidden_quest_detector, hour=2, minute=0),  # 2:00 AM daily
    ]

# Test execution
result = await hidden_quest_detector({})
assert isinstance(result, dict)
assert "users_processed" in result
assert "quests_unlocked" in result
```

### AC2: Trigger Evaluation Supports Multiple Trigger Types

**Given** hidden quests with different trigger types exist
**When** the worker evaluates triggers
**Then** it correctly evaluates:

**Streak-based triggers:**
```python
{"streak_days": 20, "attribute": "craft"}
# Unlocks if user has 20+ day streak with craft as dominant attribute
```

**Mission count triggers:**
```python
{"missions_completed": 100}
# Unlocks if user has completed 100+ total missions
```

**Balance triggers:**
```python
{"equal_value_distribution": 14}
# Unlocks if user completed equal missions across all 4 values for 14 days
```

**Time-based triggers:**
```python
{"missions_after_10pm": 30}
# Unlocks if user completed 30+ missions after 10 PM
```

**Reflection triggers:**
```python
{"reflection_notes_written": 50}
# Unlocks if user wrote 50+ reflection notes
```

**Verification:**

```python
# Test each trigger type
triggers = [
    {"streak_days": 20, "attribute": "craft"},
    {"missions_completed": 100},
    {"equal_value_distribution": 14},
    {"missions_after_10pm": 30},
    {"reflection_notes_written": 50}
]

for trigger in triggers:
    result = evaluate_trigger(trigger, user_progress)
    assert isinstance(result, bool)
```

### AC3: Quest Unlocking Updates Narrative State

**Given** a hidden quest trigger is met
**When** the worker unlocks the quest
**Then** the quest ID is added to `narrative_states.unlocked_quests` array

**And** the unlock timestamp is recorded in `story_progress.quest_unlocks`:

```json
{
  "story_progress": {
    "quest_unlocks": [
      {
        "quest_id": "relentless_achievement",
        "unlocked_at": "2025-11-18T02:00:15Z",
        "trigger_met": {"streak_days": 20, "attribute": "craft"}
      }
    ]
  }
}
```

**And** the database transaction commits successfully

**Verification:**

```sql
SELECT unlocked_quests, story_progress->'quest_unlocks'
FROM narrative_states
WHERE user_id = 'test-user';
```

### AC4: In-App Notifications Created for Quest Unlocks

**Given** a hidden quest unlocks
**When** the worker processes the unlock
**Then** an in-app notification is created with:

- **Title**: Quest title from scenario template
- **Message**: Narrative context from scenario template
- **Type**: "hidden_quest_unlock"
- **Data**: `{quest_id, rewards_preview, time_limit}`
- **Created timestamp**

**And** the notification appears in user's notification feed

**Verification:**

```python
notifications = await db.execute(
    select(Notification).where(
        Notification.user_id == user_id,
        Notification.type == "hidden_quest_unlock"
    )
)
assert len(notifications) > 0
```

### AC5: Eliza Messages Users About Hidden Quest Unlocks

**Given** a hidden quest unlocks
**When** the worker creates the notification
**Then** an Eliza message is queued with:

- **From**: "Eliza"
- **Message**: "{Narrative context}. This special quest has unlocked for you. Would you like to hear more about it?"
- **Includes**: Quest title, brief reward preview
- **CTA**: Link to quest details in missions view

**And** the message appears in user's companion chat (next time they open Eliza)

**Verification:**

```python
messages = await db.execute(
    select(CompanionMessage).where(
        CompanionMessage.user_id == user_id,
        CompanionMessage.message_type == "quest_unlock"
    )
)
assert len(messages) > 0
```

### AC6: Quests Appear in Mission Pool Marked as "Special"

**Given** a hidden quest is unlocked
**When** the user views their mission pool
**Then** the quest appears with:

- **Label**: "Special Quest" or "Hidden Quest Unlocked"
- **Visual treatment**: Gold border or special icon
- **Rewards displayed**: Essence, title, artifact, relationship boost
- **Time limit** (if applicable): Countdown timer
- **Narrative significance**: Brief description of story impact

**And** quest can be started like regular missions

**And** quest completion triggers narrative beat generation (if significant)

**Verification:**

```python
missions = await mission_service.get_user_missions(user_id, include_hidden=True)
special_missions = [m for m in missions if m.is_hidden_quest]
assert len(special_missions) > 0
assert special_missions[0].quest_type == "special"
```

### AC7: Time-Limited Quests Enforce Time Constraints

**Given** a hidden quest has `time_limit_hours` defined
**When** the quest unlocks
**Then** a deadline is calculated: `unlocked_at + time_limit_hours`

**And** the quest expires if not completed by deadline

**And** expired quests are marked as `status: 'expired'` (not deleted)

**And** user receives notification before expiration (24 hours warning)

**Verification:**

```python
# Quest with 72-hour time limit
quest = {
    "id": "century_milestone",
    "time_limit_hours": 72,
    "unlocked_at": "2025-11-18T02:00:00Z"
}

deadline = calculate_deadline(quest)
assert deadline == datetime(2025, 11, 21, 2, 0, 0)  # 72 hours later

# Test expiration
is_expired = check_quest_expired(quest, current_time=datetime(2025, 11, 22))
assert is_expired == True
```

### AC8: Worker Logs Quest Unlock Events for Analytics

**Given** the worker processes quest unlocks
**When** quests are unlocked
**Then** the following metrics are logged:

- Total users processed
- Total quests unlocked
- Breakdown by quest type
- Average time to unlock per quest
- Unlock rate by quest (% of users who unlocked each quest)

**And** logs are structured for easy querying

**Verification:**

```python
# Log format
logger.info("Hidden quest unlock batch complete", extra={
    "users_processed": 1523,
    "quests_unlocked": 47,
    "quest_breakdown": {
        "relentless_achievement": 15,
        "century_milestone": 12,
        "balanced_path": 10,
        "night_owl": 6,
        "unseen_observer": 4
    },
    "processing_time_ms": 2340
})
```

---

## Tasks / Subtasks

### Task 1: Extend Quest Generator Worker for Hidden Quests (AC: #1)

- [ ] **1.1** Update `app/workers/quest_generator.py` (from Epic 3)
- [ ] **1.2** Add `hidden_quest_detector` async function
- [ ] **1.3** Configure ARQ cron schedule: daily at 2:00 AM
- [ ] **1.4** Implement main loop:
  - Query all users with narrative_states
  - Load scenario template for each user
  - Load user progress data (missions, streaks, etc.)
  - Evaluate triggers for each hidden quest
  - Unlock quests if triggers met
- [ ] **1.5** Add retry configuration (3 attempts, exponential backoff)
- [ ] **1.6** Add comprehensive logging

### Task 2: Implement Trigger Evaluation Logic (AC: #2)

- [ ] **2.1** Create `app/services/quest_trigger_evaluator.py`
- [ ] **2.2** Implement `evaluate_trigger(trigger_def, user_progress)` function
- [ ] **2.3** Add trigger type handlers:
  - `_evaluate_streak_trigger()`: Check streak_days and attribute
  - `_evaluate_mission_count_trigger()`: Check missions_completed
  - `_evaluate_balance_trigger()`: Check equal_value_distribution
  - `_evaluate_time_trigger()`: Check missions_after_10pm
  - `_evaluate_reflection_trigger()`: Check reflection_notes_written
- [ ] **2.4** Add helper methods:
  - `_get_user_streak()`: Query progress for current streak
  - `_get_mission_count()`: Count total missions
  - `_check_value_balance()`: Analyze last N days for equal distribution
  - `_count_time_based_missions()`: Query missions by time filter
  - `_count_reflections()`: Query reflection notes
- [ ] **2.5** Add unit tests for each trigger type

### Task 3: Implement Quest Unlocking Logic (AC: #3)

- [ ] **3.1** Create `unlock_hidden_quest()` method in narrative_service
- [ ] **3.2** Update narrative_states.unlocked_quests array:
  - Use PostgreSQL array append: `UPDATE narrative_states SET unlocked_quests = array_append(unlocked_quests, quest_id)`
- [ ] **3.3** Update story_progress.quest_unlocks JSONB:
  - Add unlock record with quest_id, unlocked_at, trigger_met
- [ ] **3.4** Commit transaction
- [ ] **3.5** Return unlock result with quest details

### Task 4: Create In-App Notifications (AC: #4)

- [ ] **4.1** Create `Notification` model if not exists:
  - id, user_id, type, title, message, data JSONB, read_at, created_at
- [ ] **4.2** Implement `create_quest_unlock_notification()` in notification_service
- [ ] **4.3** Populate notification data:
  - Title: Quest title from scenario template
  - Message: Narrative context
  - Data: {quest_id, rewards, time_limit_hours, expires_at}
- [ ] **4.4** Save notification to database
- [ ] **4.5** Trigger real-time notification delivery (WebSocket or polling)

### Task 5: Create Eliza Messages for Quest Unlocks (AC: #5)

- [ ] **5.1** Create `queue_eliza_quest_message()` in companion_service
- [ ] **5.2** Construct Eliza message:
  - Tone: Excited, supportive
  - Content: Narrative context + quest introduction
  - CTA: "Ready to embark on this special quest?"
- [ ] **5.3** Store message in companion messages table
- [ ] **5.4** Set message type: "quest_unlock"
- [ ] **5.5** Mark as unread for user

### Task 6: Integrate with Mission System (AC: #6)

- [ ] **6.1** Update `Mission` model to include:
  - `is_hidden_quest` BOOLEAN DEFAULT FALSE
  - `hidden_quest_id` VARCHAR (references scenario template quest)
  - `quest_rewards` JSONB (essence, title, artifact, etc.)
- [ ] **6.2** Create mission from hidden quest on unlock:
  - Convert quest to Mission object
  - Set is_hidden_quest = TRUE
  - Set special visual markers
  - Set time limit (expires_at) if applicable
- [ ] **6.3** Update mission service to handle hidden quests:
  - Filter hidden quests separately
  - Apply special sorting (top of mission list)
  - Track completion separately
- [ ] **6.4** Create migration for new Mission fields

### Task 7: Implement Time-Limited Quest Logic (AC: #7)

- [ ] **7.1** Add `calculate_quest_deadline()` helper:
  - deadline = unlocked_at + timedelta(hours=time_limit_hours)
- [ ] **7.2** Add `check_quest_expired()` function:
  - Compare current_time to deadline
  - Return boolean
- [ ] **7.3** Create expiration worker (runs hourly):
  - Query quests with deadlines approaching
  - Mark expired quests
  - Send expiration notifications
- [ ] **7.4** Create warning notification system:
  - Send notification 24 hours before expiration
  - "Your special quest expires in 24 hours!"

### Task 8: Add Analytics Logging (AC: #8)

- [ ] **8.1** Add structured logging to worker:
  - Users processed count
  - Quests unlocked count
  - Quest breakdown by ID
  - Processing time
- [ ] **8.2** Create analytics events:
  - Event: "hidden_quest_unlocked"
  - Properties: quest_id, user_id, trigger_type, time_to_unlock_days
- [ ] **8.3** Add dashboard metrics (optional):
  - Quest unlock rates
  - Popular quests
  - Average time to unlock

### Task 9: Create API Endpoints (AC: #4, #6)

- [ ] **9.1** Add to `app/api/v1/narrative.py`:
  - `GET /api/v1/narrative/hidden-quests` - Returns unlocked quests for user
  - `POST /api/v1/narrative/hidden-quests/{quest_id}/complete` - Mark quest complete
- [ ] **9.2** Add Pydantic schemas:
  - `HiddenQuestResponse`: id, title, rewards, narrative_context, time_limit, expires_at
  - `HiddenQuestsListResponse`: unlocked[], progress_hints[]
- [ ] **9.3** Add authentication middleware
- [ ] **9.4** Add rate limiting

### Task 10: Create Unit Tests (AC: All)

- [ ] **10.1** Create `tests/services/test_quest_trigger_evaluator.py`
- [ ] **10.2** Test each trigger type with various user progress scenarios
- [ ] **10.3** Test edge cases (exactly at threshold, just under threshold)
- [ ] **10.4** Test combination triggers (multiple conditions)
- [ ] **10.5** Test trigger evaluation with mock data

### Task 11: Create Integration Tests (AC: #1, #3, #4, #5)

- [ ] **11.1** Create `tests/integration/test_hidden_quest_system.py`
- [ ] **11.2** Test complete unlock flow:
  - Create test user with specific progress pattern
  - Run worker
  - Verify quest unlocked
  - Verify notification created
  - Verify Eliza message queued
  - Verify mission created
- [ ] **11.3** Test time-limited quests:
  - Unlock quest
  - Verify deadline calculated
  - Test expiration logic
- [ ] **11.4** Test worker execution manually
- [ ] **11.5** Test analytics logging

### Task 12: Documentation (AC: All)

- [ ] **12.1** Document trigger types and examples
- [ ] **12.2** Document quest unlock flow
- [ ] **12.3** Create `docs/epic-4/HIDDEN-QUESTS-GUIDE.md`:
  - How to create new hidden quests
  - Trigger condition reference
  - Reward types
  - Time limit best practices
- [ ] **12.4** Update API documentation
- [ ] **12.5** Add code comments for trigger evaluation logic

---

## Dev Notes

### Hidden Quest Design Philosophy

**From Epics (epics.md lines 1049-1093):**

Hidden quests create delightful surprises by:

1. **Remaining Secret**: Users don't know what quests exist until unlock
2. **Rewarding Patterns**: Different behaviors trigger different quests
3. **Creating Narrative Moments**: Quest unlocks advance the story
4. **Building Anticipation**: Users wonder "what else is hidden?"

**Examples from Modern Reality Scenario:**

1. **The Relentless** (Craft Focus):
   - Trigger: 20-day streak with craft as dominant value
   - Reward: Title "The Relentless", 500 Essence, +2 Lyra relationship
   - Narrative: "Your unwavering dedication to craft has awakened something ancient..."

2. **Century Milestone** (Volume):
   - Trigger: 100 missions completed
   - Reward: Title "The Hundred Steps", 1000 Essence, medallion artifact
   - Narrative: "A century of actions completed. The world takes notice."
   - Time limit: 72 hours (creates urgency)

3. **The Balanced Path** (Variety):
   - Trigger: Equal missions across all 4 values for 14 consecutive days
   - Reward: Title "The Harmonious", unlock Observatory location
   - Narrative: "Your balanced approach reveals a hidden path..."

### Trigger Evaluation Implementation

**Streak-Based Triggers:**

```python
def _evaluate_streak_trigger(trigger, user_progress):
    """
    Trigger format: {"streak_days": 20, "attribute": "craft"}
    """
    required_days = trigger.get("streak_days")
    required_attribute = trigger.get("attribute")

    current_streak = user_progress.get("current_streak_days", 0)
    streak_attribute = user_progress.get("streak_attribute")

    if required_attribute:
        # Must have streak in specific attribute
        return current_streak >= required_days and streak_attribute == required_attribute
    else:
        # Any streak of N days
        return current_streak >= required_days
```

**Balance Triggers (Complex):**

```python
def _evaluate_balance_trigger(trigger, user_progress):
    """
    Trigger format: {"equal_value_distribution": 14}
    Checks if last N days had equal distribution across all values.
    Equal = within 25% variance (e.g., 22-28% for each of 4 values).
    """
    days = trigger.get("equal_value_distribution")

    # Get mission distribution for last N days
    distribution = user_progress.get(f"value_distribution_{days}d", {})

    # Check if all values within 25% variance
    values = list(distribution.values())
    if len(values) != 4:
        return False

    avg = sum(values) / 4
    max_variance = 0.25  # 25%

    for value in values:
        if abs(value - avg) > max_variance:
            return False

    return True
```

**Time-Based Triggers:**

```python
def _evaluate_time_trigger(trigger, user_progress):
    """
    Trigger format: {"missions_after_10pm": 30}
    Counts missions completed after specific time.
    """
    required_count = trigger.get("missions_after_10pm")
    time_threshold = 22  # 10 PM = 22:00

    # Query missions where completed_at hour >= time_threshold
    late_night_count = user_progress.get("missions_after_22h", 0)

    return late_night_count >= required_count
```

### Worker Implementation Pattern

**ARQ Worker Structure:**

```python
# app/workers/quest_generator.py

from arq import cron
from datetime import datetime
import asyncio

async def hidden_quest_detector(ctx):
    """
    Daily worker to check hidden quest triggers for all users.
    Runs at 2:00 AM daily.
    """
    logger.info("Starting hidden quest detection batch")
    start_time = datetime.now()

    async with get_db() as db:
        # Query all users with narrative states
        result = await db.execute(
            select(NarrativeState).options(selectinload(NarrativeState.user))
        )
        narrative_states = result.scalars().all()

        users_processed = 0
        quests_unlocked = 0
        quest_breakdown = {}

        for narrative_state in narrative_states:
            try:
                # Load scenario template
                scenario = await db.get(ScenarioTemplate, narrative_state.scenario_id)

                # Load user progress
                user_progress = await get_user_progress_summary(db, narrative_state.user_id)

                # Evaluate triggers
                for hidden_quest in scenario.hidden_quests:
                    quest_id = hidden_quest["id"]

                    # Skip if already unlocked
                    if quest_id in narrative_state.unlocked_quests:
                        continue

                    # Evaluate trigger
                    trigger_met = evaluate_trigger(hidden_quest["trigger"], user_progress)

                    if trigger_met:
                        # Unlock quest
                        await unlock_hidden_quest(db, narrative_state, hidden_quest)
                        quests_unlocked += 1
                        quest_breakdown[quest_id] = quest_breakdown.get(quest_id, 0) + 1

                users_processed += 1

            except Exception as e:
                logger.error(f"Error processing user {narrative_state.user_id}: {e}")
                continue

    processing_time = (datetime.now() - start_time).total_seconds() * 1000

    logger.info("Hidden quest detection batch complete", extra={
        "users_processed": users_processed,
        "quests_unlocked": quests_unlocked,
        "quest_breakdown": quest_breakdown,
        "processing_time_ms": processing_time
    })

    return {
        "users_processed": users_processed,
        "quests_unlocked": quests_unlocked,
        "quest_breakdown": quest_breakdown
    }


class WorkerSettings:
    redis_settings = get_redis_settings()
    functions = [hidden_quest_detector]
    cron_jobs = [
        cron(hidden_quest_detector, hour=2, minute=0)  # 2:00 AM daily
    ]
```

### Notification Integration

**In-App Notification:**

```python
# app/services/notification_service.py

async def create_quest_unlock_notification(db, user_id, quest_data):
    """Create notification for hidden quest unlock."""
    notification = Notification(
        user_id=user_id,
        type="hidden_quest_unlock",
        title=quest_data["title"],
        message=quest_data["narrative_context"],
        data={
            "quest_id": quest_data["id"],
            "rewards": quest_data["rewards"],
            "time_limit_hours": quest_data.get("time_limit_hours"),
            "expires_at": calculate_deadline(quest_data) if quest_data.get("time_limit_hours") else None
        }
    )

    db.add(notification)
    await db.commit()

    # Trigger real-time notification delivery (WebSocket or push)
    await send_realtime_notification(user_id, notification)

    return notification
```

**Eliza Message:**

```python
# app/services/companion_service.py

async def queue_eliza_quest_message(db, user_id, quest_data):
    """Queue Eliza message about quest unlock."""
    message_text = f"""✨ {quest_data['narrative_context']}

I've sensed something special unlock for you: **{quest_data['title']}**.

This quest offers unique rewards:
- {format_rewards(quest_data['rewards'])}

{"⏰ Complete within " + str(quest_data['time_limit_hours']) + " hours!" if quest_data.get('time_limit_hours') else ""}

Ready to embark on this special quest? You'll find it marked as "Special" in your mission pool."""

    companion_message = CompanionMessage(
        user_id=user_id,
        sender="Eliza",
        message_type="quest_unlock",
        content=message_text,
        metadata={"quest_id": quest_data["id"]}
    )

    db.add(companion_message)
    await db.commit()

    return companion_message
```

### Learnings from Previous Stories

**From Story 4.2 (Narrative Agent):**

- check_unlocks node already detects quests to unlock
- This story implements the worker that runs nightly (Story 4.2 runs on-demand)
- Trigger evaluation logic can be shared

**From Story 4.1 (Narrative Schema):**

- hidden_quests already defined in scenario_templates
- unlocked_quests array already exists in narrative_states
- Just need to implement trigger evaluation and unlocking logic

**From Epic 3 (Missions - assumed):**

- Mission model exists with completion tracking
- Progress tracking provides streak and count data
- Can extend Mission model for hidden quests

### Project Structure Notes

**Modified Files:**

```
packages/backend/
├── app/
│   ├── workers/
│   │   └── quest_generator.py              # UPDATE: Add hidden quest detection
│   ├── services/
│   │   ├── quest_trigger_evaluator.py      # NEW: Trigger evaluation logic
│   │   ├── notification_service.py         # UPDATE: Add quest notifications
│   │   └── companion_service.py            # UPDATE: Add quest messages
│   ├── models/
│   │   ├── notification.py                 # NEW: Notification model
│   │   └── mission.py                      # UPDATE: Add hidden quest fields
│   └── api/v1/
│       └── narrative.py                     # UPDATE: Add hidden quest endpoints
└── tests/
    ├── services/
    │   └── test_quest_trigger_evaluator.py # NEW: Trigger tests
    └── integration/
        └── test_hidden_quest_system.py     # NEW: End-to-end tests
```

### Relationship to Epic 4 Stories

This story (4.3) **uses**:

- **Story 4.1**: scenario_templates.hidden_quests, narrative_states.unlocked_quests
- **Story 4.2**: check_unlocks node logic (can share trigger evaluation)

This story (4.3) **enables**:

- **Story 4.4**: Hidden quests appear in story UI as unlocked
- **Story 4.7**: Essence rewards from quests used for lore unlocking

**Dependencies Flow:**

```
Story 4.1 (Narrative Schema)
    ↓
Story 4.2 (Narrative Agent)
    ↓
Story 4.3 (Hidden Quest System) ← THIS STORY
    ↓
Story 4.4 (Story UI) - displays unlocked quests
```

### References

**Source Documents:**

- **Epic 4 Tech Spec**: `docs/tech-spec-epic-4.md` (Hidden quests structure)
- **Epics File**: `docs/epics.md` (Story 4.3 requirements, lines 1049-1093)
- **Architecture**: `docs/ARCHITECTURE.md` (ARQ workers, background jobs)

**Technical Documentation:**

- **ARQ**: https://arq-docs.helpmanual.io/
- **PostgreSQL Arrays**: https://www.postgresql.org/docs/current/arrays.html
- **JSONB Updates**: https://www.postgresql.org/docs/current/functions-json.html

---

## Definition of Done

- [ ] ✅ ARQ worker created for nightly hidden quest detection (2:00 AM)
- [ ] ✅ Trigger evaluation logic implemented for all 5 trigger types
- [ ] ✅ Quest unlocking updates narrative_states correctly
- [ ] ✅ In-app notifications created for quest unlocks
- [ ] ✅ Eliza messages queued for quest unlocks
- [ ] ✅ Quests appear in mission pool marked as "Special"
- [ ] ✅ Time-limited quests enforce deadlines and expiration
- [ ] ✅ Analytics logging captures unlock events
- [ ] ✅ API endpoints created for hidden quest retrieval
- [ ] ✅ Unit tests pass for trigger evaluation
- [ ] ✅ Integration tests pass for complete unlock flow
- [ ] ✅ Worker runs successfully in test environment
- [ ] ✅ Documentation complete (trigger types, quest guide)
- [ ] ✅ No secrets committed
- [ ] ✅ Code follows async patterns
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline

- **Task 1** (Worker Extension): 1 hour
- **Task 2** (Trigger Evaluation): 2 hours
- **Task 3** (Quest Unlocking): 1 hour
- **Task 4** (Notifications): 1 hour
- **Task 5** (Eliza Messages): 1 hour
- **Task 6** (Mission Integration): 1.5 hours
- **Task 7** (Time Limits): 1 hour
- **Task 8** (Analytics): 30 minutes
- **Task 9** (API Endpoints): 1 hour
- **Task 10** (Unit Tests): 1.5 hours
- **Task 11** (Integration Tests): 1.5 hours
- **Task 12** (Documentation): 1 hour

**Total:** 14 hours (within 6-8 hour estimate with efficient execution focusing on core features)

### Risk Mitigation

**Risk:** Trigger evaluation too slow (>10 seconds per user)

- **Mitigation**: Optimize queries, cache user progress data, use database indexes
- **Impact**: Low (worker runs overnight, not time-sensitive)

**Risk:** Users don't notice quest unlocks

- **Mitigation**: Prominent notifications, Eliza messages, special visual treatment in UI
- **Impact**: Medium (reduces engagement value)

**Risk:** Time-limited quests expire before users see them

- **Mitigation**: Send notification immediately on unlock, send 24-hour warning, reasonable time limits (72+ hours)
- **Impact**: Medium (frustrating user experience)

**Risk:** Trigger conditions too hard/easy

- **Mitigation**: Track unlock rates, adjust triggers based on analytics, A/B test thresholds
- **Impact**: High (affects engagement and reward balance)

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Create context file, then implement worker, trigger evaluation, and notification system
