# POC: Real-Time Streaming Workflows

## Overview

This proof-of-concept demonstrates how to add Server-Sent Events (SSE) streaming to the multi-step prompting system, transforming the UX from "batch and wait" to "real-time and responsive."

**Impact**: Users see live progress instead of waiting blindly for results.

---

## Current vs. Proposed

### Current Experience ❌

```
User: "Research AI in healthcare"
[POST /api/v1/workflows/{id}/execute]

User sees: "Workflow running..." 🔄
[... 60 seconds of silence ...]

User thinks: "Is it stuck? What's happening?"
[... more waiting ...]

Finally: Results appear! ✅
```

**Problems**:
- No visibility into progress
- Anxiety about whether it's working
- Can't cancel if going wrong direction
- Feels slow even if objectively fast

### Proposed Experience ✅

```
User: "Research AI in healthcare"
[GET /api/v1/workflows/{id}/stream - SSE connection]

 0% [⏳] Planning research approach...
20% [✓] Plan complete: Will research diagnostics, treatment, patient care
25% [⏳] Researching AI diagnostics...
35% [📊] Found: AI diagnostics accuracy 94% vs 88% human
50% [⏳] Researching AI treatment planning...
65% [📊] Found: AI reduces treatment planning time by 40%
75% [⏳] Researching AI patient care...
85% [📊] Found: AI chatbots handle 70% of routine inquiries
90% [⏳] Synthesizing findings...
100% [✅] Complete! Here's your comprehensive report...
```

**Benefits**:
- Real-time visibility
- Perceived performance 10x better
- Can cancel early if wrong direction
- Engaging, not boring

---

## Implementation

### 1. Add Event Emission to Task Execution

```python
# app/agents/events.py
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class WorkflowEventType(str, Enum):
    """Types of workflow events."""

    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    ITERATION_STARTED = "iteration_started"
    ITERATION_COMPLETED = "iteration_completed"

class WorkflowEvent(BaseModel):
    """Event emitted during workflow execution."""

    event_type: WorkflowEventType
    workflow_id: UUID
    task_id: Optional[UUID] = None
    task_name: Optional[str] = None
    progress_percent: float
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format."""
        return f"event: {self.event_type}\ndata: {self.model_dump_json()}\n\n"
```

### 2. Add Event Bus to Workflow

```python
# app/agents/task_types.py
from asyncio import Queue
from typing import AsyncIterator

class Workflow(BaseModel):
    # ... existing fields

    _event_queue: Optional[Queue] = None  # Private field for events

    def enable_streaming(self):
        """Enable event streaming for this workflow."""
        self._event_queue = Queue()

    async def emit_event(self, event: WorkflowEvent):
        """Emit an event to all listeners."""
        if self._event_queue:
            await self._event_queue.put(event)

    async def stream_events(self) -> AsyncIterator[WorkflowEvent]:
        """Stream events as they occur."""
        if not self._event_queue:
            raise ValueError("Streaming not enabled for this workflow")

        while True:
            event = await self._event_queue.get()
            yield event

            # Stop streaming when workflow completes
            if event.event_type in [
                WorkflowEventType.WORKFLOW_COMPLETED,
                WorkflowEventType.WORKFLOW_FAILED
            ]:
                break
```

### 3. Update Orchestrator to Emit Events

