# AI Orchestration System

## Overview

The AI orchestration system is the brain of Delight's assistant, coordinating goal-driven workflows through a state machine architecture. It enables the AI to break down complex user requests into manageable steps, execute them reliably, and maintain transparency throughout the process.

## Core Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    User Request                              │
│           "Help me organize my week and gamify it"          │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  Request Analyzer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Parse intent                                         │ │
│  │ • Identify complexity level                           │ │
│  │ • Determine required tools                            │ │
│  │ • Check auth/permissions                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  Goal Planner                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Break into sub-goals                                │ │
│  │ • Create workflow graph (nodes + edges)               │ │
│  │ • Identify parallelizable steps                       │ │
│  │ • Estimate time & resources                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                 Plan Approval (Optional)                     │
│  Display plan to user, allow modifications                   │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  Execution Engine                            │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ State Machine  │  │  Tool Manager  │  │ LLM Router   │  │
│  │ (LangGraph)    │  │  (Functions)   │  │ (Model Sel)  │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Execute nodes in order (sequential/parallel)          │ │
│  │ • Monitor progress                                     │ │
│  │ • Handle errors and retries                           │ │
│  │ • Update user on milestones                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  Result Synthesizer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Aggregate outputs from all nodes                    │ │
│  │ • Format final response                               │ │
│  │ • Extract facts for memory storage                    │ │
│  │ • Update game state (XP, achievements)                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    Response to User                          │
│         "✓ Week organized! You've earned 50 XP"             │
└──────────────────────────────────────────────────────────────┘
```

## State Machine Design

### LangGraph Integration

We use LangGraph for explicit state management and workflow control:

```typescript
import { StateGraph, END } from "@langchain/langgraph";

// Define the state shape
interface AgentState {
  // User context
  userId: string;
  sessionId: string;

  // Current request
  userRequest: string;
  intent: string;

  // Workflow tracking
  currentGoal: string;
  subGoals: string[];
  completedGoals: string[];

  // Execution data
  workflowNodes: WorkflowNode[];
  currentNodeId: string | null;
  nodeResults: Record<string, any>;

  // Tool outputs
  toolCalls: ToolCall[];

  // Memory and context
  relevantMemories: string[];

  // Final output
  response: string;

  // Error handling
  errors: Error[];
  retryCount: number;
}

// Create the graph
const workflow = new StateGraph<AgentState>({
  channels: {
    userId: null,
    sessionId: null,
    userRequest: null,
    intent: null,
    currentGoal: null,
    subGoals: [],
    completedGoals: [],
    workflowNodes: [],
    currentNodeId: null,
    nodeResults: {},
    toolCalls: [],
    relevantMemories: [],
    response: null,
    errors: [],
    retryCount: 0,
  },
});

// Add nodes (steps in the workflow)
workflow.addNode("analyze_request", analyzeRequestNode);
workflow.addNode("plan_workflow", planWorkflowNode);
workflow.addNode("load_memory", loadMemoryNode);
workflow.addNode("execute_node", executeNodeNode);
workflow.addNode("synthesize_result", synthesizeResultNode);

// Define edges (transitions)
workflow.addEdge("analyze_request", "plan_workflow");
workflow.addEdge("plan_workflow", "load_memory");
workflow.addEdge("load_memory", "execute_node");

// Conditional edge: loop if more nodes to execute
workflow.addConditionalEdges("execute_node", (state) => {
  // If there are more nodes, continue executing
  if (hasMoreNodesToExecute(state)) {
    return "execute_node";
  }
  // Otherwise, move to synthesis
  return "synthesize_result";
});

workflow.addEdge("synthesize_result", END);

// Set entry point
workflow.setEntryPoint("analyze_request");

