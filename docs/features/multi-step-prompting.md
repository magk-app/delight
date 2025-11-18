# Multi-Step Prompting: Parallelization vs. Serialization

## Overview

The multi-step prompting orchestration system enables Delight to break down complex tasks into smaller, manageable sub-tasks and execute them efficiently using a combination of parallel and sequential execution strategies.

This implementation provides a sophisticated workflow orchestration framework that:
- **Decomposes complex problems** into atomic tasks
- **Executes independent tasks in parallel** to maximize throughput
- **Chains dependent tasks sequentially** to maintain logical flow
- **Manages state and context** across task executions
- **Handles failures with automatic retry** logic
- **Aggregates results** from multiple execution paths

---

## Architecture

### Core Components

#### 1. **Task Model** (`app/agents/task_types.py`)

Represents a single unit of work with:
- **Prompt**: The LLM prompt or action to execute
- **Type**: Sequential, Parallel, or Hybrid execution
- **Status**: Pending, Running, Completed, Failed, Cancelled
- **Dependencies**: Tasks that must complete before this task
- **Context**: Input data and previous task results
- **Result**: Output from task execution
- **Retry Configuration**: Max retries and current attempt count

```python
from app.agents.task_types import Task, TaskType, TaskPriority

task = Task(
    name="Research Topic",
    prompt="Research the latest developments in AI healthcare",
    task_type=TaskType.PARALLEL,
    priority=TaskPriority.HIGH,
    max_retries=3
)
```

#### 2. **Workflow Model** (`app/agents/task_types.py`)

A directed acyclic graph (DAG) of tasks with:
- **Tasks**: Collection of all tasks in the workflow
- **Configuration**: Breadth (parallelization) and depth (iteration) controls
- **Status**: Overall workflow execution status
- **Results**: Aggregated outputs from all tasks

```python
from app.agents.task_types import Workflow, WorkflowConfig

workflow = Workflow(
    name="Healthcare AI Research",
    config=WorkflowConfig(
        breadth=5,  # Max 5 parallel tasks
        depth=10,   # Max 10 sequential iterations
        timeout_seconds=300
    )
)
```

#### 3. **Executors** (`app/agents/executors.py`)

Three execution engines for different strategies:

**SequentialExecutor**
- Executes tasks one after another
- Passes results forward through context
- Ensures proper ordering for dependent logic

**ParallelExecutor**
- Executes independent tasks concurrently
- Respects max parallelism limit (breadth)
- Uses asyncio semaphores for concurrency control

**HybridExecutor**
- Combines both strategies
- Groups independent tasks into parallel stages
- Executes stages sequentially
- Optimal for complex dependency graphs

#### 4. **Orchestrator** (`app/agents/orchestrator.py`)

The main coordinator that:
- Manages workflow execution lifecycle
- Dispatches tasks to appropriate executors
- Handles retry logic and failure recovery
- Aggregates results across iterations
- Implements plan-execute-reflect pattern

---

## Key Concepts

### Sequential Execution

Tasks that must run in order due to dependencies:

```
Task A → Task B → Task C
```

- **Use Case**: When Task B needs output from Task A
- **Example**: Summarize document → Translate summary → Extract key points
- **Implementation**: `TaskType.SEQUENTIAL`

### Parallel Execution

Independent tasks that can run simultaneously:

```
       → Task B →
Task A → Task C → Task D
       → Task E →
```

- **Use Case**: When tasks don't depend on each other
- **Example**: Research economy + Research health + Research education (in parallel)
- **Implementation**: `TaskType.PARALLEL`
- **Controlled by**: `breadth` parameter (max concurrent tasks)

### Hybrid Execution

Combination of both strategies:

```
Stage 1: Task A (sequential)
Stage 2: Task B, Task C, Task D (parallel, depend on A)
Stage 3: Task E (sequential, depends on B+C+D)
```

- **Use Case**: Complex workflows with mixed dependencies
- **Implementation**: `TaskType.HYBRID`
- **Benefit**: Optimal performance through intelligent staging

### Depth and Breadth

**Breadth** (Parallelization)
- Maximum number of tasks to execute simultaneously
- Controls concurrency level
- Higher breadth = more parallelism = faster execution (if resources allow)
- Default: 3

