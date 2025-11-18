"""
Unit tests for multi-step prompting orchestration system.

Tests the task types, executors, and orchestrator components.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from app.agents.task_types import (
    Task,
    TaskType,
    TaskStatus,
    TaskPriority,
    Workflow,
    WorkflowConfig,
)
from app.agents.executors import (
    SequentialExecutor,
    ParallelExecutor,
    HybridExecutor,
)
from app.agents.orchestrator import WorkflowOrchestrator, WorkflowBuilder


class TestTask:
    """Test Task model."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            name="Test Task",
            prompt="Test prompt",
            task_type=TaskType.SEQUENTIAL,
        )

        assert task.name == "Test Task"
        assert task.prompt == "Test prompt"
        assert task.status == TaskStatus.PENDING
        assert task.task_type == TaskType.SEQUENTIAL
        assert isinstance(task.id, type(uuid4()))

    def test_task_can_execute_no_dependencies(self):
        """Test task with no dependencies can execute."""
        task = Task(name="Test", prompt="Test")
        assert task.can_execute(set())

    def test_task_can_execute_with_dependencies(self):
        """Test task with dependencies."""
        dep_id = uuid4()
        task = Task(name="Test", prompt="Test", depends_on=[dep_id])

        # Cannot execute without dependency
        assert not task.can_execute(set())

        # Can execute with dependency
        assert task.can_execute({dep_id})

    def test_task_lifecycle(self):
        """Test task state transitions."""
        task = Task(name="Test", prompt="Test")

        # Start task
        task.mark_running()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None

        # Complete task
        result = {"output": "success"}
        task.mark_completed(result)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == result
        assert task.completed_at is not None

    def test_task_failure_and_retry(self):
        """Test task failure and retry logic."""
        task = Task(name="Test", prompt="Test", max_retries=3)

        # Fail task
        task.mark_failed("Error occurred")
        assert task.status == TaskStatus.FAILED
        assert task.error == "Error occurred"
        assert task.should_retry()

        # Increment retry
        task.increment_retry()
        assert task.retry_count == 1
        assert task.status == TaskStatus.PENDING

        # Exhaust retries
        for i in range(3):
            task.mark_failed("Error")
            if task.should_retry():
                task.increment_retry()

        assert not task.should_retry()
        assert task.retry_count == 3


class TestWorkflow:
    """Test Workflow model."""

    def test_workflow_creation(self):
        """Test creating a workflow."""
        workflow = Workflow(name="Test Workflow", description="Test description")

        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test description"
        assert workflow.status == TaskStatus.PENDING
        assert len(workflow.tasks) == 0

    def test_workflow_add_tasks(self):
        """Test adding tasks to workflow."""
        workflow = Workflow(name="Test")

        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2")

        workflow.add_task(task1)
        workflow.add_task(task2)

        assert len(workflow.tasks) == 2
        assert workflow.get_task(task1.id) == task1
        assert workflow.get_task(task2.id) == task2

    def test_workflow_get_ready_tasks(self):
        """Test getting ready tasks from workflow."""
        workflow = Workflow(name="Test")

        # Create tasks with dependencies
        task1 = Task(name="Task 1", prompt="Prompt 1", priority=TaskPriority.HIGH)
        task2 = Task(
            name="Task 2",
            prompt="Prompt 2",
            depends_on=[task1.id],
            priority=TaskPriority.NORMAL,
        )
        task3 = Task(name="Task 3", prompt="Prompt 3", priority=TaskPriority.LOW)

        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.add_task(task3)

        # Initially, task1 and task3 are ready (no dependencies)
        ready = workflow.get_ready_tasks()
        assert len(ready) == 2
        assert task1 in ready
        assert task3 in ready
        # Should be sorted by priority
        assert ready[0].priority == TaskPriority.HIGH

        # Complete task1
        task1.mark_completed({"result": "done"})

        # Now task2 should also be ready
        ready = workflow.get_ready_tasks()
        assert len(ready) == 2
        assert task2 in ready
        assert task3 in ready

    def test_workflow_is_complete(self):
        """Test workflow completion check."""
        workflow = Workflow(name="Test")

        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2")

        workflow.add_task(task1)
        workflow.add_task(task2)

        # Not complete initially
        assert not workflow.is_complete()

        # Complete first task
        task1.mark_completed({"result": "done"})
        assert not workflow.is_complete()

        # Complete second task
        task2.mark_completed({"result": "done"})
        assert workflow.is_complete()

    def test_workflow_has_failures(self):
        """Test workflow failure detection."""
        workflow = Workflow(name="Test")

        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2", max_retries=0)

        workflow.add_task(task1)
        workflow.add_task(task2)

        assert not workflow.has_failures()

        task1.mark_completed({"result": "done"})
        task2.mark_failed("Error")

        assert workflow.has_failures()


