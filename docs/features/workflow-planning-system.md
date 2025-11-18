# Node-Based Workflow Planning and Transparency System

**Version:** 1.0.0
**Date:** 2025-11-18
**Status:** Implemented

## Overview

The Node-Based Workflow Planning and Transparency System is a sophisticated feature that enables Delight to represent complex multi-step processes as structured graphs of nodes (steps) and edges (dependencies). This system provides both internal clarity for AI agents and complete transparency for users, allowing them to see, understand, and approve workflows before execution.

## Key Features

### 1. **Node-Based Planning**
- Workflows are represented as directed graphs with nodes and edges
- Each node represents a unit of work (task, decision, input, verification, etc.)
- Edges define dependencies and execution flow between nodes
- Support for sequential, parallel, and conditional execution paths

### 2. **LLM-Generated Workflows**
- Automatically generate workflow plans from natural language user queries
- Uses GPT-4o-mini to analyze tasks and create structured workflows
- Provides human-readable summaries and estimated durations
- Intelligent breakdown of complex tasks into manageable steps

### 3. **User Transparency**
- Present generated plans to users for approval
- Allow users to modify workflows before execution
- Real-time progress updates via Server-Sent Events (SSE)
- Milestone notifications at key checkpoints

### 4. **Parallel and Conditional Execution**
- Nodes can be marked to run in parallel for efficiency
- Conditional branches based on previous step results
- Decision nodes for if/else logic
- Dynamic workflow adjustment based on runtime conditions

### 5. **Error Handling and Retries**
- Automatic retry logic for failed nodes
- Configurable retry attempts per node
- Error message capture and reporting
- Graceful failure handling

## Architecture

### Database Schema

The system uses four main tables:

#### **workflows**
Main workflow container storing the overall plan.

```sql
- id (UUID, PK)
- user_id (UUID, FK -> users.id)
- name (String)
- description (Text)
- status (Enum: draft, pending_approval, approved, executing, paused, completed, failed, cancelled)
- llm_generated (Boolean)
- metadata (JSONB)
- created_at, updated_at
```

#### **workflow_nodes**
Individual steps in the workflow.

```sql
- id (UUID, PK)
- workflow_id (UUID, FK -> workflows.id)
- name (String)
- description (Text)
- node_type (Enum: task, decision, parallel_group, conditional, input, output, verification)
- status (Enum: pending, ready, in_progress, completed, failed, skipped, blocked)
- tool_name (String, nullable) - which tool/function to execute
- input_schema (JSONB) - expected inputs
- output_data (JSONB) - execution results
- can_run_parallel (Boolean)
- position (JSONB) - {x, y} for UI visualization
- retry_count, max_retries (Integer)
- error_message (Text)
- started_at, completed_at, created_at, updated_at
```

#### **workflow_edges**
Connections defining execution flow.

```sql
- id (UUID, PK)
- workflow_id (UUID, FK -> workflows.id)
- source_node_id (UUID, FK -> workflow_nodes.id)
- target_node_id (UUID, FK -> workflow_nodes.id)
- edge_type (Enum: sequential, parallel, conditional)
- condition (JSONB) - conditional logic
- created_at
```

#### **workflow_executions**
Tracks execution state and history.

```sql
- id (UUID, PK)
- workflow_id (UUID, FK -> workflows.id)
- status (Enum: running, paused, completed, failed)
- current_node_id (UUID, FK -> workflow_nodes.id)
- execution_context (JSONB) - shared data between nodes
- started_at, completed_at, created_at, updated_at
```

### Backend Components

#### **Models** (`app/models/workflow.py`)
- SQLAlchemy 2.0 async models
- Enum types for status tracking
- Relationships between workflows, nodes, edges, and executions

#### **Services**

**WorkflowService** (`app/services/workflow_service.py`)
- CRUD operations for workflows, nodes, edges
- Workflow structure validation
- Ready node detection (dependency resolution)
- Execution state management

**WorkflowExecutor** (`app/services/workflow_executor.py`)
- Core execution engine
- Parallel node execution with asyncio
- Conditional branching logic
- Tool registry for node execution
- Real-time progress callbacks for SSE
- Error handling and retry logic

**WorkflowPlanner** (`app/services/workflow_planner.py`)
- LLM-powered plan generation
- Natural language to workflow conversion
- Plan refinement based on user feedback
- Context-aware planning

#### **API Endpoints** (`app/api/v1/workflows.py`)

**Workflow CRUD**
- `POST /workflows` - Create workflow
- `GET /workflows` - List user workflows (with pagination/filtering)
- `GET /workflows/{id}` - Get workflow details
- `PATCH /workflows/{id}` - Update workflow
- `DELETE /workflows/{id}` - Delete workflow

**Node Management**
- `POST /workflows/{id}/nodes` - Add node
- `PATCH /workflows/nodes/{id}` - Update node

**Edge Management**
- `POST /workflows/{id}/edges` - Add edge
- `DELETE /workflows/edges/{id}` - Delete edge