**Depth** (Iteration Cycles)
- Maximum number of sequential iteration rounds
- Enables iterative refinement
- Useful for research tasks that need multiple passes
- Default: 5

---

## API Usage

### 1. Create a Workflow

```bash
POST /api/v1/workflows/
```

**Request:**
```json
{
  "name": "AI Healthcare Research",
  "description": "Research AI applications in healthcare",
  "tasks": [
    {
      "name": "Initial Research",
      "prompt": "Gather general information about AI in healthcare",
      "task_type": "sequential",
      "priority": "high"
    },
    {
      "name": "Research Diagnostics",
      "prompt": "Research AI diagnostic tools",
      "task_type": "parallel",
      "depends_on": ["Initial Research"]
    },
    {
      "name": "Research Treatment",
      "prompt": "Research AI treatment planning",
      "task_type": "parallel",
      "depends_on": ["Initial Research"]
    },
    {
      "name": "Synthesize",
      "prompt": "Synthesize findings into comprehensive report",
      "task_type": "sequential",
      "depends_on": ["Research Diagnostics", "Research Treatment"]
    }
  ],
  "config": {
    "breadth": 3,
    "depth": 5,
    "timeout_seconds": 300,
    "enable_retry": true
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "AI Healthcare Research",
  "status": "pending",
  "tasks": [...],
  "created_at": "2025-11-18T10:00:00Z"
}
```

### 2. Execute Workflow

```bash
POST /api/v1/workflows/{workflow_id}/execute
```

Starts workflow execution in the background.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "started_at": "2025-11-18T10:00:05Z"
}
```

### 3. Check Status

```bash
GET /api/v1/workflows/{workflow_id}/status
```

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 0.5,
  "tasks_completed": 2,
  "tasks_total": 4,
  "current_depth": 1,
  "max_depth": 5,
  "elapsed_seconds": 45.2
}
```

### 4. Get Results

```bash
GET /api/v1/workflows/{workflow_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "tasks": [...],
  "results": {
    "summary": {
      "total_tasks": 4,
      "completed_count": 4,
      "success_rate": 1.0,
      "completed_tasks": [...]
    }
  },
  "completed_at": "2025-11-18T10:01:30Z"
}
```

### 5. Plan-Execute-Reflect Workflow

High-level endpoint that automatically creates a workflow with planning, parallel execution, and reflection phases.

```bash
POST /api/v1/workflows/plan-execute
```

**Request:**
```json
{
  "objective": "Create a comprehensive report on AI in healthcare",
  "context": {
    "focus_areas": ["diagnostics", "treatment", "patient care"]
  },
  "config": {
    "breadth": 5,
    "depth": 10
  }
}
```

---

## Programmatic Usage

### Using WorkflowBuilder

```python
from app.agents.orchestrator import WorkflowBuilder
from app.agents.task_types import TaskType

# Build workflow programmatically
workflow = (
    WorkflowBuilder(name="Research Workflow")
    .with_config(breadth=5, depth=10, timeout_seconds=300)
    .add_task(
        name="initialize",
        prompt="Initialize research on the topic",
        task_type=TaskType.SEQUENTIAL
    )
    .add_parallel_tasks(
        task_specs=[
            {"name": "research_a", "prompt": "Research aspect A"},
            {"name": "research_b", "prompt": "Research aspect B"},
            {"name": "research_c", "prompt": "Research aspect C"},
        ],
        depends_on=["initialize"]
    )
    .add_task(
        name="synthesize",
        prompt="Synthesize all research findings",
        task_type=TaskType.SEQUENTIAL,
        depends_on=["research_a", "research_b", "research_c"]
    )
    .build()
)

# Execute workflow
from app.agents.orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(config=workflow.config)
result = await orchestrator.execute_workflow(workflow)

print(f"Status: {result.status}")
print(f"Results: {result.results['summary']}")
```

### Using Plan-Execute-Reflect Pattern

```python
from app.agents.orchestrator import WorkflowOrchestrator
from app.agents.task_types import WorkflowConfig

# Create orchestrator
config = WorkflowConfig(breadth=5, depth=10)
orchestrator = WorkflowOrchestrator(config=config)

# Execute plan-execute-reflect workflow
workflow = await orchestrator.execute_plan_and_execute_workflow(
    objective="Research AI applications in healthcare",
    context={"domain": "healthcare", "focus": "AI"}
)

# Access results
for task in workflow.tasks:
    print(f"{task.name}: {task.status}")
    if task.result:
        print(f"  Result: {task.result}")
```

