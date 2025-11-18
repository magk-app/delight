"""
Workflow service for managing node-based planning and execution.
Handles workflow creation, modification, and state management.
"""

from collections import defaultdict
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workflow import (
    EdgeType,
    ExecutionStatus,
    NodeStatus,
    Workflow,
    WorkflowEdge,
    WorkflowExecution,
    WorkflowNode,
    WorkflowStatus,
)
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowEdgeCreate,
    WorkflowNodeCreate,
    WorkflowUpdate,
)


class WorkflowService:
    """Service for workflow operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # Workflow CRUD Operations
    # ========================================================================

    async def create_workflow(
        self,
        user_id: UUID,
        workflow_data: WorkflowCreate,
    ) -> Workflow:
        """
        Create a new workflow with nodes and edges.

        Args:
            user_id: Owner user ID
            workflow_data: Workflow creation data

        Returns:
            Created workflow with nodes and edges
        """
        # Create workflow
        workflow = Workflow(
            user_id=user_id,
            name=workflow_data.name,
            description=workflow_data.description,
            metadata=workflow_data.metadata or {},
            llm_generated=workflow_data.llm_generated,
            status=WorkflowStatus.DRAFT,
        )
        self.db.add(workflow)
        await self.db.flush()  # Get workflow.id

        # Create nodes
        node_id_map = {}  # Map temporary IDs to actual UUIDs
        for idx, node_data in enumerate(workflow_data.nodes):
            node = WorkflowNode(
                workflow_id=workflow.id,
                name=node_data.name,
                description=node_data.description,
                node_type=node_data.node_type,
                tool_name=node_data.tool_name,
                input_schema=node_data.input_schema or {},
                can_run_parallel=node_data.can_run_parallel,
                position=node_data.position.model_dump() if node_data.position else None,
                max_retries=node_data.max_retries,
                status=NodeStatus.PENDING,
            )
            self.db.add(node)
            await self.db.flush()  # Get node.id
            node_id_map[idx] = node.id

        # Create edges
        for edge_data in workflow_data.edges:
            edge = WorkflowEdge(
                workflow_id=workflow.id,
                source_node_id=edge_data.source_node_id,
                target_node_id=edge_data.target_node_id,
                edge_type=edge_data.edge_type,
                condition=edge_data.condition,
            )
            self.db.add(edge)

        await self.db.commit()
        await self.db.refresh(workflow)

        # Load relationships
        return await self.get_workflow_with_details(workflow.id)

    async def get_workflow(self, workflow_id: UUID) -> Workflow | None:
        """Get workflow by ID."""
        result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalar_one_or_none()

    async def get_workflow_with_details(self, workflow_id: UUID) -> Workflow | None:
        """Get workflow with all nodes and edges loaded."""
        result = await self.db.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(
                selectinload(Workflow.nodes),
                selectinload(Workflow.edges),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_workflows(
        self,
        user_id: UUID,
        status: WorkflowStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Workflow], int]:
        """
        Get workflows for a user with pagination.

        Returns:
            Tuple of (workflows, total_count)
        """
        query = select(Workflow).where(Workflow.user_id == user_id)

        if status:
            query = query.where(Workflow.status == status)

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Get paginated results
        query = query.order_by(Workflow.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        workflows = result.scalars().all()

        return list(workflows), total

    async def update_workflow(
        self,
        workflow_id: UUID,
        update_data: WorkflowUpdate,
    ) -> Workflow | None:
        """Update workflow fields."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None

        # Update fields
        if update_data.name is not None:
            workflow.name = update_data.name
        if update_data.description is not None:
            workflow.description = update_data.description
        if update_data.status is not None:
            workflow.status = update_data.status
        if update_data.metadata is not None:
            workflow.metadata = update_data.metadata

        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow_id: UUID) -> bool:
        """Delete workflow (cascades to nodes, edges, executions)."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return False

        await self.db.delete(workflow)
        await self.db.commit()
        return True

    # ========================================================================
    # Node Operations
    # ========================================================================

    async def add_node(
        self,
        workflow_id: UUID,
        node_data: WorkflowNodeCreate,
    ) -> WorkflowNode:
        """Add a new node to an existing workflow."""
        node = WorkflowNode(
            workflow_id=workflow_id,
            name=node_data.name,
            description=node_data.description,
            node_type=node_data.node_type,
            tool_name=node_data.tool_name,
            input_schema=node_data.input_schema or {},
            can_run_parallel=node_data.can_run_parallel,
            position=node_data.position.model_dump() if node_data.position else None,
            max_retries=node_data.max_retries,
            status=NodeStatus.PENDING,
        )
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        return node

    async def update_node_status(
        self,
        node_id: UUID,
        status: NodeStatus,
        output_data: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> WorkflowNode | None:
        """Update node execution status."""
        result = await self.db.execute(select(WorkflowNode).where(WorkflowNode.id == node_id))
        node = result.scalar_one_or_none()
        if not node:
            return None

        node.status = status

        if status == NodeStatus.IN_PROGRESS and not node.started_at:
            node.started_at = datetime.utcnow()

        if status in (NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.SKIPPED):
            node.completed_at = datetime.utcnow()

        if output_data is not None:
            node.output_data = output_data

        if error_message is not None:
            node.error_message = error_message

        if status == NodeStatus.FAILED:
            node.retry_count += 1

        await self.db.commit()
        await self.db.refresh(node)
        return node

    async def get_node(self, node_id: UUID) -> WorkflowNode | None:
        """Get node by ID."""
        result = await self.db.execute(select(WorkflowNode).where(WorkflowNode.id == node_id))
        return result.scalar_one_or_none()

    # ========================================================================
    # Edge Operations
    # ========================================================================

    async def add_edge(
        self,
        workflow_id: UUID,
        edge_data: WorkflowEdgeCreate,
    ) -> WorkflowEdge:
        """Add a new edge to connect nodes."""
        edge = WorkflowEdge(
            workflow_id=workflow_id,
            source_node_id=edge_data.source_node_id,
            target_node_id=edge_data.target_node_id,
            edge_type=edge_data.edge_type,
            condition=edge_data.condition,
        )
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge

    async def delete_edge(self, edge_id: UUID) -> bool:
        """Delete an edge."""
        result = await self.db.execute(select(WorkflowEdge).where(WorkflowEdge.id == edge_id))
        edge = result.scalar_one_or_none()
        if not edge:
            return False

        await self.db.delete(edge)
        await self.db.commit()
        return True

    # ========================================================================
    # Execution Operations
    # ========================================================================

    async def create_execution(
        self,
        workflow_id: UUID,
        execution_context: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Start a new workflow execution."""
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=ExecutionStatus.RUNNING,
            execution_context=execution_context or {},
            started_at=datetime.utcnow(),
        )
        self.db.add(execution)

        # Update workflow status
        workflow = await self.get_workflow(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.EXECUTING

        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def get_execution(self, execution_id: UUID) -> WorkflowExecution | None:
        """Get execution by ID."""
        result = await self.db.execute(
            select(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .options(
                selectinload(WorkflowExecution.workflow).selectinload(Workflow.nodes),
                selectinload(WorkflowExecution.workflow).selectinload(Workflow.edges),
            )
        )
        return result.scalar_one_or_none()

    async def update_execution_status(
        self,
        execution_id: UUID,
        status: ExecutionStatus,
        current_node_id: UUID | None = None,
    ) -> WorkflowExecution | None:
        """Update execution status."""
        result = await self.db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        if not execution:
            return None

        execution.status = status
        if current_node_id is not None:
            execution.current_node_id = current_node_id

        if status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            execution.completed_at = datetime.utcnow()

            # Update workflow status
            workflow = await self.get_workflow(execution.workflow_id)
            if workflow:
                workflow.status = (
                    WorkflowStatus.COMPLETED
                    if status == ExecutionStatus.COMPLETED
                    else WorkflowStatus.FAILED
                )

        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def update_execution_context(
        self,
        execution_id: UUID,
        context_updates: dict[str, Any],
    ) -> WorkflowExecution | None:
        """Update shared execution context."""
        result = await self.db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        if not execution:
            return None

        # Merge context updates
        current_context = execution.execution_context or {}
        current_context.update(context_updates)
        execution.execution_context = current_context

        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    # ========================================================================
    # Workflow Analysis & Planning Helpers
    # ========================================================================

    async def get_ready_nodes(self, workflow_id: UUID) -> list[WorkflowNode]:
        """
        Get nodes that are ready to execute.
        A node is ready if all its dependencies (incoming edges) are completed.
        """
        workflow = await self.get_workflow_with_details(workflow_id)
        if not workflow:
            return []

        ready_nodes = []
        for node in workflow.nodes:
            if node.status != NodeStatus.PENDING:
                continue

            # Check if all dependencies are completed
            dependencies_met = True
            for edge in node.incoming_edges:
                source_node = await self.get_node(edge.source_node_id)
                if source_node and source_node.status != NodeStatus.COMPLETED:
                    dependencies_met = False
                    break

            if dependencies_met:
                # Mark as ready
                node.status = NodeStatus.READY
                ready_nodes.append(node)

        if ready_nodes:
            await self.db.commit()

        return ready_nodes

    async def get_parallel_nodes(self, workflow_id: UUID) -> list[WorkflowNode]:
        """Get nodes that can run in parallel."""
        ready_nodes = await self.get_ready_nodes(workflow_id)
        return [node for node in ready_nodes if node.can_run_parallel]

    async def validate_workflow_structure(self, workflow_id: UUID) -> tuple[bool, list[str]]:
        """
        Validate workflow structure for cycles, orphaned nodes, etc.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        workflow = await self.get_workflow_with_details(workflow_id)
        if not workflow:
            return False, ["Workflow not found"]

        errors = []

        # Check for cycles using DFS with color marking
        if self._has_cycle(workflow.nodes, workflow.edges):
            errors.append("Workflow contains a cycle (circular dependency)")

        # Check for orphaned nodes (no incoming or outgoing edges)
        for node in workflow.nodes:
            if not node.incoming_edges and not node.outgoing_edges:
                if len(workflow.nodes) > 1:  # Single node workflows are OK
                    errors.append(f"Node '{node.name}' is orphaned (no connections)")

        return len(errors) == 0, errors

    def _has_cycle(self, nodes: list[WorkflowNode], edges: list[WorkflowEdge]) -> bool:
        """
        Detect cycles in workflow graph using DFS with color marking.

        Color scheme:
        - 0 (white): unvisited
        - 1 (gray): currently being visited (in DFS stack)
        - 2 (black): completely visited

        A back edge (edge to a gray node) indicates a cycle.
        """
        # Build adjacency list
        graph = defaultdict(list)
        for edge in edges:
            graph[edge.source_node_id].append(edge.target_node_id)

        # Initialize colors: 0=white (unvisited), 1=gray (visiting), 2=black (visited)
        color = {node.id: 0 for node in nodes}

        def dfs(node_id: UUID) -> bool:
            """DFS helper that returns True if a cycle is detected."""
            if color[node_id] == 1:  # Gray node - back edge found (cycle!)
                return True
            if color[node_id] == 2:  # Black node - already fully processed
                return False

            # Mark as gray (visiting)
            color[node_id] = 1

            # Visit all neighbors
            for neighbor_id in graph[node_id]:
                if dfs(neighbor_id):
                    return True

            # Mark as black (visited)
            color[node_id] = 2
            return False

        # Check from all nodes (handles disconnected components)
        for node in nodes:
            if color[node.id] == 0:  # Unvisited
                if dfs(node.id):
                    return True

        return False
