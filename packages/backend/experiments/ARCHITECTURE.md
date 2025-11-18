# Experimental AI Agent System - Architecture

**Based on**: "Hierarchical Memory and Adaptive State Management for an AI Agent" (Jack Luo, Nov 2025)

## Overview

This experimental system implements a complete AI agent platform with:
- **3-tier hierarchical memory** (Personal/Project/Task)
- **Graph-based knowledge retrieval** with semantic search
- **Node-based workflow planning** with visual execution tracking
- **Goal-driven state management** with tool orchestration
- **Standalone web interface** for memory browsing and agent visualization

**Purpose**: Experimentation playground separate from production app. Proven patterns can be extracted to the main Delight application.

---

## Core Principles

### 1. Memory Partitions (3-Tier Hierarchy)

```
Personal Memory (Global Context)
├── User profile and preferences
├── Core system directives
├── Long-term facts about the user
└── Persistent across all sessions

Project Memory (Domain Context)
├── Project-specific documents
├── Domain terminology and context
├── Project goals and constraints
└── Persists throughout project lifecycle

Task Memory (Working Memory)
├── Current conversation context
├── Recent user queries
├── Intermediate reasoning steps
└── Cleared after task completion
```

**Implementation**:
- PostgreSQL `memory_collections` table with `memory_type` enum
- Personal: `user_id` scoped, no expiration
- Project: `user_id` + `project_id` scoped, optional expiration
- Task: `user_id` + `session_id` scoped, short TTL

### 2. Graph-Based Hierarchical Retrieval

**Problem**: Flat vector search is slow and returns irrelevant results.

**Solution**: Organize memories in a graph structure:
```
User Knowledge Graph
├── Personal
│   ├── Profile
│   │   ├── Name: "Jack"
│   │   ├── Role: "Developer"
│   │   └── Preferences: {...}
│   └── Relationships
│       └── Team: [...]
├── Projects
│   ├── Project: "Delight"
│   │   ├── Context: "AI companion app"
│   │   ├── Tech Stack: {...}
│   │   └── Goals: [...]
│   └── Project: "Experiment"
│       └── Context: "Agent research"
└── Current Task
    ├── Goal: "Build memory system"
    ├── Steps: [...]
    └── Working Context: {...}
```

**Retrieval Strategy**:
1. **Route to category** (Personal/Project/Task) based on query type
2. **Graph traversal** to find relevant nodes
3. **Vector search** within narrowed scope
4. **Hybrid ranking** (graph distance + semantic similarity)

**Benefits**:
- 10-100x faster retrieval (smaller search space)
- Better precision (contextual disambiguation)
- Relationship awareness (connected knowledge)

### 3. Goal-Driven State Transitions

**State Machine Design**:
```python
State = {
    "goal": "Answer user question about X",
    "constraints": ["Use only 2024 data", "Cite sources"],
    "current_step": "gather_information",
    "completed_steps": ["understand_query", "plan_approach"],
    "pending_steps": ["analyze_data", "synthesize_answer"],
    "tool_outputs": {
        "search_results": [...],
        "database_query": [...]
    },
    "working_memory": {...}
}
```

**Transition Logic**:
```
User Query → Understand Intent → Plan Workflow
              ↓
         Execute Steps (with tools)
              ↓
    ┌─────────┴─────────┐
Parallel Tasks     Sequential Tasks
    └─────────┬─────────┘
              ↓
      Synthesize Results → Verify Quality
              ↓
         Present Answer → Update Memory
```

**Tool Awareness**:
- Each tool has defined inputs/outputs
- State tracks tool prerequisites and results
- Avoid redundant tool calls (check state first)
- Share context across tools via state

### 4. Node-Based Workflow Planning

