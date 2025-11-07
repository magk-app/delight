# Memory System Architecture

## Overview

Delight implements a three-tier memory architecture that enables the AI assistant to maintain context at different time scales: Personal (lifetime), Project (mid-term), and Task (session-based). This approach prevents context overload while ensuring the AI has access to relevant information at the right time.

## Three-Tier Memory Architecture

### Tier 1: Personal Memory (Long-Term)

**Duration**: Permanent, user-lifetime  
**Scope**: User-wide preferences, habits, contacts, and global knowledge

#### What Gets Stored

- User preferences (work hours, notification settings, tone preferences)
- Personal facts (birthday, location, occupation)
- Contacts and relationships (colleague names, roles, contact info)
- Recurring patterns (user tends to work on coding tasks in the morning)
- Global skills and knowledge (user knows Python, TypeScript, React)
- Historical patterns (user's productivity peaks, common blockers)

#### Storage Implementation

```typescript
interface PersonalMemory {
  userId: string;
  factId: string;
  factType: "preference" | "contact" | "skill" | "pattern" | "historical";
  content: string;
  embedding: number[]; // 1536-dim vector (OpenAI ada-002)
  metadata: {
    category: string;
    importance: "high" | "medium" | "low";
    confidence: number; // 0-1
    source: string; // Where this fact came from
    lastUpdated: Date;
    accessCount: number;
  };
}
```

#### Example Queries

- "What's my preferred working schedule?"
- "Who is my manager?"
- "What programming languages do I know?"

### Tier 2: Project Memory (Mid-Term)

**Duration**: Project lifetime (weeks to months)  
**Scope**: Project-specific context, documents, decisions, and team members

#### What Gets Stored

- Project metadata (name, description, goals, deadlines)
- Team members and roles
- Key decisions made during the project
- Project-related documents and references
- Technical context (tech stack, architecture decisions)
- Meeting notes and action items specific to the project
- Project milestones and progress

#### Storage Implementation

```typescript
interface ProjectMemory {
  projectId: string;
  userId: string;
  factId: string;
  factType: "decision" | "document" | "team_member" | "milestone" | "technical";
  content: string;
  embedding: number[];
  metadata: {
    relevanceScore: number;
    relatedTasks: string[]; // Task IDs
    relatedDocs: string[]; // Document IDs
    tags: string[];
    lastAccessed: Date;
  };
}
```

#### Knowledge Graph Structure

```cypher
// Neo4j graph schema
(User)-[:OWNS]->(Project)
(Project)-[:HAS_TEAM_MEMBER]->(Person)
(Project)-[:HAS_TASK]->(Task)
(Project)-[:CONTAINS_DOCUMENT]->(Document)
(Project)-[:MADE_DECISION]->(Decision)
(Task)-[:RELATED_TO]->(Document)
(Task)-[:ASSIGNED_TO]->(Person)
(Decision)-[:AFFECTS]->(Task)
```

#### Example Queries

- "What's the deadline for the Budget Report project?"
- "Who's working on Project Atlas with me?"
- "What tech stack are we using for the mobile app?"

### Tier 3: Task Memory (Short-Term)

**Duration**: Single session or task execution  
**Scope**: Current conversation, intermediate results, working context

#### What Gets Stored

- Recent conversation history (last 10-20 exchanges)
- Intermediate computation results
- Current search results being analyzed
- Temporary user context (current mood, immediate goal)
- In-progress workflow state

#### Storage Implementation

```typescript
interface TaskMemory {
  sessionId: string;
  userId: string;
  messages: ConversationMessage[];
  workingContext: {
    currentGoal: string;
    subGoals: string[];
    intermediateResults: Record<string, any>;
    toolOutputs: ToolOutput[];
  };
  expiresAt: Date;
}

interface ConversationMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: {
    tokenCount: number;
    model: string;
  };
}
```

#### Storage Backend

- **Primary**: Redis (in-memory, fast)
- **TTL**: 4 hours (auto-cleanup)
- **Persistence**: Optional save to PostgreSQL for important sessions

#### Example Usage

- Keeps track of what the user just said
- Remembers search results from 2 prompts ago
- Maintains state during multi-step task execution

---

## Memory Framework: Zep Integration

### Why Zep?

[Zep](https://www.getzep.com/) is chosen as the primary memory framework because:

1. **Temporal Knowledge Graph**: Graphiti engine links facts over time
2. **Automatic Fact Extraction**: Extracts entities and relationships from conversations
3. **Fast Retrieval**: Optimized for real-time queries (<100ms)
4. **Scalable**: Handles millions of facts per user
5. **SOC 2 Compliant**: Enterprise-ready security
6. **Open Source Core**: Self-hostable

### Zep Architecture

```
┌─────────────────────────────────────────────┐
│         Delight AI Agent                    │
│  ┌───────────────────────────────────────┐ │
│  │  Conversation Manager                 │ │
│  └─────────────┬─────────────────────────┘ │
└────────────────┼───────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│            Zep Memory Server                │
│                                             │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │   Session    │  │  Knowledge Graph │   │
│  │   Manager    │  │   (Graphiti)     │   │
│  └──────────────┘  └──────────────────┘   │
│                                             │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ Fact         │  │  Embedding       │   │
│  │ Extractor    │  │  Store           │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          Persistent Storage                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │PostgreSQL│  │  Vector  │  │  Redis   │ │
│  │          │  │   Store  │  │          │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
```

### Zep Integration Code Example

```typescript
import { ZepClient } from "@getzep/zep-js";

class MemoryManager {
  private zepClient: ZepClient;

  constructor(apiUrl: string, apiKey: string) {
    this.zepClient = new ZepClient({
      apiUrl,
      apiKey,
    });
  }

  // Add message to session (auto-extracts facts)
  async addMessage(
    sessionId: string,
    role: "user" | "assistant",
    content: string
  ): Promise<void> {
    await this.zepClient.memory.addMemory(sessionId, {
      messages: [
        {
          role,
          content,
          role_type: role === "user" ? "human" : "ai",
        },
      ],
    });
  }

  // Retrieve relevant context for a query
  async getRelevantContext(
    sessionId: string,
    query: string,
    memoryType: "perpetual" | "summary" = "perpetual"
  ): Promise<string> {
    const searchResults = await this.zepClient.memory.searchMemory(
      sessionId,
      {
        text: query,
        metadata: {
          // Can filter by project, date range, etc.
        },
      },
      10 // top 10 results
    );

    // Combine relevant facts into context string
    return searchResults.map((r) => r.message?.content || "").join("\n\n");
  }

  // Extract and store a specific fact
  async storeFact(
    userId: string,
    fact: string,
    factType: "personal" | "project" | "task",
    metadata: Record<string, any>
  ): Promise<void> {
    const sessionId = `${userId}_${factType}`;

    await this.zepClient.memory.addMemory(sessionId, {
      messages: [
        {
          role: "system",
          content: `FACT: ${fact}`,
          role_type: "system",
          metadata: {
            type: factType,
            ...metadata,
          },
        },
      ],
    });
  }

  // Get user's personal memory summary
  async getPersonalMemorySummary(userId: string): Promise<string> {
    const memory = await this.zepClient.memory.getMemory(
      `${userId}_personal`,
      "summary" // Get summarized version
    );

    return memory.summary?.content || "";
  }
}
```

---

## Two-Stage Retrieval Strategy

To ensure fast and relevant memory retrieval, we employ a two-stage approach:

### Stage 1: Coarse Filtering (Graph Query)

**Goal**: Identify the relevant domain/project/category

**Implementation**:

```cypher
// Neo4j query to find relevant project
MATCH (u:User {id: $userId})-[:OWNS]->(p:Project)
WHERE p.name CONTAINS $queryKeyword
  OR ANY(tag IN p.tags WHERE tag CONTAINS $queryKeyword)
RETURN p.id, p.name, p.metadata
LIMIT 5
```

**Example**:

- User asks: "What's the deadline for the budget report?"
- Stage 1: Find `Project` nodes with name containing "budget"
- Result: `project_id = "proj_123"`

### Stage 2: Fine Retrieval (Vector Search)

**Goal**: Find the most semantically relevant facts within the scope

**Implementation**:

```typescript
async function retrieveMemory(
  userId: string,
  query: string,
  projectId?: string
): Promise<MemoryResult[]> {
  // Stage 1: Determine scope
  const scope = projectId ? `project:${projectId}` : `user:${userId}`;

  // Stage 2: Vector search within scope
  const queryEmbedding = await getEmbedding(query);

  const results = await vectorDB.query({
    vector: queryEmbedding,
    filter: {
      userId,
      ...(projectId && { projectId }),
    },
    topK: 10,
  });

  return results.map((r) => ({
    content: r.metadata.content,
    relevance: r.score,
    source: r.metadata.source,
    timestamp: r.metadata.lastUpdated,
  }));
}
```

**Example**:

- Scope: `project_id = "proj_123"`
- Vector search query: "deadline"
- Result: Top 10 most relevant facts about deadlines in that project

---

## Memory Update Mechanisms

### Automatic Fact Extraction

After each user interaction, extract new facts:

```typescript
async function extractAndStoreFacts(
  userId: string,
  conversation: string
): Promise<void> {
  // Use LLM to extract facts
  const prompt = `
Extract important facts from this conversation that should be remembered long-term.
Format: JSON array of objects with {fact, type, importance}

Conversation:
${conversation}

Facts:`;

  const response = await llm.complete(prompt);
  const facts = JSON.parse(response);

  for (const { fact, type, importance } of facts) {
    // Check for duplicates
    const existing = await checkDuplicateFact(userId, fact);
    if (!existing) {
      await memoryManager.storeFact(userId, fact, type, {
        importance,
        source: "conversation",
        timestamp: new Date(),
      });
    }
  }
}
```

### Deduplication

Prevent storing the same fact multiple times:

```typescript
async function checkDuplicateFact(
  userId: string,
  newFact: string
): Promise<boolean> {
  const embedding = await getEmbedding(newFact);

  const similar = await vectorDB.query({
    vector: embedding,
    filter: { userId },
    topK: 1,
  });

  // If cosine similarity > 0.95, consider it a duplicate
  return similar[0]?.score > 0.95;
}
```

### Memory Consolidation

Periodically summarize and consolidate memories:

```typescript
async function consolidateMemories(userId: string): Promise<void> {
  // Every week, summarize task memories into project memories
  const recentTasks = await getTaskMemories(userId, {
    since: Date.now() - 7 * 24 * 60 * 60 * 1000,
  });

  const summary = await llm.complete(`
Summarize these task interactions into key takeaways:
${recentTasks.join("\n\n")}

Key takeaways:
`);

  await memoryManager.storeFact(userId, summary, "project", {
    importance: "high",
    source: "consolidation",
    timestamp: new Date(),
  });

  // Archive or delete old task memories
  await archiveTaskMemories(userId, recentTasks);
}
```

---

## Memory Retrieval Optimization

### Caching Strategy

```typescript
class MemoryCacheManager {
  private redis: RedisClient;

  // Cache frequently accessed facts
  async getCachedMemory(key: string): Promise<string | null> {
    return await this.redis.get(`memory:${key}`);
  }

  async setCachedMemory(
    key: string,
    value: string,
    ttl: number = 3600
  ): Promise<void> {
    await this.redis.setex(`memory:${key}`, ttl, value);
  }

  // Invalidate cache when memory updated
  async invalidate(pattern: string): Promise<void> {
    const keys = await this.redis.keys(`memory:${pattern}*`);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
}
```

### Lazy Loading

Load memories only when needed:

```typescript
class LazyMemoryLoader {
  private loaded: Set<string> = new Set();

  async loadIfNeeded(
    userId: string,
    context: "personal" | "project" | "task"
  ): Promise<void> {
    const key = `${userId}:${context}`;

    if (!this.loaded.has(key)) {
      // Load memories on first access
      await this.loadMemoriesForContext(userId, context);
      this.loaded.add(key);
    }
  }

  private async loadMemoriesForContext(
    userId: string,
    context: string
  ): Promise<void> {
    // Load from Zep/vector DB into local cache
    const memories = await memoryManager.getMemories(userId, context);
    await cacheManager.setCachedMemory(
      `${userId}:${context}`,
      JSON.stringify(memories),
      3600
    );
  }
}
```

---

## Privacy & Security

### User Control

Users have full control over their memories:

```typescript
interface MemoryControls {
  // View all stored memories
  listMemories(userId: string): Promise<Memory[]>;

  // Delete specific memory
  deleteMemory(userId: string, memoryId: string): Promise<void>;

  // Export all memories (GDPR compliance)
  exportMemories(userId: string): Promise<ExportData>;

  // Clear all memories
  clearAllMemories(userId: string): Promise<void>;

  // Set retention policy
  setRetentionPolicy(
    userId: string,
    policy: "minimal" | "standard" | "comprehensive"
  ): Promise<void>;
}
```

### Encryption

Sensitive memories encrypted at rest:

```typescript
import { createCipheriv, createDecipheriv, randomBytes } from "crypto";

class MemoryEncryption {
  private algorithm = "aes-256-gcm";

  encrypt(text: string, key: Buffer): EncryptedData {
    const iv = randomBytes(16);
    const cipher = createCipheriv(this.algorithm, key, iv);

    let encrypted = cipher.update(text, "utf8", "hex");
    encrypted += cipher.final("hex");

    const authTag = cipher.getAuthTag();

    return {
      encrypted,
      iv: iv.toString("hex"),
      authTag: authTag.toString("hex"),
    };
  }

  decrypt(data: EncryptedData, key: Buffer): string {
    const decipher = createDecipheriv(
      this.algorithm,
      key,
      Buffer.from(data.iv, "hex")
    );

    decipher.setAuthTag(Buffer.from(data.authTag, "hex"));

    let decrypted = decipher.update(data.encrypted, "hex", "utf8");
    decrypted += decipher.final("utf8");

    return decrypted;
  }
}
```

---

## Performance Benchmarks

Target performance metrics:

| Operation                 | Target Latency | Notes                          |
| ------------------------- | -------------- | ------------------------------ |
| Personal Memory Retrieval | < 100ms        | Single fact lookup             |
| Project Memory Retrieval  | < 200ms        | Filtered vector search         |
| Task Memory Access        | < 50ms         | Redis cache hit                |
| Memory Storage            | < 300ms        | Including embedding generation |
| Graph Query               | < 150ms        | Neo4j traversal                |
| Full Context Assembly     | < 500ms        | All tiers combined             |

---

## Example: Full Memory Flow

```typescript
// User asks: "What tasks do I have for Project Atlas?"

async function handleQuery(userId: string, query: string): Promise<string> {
  // 1. Load personal context (user preferences, habits)
  const personalContext = await memoryManager.getPersonalMemorySummary(userId);

  // 2. Identify relevant project (Stage 1: Graph query)
  const projects = await graphDB.query(
    `
    MATCH (u:User {id: $userId})-[:OWNS]->(p:Project)
    WHERE p.name CONTAINS 'Atlas'
    RETURN p
  `,
    { userId }
  );

  const projectId = projects[0]?.id;

  // 3. Retrieve project-specific context (Stage 2: Vector search)
  const projectContext = await memoryManager.getRelevantContext(
    `${userId}_project_${projectId}`,
    query
  );

  // 4. Get current task memory (Redis)
  const taskContext = await redis.get(`session:${userId}:current`);

  // 5. Assemble full context
  const fullContext = `
Personal Context:
${personalContext}

Project Context (Project Atlas):
${projectContext}

Current Session:
${taskContext}

User Query: ${query}
`;

  // 6. Send to LLM with full context
  const response = await llm.complete(fullContext);

  // 7. Extract and store new facts from this interaction
  await extractAndStoreFacts(userId, `Query: ${query}\nResponse: ${response}`);

  return response;
}
```

---

## Next Steps

1. **Set up Zep server**: Deploy Zep on Railway or self-hosted
2. **Configure vector database**: Choose between Chroma (embedded) or Weaviate (server)
3. **Implement memory manager**: Build TypeScript wrapper around Zep
4. **Build knowledge graph**: Set up Neo4j and define schema
5. **Test retrieval performance**: Benchmark against targets
6. **Implement memory UI**: Let users view/manage their memories

---

_Last Updated: November 7, 2025_