// Compile the graph
const app = workflow.compile();
```

### Node Implementations

#### 1. Analyze Request Node

```typescript
async function analyzeRequestNode(
  state: AgentState
): Promise<Partial<AgentState>> {
  const prompt = `
Analyze this user request and extract:
1. Primary intent (what does the user want to accomplish?)
2. Complexity level (simple, moderate, complex)
3. Required tools (calendar, search, email, etc.)

User request: "${state.userRequest}"

Respond in JSON:
{
  "intent": "string",
  "complexity": "simple|moderate|complex",
  "requiredTools": ["tool1", "tool2"]
}
`;

  const analysis = await llm.complete(prompt);
  const parsed = JSON.parse(analysis);

  return {
    intent: parsed.intent,
    // Store complexity and tools in state for later use
  };
}
```

#### 2. Plan Workflow Node

```typescript
async function planWorkflowNode(
  state: AgentState
): Promise<Partial<AgentState>> {
  const prompt = `
Create a step-by-step workflow to accomplish this goal:

Goal: ${state.intent}
Available tools: ${getAvailableTools(state).join(", ")}

Create a workflow as a JSON array of nodes:
[
  {
    "id": "node_1",
    "action": "Gather all tasks due this week",
    "type": "sequential",
    "tool": "database_query",
    "depends_on": []
  },
  {
    "id": "node_2",
    "action": "Prioritize tasks by difficulty and deadline",
    "type": "sequential",
    "tool": "llm_analysis",
    "depends_on": ["node_1"]
  },
  ...
]

Workflow:
`;

  const workflowPlan = await llm.complete(prompt);
  const nodes: WorkflowNode[] = JSON.parse(workflowPlan);

  // Optionally show plan to user for approval
  if (state.requiresApproval) {
    await showPlanToUser(nodes);
  }

  return {
    workflowNodes: nodes,
    currentNodeId: nodes[0].id,
    subGoals: nodes.map((n) => n.action),
  };
}
```

#### 3. Execute Node Node

```typescript
async function executeNodeNode(
  state: AgentState
): Promise<Partial<AgentState>> {
  const currentNode = state.workflowNodes.find(
    (n) => n.id === state.currentNodeId
  );
  if (!currentNode) {
    throw new Error("Current node not found");
  }

  try {
    // Execute the node's action
    const result = await executeAction(currentNode, state);

    // Store result
    const updatedResults = {
      ...state.nodeResults,
      [currentNode.id]: result,
    };

    // Mark goal as completed
    const completedGoals = [...state.completedGoals, currentNode.action];

    // Notify user of progress
    await notifyProgress(state.userId, currentNode.action, "completed");

    // Move to next node
    const nextNode = getNextNode(state.workflowNodes, currentNode.id);

    return {
      nodeResults: updatedResults,
      completedGoals,
      currentNodeId: nextNode?.id || null,
      retryCount: 0, // Reset retry count on success
    };
  } catch (error) {
    // Handle error with retry logic
    if (state.retryCount < 3) {
      console.warn(`Node ${currentNode.id} failed, retrying...`, error);
      return {
        retryCount: state.retryCount + 1,
        errors: [...state.errors, error],
      };
    } else {
      // Max retries reached, fail gracefully
      await notifyProgress(state.userId, currentNode.action, "failed");
      throw error;
    }
  }
}
```

#### 4. Synthesize Result Node

```typescript
async function synthesizeResultNode(
  state: AgentState
): Promise<Partial<AgentState>> {
  // Combine all node results into a final response
  const allResults = Object.values(state.nodeResults);

  const prompt = `
Based on these intermediate results, create a final response for the user:

Original request: ${state.userRequest}
Results: ${JSON.stringify(allResults, null, 2)}

Provide a clear, actionable response that addresses the user's request.
`;

  const finalResponse = await llm.complete(prompt);

  // Extract facts for memory storage
  await extractAndStoreFacts(state.userId, finalResponse);

  // Update game state (award XP)
  await updateGameState(state.userId, {
    xpGained: calculateXP(state.workflowNodes.length),
    tasksCompleted: state.completedGoals.length,
  });

  return {
    response: finalResponse,
  };
}
```

---

## Tool Management

### Tool Registry

```typescript
interface Tool {
  name: string;
  description: string;
  parameters: Record<string, ParameterDefinition>;
  execute: (
    params: Record<string, any>,
    context: ExecutionContext
  ) => Promise<any>;
}