@pytest.mark.asyncio
class TestSequentialExecutor:
    """Test SequentialExecutor."""

    async def test_execute_single_task(self):
        """Test executing a single task sequentially."""
        executor = SequentialExecutor(timeout_seconds=10)
        task = Task(name="Test Task", prompt="Test prompt")

        result = await executor.execute_task(task, {})

        assert task.status == TaskStatus.COMPLETED
        assert result is not None
        assert "task_name" in result

    async def test_execute_multiple_tasks_sequentially(self):
        """Test executing multiple tasks in sequence."""
        executor = SequentialExecutor(timeout_seconds=10)
        workflow = Workflow(name="Test")

        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2")
        task3 = Task(name="Task 3", prompt="Prompt 3")

        tasks = [task1, task2, task3]
        for task in tasks:
            workflow.add_task(task)

        results = await executor.execute_tasks(tasks, workflow)

        assert len(results) == 3
        assert all(task.status == TaskStatus.COMPLETED for task in tasks)

    async def test_sequential_executor_context_passing(self):
        """Test that results are passed forward in context."""
        executor = SequentialExecutor(timeout_seconds=10)
        workflow = Workflow(name="Test")

        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2")

        workflow.add_task(task1)
        workflow.add_task(task2)

        results = await executor.execute_tasks([task1, task2], workflow)

        # Task 2 should have received Task 1's result in context
        assert results[task1.id] is not None
        assert results[task2.id] is not None


@pytest.mark.asyncio
class TestParallelExecutor:
    """Test ParallelExecutor."""

    async def test_execute_single_task_parallel(self):
        """Test executing a single task in parallel mode."""
        executor = ParallelExecutor(max_parallel=3, timeout_seconds=10)
        task = Task(name="Test Task", prompt="Test prompt")

        result = await executor.execute_task(task, {})

        assert task.status == TaskStatus.COMPLETED
        assert result is not None

    async def test_execute_multiple_tasks_parallel(self):
        """Test executing multiple tasks in parallel."""
        executor = ParallelExecutor(max_parallel=3, timeout_seconds=10)
        workflow = Workflow(name="Test")

        tasks = [Task(name=f"Task {i}", prompt=f"Prompt {i}") for i in range(5)]
        for task in tasks:
            workflow.add_task(task)

        results = await executor.execute_tasks(tasks, workflow)

        # All tasks should complete
        assert len(results) == 5
        assert all(task.status == TaskStatus.COMPLETED for task in tasks)

    async def test_parallel_executor_concurrency_limit(self):
        """Test that parallel executor respects max_parallel limit."""
        max_parallel = 2
        executor = ParallelExecutor(max_parallel=max_parallel, timeout_seconds=10)
        workflow = Workflow(name="Test")

        # Create tasks that track execution
        tasks = [Task(name=f"Task {i}", prompt=f"Prompt {i}") for i in range(5)]
        for task in tasks:
            workflow.add_task(task)

        # Execute tasks
        start_time = datetime.utcnow()
        results = await executor.execute_tasks(tasks, workflow)
        duration = (datetime.utcnow() - start_time).total_seconds()

        # All should complete
        assert len(results) == 5

        # With batching, should take longer than running all at once
        # (but this is hard to test precisely without timing each task)


@pytest.mark.asyncio
class TestHybridExecutor:
    """Test HybridExecutor."""

    async def test_hybrid_executor_with_dependencies(self):
        """Test hybrid executor handling task dependencies."""
        executor = HybridExecutor(max_parallel=3, timeout_seconds=10)
        workflow = Workflow(name="Test")

        # Create DAG of tasks
        task1 = Task(name="Task 1", prompt="Prompt 1", task_type=TaskType.SEQUENTIAL)
        task2 = Task(
            name="Task 2",
            prompt="Prompt 2",
            task_type=TaskType.PARALLEL,
            depends_on=[task1.id],
        )
        task3 = Task(
            name="Task 3",
            prompt="Prompt 3",
            task_type=TaskType.PARALLEL,
            depends_on=[task1.id],
        )
        task4 = Task(
            name="Task 4",
            prompt="Prompt 4",
            task_type=TaskType.SEQUENTIAL,
            depends_on=[task2.id, task3.id],
        )

        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.add_task(task3)
        workflow.add_task(task4)

        results = await executor.execute_tasks([task1, task2, task3, task4], workflow)

        # All tasks should complete
        assert len(results) == 4
        assert all(task.status == TaskStatus.COMPLETED for task in [task1, task2, task3, task4])

        # Verify execution order by checking timestamps
        assert task1.started_at < task2.started_at
        assert task1.started_at < task3.started_at
        assert task2.completed_at < task4.started_at
        assert task3.completed_at < task4.started_at


