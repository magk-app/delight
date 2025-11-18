"""
Pydantic schemas for workflow-related API requests/responses.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import (
    EdgeType,
    ExecutionStatus,
    NodeStatus,
    NodeType,
    WorkflowStatus,
)


# ============================================================================
# Node Schemas
# ============================================================================


class NodePositionSchema(BaseModel):
    """Position of node in UI visualization."""

    x: float
    y: float


class WorkflowNodeBase(BaseModel):
    """Base schema for workflow nodes."""

    name: str = Field(..., max_length=255, description="Node name")
    description: str | None = Field(None, description="Detailed node description")
    node_type: NodeType = Field(default=NodeType.TASK, description="Type of node")
    tool_name: str | None = Field(None, max_length=100, description="Tool/function to execute")
    input_schema: dict[str, Any] | None = Field(None, description="Expected input parameters")
    can_run_parallel: bool = Field(default=False, description="Can run in parallel")
    position: NodePositionSchema | None = Field(None, description="UI position")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")


class WorkflowNodeCreate(WorkflowNodeBase):
    """Schema for creating a workflow node."""

    pass


class WorkflowNodeUpdate(BaseModel):
    """Schema for updating a workflow node."""

    name: str | None = Field(None, max_length=255)
    description: str | None = None
    node_type: NodeType | None = None
    tool_name: str | None = None
    input_schema: dict[str, Any] | None = None
    can_run_parallel: bool | None = None
    position: NodePositionSchema | None = None
    max_retries: int | None = Field(None, ge=0, le=10)
    status: NodeStatus | None = None


class WorkflowNodeResponse(WorkflowNodeBase):
    """Schema for workflow node responses."""

    id: UUID
    workflow_id: UUID
    status: NodeStatus
    output_data: dict[str, Any] | None
    retry_count: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


# ============================================================================
# Edge Schemas
# ============================================================================


class WorkflowEdgeBase(BaseModel):
    """Base schema for workflow edges."""

    source_node_id: UUID = Field(..., description="Starting node")
    target_node_id: UUID = Field(..., description="Destination node")
    edge_type: EdgeType = Field(default=EdgeType.SEQUENTIAL, description="Type of connection")
    condition: dict[str, Any] | None = Field(None, description="Conditional logic")


class WorkflowEdgeCreate(WorkflowEdgeBase):
    """Schema for creating a workflow edge."""

    pass


class WorkflowEdgeResponse(WorkflowEdgeBase):
    """Schema for workflow edge responses."""

    id: UUID
    workflow_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Workflow Schemas
# ============================================================================


class WorkflowBase(BaseModel):
    """Base schema for workflows."""

    name: str = Field(..., max_length=255, description="Workflow name")
    description: str | None = Field(None, description="Detailed workflow description")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow."""

    llm_generated: bool = Field(default=False, description="LLM-generated workflow")
    nodes: list[WorkflowNodeCreate] = Field(default_factory=list, description="Initial nodes")
    edges: list[WorkflowEdgeCreate] = Field(default_factory=list, description="Initial edges")


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""

    name: str | None = Field(None, max_length=255)
    description: str | None = None
    status: WorkflowStatus | None = None
    metadata: dict[str, Any] | None = None


class WorkflowResponse(WorkflowBase):
    """Schema for workflow responses."""

    id: UUID
    user_id: UUID
    status: WorkflowStatus
    llm_generated: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class WorkflowDetailResponse(WorkflowResponse):
    """Detailed workflow response with nodes and edges."""

    nodes: list[WorkflowNodeResponse]
    edges: list[WorkflowEdgeResponse]


# ============================================================================
# Execution Schemas
# ============================================================================


class WorkflowExecutionBase(BaseModel):
    """Base schema for workflow executions."""

    execution_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Shared data between nodes",
    )


class WorkflowExecutionCreate(WorkflowExecutionBase):
    """Schema for starting a workflow execution."""

    pass


class WorkflowExecutionResponse(WorkflowExecutionBase):
    """Schema for workflow execution responses."""

    id: UUID
    workflow_id: UUID
    status: ExecutionStatus
    current_node_id: UUID | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class WorkflowExecutionDetailResponse(WorkflowExecutionResponse):
    """Detailed execution response with workflow details."""

    workflow: WorkflowDetailResponse


# ============================================================================
# LLM Plan Generation Schemas
# ============================================================================


class WorkflowPlanRequest(BaseModel):
    """Request schema for LLM-generated workflow plan."""

    user_query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's task or query to plan",
    )
    context: dict[str, Any] | None = Field(
        None,
        description="Additional context for planning",
    )
    auto_approve: bool = Field(
        default=False,
        description="Automatically approve and start execution",
    )


class WorkflowPlanResponse(BaseModel):
    """Response schema for LLM-generated workflow plan."""

    workflow: WorkflowDetailResponse
    plan_summary: str = Field(..., description="Human-readable plan summary")
    estimated_duration: str | None = Field(None, description="Estimated completion time")
    requires_approval: bool = Field(default=True, description="Needs user approval")


# ============================================================================
# Progress Update Schemas (for SSE)
# ============================================================================


class NodeProgressUpdate(BaseModel):
    """Real-time node progress update."""

    execution_id: UUID
    workflow_id: UUID
    node_id: UUID
    node_name: str
    node_status: NodeStatus
    progress_message: str
    timestamp: datetime


class WorkflowProgressUpdate(BaseModel):
    """Real-time workflow progress update."""

    execution_id: UUID
    workflow_id: UUID
    workflow_status: ExecutionStatus
    completed_nodes: int
    total_nodes: int
    progress_percentage: float
    current_milestone: str | None
    timestamp: datetime


# ============================================================================
# List/Filter Schemas
# ============================================================================


class WorkflowListResponse(BaseModel):
    """Paginated list of workflows."""

    workflows: list[WorkflowResponse]
    total: int
    page: int
    page_size: int


class WorkflowExecutionListResponse(BaseModel):
    """Paginated list of workflow executions."""

    executions: list[WorkflowExecutionResponse]
    total: int
    page: int
    page_size: int
