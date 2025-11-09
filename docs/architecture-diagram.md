# Delight - Comprehensive Architecture Diagram

## Full System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer - Next.js 15 + React 19"
        UI[UI Components<br/>shadcn/ui + Framer Motion]
        APP[App Router<br/>Routes & Pages]
        HOOKS[React Hooks<br/>State Management]
        API_CLIENT[API Client<br/>REST + SSE]
        THEMES[Theme System<br/>Medieval/Sci-Fi]
    end

    subgraph "Backend Layer - FastAPI"
        subgraph "API Endpoints"
            API_COMPANION[Companion API<br/>/api/v1/companion]
            API_MISSIONS[Missions API<br/>/api/v1/missions]
            API_NARRATIVE[Narrative API<br/>/api/v1/narrative]
            API_WORLD[World API<br/>/api/v1/world]
            API_PROGRESS[Progress API<br/>/api/v1/progress]
            SSE[SSE Streaming<br/>/api/v1/sse/*]
        end

        subgraph "Services Layer"
            SVC_COMPANION[Companion Service<br/>Eliza Orchestration]
            SVC_NARRATIVE[Narrative Service<br/>Story Generation]
            SVC_MISSION[Mission Service<br/>Quest Logic]
            SVC_CHARACTER[Character Service<br/>Multi-Character AI]
            SVC_MEMORY[Memory Service<br/>Chroma Integration]
            SVC_WORLD[World Service<br/>Time-Aware State]
        end
    end

    subgraph "AI Orchestration Layer - LangGraph + LangChain"
        subgraph "LangGraph Agents"
            AGENT_ELIZA[Eliza Agent<br/>Main Companion]
            AGENT_NARRATIVE[Narrative Agent<br/>Story State Machine]
            AGENT_LYRA[Lyra Agent<br/>Craft Focus]
            AGENT_THORNE[Thorne Agent<br/>Health Focus]
            AGENT_ELARA[Elara Agent<br/>Growth Focus]
        end

        LANGCHAIN[LangChain Core<br/>LLM Integration]
    end

    subgraph "Background Jobs Layer - ARQ + Redis"
        WORKER_QUEST[Quest Generator<br/>Pre-plan Hidden Quests]
        WORKER_NUDGE[Nudge Scheduler<br/>Proactive Outreach]
        WORKER_CHARACTER[Character Initiator<br/>AI-Initiated Chats]
        WORKER_MEMORY[Memory Consolidation<br/>Long-term Storage]
    end

    subgraph "Storage Layer"
        subgraph "PostgreSQL Database"
            DB_USERS[(Users)]
            DB_MISSIONS[(Missions)]
            DB_CHARACTERS[(Characters)]
            DB_NARRATIVE[(Narrative States)]
            DB_PROGRESS[(Progress/DCI)]
            DB_RELATIONSHIPS[(Character<br/>Relationships)]
        end

        subgraph "Vector Storage - Chroma"
            CHROMA_PERSONAL[(Personal<br/>Memory)]
            CHROMA_PROJECT[(Project<br/>Memory)]
            CHROMA_TASK[(Task<br/>Memory)]
            CHROMA_CHAR[(Character<br/>Conversations)]
        end

        REDIS[(Redis Cache<br/>World State<br/>Sessions)]
        S3[(S3 Storage<br/>Evidence Files)]
    end

    subgraph "External Services"
        LLM_PROVIDERS[LLM Providers<br/>OpenAI/Anthropic]
    end

    %% Frontend Connections
    UI --> APP
    APP --> HOOKS
    HOOKS --> API_CLIENT
    API_CLIENT --> API_COMPANION
    API_CLIENT --> API_MISSIONS
    API_CLIENT --> API_NARRATIVE
    API_CLIENT --> API_WORLD
    API_CLIENT --> API_PROGRESS
    API_CLIENT --> SSE

    %% API to Services
    API_COMPANION --> SVC_COMPANION
    API_MISSIONS --> SVC_MISSION
    API_NARRATIVE --> SVC_NARRATIVE
    API_WORLD --> SVC_WORLD
    API_PROGRESS --> SVC_MISSION
    SSE --> SVC_COMPANION
    SSE --> SVC_NARRATIVE

    %% Services to AI Layer
    SVC_COMPANION --> AGENT_ELIZA
    SVC_NARRATIVE --> AGENT_NARRATIVE
    SVC_CHARACTER --> AGENT_LYRA
    SVC_CHARACTER --> AGENT_THORNE
    SVC_CHARACTER --> AGENT_ELARA
    SVC_MEMORY --> LANGCHAIN

    %% AI to LangChain
    AGENT_ELIZA --> LANGCHAIN
    AGENT_NARRATIVE --> LANGCHAIN
    AGENT_LYRA --> LANGCHAIN
    AGENT_THORNE --> LANGCHAIN
    AGENT_ELARA --> LANGCHAIN

    %% LangChain to LLM
    LANGCHAIN --> LLM_PROVIDERS

    %% Services to Storage
    SVC_COMPANION --> DB_USERS
    SVC_MISSION --> DB_MISSIONS
    SVC_CHARACTER --> DB_CHARACTERS
    SVC_CHARACTER --> DB_RELATIONSHIPS
    SVC_NARRATIVE --> DB_NARRATIVE
    SVC_MISSION --> DB_PROGRESS
    SVC_WORLD --> REDIS

    %% Memory Service to Vector Storage
    SVC_MEMORY --> CHROMA_PERSONAL
    SVC_MEMORY --> CHROMA_PROJECT
    SVC_MEMORY --> CHROMA_TASK
    SVC_MEMORY --> CHROMA_CHAR

    %% Evidence Storage
    SVC_MISSION --> S3

    %% Background Jobs
    WORKER_QUEST --> DB_NARRATIVE
    WORKER_QUEST --> AGENT_NARRATIVE
    WORKER_NUDGE --> DB_USERS
    WORKER_NUDGE --> SVC_COMPANION
    WORKER_CHARACTER --> DB_CHARACTERS
    WORKER_CHARACTER --> SVC_CHARACTER
    WORKER_MEMORY --> CHROMA_PERSONAL
    WORKER_MEMORY --> CHROMA_PROJECT

    %% Styling
    classDef frontend fill:#3b82f6,stroke:#1e40af,color:#fff
    classDef backend fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef ai fill:#ec4899,stroke:#be185d,color:#fff
    classDef storage fill:#10b981,stroke:#059669,color:#fff
    classDef workers fill:#f59e0b,stroke:#d97706,color:#fff
    classDef external fill:#6366f1,stroke:#4338ca,color:#fff

    class UI,APP,HOOKS,API_CLIENT,THEMES frontend
    class API_COMPANION,API_MISSIONS,API_NARRATIVE,API_WORLD,API_PROGRESS,SSE,SVC_COMPANION,SVC_NARRATIVE,SVC_MISSION,SVC_CHARACTER,SVC_MEMORY,SVC_WORLD backend
    class AGENT_ELIZA,AGENT_NARRATIVE,AGENT_LYRA,AGENT_THORNE,AGENT_ELARA,LANGCHAIN ai
    class DB_USERS,DB_MISSIONS,DB_CHARACTERS,DB_NARRATIVE,DB_PROGRESS,DB_RELATIONSHIPS,CHROMA_PERSONAL,CHROMA_PROJECT,CHROMA_TASK,CHROMA_CHAR,REDIS,S3 storage
    class WORKER_QUEST,WORKER_NUDGE,WORKER_CHARACTER,WORKER_MEMORY workers
    class LLM_PROVIDERS external
```

## Living Narrative Engine - Detailed Flow

```mermaid
stateDiagram-v2
    [*] --> StoryStart: User Onboarding

    StoryStart --> GenerateQuests: Initialize Story
    GenerateQuests --> Chapter1: 3-5 Hidden Quests Pre-planned

    state Chapter1 {
        [*] --> InProgress
        InProgress --> CheckTriggers: User Completes Missions
        CheckTriggers --> InProgress: Conditions Not Met
        CheckTriggers --> UnlockQuest: Condition Met (e.g., 20 missions)
        UnlockQuest --> InProgress: Quest Available
    }

    Chapter1 --> Chapter2: Chapter Complete

    state Chapter2 {
        [*] --> GenerateNewQuests
        GenerateNewQuests --> ChapterProgress
        ChapterProgress --> UnlockHiddenQuest
        UnlockHiddenQuest --> ChapterProgress
    }

    Chapter2 --> Chapter3: Advance Story
    Chapter3 --> Epilogue
    Epilogue --> [*]: Story Complete

    note right of GenerateQuests
        Narrative Agent (LangGraph)
        Pre-generates hidden quests
        with triggers and rewards
    end note

    note right of CheckTriggers
        ARQ Worker monitors
        mission completion count,
        specific achievements,
        time-based conditions
    end note
```

## Multi-Character AI System

```mermaid
graph LR
    subgraph "User Interactions"
        USER[User]
    end

    subgraph "Character Orchestration"
        ORCHESTRATOR[Character Service<br/>Orchestrator]

        subgraph "Character Agents"
            ELIZA[Eliza<br/>Protagonist<br/>General Support]
            LYRA[Lyra<br/>Craft Domain<br/>Creative Focus]
            THORNE[Thorne<br/>Health Domain<br/>Physical Goals]
            ELARA[Elara<br/>Growth Domain<br/>Learning Focus]
        end

        PERSONALITY[Personality System<br/>JSONB Configs]
        RELATIONSHIPS[Relationship Tracker<br/>0-10 Levels]
    end

    subgraph "Character Memory"
        CONV_ELIZA[(Eliza<br/>Conversations)]
        CONV_LYRA[(Lyra<br/>Conversations)]
        CONV_THORNE[(Thorne<br/>Conversations)]
        CONV_ELARA[(Elara<br/>Conversations)]
    end

    subgraph "Initiation System"
        SCHEDULER[ARQ Scheduler<br/>Proactive Outreach]
        PATTERNS[Activity Pattern<br/>Analyzer]
    end

    %% User to Orchestrator
    USER -->|Chat Request| ORCHESTRATOR

    %% Orchestrator to Characters
    ORCHESTRATOR --> ELIZA
    ORCHESTRATOR --> LYRA
    ORCHESTRATOR --> THORNE
    ORCHESTRATOR --> ELARA

    %% Characters to Memory
    ELIZA --> CONV_ELIZA
    LYRA --> CONV_LYRA
    THORNE --> CONV_THORNE
    ELARA --> CONV_ELARA

    %% Personality System
    PERSONALITY --> ELIZA
    PERSONALITY --> LYRA
    PERSONALITY --> THORNE
    PERSONALITY --> ELARA

    %% Relationship Tracking
    RELATIONSHIPS --> ORCHESTRATOR

    %% Proactive Initiation
    SCHEDULER --> PATTERNS
    PATTERNS --> ORCHESTRATOR
    ORCHESTRATOR -->|Notification| USER

    %% Styling
    classDef user fill:#3b82f6,stroke:#1e40af,color:#fff
    classDef orchestration fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef character fill:#ec4899,stroke:#be185d,color:#fff
    classDef memory fill:#10b981,stroke:#059669,color:#fff
    classDef scheduler fill:#f59e0b,stroke:#d97706,color:#fff

    class USER user
    class ORCHESTRATOR,PERSONALITY,RELATIONSHIPS orchestration
    class ELIZA,LYRA,THORNE,ELARA character
    class CONV_ELIZA,CONV_LYRA,CONV_THORNE,CONV_ELARA memory
    class SCHEDULER,PATTERNS scheduler
```

## Time-Aware World State System

```mermaid
graph TB
    subgraph "Time Rules Engine"
        TIME[Real-World Time<br/>User Timezone]
        RULES[Time Rules<br/>Default + Overrides]
        USER_PREFS[User Preferences<br/>Custom Hours]
    end

    subgraph "World Zones"
        ARENA[Arena<br/>Health Domain<br/>Opens: 6am<br/>Closes: 9pm]
        OBSERVATORY[Observatory<br/>Growth Domain<br/>Always Open]
        COMMONS[Commons<br/>Connection<br/>Opens: 12pm<br/>Closes: 10pm]
    end

    subgraph "Character Presence"
        CHAR_AVAIL[Character Availability<br/>Based on Zone & Time]
    end

    subgraph "Cache Layer"
        REDIS_CACHE[(Redis Cache<br/>World State<br/>TTL: 15min)]
    end

    subgraph "Frontend"
        WORLD_UI[World State Display<br/>Polls every 15min]
    end

    %% Time Flow
    TIME --> RULES
    USER_PREFS --> RULES
    RULES --> ARENA
    RULES --> OBSERVATORY
    RULES --> COMMONS

    %% Character Presence
    ARENA --> CHAR_AVAIL
    OBSERVATORY --> CHAR_AVAIL
    COMMONS --> CHAR_AVAIL

    %% Caching
    ARENA --> REDIS_CACHE
    OBSERVATORY --> REDIS_CACHE
    COMMONS --> REDIS_CACHE
    CHAR_AVAIL --> REDIS_CACHE

    %% Frontend Polling
    REDIS_CACHE --> WORLD_UI

    %% Styling
    classDef time fill:#3b82f6,stroke:#1e40af,color:#fff
    classDef zones fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef cache fill:#10b981,stroke:#059669,color:#fff
    classDef frontend fill:#ec4899,stroke:#be185d,color:#fff

    class TIME,RULES,USER_PREFS time
    class ARENA,OBSERVATORY,COMMONS,CHAR_AVAIL zones
    class REDIS_CACHE cache
    class WORLD_UI frontend
```

## Data Architecture

```mermaid
erDiagram
    USERS ||--o{ MISSIONS : creates
    USERS ||--|| NARRATIVE_STATES : has
    USERS ||--o{ PROGRESS : tracks
    USERS ||--o{ CHARACTER_RELATIONSHIPS : has
    CHARACTERS ||--o{ CHARACTER_RELATIONSHIPS : participates
    MISSIONS ||--o{ EVIDENCE : contains

    USERS {
        uuid id PK
        string email
        string password_hash
        string timezone
        string theme_preference
        timestamp created_at
    }

    MISSIONS {
        uuid id PK
        uuid user_id FK
        string title
        string description
        int duration_minutes
        int essence_reward
        enum attribute_type
        enum status
        timestamp created_at
        timestamp completed_at
    }

    CHARACTERS {
        uuid id PK
        string name
        jsonb personality_prompt
        enum attribute_focus
        string scenario
    }

    CHARACTER_RELATIONSHIPS {
        uuid id PK
        uuid user_id FK
        uuid character_id FK
        int relationship_level
        timestamp last_interaction_at
    }

    NARRATIVE_STATES {
        uuid id PK
        uuid user_id FK
        string scenario
        int current_chapter
        jsonb hidden_quests
        jsonb story_progress
    }

    PROGRESS {
        uuid id PK
        uuid user_id FK
        date date
        float dci_score
        int missions_completed
        int streak_days
        int essence_earned
    }

    EVIDENCE {
        uuid id PK
        uuid mission_id FK
        string file_url
        string note
        timestamp created_at
    }
```

## API Communication Flow

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Frontend (Next.js)
    participant A as API Layer (FastAPI)
    participant S as Service Layer
    participant AI as AI Agents (LangGraph)
    participant LLM as LLM (OpenAI/Anthropic)
    participant DB as PostgreSQL
    participant V as Chroma (Vector DB)

    Note over U,V: User starts chat with Eliza

    U->>F: Types message
    F->>A: POST /api/v1/companion/chat
    A->>S: companion_service.chat()

    par Retrieve Context
        S->>V: Search personal memory
        V-->>S: Relevant memories
    and Load User Data
        S->>DB: Get user profile
        DB-->>S: User context
    end

    S->>AI: Invoke Eliza Agent
    AI->>LLM: Generate response (streaming)

    Note over A,F: SSE Streaming Response

    loop Token by token
        LLM-->>AI: Token
        AI-->>S: Token
        S-->>A: Token
        A-->>F: SSE: data: {"token": "..."}
        F-->>U: Display token
    end

    LLM-->>AI: Complete
    AI-->>S: Full response

    par Save to Memory
        S->>V: Store conversation
    and Update State
        S->>DB: Update last interaction
    end

    A-->>F: SSE: data: {"type": "complete"}
    F-->>U: Message complete

    Note over U,V: Background: Hidden Quest Check

    Note over S,DB: ARQ Worker monitors mission count
    S->>DB: Check hidden quest triggers
    DB-->>S: Trigger met (20 missions)
    S->>DB: Unlock hidden quest
    S->>F: SSE notification
    F->>U: "New quest unlocked!"
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Client"
        BROWSER[Web Browser<br/>React UI]
    end

    subgraph "CDN Layer"
        VERCEL[Vercel Edge Network<br/>Next.js Frontend<br/>Static Assets]
    end

    subgraph "Backend Services"
        subgraph "Compute"
            API_SERVER1[FastAPI Instance 1]
            API_SERVER2[FastAPI Instance 2]
            WORKER_POOL[ARQ Worker Pool]
        end

        LOAD_BALANCER[Load Balancer<br/>Railway/Fly.io]
    end

    subgraph "Data Layer"
        PRIMARY_DB[(PostgreSQL<br/>Primary)]
        REPLICA_DB[(PostgreSQL<br/>Read Replica)]
        REDIS_CLUSTER[(Redis<br/>Cache + Queue)]
        CHROMA_STORE[(Chroma<br/>Vector Storage)]
        S3_BUCKET[(S3<br/>File Storage)]
    end

    subgraph "External"
        LLM_API[LLM APIs<br/>OpenAI/Anthropic]
    end

    subgraph "Observability"
        SENTRY[Sentry<br/>Error Tracking]
        DATADOG[Datadog/New Relic<br/>APM & Monitoring]
    end

    %% User Flow
    BROWSER --> VERCEL
    VERCEL --> LOAD_BALANCER

    %% Load Balancing
    LOAD_BALANCER --> API_SERVER1
    LOAD_BALANCER --> API_SERVER2

    %% Backend to Data
    API_SERVER1 --> PRIMARY_DB
    API_SERVER1 --> REPLICA_DB
    API_SERVER1 --> REDIS_CLUSTER
    API_SERVER1 --> CHROMA_STORE
    API_SERVER1 --> S3_BUCKET

    API_SERVER2 --> PRIMARY_DB
    API_SERVER2 --> REPLICA_DB
    API_SERVER2 --> REDIS_CLUSTER
    API_SERVER2 --> CHROMA_STORE
    API_SERVER2 --> S3_BUCKET

    %% Workers
    WORKER_POOL --> PRIMARY_DB
    WORKER_POOL --> REDIS_CLUSTER
    WORKER_POOL --> CHROMA_STORE

    %% External
    API_SERVER1 --> LLM_API
    API_SERVER2 --> LLM_API
    WORKER_POOL --> LLM_API

    %% Monitoring
    API_SERVER1 --> SENTRY
    API_SERVER1 --> DATADOG
    API_SERVER2 --> SENTRY
    API_SERVER2 --> DATADOG
    WORKER_POOL --> SENTRY
    WORKER_POOL --> DATADOG

    %% Styling
    classDef client fill:#3b82f6,stroke:#1e40af,color:#fff
    classDef cdn fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef compute fill:#ec4899,stroke:#be185d,color:#fff
    classDef data fill:#10b981,stroke:#059669,color:#fff
    classDef external fill:#f59e0b,stroke:#d97706,color:#fff
    classDef observability fill:#6366f1,stroke:#4338ca,color:#fff

    class BROWSER client
    class VERCEL cdn
    class API_SERVER1,API_SERVER2,WORKER_POOL,LOAD_BALANCER compute
    class PRIMARY_DB,REPLICA_DB,REDIS_CLUSTER,CHROMA_STORE,S3_BUCKET data
    class LLM_API external
    class SENTRY,DATADOG observability
```

---

## Legend

- **Blue**: Frontend Layer (Next.js, React)
- **Purple**: Backend Layer (FastAPI, Services)
- **Pink**: AI Layer (LangGraph Agents)
- **Green**: Storage Layer (PostgreSQL, Chroma, Redis, S3)
- **Orange**: Background Jobs (ARQ Workers)
- **Indigo**: External Services (LLM Providers)

## Key Architectural Patterns

1. **Living Narrative Engine**: Pre-planned hidden quests with trigger-based unlocking
2. **Multi-Character AI**: Separate LangGraph agents for each character with personality/memory
3. **Time-Aware World**: Zones open/close based on real-world time with user overrides
4. **Hybrid Communication**: SSE for AI streaming, HTTP REST for user actions
5. **Memory Hierarchy**: Vector storage (Chroma) + Structured storage (PostgreSQL)
6. **Async-First**: FastAPI + ARQ for background jobs + async SQLAlchemy