**Workflow Graph**:
```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       ↓
┌──────────────────┐
│ Understand Query │ ← Initial node
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Plan Approach   │ ← Planning node
└──────┬───────────┘
       ↓
  ┌────┴────┐
  ↓         ↓
┌───────┐ ┌───────┐
│ Tool1 │ │ Tool2 │ ← Parallel execution
└───┬───┘ └───┬───┘
    └─────┬─────┘
          ↓
    ┌──────────┐
    │ Synthesize│ ← Convergence node
    └─────┬────┘
          ↓
    ┌──────────┐
    │  Verify  │ ← Validation node
    └─────┬────┘
          ↓
    ┌──────────┐
    │  Answer  │ ← Final output
    └──────────┘
```

**Node Types**:
- **Action**: Execute tool or LLM call
- **Decision**: Conditional branching
- **Parallel**: Fan-out to multiple paths
- **Converge**: Wait for all parallel paths
- **Verify**: Quality check/validation

**Transparency**:
- Show workflow graph to user before execution
- Update user at milestone nodes
- Allow user to modify plan
- Visualize execution progress in real-time

### 5. Multi-Step Prompting (Parallelization + Serialization)

**Sequential Steps** (dependencies):
```python
# Example: Summarize then translate
summary = await llm_call("Summarize this document", doc)
translation = await llm_call("Translate to Spanish", summary)
```

**Parallel Steps** (independent):
```python
# Example: Multi-facet research
results = await asyncio.gather(
    search_tool("economy trends 2024"),
    search_tool("health trends 2024"),
    search_tool("education trends 2024")
)
synthesis = await llm_call("Synthesize these findings", results)
```

**Hybrid Workflow**:
```python
# Plan → Parallel Execution → Sequential Refinement
plan = await planner.create_plan(query)

# Parallel data gathering
data = await execute_parallel(plan.data_tasks)

# Sequential analysis
for analysis_step in plan.analysis_steps:
    result = await execute_step(analysis_step, data)
    data.update(result)

# Final synthesis
answer = await synthesize(data)
```

**Configuration**:
- `max_parallel_tasks`: Control breadth of exploration
- `max_sequential_depth`: Control depth of reasoning
- Trade-off speed vs thoroughness

---

## Implementation Details

### Memory System (`experiments/memory/`)

#### `embedding_service.py`
```python
class EmbeddingService:
    """Generate and manage OpenAI embeddings."""

    async def embed_text(self, text: str) -> List[float]:
        """Generate 1536-dim embedding using text-embedding-3-small."""

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding generation for efficiency."""

    async def embed_and_store(self, memory_id: UUID, text: str):
        """Embed text and update memory record in database."""
```

#### `memory_service.py`
```python
class MemoryService:
    """3-tier memory CRUD and retrieval."""

    async def create_personal_memory(
        self, user_id: UUID, content: str, metadata: dict
    ) -> Memory:
        """Create long-term personal memory."""

    async def create_project_memory(
        self, user_id: UUID, project_id: UUID, content: str, metadata: dict
    ) -> Memory:
        """Create project-scoped memory."""

    async def create_task_memory(
        self, user_id: UUID, session_id: UUID, content: str, metadata: dict
    ) -> Memory:
        """Create ephemeral task memory."""

    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        memory_types: List[MemoryType],
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Memory]:
        """Hybrid search: vector similarity + metadata filters."""

    async def get_related_memories(
        self, memory_id: UUID, limit: int = 5
    ) -> List[Memory]:
        """Graph-based related memory retrieval."""
```

#### `graph_service.py`
```python
class MemoryGraph:
    """Graph-based memory relationships and navigation."""

    async def add_relationship(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: str,
        weight: float = 1.0
    ):
        """Create directed edge between memories."""

    async def find_path(
        self, source_id: UUID, target_id: UUID, max_depth: int = 3
    ) -> List[Memory]:
        """Find shortest path between memories."""

    async def get_subgraph(
        self, root_id: UUID, depth: int = 2
    ) -> Dict[UUID, List[UUID]]:
        """Get memory subgraph for visualization."""

    async def cluster_memories(
        self, user_id: UUID, memory_type: MemoryType
    ) -> Dict[str, List[Memory]]:
        """Cluster related memories using graph + embeddings."""
```

