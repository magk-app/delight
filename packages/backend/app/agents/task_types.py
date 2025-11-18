"""
Task type definitions for multi-step prompting orchestration.

This module defines the core data structures for representing tasks, workflows,
and execution state in the multi-step prompting system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Type of task execution strategy."""

    SEQUENTIAL = "sequential"  # Tasks must run one after another
    PARALLEL = "parallel"  # Tasks can run simultaneously
    HYBRID = "hybrid"  # Mix of sequential and parallel execution


class TaskStatus(str, Enum):
    """Current status of a task."""

    PENDING = "pending"  # Not yet started
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"  # Execution failed
    CANCELLED = "cancelled"  # Manually cancelled


class TaskPriority(int, Enum):
    """Priority levels for task execution."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class Task(BaseModel):
    """
    Represents a single unit of work in a multi-step workflow.

    A task encapsulates a prompt or action that needs to be executed,
    along with its metadata, dependencies, and execution results.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Human-readable task name")
    description: Optional[str] = Field(None, description="Detailed task description")
    prompt: str = Field(..., description="The prompt or action to execute")
    task_type: TaskType = Field(
        default=TaskType.SEQUENTIAL, description="Execution strategy for this task"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="Task execution priority"
    )

    # Dependencies and relationships
    depends_on: List[UUID] = Field(
        default_factory=list, description="Task IDs that must complete before this task"
    )
    parent_id: Optional[UUID] = Field(None, description="Parent task ID for nested workflows")

    # Execution context
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Input context for task execution"
    )
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error: Optional[str] = Field(None, description="Error message if task failed")

    # Timing information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts on failure")
    retry_count: int = Field(default=0, description="Current retry attempt number")

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional task metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}

    def can_execute(self, completed_tasks: Set[UUID]) -> bool:
        """
        Check if task can be executed based on its dependencies.

        Args:
            completed_tasks: Set of task IDs that have completed

        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        return all(dep_id in completed_tasks for dep_id in self.depends_on)

    def mark_running(self) -> None:
        """Mark task as running and record start time."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def mark_completed(self, result: Dict[str, Any]) -> None:
        """
        Mark task as completed with result.

        Args:
            result: Task execution result
        """
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """
        Mark task as failed with error message.

        Args:
            error: Error message
        """
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()

    def should_retry(self) -> bool:
        """
        Check if task should be retried after failure.

        Returns:
            True if retry is possible, False otherwise
        """
        return self.status == TaskStatus.FAILED and self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment retry counter and reset status to pending."""
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.error = None


class WorkflowConfig(BaseModel):
    """
    Configuration for workflow execution.

    Controls parallelization (breadth) and iteration depth.
    """

    breadth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of parallel tasks to execute simultaneously",
    )
    depth: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of sequential iteration cycles",
    )
    timeout_seconds: int = Field(
        default=300, ge=1, description="Maximum execution time per task in seconds"
    )
    enable_retry: bool = Field(default=True, description="Enable automatic retry on failure")
    collect_intermediate: bool = Field(
        default=True, description="Collect intermediate results from all tasks"
    )


class Workflow(BaseModel):
    """
    Represents a complete multi-step workflow.

    A workflow is a directed acyclic graph (DAG) of tasks with dependencies.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    tasks: List[Task] = Field(default_factory=list, description="All tasks in the workflow")
    config: WorkflowConfig = Field(
        default_factory=WorkflowConfig, description="Workflow execution configuration"
    )

    # Execution state
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Overall workflow status")
    current_depth: int = Field(default=0, description="Current iteration depth")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results aggregation
    results: Dict[str, Any] = Field(
        default_factory=dict, description="Aggregated workflow results"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Workflow metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}

    def add_task(self, task: Task) -> None:
        """
        Add a task to the workflow.

        Args:
            task: Task to add
        """
        self.tasks.append(task)

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """
        Get all tasks that are ready to execute.

        A task is ready if:
        1. Status is PENDING
        2. All dependencies are completed

        Returns:
            List of ready tasks sorted by priority
        """
        completed_task_ids = {
            task.id for task in self.tasks if task.status == TaskStatus.COMPLETED
        }

        ready_tasks = [
            task
            for task in self.tasks
            if task.status == TaskStatus.PENDING and task.can_execute(completed_task_ids)
        ]

        # Sort by priority (highest first)
        return sorted(ready_tasks, key=lambda t: t.priority.value, reverse=True)

    def get_failed_tasks(self) -> List[Task]:
        """
        Get all failed tasks that should be retried.

        Returns:
            List of tasks eligible for retry
        """
        return [task for task in self.tasks if task.should_retry()]

    def is_complete(self) -> bool:
        """
        Check if workflow is complete.

        A workflow is complete if all tasks are either completed or failed
        (and not eligible for retry).

        Returns:
            True if workflow is complete, False otherwise
        """
        for task in self.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                return False
            if task.should_retry():
                return False
        return True

    def has_failures(self) -> bool:
        """
        Check if workflow has any failed tasks.

        Returns:
            True if any tasks failed, False otherwise
        """
        return any(task.status == TaskStatus.FAILED for task in self.tasks)

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of workflow execution.

        Returns:
            Dictionary with execution statistics
        """
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)

        return {
            "workflow_id": str(self.id),
            "name": self.name,
            "status": self.status.value,
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "current_depth": self.current_depth,
            "max_depth": self.config.depth,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