---

## Configuration Options

### WorkflowConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `breadth` | int | 3 | Maximum parallel tasks (1-10) |
| `depth` | int | 5 | Maximum iteration cycles (1-20) |
| `timeout_seconds` | int | 300 | Task timeout in seconds |
| `enable_retry` | bool | true | Enable automatic retry on failure |
| `collect_intermediate` | bool | true | Collect intermediate results |

### Task Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Task name |
| `prompt` | string | required | LLM prompt to execute |
| `task_type` | enum | sequential | sequential, parallel, or hybrid |
| `priority` | enum | normal | low, normal, high, critical |
| `depends_on` | list | [] | Task names this depends on |
| `context` | dict | {} | Input context |
| `max_retries` | int | 3 | Maximum retry attempts |

---

## Use Cases

### 1. Deep Research

**Scenario**: Research a complex topic with multiple facets

**Strategy**:
- Plan research areas (sequential)
- Research each area in parallel
- Synthesize findings (sequential)
- Iterate for depth

**Configuration**:
```json
{
  "breadth": 5,  // Research 5 areas simultaneously
  "depth": 10    // Up to 10 refinement iterations
}
```

### 2. Document Processing Pipeline

**Scenario**: Process multiple documents through stages

**Strategy**:
- Load documents (sequential)
- Process each document in parallel
- Aggregate results (sequential)

**Implementation**:
```python
workflow = (
    WorkflowBuilder(name="Document Pipeline")
    .add_task("load", "Load all documents", TaskType.SEQUENTIAL)
    .add_parallel_tasks([
        {"name": f"process_{i}", "prompt": f"Process document {i}"}
        for i in range(num_docs)
    ], depends_on=["load"])
    .add_task("aggregate", "Aggregate results", TaskType.SEQUENTIAL,
              depends_on=[f"process_{i}" for i in range(num_docs)])
    .build()
)
```

### 3. Multi-Agent Collaboration

**Scenario**: Multiple AI agents working on different aspects

**Strategy**:
- Each agent works independently (parallel)
- Consolidate agent outputs (sequential)
- Iterate if needed

**Configuration**:
```json
{
  "breadth": 10,  // Many agents simultaneously
  "depth": 3      // Few refinement rounds
}
```

---

## Performance Characteristics

### Time Complexity

**Sequential Execution**: O(n) where n = number of tasks
- Each task waits for previous task
- Total time = sum of all task durations

**Parallel Execution**: O(n / breadth) where n = number of tasks
- Tasks execute concurrently up to breadth limit
- Total time ≈ max task duration × (n / breadth)

**Hybrid Execution**: O(stages) where stages = DAG depth
- Optimal balance between parallelism and dependencies
- Total time = sum of stage durations

### Best Practices

1. **Maximize Parallelism**: Set high breadth for independent tasks
2. **Minimize Dependencies**: Reduce sequential bottlenecks
3. **Set Appropriate Timeouts**: Balance thoroughness vs. responsiveness
4. **Enable Retry**: Use for unreliable operations
5. **Monitor Progress**: Check status for long-running workflows

---

## Error Handling

### Task Failures

When a task fails:
1. Task status set to `FAILED`
2. Error message stored in `task.error`
3. If `retry_count < max_retries`: task retried automatically
4. If max retries exceeded: task remains failed

### Workflow Failures

Workflow fails when:
- Any task fails permanently (after retries)
- Timeout exceeded
- Circular dependency detected

**Recovery**:
```python
if workflow.has_failures():
    failed_tasks = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
    for task in failed_tasks:
        print(f"Failed: {task.name} - {task.error}")
```

---

## Testing

### Unit Tests

```bash
cd packages/backend
poetry run pytest tests/unit/test_orchestrator.py -v
```

Tests cover:
- Task lifecycle and state transitions
- Dependency resolution
- Sequential execution
- Parallel execution with concurrency limits
- Hybrid execution with complex DAGs
- Workflow builder

### Integration Tests

```bash
poetry run pytest tests/integration/test_workflow_api.py -v
```