### Agent Core (`experiments/agent/`)

#### `state.py`
```python
@dataclass
class AgentState:
    """Goal-driven agent state with tool awareness."""

    user_id: UUID
    session_id: UUID
    goal: str
    constraints: List[str]

    # Workflow tracking
    current_node: str
    completed_nodes: List[str]
    pending_nodes: List[str]

    # Memory context
    personal_context: List[Memory]
    project_context: List[Memory]
    task_context: List[Memory]

    # Tool outputs
    tool_results: Dict[str, Any]

    # Working memory
    intermediate_results: Dict[str, Any]

    def can_proceed_to(self, node: str) -> bool:
        """Check if dependencies for node are satisfied."""

    def update_with_tool_result(self, tool_name: str, result: Any):
        """Add tool output to state."""
```

#### `planner.py`
```python
class WorkflowPlanner:
    """Create node-based execution plans."""

    async def plan_workflow(
        self, goal: str, constraints: List[str]
    ) -> WorkflowGraph:
        """Generate workflow graph using LLM reasoning."""

    async def optimize_plan(self, graph: WorkflowGraph) -> WorkflowGraph:
        """Identify parallel vs sequential nodes."""

    def visualize_plan(self, graph: WorkflowGraph) -> str:
        """Generate ASCII or Mermaid diagram for user approval."""

@dataclass
class WorkflowNode:
    """Single step in workflow."""

    id: str
    type: NodeType  # ACTION, DECISION, PARALLEL, CONVERGE
    description: str
    tool: Optional[str]
    dependencies: List[str]
    can_parallelize: bool
```

#### `executor.py`
```python
class GoalDrivenExecutor:
    """Execute workflow with adaptive state management."""

    async def execute_workflow(
        self,
        graph: WorkflowGraph,
        state: AgentState,
        on_milestone: Callable[[str], None]
    ) -> AgentState:
        """Execute nodes with parallelization and error handling."""

    async def execute_node(
        self, node: WorkflowNode, state: AgentState
    ) -> Any:
        """Execute single node (tool call or LLM reasoning)."""

    async def execute_parallel_nodes(
        self, nodes: List[WorkflowNode], state: AgentState
    ) -> Dict[str, Any]:
        """Execute multiple nodes concurrently."""
```

#### `graph.py` (LangGraph Integration)
```python
from langgraph.graph import StateGraph, END

class AgentGraph:
    """LangGraph-based agent with memory and tools."""

    def build_graph(self) -> StateGraph:
        """Construct state graph with nodes and edges."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("understand", self.understand_query)
        graph.add_node("plan", self.plan_approach)
        graph.add_node("gather_info", self.gather_information)
        graph.add_node("analyze", self.analyze_data)
        graph.add_node("synthesize", self.synthesize_answer)
        graph.add_node("verify", self.verify_quality)

        # Add edges (with conditions)
        graph.add_edge("understand", "plan")
        graph.add_conditional_edges(
            "plan",
            self.should_gather_info,
            {
                True: "gather_info",
                False: "synthesize"
            }
        )
        # ... more edges

        graph.set_entry_point("understand")
        return graph.compile()
```

### Visualization (`experiments/web/` and `experiments/memory_util/`)

#### Terminal Visualizer (`memory_util/visualizer.py`)
```python
from rich.console import Console
from rich.tree import Tree
from rich.table import Table

class MemoryVisualizer:
    """Rich terminal visualization for memories."""

    def visualize_memory_tree(self, user_id: UUID):
        """Show hierarchical memory tree."""
        tree = Tree("🧠 Memory Structure")

        personal = tree.add("👤 Personal")
        # Add personal memories

        projects = tree.add("📁 Projects")
        # Add project memories

        tasks = tree.add("📝 Tasks")
        # Add task memories

        console.print(tree)

    def visualize_similarity_results(
        self, query: str, results: List[Tuple[Memory, float]]
    ):
        """Show similarity search results with scores."""
        table = Table(title=f"Search: {query}")
        table.add_column("Score", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Content", style="white")

        for memory, score in results:
            table.add_row(
                f"{score:.3f}",
                memory.memory_type.value,
                memory.content[:100]
            )

        console.print(table)

    def visualize_graph(self, graph_data: Dict[UUID, List[UUID]]):
        """Show memory relationship graph."""
        # ASCII graph visualization
```

