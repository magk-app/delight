---
title: Architecture Overview
description: Complete technical architecture of the Delight platform
---

# Architecture Overview

Delight is a self-improvement companion platform that blends emotionally-aware AI coaching with narrative world-building. The architecture is designed to support a **living narrative engine** where real-world goal achievement drives personalized story progression, multi-character AI interactions, and adaptive quest systems.

## Key Architectural Approach

- **Frontend:** Next.js 15 + React 19 for modern, performant UI with streaming support
- **Backend:** FastAPI for async-first API layer optimized for AI orchestration
- **AI Layer:** LangGraph + LangChain for stateful multi-agent character system
- **Memory:** PostgreSQL with pgvector extension for unified vector + structured storage
- **Real-Time:** Hybrid SSE + HTTP for AI streaming and user actions, WebSocket for world state updates
- **Novel Patterns:** Living narrative engine, character-initiated interactions, pre-planned hidden quest system

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Frontend Framework | Next.js | 15.x | React ecosystem, streaming support |
| UI Library | React | 19.x | Latest React features, Server Components |
| Backend Framework | FastAPI | Latest | Async-first, AI ecosystem integration |
| Authentication | Clerk | Latest | Managed auth, OAuth |
| AI Orchestration | LangGraph + LangChain | Latest | Stateful agents, multi-character support |
| Database | Supabase (PostgreSQL) | PG 15+ | Managed DB with pgvector |
| Vector Storage | PostgreSQL pgvector | 0.5+ | Unified storage, production-ready |

## System Architecture

```
┌─────────────────┐
│   Next.js UI    │  ← React 19, Tailwind, shadcn/ui
└────────┬────────┘
         │ HTTP/SSE
┌────────▼────────┐
│   FastAPI API   │  ← Async endpoints, auth middleware
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│LangGraph│ │Supabase│  ← AI orchestration + PostgreSQL + pgvector
└────────┘ └────────┘
```

## Core Components

### Frontend (Next.js)
- App Router with Server Components
- Streaming AI responses via SSE
- Real-time world state updates via WebSocket
- Clerk authentication integration

### Backend (FastAPI)
- Async-first API design
- LangGraph state machines for AI agents
- Three-tier memory architecture (personal, project, task)
- Background job processing with ARQ

### AI Layer
- Multi-character system (Eliza companion + narrative characters)
- Emotion-aware responses
- Context-aware quest generation
- Persistent memory across conversations

## Design Principles

1. **Cost Efficiency**: Target <$0.10/user/day operational cost
2. **Emotional Intelligence**: AI adapts to user's emotional state
3. **Narrative Coherence**: Goals become part of a living story
4. **Performance**: Streaming responses, optimized database queries
5. **Scalability**: Async architecture, horizontal scaling ready

## Next Steps

- [Executive Summary](/architecture/executive-summary) - High-level overview
- [Technology Stack Details](/architecture/technology-stack) - Detailed tech decisions
- [Decision Records](/architecture/decision-records) - ADRs explaining choices
- [Data Architecture](/architecture/data-architecture) - Database schema and models
- [API Contracts](/architecture/api-contracts) - API specifications
- [Security Architecture](/architecture/security) - Security design
- [Deployment Architecture](/architecture/deployment) - Hosting strategy

---

For complete architecture documentation, see the [full architecture document](/architecture/overview) in the repository.

