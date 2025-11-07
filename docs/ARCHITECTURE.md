# Delight by Magk - System Architecture

## Overview

Delight is a gamified AI productivity assistant that transforms work into an engaging, game-like experience while intelligently managing tasks through advanced AI orchestration and multi-tier memory systems.

## Core Architecture Principles

1. **Multi-Tier Memory Management** - Personal, Project, and Task-level context separation
2. **Goal-Driven Orchestration** - State machine-based agent workflow with transparent node planning
3. **Modular & Extensible** - Pluggable LLMs, memory backends, and tool integrations
4. **Gamification First** - RPG elements deeply integrated into the productivity experience
5. **Privacy & Control** - User owns their data, can choose models, and customize behavior

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  (Electron + React/Vue - Multi-platform: Desktop, Web, Mobile)  │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐        │
│  │ Game UI     │  │ Task Manager │  │  AI Chat       │        │
│  │ (RPG Theme) │  │ (Quest Board)│  │  Interface     │        │
│  └─────────────┘  └──────────────┘  └────────────────┘        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ WebSocket + REST API
┌───────────────────────────┴─────────────────────────────────────┐
│                      Backend Services Layer                      │
│                     (Node.js/TypeScript)                        │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  API Gateway     │  │  Auth Service    │  │  Game Engine │ │
│  │  (Express/Fastify)│  │  (JWT/OAuth)     │  │  (XP/Levels) │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            AI Orchestration Layer                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │  │
│  │  │ State      │  │ Goal       │  │  Tool Manager  │    │  │
│  │  │ Machine    │  │ Planner    │  │  (Search, etc) │    │  │
│  │  └────────────┘  └────────────┘  └────────────────┘    │  │
│  │                                                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │  │
│  │  │ LLM Router │  │ Prompt     │  │  Execution     │    │  │
│  │  │ (Model Sel)│  │ Manager    │  │  Engine        │    │  │
│  │  └────────────┘  └────────────┘  └────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Memory Management Layer                     │  │
│  │  ┌────────────────┐  ┌───────────────┐  ┌────────────┐ │  │
│  │  │ Personal Memory│  │Project Memory │  │Task Memory │ │  │
│  │  │(Long-term/User)│  │(Mid-term/Proj)│  │(Short-term)│ │  │
│  │  └────────────────┘  └───────────────┘  └────────────┘ │  │
│  │                                                          │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │  Memory Framework Integration                   │   │  │
│  │  │  (Zep/Letta/Mem0 - Knowledge Graph + Vectors)  │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                      Data Persistence Layer                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ PostgreSQL   │  │ Vector DB    │  │  Graph DB (Neo4j)    │ │
│  │ (User/Tasks) │  │ (Chroma/     │  │  (Knowledge Graph)   │ │
│  │              │  │  Weaviate)   │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ Redis        │  │ File Storage │                           │
│  │ (Cache/      │  │ (S3/Local)   │                           │
│  │  Sessions)   │  │              │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                    External Services Layer                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ LLM APIs     │  │ Search APIs  │  │  Integration APIs    │ │
│  │ (OpenAI/     │  │ (Google/     │  │  (Calendar/Email/    │ │
│  │  Anthropic/  │  │  Bing/       │  │   Notion/Obsidian)   │ │
│  │  Local LLMs) │  │  Custom)     │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. AI Orchestration System

**Framework Choice: LangGraph + Atomic Agents hybrid approach**

- **State Machine Core**: Tracks current goal, sub-goals, and execution state
- **Goal Planner**: Breaks complex requests into node-based workflows
- **LLM Router**: Intelligently selects appropriate model for each task
- **Tool Manager**: Manages external tool integrations and API calls
- **Execution Engine**: Handles sequential and parallel task execution

**Design Pattern**:

- Use LangGraph for visual workflow design and state management
- Employ Atomic Agents principles for deterministic, structured I/O
- Implement explicit node graphs rather than freestyle agent loops

### 2. Multi-Tier Memory System

**Three-Layer Memory Architecture**:

#### Personal Memory (Long-term)

- **Duration**: Permanent, user-lifetime
- **Scope**: User preferences, habits, personal facts, global context
- **Storage**: Vector DB + Knowledge Graph
- **Examples**:
  - "User prefers morning work sessions"
  - "Client XYZ contact is john@xyz.com"
  - "User's coding language preference: TypeScript"

#### Project Memory (Mid-term)

- **Duration**: Project lifetime (weeks to months)
- **Scope**: Project-specific context, documents, decisions
- **Storage**: Scoped vector indices per project + graph nodes
- **Examples**:
  - "Budget Report deadline: Nov 15"
  - "Project Atlas uses React + Node.js"
  - "Team members: Alice (PM), Bob (Dev)"

#### Task Memory (Short-term)

- **Duration**: Single session or task execution
- **Scope**: Current conversation context, intermediate results
- **Storage**: In-memory + Redis for active sessions
- **Examples**:
  - Last 10 dialogue turns
  - Current search results being analyzed
  - Intermediate calculation outputs