class ToolManager {
  private tools: Map<string, Tool> = new Map();

  registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }

  async executeTool(
    toolName: string,
    params: Record<string, any>,
    context: ExecutionContext
  ): Promise<any> {
    const tool = this.tools.get(toolName);
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }

    // Validate parameters
    this.validateParams(params, tool.parameters);

    // Execute with timeout and error handling
    return await this.executeWithTimeout(
      () => tool.execute(params, context),
      30000 // 30 second timeout
    );
  }

  private async executeWithTimeout<T>(
    fn: () => Promise<T>,
    timeout: number
  ): Promise<T> {
    return Promise.race([
      fn(),
      new Promise<T>((_, reject) =>
        setTimeout(() => reject(new Error("Tool execution timeout")), timeout)
      ),
    ]);
  }
}
```

### Built-in Tools

#### Web Search Tool

```typescript
const webSearchTool: Tool = {
  name: "web_search",
  description: "Search the web for information",
  parameters: {
    query: { type: "string", required: true },
    numResults: { type: "number", required: false, default: 5 },
  },
  execute: async (params, context) => {
    const { query, numResults = 5 } = params;

    // Use Brave Search API or similar
    const response = await fetch(
      `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(
        query
      )}&count=${numResults}`,
      {
        headers: {
          "X-Subscription-Token": process.env.BRAVE_API_KEY!,
        },
      }
    );

    const data = await response.json();

    return {
      results: data.web.results.map((r: any) => ({
        title: r.title,
        url: r.url,
        description: r.description,
      })),
    };
  },
};
```

#### Calendar Tool

```typescript
const calendarTool: Tool = {
  name: "calendar_query",
  description: "Query user's calendar for events",
  parameters: {
    startDate: { type: "string", required: true },
    endDate: { type: "string", required: true },
  },
  execute: async (params, context) => {
    const { startDate, endDate } = params;

    // Integrate with Google Calendar API
    const calendar = google.calendar({
      version: "v3",
      auth: context.oauth2Client,
    });

    const response = await calendar.events.list({
      calendarId: "primary",
      timeMin: new Date(startDate).toISOString(),
      timeMax: new Date(endDate).toISOString(),
      singleEvents: true,
      orderBy: "startTime",
    });

    return {
      events:
        response.data.items?.map((event) => ({
          id: event.id,
          title: event.summary,
          start: event.start?.dateTime || event.start?.date,
          end: event.end?.dateTime || event.end?.date,
          description: event.description,
        })) || [],
    };
  },
};
```

#### Task Database Tool

```typescript
const taskQueryTool: Tool = {
  name: "task_query",
  description: "Query user's tasks from database",
  parameters: {
    filters: { type: "object", required: false },
    limit: { type: "number", required: false, default: 20 },
  },
  execute: async (params, context) => {
    const { filters = {}, limit = 20 } = params;

    const query = db.select().from("tasks").where("user_id", context.userId);

    // Apply filters
    if (filters.status) {
      query.where("status", filters.status);
    }
    if (filters.dueAfter) {
      query.where("due_date", ">=", filters.dueAfter);
    }
    if (filters.dueBefore) {
      query.where("due_date", "<=", filters.dueBefore);
    }

    const tasks = await query.limit(limit);

    return { tasks };
  },
};
```

---

## LLM Router

### Model Selection Strategy

```typescript
interface ModelConfig {
  provider: "openai" | "anthropic" | "local";
  model: string;
  maxTokens: number;
  costPerToken: number;
  speed: "fast" | "medium" | "slow";
  quality: "high" | "medium" | "low";
}

