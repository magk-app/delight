"""
Pydantic schemas for workflow API requests and responses.

These schemas define the API contract for creating and managing
multi-step prompting workflows.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.agents.task_types import TaskType, TaskStatus, TaskPriority


class TaskCreateRequest(BaseModel):
    """Request schema for creating a new task."""

    name: str = Field(..., description="Task name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Task description", max_length=1000)
    prompt: str = Field(..., description="The prompt to execute", min_length=1)
    task_type: TaskType = Field(default=TaskType.SEQUENTIAL, description="Execution type")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    depends_on: List[str] = Field(
        default_factory=list, description="Names of tasks this task depends on"
    )
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskResponse(BaseModel):
    """Response schema for task information."""

    id: UUID
    name: str
    description: Optional[str]
    prompt: str
    task_type: TaskType
    status: TaskStatus
    priority: TaskPriority
    depends_on: List[UUID]
    context: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int
    max_retries: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class WorkflowConfigRequest(BaseModel):
    """Request schema for workflow configuration."""

    breadth: int = Field(
        default=3, ge=1, le=10, description="Maximum parallel tasks to execute simultaneously"
    )
    depth: int = Field(
        default=5, ge=1, le=20, description="Maximum sequential iteration cycles"
    )
    timeout_seconds: int = Field(
        default=300, ge=1, le=3600, description="Maximum execution time per task"
    )
    enable_retry: bool = Field(default=True, description="Enable automatic retry on failure")
    collect_intermediate: bool = Field(
        default=True, description="Collect intermediate results from all tasks"
    )


class WorkflowCreateRequest(BaseModel):
    """Request schema for creating a new workflow."""

    name: str = Field(..., description="Workflow name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Workflow description", max_length=1000)
    tasks: List[TaskCreateRequest] = Field(..., description="Tasks in the workflow", min_items=1)
    config: Optional[WorkflowConfigRequest] = Field(
        None, description="Workflow execution configuration"
    )


class WorkflowExecuteSummary(BaseModel):
    """Execution summary for a workflow."""

    workflow_id: UUID
    name: str
    status: TaskStatus
    total_tasks: int
    completed: int
    failed: int
    running: int
    pending: int
    current_depth: int
    max_depth: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class WorkflowResponse(BaseModel):
    """Response schema for workflow information."""

    id: UUID
    name: str
    description: Optional[str]
    status: TaskStatus
    tasks: List[TaskResponse]
    config: WorkflowConfigRequest
    current_depth: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: Dict[str, Any]
    execution_summary: Optional[WorkflowExecuteSummary]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class PlanExecuteRequest(BaseModel):
    """Request schema for plan-execute-reflect workflow."""

    objective: str = Field(..., description="The goal to achieve", min_length=1)
    context: Optional[Dict[str, Any]] = Field(
        None, description="Optional context for planning"
    )
    config: Optional[WorkflowConfigRequest] = Field(
        None, description="Workflow configuration"
    )


class WorkflowStatusResponse(BaseModel):
    """Response schema for workflow status check."""

    workflow_id: UUID
    status: TaskStatus
    progress: float = Field(..., ge=0.0, le=1.0, description="Completion percentage")
    tasks_completed: int
    tasks_total: int
    current_depth: int
    max_depth: int
    elapsed_seconds: Optional[float]


class TaskResultResponse(BaseModel):
    """Response schema for individual task result."""

    task_id: UUID
    task_name: str
    status: TaskStatus
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    duration_seconds: Optional[float]