#### Web Dashboard (`web/server.py`)
```python
from fastapi import FastAPI, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Experimental Agent Dashboard")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def dashboard():
    """Main dashboard."""
    return templates.TemplateResponse("dashboard.html", {...})

@app.get("/memories")
async def memory_browser():
    """Interactive memory browser."""
    return templates.TemplateResponse("memories.html", {...})

@app.get("/api/memories/{user_id}")
async def get_memories(user_id: UUID):
    """API: Get user memories."""
    # Return memories as JSON

@app.websocket("/ws/agent/{session_id}")
async def agent_execution_stream(websocket: WebSocket, session_id: UUID):
    """WebSocket: Stream agent execution in real-time."""
    await websocket.accept()

    # Send workflow graph
    await websocket.send_json({
        "type": "workflow",
        "data": workflow_graph
    })

    # Stream node execution updates
    async for update in agent.execute_stream():
        await websocket.send_json({
            "type": "node_update",
            "node_id": update.node_id,
            "status": update.status,
            "result": update.result
        })
```

#### Web UI Features
1. **Memory Browser**:
   - Hierarchical tree view (Personal/Project/Task)
   - Search with filters
   - Edit/delete memories
   - Visualize embeddings (t-SNE/UMAP projection)
   - Graph visualization (force-directed layout)

2. **Agent Workflow Visualizer**:
   - Interactive workflow graph (D3.js/Cytoscape.js)
   - Real-time node execution highlighting
   - Step-through debugging
   - State inspection at each node
   - Tool call details

3. **Live Chat Interface**:
   - Talk to Eliza agent
   - See memory retrieval in sidebar
   - Watch workflow execution
   - Approve/modify plans before execution

---

## File Structure

```
experiments/
├── __init__.py
├── README.md                      # Usage guide
├── ARCHITECTURE.md                # This file
├── config.py                      # Shared configuration
├── requirements.txt               # Additional dependencies
│
├── database/
│   ├── __init__.py
│   ├── connection.py              # Safe DB connection wrapper
│   ├── inspector.py               # Schema inspection tools
│   └── test_data.py               # Test data generators
│
├── memory/
│   ├── __init__.py
│   ├── embedding_service.py       # OpenAI embedding generation
│   ├── memory_service.py          # 3-tier CRUD + vector search
│   ├── graph_service.py           # Graph relationships
│   ├── similarity_search.py       # Semantic search utilities
│   └── types.py                   # Type definitions
│
├── memory_util/
│   ├── __init__.py
│   ├── visualizer.py              # Rich terminal visualization
│   ├── organizer.py               # Memory categorization
│   ├── analyzer.py                # Statistics and insights
│   └── exporter.py                # Export/import (JSON/CSV)
│
├── agent/
│   ├── __init__.py
│   ├── state.py                   # AgentState definition
│   ├── planner.py                 # Workflow planning
│   ├── executor.py                # Goal-driven execution
│   ├── tools.py                   # Tool registry
│   ├── eliza.py                   # Eliza character
│   └── graph.py                   # LangGraph definitions
│
├── web/
│   ├── __init__.py
│   ├── server.py                  # FastAPI server
│   ├── templates/
│   │   ├── dashboard.html
│   │   ├── memories.html
│   │   └── agent.html
│   └── static/
│       ├── css/
│       ├── js/
│       │   ├── memory-graph.js    # D3.js memory visualization
│       │   └── workflow-viz.js    # Cytoscape.js workflow viz
│       └── images/
│
└── cli/
    ├── __init__.py
    ├── repl.py                    # Interactive agent REPL
    ├── memory_cli.py              # Memory management CLI
    └── workflow_debugger.py       # Step-through debugger
```

