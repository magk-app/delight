"""
LLM-powered workflow planning service.
Generates node-based workflows from natural language user queries.
"""

import json
from typing import Any
from uuid import UUID

import openai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.workflow import (
    EdgeType,
    NodeType,
    Workflow,
)
from app.schemas.workflow import (
    NodePositionSchema,
    WorkflowCreate,
    WorkflowEdgeCreate,
    WorkflowNodeCreate,
)
from app.services.workflow_service import WorkflowService

settings = get_settings()


class WorkflowPlanner:
    """
    Generates workflow plans using LLM.
    Converts user queries into structured node-based workflows.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = WorkflowService(db)
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_workflow_plan(
        self,
        user_id: UUID,
        user_query: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[Workflow, str]:
        """
        Generate a workflow plan from user query using LLM.

        Args:
            user_id: User ID
            user_query: Natural language task description
            context: Additional context for planning

        Returns:
            Tuple of (created workflow, plan summary)
        """
        # Build prompt for LLM
        system_prompt = self._build_planning_system_prompt()
        user_prompt = self._build_planning_user_prompt(user_query, context)

        # Call LLM to generate plan
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        # Parse LLM response
        plan_data = json.loads(response.choices[0].message.content)

        # Convert LLM plan to workflow structure
        workflow = await self._create_workflow_from_plan(
            user_id,
            user_query,
            plan_data,
        )

        # Generate human-readable summary
        summary = plan_data.get("summary", "Workflow plan generated")

        return workflow, summary

    def _build_planning_system_prompt(self) -> str:
        """Build system prompt for workflow planning."""
        return """You are an AI workflow planner that converts user tasks into structured, node-based workflows.

Your job is to:
1. Analyze the user's task or query
2. Break it down into discrete steps (nodes)
3. Identify dependencies between steps
4. Determine which steps can run in parallel
5. Add decision points and conditional logic where needed
6. Output a structured JSON workflow plan

Node Types:
- task: Regular execution task (fetch data, process, etc.)
- decision: Decision point (if/else logic)
- conditional: Conditional execution based on previous results
- input: Requires user input
- verification: Validates results meet criteria
- parallel_group: Group of tasks that can run simultaneously

Edge Types:
- sequential: One step after another
- parallel: Can run at the same time
- conditional: Transition depends on condition

Output Format (JSON):
{
  "workflow_name": "string",
  "workflow_description": "string",
  "summary": "Human-readable summary of the plan",
  "estimated_duration": "string (e.g., '5-10 minutes')",
  "nodes": [
    {
      "id": "string (unique identifier like 'node_1')",
      "name": "string",
      "description": "string",
      "node_type": "task|decision|conditional|input|verification|parallel_group",
      "tool_name": "string|null (name of tool to use)",
      "input_schema": {},
      "can_run_parallel": boolean,
      "position": {"x": number, "y": number}
    }
  ],
  "edges": [
    {
      "source": "string (node id)",
      "target": "string (node id)",
      "edge_type": "sequential|parallel|conditional",
      "condition": {} // optional, for conditional edges
    }
  ]
}

