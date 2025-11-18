"""
Workflow execution engine with support for parallel and conditional execution.
Orchestrates node execution, handles state management, and emits progress updates.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Callable, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import (
    EdgeType,
    ExecutionStatus,
    NodeStatus,
    NodeType,
    WorkflowExecution,
    WorkflowNode,
)
from app.services.workflow_service import WorkflowService


class WorkflowExecutor:
    """
    Executes workflows with support for:
    - Sequential execution
    - Parallel node execution
    - Conditional branching
    - Error handling and retries
    - Real-time progress updates
    """

    def __init__(
        self,
        db: AsyncSession,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        """
        Initialize workflow executor.

        Args:
            db: Database session
            progress_callback: Optional callback for progress updates (for SSE)
        """
        self.db = db
        self.service = WorkflowService(db)
        self.progress_callback = progress_callback
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool/function that can be executed by nodes.

        Args:
            name: Tool identifier (matches node.tool_name)
            func: Async function to execute
        """
        self.tool_registry[name] = func

    async def execute_workflow(
        self,
        execution_id: UUID,
    ) -> WorkflowExecution:
        """
        Execute a workflow from start to finish.

        Args:
            execution_id: Workflow execution ID

        Returns:
            Completed execution with results

        Raises:
            ValueError: If execution not found or workflow invalid
        """
        execution = await self.service.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        workflow = execution.workflow
        if not workflow:
            raise ValueError("Workflow not found for execution")

        try:
            # Emit start event
            await self._emit_progress(
                execution_id,
                workflow.id,
                "workflow_started",
                {"workflow_name": workflow.name},
            )

            # Main execution loop
            while True:
                # Get nodes ready to execute
                ready_nodes = await self.service.get_ready_nodes(workflow.id)
                if not ready_nodes:
                    # Check if all nodes are completed
                    all_completed = all(
                        node.status in (NodeStatus.COMPLETED, NodeStatus.SKIPPED)
                        for node in workflow.nodes
                    )
                    if all_completed:
                        # Workflow complete
                        await self.service.update_execution_status(
                            execution_id,
                            ExecutionStatus.COMPLETED,
                        )
                        await self._emit_progress(
                            execution_id,
                            workflow.id,
                            "workflow_completed",
                            {"total_nodes": len(workflow.nodes)},
                        )
                        break

                    # Check if any nodes failed
                    any_failed = any(
                        node.status == NodeStatus.FAILED for node in workflow.nodes
                    )
                    if any_failed:
                        await self.service.update_execution_status(
                            execution_id,
                            ExecutionStatus.FAILED,
                        )
                        await self._emit_progress(
                            execution_id,
                            workflow.id,
                            "workflow_failed",
                            {"reason": "One or more nodes failed"},
                        )
                        break

                    # No ready nodes but not complete - might be blocked
                    await self._emit_progress(
                        execution_id,
                        workflow.id,
                        "workflow_blocked",
                        {"reason": "No nodes ready to execute"},
                    )
                    break

                # Separate parallel and sequential nodes
                parallel_nodes = [n for n in ready_nodes if n.can_run_parallel]
                sequential_nodes = [n for n in ready_nodes if not n.can_run_parallel]

                # Execute parallel nodes concurrently
                if parallel_nodes:
                    await self._execute_parallel_nodes(
                        execution_id,
                        parallel_nodes,
                        execution.execution_context,
                    )

                # Execute sequential nodes one by one
                for node in sequential_nodes:
                    await self._execute_node(
                        execution_id,
                        node,
                        execution.execution_context,
                    )

                # Refresh execution to get updated context
                execution = await self.service.get_execution(execution_id)

        except Exception as e:
            # Handle execution errors
            await self.service.update_execution_status(
                execution_id,
                ExecutionStatus.FAILED,
            )
            await self._emit_progress(
                execution_id,
                workflow.id,
                "workflow_error",
                {"error": str(e)},
            )
            raise

        return execution

    async def _execute_parallel_nodes(
        self,
        execution_id: UUID,
        nodes: list[WorkflowNode],
        execution_context: dict[str, Any],
    ) -> None:
        """Execute multiple nodes in parallel."""
        tasks = [
            self._execute_node(execution_id, node, execution_context) for node in nodes
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_node(
        self,
        execution_id: UUID,
        node: WorkflowNode,
        execution_context: dict[str, Any],
    ) -> None:
        """
        Execute a single node.

        Args:
            execution_id: Current execution ID
            node: Node to execute
            execution_context: Shared data between nodes
        """
        try:
            # Update execution current node
            await self.service.update_execution_status(
                execution_id,
                ExecutionStatus.RUNNING,
                current_node_id=node.id,
            )

            # Update node status to in_progress
            await self.service.update_node_status(node.id, NodeStatus.IN_PROGRESS)

            # Emit progress
            await self._emit_progress(
                execution_id,
                node.workflow_id,
                "node_started",
                {
                    "node_id": str(node.id),
                    "node_name": node.name,
                    "node_type": node.node_type.value,
                },
            )

            # Execute based on node type
            if node.node_type == NodeType.TASK:
                output = await self._execute_task_node(node, execution_context)
            elif node.node_type == NodeType.DECISION:
                output = await self._execute_decision_node(node, execution_context)
            elif node.node_type == NodeType.CONDITIONAL:
                output = await self._execute_conditional_node(node, execution_context)
            elif node.node_type == NodeType.INPUT:
                output = await self._execute_input_node(node, execution_context)
            elif node.node_type == NodeType.VERIFICATION:
                output = await self._execute_verification_node(node, execution_context)
            else:
                output = {"status": "skipped", "reason": f"Unsupported node type: {node.node_type}"}

            # Update node with output
            await self.service.update_node_status(
                node.id,
                NodeStatus.COMPLETED,
                output_data=output,
            )

            # Update execution context with node outputs
            if output:
                await self.service.update_execution_context(
                    execution_id,
                    {f"node_{node.id}_output": output},
                )

            # Emit completion
            await self._emit_progress(
                execution_id,
                node.workflow_id,
                "node_completed",
                {
                    "node_id": str(node.id),
                    "node_name": node.name,
                    "output": output,
                },
            )

        except Exception as e:
            # Handle node execution errors
            error_msg = f"Node execution failed: {str(e)}"

            # Check if we should retry
            if node.retry_count < node.max_retries:
                await self.service.update_node_status(
                    node.id,
                    NodeStatus.PENDING,  # Reset to pending for retry
                    error_message=error_msg,
                )
                await self._emit_progress(
                    execution_id,
                    node.workflow_id,
                    "node_retry",
                    {
                        "node_id": str(node.id),
                        "node_name": node.name,
                        "retry_count": node.retry_count + 1,
                        "max_retries": node.max_retries,
                        "error": error_msg,
                    },
                )
            else:
                # Max retries exceeded, mark as failed
                await self.service.update_node_status(
                    node.id,
                    NodeStatus.FAILED,
                    error_message=error_msg,
                )
                await self._emit_progress(
                    execution_id,
                    node.workflow_id,
                    "node_failed",
                    {
                        "node_id": str(node.id),
                        "node_name": node.name,
                        "error": error_msg,
                    },
                )

    async def _execute_task_node(
        self,
        node: WorkflowNode,
        execution_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a task node using registered tools."""
        if not node.tool_name:
            return {"status": "skipped", "reason": "No tool specified"}

        tool_func = self.tool_registry.get(node.tool_name)
        if not tool_func:
            raise ValueError(f"Tool '{node.tool_name}' not registered")

        # Prepare input from node input_schema and execution context
        input_data = node.input_schema or {}

        # Resolve any references to execution context
        resolved_input = self._resolve_context_references(input_data, execution_context)

        # Execute tool
        result = await tool_func(resolved_input)

        return {
            "status": "success",
            "tool": node.tool_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _execute_decision_node(
        self,
        node: WorkflowNode,
        execution_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a decision node (evaluates conditions)."""
        # Decision logic based on input_schema
        condition = node.input_schema or {}
        result = self._evaluate_condition(condition, execution_context)

        return {
            "status": "success",
            "decision": result,
            "condition": condition,
        }

    async def _execute_conditional_node(
        self,
        node: WorkflowNode,
        execution_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a conditional node."""
        # Similar to decision but might have side effects
        condition = node.input_schema or {}
        result = self._evaluate_condition(condition, execution_context)

        return {
            "status": "success",
            "condition_met": result,
        }

    async def _execute_input_node(
        self,
        node: WorkflowNode,
        execution_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle input node (requires user interaction)."""
        # In a real implementation, this would pause execution
        # and wait for user input via the API
        return {
            "status": "waiting_for_input",
            "prompt": node.description,
            "input_schema": node.input_schema,
        }

    async def _execute_verification_node(
        self,
        node: WorkflowNode,
        execution_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a verification/validation node."""
        # Verify previous results meet criteria
        verification_rules = node.input_schema or {}
        passed = True
        errors = []

        for key, rule in verification_rules.items():
            value = execution_context.get(key)
            if not self._verify_value(value, rule):
                passed = False
                errors.append(f"Verification failed for {key}: {rule}")

        return {
            "status": "success" if passed else "failed",
            "passed": passed,
            "errors": errors if not passed else None,
        }

    def _resolve_context_references(
        self,
        data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve references to execution context.
        Supports syntax like: {"input": "$context.node_123_output.result"}
        """
        resolved = {}
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("$context."):
                # Extract context path
                path = value[9:]  # Remove "$context."
                resolved[key] = self._get_nested_value(context, path)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_context_references(value, context)
            else:
                resolved[key] = value
        return resolved

    def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
        """Get nested value from dict using dot notation."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _evaluate_condition(
        self,
        condition: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        """Evaluate a condition against execution context."""
        operator = condition.get("operator", "==")
        left = condition.get("left")
        right = condition.get("right")

        # Resolve context references
        if isinstance(left, str) and left.startswith("$context."):
            left = self._get_nested_value(context, left[9:])
        if isinstance(right, str) and right.startswith("$context."):
            right = self._get_nested_value(context, right[9:])

        # Evaluate
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        elif operator == "in":
            return left in right
        elif operator == "not_in":
            return left not in right
        else:
            return False

    def _verify_value(self, value: Any, rule: dict[str, Any]) -> bool:
        """Verify a value against a rule."""
        rule_type = rule.get("type")

        if rule_type == "not_null":
            return value is not None
        elif rule_type == "not_empty":
            return value is not None and len(value) > 0
        elif rule_type == "equals":
            return value == rule.get("value")
        elif rule_type == "contains":
            return rule.get("value") in value
        elif rule_type == "range":
            min_val = rule.get("min")
            max_val = rule.get("max")
            return (min_val is None or value >= min_val) and (
                max_val is None or value <= max_val
            )
        else:
            return True

    async def _emit_progress(
        self,
        execution_id: UUID,
        workflow_id: UUID,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """Emit progress update via callback (for SSE)."""
        if not self.progress_callback:
            return

        progress_event = {
            "execution_id": str(execution_id),
            "workflow_id": str(workflow_id),
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.progress_callback(progress_event)