Tests cover:
- Workflow creation via API
- Workflow execution
- Status checking
- Result retrieval
- Error scenarios
- Plan-execute workflows

---

## Future Enhancements

### Planned Features

1. **Persistent Storage**: Store workflows in database
2. **LLM Integration**: Connect to actual LLM providers (OpenAI, Anthropic)
3. **Streaming Results**: SSE for real-time progress updates
4. **Workflow Templates**: Pre-built workflows for common patterns
5. **Visual DAG Editor**: UI for building workflows graphically
6. **Cost Tracking**: Monitor LLM API costs per workflow
7. **Performance Analytics**: Track execution times and bottlenecks
8. **Conditional Branching**: Dynamic workflow paths based on results
9. **Sub-workflows**: Nested workflow execution
10. **Checkpointing**: Resume from failure points

### Integration Points

- **LangChain**: Use LangChain for LLM execution
- **LangGraph**: Leverage LangGraph state machines
- **Celery/ARQ**: Distribute execution across workers
- **Redis**: Cache intermediate results
- **WebSocket**: Real-time status updates to frontend

---

## References

- **Task Types**: `packages/backend/app/agents/task_types.py`
- **Executors**: `packages/backend/app/agents/executors.py`
- **Orchestrator**: `packages/backend/app/agents/orchestrator.py`
- **API Endpoints**: `packages/backend/app/api/v1/workflows.py`
- **API Schemas**: `packages/backend/app/schemas/workflow.py`
- **Tests**: `packages/backend/tests/unit/test_orchestrator.py`

---

## Example: Complete Workflow

```python
from app.agents.orchestrator import WorkflowBuilder, WorkflowOrchestrator
from app.agents.task_types import TaskType, WorkflowConfig

# Build comprehensive research workflow
workflow = (
    WorkflowBuilder(
        name="AI Healthcare Impact Research",
        description="Multi-faceted research on AI in healthcare"
    )
    .with_config(breadth=5, depth=10, timeout_seconds=600)

    # Phase 1: Planning
    .add_task(
        name="plan",
        prompt="Create a research plan for AI healthcare impact",
        task_type=TaskType.SEQUENTIAL
    )

    # Phase 2: Parallel Research
    .add_parallel_tasks([
        {
            "name": "research_diagnostics",
            "prompt": "Research AI diagnostic tools and accuracy",
        },
        {
            "name": "research_treatment",
            "prompt": "Research AI treatment planning systems",
        },
        {
            "name": "research_patient_care",
            "prompt": "Research AI patient care improvements",
        },
        {
            "name": "research_administration",
            "prompt": "Research AI healthcare administration",
        },
    ], depends_on=["plan"])

    # Phase 3: Deep Dives (depends on initial research)
    .add_task(
        name="deep_dive_diagnostics",
        prompt="Deep dive into most promising diagnostic AI",
        task_type=TaskType.SEQUENTIAL,
        depends_on=["research_diagnostics"]
    )

    # Phase 4: Synthesis
    .add_task(
        name="synthesize",
        prompt="Synthesize all research into comprehensive report",
        task_type=TaskType.SEQUENTIAL,
        depends_on=[
            "deep_dive_diagnostics",
            "research_treatment",
            "research_patient_care",
            "research_administration"
        ]
    )

    # Phase 5: Review
    .add_task(
        name="review",
        prompt="Review report for accuracy and completeness",
        task_type=TaskType.SEQUENTIAL,
        depends_on=["synthesize"]
    )

    .build()
)

# Execute workflow
orchestrator = WorkflowOrchestrator(config=workflow.config)
result = await orchestrator.execute_workflow(workflow)

# Display results
print(f"\nWorkflow Status: {result.status}")
print(f"Execution Summary: {result.get_execution_summary()}")
print(f"\nFinal Results:")
for key, value in result.results.items():
    print(f"  {key}: {value}")
```

This will execute:
1. **Sequential**: Planning (1 task)
2. **Parallel**: Four research areas simultaneously (breadth=5)
3. **Sequential**: Deep dive into diagnostics
4. **Sequential**: Synthesize all findings
5. **Sequential**: Review final report

Total execution time is significantly reduced through parallelization while maintaining logical flow through dependencies.

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Author**: Delight Development Team