class LLMRouter {
  private models: Record<string, ModelConfig> = {
    "gpt-4": {
      provider: "openai",
      model: "gpt-4-turbo-preview",
      maxTokens: 4096,
      costPerToken: 0.00003, // $0.03 per 1K tokens
      speed: "medium",
      quality: "high",
    },
    "gpt-3.5": {
      provider: "openai",
      model: "gpt-3.5-turbo",
      maxTokens: 4096,
      costPerToken: 0.000001, // $0.001 per 1K tokens
      speed: "fast",
      quality: "medium",
    },
    "llama-70b": {
      provider: "local",
      model: "llama-2-70b",
      maxTokens: 4096,
      costPerToken: 0, // Self-hosted
      speed: "medium",
      quality: "high",
    },
    "claude-2": {
      provider: "anthropic",
      model: "claude-2.1",
      maxTokens: 100000,
      costPerToken: 0.000008,
      speed: "medium",
      quality: "high",
    },
  };

  selectModel(config: {
    taskType: "chat" | "code" | "analysis" | "creative";
    complexity: "simple" | "moderate" | "complex";
    userTier: "free" | "pro" | "enterprise";
    requiresAccuracy: boolean;
  }): ModelConfig {
    const { taskType, complexity, userTier, requiresAccuracy } = config;

    // Free users: always use local model or cheapest option
    if (userTier === "free") {
      return this.models["llama-70b"] || this.models["gpt-3.5"];
    }

    // Complex tasks requiring accuracy: use best model
    if (complexity === "complex" && requiresAccuracy) {
      return this.models["gpt-4"];
    }

    // Code tasks: prefer specialized model (future)
    if (taskType === "code") {
      return this.models["gpt-4"]; // or code-llama when added
    }

    // Long context needed: use Claude
    if (taskType === "analysis" && complexity === "complex") {
      return this.models["claude-2"];
    }

    // Default: use local model
    return this.models["llama-70b"];
  }

  async complete(
    prompt: string,
    config: ModelConfig,
    options?: {
      temperature?: number;
      maxTokens?: number;
    }
  ): Promise<string> {
    switch (config.provider) {
      case "openai":
        return this.callOpenAI(prompt, config, options);
      case "anthropic":
        return this.callAnthropic(prompt, config, options);
      case "local":
        return this.callLocalModel(prompt, config, options);
    }
  }

  private async callOpenAI(
    prompt: string,
    config: ModelConfig,
    options?: any
  ): Promise<string> {
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

    const response = await openai.chat.completions.create({
      model: config.model,
      messages: [{ role: "user", content: prompt }],
      temperature: options?.temperature ?? 0.7,
      max_tokens: options?.maxTokens ?? config.maxTokens,
    });

    return response.choices[0].message.content || "";
  }
}
```

---

## Parallel Execution

### Concurrent Node Execution

```typescript
async function executeParallelNodes(
  nodes: WorkflowNode[],
  state: AgentState
): Promise<Record<string, any>> {
  // Group nodes that can run in parallel
  const parallelGroups = groupParallelNodes(nodes);

  const results: Record<string, any> = {};

  for (const group of parallelGroups) {
    // Execute all nodes in this group concurrently
    const groupResults = await Promise.allSettled(
      group.map(async (node) => {
        const result = await executeAction(node, state);
        return { nodeId: node.id, result };
      })
    );

    // Collect results
    for (const outcome of groupResults) {
      if (outcome.status === "fulfilled") {
        results[outcome.value.nodeId] = outcome.value.result;
      } else {
        // Handle failure
        console.error(`Node failed:`, outcome.reason);
      }
    }
  }

  return results;
}

