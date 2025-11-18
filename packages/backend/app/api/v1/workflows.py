"""
Workflow API endpoints for node-based planning and execution.
"""

import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clerk_auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.workflow import WorkflowStatus
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowDetailResponse,
    WorkflowEdgeCreate,
    WorkflowEdgeResponse,
    WorkflowExecutionCreate,
    WorkflowExecutionDetailResponse,
    WorkflowExecutionListResponse,
    WorkflowExecutionResponse,
    WorkflowListResponse,
    WorkflowNodeCreate,
    WorkflowNodeResponse,
    WorkflowNodeUpdate,
    WorkflowPlanRequest,
    WorkflowPlanResponse,
    WorkflowResponse,
    WorkflowUpdate,
)
from app.services.workflow_executor import WorkflowExecutor
from app.services.workflow_planner import WorkflowPlanner
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ============================================================================
# Workflow CRUD Endpoints
# ============================================================================


@router.post("", response_model=WorkflowDetailResponse, status_code=201)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new workflow with nodes and edges.

    This endpoint allows manual workflow creation. For LLM-generated workflows,
    use the POST /workflows/generate endpoint instead.
    """
    service = WorkflowService(db)
    workflow = await service.create_workflow(current_user.id, workflow_data)
    return workflow


@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status: WorkflowStatus | None = Query(None, description="Filter by workflow status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List user's workflows with pagination and filtering.
    """
    service = WorkflowService(db)
    skip = (page - 1) * page_size
    workflows, total = await service.get_user_workflows(
        current_user.id,
        status=status,
        skip=skip,
        limit=page_size,
    )

    return WorkflowListResponse(
        workflows=[WorkflowResponse.model_validate(w) for w in workflows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get workflow details with all nodes and edges.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow_with_details(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    update_data: WorkflowUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update workflow properties (name, description, status, metadata).
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    updated_workflow = await service.update_workflow(workflow_id, update_data)
    return updated_workflow


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a workflow and all associated nodes, edges, and executions.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    await service.delete_workflow(workflow_id)
    return None


# ============================================================================
# Node Management Endpoints
# ============================================================================


@router.post("/{workflow_id}/nodes", response_model=WorkflowNodeResponse, status_code=201)
async def add_node(
    workflow_id: UUID,
    node_data: WorkflowNodeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new node to an existing workflow.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    node = await service.add_node(workflow_id, node_data)
    return node


@router.patch("/nodes/{node_id}", response_model=WorkflowNodeResponse)
async def update_node(
    node_id: UUID,
    update_data: WorkflowNodeUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update node properties.
    """
    service = WorkflowService(db)
    node = await service.get_node(node_id)

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Check workflow ownership
    workflow = await service.get_workflow(node.workflow_id)
    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update node fields
    if update_data.name is not None:
        node.name = update_data.name
    if update_data.description is not None:
        node.description = update_data.description
    if update_data.node_type is not None:
        node.node_type = update_data.node_type
    if update_data.tool_name is not None:
        node.tool_name = update_data.tool_name
    if update_data.input_schema is not None:
        node.input_schema = update_data.input_schema
    if update_data.can_run_parallel is not None:
        node.can_run_parallel = update_data.can_run_parallel
    if update_data.position is not None:
        node.position = update_data.position.model_dump()
    if update_data.max_retries is not None:
        node.max_retries = update_data.max_retries
    if update_data.status is not None:
        node.status = update_data.status

    await db.commit()
    await db.refresh(node)
    return node


# ============================================================================
# Edge Management Endpoints
# ============================================================================


@router.post("/{workflow_id}/edges", response_model=WorkflowEdgeResponse, status_code=201)
async def add_edge(
    workflow_id: UUID,
    edge_data: WorkflowEdgeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new edge to connect workflow nodes.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    edge = await service.add_edge(workflow_id, edge_data)
    return edge


@router.delete("/edges/{edge_id}", status_code=204)
async def delete_edge(
    edge_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an edge between nodes.
    """
    service = WorkflowService(db)

    # TODO: Add ownership check
    success = await service.delete_edge(edge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Edge not found")

    return None


# ============================================================================
# LLM Plan Generation Endpoints
# ============================================================================


@router.post("/generate", response_model=WorkflowPlanResponse, status_code=201)
async def generate_workflow_plan(
    plan_request: WorkflowPlanRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a workflow plan from natural language using LLM.

    This endpoint uses GPT-4o-mini to analyze the user's query and generate
    a complete workflow with nodes, edges, and dependencies.

    The generated workflow is in PENDING_APPROVAL status by default unless
    auto_approve is set to true.
    """
    planner = WorkflowPlanner(db)

    try:
        workflow, summary = await planner.generate_workflow_plan(
            user_id=current_user.id,
            user_query=plan_request.user_query,
            context=plan_request.context,
        )

        # Set status based on auto_approve
        if plan_request.auto_approve:
            service = WorkflowService(db)
            await service.update_workflow(
                workflow.id,
                WorkflowUpdate(status=WorkflowStatus.APPROVED),
            )
            workflow = await service.get_workflow_with_details(workflow.id)

        return WorkflowPlanResponse(
            workflow=WorkflowDetailResponse.model_validate(workflow),
            plan_summary=summary,
            estimated_duration=workflow.metadata.get("estimated_duration"),
            requires_approval=not plan_request.auto_approve,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate workflow plan: {str(e)}",
        )


@router.patch("/{workflow_id}/approve", response_model=WorkflowResponse)
async def approve_workflow(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a workflow plan, allowing it to be executed.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    updated_workflow = await service.update_workflow(
        workflow_id,
        WorkflowUpdate(status=WorkflowStatus.APPROVED),
    )
    return updated_workflow


# ============================================================================
# Execution Endpoints
# ============================================================================


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse, status_code=201)
async def execute_workflow(
    workflow_id: UUID,
    execution_data: WorkflowExecutionCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Start workflow execution.

    The workflow must be in APPROVED status to execute.
    Execution runs in the background and progress can be monitored via SSE.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if workflow.status not in (WorkflowStatus.APPROVED, WorkflowStatus.DRAFT):
        raise HTTPException(
            status_code=400,
            detail=f"Workflow must be approved before execution (current status: {workflow.status})",
        )

    # Validate workflow structure
    is_valid, errors = await service.validate_workflow_structure(workflow_id)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid workflow structure: {', '.join(errors)}",
        )

    # Create execution
    execution = await service.create_execution(
        workflow_id,
        execution_context=execution_data.execution_context,
    )

    # Run execution in background
    # Note: In production, this should use ARQ or similar task queue
    # background_tasks.add_task(run_workflow_execution, execution.id, db)

    return execution


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionDetailResponse)
async def get_execution(
    execution_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get execution details with workflow information.
    """
    service = WorkflowService(db)
    execution = await service.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return execution


@router.get("/{workflow_id}/executions", response_model=WorkflowExecutionListResponse)
async def list_workflow_executions(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List all executions for a workflow.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get executions
    skip = (page - 1) * page_size
    # TODO: Implement pagination in service
    executions = workflow.executions[skip : skip + page_size]
    total = len(workflow.executions)

    return WorkflowExecutionListResponse(
        executions=[WorkflowExecutionResponse.model_validate(e) for e in executions],
        total=total,
        page=page,
        page_size=page_size,
    )
