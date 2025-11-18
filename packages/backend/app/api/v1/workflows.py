"""
Workflow API endpoints for multi-step prompting orchestration.

Provides REST API for creating, executing, and managing workflows.
"""

from typing import Dict, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from app.schemas.workflow import (
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    TaskResponse,
    PlanExecuteRequest,
    WorkflowConfigRequest,
)
from app.agents.task_types import (
    Task,
    TaskType,
    TaskStatus,
    Workflow,
    WorkflowConfig,
    TaskPriority,
)
from app.agents.orchestrator import WorkflowOrchestrator, WorkflowBuilder


router = APIRouter(prefix="/workflows", tags=["Workflows"])


# In-memory workflow storage (replace with database in production)
_workflows: Dict[UUID, Workflow] = {}
_orchestrators: Dict[UUID, WorkflowOrchestrator] = {}


def _convert_task_to_response(task: Task) -> TaskResponse:
    """Convert Task model to API response."""
    return TaskResponse(
        id=task.id,
        name=task.name,
        description=task.description,
        prompt=task.prompt,
        task_type=task.task_type,
        status=task.status,
        priority=task.priority,
        depends_on=task.depends_on,
        context=task.context,
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
    )


def _convert_workflow_to_response(workflow: Workflow) -> WorkflowResponse:
    """Convert Workflow model to API response."""
    execution_summary = None
    if workflow.status != TaskStatus.PENDING:
        summary_dict = workflow.get_execution_summary()
        execution_summary = {
            "workflow_id": workflow.id,
            "name": summary_dict["name"],
            "status": workflow.status,
            "total_tasks": summary_dict["total_tasks"],
            "completed": summary_dict["completed"],
            "failed": summary_dict["failed"],
            "running": summary_dict["running"],
            "pending": summary_dict["pending"],
            "current_depth": summary_dict["current_depth"],
            "max_depth": summary_dict["max_depth"],
            "created_at": workflow.created_at,
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at,
        }

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        tasks=[_convert_task_to_response(task) for task in workflow.tasks],
        config=WorkflowConfigRequest(
            breadth=workflow.config.breadth,
            depth=workflow.config.depth,
            timeout_seconds=workflow.config.timeout_seconds,
            enable_retry=workflow.config.enable_retry,
            collect_intermediate=workflow.config.collect_intermediate,
        ),
        current_depth=workflow.current_depth,
        created_at=workflow.created_at,
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        results=workflow.results,
        execution_summary=execution_summary,
    )


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(request: WorkflowCreateRequest) -> WorkflowResponse:
    """
    Create a new multi-step workflow.

    This endpoint creates a workflow with the specified tasks and configuration.
    The workflow is not executed immediately - use the execute endpoint.

    Args:
        request: Workflow creation request

    Returns:
        Created workflow with assigned IDs
    """
    # Create workflow config
    config = WorkflowConfig()
    if request.config:
        config.breadth = request.config.breadth
        config.depth = request.config.depth
        config.timeout_seconds = request.config.timeout_seconds
        config.enable_retry = request.config.enable_retry
        config.collect_intermediate = request.config.collect_intermediate

    # Create workflow
    workflow = Workflow(
        name=request.name, description=request.description, config=config
    )

    # Build task name to ID mapping for dependencies
    task_name_to_id: Dict[str, UUID] = {}

    # Create tasks
    for task_req in request.tasks:
        task = Task(
            name=task_req.name,
            description=task_req.description,
            prompt=task_req.prompt,
            task_type=task_req.task_type,
            priority=task_req.priority,
            context=task_req.context,
            max_retries=task_req.max_retries,
            metadata=task_req.metadata,
        )
        workflow.add_task(task)
        task_name_to_id[task.name] = task.id

    # Resolve dependencies by name
    for task, task_req in zip(workflow.tasks, request.tasks):
        for dep_name in task_req.depends_on:
            if dep_name in task_name_to_id:
                task.depends_on.append(task_name_to_id[dep_name])
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Dependency '{dep_name}' not found for task '{task.name}'",
                )

    # Store workflow
    _workflows[workflow.id] = workflow

    return _convert_workflow_to_response(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID) -> WorkflowResponse:
    """
    Get workflow by ID.

    Args:
        workflow_id: Workflow UUID

    Returns:
        Workflow details

    Raises:
        HTTPException: If workflow not found
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]
    return _convert_workflow_to_response(workflow)


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    status: TaskStatus | None = None, limit: int = 100, offset: int = 0
) -> List[WorkflowResponse]:
    """
    List all workflows with optional filtering.

    Args:
        status: Filter by workflow status
        limit: Maximum number of workflows to return
        offset: Number of workflows to skip

    Returns:
        List of workflows
    """
    workflows = list(_workflows.values())

    # Filter by status if specified
    if status:
        workflows = [w for w in workflows if w.status == status]

    # Apply pagination
    workflows = workflows[offset : offset + limit]

    return [_convert_workflow_to_response(w) for w in workflows]


@router.post("/{workflow_id}/execute", response_model=WorkflowResponse)
async def execute_workflow(
    workflow_id: UUID, background_tasks: BackgroundTasks
) -> WorkflowResponse:
    """
    Execute a workflow.

    This endpoint starts workflow execution. For long-running workflows,
    execution happens in the background. Use the status endpoint to check progress.

    Args:
        workflow_id: Workflow UUID
        background_tasks: FastAPI background tasks

    Returns:
        Updated workflow (may still be running)

    Raises:
        HTTPException: If workflow not found or already running
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]

    if workflow.status == TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Workflow is already running")

    if workflow.status == TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Workflow has already completed")

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(config=workflow.config)
    _orchestrators[workflow_id] = orchestrator

    # Execute workflow in background
    async def run_workflow():
        try:
            await orchestrator.execute_workflow(workflow)
        except Exception as e:
            workflow.status = TaskStatus.FAILED
            workflow.results["error"] = str(e)

    background_tasks.add_task(run_workflow)

    # Return immediately with running status
    workflow.status = TaskStatus.RUNNING
    return _convert_workflow_to_response(workflow)


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: UUID) -> WorkflowStatusResponse:
    """
    Get workflow execution status.

    Args:
        workflow_id: Workflow UUID

    Returns:
        Workflow status summary

    Raises:
        HTTPException: If workflow not found
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]

    # Calculate progress
    total_tasks = len(workflow.tasks)
    completed_tasks = sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED)
    progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0

    # Calculate elapsed time
    elapsed_seconds = None
    if workflow.started_at:
        end_time = workflow.completed_at or datetime.utcnow()
        elapsed_seconds = (end_time - workflow.started_at).total_seconds()

    return WorkflowStatusResponse(
        workflow_id=workflow.id,
        status=workflow.status,
        progress=progress,
        tasks_completed=completed_tasks,
        tasks_total=total_tasks,
        current_depth=workflow.current_depth,
        max_depth=workflow.config.depth,
        elapsed_seconds=elapsed_seconds,
    )


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: UUID) -> Dict[str, str]:
    """
    Cancel a running workflow.

    Args:
        workflow_id: Workflow UUID

    Returns:
        Success message

    Raises:
        HTTPException: If workflow not found or not running
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]

    if workflow.status != TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Workflow is not running")

    # Cancel all pending and running tasks
    for task in workflow.tasks:
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED

    workflow.status = TaskStatus.CANCELLED
    workflow.completed_at = datetime.utcnow()

    return {"message": "Workflow cancelled successfully"}


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: UUID) -> Dict[str, str]:
    """
    Delete a workflow.

    Args:
        workflow_id: Workflow UUID

    Returns:
        Success message

    Raises:
        HTTPException: If workflow not found or still running
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = _workflows[workflow_id]

    if workflow.status == TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Cannot delete running workflow")

    # Remove workflow and orchestrator
    del _workflows[workflow_id]
    if workflow_id in _orchestrators:
        del _orchestrators[workflow_id]

    return {"message": "Workflow deleted successfully"}


@router.post("/plan-execute", response_model=WorkflowResponse, status_code=201)
async def create_plan_execute_workflow(
    request: PlanExecuteRequest, background_tasks: BackgroundTasks
) -> WorkflowResponse:
    """
    Create and execute a Plan-Execute-Reflect workflow.

    This is a high-level endpoint that automatically creates a workflow with:
    1. Planning phase (sequential)
    2. Execution phase (parallel sub-tasks)
    3. Reflection phase (sequential consolidation)

    Args:
        request: Plan-execute request
        background_tasks: FastAPI background tasks

    Returns:
        Created and executing workflow
    """
    # Create workflow config
    config = WorkflowConfig()
    if request.config:
        config.breadth = request.config.breadth
        config.depth = request.config.depth
        config.timeout_seconds = request.config.timeout_seconds
        config.enable_retry = request.config.enable_retry
        config.collect_intermediate = request.config.collect_intermediate

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(config=config)

    # Execute plan-execute workflow in background
    workflow = None

    async def run_plan_execute():
        nonlocal workflow
        workflow = await orchestrator.execute_plan_and_execute_workflow(
            objective=request.objective, context=request.context
        )
        _workflows[workflow.id] = workflow

    background_tasks.add_task(run_plan_execute)

    # Create placeholder workflow for immediate response
    workflow = Workflow(
        name=f"Plan-Execute: {request.objective[:50]}",
        description="Automated plan-execute-reflect workflow",
        config=config,
    )
    workflow.status = TaskStatus.RUNNING
    workflow.started_at = datetime.utcnow()

    _workflows[workflow.id] = workflow
    _orchestrators[workflow.id] = orchestrator

    return _convert_workflow_to_response(workflow)


@router.post("/builder/example", response_model=WorkflowResponse, status_code=201)
async def create_example_workflow() -> WorkflowResponse:
    """
    Create an example workflow using the builder pattern.

    This demonstrates how to use the WorkflowBuilder to create
    complex workflows programmatically.

    Returns:
        Created example workflow
    """
    # Use builder to create workflow
    workflow = (
        WorkflowBuilder(name="Example Multi-Step Research Workflow")
        .with_config(breadth=3, depth=5, timeout_seconds=300)
        .add_task(
            name="initial_research",
            prompt="Gather initial research on the topic",
            task_type=TaskType.SEQUENTIAL,
        )
        .add_parallel_tasks(
            task_specs=[
                {
                    "name": "research_economy",
                    "prompt": "Research economic aspects",
                    "context": {"topic": "economy"},
                },
                {
                    "name": "research_health",
                    "prompt": "Research health aspects",
                    "context": {"topic": "health"},
                },
                {
                    "name": "research_education",
                    "prompt": "Research education aspects",
                    "context": {"topic": "education"},
                },
            ],
            depends_on=["initial_research"],
        )
        .add_task(
            name="synthesize",
            prompt="Synthesize all research findings",
            task_type=TaskType.SEQUENTIAL,
            depends_on=["research_economy", "research_health", "research_education"],
        )
        .build()
    )

    # Store workflow
    _workflows[workflow.id] = workflow

    return _convert_workflow_to_response(workflow)
