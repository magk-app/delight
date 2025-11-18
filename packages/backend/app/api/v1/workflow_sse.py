"""
Server-Sent Events (SSE) endpoints for real-time workflow progress updates.
"""

import asyncio
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clerk_auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows/sse", tags=["workflows", "sse"])


# Global progress queue (in production, use Redis pub/sub)
progress_queues: dict[UUID, asyncio.Queue] = {}


async def progress_callback(execution_id: UUID, event_data: dict):
    """
    Callback function to receive progress updates from workflow executor.
    Pushes events to the appropriate queue for SSE streaming.
    """
    if execution_id not in progress_queues:
        progress_queues[execution_id] = asyncio.Queue()

    await progress_queues[execution_id].put(event_data)


async def event_stream_generator(execution_id: UUID, user_id: UUID):
    """
    Generate SSE events for workflow execution progress.

    Yields:
        Formatted SSE events with progress updates
    """
    # Create queue for this execution if it doesn't exist
    if execution_id not in progress_queues:
        progress_queues[execution_id] = asyncio.Queue()

    queue = progress_queues[execution_id]

    try:
        # Send initial connection event
        yield f"data: {json.dumps({'event': 'connected', 'execution_id': str(execution_id)})}\n\n"

        # Stream events from queue
        while True:
            try:
                # Wait for event with timeout
                event_data = await asyncio.wait_for(queue.get(), timeout=30.0)

                # Format as SSE event
                event_type = event_data.get("event_type", "progress")
                event_json = json.dumps(event_data)

                yield f"event: {event_type}\ndata: {event_json}\n\n"

                # Check if workflow is complete
                if event_type in ("workflow_completed", "workflow_failed", "workflow_error"):
                    # Send final event and close stream
                    yield f"data: {json.dumps({'event': 'stream_end'})}\n\n"
                    break

            except asyncio.TimeoutError:
                # Send keepalive ping
                yield f": keepalive\n\n"

    except asyncio.CancelledError:
        # Client disconnected
        pass
    finally:
        # Cleanup
        if execution_id in progress_queues:
            del progress_queues[execution_id]


@router.get("/executions/{execution_id}/progress")
async def stream_execution_progress(
    execution_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Stream real-time progress updates for a workflow execution via SSE.

    Returns a Server-Sent Events stream with the following event types:
    - workflow_started: Execution began
    - node_started: Node execution started
    - node_completed: Node execution completed
    - node_failed: Node execution failed
    - node_retry: Node is being retried
    - workflow_completed: Workflow finished successfully
    - workflow_failed: Workflow failed
    - workflow_error: Unexpected error occurred
    - workflow_blocked: Workflow is blocked (e.g., waiting for input)

    Example usage (JavaScript):
    ```javascript
    const eventSource = new EventSource(`/api/v1/workflows/sse/executions/${executionId}/progress`);

    eventSource.addEventListener('node_started', (event) => {
      const data = JSON.parse(event.data);
      console.log('Node started:', data.node_name);
    });

    eventSource.addEventListener('workflow_completed', (event) => {
      console.log('Workflow completed!');
      eventSource.close();
    });
    ```
    """
    # Verify execution exists and user has access
    service = WorkflowService(db)
    execution = await service.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Return SSE stream
    return StreamingResponse(
        event_stream_generator(execution_id, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/workflows/{workflow_id}/live")
async def stream_workflow_live_updates(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Stream live updates for the most recent execution of a workflow.

    This is a convenience endpoint that automatically connects to the
    latest execution's progress stream.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow_with_details(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get most recent execution
    if not workflow.executions:
        raise HTTPException(status_code=404, detail="No executions found for this workflow")

    latest_execution = workflow.executions[0]  # Already ordered by created_at desc

    # Stream progress for latest execution
    return StreamingResponse(
        event_stream_generator(latest_execution.id, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