**LLM Generation**
- `POST /workflows/generate` - Generate workflow from natural language
- `PATCH /workflows/{id}/approve` - Approve workflow

**Execution**
- `POST /workflows/{id}/execute` - Start execution
- `GET /workflows/executions/{id}` - Get execution details
- `GET /workflows/{id}/executions` - List workflow executions

**SSE Progress Updates** (`app/api/v1/workflow_sse.py`)
- `GET /workflows/sse/executions/{id}/progress` - Stream execution progress
- `GET /workflows/sse/workflows/{id}/live` - Stream latest execution

### Frontend Components

#### **Types** (`src/lib/types/workflow.ts`)
- TypeScript interfaces matching backend schemas
- Enums for all status types
- Type-safe workflow, node, edge, and execution types

#### **API Client** (`src/lib/api/workflows.ts`)
- Async functions for all workflow operations
- Error handling with custom WorkflowAPIError
- SSE subscription management
- Authentication integration (Clerk)

#### **React Hooks** (`src/hooks/useWorkflow.ts`)

**useWorkflow(workflowId)**
- Fetch and manage single workflow
- Update, delete, approve, execute operations
- Auto-refresh on changes

**useWorkflowList(page, pageSize)**
- Paginated workflow listing
- Status filtering
- Real-time refresh

**useWorkflowGenerator()**
- Generate plans from natural language
- Loading states and error handling

**useWorkflowExecution()**
- Monitor execution progress
- SSE subscription management
- Progress event history
- Completion detection

## Usage Examples

### Backend: Generate Workflow Plan

```python
from app.services.workflow_planner import WorkflowPlanner
from uuid import UUID

async def generate_plan(db: AsyncSession, user_id: UUID):
    planner = WorkflowPlanner(db)

    workflow, summary = await planner.generate_workflow_plan(
        user_id=user_id,
        user_query="Analyze quarterly sales data and generate a report with insights",
        context={"quarter": "Q4 2024"}
    )

    print(f"Generated workflow: {workflow.name}")
    print(f"Summary: {summary}")
    print(f"Nodes: {len(workflow.nodes)}")
```

### Backend: Execute Workflow

```python
from app.services.workflow_executor import WorkflowExecutor
from app.services.workflow_service import WorkflowService

async def execute_workflow_example(db: AsyncSession, workflow_id: UUID):
    service = WorkflowService(db)

    # Create execution
    execution = await service.create_execution(workflow_id)

    # Set up executor with progress callback
    def progress_callback(event):
        print(f"Progress: {event['event_type']} - {event.get('data', {})}")

    executor = WorkflowExecutor(db, progress_callback=progress_callback)

    # Register tools
    executor.register_tool("fetch_data", fetch_data_function)
    executor.register_tool("analyze", analyze_function)

    # Execute
    result = await executor.execute_workflow(execution.id)
    print(f"Execution completed: {result.status}")
```

### Frontend: Generate and Display Workflow

```typescript
import { useWorkflowGenerator, useWorkflow } from '@/hooks/useWorkflow';

function WorkflowGeneratorComponent() {
  const { generating, generatePlan } = useWorkflowGenerator();
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const { workflow, approve, execute } = useWorkflow(workflowId);

  const handleGenerate = async () => {
    try {
      const response = await generatePlan(
        "Analyze Q4 sales and create a summary report"
      );

      setWorkflowId(response.workflow.id);
      console.log("Plan summary:", response.plan_summary);
      console.log("Estimated duration:", response.estimated_duration);
    } catch (error) {
      console.error("Failed to generate plan:", error);
    }
  };

  const handleApprove = async () => {
    await approve();
    console.log("Workflow approved!");
  };

  const handleExecute = async () => {
    const execution = await execute();
    console.log("Execution started:", execution.id);
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={generating}>
        {generating ? "Generating..." : "Generate Plan"}
      </button>

      {workflow && (
        <>
          <h2>{workflow.name}</h2>
          <p>{workflow.description}</p>

          <h3>Steps:</h3>
          <ul>
            {workflow.nodes.map(node => (
              <li key={node.id}>
                {node.name} - {node.status}
              </li>
            ))}
          </ul>

          {workflow.status === 'pending_approval' && (
            <button onClick={handleApprove}>Approve Plan</button>
          )}

          {workflow.status === 'approved' && (
            <button onClick={handleExecute}>Start Execution</button>
          )}
        </>
      )}
    </div>
  );
}
```

### Frontend: Monitor Execution Progress

```typescript
import { useWorkflowExecution } from '@/hooks/useWorkflow';
import { useEffect } from 'react';

function ExecutionMonitor({ executionId }: { executionId: string }) {
  const { execution, progress, isComplete, subscribe } = useWorkflowExecution();

  useEffect(() => {
    if (executionId) {
      subscribe(executionId);
    }
  }, [executionId, subscribe]);

  return (
    <div>
      <h2>Execution Progress</h2>

      {execution && (
        <div>
          <p>Status: {execution.status}</p>
          <p>Started: {new Date(execution.started_at).toLocaleString()}</p>
        </div>
      )}

      <h3>Progress Log:</h3>
      <ul>
        {progress.map((event, idx) => (
          <li key={idx}>
            [{event.timestamp}] {event.event_type}: {JSON.stringify(event.data)}
          </li>
        ))}
      </ul>

      {isComplete && <p>✅ Execution completed!</p>}
    </div>
  );
}
```

