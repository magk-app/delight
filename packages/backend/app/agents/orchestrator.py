"""
Multi-step prompting orchestrator.

This module provides the main orchestrator that coordinates the execution
of complex multi-step workflows with parallel and sequential task execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from uuid import UUID

from app.agents.task_types import (
    Task,
    TaskStatus,
    TaskType,
    Workflow,
    WorkflowConfig,
)
from app.agents.executors import (
    SequentialExecutor,
    ParallelExecutor,
    HybridExecutor,
    RetryExecutor,
)


logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Main orchestrator for multi-step prompting workflows.

    Coordinates the execution of complex workflows that combine sequential
    and parallel task execution, handles retries, manages state, and
    aggregates results.
    """

    def __init__(
        self,
        config: Optional[WorkflowConfig] = None,
        task_runner: Optional[Callable] = None,
    ):
        """
        Initialize workflow orchestrator.

        Args:
            config: Workflow execution configuration
            task_runner: Custom task runner function for executing prompts
        """
        self.config = config or WorkflowConfig()
        self.task_runner = task_runner

        # Initialize executors
        self.sequential_executor = SequentialExecutor(self.config.timeout_seconds)
        self.parallel_executor = ParallelExecutor(
            max_parallel=self.config.breadth, timeout_seconds=self.config.timeout_seconds
        )
        self.hybrid_executor = HybridExecutor(
            max_parallel=self.config.breadth,
            timeout_seconds=self.config.timeout_seconds,
            enable_retry=self.config.enable_retry,
        )

        # If custom task runner provided, inject it into executors
        if task_runner:
            self._inject_task_runner(task_runner)

    def _inject_task_runner(self, task_runner: Callable) -> None:
        """
        Inject custom task runner into all executors.

        Args:
            task_runner: Custom task runner function
        """
        self.sequential_executor._run_task = task_runner
        self.parallel_executor._run_task = task_runner

    async def execute_workflow(self, workflow: Workflow) -> Workflow:
        """
        Execute a complete workflow.

        This is the main entry point for workflow execution. It handles:
        1. Workflow initialization
        2. Iterative execution over depth cycles
        3. Retry logic for failed tasks
        4. Result aggregation
        5. Status management

        Args:
            workflow: Workflow to execute

        Returns:
            Updated workflow with execution results
        """
        logger.info(f"Starting workflow execution: {workflow.name} (ID: {workflow.id})")

        # Mark workflow as running
        workflow.status = TaskStatus.RUNNING
        workflow.started_at = datetime.utcnow()

        try:
            # Execute workflow with depth iterations
            for depth in range(self.config.depth):
                workflow.current_depth = depth + 1
                logger.info(
                    f"Workflow depth iteration {workflow.current_depth}/{self.config.depth}"
                )

                # Execute one iteration
                iteration_results = await self._execute_iteration(workflow)

                # Store intermediate results if configured
                if self.config.collect_intermediate:
                    workflow.results[f"depth_{workflow.current_depth}"] = iteration_results

                # Check if workflow is complete
                if workflow.is_complete():
                    logger.info(f"Workflow completed at depth {workflow.current_depth}")
                    break

                # Handle retries for failed tasks
                if self.config.enable_retry:
                    failed_tasks = workflow.get_failed_tasks()
                    if failed_tasks:
                        logger.info(f"Retrying {len(failed_tasks)} failed tasks")
                        for task in failed_tasks:
                            task.increment_retry()

            # Mark workflow as completed or failed
            if workflow.has_failures():
                workflow.status = TaskStatus.FAILED
                logger.warning(f"Workflow completed with failures: {workflow.name}")
            else:
                workflow.status = TaskStatus.COMPLETED
                logger.info(f"Workflow completed successfully: {workflow.name}")

            workflow.completed_at = datetime.utcnow()

            # Aggregate final results
            workflow.results["summary"] = self._aggregate_results(workflow)
            workflow.results["execution_summary"] = workflow.get_execution_summary()

        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            workflow.status = TaskStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            workflow.results["error"] = str(e)

        return workflow

    async def _execute_iteration(self, workflow: Workflow) -> Dict[UUID, Dict[str, Any]]:
        """
        Execute one iteration of the workflow.

        An iteration processes all ready tasks based on their execution strategy.

        Args:
            workflow: Workflow to execute

        Returns:
            Dictionary mapping task IDs to their results
        """
        # Get tasks ready to execute
        ready_tasks = workflow.get_ready_tasks()

        if not ready_tasks:
            logger.info("No tasks ready to execute in this iteration")
            return {}

        logger.info(f"Executing {len(ready_tasks)} ready tasks")

        # Group tasks by execution type
        sequential_tasks = [t for t in ready_tasks if t.task_type == TaskType.SEQUENTIAL]
        parallel_tasks = [t for t in ready_tasks if t.task_type == TaskType.PARALLEL]
        hybrid_tasks = [t for t in ready_tasks if t.task_type == TaskType.HYBRID]

        results: Dict[UUID, Dict[str, Any]] = {}

        # Execute parallel tasks first (independent)
        if parallel_tasks:
            logger.info(f"Executing {len(parallel_tasks)} parallel tasks")
            parallel_results = await self.parallel_executor.execute_tasks(
                parallel_tasks, workflow
            )
            results.update(parallel_results)

        # Execute sequential tasks (may depend on parallel results)
        if sequential_tasks:
            logger.info(f"Executing {len(sequential_tasks)} sequential tasks")
            sequential_results = await self.sequential_executor.execute_tasks(
                sequential_tasks, workflow
            )
            results.update(sequential_results)

        # Execute hybrid tasks (complex dependencies)
        if hybrid_tasks:
            logger.info(f"Executing {len(hybrid_tasks)} hybrid tasks")
            hybrid_results = await self.hybrid_executor.execute_tasks(hybrid_tasks, workflow)
            results.update(hybrid_results)

        return results

    def _aggregate_results(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Aggregate results from all tasks in the workflow.

        Args:
            workflow: Completed workflow

        Returns:
            Aggregated results dictionary
        """
        completed_tasks = [t for t in workflow.tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]

        aggregated = {
            "total_tasks": len(workflow.tasks),
            "completed_count": len(completed_tasks),
            "failed_count": len(failed_tasks),
            "success_rate": (
                len(completed_tasks) / len(workflow.tasks) if workflow.tasks else 0
            ),
            "completed_tasks": [
                {
                    "id": str(task.id),
                    "name": task.name,
                    "result": task.result,
                    "duration_seconds": (
                        (task.completed_at - task.started_at).total_seconds()
                        if task.started_at and task.completed_at
                        else None
                    ),
                }
                for task in completed_tasks
            ],
            "failed_tasks": [
                {"id": str(task.id), "name": task.name, "error": task.error}
                for task in failed_tasks
            ],
        }

        return aggregated

    async def execute_plan_and_execute_workflow(
        self, objective: str, context: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        High-level workflow: Plan → Execute → Reflect.

        This implements a common pattern where:
        1. Plan: Create a plan for achieving the objective
        2. Execute: Run the planned tasks (possibly in parallel)
        3. Reflect: Review and consolidate results

        Args:
            objective: The goal to achieve
            context: Optional context for planning

        Returns:
            Completed workflow with results
        """
        logger.info(f"Starting plan-execute-reflect workflow: {objective}")

        # Create workflow
        workflow = Workflow(
            name=f"Plan-Execute-Reflect: {objective}",
            description="Automated workflow with planning, execution, and reflection",
            config=self.config,
        )

        # Phase 1: Planning
        plan_task = Task(
            name="Plan",
            description="Create execution plan for the objective",
            prompt=f"Create a detailed plan to achieve this objective: {objective}",
            task_type=TaskType.SEQUENTIAL,
            context=context or {},
        )
        workflow.add_task(plan_task)

        # Execute planning phase
        await self.sequential_executor.execute_task(plan_task, {})

        # Phase 2: Extract sub-tasks from plan and execute in parallel
        if plan_task.status == TaskStatus.COMPLETED and plan_task.result:
            # TODO: Parse plan result to extract sub-tasks
            # For now, create example sub-tasks
            sub_tasks = self._extract_tasks_from_plan(plan_task.result, objective)

            for sub_task in sub_tasks:
                sub_task.depends_on = [plan_task.id]  # Depend on planning
                workflow.add_task(sub_task)

        # Phase 3: Reflection
        reflect_task = Task(
            name="Reflect",
            description="Consolidate and review results",
            prompt=f"Review the results and provide a final answer for: {objective}",
            task_type=TaskType.SEQUENTIAL,
            context={},
        )
        # Reflection depends on all sub-tasks
        reflect_task.depends_on = [
            t.id for t in workflow.tasks if t.id != plan_task.id and t != reflect_task
        ]
        workflow.add_task(reflect_task)

        # Execute the complete workflow
        result = await self.execute_workflow(workflow)

        return result

    def _extract_tasks_from_plan(
        self, plan_result: Dict[str, Any], objective: str
    ) -> List[Task]:
        """
        Extract executable tasks from a planning result.

        This is a placeholder that should be enhanced with actual
        plan parsing logic.

        Args:
            plan_result: Result from planning task
            objective: Original objective

        Returns:
            List of tasks extracted from plan
        """
        # TODO: Implement intelligent plan parsing
        # For now, create example tasks
        tasks = [
            Task(
                name="Gather Information",
                description="Collect relevant information",
                prompt=f"Gather information relevant to: {objective}",
                task_type=TaskType.PARALLEL,
            ),
            Task(
                name="Analyze Data",
                description="Analyze collected information",
                prompt=f"Analyze the gathered information for: {objective}",
                task_type=TaskType.PARALLEL,
            ),
            Task(
                name="Synthesize Solution",
                description="Create solution from analysis",
                prompt=f"Synthesize a solution for: {objective}",
                task_type=TaskType.SEQUENTIAL,
            ),
        ]

        return tasks


class WorkflowBuilder:
    """
    Builder class for constructing workflows programmatically.

    Provides a fluent interface for creating complex workflows.
    """

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize workflow builder.

        Args:
            name: Workflow name
            description: Workflow description
        """
        self.workflow = Workflow(name=name, description=description)
        self._task_map: Dict[str, Task] = {}

    def with_config(
        self,
        breadth: Optional[int] = None,
        depth: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
    ) -> "WorkflowBuilder":
        """
        Configure workflow parameters.

        Args:
            breadth: Maximum parallel tasks
            depth: Maximum iteration depth
            timeout_seconds: Task timeout

        Returns:
            Self for chaining
        """
        if breadth is not None:
            self.workflow.config.breadth = breadth
        if depth is not None:
            self.workflow.config.depth = depth
        if timeout_seconds is not None:
            self.workflow.config.timeout_seconds = timeout_seconds

        return self

    def add_task(
        self,
        name: str,
        prompt: str,
        task_type: TaskType = TaskType.SEQUENTIAL,
        depends_on: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "WorkflowBuilder":
        """
        Add a task to the workflow.

        Args:
            name: Task name (also used as reference key)
            prompt: Task prompt
            task_type: Execution type
            depends_on: List of task names this task depends on
            context: Task context

        Returns:
            Self for chaining
        """
        task = Task(
            name=name,
            prompt=prompt,
            task_type=task_type,
            context=context or {},
        )

        # Resolve dependencies
        if depends_on:
            for dep_name in depends_on:
                if dep_name in self._task_map:
                    task.depends_on.append(self._task_map[dep_name].id)
                else:
                    logger.warning(f"Dependency '{dep_name}' not found for task '{name}'")

        self.workflow.add_task(task)
        self._task_map[name] = task

        return self

    def add_parallel_tasks(
        self, task_specs: List[Dict[str, Any]], depends_on: Optional[List[str]] = None
    ) -> "WorkflowBuilder":
        """
        Add multiple parallel tasks at once.

        Args:
            task_specs: List of task specifications (name, prompt, context)
            depends_on: Common dependencies for all tasks

        Returns:
            Self for chaining
        """
        for spec in task_specs:
            self.add_task(
                name=spec["name"],
                prompt=spec["prompt"],
                task_type=TaskType.PARALLEL,
                depends_on=depends_on,
                context=spec.get("context"),
            )

        return self

    def build(self) -> Workflow:
        """
        Build and return the workflow.

        Returns:
            Constructed workflow
        """
        return self.workflow
