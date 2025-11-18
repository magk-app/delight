# Getting Started with Delight Development

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v20 or higher) - [Download](https://nodejs.org/)
- **pnpm** (v8 or higher) - `npm install -g pnpm`
- **Docker** & **Docker Compose** - [Download](https://www.docker.com/products/docker-desktop)
- **Git** - [Download](https://git-scm.com/)

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/magk/delight.git
cd delight

# Install dependencies
pnpm install
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and configuration
# At minimum, you'll need:
# - DATABASE_URL (will be set automatically when Docker starts)
# - OPENAI_API_KEY or ANTHROPIC_API_KEY for AI features
```

### 3. Start Infrastructure

```bash
# Start all services (PostgreSQL, Redis, Neo4j, Chroma)
pnpm docker:up

# Wait for services to be healthy (about 30 seconds)
# Check status:
docker ps
```

### 4. Initialize Database

```bash
# Navigate to backend package
cd packages/backend

# Run database migrations (once implemented)
pnpm run db:migrate

# Seed initial data (optional)
pnpm run db:seed
```

### 5. Start Development Servers

```bash
# In the root directory, start all packages in development mode
pnpm dev

# This will start:
# - Frontend (Electron app) on http://localhost:5173
# - Backend API on http://localhost:3000
# - AI Agent service (embedded in backend for now)
```

### 6. Open the Application

- The Electron app should open automatically
- Or navigate to http://localhost:5173 in your browser
- Backend API docs: http://localhost:3000/docs (if implemented)

## Project Structure

```
delight/
├── packages/
│   ├── frontend/         # Electron + React app
│   │   ├── src/
│   │   │   ├── components/   # React components
│   │   │   ├── pages/        # Page components
│   │   │   ├── stores/       # Zustand stores
│   │   │   ├── api/          # API client
│   │   │   └── main.ts       # Electron main process
│   │   └── package.json
│   │
│   ├── backend/          # Fastify API server
│   │   ├── src/
│   │   │   ├── routes/       # API routes
│   │   │   ├── services/     # Business logic
│   │   │   ├── db/           # Database schemas & queries
│   │   │   └── index.ts      # Server entry point
│   │   └── package.json
│   │
│   ├── ai-agent/         # AI orchestration & memory
│   │   ├── src/
│   │   │   ├── orchestrator/ # LangGraph workflows
│   │   │   ├── memory/       # Zep integration
│   │   │   ├── tools/        # AI tools (search, etc.)
│   │   │   └── llm/          # LLM router
│   │   └── package.json
│   │
│   ├── game-engine/      # Gamification logic
│   │   ├── src/
│   │   │   ├── xp.ts         # XP & leveling
│   │   │   ├── quests.ts     # Quest generation
│   │   │   ├── world.ts      # World building
│   │   │   └── social.ts     # Social features
│   │   └── package.json
│   │
│   └── shared/           # Shared types & utilities
│       ├── src/
│       │   ├── types/        # TypeScript types
│       │   ├── schemas/      # Zod schemas
│       │   └── utils/        # Utilities
│       └── package.json
│
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md
│   ├── MEMORY_SYSTEM.md
│   ├── AI_ORCHESTRATION.md
│   └── GAMIFICATION.md
│
├── infrastructure/       # Docker, K8s configs
├── scripts/             # Build & deployment scripts
├── docker-compose.yml   # Local dev services
├── package.json         # Root package (workspaces)
└── README.md
```

## Development Workflow

### Running Individual Packages

```bash
# Frontend only
cd packages/frontend
pnpm dev

# Backend only
cd packages/backend
pnpm dev

# AI Agent (usually embedded in backend)
cd packages/ai-agent
pnpm dev
```

### Building for Production

```bash
# Build all packages
pnpm build

# Build specific package
cd packages/frontend
pnpm build
```

### Testing

```bash
# Run all tests
pnpm test

# Run tests in watch mode
cd packages/backend
pnpm test --watch
```

### Linting & Formatting

```bash
# Lint all packages
pnpm lint

# Format all files
pnpm format
```

## Database Management

### Accessing Databases

**PostgreSQL:**

```bash
# Via Docker
docker exec -it delight-postgres psql -U delight -d delight

# Or use a GUI tool like pgAdmin or TablePlus
# Host: localhost, Port: 5432, User: delight, Password: delight_dev_password
```

**Redis:**

```bash
# Via Docker
docker exec -it delight-redis redis-cli

# Or use RedisInsight
```

**Neo4j:**

```bash
# Open browser
http://localhost:7474

# Login: neo4j / delight_dev_password
```

**Chroma (Vector DB):**

```bash
# API endpoint
http://localhost:8000

# View collections
curl http://localhost:8000/api/v1/collections
```

### Migrations

```bash
cd packages/backend

# Create a new migration
pnpm run db:migration:create add_users_table

# Run migrations
pnpm run db:migrate

# Rollback last migration
pnpm run db:rollback
```

## Working with AI Features

### Setting Up LLM Access

1. **OpenAI** (recommended for development):

   - Get an API key from https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=sk-...`

2. **Anthropic Claude** (optional):

   - Get an API key from https://console.anthropic.com/
   - Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

3. **Local LLM** (advanced):
   - Install llama.cpp or vLLM
   - Download a model (e.g., LLaMA 2 70B)
   - Set `LOCAL_LLM_URL` in `.env`

### Testing Memory System

```bash
cd packages/ai-agent

# Test Zep integration
pnpm test src/memory/zep.test.ts

# Test vector search
pnpm test src/memory/vector.test.ts
```

### Testing Orchestration

```bash
# Test a workflow
pnpm test src/orchestrator/workflow.test.ts
```

## Troubleshooting

### Docker Services Won't Start

```bash
# Check if ports are already in use
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :7474  # Neo4j

# Stop all services and restart
pnpm docker:down
pnpm docker:up
```

### Frontend Won't Connect to Backend

- Ensure backend is running on port 3000
- Check CORS configuration in `packages/backend/src/index.ts`
- Verify API URL in frontend config

### Database Connection Errors

- Ensure Docker services are healthy: `docker ps`
- Check `.env` has correct DATABASE_URL
- Verify PostgreSQL is accepting connections: `docker logs delight-postgres`

### Electron App Not Opening

```bash
# Try running directly
cd packages/frontend
pnpm electron:dev

# Check Electron logs
# On macOS: ~/Library/Logs/delight/
# On Windows: %APPDATA%/delight/logs/
```

## Next Steps

1. **Read the Architecture**: Start with [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Explore Roadmap**: See [ROADMAP.md](./ROADMAP.md) for implementation phases
3. **Dive into Subsystems**:
   - [Memory System](./docs/MEMORY_SYSTEM.md)
   - [AI Orchestration](./docs/AI_ORCHESTRATION.md)
   - [Gamification](./docs/GAMIFICATION.md)
4. **Pick a Task**: Check the issues board or ROADMAP for Phase 1 tasks
5. **Join Discussions**: (Add Discord/Slack link if applicable)

## Useful Commands

```bash
# View all Docker logs
docker-compose logs -f

# Clean everything and start fresh
pnpm clean
pnpm docker:down -v  # -v removes volumes
pnpm install
pnpm docker:up
pnpm dev

# Check package interdependencies
pnpm list --depth=1

# Update all dependencies
pnpm update -r --latest

# Generate TypeScript types from Zod schemas
cd packages/shared
pnpm run generate-types
```

## Resources

- [LangChain Documentation](https://js.langchain.com/docs/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraphjs/)
- [Zep Documentation](https://docs.getzep.com/)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Fastify Documentation](https://fastify.dev/)
- [Electron Documentation](https://www.electronjs.org/docs/latest/)
- [Vite Documentation](https://vitejs.dev/)

## Getting Help

- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review code comments
- Ask in community channels

---

Happy coding! 🚀