```python
# app/agents/orchestrator.py
class WorkflowOrchestrator:
    async def execute_workflow(self, workflow: Workflow) -> Workflow:
        """Execute workflow with event emission."""

        # Enable streaming if not already enabled
        if not workflow._event_queue:
            workflow.enable_streaming()

        # Emit start event
        await workflow.emit_event(WorkflowEvent(
            event_type=WorkflowEventType.WORKFLOW_STARTED,
            workflow_id=workflow.id,
            progress_percent=0.0,
            message=f"Starting workflow: {workflow.name}"
        ))

        workflow.status = TaskStatus.RUNNING
        workflow.started_at = datetime.utcnow()

        try:
            # Execute workflow iterations
            for depth in range(self.config.depth):
                workflow.current_depth = depth + 1

                # Emit iteration start
                await workflow.emit_event(WorkflowEvent(
                    event_type=WorkflowEventType.ITERATION_STARTED,
                    workflow_id=workflow.id,
                    progress_percent=self._calculate_progress(workflow),
                    message=f"Iteration {depth + 1}/{self.config.depth}"
                ))

                # Execute iteration
                await self._execute_iteration(workflow)

                # Emit iteration complete
                await workflow.emit_event(WorkflowEvent(
                    event_type=WorkflowEventType.ITERATION_COMPLETED,
                    workflow_id=workflow.id,
                    progress_percent=self._calculate_progress(workflow),
                    message=f"Completed {workflow.current_depth} iterations"
                ))

                if workflow.is_complete():
                    break

            # Emit completion event
            workflow.status = TaskStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()

            await workflow.emit_event(WorkflowEvent(
                event_type=WorkflowEventType.WORKFLOW_COMPLETED,
                workflow_id=workflow.id,
                progress_percent=100.0,
                message="Workflow completed successfully",
                data={"results": workflow.results}
            ))

        except Exception as e:
            workflow.status = TaskStatus.FAILED
            await workflow.emit_event(WorkflowEvent(
                event_type=WorkflowEventType.WORKFLOW_FAILED,
                workflow_id=workflow.id,
                progress_percent=self._calculate_progress(workflow),
                message=f"Workflow failed: {str(e)}"
            ))

        return workflow

    def _calculate_progress(self, workflow: Workflow) -> float:
        """Calculate workflow progress percentage."""
        if not workflow.tasks:
            return 0.0

        completed = sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(workflow.tasks)) * 100.0
```

### 4. Update Executors to Emit Task Events

```python
# app/agents/executors.py
class SequentialExecutor(TaskExecutor):
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with event emission."""

        # Get workflow from context
        workflow = context.get("workflow")

        # Emit task start event
        if workflow:
            await workflow.emit_event(WorkflowEvent(
                event_type=WorkflowEventType.TASK_STARTED,
                workflow_id=workflow.id,
                task_id=task.id,
                task_name=task.name,
                progress_percent=workflow._calculate_progress(),
                message=f"Starting task: {task.name}"
            ))

        try:
            # Mark running
            task.mark_running()

            # Execute with timeout
            result = await asyncio.wait_for(
                self._run_task(task, context),
                timeout=self.timeout_seconds
            )

            # Mark completed
            task.mark_completed(result)

            # Emit completion event
            if workflow:
                await workflow.emit_event(WorkflowEvent(
                    event_type=WorkflowEventType.TASK_COMPLETED,
                    workflow_id=workflow.id,
                    task_id=task.id,
                    task_name=task.name,
                    progress_percent=workflow._calculate_progress(),
                    message=f"Completed: {task.name}",
                    data={"result": result}
                ))

            return result

        except Exception as e:
            task.mark_failed(str(e))

            # Emit failure event
            if workflow:
                await workflow.emit_event(WorkflowEvent(
                    event_type=WorkflowEventType.TASK_FAILED,
                    workflow_id=workflow.id,
                    task_id=task.id,
                    task_name=task.name,
                    progress_percent=workflow._calculate_progress(),
                    message=f"Task failed: {task.name} - {str(e)}"
                ))

            raise
```

### 5. Add SSE Endpoint

```python
# app/api/v1/workflows.py
from fastapi.responses import StreamingResponse
from typing import AsyncIterator

@router.get("/{workflow_id}/stream")
async def stream_workflow_progress(workflow_id: UUID):
    """
    Stream workflow progress via Server-Sent Events.

    This endpoint establishes an SSE connection and streams real-time
    updates about workflow execution progress.

    Example:
        const eventSource = new EventSource('/api/v1/workflows/{id}/stream');

        eventSource.addEventListener('task_started', (event) => {
            const data = JSON.parse(event.data);
            console.log(`Task started: ${data.task_name}`);
        });

        eventSource.addEventListener('task_completed', (event) => {
            const data = JSON.parse(event.data);
            console.log(`Task completed: ${data.task_name}`);
        });
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]

    # Enable streaming if not already
    if not workflow._event_queue:
        workflow.enable_streaming()

    async def event_stream() -> AsyncIterator[str]:
        """Generate Server-Sent Events."""

        # Send initial connection message
        yield f"data: {json.dumps({'status': 'connected', 'workflow_id': str(workflow_id)})}\n\n"

        try:
            # Stream events from workflow
            async for event in workflow.stream_events():
                yield event.to_sse()

        except asyncio.CancelledError:
            # Client disconnected
            yield f"event: disconnected\ndata: {json.dumps({'status': 'client_disconnected'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

### 6. Update Execute Endpoint to Support Streaming

```python
# app/api/v1/workflows.py
@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: UUID,
    background_tasks: BackgroundTasks,
    stream: bool = False  # New parameter
) -> WorkflowResponse:
    """Execute a workflow with optional streaming."""

    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]

    # ... existing validation ...

    # Enable streaming if requested
    if stream:
        workflow.enable_streaming()

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(config=workflow.config)
    _orchestrators[workflow_id] = orchestrator

    # Set status to RUNNING
    workflow.status = TaskStatus.RUNNING
    workflow.started_at = datetime.utcnow()

    # Execute workflow in background
    async def run_workflow():
        try:
            await orchestrator.execute_workflow(workflow)
        except Exception as e:
            workflow.status = TaskStatus.FAILED
            workflow.results["error"] = str(e)
        finally:
            # Clean up orchestrator
            if workflow_id in _orchestrators:
                del _orchestrators[workflow_id]

    background_tasks.add_task(run_workflow)

    response = _convert_workflow_to_response(workflow)

    # Add streaming URL if enabled
    if stream:
        response.metadata = response.metadata or {}
        response.metadata["stream_url"] = f"/api/v1/workflows/{workflow_id}/stream"

    return response
