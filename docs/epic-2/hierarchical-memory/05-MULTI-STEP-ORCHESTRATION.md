# Multi-Step Prompting and Orchestration

**Date:** 2025-11-18
**Epic:** Epic 2 - Companion & Memory System (+ Cross-Epic Integration)
**Purpose:** Design patterns for parallel and sequential task orchestration in Delight's AI workflows

---

## Table of Contents

1. [Overview](#overview)
2. [Parallel vs Sequential Execution](#parallel-vs-sequential-execution)
3. [Orchestration Patterns](#orchestration-patterns)
4. [Cross-Epic Workflows](#cross-epic-workflows)
5. [Background Job Orchestration](#background-job-orchestration)
6. [Performance and Cost Optimization](#performance-and-cost-optimization)

---

## Overview

Complex AI tasks require multiple steps: retrieving data, making decisions, calling tools, and synthesizing results. **Multi-step orchestration** determines whether steps run **in parallel** (simultaneously) or **sequentially** (one after another).

### Why Multi-Step Orchestration?

**Without orchestration**:
- Sequential everything → slow (wait for each step)
- Parallel everything → errors (missing dependencies)
- No retry logic → failures leave user stranded

**With intelligent orchestration**:
- ✅ Parallel when possible (3-5x faster)
- ✅ Sequential when needed (correct dependencies)
- ✅ Retry and fallback (reliable experience)

### Design Principles

1. **Maximize Parallelization**: Run independent tasks simultaneously
2. **Respect Dependencies**: Sequential for dependent tasks
3. **Fail Gracefully**: Timeout and retry with exponential backoff
4. **Observable**: Log each step for debugging and monitoring
5. **Cost-Aware**: Batch API calls to reduce costs

---

## Parallel vs Sequential Execution

### When to Use Parallel Execution

**Independent tasks** that don't depend on each other's results:

```python
# ✅ PARALLEL: These can run simultaneously
emotion, memories, progress = await asyncio.gather(
    emotion_service.detect(user_input),      # Independent
    memory_service.retrieve(user_id, query), # Independent
    progress_service.get_dci(user_id)        # Independent
)
```

**Benefits**:
- **Speed**: 3 tasks in 200ms instead of 600ms
- **Throughput**: Handle more requests concurrently
- **User Experience**: Faster responses

**Use Cases**:
- Emotion detection + memory retrieval + context gathering
- Multiple goal analysis in parallel
- Fetching different data sources simultaneously

### When to Use Sequential Execution

**Dependent tasks** where output of one feeds into the next:

```python
# ✅ SEQUENTIAL: Second task needs first task's result
goal = await goal_service.get_goal(goal_id)  # Must happen first
missions = await mission_service.get_missions(goal.id)  # Depends on goal
```

**Benefits**:
- **Correctness**: Ensures data dependencies met
- **Consistency**: Maintains logical flow
- **Debugging**: Easier to trace execution

**Use Cases**:
- Goal decomposition → mission generation → quest content
- User query → memory retrieval → LLM reasoning → response
- Story progression → unlock check → narrative generation

### Hybrid Approach (Parallel + Sequential)

Best of both worlds: parallel where possible, sequential where needed:

```python
# HYBRID: Parallel data gathering, sequential processing

# Step 1: Parallel data collection
user_data, goal_data, progress_data = await asyncio.gather(
    get_user_preferences(user_id),
    get_active_goals(user_id),
    get_recent_progress(user_id)
)

# Step 2: Sequential reasoning (depends on Step 1)
analysis = await analyze_user_state(user_data, goal_data, progress_data)

# Step 3: Parallel action execution (depends on Step 2, but actions independent)
await asyncio.gather(
    create_mission(analysis.suggested_mission),
    send_encouragement(analysis.emotional_state),
    update_narrative(analysis.milestone_reached)
)
```

---

## Orchestration Patterns

### Pattern 1: Fan-Out, Fan-In (Parallel Gather)

**Use Case**: Gather data from multiple sources, synthesize into single result

```python
async def eliza_response_orchestration(
    user_id: str,
    user_input: str,
    context: dict
) -> str:
    """
    Orchestrate Eliza's response with parallel data gathering.

    Flow:
    1. Fan-out: Gather emotion, memories, progress in parallel
    2. Fan-in: Synthesize into context
    3. Sequential: LLM reasoning and response
    """

    # FAN-OUT: Parallel data gathering
    emotion_task = emotion_service.detect(user_input)
    memory_task = memory_service.retrieve(user_id, user_input, context)
    progress_task = progress_service.get_recent(user_id, days=7)

    # GATHER: Wait for all parallel tasks
    emotion, memories, progress = await asyncio.gather(
        emotion_task,
        memory_task,
        progress_task,
        return_exceptions=True  # Don't fail if one task errors
    )

    # Handle errors gracefully
    if isinstance(emotion, Exception):
        logger.error(f"Emotion detection failed: {emotion}")
        emotion = {"dominant": "neutral"}  # Fallback

    if isinstance(memories, Exception):
        logger.error(f"Memory retrieval failed: {memories}")
        memories = {"personal": [], "project": [], "task": []}  # Fallback

    # FAN-IN: Synthesize context
    full_context = {
        "emotional_state": emotion,
        "retrieved_memories": memories,
        "recent_progress": progress,
        "user_input": user_input
    }

    # SEQUENTIAL: LLM reasoning (depends on context)
    response = await generate_response_with_llm(full_context)

    return response
```

### Pattern 2: Sequential Pipeline (Waterfall)

**Use Case**: Multi-step process where each step depends on previous

```python
async def goal_decomposition_pipeline(
    user_id: str,
    goal_id: str
) -> dict:
    """
    Decompose goal into missions (sequential pipeline).

    Flow:
    1. Retrieve goal details
    2. Analyze goal complexity
    3. Generate milestone breakdown
    4. Create mission templates
    5. Store in database
    """

    # Step 1: Get goal
    goal = await goal_service.get_goal(goal_id)

    # Step 2: Analyze complexity (depends on goal)
    complexity_analysis = await analyze_goal_with_llm(
        goal.title,
        goal.description,
        goal.target_date
    )

    # Step 3: Generate milestones (depends on analysis)
    milestones = await generate_milestones_with_llm(
        goal,
        complexity_analysis
    )

    # Step 4: Create missions (depends on milestones)
    missions = []
    for milestone in milestones:
        mission_batch = await generate_missions_for_milestone(
            goal_id,
            milestone
        )
        missions.extend(mission_batch)

    # Step 5: Store in database (depends on missions created)
    await mission_service.create_missions_batch(missions)

    return {
        "goal_id": goal_id,
        "milestones": len(milestones),
        "missions_created": len(missions)
    }
```

### Pattern 3: Conditional Branching

**Use Case**: Different paths based on conditions

```python
async def adaptive_mission_orchestration(
    user_id: str,
    context: dict
) -> dict:
    """
    Generate mission adaptively based on user state.

    Flow:
    1. Assess user emotional state and energy
    2. Branch: If overwhelmed → suggest break
              If energized → generate challenging mission
              If neutral → suggest priority triad
    """

    # Step 1: Parallel assessment
    emotion, energy_level, recent_completions = await asyncio.gather(
        emotion_service.get_current(user_id),
        get_user_energy_level(user_id),
        mission_service.get_recent_completions(user_id, days=1)
    )

    # Step 2: Conditional branching
    if emotion.get("sadness", 0) > 0.7 or energy_level == "low":
        # Path A: Overwhelmed → suggest break or easy mission
        return await suggest_self_care_mission(user_id)

    elif emotion.get("joy", 0) > 0.8 and energy_level == "high":
        # Path B: Energized → challenging mission
        return await generate_challenging_mission(user_id, context)

    elif len(recent_completions) >= 3:
        # Path C: Productive day → celebrate and suggest rest
        return await create_celebration_with_rest(user_id, recent_completions)

    else:
        # Path D: Normal state → priority triad
        return await generate_priority_triad(user_id, context)
```

### Pattern 4: Retry with Exponential Backoff

**Use Case**: Reliable external API calls (LLM, embeddings, etc.)

```python
async def reliable_llm_call(
    prompt: str,
    model: str = "gpt-4o-mini",
    max_retries: int = 3
) -> str:
    """
    Call LLM with retry logic and exponential backoff.

    Retry delays: 2s, 4s, 8s
    """

    for attempt in range(max_retries):
        try:
            response = await call_llm(prompt, model=model)
            return response

        except RateLimitError as e:
            if attempt < max_retries - 1:
                delay = 2 ** attempt  # 2, 4, 8 seconds
                logger.warning(f"Rate limited, retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error("Max retries exceeded for LLM call")
                raise

        except APIError as e:
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                logger.warning(f"API error, retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error("Max retries exceeded for LLM call")
                raise

    # Should never reach here, but fallback
    return "I'm having trouble processing that right now."
```

### Pattern 5: Batched Parallel Execution

**Use Case**: Process many items in parallel with concurrency limit

```python
import asyncio
from asyncio import Semaphore

async def process_missions_batch(
    user_id: str,
    mission_ids: list[str],
    max_concurrent: int = 5
) -> list:
    """
    Process multiple missions in parallel with concurrency limit.

    Prevents overwhelming system with too many simultaneous tasks.
    """

    semaphore = Semaphore(max_concurrent)

    async def process_with_limit(mission_id: str):
        async with semaphore:  # Limit concurrent tasks
            return await process_mission(user_id, mission_id)

    # Create tasks for all missions
    tasks = [process_with_limit(mid) for mid in mission_ids]

    # Gather results (max 5 concurrent)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

---

## Cross-Epic Workflows

### Epic 2 + Epic 3: Goal Creation with Memory

```python
async def create_goal_with_memory_workflow(
    user_id: str,
    goal_title: str,
    goal_description: str
) -> dict:
    """
    Create goal and initialize memory context.

    Parallel:
    - Emotion detection (why is user creating this goal?)
    - Retrieve similar past goals (has user tried similar before?)

    Sequential:
    - Create goal (Epic 3)
    - Create project memory (Epic 2)
    - Trigger decomposition (Epic 3)
    """

    # PARALLEL: Gather context
    emotion, past_goals = await asyncio.gather(
        emotion_service.detect(goal_description),
        memory_service.retrieve(user_id, f"goals similar to {goal_title}")
    )

    # SEQUENTIAL: Create goal
    goal = await goal_service.create_goal(
        user_id=user_id,
        title=goal_title,
        description=goal_description,
        emotional_driver=emotion.get("dominant")
    )

    # SEQUENTIAL: Create project memory (depends on goal creation)
    await create_memory(
        db=db,
        user_id=user_id,
        content=f"User created goal '{goal_title}'. Motivation: {goal_description}",
        memory_type="project",
        metadata={"goal_id": goal.id, "emotional_state": emotion},
        tags=["goal_creation", goal.value_category]
    )

    # PARALLEL: Trigger decomposition + notify user
    await asyncio.gather(
        trigger_goal_decomposition_job(goal.id),
        send_goal_creation_confirmation(user_id, goal)
    )

    return {"goal": goal, "emotion": emotion, "past_context": past_goals}
```

### Epic 2 + Epic 4: Narrative Generation with Memory

```python
async def generate_narrative_beat_workflow(
    user_id: str,
    goal_id: str
) -> dict:
    """
    Generate personalized narrative beat using memories.

    Parallel:
    - Retrieve project memories (goal progress)
    - Retrieve personal memories (user preferences)
    - Get current progress stats

    Sequential:
    - Analyze progress triggers
    - Select narrative beat type
    - Generate story content (LLM)
    - Check hidden quest unlocks
    - Store narrative in memory
    """

    # PARALLEL: Data gathering
    project_memories, personal_memories, progress = await asyncio.gather(
        memory_service.get_project_memories(user_id, goal_id),
        memory_service.get_personal_memories(user_id, tags=["narrative_pref"]),
        progress_service.get_goal_progress(user_id, goal_id)
    )

    # SEQUENTIAL: Narrative pipeline
    # Step 1: Analyze triggers
    triggers = analyze_narrative_triggers(progress)

    # Step 2: Select beat (depends on triggers)
    beat_type = select_narrative_beat(triggers, project_memories)

    # Step 3: Generate story (depends on beat selection)
    story_text = await generate_story_with_llm(
        user_id, goal_id, beat_type, progress, project_memories, personal_memories
    )

    # Step 4: Check unlocks (depends on progress)
    unlocks = check_hidden_quest_triggers(progress)

    # Step 5: Store narrative memory
    await create_memory(
        db=db,
        user_id=user_id,
        content=story_text,
        memory_type="project",
        metadata={
            "goal_id": goal_id,
            "beat_type": beat_type,
            "unlocks": unlocks
        },
        tags=["narrative", "story_beat", beat_type]
    )

    return {
        "story": story_text,
        "beat_type": beat_type,
        "unlocks": unlocks
    }
```

### Epic 2 + Epic 5: Progress Insights with Memory

```python
async def generate_weekly_insights_workflow(user_id: str) -> dict:
    """
    Generate weekly insights using memory consolidation.

    Parallel:
    - Retrieve task memories (past 7 days)
    - Calculate DCI score
    - Get mission completion stats

    Sequential:
    - Analyze patterns with LLM
    - Generate actionable insights
    - Store insights in personal memory
    - Create highlight reel (if milestone)
    """

    # PARALLEL: Data collection
    task_memories, dci_score, stats = await asyncio.gather(
        memory_service.get_task_memories(user_id, days=7),
        progress_service.calculate_dci(user_id),
        mission_service.get_completion_stats(user_id, days=7)
    )

    # SEQUENTIAL: Insight generation
    # Step 1: Analyze patterns
    patterns = await analyze_patterns_with_llm(task_memories, stats)

    # Step 2: Generate insights
    insights = await generate_insights_with_llm(patterns, dci_score)

    # Step 3: Store in personal memory
    await create_memory(
        db=db,
        user_id=user_id,
        content=f"Weekly Insight: {insights}",
        memory_type="personal",
        metadata={"dci_score": dci_score, "week": get_current_week()},
        tags=["insight", "weekly_summary", "analytics"]
    )

    # Step 4: Conditional highlight reel
    if dci_score >= 0.8 or stats["streak_days"] >= 7:
        reel = await create_highlight_reel(user_id, insights, stats)
    else:
        reel = None

    return {
        "insights": insights,
        "dci": dci_score,
        "highlight_reel": reel
    }
```

### Epic 2 + Epic 7: Personalized Nudge with Memory

```python
async def generate_personalized_nudge_workflow(user_id: str) -> dict:
    """
    Generate nudge using personal memory preferences.

    Parallel:
    - Retrieve personal memory (preferences)
    - Retrieve project memory (active goals)
    - Get dropoff analysis

    Sequential:
    - Select nudge channel
    - Generate message (LLM with memory context)
    - Schedule send
    - Store nudge in task memory
    """

    # PARALLEL: Context gathering
    preferences, active_goals, dropoff_info = await asyncio.gather(
        memory_service.get_personal_preferences(user_id),
        memory_service.get_project_memories(user_id, tags=["active_goal"]),
        get_dropoff_analysis(user_id)
    )

    # SEQUENTIAL: Nudge pipeline
    # Step 1: Select channel
    channel = select_nudge_channel(dropoff_info["days_inactive"], preferences)

    # Step 2: Generate personalized message
    message = await generate_nudge_with_llm(
        user_id=user_id,
        days_inactive=dropoff_info["days_inactive"],
        active_goals=active_goals,
        preferences=preferences,
        tone=preferences.get("nudge_tone", "encouraging")
    )

    # Step 3: Calculate optimal send time
    send_time = calculate_optimal_send_time(user_id, preferences)

    # Step 4: Schedule
    await schedule_nudge(user_id, channel, message, send_time)

    # Step 5: Log in task memory
    await create_memory(
        db=db,
        user_id=user_id,
        content=f"Nudge scheduled: {dropoff_info['days_inactive']} days inactive, {channel}",
        memory_type="task",
        tags=["nudge", channel, "scheduled"]
    )

    return {
        "channel": channel,
        "message": message,
        "send_time": send_time
    }
```

---

## Background Job Orchestration

### ARQ Worker Patterns

Delight uses **ARQ (async Redis queue)** for background jobs. Orchestration applies to workers too.

#### Pattern: Sequential Multi-Step Job

```python
# backend/app/workers/quest_generator.py

from arq import cron

async def generate_weekly_quests(ctx: dict, user_id: str):
    """
    Background job: Generate quests for upcoming week.

    Sequential pipeline:
    1. Get active goals
    2. Analyze completion patterns
    3. Generate quest templates
    4. Create missions in database
    5. Send notification
    """

    logger.info(f"Generating weekly quests for user {user_id}")

    try:
        # Step 1: Get goals
        goals = await goal_service.get_active_goals(user_id)

        # Step 2: Analyze patterns
        patterns = await analyze_completion_patterns(user_id, days=30)

        # Step 3: Generate quests (LLM)
        quest_templates = await generate_quests_with_llm(goals, patterns)

        # Step 4: Create missions
        missions = await mission_service.create_missions_batch(quest_templates)

        # Step 5: Notify user
        await send_notification(
            user_id,
            f"Your weekly quests are ready! {len(missions)} new missions await."
        )

        logger.info(f"Generated {len(missions)} quests for user {user_id}")

    except Exception as e:
        logger.exception(f"Quest generation failed for {user_id}: {e}")
        raise  # ARQ will retry based on configuration

# Configure ARQ with retry settings
class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [generate_weekly_quests]
    max_tries = 3  # Retry failed jobs 3 times
    job_timeout = 300  # 5 minutes max per job
    retry_delay = 2  # Wait 2 seconds between retries
```

#### Pattern: Parallel Background Jobs

```python
async def nightly_maintenance_jobs(ctx: dict):
    """
    Nightly maintenance: Run multiple independent jobs in parallel.

    Parallel jobs:
    - Prune expired task memories
    - Consolidate weekly progress
    - Update DCI scores
    - Check hidden quest triggers
    """

    logger.info("Starting nightly maintenance jobs")

    # Run all jobs in parallel
    results = await asyncio.gather(
        prune_expired_task_memories(),
        consolidate_weekly_progress(),
        update_all_dci_scores(),
        check_hidden_quest_triggers_all(),
        return_exceptions=True
    )

    # Log results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Job {i} failed: {result}")
        else:
            logger.info(f"Job {i} completed: {result}")

    logger.info("Nightly maintenance complete")
```

---

## Performance and Cost Optimization

### 1. Batch LLM Calls

**Anti-pattern**: Multiple sequential LLM calls
```python
# ❌ SLOW: 3 sequential LLM calls
response1 = await call_llm("Analyze user emotion")
response2 = await call_llm("Suggest mission")
response3 = await call_llm("Generate encouragement")
# Total: ~3 seconds
```

**Pattern**: Single batched LLM call
```python
# ✅ FAST: 1 LLM call with structured output
combined_prompt = """
Analyze the user's emotional state, suggest an appropriate mission, and generate encouragement.

User input: "{user_input}"

Output format:
Emotion: [emotion]
Mission: [mission suggestion]
Encouragement: [encouraging message]
"""

response = await call_llm(combined_prompt)
parsed = parse_structured_response(response)
# Total: ~1 second
```

### 2. Parallel Independent LLM Calls

When multiple LLM calls are needed and independent:

```python
# ✅ PARALLEL: Independent LLM calls
emotion_analysis, mission_suggestion, story_beat = await asyncio.gather(
    call_llm("Analyze emotion", model="gpt-4o-mini"),
    call_llm("Suggest mission", model="gpt-4o-mini"),
    call_llm("Generate story beat", model="gpt-4o")  # Premium model for narrative
)
# Total: ~1.5 seconds (limited by slowest call)
```

### 3. Cache Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_embedding(text: str) -> list[float]:
    """Cache embeddings to avoid regeneration."""
    return generate_embedding(text)

# Usage
embedding = get_cached_embedding(user_input)  # Cached if seen before
```

### 4. Async Database Operations

```python
# ✅ PARALLEL: Multiple independent DB queries
user, goals, missions = await asyncio.gather(
    db.get(User, user_id),
    goal_service.get_active_goals(user_id),
    mission_service.get_pending_missions(user_id)
)
```

---

## Summary

Multi-step orchestration in Delight:

✅ **Parallel execution** for independent tasks (3-5x speedup)
✅ **Sequential execution** for dependent workflows (correctness)
✅ **Hybrid patterns** combining parallel + sequential (optimal performance)
✅ **Retry logic** with exponential backoff (reliability)
✅ **Cross-epic workflows** for cohesive user experience
✅ **Background jobs** with ARQ for async processing
✅ **Cost optimization** through batching and caching

**Key Takeaways**:
1. Identify dependencies before orchestrating
2. Maximize parallelization for speed
3. Use retry logic for external APIs
4. Batch LLM calls when possible
5. Monitor and log each step for debugging

**Next**: Read `06-WORKFLOW-PLANNING.md` for node-based transparent workflow design.

---

**Last Updated**: 2025-11-18
**Status**: Design Specification
**Maintainer**: Jack & Delight Team
