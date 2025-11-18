"""
Task execution engines for multi-step prompting.

This module provides sequential, parallel, and hybrid execution engines
for running tasks in the orchestration system.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID
import logging

from app.agents.task_types import Task, TaskStatus, Workflow


logger = logging.getLogger(__name__)


class TaskExecutor(ABC):
    """
    Abstract base class for task executors.

    Executors are responsible for running tasks and managing their lifecycle.
    """

    @abstractmethod
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task execution result

        Raises:
            Exception: If task execution fails
        """
        pass

    @abstractmethod
    async def execute_tasks(
        self, tasks: List[Task], workflow: Workflow
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Execute multiple tasks.

        Args:
            tasks: List of tasks to execute
            workflow: Parent workflow

        Returns:
            Dictionary mapping task IDs to their results
        """
        pass


class SequentialExecutor(TaskExecutor):
    """
    Executes tasks one after another in sequence.

    Each task waits for the previous task to complete before starting.
    Results from earlier tasks are passed to later tasks via context.
    """

    def __init__(self, timeout_seconds: int = 300):
        """
        Initialize sequential executor.

        Args:
            timeout_seconds: Maximum execution time per task
        """
        self.timeout_seconds = timeout_seconds

    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task with timeout.

        Args:
            task: Task to execute
            context: Execution context including previous results

        Returns:
            Task execution result

        Raises:
            asyncio.TimeoutError: If task execution exceeds timeout
            Exception: If task execution fails
        """
        logger.info(f"Executing task sequentially: {task.name} (ID: {task.id})")

        try:
            # Merge task context with execution context
            merged_context = {**task.context, **context}

            # Mark task as running
            task.mark_running()

            # Execute with timeout
            result = await asyncio.wait_for(
                self._run_task(task, merged_context), timeout=self.timeout_seconds
            )

            # Mark task as completed
            task.mark_completed(result)
            logger.info(f"Task completed successfully: {task.name}")

            return result

        except asyncio.TimeoutError:
            error_msg = f"Task timed out after {self.timeout_seconds} seconds"
            logger.error(f"Task timeout: {task.name} - {error_msg}")
            task.mark_failed(error_msg)
            raise

        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(f"Task error: {task.name} - {error_msg}")
            task.mark_failed(error_msg)
            raise

    async def execute_tasks(
        self, tasks: List[Task], workflow: Workflow
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Execute tasks sequentially, passing results forward.

        Args:
            tasks: List of tasks to execute in order
            workflow: Parent workflow

        Returns:
            Dictionary mapping task IDs to their results
        """
        results: Dict[UUID, Dict[str, Any]] = {}
        context: Dict[str, Any] = {}

        logger.info(f"Starting sequential execution of {len(tasks)} tasks")

        for task in tasks:
            try:
                # Execute task with accumulated context
                result = await self.execute_task(task, context)
                results[task.id] = result

                # Add result to context for next task
                context[f"task_{task.id}_result"] = result
                context[f"task_{task.name}_result"] = result

            except Exception as e:
                logger.error(f"Sequential execution failed at task {task.name}: {e}")

                # Check if task should be retried
                if task.should_retry():
                    task.increment_retry()
                    logger.info(f"Retrying task {task.name} (attempt {task.retry_count})")
                    # Task will be picked up in next iteration
                else:
                    # Stop sequential execution on failure
                    if not workflow.config.enable_retry:
                        break

        logger.info(f"Sequential execution completed with {len(results)} results")
        return results

    async def _run_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to run task logic.

        This is a placeholder that will be overridden or configured
        with actual LLM execution logic.

        Args:
            task: Task to run
            context: Execution context

        Returns:
            Task result
        """
        # TODO: Integrate with LangChain/LangGraph for actual LLM execution
        # For now, return a mock result
        await asyncio.sleep(0.1)  # Simulate processing

        return {
            "task_id": str(task.id),
            "task_name": task.name,
            "prompt": task.prompt,
            "context": context,
            "response": f"Processed: {task.prompt}",
            "metadata": task.metadata,
        }


class ParallelExecutor(TaskExecutor):
    """
    Executes multiple independent tasks concurrently.

    Tasks are executed in parallel up to a maximum breadth limit.
    All tasks receive the same initial context.
    """

    def __init__(self, max_parallel: int = 3, timeout_seconds: int = 300):
        """
        Initialize parallel executor.

        Args:
            max_parallel: Maximum number of tasks to run simultaneously (breadth)
            timeout_seconds: Maximum execution time per task
        """
        self.max_parallel = max_parallel
        self.timeout_seconds = timeout_seconds
        self.semaphore = asyncio.Semaphore(max_parallel)

    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task with concurrency control.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task execution result

        Raises:
            Exception: If task execution fails
        """
        async with self.semaphore:
            logger.info(f"Executing task in parallel: {task.name} (ID: {task.id})")

            try:
                # Merge contexts
                merged_context = {**task.context, **context}

                # Mark task as running
                task.mark_running()

                # Execute with timeout
                result = await asyncio.wait_for(
                    self._run_task(task, merged_context), timeout=self.timeout_seconds
                )

                # Mark task as completed
                task.mark_completed(result)
                logger.info(f"Parallel task completed: {task.name}")

                return result

            except asyncio.TimeoutError:
                error_msg = f"Task timed out after {self.timeout_seconds} seconds"
                logger.error(f"Parallel task timeout: {task.name} - {error_msg}")
                task.mark_failed(error_msg)
                raise

            except Exception as e:
                error_msg = f"Task execution failed: {str(e)}"
                logger.error(f"Parallel task error: {task.name} - {error_msg}")
                task.mark_failed(error_msg)
                raise

    async def execute_tasks(
        self, tasks: List[Task], workflow: Workflow
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Execute tasks in parallel with concurrency control.

        Args:
            tasks: List of tasks to execute concurrently
            workflow: Parent workflow

        Returns:
            Dictionary mapping task IDs to their results
        """
        logger.info(
            f"Starting parallel execution of {len(tasks)} tasks "
            f"(max parallel: {self.max_parallel})"
        )

        # Create execution context from workflow
        context: Dict[str, Any] = {"workflow_id": str(workflow.id)}

        # Create tasks for parallel execution
        task_coroutines = [self.execute_task(task, context) for task in tasks]

        # Execute all tasks concurrently and gather results
        # Use return_exceptions=True to continue even if some tasks fail
        results_list = await asyncio.gather(*task_coroutines, return_exceptions=True)

        # Map results back to task IDs
        results: Dict[UUID, Dict[str, Any]] = {}
        for task, result in zip(tasks, results_list):
            if isinstance(result, Exception):
                logger.error(f"Parallel task {task.name} failed with exception: {result}")
                # Check if task should be retried
                if task.should_retry():
                    task.increment_retry()
                    logger.info(f"Retrying task {task.name} (attempt {task.retry_count})")
            else:
                results[task.id] = result

        logger.info(f"Parallel execution completed with {len(results)}/{len(tasks)} successes")
        return results

    async def _run_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to run task logic.

        This is a placeholder that will be overridden or configured
        with actual LLM execution logic.

        Args:
            task: Task to run
            context: Execution context

        Returns:
            Task result
        """
        # TODO: Integrate with LangChain/LangGraph for actual LLM execution
        # For now, return a mock result
        await asyncio.sleep(0.1)  # Simulate processing

        return {
            "task_id": str(task.id),
            "task_name": task.name,
            "prompt": task.prompt,
            "context": context,
            "response": f"Processed: {task.prompt}",
            "metadata": task.metadata,
        }


class HybridExecutor(TaskExecutor):
    """
    Combines sequential and parallel execution strategies.

    Can execute groups of parallel tasks in sequential stages,
    or run sequential chains in parallel, depending on task dependencies.
    """

    def __init__(
        self, max_parallel: int = 3, timeout_seconds: int = 300, enable_retry: bool = True
    ):
        """
        Initialize hybrid executor.

        Args:
            max_parallel: Maximum number of parallel tasks per stage
            timeout_seconds: Maximum execution time per task
            enable_retry: Enable automatic retry on failure
        """
        self.sequential_executor = SequentialExecutor(timeout_seconds)
        self.parallel_executor = ParallelExecutor(max_parallel, timeout_seconds)
        self.enable_retry = enable_retry

    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task using appropriate executor.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task execution result
        """
        # Delegate to appropriate executor based on task type
        from app.agents.task_types import TaskType

        if task.task_type == TaskType.PARALLEL:
            return await self.parallel_executor.execute_task(task, context)
        else:
            return await self.sequential_executor.execute_task(task, context)

    async def execute_tasks(
        self, tasks: List[Task], workflow: Workflow
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Execute tasks using a hybrid strategy based on dependencies.

        Groups independent tasks into parallel stages, executes stages sequentially.

        Args:
            tasks: List of tasks to execute
            workflow: Parent workflow

        Returns:
            Dictionary mapping task IDs to their results
        """
        logger.info(f"Starting hybrid execution of {len(tasks)} tasks")

        results: Dict[UUID, Dict[str, Any]] = {}
        completed_task_ids: set[UUID] = set()
        remaining_tasks = tasks.copy()

        # Execute in stages until all tasks are complete
        stage = 0
        while remaining_tasks:
            stage += 1
            logger.info(
                f"Hybrid execution stage {stage}: {len(remaining_tasks)} tasks remaining"
            )

            # Find all tasks that can execute in this stage (dependencies met)
            ready_tasks = [
                task for task in remaining_tasks if task.can_execute(completed_task_ids)
            ]

            if not ready_tasks:
                # No tasks ready - check for circular dependencies
                logger.error("No tasks ready to execute - possible circular dependency")
                break

            # Execute ready tasks in parallel
            stage_results = await self.parallel_executor.execute_tasks(ready_tasks, workflow)
            results.update(stage_results)

            # Update completed tasks
            for task in ready_tasks:
                if task.status == TaskStatus.COMPLETED:
                    completed_task_ids.add(task.id)
                    remaining_tasks.remove(task)
                elif task.status == TaskStatus.FAILED and not task.should_retry():
                    # Remove failed tasks that won't be retried
                    remaining_tasks.remove(task)

        logger.info(f"Hybrid execution completed in {stage} stages with {len(results)} results")
        return results


class RetryExecutor:
    """
    Wrapper executor that adds retry logic to any task executor.

    Automatically retries failed tasks up to a maximum number of attempts.
    """

    def __init__(self, base_executor: TaskExecutor, max_retries: int = 3):
        """
        Initialize retry executor.

        Args:
            base_executor: Underlying executor to wrap
            max_retries: Maximum retry attempts
        """
        self.base_executor = base_executor
        self.max_retries = max_retries

    async def execute_with_retry(
        self, task: Task, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute task with automatic retry on failure.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task result if successful, None if all retries failed
        """
        attempts = 0

        while attempts <= self.max_retries:
            try:
                result = await self.base_executor.execute_task(task, context)
                return result

            except Exception as e:
                attempts += 1
                logger.warning(
                    f"Task {task.name} failed (attempt {attempts}/{self.max_retries + 1}): {e}"
                )

                if attempts <= self.max_retries:
                    task.increment_retry()
                    # Exponential backoff
                    backoff = 2**attempts
                    logger.info(f"Retrying task {task.name} after {backoff}s backoff")
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"Task {task.name} failed after {attempts} attempts")
                    return None

        return None
