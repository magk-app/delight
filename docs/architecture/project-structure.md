# Project Structure

```
delight/
├── packages/
│   ├── frontend/                    # Next.js 15 application
│   │   ├── src/
│   │   │   ├── app/                 # App Router pages
│   │   │   │   ├── (auth)/          # Auth routes
│   │   │   │   ├── (world)/         # World/zone routes
│   │   │   │   │   ├── arena/
│   │   │   │   │   ├── observatory/
│   │   │   │   │   └── commons/
│   │   │   │   ├── companion/       # Eliza chat interface
│   │   │   │   ├── missions/        # Mission views
│   │   │   │   └── progress/        # Dashboard, DCI
│   │   │   ├── components/
│   │   │   │   ├── ui/              # shadcn/ui components
│   │   │   │   ├── companion/       # Eliza, character components
│   │   │   │   ├── missions/        # Mission cards, progress bars
│   │   │   │   ├── world/           # Zone components, time display
│   │   │   │   └── narrative/       # Story text, dialogue
│   │   │   ├── lib/
│   │   │   │   ├── api/             # API client, SSE handlers
│   │   │   │   ├── hooks/           # React hooks
│   │   │   │   ├── utils/           # Utilities
│   │   │   │   └── themes/          # Theme system (medieval, sci-fi, etc.)
│   │   │   └── types/               # TypeScript types
│   │   ├── public/                  # Static assets
│   │   ├── tailwind.config.ts       # Tailwind + theme config
│   │   └── package.json
│   │
│   ├── backend/                     # FastAPI application
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── companion.py # Eliza chat endpoints
│   │   │   │   │   ├── missions.py  # Mission CRUD
│   │   │   │   │   ├── narrative.py # Story generation
│   │   │   │   │   ├── progress.py  # DCI, analytics
│   │   │   │   │   └── world.py     # World state, zones
│   │   │   │   └── sse.py           # SSE streaming endpoints
│   │   │   ├── core/
│   │   │   │   ├── config.py        # Settings, env vars
│   │   │   │   ├── security.py      # Auth, JWT
│   │   │   │   └── dependencies.py  # FastAPI dependencies
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   │   ├── user.py
│   │   │   │   ├── mission.py
│   │   │   │   ├── character.py
│   │   │   │   ├── narrative.py
│   │   │   │   └── progress.py
│   │   │   ├── schemas/             # Pydantic schemas
│   │   │   │   └── ...
│   │   │   ├── services/
│   │   │   │   ├── companion_service.py    # Eliza orchestration
│   │   │   │   ├── narrative_service.py    # Story generation
│   │   │   │   ├── mission_service.py      # Quest logic
│   │   │   │   ├── memory_service.py       # Chroma integration
│   │   │   │   └── character_service.py    # Character AI
│   │   │   ├── agents/              # LangGraph agents
│   │   │   │   ├── eliza_agent.py   # Main companion agent
│   │   │   │   ├── character_agents.py # Lyra, Thorne, Elara
│   │   │   │   └── narrative_agent.py # Story generation agent
│   │   │   ├── workers/             # ARQ background jobs
│   │   │   │   ├── quest_generator.py
│   │   │   │   ├── nudge_scheduler.py
│   │   │   │   └── memory_consolidation.py
│   │   │   └── db/                  # Database setup
│   │   │       ├── base.py          # Base model, session
│   │   │       └── migrations/      # Alembic migrations
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── pyproject.toml           # Poetry dependencies
│   │   └── .env.example
│   │
│   └── shared/                      # Shared TypeScript types
│       └── types/
│           ├── mission.ts
│           ├── character.ts
│           ├── narrative.ts
│           └── progress.ts
│
├── docs/                            # Documentation
│   ├── architecture.md              # This file
│   ├── product-brief-Delight-2025-11-09.md
│   └── ux-design-specification.md
│
└── docker-compose.yml               # Local dev environment
```

---
