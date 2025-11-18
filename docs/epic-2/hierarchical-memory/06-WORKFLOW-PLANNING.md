# Node-Based Workflow Planning for Transparency

**Date:** 2025-11-18
**Epic:** Epic 2 - Companion & Memory System
**Purpose:** Design transparent, user-visible workflow planning using node-based graph representation

---

## Table of Contents

1. [Overview](#overview)
2. [Why Transparency Matters](#why-transparency-matters)
3. [Node-Based Workflow Design](#node-based-workflow-design)
4. [Showing Plans to Users](#showing-plans-to-users)
5. [Milestone Progress Updates](#milestone-progress-updates)
6. [Dynamic Plan Adjustment](#dynamic-plan-adjustment)
7. [Implementation Examples](#implementation-examples)

---

## Overview

Traditional AI systems operate as "black boxes"—users don't see how the AI reaches conclusions or what steps it's taking. **Node-based workflow planning** makes AI reasoning transparent by:

1. **Showing the plan** before execution ("Here's how I'll help...")
2. **Visualizing progress** through workflow nodes
3. **Allowing user feedback** to adjust the plan mid-execution
4. **Explaining decisions** at each node

This builds **trust**, creates **collaboration**, and gives users **control** over AI assistance.

### Design Principles

1. **Show, Don't Hide**: Make AI reasoning visible to users
2. **Collaborative Planning**: Let users approve or modify plans
3. **Progress Transparency**: Update users at key milestones
4. **Adjustable Workflows**: Allow mid-flight plan changes
5. **Educational**: Help users understand what the AI is doing

---

## Why Transparency Matters

### The Black Box Problem

**Without transparency**:
```
User: "Help me train for a marathon"
AI: [Internal processing...]
AI: "Here's your 12-week training plan!"
```

**User questions**:
- How did you come up with this plan?
- Why 12 weeks instead of 16?
- Can I modify the schedule?
- What if I miss a week?

**Result**: User feels uncertain, doesn't trust the plan, might not follow through.

### The Transparent Approach

**With node-based workflow planning**:
```
User: "Help me train for a marathon"

AI: "Here's my plan to create your marathon training program:

1. ✓ Assess your current fitness level
2. ✓ Determine timeline (12 weeks based on goal date)
3. → Break down into 4 training phases
4.   Generate weekly mission schedules
5.   Create recovery and rest protocols
6.   Set up progress milestones

Shall I proceed? Feel free to adjust any step."

User: "Actually, can you make it 16 weeks? I want more buffer time."

AI: "Absolutely! Updating timeline to 16 weeks...
2. ✓ Determine timeline (16 weeks with more gradual progression)
   Proceeding with adjusted plan..."
```

**Result**: User understands the process, feels in control, trusts the AI's approach.

---

## Node-Based Workflow Design

### Workflow as Graph

Represent complex processes as a graph of nodes:

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class NodeStatus(Enum):
    """Status of a workflow node."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"

@dataclass
class WorkflowNode:
    """A single node in the workflow graph."""

    node_id: str
    title: str  # User-friendly title
    description: str  # What this node does
    status: NodeStatus
    depends_on: List[str]  # List of node_ids this depends on
    result: Optional[dict] = None  # Output of this node
    error: Optional[str] = None  # Error message if failed

@dataclass
class Workflow:
    """Complete workflow with all nodes."""

    workflow_id: str
    title: str  # Overall workflow title
    description: str  # What this workflow achieves
    nodes: List[WorkflowNode]
    current_node: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
```

### Example: Goal Decomposition Workflow

```python
def create_goal_decomposition_workflow(goal_id: str) -> Workflow:
    """Create workflow for decomposing a goal into missions."""

    nodes = [
        WorkflowNode(
            node_id="analyze_goal",
            title="Analyze Goal",
            description="Understand the goal's complexity and requirements",
            status=NodeStatus.PENDING,
            depends_on=[]
        ),
        WorkflowNode(
            node_id="identify_milestones",
            title="Identify Milestones",
            description="Break down goal into 3-7 major milestones",
            status=NodeStatus.PENDING,
            depends_on=["analyze_goal"]
        ),
        WorkflowNode(
            node_id="generate_missions",
            title="Generate Missions",
            description="Create daily missions for each milestone",
            status=NodeStatus.PENDING,
            depends_on=["identify_milestones"]
        ),
        WorkflowNode(
            node_id="estimate_timeline",
            title="Estimate Timeline",
            description="Calculate expected completion dates",
            status=NodeStatus.PENDING,
            depends_on=["generate_missions"]
        ),
        WorkflowNode(
            node_id="create_database",
            title="Save to Database",
            description="Store missions and schedule",
            status=NodeStatus.PENDING,
            depends_on=["estimate_timeline"]
        )
    ]

    return Workflow(
        workflow_id=f"goal_decomp_{goal_id}",
        title="Goal Decomposition",
        description=f"Breaking down your goal into actionable missions",
        nodes=nodes,
        current_node="analyze_goal"
    )
```

---

## Showing Plans to Users

### Plan Preview (Before Execution)

```python
async def show_workflow_plan(
    user_id: str,
    workflow: Workflow
) -> str:
    """
    Generate user-friendly workflow preview.

    Returns formatted plan for user approval.
    """

    # Build plan text
    plan_text = f"**{workflow.title}**\n\n"
    plan_text += f"{workflow.description}\n\n"
    plan_text += "Here's my plan:\n\n"

    for i, node in enumerate(workflow.nodes, 1):
        # Format based on status
        if node.status == NodeStatus.COMPLETED:
            icon = "✓"
        elif node.status == NodeStatus.IN_PROGRESS:
            icon = "→"
        else:
            icon = " "

        plan_text += f"{i}. {icon} {node.title}\n"
        plan_text += f"   {node.description}\n\n"

    plan_text += "\nShall I proceed? You can adjust any step before we begin."

    return plan_text

# Usage in Eliza agent
workflow = create_goal_decomposition_workflow(goal_id)
plan_preview = await show_workflow_plan(user_id, workflow)

# Show to user (via chat)
await send_message_to_user(user_id, plan_preview)

# Wait for user approval
user_response = await wait_for_user_input(user_id)

if "adjust" in user_response.lower() or "change" in user_response.lower():
    # User wants to modify plan
    await handle_plan_modification(user_id, workflow, user_response)
else:
    # User approved, execute workflow
    await execute_workflow(user_id, workflow)
```

### Frontend Visualization

Display workflow as interactive flowchart:

```tsx
// frontend/src/components/companion/WorkflowPlan.tsx

import { useState } from 'react';

interface WorkflowNodeProps {
  node: {
    node_id: string;
    title: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
  };
}

function WorkflowNode({ node }: WorkflowNodeProps) {
  const statusColors = {
    pending: 'bg-gray-200 text-gray-700',
    in_progress: 'bg-blue-500 text-white animate-pulse',
    completed: 'bg-green-500 text-white',
    failed: 'bg-red-500 text-white'
  };

  const statusIcons = {
    pending: '○',
    in_progress: '→',
    completed: '✓',
    failed: '✗'
  };

  return (
    <div className={`p-4 rounded-lg ${statusColors[node.status]} shadow-md`}>
      <div className="flex items-center gap-2">
        <span className="text-2xl">{statusIcons[node.status]}</span>
        <h3 className="font-semibold">{node.title}</h3>
      </div>
      <p className="text-sm mt-2 opacity-90">{node.description}</p>
    </div>
  );
}

export function WorkflowPlan({ workflow }: { workflow: Workflow }) {
  return (
    <div className="space-y-4 p-6">
      <h2 className="text-2xl font-bold">{workflow.title}</h2>
      <p className="text-gray-600">{workflow.description}</p>

      <div className="space-y-3 mt-6">
        {workflow.nodes.map((node, index) => (
          <div key={node.node_id} className="relative">
            <WorkflowNode node={node} />

            {/* Connector line to next node */}
            {index < workflow.nodes.length - 1 && (
              <div className="h-6 w-1 bg-gray-300 mx-auto" />
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 flex gap-3">
        <button className="btn-primary">Approve Plan</button>
        <button className="btn-secondary">Adjust Steps</button>
      </div>
    </div>
  );
}
```

---

## Milestone Progress Updates

### Update User at Key Nodes

```python
async def execute_workflow_with_updates(
    user_id: str,
    workflow: Workflow
) -> dict:
    """
    Execute workflow and send progress updates to user.

    Updates at:
    - Start of workflow
    - Completion of major nodes
    - Final completion
    """

    # Send initial update
    await send_message_to_user(
        user_id,
        f"Starting: {workflow.title}\n{workflow.description}"
    )

    results = {}

    for node in workflow.nodes:
        # Update node status
        node.status = NodeStatus.IN_PROGRESS
        workflow.current_node = node.node_id

        # Send progress update
        await send_progress_update(user_id, workflow, node)

        # Execute node
        try:
            result = await execute_node(node, results)
            node.result = result
            node.status = NodeStatus.COMPLETED
            results[node.node_id] = result

            # Send completion update for major nodes
            if is_major_node(node):
                await send_milestone_update(user_id, workflow, node, result)

        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            await send_error_update(user_id, workflow, node, str(e))
            raise

    # Send final completion
    await send_final_completion(user_id, workflow, results)

    return results

async def send_progress_update(
    user_id: str,
    workflow: Workflow,
    node: WorkflowNode
):
    """Send brief progress update."""

    message = f"→ {node.title}..."
    await send_message_to_user(user_id, message)

async def send_milestone_update(
    user_id: str,
    workflow: Workflow,
    node: WorkflowNode,
    result: dict
):
    """Send detailed update after major node completion."""

    message = f"✓ {node.title} complete!\n\n"

    # Add node-specific details
    if node.node_id == "identify_milestones":
        milestones = result.get("milestones", [])
        message += f"Identified {len(milestones)} milestones:\n"
        for i, milestone in enumerate(milestones, 1):
            message += f"{i}. {milestone['title']}\n"

    elif node.node_id == "generate_missions":
        missions = result.get("missions", [])
        message += f"Created {len(missions)} missions to guide your progress."

    await send_message_to_user(user_id, message)

def is_major_node(node: WorkflowNode) -> bool:
    """Determine if node is significant enough for milestone update."""

    major_nodes = [
        "identify_milestones",
        "generate_missions",
        "create_database"
    ]

    return node.node_id in major_nodes
```

### Real-Time Progress in UI

```tsx
// frontend/src/components/companion/WorkflowProgress.tsx

import { useEffect, useState } from 'react';

export function WorkflowProgress({ workflowId }: { workflowId: string }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);

  useEffect(() => {
    // Subscribe to workflow updates via SSE
    const eventSource = new EventSource(
      `/api/v1/sse/workflow/${workflowId}`
    );

    eventSource.onmessage = (event) => {
      const update = JSON.parse(event.data);

      if (update.type === 'workflow_update') {
        setWorkflow(update.workflow);
      }
    };

    return () => eventSource.close();
  }, [workflowId]);

  if (!workflow) return <div>Loading workflow...</div>;

  const progress = calculateProgress(workflow);

  return (
    <div className="workflow-progress">
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Current node */}
      <div className="mt-4">
        <p className="text-sm text-gray-600">Current step:</p>
        <p className="font-semibold">
          {workflow.nodes.find(n => n.node_id === workflow.current_node)?.title}
        </p>
      </div>

      {/* Node list */}
      <div className="mt-6 space-y-2">
        {workflow.nodes.map(node => (
          <div key={node.node_id} className="flex items-center gap-2">
            <NodeStatusIcon status={node.status} />
            <span className={
              node.status === 'completed' ? 'line-through text-gray-500' : ''
            }>
              {node.title}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function calculateProgress(workflow: Workflow): number {
  const completed = workflow.nodes.filter(
    n => n.status === 'completed'
  ).length;

  return (completed / workflow.nodes.length) * 100;
}
```

---

## Dynamic Plan Adjustment

### User Requests Plan Change

```python
async def handle_plan_modification(
    user_id: str,
    workflow: Workflow,
    user_request: str
) -> Workflow:
    """
    Modify workflow based on user feedback.

    Example user requests:
    - "Can you make the timeline longer?"
    - "Skip the advanced missions, keep it simple"
    - "Add more recovery days between runs"
    """

    # Use LLM to understand modification request
    modification_prompt = f"""
    The user wants to modify this workflow:
    {format_workflow_for_llm(workflow)}

    User's request: "{user_request}"

    What changes should we make?
    Output format:
    - Node to modify: [node_id]
    - Change type: [add/remove/modify/reorder]
    - Details: [what to change]
    """

    modification_plan = await call_llm(modification_prompt, model="gpt-4o-mini")
    changes = parse_modification_plan(modification_plan)

    # Apply changes
    for change in changes:
        if change["type"] == "modify":
            node = find_node(workflow, change["node_id"])
            node.description = change["new_description"]

        elif change["type"] == "add":
            new_node = WorkflowNode(
                node_id=change["node_id"],
                title=change["title"],
                description=change["description"],
                status=NodeStatus.PENDING,
                depends_on=change["depends_on"]
            )
            insert_node(workflow, new_node, change["insert_after"])

        elif change["type"] == "remove":
            remove_node(workflow, change["node_id"])

    # Show updated plan to user
    updated_plan = await show_workflow_plan(user_id, workflow)
    await send_message_to_user(
        user_id,
        f"Updated plan:\n\n{updated_plan}\n\nLooks good?"
    )

    return workflow
```

### Mid-Execution Pause and Resume

```python
async def pause_workflow(user_id: str, workflow: Workflow) -> Workflow:
    """Pause workflow execution, allowing user to review or modify."""

    # Mark current node as paused
    current_node = find_node(workflow, workflow.current_node)
    current_node.status = NodeStatus.PENDING  # Reset to pending

    # Save workflow state
    await save_workflow_state(workflow)

    await send_message_to_user(
        user_id,
        f"Workflow paused at: {current_node.title}\n\n"
        f"You can review the plan and make changes. Say 'resume' when ready."
    )

    return workflow

async def resume_workflow(user_id: str, workflow: Workflow) -> dict:
    """Resume paused workflow from last checkpoint."""

    await send_message_to_user(
        user_id,
        f"Resuming workflow: {workflow.title}"
    )

    # Find first non-completed node
    for node in workflow.nodes:
        if node.status != NodeStatus.COMPLETED:
            workflow.current_node = node.node_id
            break

    # Continue execution
    return await execute_workflow_with_updates(user_id, workflow)
```

---

## Implementation Examples

### Example 1: Mission Decomposition with User Collaboration

```python
async def collaborative_mission_decomposition(
    user_id: str,
    goal_id: str
) -> dict:
    """
    Decompose goal with user collaboration.

    Flow:
    1. Show plan to user
    2. Get approval or modifications
    3. Execute with progress updates
    4. Show final summary
    """

    # Step 1: Create workflow
    workflow = create_goal_decomposition_workflow(goal_id)

    # Step 2: Show plan
    plan_preview = await show_workflow_plan(user_id, workflow)
    await send_message_to_user(user_id, plan_preview)

    # Step 3: Wait for approval
    user_response = await wait_for_user_input(user_id, timeout=300)

    if "change" in user_response.lower() or "adjust" in user_response.lower():
        workflow = await handle_plan_modification(user_id, workflow, user_response)

    # Step 4: Execute with updates
    results = await execute_workflow_with_updates(user_id, workflow)

    # Step 5: Final summary
    summary = f"""
    ✓ Goal decomposition complete!

    **Results:**
    - {len(results['milestones'])} milestones identified
    - {len(results['missions'])} missions created
    - Estimated timeline: {results['timeline']} weeks

    Ready to start your first mission?
    """

    await send_message_to_user(user_id, summary)

    return results
```

### Example 2: Narrative Generation with Preview

```python
async def generate_narrative_with_preview(
    user_id: str,
    goal_id: str
) -> dict:
    """
    Generate narrative beat and show planning process.
    """

    # Create workflow
    workflow = Workflow(
        workflow_id=f"narrative_{goal_id}",
        title="Story Generation",
        description="Creating your personalized narrative beat",
        nodes=[
            WorkflowNode(
                node_id="assess_progress",
                title="Assess Progress",
                description="Analyzing your recent achievements",
                status=NodeStatus.PENDING,
                depends_on=[]
            ),
            WorkflowNode(
                node_id="select_beat",
                title="Select Story Beat",
                description="Choosing narrative moment that fits your journey",
                status=NodeStatus.PENDING,
                depends_on=["assess_progress"]
            ),
            WorkflowNode(
                node_id="generate_content",
                title="Generate Story",
                description="Crafting personalized narrative text",
                status=NodeStatus.PENDING,
                depends_on=["select_beat"]
            ),
            WorkflowNode(
                node_id="check_unlocks",
                title="Check Quest Unlocks",
                description="Seeing if you've unlocked any hidden quests",
                status=NodeStatus.PENDING,
                depends_on=["assess_progress"]
            )
        ]
    )

    # Show plan
    await send_message_to_user(
        user_id,
        f"Generating your story beat! Here's what I'll do:\n\n"
        f"{await show_workflow_plan(user_id, workflow)}"
    )

    # Execute
    results = await execute_workflow_with_updates(user_id, workflow)

    # Show story
    story_text = results["generate_content"]["story"]
    await send_message_to_user(user_id, f"\n\n**Your Story:**\n\n{story_text}")

    # Show unlocks if any
    if results["check_unlocks"]["unlocked_quests"]:
        await send_message_to_user(
            user_id,
            f"\n🎉 You've unlocked a hidden quest: "
            f"{results['check_unlocks']['unlocked_quests'][0]['title']}!"
        )

    return results
```

---

## Summary

Node-based workflow planning provides:

✅ **Transparency**: Users see AI's plan before execution
✅ **Collaboration**: Users can modify plans to fit their needs
✅ **Progress visibility**: Real-time updates at milestones
✅ **Trust building**: Understanding process increases confidence
✅ **Educational**: Users learn how AI approaches problems
✅ **Control**: Pause, resume, or adjust workflows mid-execution

**Key Implementation Patterns**:
1. Represent workflows as graphs of nodes
2. Show plan preview before execution
3. Send progress updates at milestones
4. Allow user modifications and feedback
5. Save workflow state for pause/resume

**Benefits for Delight**:
- Users feel in control of AI assistance
- Transparency builds trust in recommendations
- Collaborative planning improves outcomes
- Educational aspect helps users learn
- Reduces anxiety about AI "taking over"

**Next**: Read `07-IMPLEMENTATION-GUIDE.md` for complete code integration examples.

---

**Last Updated**: 2025-11-18
**Status**: Design Specification
**Maintainer**: Jack & Delight Team