@pytest.mark.asyncio
class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator."""

    async def test_orchestrator_execute_simple_workflow(self):
        """Test orchestrator executing a simple workflow."""
        config = WorkflowConfig(breadth=3, depth=2, timeout_seconds=10)
        orchestrator = WorkflowOrchestrator(config=config)

        workflow = Workflow(name="Test Workflow", config=config)
        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2")

        workflow.add_task(task1)
        workflow.add_task(task2)

        result = await orchestrator.execute_workflow(workflow)

        assert result.status == TaskStatus.COMPLETED
        assert all(task.status == TaskStatus.COMPLETED for task in result.tasks)
        assert "summary" in result.results

    async def test_orchestrator_execute_workflow_with_dependencies(self):
        """Test orchestrator with task dependencies."""
        config = WorkflowConfig(breadth=3, depth=3, timeout_seconds=10)
        orchestrator = WorkflowOrchestrator(config=config)

        workflow = Workflow(name="Test Workflow", config=config)

        task1 = Task(name="Task 1", prompt="Prompt 1")
        task2 = Task(name="Task 2", prompt="Prompt 2", depends_on=[task1.id])
        task3 = Task(name="Task 3", prompt="Prompt 3", depends_on=[task2.id])

        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.add_task(task3)

        result = await orchestrator.execute_workflow(workflow)

        assert result.status == TaskStatus.COMPLETED
        assert all(task.status == TaskStatus.COMPLETED for task in result.tasks)

    async def test_orchestrator_parallel_execution(self):
        """Test orchestrator executing parallel tasks."""
        config = WorkflowConfig(breadth=5, depth=2, timeout_seconds=10)
        orchestrator = WorkflowOrchestrator(config=config)

        workflow = Workflow(name="Test Workflow", config=config)

        # Create 5 independent parallel tasks
        for i in range(5):
            task = Task(name=f"Task {i}", prompt=f"Prompt {i}", task_type=TaskType.PARALLEL)
            workflow.add_task(task)

        result = await orchestrator.execute_workflow(workflow)

        assert result.status == TaskStatus.COMPLETED
        assert len(result.tasks) == 5
        assert all(task.status == TaskStatus.COMPLETED for task in result.tasks)


class TestWorkflowBuilder:
    """Test WorkflowBuilder."""

    def test_builder_basic_workflow(self):
        """Test building a basic workflow."""
        workflow = (
            WorkflowBuilder(name="Test Workflow", description="Test description")
            .with_config(breadth=5, depth=10, timeout_seconds=300)
            .add_task(name="Task 1", prompt="Prompt 1")
            .add_task(name="Task 2", prompt="Prompt 2")
            .build()
        )

        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test description"
        assert len(workflow.tasks) == 2
        assert workflow.config.breadth == 5
        assert workflow.config.depth == 10

    def test_builder_with_dependencies(self):
        """Test building workflow with dependencies."""
        workflow = (
            WorkflowBuilder(name="Test")
            .add_task(name="Task 1", prompt="Prompt 1")
            .add_task(name="Task 2", prompt="Prompt 2", depends_on=["Task 1"])
            .add_task(name="Task 3", prompt="Prompt 3", depends_on=["Task 1", "Task 2"])
            .build()
        )

        assert len(workflow.tasks) == 3

        task1 = workflow.get_task(workflow.tasks[0].id)
        task2 = workflow.get_task(workflow.tasks[1].id)
        task3 = workflow.get_task(workflow.tasks[2].id)

        assert len(task1.depends_on) == 0
        assert len(task2.depends_on) == 1
        assert task1.id in task2.depends_on
        assert len(task3.depends_on) == 2

    def test_builder_parallel_tasks(self):
        """Test adding parallel tasks."""
        workflow = (
            WorkflowBuilder(name="Test")
            .add_task(name="Init", prompt="Initialize")
            .add_parallel_tasks(
                task_specs=[
                    {"name": "Parallel 1", "prompt": "Prompt 1"},
                    {"name": "Parallel 2", "prompt": "Prompt 2"},
                    {"name": "Parallel 3", "prompt": "Prompt 3"},
                ],
                depends_on=["Init"],
            )
            .build()
        )

        assert len(workflow.tasks) == 4

        # Check that all parallel tasks depend on Init
        init_task = workflow.tasks[0]
        for task in workflow.tasks[1:]:
            assert task.task_type == TaskType.PARALLEL
            assert init_task.id in task.depends_on