**Implementation Framework**: **Zep** (primary choice)

- Temporal knowledge graph (Graphiti engine)
- Automatic fact extraction and categorization
- Fast retrieval with semantic + graph search
- SOC 2 compliant for enterprise use

**Alternative/Complementary**: Mem0 or Letta for additional context management

### 3. Gamification Engine

**Core RPG Elements**:

- **Character System**: User avatar with stats, levels, and progression
- **XP & Leveling**: Tasks award XP based on difficulty/completion
- **Quest System**: Tasks become quests with narratives
- **World Building**: Procedurally generated world that expands with progress
- **Social Features**: Teams, leaderboards, collaborative quests
- **Rewards & Unlocks**: Cosmetic items, themes, power-ups

**AI-Enhanced Gamification**:

- **Dynamic Narratives**: LLM generates quest descriptions from boring tasks
- **Adaptive Difficulty**: AI adjusts challenge based on user performance
- **Procedural Content**: Story elements and world expansions generated by AI
- **Personalized Themes**: AI tailors game elements to user preferences

**Technical Stack**:

- Game state stored in PostgreSQL
- Real-time updates via WebSockets
- Canvas/WebGL for visual elements (lightweight pixel art style)
- Phaser.js or PixiJS for game rendering (optional)

### 4. LLM Selection Strategy

**Hybrid Approach**:

#### Primary: Open-Source Models (Self-hosted)

- **Model**: LLaMA 2 70B or fine-tuned variant (Vicuna, Mistral)
- **Hosting**: GPU server (A100/H100) or cloud GPU instances
- **Use Cases**:
  - General conversation
  - Task planning
  - Light analysis
  - Gamification narrative generation

#### Secondary: Vendor APIs (Premium/Complex Tasks)

- **Models**: GPT-4/GPT-5, Claude 2/3
- **Use Cases**:
  - Complex multi-step reasoning
  - High-stakes decisions requiring maximum accuracy
  - Premium user tier features
  - Code generation and analysis

#### Specialized Models:

- **Code**: Code Llama, OpenAI Code Interpreter
- **Vision**: GPT-4V, DALL-E (for visual gamification assets)

**Model Router Logic**:

```typescript
interface ModelRouterConfig {
  taskComplexity: "simple" | "moderate" | "complex";
  userTier: "free" | "pro" | "enterprise";
  requiresAccuracy: boolean;
  taskType: "chat" | "code" | "analysis" | "creative";
}

function selectModel(config: ModelRouterConfig): ModelEndpoint {
  if (config.requiresAccuracy && config.taskComplexity === "complex") {
    return "gpt-4"; // Premium API
  }
  if (config.taskType === "code") {
    return "code-llama-34b"; // Specialized
  }
  return "llama-2-70b"; // Default open model
}
```

### 5. Knowledge Retrieval System

**Graph-Based + Vector Hybrid**:

1. **Knowledge Graph Structure** (Neo4j):

   ```
   (User) -[WORKS_ON]-> (Project)
   (Project) -[HAS_TASK]-> (Task)
   (Project) -[INVOLVES]-> (Person)
   (Task) -[RELATED_TO]-> (Document)
   (Topic) -[SUBTOPIC_OF]-> (Topic)
   ```

2. **Vector Embeddings** (Chroma/Weaviate):

   - All documents, notes, conversations embedded
   - Tagged with project_id, date, type metadata
   - Enables semantic search within scoped contexts

3. **Two-Stage Retrieval**:
   - **Stage 1**: Graph query to identify relevant project/context
   - **Stage 2**: Vector similarity search within that context
   - Result: Highly relevant, contextually appropriate information

**Retrieval Flow Example**:

```
User Query: "What's the deadline for the budget report?"
├─ Graph Query: Find (Project {name: ~"budget"})
├─ Scope: project_id = "proj_123"
├─ Vector Search: Semantic search for "deadline" in project_id="proj_123"
└─ Result: "Deadline: November 15, 2024 (from meeting notes on Nov 1)"
```

### 6. Node-Based Planning & Transparency

**Workflow Visualization**:

Every complex task generates a plan as a directed graph:

```typescript
interface WorkflowNode {
  id: string;
  type: "sequential" | "parallel" | "conditional" | "loop";
  action: string; // Human-readable description
  tool?: string; // Tool to invoke (optional)
  status: "pending" | "in_progress" | "completed" | "failed";
  children: WorkflowNode[];
}

// Example: "Organize my week and gamify it"
const examplePlan: WorkflowNode = {
  id: "root",
  type: "sequential",
  action: "Organize and gamify weekly schedule",
  status: "in_progress",
  children: [
    {
      id: "gather",
      type: "parallel",
      action: "Gather upcoming tasks and events",
      tool: "calendar_api",
      status: "completed",
      children: [],
    },
    {
      id: "prioritize",
      type: "sequential",
      action: "Prioritize and assign point values",
      status: "in_progress",
      children: [],
    },
    {
      id: "schedule",
      type: "sequential",
      action: "Create weekly schedule",
      status: "pending",
      children: [],
    },
    {
      id: "gamify",
      type: "sequential",
      action: "Generate game narrative and quest descriptions",
      tool: "llm_narrative",
      status: "pending",
      children: [],
    },
  ],
};
```