---

## Usage Examples

### 1. Memory Management

```bash
# Terminal visualization
poetry run python experiments/memory_util/visualizer.py --user-id <uuid>

# Create memories
poetry run python experiments/cli/memory_cli.py create \
  --type personal \
  --content "My name is Jack and I'm a developer" \
  --metadata '{"category": "profile"}'

# Search memories
poetry run python experiments/cli/memory_cli.py search \
  --query "what is my name?" \
  --types personal,project \
  --limit 5

# Generate embeddings for existing memories
poetry run python experiments/memory/embedding_service.py \
  --user-id <uuid> \
  --generate-all
```

### 2. Agent Interaction

```bash
# Interactive REPL
poetry run python experiments/cli/repl.py --user-id <uuid>

# Example conversation:
> You: What projects am I working on?
> Eliza: [Retrieves project memories...]
>        Based on your memories, you're working on:
>        1. Delight - AI companion app
>        2. Experiment - Agent research
>
>        [Workflow visualization shown]
```

### 3. Web Interface

```bash
# Start web server
poetry run python experiments/web/server.py

# Open browser to http://localhost:5000
# - Browse memories
# - Visualize graphs
# - Chat with Eliza
# - Watch agent execution
```

### 4. Workflow Debugging

```bash
# Step-through debugger
poetry run python experiments/cli/workflow_debugger.py \
  --goal "Research AI memory systems" \
  --step-by-step

# Shows:
# [Node 1] Understanding query...
# State: {...}
# Press Enter to continue...
#
# [Node 2] Planning approach...
# Proposed plan:
#   1. Search academic papers
#   2. Search industry implementations
#   3. Synthesize findings
# Approve plan? [Y/n]:
```

---

## Safety Features

1. **Database Safety**:
   - Read-only mode flag
   - Confirmation prompts for writes
   - Test user isolation
   - Automatic backups before bulk operations

2. **Cost Control**:
   - OpenAI API usage tracking
   - Configurable limits
   - Batch embedding for efficiency
   - Caching of embeddings

3. **Data Integrity**:
   - Validation before writes
   - Transaction rollback on errors
   - Memory version tracking
   - Audit logs

---

## Dependencies

Add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
# Existing dependencies...

# Visualization
rich = "^13.7.0"
networkx = "^3.2"
matplotlib = "^3.8.0"

# Web interface
jinja2 = "^3.1.2"
websockets = "^12.0"

# Graph visualization (for web)
# Install via npm in experiments/web/static:
# - d3.js
# - cytoscape.js
```

---

## Future Enhancements

1. **Advanced Retrieval**:
   - Hybrid search (BM25 + vector)
   - Re-ranking models
   - Query expansion
   - Contextual compression

2. **Agent Improvements**:
   - Multi-agent collaboration
   - Tool learning (agent discovers new tools)
   - Self-reflection and correction
   - Long-term goal tracking

3. **Visualization**:
   - 3D memory graph
   - Timeline view
   - Heat maps of memory usage
   - Export to graph formats (GraphML, GEXF)

4. **Integration**:
   - Export proven patterns to main app
   - Shared memory service
   - Production-ready API
   - Performance benchmarking

---

## Next Steps

1. ✅ Create directory structure
2. ✅ Implement database connection layer
3. ✅ Build embedding service
4. ✅ Implement 3-tier memory service
5. ✅ Create graph-based retrieval
6. ✅ Build terminal visualizer
7. ✅ Implement agent state management
8. ✅ Create workflow planner
9. ✅ Build goal-driven executor
10. ✅ Implement Eliza character
11. ✅ Create web interface
12. ✅ Build CLI tools
13. ✅ Add documentation

**Let's start building!** 🚀