Guidelines:
- Keep workflows simple and focused (5-15 nodes typically)
- Mark independent tasks as can_run_parallel: true
- Use clear, descriptive names
- Include verification nodes for critical outputs
- Add decision nodes for branching logic
- Position nodes logically (left-to-right flow, y increases by 100 per level)
- Always include summary and estimated_duration
"""

    def _build_planning_user_prompt(
        self,
        user_query: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Build user prompt for workflow planning."""
        prompt = f"Create a workflow plan for the following task:\n\n{user_query}"

        if context:
            prompt += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"

        prompt += "\n\nGenerate a complete workflow plan in JSON format."

        return prompt

    async def _create_workflow_from_plan(
        self,
        user_id: UUID,
        user_query: str,
        plan_data: dict[str, Any],
    ) -> Workflow:
        """Convert LLM plan data into workflow database objects."""
        # Create nodes
        nodes_create = []
        node_id_map = {}  # Map LLM node IDs to indices

        for idx, node_data in enumerate(plan_data.get("nodes", [])):
            llm_node_id = node_data.get("id")
            node_id_map[llm_node_id] = idx

            position = node_data.get("position")
            position_schema = None
            if position:
                position_schema = NodePositionSchema(
                    x=position.get("x", 0),
                    y=position.get("y", 0),
                )

            node = WorkflowNodeCreate(
                name=node_data.get("name", f"Step {idx + 1}"),
                description=node_data.get("description"),
                node_type=NodeType(node_data.get("node_type", "task")),
                tool_name=node_data.get("tool_name"),
                input_schema=node_data.get("input_schema", {}),
                can_run_parallel=node_data.get("can_run_parallel", False),
                position=position_schema,
                max_retries=3,
            )
            nodes_create.append(node)

        # Create workflow with nodes
        workflow_create = WorkflowCreate(
            name=plan_data.get("workflow_name", "Generated Workflow"),
            description=plan_data.get("workflow_description", user_query),
            llm_generated=True,
            metadata={
                "user_query": user_query,
                "estimated_duration": plan_data.get("estimated_duration"),
                "llm_model": "gpt-4o-mini",
            },
            nodes=nodes_create,
            edges=[],  # Will add edges separately after nodes are created
        )

        # Create workflow
        workflow = await self.service.create_workflow(user_id, workflow_create)

        # Now create edges with actual node IDs
        # We need to map LLM node IDs to actual database UUIDs
        llm_to_db_map = {}
        for idx, node in enumerate(workflow.nodes):
            # Find corresponding LLM node ID
            llm_node_id = plan_data["nodes"][idx].get("id")
            llm_to_db_map[llm_node_id] = node.id

        # Create edges
        for edge_data in plan_data.get("edges", []):
            source_llm_id = edge_data.get("source")
            target_llm_id = edge_data.get("target")

            if source_llm_id in llm_to_db_map and target_llm_id in llm_to_db_map:
                edge_create = WorkflowEdgeCreate(
                    source_node_id=llm_to_db_map[source_llm_id],
                    target_node_id=llm_to_db_map[target_llm_id],
                    edge_type=EdgeType(edge_data.get("edge_type", "sequential")),
                    condition=edge_data.get("condition"),
                )
                await self.service.add_edge(workflow.id, edge_create)

        # Refresh workflow with edges
        workflow = await self.service.get_workflow_with_details(workflow.id)

        return workflow

    async def refine_workflow_plan(
        self,
        workflow_id: UUID,
        user_feedback: str,
    ) -> Workflow:
        """
        Refine an existing workflow based on user feedback.

        Args:
            workflow_id: Workflow to refine
            user_feedback: User's feedback or requested changes

        Returns:
            Updated workflow
        """
        workflow = await self.service.get_workflow_with_details(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Build refinement prompt
        current_plan = self._workflow_to_dict(workflow)

        system_prompt = """You are refining a workflow plan based on user feedback.

Analyze the current workflow and user feedback, then output an updated JSON workflow plan.
Maintain the same JSON structure as the original plan.
Only modify what's needed based on the feedback."""

        user_prompt = f"""Current Workflow:
{json.dumps(current_plan, indent=2)}

User Feedback:
{user_feedback}

Generate the refined workflow plan in JSON format."""

        # Call LLM
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        # Parse and apply changes
        refined_plan = json.loads(response.choices[0].message.content)

        # Update workflow
        # TODO: Implement intelligent merging of changes
        # For now, we'll update basic workflow fields
        await self.service.update_workflow(
            workflow_id,
            WorkflowUpdate(
                name=refined_plan.get("workflow_name", workflow.name),
                description=refined_plan.get("workflow_description", workflow.description),
            ),
        )

        return await self.service.get_workflow_with_details(workflow_id)

    def _workflow_to_dict(self, workflow: Workflow) -> dict[str, Any]:
        """Convert workflow to dictionary for LLM."""
        return {
            "workflow_name": workflow.name,
            "workflow_description": workflow.description,
            "nodes": [
                {
                    "id": str(node.id),
                    "name": node.name,
                    "description": node.description,
                    "node_type": node.node_type.value,
                    "tool_name": node.tool_name,
                    "input_schema": node.input_schema,
                    "can_run_parallel": node.can_run_parallel,
                    "position": node.position,
                }
                for node in workflow.nodes
            ],
            "edges": [
                {
                    "source": str(edge.source_node_id),
                    "target": str(edge.target_node_id),
                    "edge_type": edge.edge_type.value,
                    "condition": edge.condition,
                }
                for edge in workflow.edges
            ],
        }


# Import WorkflowUpdate
from app.schemas.workflow import WorkflowUpdate