**User-Facing Transparency**:

- Display plan before execution: "Here's how I'll tackle this..."
- Real-time progress updates: "Gathering tasks... ✓ Found 12 tasks"
- Allow mid-course corrections: User can skip/modify steps
- Show citations and sources for facts

### 7. Continuous Learning & Customization

**Memory Update Mechanisms**:

- **Automatic Fact Extraction**: After each interaction, extract new facts
- **Deduplication**: Check if fact already exists before storing
- **Summarization**: Compress long conversations into key takeaways
- **Timestamp Tracking**: Version facts with temporal data
- **Source Attribution**: Store where information came from

**User Customization Options**:

```typescript
interface UserPreferences {
  // Memory Settings
  memoryRetention: "minimal" | "standard" | "comprehensive";
  allowPersonalData: boolean;

  // AI Behavior
  llmProvider: "open-source" | "openai" | "anthropic" | "bring-your-own";
  apiKey?: string; // For BYO model
  responseStyle: "formal" | "casual" | "humorous";
  verbosity: "concise" | "balanced" | "detailed";

  // Gamification
  gameTheme: "fantasy-rpg" | "sci-fi" | "minimal" | "custom";
  showNarratives: boolean;
  socialFeatures: boolean;

  // Tools & Integrations
  enabledTools: string[]; // ['calendar', 'email', 'notion', ...]
  integrations: { [key: string]: IntegrationConfig };
}
```

## Technology Stack

### Frontend

- **Framework**: Electron (cross-platform desktop) + React/Vue
- **UI Library**: Tailwind CSS + shadcn/ui or Ant Design
- **Game Rendering**: Canvas API + PixiJS (optional)
- **State Management**: Zustand or Redux Toolkit
- **Real-time**: Socket.io-client

### Backend

- **Runtime**: Node.js 20+ with TypeScript
- **Framework**: Fastify (high-performance) or Express
- **API**: REST + GraphQL (optional) + WebSocket
- **Validation**: Zod for schema validation
- **Authentication**: JWT + OAuth2 (Google, GitHub)

### AI/ML Stack

- **Orchestration**: LangGraph + Atomic Agents patterns
- **Memory**: Zep + custom layer
- **LLM**:
  - Open: llama.cpp (CPU inference) or vLLM (GPU inference)
  - APIs: OpenAI SDK, Anthropic SDK
- **Embeddings**: OpenAI text-embedding-3, or local (all-MiniLM-L6-v2)
- **Vector DB**: Chroma (embedded) or Weaviate (server)

### Databases

- **Primary**: PostgreSQL 15+ (user data, tasks, game state)
- **Cache**: Redis 7+ (sessions, rate limiting)
- **Vector**: Chroma or Weaviate
- **Graph**: Neo4j Community Edition (knowledge graph)

### DevOps

- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (production scale)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Winston + Loki

### Hosting

- **Backend**: AWS EC2/ECS, Railway, or Render
- **Database**: Managed PostgreSQL (RDS, Supabase)
- **Vector DB**: Hosted Weaviate or self-hosted
- **GPU Inference**: Modal, RunPod, or AWS EC2 with GPU
- **CDN**: Cloudflare or AWS CloudFront

## Security & Privacy

1. **Data Encryption**: At rest (AES-256) and in transit (TLS 1.3)
2. **Authentication**: JWT with refresh tokens, optional OAuth
3. **Authorization**: Role-based access control (RBAC)
4. **Memory Isolation**: Per-user encryption keys for sensitive data
5. **Audit Logs**: All AI actions logged for transparency
6. **GDPR Compliance**: User data export, deletion, and consent management
7. **Rate Limiting**: Prevent abuse of AI endpoints
8. **Input Sanitization**: Prevent prompt injection attacks

## Scalability Considerations

1. **Horizontal Scaling**: Stateless backend services with Redis for shared state
2. **Database Sharding**: Partition by user_id for large user bases
3. **Vector DB Optimization**: Index partitioning by project/user
4. **LLM Inference**: Queue system for handling concurrent requests
5. **CDN**: Static assets and frontend bundles
6. **Caching Strategy**: Multi-tier (browser → Redis → DB)

## Development Phases

See [ROADMAP.md](./ROADMAP.md) for detailed implementation phases.

## Next Steps

1. Set up project structure and initialize repositories
2. Implement core backend services (auth, database)
3. Integrate memory framework (Zep) with vector DB
4. Build AI orchestration layer with LangGraph
5. Develop gamification engine
6. Create frontend UI with game elements
7. Testing, optimization, and deployment

---

_Last Updated: November 7, 2025_