function groupParallelNodes(nodes: WorkflowNode[]): WorkflowNode[][] {
  const groups: WorkflowNode[][] = [];
  const executed = new Set<string>();

  while (executed.size < nodes.length) {
    const parallelGroup = nodes.filter((node) => {
      // Can execute if all dependencies are met
      const depsmet = node.dependsOn.every((depId) => executed.has(depId));
      return depsmet && !executed.has(node.id);
    });

    if (parallelGroup.length === 0) break;

    groups.push(parallelGroup);
    parallelGroup.forEach((n) => executed.add(n.id));
  }

  return groups;
}
```

---

## Transparency & User Feedback

### Progress Notifications

```typescript
async function notifyProgress(
  userId: string,
  action: string,
  status: "started" | "in_progress" | "completed" | "failed"
): Promise<void> {
  // Send via WebSocket for real-time updates
  const message = {
    type: "workflow_progress",
    action,
    status,
    timestamp: Date.now(),
  };

  await websocketServer.sendToUser(userId, message);

  // Also store in database for history
  await db.insert("workflow_logs", {
    user_id: userId,
    action,
    status,
    timestamp: new Date(),
  });
}
```

### Plan Visualization

```typescript
interface WorkflowPlanDisplay {
  nodes: {
    id: string;
    label: string;
    status: "pending" | "in_progress" | "completed" | "failed";
    estimatedTime?: string;
  }[];
  edges: {
    from: string;
    to: string;
  }[];
}

function generatePlanVisualization(nodes: WorkflowNode[]): WorkflowPlanDisplay {
  return {
    nodes: nodes.map((n) => ({
      id: n.id,
      label: n.action,
      status: "pending",
      estimatedTime: estimateNodeTime(n),
    })),
    edges: nodes.flatMap((n) =>
      n.dependsOn.map((depId) => ({
        from: depId,
        to: n.id,
      }))
    ),
  };
}
```

---

## Error Handling & Resilience

### Retry Logic with Exponential Backoff

```typescript
async function executeWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) {
        throw error; // Final attempt failed
      }

      // Exponential backoff
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise((resolve) => setTimeout(resolve, delay));

      console.log(
        `Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`
      );
    }
  }

  throw new Error("Unreachable");
}
```

### Graceful Degradation

```typescript
async function executeWithFallback<T>(
  primaryFn: () => Promise<T>,
  fallbackFn: () => Promise<T>
): Promise<T> {
  try {
    return await primaryFn();
  } catch (error) {
    console.warn("Primary execution failed, using fallback", error);
    return await fallbackFn();
  }
}

// Example: Use GPT-4, fallback to local model
const result = await executeWithFallback(
  () => llmRouter.complete(prompt, models["gpt-4"]),
  () => llmRouter.complete(prompt, models["llama-70b"])
);
```

---

## Performance Optimization

### Caching Strategy

```typescript
class OrchestrationCache {
  private cache: Map<string, CachedResult> = new Map();

  async getCached<T>(key: string, ttl: number = 3600): Promise<T | null> {
    const cached = this.cache.get(key);
    if (!cached) return null;

    // Check if expired
    if (Date.now() - cached.timestamp > ttl * 1000) {
      this.cache.delete(key);
      return null;
    }

    return cached.value as T;
  }

  set(key: string, value: any): void {
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
    });
  }
}

// Cache workflow plans for similar requests
const cacheKey = `plan:${hashRequest(userRequest)}`;
let plan = await cache.getCached<WorkflowNode[]>(cacheKey);

if (!plan) {
  plan = await generateWorkflowPlan(userRequest);
  cache.set(cacheKey, plan);
}
```

---

## Next Steps

1. **Set up LangGraph**: Install and configure LangGraph
2. **Implement tool registry**: Build the tool management system
3. **Create workflow templates**: Define common workflows (research, planning, etc.)
4. **Build LLM router**: Implement model selection logic
5. **Add observability**: Logging and monitoring
6. **Test orchestration**: End-to-end testing of complex workflows

---

_Last Updated: November 7, 2025_
