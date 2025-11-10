# Decision Summary

| Category               | Decision              | Version               | Affects Epics                     | Rationale                                  |
| ---------------------- | --------------------- | --------------------- | --------------------------------- | ------------------------------------------ |
| **Frontend Framework** | Next.js               | 15.x                  | All frontend epics                | React ecosystem, streaming support, SEO    |
| **UI Library**         | React                 | 19.x                  | All frontend epics                | Latest React features, Server Components   |
| **Component Library**  | shadcn/ui + Radix UI  | Latest                | UI components                     | Copy-paste components, theme customization |
| **Styling**            | Tailwind CSS          | Latest                | All frontend epics                | Utility-first, theme system support        |
| **Animation**          | Framer Motion         | Latest                | Character animations, transitions | Declarative, performant, React-native      |
| **Backend Framework**  | FastAPI               | Latest                | All backend epics                 | Async-first, AI ecosystem integration      |
| **Authentication**     | Clerk                 | Latest                | User auth, onboarding             | Managed auth, OAuth, reduces complexity    |
| **AI Orchestration**   | LangGraph + LangChain | Latest                | Companion, Narrative Engine       | Stateful agents, multi-character support   |
| **AI Models**          | GPT-4o-mini (primary) | Latest                | Chat, personas, quest generation  | Cost-effective, fast, good quality         |
| **Emotion Detection**  | cardiffnlp/roberta    | Latest                | Emotional state tracking          | Open source, multilingual, 7 emotions      |
| **Vector Storage**     | PostgreSQL pgvector   | PG 15+, pgvector 0.5+ | Memory, Companion                 | Unified storage, production-ready          |
| **Database**           | PostgreSQL            | 15+                   | All data persistence              | Production-ready, async support, pgvector  |
| **ORM**                | SQLAlchemy (async)    | 2.0+                  | Data models                       | Async support, mature ecosystem            |
| **Migrations**         | Alembic               | Latest                | Database schema changes           | Industry standard for SQLAlchemy           |
| **Background Jobs**    | ARQ                   | Latest                | Quest generation, nudges          | Async-native, Redis-based                  |
| **Real-Time**          | SSE + WebSocket       | Native                | AI streaming, world updates       | SSE for AI, WebSocket for world state      |
| **File Storage**       | S3-compatible         | -                     | Evidence uploads                  | Scalable, cost-effective                   |
| **Observability**      | Sentry                | Latest                | Error tracking, performance       | Session replay, performance monitoring     |

---