## API Examples

### Generate Workflow Plan

```bash
curl -X POST http://localhost:8000/api/v1/workflows/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Analyze quarterly sales and generate insights",
    "context": {"quarter": "Q4 2024"},
    "auto_approve": false
  }'
```

Response:
```json
{
  "workflow": {
    "id": "uuid",
    "name": "Quarterly Sales Analysis Workflow",
    "description": "Analyze sales data and generate insights",
    "status": "pending_approval",
    "nodes": [
      {
        "id": "uuid",
        "name": "Collect Sales Data",
        "node_type": "task",
        "status": "pending",
        "can_run_parallel": false
      },
      {
        "id": "uuid",
        "name": "Analyze Trends",
        "node_type": "task",
        "status": "pending",
        "can_run_parallel": false
      }
    ],
    "edges": [...]
  },
  "plan_summary": "This workflow will collect Q4 sales data, analyze trends, and generate insights.",
  "estimated_duration": "5-10 minutes",
  "requires_approval": true
}
```

### Stream Execution Progress (SSE)

```bash
curl -N http://localhost:8000/api/v1/workflows/sse/executions/{execution_id}/progress \
  -H "Authorization: Bearer $TOKEN"
```

Events received:
```
event: node_started
data: {"execution_id": "...", "node_name": "Collect Sales Data", "timestamp": "..."}

event: node_completed
data: {"execution_id": "...", "node_name": "Collect Sales Data", "output": {...}}

event: workflow_completed
data: {"execution_id": "...", "total_nodes": 5, "timestamp": "..."}
```

## Benefits

### For AI Agents
1. **Structured Reasoning**: Break complex tasks into manageable steps
2. **Dependency Management**: Clear understanding of task dependencies
3. **State Tracking**: Know exactly what's been done and what's pending
4. **Error Recovery**: Retry failed steps without starting over
5. **Parallel Optimization**: Execute independent tasks simultaneously

### For Users
1. **Transparency**: See exactly what the AI plans to do
2. **Control**: Approve or modify workflows before execution
3. **Visibility**: Real-time progress updates on task execution
4. **Trust**: Build confidence through clear communication
5. **Learning**: Understand how complex tasks are accomplished

### For the System
1. **Maintainability**: Clear structure for debugging and optimization
2. **Extensibility**: Easy to add new node types and tools
3. **Scalability**: Parallel execution and async operations
4. **Observability**: Complete execution history and logging
5. **Flexibility**: Dynamic workflow adjustment based on conditions

## Future Enhancements

1. **Visual Workflow Editor**: Drag-and-drop workflow builder UI
2. **Workflow Templates**: Pre-built workflows for common tasks
3. **Sub-workflows**: Nest workflows within workflows
4. **Human-in-the-Loop Nodes**: Pause for user input mid-execution
5. **Workflow Versioning**: Track and rollback workflow changes
6. **Performance Analytics**: Optimize workflows based on execution metrics
7. **Collaborative Workflows**: Share and collaborate on workflows
8. **Workflow Marketplace**: Share and discover community workflows

## Testing

### Backend Tests

```bash
cd packages/backend
poetry run pytest tests/test_workflow_service.py -v
poetry run pytest tests/test_workflow_executor.py -v
poetry run pytest tests/test_workflow_planner.py -v
```

### Frontend Tests

```bash
cd packages/frontend
npm run test:e2e -- tests/workflow.spec.ts
```

## Deployment

### Database Migration

```bash
cd packages/backend
poetry run alembic upgrade head
```

This will create all workflow tables and indexes.

### Environment Variables

No additional environment variables required - uses existing OpenAI API key for LLM plan generation.

## Troubleshooting

### Common Issues

**Issue**: Workflow nodes stuck in "pending" status
**Solution**: Check node dependencies - a node may be waiting for an upstream node to complete

**Issue**: SSE connection drops
**Solution**: Check network/proxy settings - SSE requires persistent connections

**Issue**: LLM-generated plans are incomplete
**Solution**: Provide more context in the plan request, or manually edit the generated workflow

## References

- Backend Models: `packages/backend/app/models/workflow.py`
- Backend Services: `packages/backend/app/services/workflow_*.py`
- Backend API: `packages/backend/app/api/v1/workflows.py`
- Database Migration: `packages/backend/app/db/migrations/versions/005_create_workflow_tables.py`
- Frontend Types: `packages/frontend/src/lib/types/workflow.ts`
- Frontend API: `packages/frontend/src/lib/api/workflows.ts`
- Frontend Hooks: `packages/frontend/src/hooks/useWorkflow.ts`

---

**Maintained by**: Delight Team
**Last Updated**: 2025-11-18