```

---

## Frontend Integration

### React Hook for Streaming

```typescript
// hooks/useWorkflowStream.ts
import { useEffect, useState } from 'react';

interface WorkflowEvent {
  event_type: string;
  workflow_id: string;
  task_id?: string;
  task_name?: string;
  progress_percent: number;
  message: string;
  data?: any;
  timestamp: string;
}

export function useWorkflowStream(workflowId: string) {
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'failed'>('idle');

  useEffect(() => {
    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/workflows/${workflowId}/stream`
    );

    eventSource.addEventListener('workflow_started', (event) => {
      const data: WorkflowEvent = JSON.parse(event.data);
      setStatus('running');
      setEvents(prev => [...prev, data]);
    });

    eventSource.addEventListener('task_started', (event) => {
      const data: WorkflowEvent = JSON.parse(event.data);
      setCurrentTask(data.task_name || null);
      setProgress(data.progress_percent);
      setEvents(prev => [...prev, data]);
    });

    eventSource.addEventListener('task_completed', (event) => {
      const data: WorkflowEvent = JSON.parse(event.data);
      setProgress(data.progress_percent);
      setEvents(prev => [...prev, data]);
    });

    eventSource.addEventListener('workflow_completed', (event) => {
      const data: WorkflowEvent = JSON.parse(event.data);
      setStatus('completed');
      setProgress(100);
      setCurrentTask(null);
      setEvents(prev => [...prev, data]);
      eventSource.close();
    });

    eventSource.addEventListener('workflow_failed', (event) => {
      const data: WorkflowEvent = JSON.parse(event.data);
      setStatus('failed');
      setEvents(prev => [...prev, data]);
      eventSource.close();
    });

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [workflowId]);

  return {
    events,
    progress,
    currentTask,
    status
  };
}
```

### React Component

```typescript
// components/WorkflowProgress.tsx
import { useWorkflowStream } from '@/hooks/useWorkflowStream';

export function WorkflowProgress({ workflowId }: { workflowId: string }) {
  const { events, progress, currentTask, status } = useWorkflowStream(workflowId);

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span>{status === 'running' ? 'Running...' : status}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Current Task */}
      {currentTask && (
        <div className="text-sm text-gray-600">
          <span className="inline-block animate-spin mr-2">⏳</span>
          {currentTask}
        </div>
      )}

      {/* Event Log */}
      <div className="max-h-64 overflow-y-auto space-y-2">
        {events.map((event, idx) => (
          <div
            key={idx}
            className={`text-sm p-2 rounded ${
              event.event_type.includes('completed')
                ? 'bg-green-50 text-green-800'
                : event.event_type.includes('failed')
                ? 'bg-red-50 text-red-800'
                : 'bg-blue-50 text-blue-800'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>
                {event.event_type.includes('completed') ? '✓' :
                 event.event_type.includes('failed') ? '✗' :
                 event.event_type.includes('started') ? '▶' : '•'}
              </span>
              <span className="flex-1">{event.message}</span>
              <span className="text-xs text-gray-500">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
            </div>

            {/* Show result data for completed tasks */}
            {event.data && event.event_type === 'task_completed' && (
              <div className="mt-2 text-xs text-gray-600 pl-6">
                {JSON.stringify(event.data.result, null, 2)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Testing the Implementation

### 1. Start Workflow with Streaming

```bash
# Start workflow
curl -X POST http://localhost:8000/api/v1/workflows/{id}/execute?stream=true

# Response includes stream URL
{
  "id": "...",
  "status": "running",
  "metadata": {
    "stream_url": "/api/v1/workflows/{id}/stream"
  }
}
```

### 2. Connect to Event Stream

```bash
# Using curl
curl -N http://localhost:8000/api/v1/workflows/{id}/stream

# Output (real-time):
data: {"status": "connected", "workflow_id": "..."}

event: workflow_started
data: {"event_type": "workflow_started", "progress_percent": 0, "message": "Starting workflow: Research AI"}

event: task_started
data: {"event_type": "task_started", "task_name": "plan", "progress_percent": 0, "message": "Starting task: plan"}

event: task_completed
data: {"event_type": "task_completed", "task_name": "plan", "progress_percent": 25, "message": "Completed: plan"}

event: task_started
data: {"event_type": "task_started", "task_name": "research_diagnostics", "progress_percent": 25, "message": "Starting task: research_diagnostics"}

...
```

### 3. Frontend Usage

```typescript
function ResearchPage() {
  const [workflowId, setWorkflowId] = useState<string | null>(null);

  const handleStartResearch = async () => {
    // Create and execute workflow
    const response = await fetch('/api/v1/workflows/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'Research AI in Healthcare',
        tasks: [/* ... */],
        config: { breadth: 3, depth: 5 }
      })
    });

    const workflow = await response.json();

    // Execute with streaming
    await fetch(`/api/v1/workflows/${workflow.id}/execute?stream=true`, {
      method: 'POST'
    });

    // Set ID to trigger streaming hook
    setWorkflowId(workflow.id);
  };

  return (
    <div>
      <button onClick={handleStartResearch}>
        Start Research
      </button>

      {workflowId && (
        <WorkflowProgress workflowId={workflowId} />
      )}
    </div>
  );
}
```

---

## Performance Considerations

### 1. Event Queue Size Limit

```python
class Workflow(BaseModel):
    _event_queue: Optional[Queue] = None
    _max_queue_size: int = 1000  # Prevent memory issues

    def enable_streaming(self):
        self._event_queue = Queue(maxsize=self._max_queue_size)
```

### 2. Client Connection Timeout

```python
# Close connection if no events for 60 seconds
async def event_stream():
    timeout = 60
    try:
        async for event in workflow.stream_events():
            yield event.to_sse()
    except asyncio.TimeoutError:
        yield "event: timeout\ndata: {}\n\n"
```

### 3. Graceful Client Disconnect

```python
# Detect client disconnect
async def event_stream():
    try:
        async for event in workflow.stream_events():
            yield event.to_sse()
    except asyncio.CancelledError:
        # Client disconnected - clean up
        logger.info(f"Client disconnected from workflow {workflow_id}")
        raise
```

---

## Migration Strategy

### Phase 1: Add Streaming (No Breaking Changes)

1. Add event types and WorkflowEvent model
2. Add optional `_event_queue` to Workflow
3. Add `enable_streaming()` method
4. Add SSE endpoint
5. Keep existing batch API working

### Phase 2: Update Orchestrator (Backward Compatible)

1. Add event emission to orchestrator
2. Make it conditional on streaming being enabled
3. Non-streaming workflows work exactly as before

### Phase 3: Update UI (Progressive Enhancement)

1. Add streaming components
2. Fall back to polling if SSE not supported
3. Gradual rollout to users

---

## Benefits

### For Users
- ✅ 10x better perceived performance
- ✅ Real-time visibility into AI thinking
- ✅ Can cancel early if wrong direction
- ✅ Engaging experience vs. boring wait

### For Development
- ✅ Easy to debug workflows
- ✅ Better monitoring and observability
- ✅ Client-side caching of events
- ✅ Foundation for advanced features (pause/resume, etc.)

### For Business
- ✅ Higher user engagement
- ✅ Lower perceived latency
- ✅ Better trust in AI system
- ✅ Competitive differentiator

---

## Next Steps

1. **This Week**: Implement basic SSE endpoint (4-6 hours)
2. **Next Week**: Add event emission to orchestrator (1-2 days)
3. **Week 3**: Build React streaming UI (2-3 days)
4. **Week 4**: Production testing and refinement

**Total Effort**: 5-7 days for complete feature
**ROI**: Massive UX improvement for minimal effort

---

**Status**: Ready for Implementation
**Priority**: CRITICAL (Highest impact on user experience)
**Dependencies**: None (can be added incrementally)
