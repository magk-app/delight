# Delight - Epic Breakdown

**Author:** Jack
**Date:** 2025-11-10
**Project Level:** Level 2
**Target Scale:** Full project (MVP → Future Vision)

---

## Overview

This document provides the complete epic and story breakdown for Delight, decomposing the requirements from the [Product Brief](./product-brief-Delight-2025-11-09.md) and [Architecture](./architecture.md) into implementable stories.

The breakdown includes **MVP features (P0/P1)** AND **future vision features** to minimize refactoring. Each epic is structured to build the foundation correctly from the start while allowing incremental feature additions.

### Epic Summary

This breakdown follows the 8-epic architecture structure defined in the Architecture document:

**Epic 1: User Onboarding & Foundation**

- **Scope:** Project initialization, auth system, user onboarding flow, monorepo structure
- **Why First:** Establishes foundation for all subsequent work
- **Architecture:** Frontend (Next.js 15), Backend (FastAPI), Database (PostgreSQL + pgvector), deployment pipeline

**Epic 2: Companion & Memory System**

- **Scope:** Eliza AI companion, LangGraph agents, 3-tier memory (personal/project/task), conversational interface
- **Priority:** P0 - Core differentiator
- **Architecture:** LangGraph/LangChain agents, PostgreSQL pgvector, memory service
- **Future:** Multiple character personas, deeper emotional intelligence

**Epic 3: Goal & Mission Management**

- **Scope:** Goal creation/decomposition, priority triads, micro-missions, progress tracking
- **Priority:** P0 - Core productivity loop
- **Architecture:** Mission service, PostgreSQL models, quest generation worker
- **Future:** Collaborative goals, guild missions, advanced quest types

**Epic 4: Narrative Engine**

- **Scope:** Living narrative system, story generation, character-initiated interactions, hidden quests
- **Priority:** P1 MVP → Enhanced post-MVP
- **Architecture:** Narrative service, LangGraph narrative agent, story template system
- **Future:** Multi-character storylines, branching narratives, lore economy

**Epic 5: Progress & Analytics**

- **Scope:** Streaks, DCI dashboard, highlight reels, momentum storytelling
- **Priority:** P1 - Engagement driver
- **Architecture:** Progress service, analytics pipeline, cinematic generation
- **Future:** Advanced analytics, peer comparisons, achievement gallery

**Epic 6: World State & Time System**

- **Scope:** Dynamic world zones (Arena, Observatory, Commons), time-aware state, zone unlocks
- **Priority:** MVP (basic) → Future (full world)
- **Architecture:** World service, WebSocket for real-time updates, zone routing
- **Future:** Full multiplayer zones, shared rituals, world events

**Epic 7: Nudge & Outreach**

- **Scope:** Compassionate nudges (in-app/SMS/email), drop-off detection, opt-in management
- **Priority:** P1 - Retention driver
- **Architecture:** ARQ workers, scheduled jobs, notification service
- **Future:** AI-driven optimal timing, multi-channel coordination

**Epic 8: Evidence & Reflection**

- **Scope:** Evidence uploads (photos/artifacts), reflection prompts, accomplishment validation
- **Priority:** Post-MVP (foundation in MVP)
- **Architecture:** S3 storage, file upload service, evidence review system
- **Future:** AI validation, shared galleries, artifact-based storylines

---

## Epic 1: User Onboarding & Foundation

**Epic Goal:** Establish the technical foundation and user authentication system that enables all subsequent features. This epic sets up the monorepo structure, deployment pipeline, core backend/frontend infrastructure, and basic user onboarding flow.

**Architecture Components:** Next.js 15, FastAPI, PostgreSQL + pgvector, Docker, deployment pipeline, auth system

### Story 1.1: Initialize Monorepo Structure and Core Dependencies

As a **developer**,  
I want **a properly structured monorepo with backend, frontend, and shared packages**,  
So that **the team can work efficiently with proper tooling and dependency management**.

**Acceptance Criteria:**

**Given** I am setting up a new development environment  
**When** I run the initialization commands  
**Then** the monorepo structure is created with:

- `packages/frontend/` with Next.js 15 + TypeScript + Tailwind
- `packages/backend/` with FastAPI + Poetry + async SQLAlchemy
- `packages/shared/` for TypeScript types
- Docker Compose for local PostgreSQL + Redis
- Root package.json with workspace configuration

**And** all core dependencies are installed:

- Frontend: Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui, @clerk/nextjs
- Backend: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL driver (asyncpg), Pydantic, Alembic, clerk-backend-sdk
- AI: LangChain, LangGraph, langchain-postgres, pgvector, transformers (for emotion detection)
- Infrastructure: ARQ, Redis, Sentry

**And** development servers can start successfully:

- `pnpm dev` (frontend at localhost:3000)
- `poetry run uvicorn main:app --reload` (backend at localhost:8000)

**Prerequisites:** None (first story)

**Technical Notes:**

- Use `npx create-next-app@latest` with App Router + TypeScript
- Install Clerk: `npm install @clerk/nextjs`
- Use Poetry for Python dependency management
- Install Clerk backend SDK: `poetry add clerk-backend-sdk`
- Install emotion detection model: `poetry add transformers torch`
- Install pgvector extension in Docker PostgreSQL container
- See Architecture doc lines 29-50 for exact initialization commands

---

### Story 1.2: Set Up Database Schema and Migrations

As a **developer**,  
I want **a versioned database schema with migration tooling**,  
So that **schema changes are tracked and can be applied consistently across environments**.

**Acceptance Criteria:**

**Given** the monorepo is initialized  
**When** I set up the database system  
**Then** Alembic is configured for migrations in `backend/app/db/migrations/`

**And** initial schema includes core tables:

- `users` (id UUID PRIMARY KEY, clerk_user_id VARCHAR UNIQUE, email, timezone, created_at, updated_at)
  - NOTE: clerk_user_id is the primary identifier from Clerk; passwords/sessions managed by Clerk
- `user_preferences` (user_id FK, custom_hours JSONB, theme, communication_preferences JSONB)

**And** pgvector extension is enabled in PostgreSQL

**And** I can run migrations successfully:

- `alembic upgrade head` applies all migrations
- `alembic downgrade -1` rolls back successfully

**Prerequisites:** Story 1.1 (monorepo structure)

**Technical Notes:**

- Use SQLAlchemy 2.0 declarative base with async support
- Install pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;`
- Store migrations in `backend/app/db/migrations/`
- Base models in `backend/app/models/base.py`

---

### Story 1.3: Integrate Clerk Authentication System

As a **new user**,  
I want **to register and log in securely with multiple options**,  
So that **my data is protected and I can use social login or email authentication**.

**Acceptance Criteria:**

**Given** the database schema is set up and Clerk is configured  
**When** I navigate to the app  
**Then** I see the Clerk authentication UI with options to:

- Sign up with email/password
- Sign in with Google OAuth
- Sign in with GitHub OAuth
- Use magic link authentication

**And** when I complete authentication  
**Then** a user record is created in our database with my Clerk user ID

**And** when I make authenticated requests to the backend  
**Then** the backend validates my Clerk session and grants access to protected endpoints

**And** when I log out  
**Then** my Clerk session is invalidated across all devices

**And** the authentication UI matches our app's theme (medieval/modern)

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- **Frontend:** Use `@clerk/nextjs` with App Router middleware
  - Wrap app in `<ClerkProvider>`
  - Protect routes with `middleware.ts` for authentication
  - Use `<SignIn>` and `<SignUp>` components or build custom UI
- **Backend:** Use `clerk-backend-sdk` for session verification
  - Create FastAPI dependency: `get_current_user()` that verifies Clerk session tokens
  - On first authentication, create user record in DB using Clerk webhook
- **Clerk Configuration:**
  - Set up Clerk project at clerk.com
  - Configure OAuth providers (Google, GitHub)
  - Set up webhook endpoint: `POST /api/v1/webhooks/clerk` (user.created, user.updated, user.deleted)
  - Store Clerk API keys in environment variables
- **User Sync:** When Clerk webhook fires for `user.created`, create corresponding user in our DB:

  ```python
  users.create(
      clerk_user_id=clerk_event.data.id,
      email=clerk_event.data.email_addresses[0].email_address,
      timezone="UTC"  # default, updated in onboarding
  )
  ```

- **Cost:** Free tier: 10,000 MAU, then $25/1000 MAU
- **Security:** Clerk handles password hashing, session management, 2FA, breach detection

---

### Story 1.4: Create User Onboarding Flow (MVP)

**⚠️ NOTE:** This story will be moved to later in the development sequence (after Epic 2: Companion & Memory System is complete). Rationale: Onboarding should showcase actual app features, which need to exist first.

As a **new user**,  
I want **a guided onboarding experience**,  
So that **I understand Delight's purpose and can set my initial preferences**.

**Acceptance Criteria:**

**Given** I have just registered  
**When** I complete the onboarding flow  
**Then** I see 3 onboarding screens:

1. Welcome screen explaining Delight's companion concept
2. Timezone and productive hours selection
3. Communication preferences (in-app, email, SMS opt-in)

**And** my preferences are saved to the database

**And** after completion, I am redirected to the companion chat interface

**And** if I close the app mid-onboarding  
**Then** I resume from my last completed step on next login

**Prerequisites:** Story 1.3 (authentication system)

**Technical Notes:**

- Frontend: `frontend/src/app/(auth)/onboarding/` with 3 step pages
- Backend: `POST /api/v1/users/preferences` endpoint
- Store onboarding progress in `user_preferences.onboarding_completed` boolean
- Use React state management for multi-step form
- Mobile-responsive design with Tailwind

---

### Story 1.5: Set Up Deployment Pipeline and Environment Configuration

As a **developer**,  
I want **automated deployment and environment management**,  
So that **we can deploy to staging/production with confidence**.

**Acceptance Criteria:**

**Given** the application is ready for deployment  
**When** I push to the main branch  
**Then** CI/CD pipeline runs:

- Lints frontend (ESLint) and backend (Ruff/Black)
- Runs frontend tests (Jest)
- Runs backend tests (pytest)
- Builds Docker images for backend and frontend
- Deploys to staging environment

**And** environment variables are properly configured:

- `.env.example` files exist for frontend and backend
- Secrets are managed securely (not committed to git)
- Different configs for dev/staging/production

**And** health check endpoints are available:

- `GET /api/v1/health` returns 200 with system status
- Frontend and backend can connect to database and Redis

**Prerequisites:** Stories 1.1-1.4 (all foundation components)

**Technical Notes:**

- Use GitHub Actions or similar CI/CD
- Docker Compose for local dev, separate Dockerfiles for production
- Environment variables: DATABASE_URL, REDIS_URL, JWT_SECRET, LLM_API_KEY
- Health check includes database connection test
- Consider Railway/Render/Fly.io for MVP hosting

---

## Epic 2: Companion & Memory System

**Epic Goal:** Build the emotionally aware AI companion (Eliza) with a 3-tier memory system that enables contextual, empathetic conversations that improve over time.

**Architecture Components:** LangGraph agents, LangChain, PostgreSQL pgvector, memory service, OpenAI/Anthropic LLMs

### Story 2.1: Set Up PostgreSQL pgvector and Memory Schema

As a **developer**,  
I want **vector storage integrated into PostgreSQL for AI memory**,  
So that **we have unified storage for structured and vector data without managing separate databases**.

**Acceptance Criteria:**

**Given** the base database is configured  
**When** I set up the memory system  
**Then** pgvector extension is enabled

**And** memory tables are created:

- `memories` (id, user_id FK, memory_type ENUM[personal/project/task], content TEXT, embedding VECTOR(1536), metadata JSONB, created_at, accessed_at)
- `memory_collections` (id, user_id FK, collection_type, name, description)

**And** vector similarity search works:

- Query with embedding returns top K similar memories
- Supports cosine similarity distance function
- Indexed for performance (HNSW or IVFFlat)

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- Use `pgvector` extension for vector operations
- Embedding dimension: 1536 (OpenAI text-embedding-3-small)
- Create index: `CREATE INDEX ON memories USING hnsw (embedding vector_cosine_ops);`
- memory_type: 'personal' (long-term identity), 'project' (goals/plans), 'task' (missions/actions)
- See Architecture doc Pattern 1 for memory architecture

---

### Story 2.2: Implement Memory Service with 3-Tier Architecture

As a **developer**,  
I want **a memory service that manages personal, project, and task memories**,  
So that **the AI companion can recall relevant context at the right abstraction level**.

**Acceptance Criteria:**

**Given** the memory schema is set up  
**When** I use the memory service  
**Then** I can store memories with automatic embedding generation

**And** I can query memories by type:

- Personal tier: Identity, preferences, emotional patterns (long-term)
- Project tier: Goals, plans, progress snapshots (medium-term)
- Task tier: Mission details, actions taken (short-term, pruned)

**And** I can retrieve relevant memories with hybrid search:

- Semantic search (vector similarity)
- Time-weighted recency boost
- Access frequency tracking

**And** task memories are automatically pruned after 30 days

**Prerequisites:** Story 2.1 (memory schema)

**Technical Notes:**

- Service: `backend/app/services/memory_service.py`
- Methods: `add_memory()`, `query_memories()`, `prune_old_task_memories()`
- Use LangChain `PostgresVectorStore` wrapper or custom implementation
- Implement time decay function: `score * (1 + log(1 + days_since_access)^-1)`
- Background job (ARQ) for pruning task memories

---

### Story 2.3: Build Eliza Agent with LangGraph

As a **developer**,  
I want **a stateful LangGraph agent for the Eliza companion**,  
So that **conversations maintain state and can execute multi-step reasoning**.

**Acceptance Criteria:**

**Given** the memory service is implemented  
**When** I create the Eliza agent  
**Then** the agent is defined as a LangGraph state machine with nodes:

- `receive_input`: Parse user message
- `recall_context`: Query relevant memories
- `reason`: LLM processes input + context
- `respond`: Generate empathetic response
- `store_memory`: Save conversation to memory

**And** the agent maintains conversation state across messages

**And** the agent can access memory tiers strategically:

- Always queries personal tier for identity/preferences
- Queries project tier when discussing goals
- Queries task tier for recent action context

**Prerequisites:** Story 2.2 (memory service)

**Technical Notes:**

- Agent: `backend/app/agents/eliza_agent.py`
- Use LangGraph `StateGraph` with typed state
- System prompt emphasizes empathy, emotional intelligence, coaching tone
- **LLM:** OpenAI GPT-4o-mini (cost-effective, fast, sufficient quality)
  - Cost: $0.15/$0.60 per 1M tokens (input/output)
  - Fallback to GPT-4o if response quality issues arise
- State includes: `messages`, `user_context`, `retrieved_memories`, `emotional_state`

---

### Story 2.4: Create Companion Chat API with SSE Streaming

As a **user**,  
I want **to have a conversation with Eliza that streams responses in real-time**,  
So that **the interaction feels natural and responsive**.

**Acceptance Criteria:**

**Given** the Eliza agent is built  
**When** I send a message to the companion  
**Then** the backend streams the response token-by-token using SSE

**And** the response includes emotional awareness:

- Acknowledges my stated feelings
- Asks clarifying questions when I'm vague
- Offers grounding suggestions when I seem overwhelmed

**And** the conversation history is persisted:

- Messages stored in database
- Context maintained across sessions
- Memory updated after each exchange

**And** the API endpoints are:

- `POST /api/v1/companion/chat` (trigger conversation)
- `GET /api/v1/sse/companion/stream/{conversation_id}` (SSE stream)

**Prerequisites:** Story 2.3 (Eliza agent)

**Technical Notes:**

- Use FastAPI `StreamingResponse` with SSE format
- Frontend uses EventSource or fetch with streaming
- Store conversations in `conversations` table (id, user_id, messages JSONB, started_at)
- Stream format: `data: {"token": "text", "type": "content"}\n\n`
- Handle connection drops gracefully

---

### Story 2.5: Build Companion Chat UI (Frontend)

As a **user**,  
I want **a beautiful, responsive chat interface to talk with Eliza**,  
So that **I feel comfortable sharing my goals and feelings**.

**Acceptance Criteria:**

**Given** the chat API is working  
**When** I open the companion interface  
**Then** I see a chat interface with:

- Message history (scrollable)
- Input field with send button
- Eliza's messages stream in character-by-character
- My messages appear immediately

**And** the UI shows Eliza's presence:

- Animated breathing effect when idle
- Typing indicator while thinking
- Smooth message animations

**And** the interface is responsive:

- Works on mobile and desktop
- Accessible (keyboard navigation, screen reader support)
- Uses Tailwind + shadcn/ui components

**Prerequisites:** Story 2.4 (chat API)

**Technical Notes:**

- Component: `frontend/src/components/companion/CompanionChat.tsx`
- Route: `frontend/src/app/companion/page.tsx`
- Use React hooks: `useState`, `useEffect` for SSE connection
- Use Framer Motion for animations
- Auto-scroll to latest message
- Store conversation ID in session storage

---

### Story 2.6: Implement Emotional State Detection with Open Source Model

**⚠️ CRITICAL FEATURE** - This is highly important for emotional intelligence.

As a **user**,  
I want **Eliza to sense when I'm overwhelmed, joyful, or stuck**,  
So that **she can offer timely support and celebrate wins with me**.

**Acceptance Criteria:**

**Given** I'm having a conversation with Eliza  
**When** my messages indicate emotional states  
**Then** Eliza detects emotions using the open source model with 7 emotion categories:

- Joy, Anger, Sadness, Fear, Love, Surprise, Neutral

**And** she responds appropriately based on detected emotion:

- **Overwhelm/Fear:** Offers calming ritual (breathing exercise, reflection prompt)
- **Sadness/Anger:** Empathetic acknowledgment, suggests breaking down goals
- **Joy/Love:** Celebrates wins, encourages momentum
- **Neutral:** Normal conversational flow

**And** emotional state is tracked in user preferences:

- `current_emotional_state` JSONB with scores for each emotion
- `dominant_emotion` VARCHAR (the highest scoring emotion)
- `last_state_change` timestamp
- Influences mission difficulty and nudge timing

**And** emotion detection is fast (< 100ms per message) and privacy-preserving (self-hosted)

**Prerequisites:** Story 2.4 (chat API)

**Technical Notes:**

- **Model:** `cardiffnlp/twitter-roberta-base-emotion-multilingual-latest` (Hugging Face)
  - 400K+ downloads, actively maintained
  - Fast inference (~50ms on CPU)
  - Multilingual support
  - 7 emotion classification: joy, anger, sadness, fear, love, surprise, neutral
- **Service:** `backend/app/services/emotion_service.py`

  ```python
  from transformers import pipeline

  emotion_classifier = pipeline(
      "text-classification",
      model="cardiffnlp/twitter-roberta-base-emotion-multilingual-latest",
      return_all_scores=True
  )

  def detect_emotion(text: str) -> dict:
      """Returns emotion scores: {joy: 0.8, anger: 0.1, ...}"""
      results = emotion_classifier(text)[0]
      return {r['label']: r['score'] for r in results}
  ```

- **Integration with Eliza:**

  - Call emotion detection in `receive_input` node of LangGraph agent
  - Pass emotion context to `reason` node for appropriate response
  - Update `user_preferences.current_emotional_state` after each message

- **Deployment:**

  - MVP: Use Hugging Face Inference API (free tier: 1000 req/day)
  - Production: Self-host model on backend (requires ~500MB model + PyTorch)
  - Model loading: Cache in memory on server startup

- **Privacy:** User messages never leave infrastructure (when self-hosted)
- **Cost:** Free after infrastructure (no per-request API costs)

---

### Story 2.7: Add Multiple Character Personas (Future)

**⚠️ CRITICAL DISTINCTION:** Eliza (AI companion) is fundamentally different from character personas. This system allows creating multiple distinct narrative characters that users interact with.

As a **user**,  
I want **to interact with different narrative AI characters beyond Eliza**,  
So that **I get specialized guidance and story experiences for different goal types and world zones**.

**Acceptance Criteria:**

**Given** I've progressed in my journey  
**When** I unlock new zones or achieve milestones  
**Then** I meet new narrative characters:

- Lyra (Craft/creativity mentor, Arena)
- Thorne (Health/physical mentor, Arena)
- Elara (Growth/learning mentor, Observatory)

**And** each character has distinct:

- **Personality** (defined in system prompts, different from Eliza's empathetic coach persona)
- **Conversation style** (e.g., Lyra is artistic/poetic, Thorne is direct/practical)
- **Areas of expertise** (aligned with specific attributes)
- **Relationship level** (grows with interactions, unlocks deeper conversations)
- **Visual representation** (character avatar/theme distinct from Eliza)

**And** the system supports creating new character personas:

- Admin/system can define new characters via configuration
- Each persona has customizable personality prompts
- Personas tied to narrative scenarios (medieval, sci-fi, etc.)

**And** characters can initiate conversations:

- ARQ worker monitors user focus areas
- Character appears when relevant (e.g., Lyra after 2 weeks of craft missions)
- User receives notification: "Lyra seeks you in the Arena"
- Initiated conversations have narrative context (not just general chat)

**Prerequisites:** Story 2.4 (chat API), Story 6.2 (world zones)

**Technical Notes:**

- Agents: `backend/app/agents/character_agents.py`
- Schema: `characters` table (id, name, persona_type ENUM[companion|narrative], personality_prompt, relationship_level, scenario_id FK)
  - Eliza is `persona_type='companion'` (persistent, always available)
  - Other characters are `persona_type='narrative'` (zone-specific, story-driven)
- Worker: `backend/app/workers/character_initiator.py`
- Each character gets own memory namespace (separate from Eliza's memories)
- **LLM:** GPT-4o-mini for character conversations (consistent with Eliza)
- See Architecture Pattern 2 for multi-character system
- **Key Distinction:** Eliza = your personal companion/coach; Character personas = story NPCs you interact with in the world

---

## Epic 3: Goal & Mission Management

**Epic Goal:** Enable users to create ambitious goals, decompose them collaboratively with Eliza, and work through adaptive micro-missions that respect their energy and time constraints.

**Architecture Components:** Mission service, PostgreSQL models, quest generation worker (ARQ), priority triage system

### Story 3.1: Create Goal Data Models and CRUD APIs

As a **user**,  
I want **to create and manage long-term goals**,  
So that **I have a clear vision of what I'm working toward**.

**Acceptance Criteria:**

**Given** I'm logged in  
**When** I create a new goal  
**Then** the goal is stored with:

- Title and description
- Goal type (abstract/concrete, MVP distinction)
- Value category (health/craft/growth/connection)
- Target completion date (optional)
- Status (active/paused/completed/archived)

**And** I can perform CRUD operations:

- `POST /api/v1/goals` - Create goal
- `GET /api/v1/goals` - List my goals
- `GET /api/v1/goals/{id}` - Get goal details
- `PATCH /api/v1/goals/{id}` - Update goal
- `DELETE /api/v1/goals/{id}` - Archive goal

**And** goals are linked to my user account

**Prerequisites:** Story 1.3 (authentication)

**Technical Notes:**

- Model: `backend/app/models/goal.py`
- Schema: `goals` table (id, user_id FK, title, description, goal_type, value_category, target_date, status, created_at, updated_at)
- Service: `backend/app/services/goal_service.py`
- Value categories align with Product Brief persona needs

---

### Story 3.2: Implement Collaborative Goal Decomposition with Eliza

As a **user**,  
I want **Eliza to help me break down big goals into actionable steps**,  
So that **abstract ambitions become concrete plans**.

**Acceptance Criteria:**

**Given** I've created a goal  
**When** I ask Eliza to help me plan  
**Then** Eliza initiates a collaborative decomposition conversation:

- Asks clarifying questions about my "why"
- Explores constraints (time, resources, dependencies)
- Proposes 3-7 milestone steps

**And** Eliza generates suggested micro-quests:

- Each quest is small (10-30 minutes)
- Quests are sequenced logically
- Energy/time estimates included

**And** I can approve, modify, or reject suggestions

**And** approved quests are saved as missions linked to the goal

**Prerequisites:** Story 2.4 (Eliza chat), Story 3.1 (goal models)

**Technical Notes:**

- Extend Eliza agent with goal decomposition node
- Use structured output parsing for quest suggestions
- Store decomposition in `goal_decompositions` table (goal_id FK, milestones JSONB, generated_quests JSONB)
- Frontend: modal or dedicated page for goal planning session

---

### Story 3.3: Build Mission/Quest System with Priority Triads

As a **user**,  
I want **to see 3 prioritized missions each day**,  
So that **I'm not overwhelmed and can choose what fits my current energy**.

**Acceptance Criteria:**

**Given** I have multiple active goals with missions  
**When** I open the missions view  
**Then** I see 3 missions presented as a "priority triad":

- High priority (urgent + important)
- Medium priority (important, less urgent)
- Low priority (easy win or exploratory)

**And** each mission shows:

- Title and description
- Estimated time (10min, 30min, 1hr)
- Energy level (low/medium/high)
- Value category icon (health/craft/growth/connection)
- Parent goal

**And** I can:

- Choose one mission to start
- Defer a mission to later
- Mark mission as completed

**And** the triad refreshes when I complete or defer missions

**Prerequisites:** Story 3.2 (missions generated)

**Technical Notes:**

- Model: `backend/app/models/mission.py`
- Schema: `missions` table (id, goal_id FK, user_id FK, title, description, estimated_minutes, energy_level, value_category, priority_score, status, created_at, completed_at)
- Prioritization algorithm considers: goal importance, time since last work, energy match, value diversity
- Frontend component: `MissionTriad.tsx`

---

### Story 3.4: Implement Mission Execution Flow with Timer

As a **user**,  
I want **to work on a mission with a gentle timer and focus support**,  
So that **I stay on track without feeling pressured**.

**Acceptance Criteria:**

**Given** I've selected a mission to work on  
**When** I start the mission  
**Then** a timer begins based on estimated duration

**And** the UI shows:

- Mission details prominently
- Timer (optional to hide)
- "I'm done" button (can complete early)
- "Extend time" option if I need more

**And** when the timer ends:

- Gentle notification (no aggressive alarm)
- Prompt to mark as complete or extend
- Option to log actual time spent

**And** when I complete the mission:

- Celebration animation
- Streak updated (if applicable)
- Eliza offers encouragement
- Next mission suggestion appears

**Prerequisites:** Story 3.3 (mission triads)

**Technical Notes:**

- Frontend: `MissionExecutor.tsx` component
- Store session data in `mission_sessions` table (mission_id FK, started_at, completed_at, actual_minutes, notes)
- Use browser timer (Notification API for gentle alerts)
- Post-completion: update mission status, trigger analytics event

---

### Story 3.5: Add Mission Session Notes and Reflection

As a **user**,  
I want **to capture quick notes during or after a mission**,  
So that **I can track learnings and progress details**.

**Acceptance Criteria:**

**Given** I'm working on or just completed a mission  
**When** I add notes  
**Then** notes are saved to the mission session

**And** notes become memory entries:

- Stored in task-tier memory (30-day retention)
- Eliza can recall them in future conversations

**And** I can view past mission notes:

- In mission history
- In goal progress view

**Prerequisites:** Story 3.4 (mission execution), Story 2.2 (memory service)

**Technical Notes:**

- Add `notes` TEXT field to `mission_sessions` table
- Automatically create task memory from notes after mission completion
- Frontend: expandable text area in mission completion modal

---

### Story 3.6: Implement Adaptive Quest Generation Worker (Future)

As a **user**,  
I want **new missions to be generated automatically based on my patterns**,  
So that **I don't run out of things to work on**.

**Acceptance Criteria:**

**Given** I'm actively working on goals  
**When** my mission queue drops below 5 pending missions  
**Then** ARQ worker triggers quest generation

**And** the worker:

- Analyzes my completion patterns (time of day, duration, value categories)
- Queries Eliza agent for new quest ideas
- Generates 3-5 new missions aligned with active goals
- Prioritizes based on goal deadlines and value diversity

**And** generated missions appear in my mission pool

**Prerequisites:** Story 3.3 (missions), Story 2.3 (Eliza agent)

**Technical Notes:**

- Worker: `backend/app/workers/quest_generator.py`
- Schedule: runs nightly + on-demand when queue low
- Uses LangGraph agent with goal context and user patterns
- Ensures diversity: don't generate all missions for one goal

---

### Story 3.7: Add Collaborative Goals and Guild Missions (Future)

As a **user**,  
I want **to work on goals with friends or accountability pods**,  
So that **we support each other and share progress**.

**Acceptance Criteria:**

**Given** I'm in an accountability pod or guild  
**When** we create a shared goal  
**Then** all pod members can:

- See the shared goal
- Contribute missions toward it
- View each other's progress
- Celebrate milestones together

**And** guild missions are available:

- Special quests that require multiple people
- Reward points go to the guild
- Unlocks shared rewards or lore

**Prerequisites:** Story 3.3 (missions), Future multiplayer system

**Technical Notes:**

- Schema: `shared_goals` table (goal_id FK, pod_id FK, member_contributions JSONB)
- Schema: `pods` table (id, name, members ARRAY, created_at)
- Requires notification system to alert pod members
- Future Epic 6 (world/multiplayer) dependency

---

## Epic 4: Narrative Engine

**Epic Goal:** Create a living narrative system that generates personalized stories adapting to real-world user progress, with pre-planned hidden quests that unlock based on achievements.

**Architecture Components:** Narrative service, LangGraph narrative agent, PostgreSQL JSONB for scenario templates, ARQ worker for quest unlocking

### Story 4.1: Create Comprehensive Narrative State Schema and Scenario Templates

**⚠️ COMPREHENSIVE SYSTEM:** This narrative state must be far more extensive than typical story systems - it tracks the entire world state including locations, events, persons, and items.

As a **developer**,  
I want **a flexible, comprehensive schema for narrative scenarios and dynamic world state**,  
So that **we can support multiple themes and maintain story consistency across all narrative elements**.

**Acceptance Criteria:**

**Given** the database is set up  
**When** I create narrative infrastructure  
**Then** the following tables exist:

- `scenario_templates` (id, name, theme, narrative_arc JSONB, character_prompts JSONB, hidden_quests JSONB, time_rules JSONB, world_schema JSONB)
- `narrative_states` (id, user_id FK, scenario_id FK, current_chapter INT, unlocked_quests ARRAY, story_progress JSONB, world_state JSONB, created_at, updated_at)

**And** the `world_state` JSONB tracks comprehensive narrative elements:

```json
{
  "locations": {
    "arena": {
      "discovered": true,
      "description": "...",
      "npcs_present": ["Lyra", "Thorne"]
    },
    "observatory": { "discovered": false, "unlock_condition": "..." }
  },
  "events": [
    {
      "event_id": "first_meeting_lyra",
      "occurred_at": "2025-11-01",
      "impact": "relationship+1"
    }
  ],
  "persons": {
    "Lyra": {
      "relationship_level": 3,
      "last_interaction": "...",
      "knows_about": ["user_craft_goals"]
    },
    "Thorne": { "relationship_level": 1, "status": "neutral" }
  },
  "items": {
    "essence": 450,
    "titles": ["The Persistent", "The Relentless"],
    "artifacts": [
      { "id": "medallion_of_craft", "acquired_at": "...", "description": "..." }
    ]
  },
  "world_time": {
    "current_act": 1,
    "current_chapter": 3,
    "days_in_story": 45
  }
}
```

**And** at least one comprehensive scenario template is seeded:

- **Modern Reality**: Contemporary alter-ego journey with realistic characters
- Defines 3 acts with progression triggers
- Includes 3-5 hidden quest templates
- Defines all possible locations, persons, items, and event types

**And** scenario templates support multiple themes (medieval, sci-fi, etc.) for future expansion

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- See Architecture doc Pattern 1 (Living Narrative Engine) for schema details
- JSONB structure allows flexibility without schema migrations for new scenarios
- **World State Management:** Each narrative generation reads and updates world_state
- **Consistency Enforcement:** Narrative agent validates all changes against scenario template rules
- Index on `narrative_states.user_id` and `scenario_templates.theme`
- Seed script: `backend/app/db/seeds/scenario_templates.py`
- **Critical:** World state must prevent inconsistencies (e.g., can't reference items not yet acquired, locations not yet discovered)

---

### Story 4.2: Build Narrative Generation Agent with LangGraph

As a **developer**,  
I want **an AI agent that generates personalized story beats**,  
So that **users experience adaptive narratives tied to their real actions**.

**Acceptance Criteria:**

**Given** the scenario templates exist  
**When** I initialize the narrative agent  
**Then** the agent is a LangGraph state machine with nodes:

- `assess_progress`: Analyzes user mission completions, streaks, value focus
- `select_beat`: Chooses appropriate story beat based on progress
- `generate_content`: LLM creates personalized narrative text
- `check_unlocks`: Determines if hidden quests should unlock

**And** the agent uses:

- Scenario template context
- User's mission history
- Current chapter/act state
- Character relationship levels

**And** generated content includes:

- Story text (200-400 words)
- Emotional tone
- Character dialogue
- Optional quest unlock

**Prerequisites:** Story 4.1 (narrative schema), Story 2.3 (LangGraph setup)

**Technical Notes:**

- Agent: `backend/app/agents/narrative_agent.py`
- Uses scenario template as base context
- Incorporates real user data (goals, completed missions, streaks)
- **LLM:** OpenAI GPT-4o (premium model for high-quality narrative writing)
  - Cost: $2.50/$10 per 1M tokens (input/output)
  - Rationale: Narrative generation requires superior writing quality and story consistency
  - Less frequent than chat interactions (~2-3 story beats per week per user)
  - Budget impact: ~$0.02/user/day (within $0.50 target)
- **Story Consistency Priority:** Most important theme - ensure no inconsistent values, items, or events
  - Agent maintains strict adherence to scenario template rules
  - Validates against previous story beats before generation
  - Tracks all narrative elements (locations, items, events, character states) in JSONB
- Output format: structured JSON with text, metadata, unlock flags

---

### Story 4.3: Implement Pre-Planned Hidden Quest System

As a **user**,  
I want **to discover surprise quests that unlock when I hit milestones**,  
So that **my journey feels rewarding and full of delightful discoveries**.

**Acceptance Criteria:**

**Given** I'm working through my story  
**When** I complete a trigger condition (e.g., 20-day streak, 50 missions)  
**Then** a hidden quest unlocks

**And** I receive a notification:

- In-app alert with story context
- Message from Eliza explaining the quest
- Quest appears in my mission pool marked as "Special"

**And** hidden quests have:

- Unique rewards (Essence points, titles, relationship boosts)
- Narrative significance (advances story arc)
- Time limits (optional, creates urgency)

**And** the ARQ worker checks trigger conditions:

- Runs nightly
- Checks all active users' progress against scenario hidden_quests
- Unlocks quests when conditions met

**Prerequisites:** Story 4.1 (narrative schema), Story 3.3 (missions)

**Technical Notes:**

- Worker: `backend/app/workers/quest_generator.py` (extend for hidden quests)
- Trigger examples: `{"streak_days": 20, "attribute": "craft"}`, `{"missions_completed": 50}`
- Store unlocked quests in `narrative_states.unlocked_quests` ARRAY
- Frontend: special UI treatment for hidden/special quests

---

### Story 4.4: Create Story Viewing Interface (MVP)

As a **user**,  
I want **to read my personalized story as it unfolds**,  
So that **I feel like my efforts are building toward something meaningful**.

**Acceptance Criteria:**

**Given** narrative content has been generated  
**When** I open the story view  
**Then** I see:

- Current chapter/act title
- Latest story beat (newest at top)
- Previous beats in chronological order
- Visual indicators for act progression

**And** the interface feels immersive:

- Beautiful typography (serif font for story text)
- Theme-appropriate styling (based on scenario)
- Fade-in animations for new beats
- Option to listen (text-to-speech, future)

**And** I can:

- Navigate between chapters
- Bookmark favorite moments
- Share story highlights (opt-in)

**Prerequisites:** Story 4.2 (narrative generation)

**Technical Notes:**

- Frontend: `frontend/src/app/narrative/page.tsx`
- Component: `StoryBeat.tsx`, `ChapterNav.tsx`
- API: `GET /api/v1/narrative/story` returns all story beats
- Use Framer Motion for smooth transitions
- Store read progress in session

---

### Story 4.5: Implement Character-Initiated Story Events (Future)

As a **user**,  
I want **characters to reach out to me with story developments**,  
So that **the narrative feels alive and characters have agency**.

**Acceptance Criteria:**

**Given** I've progressed through several story chapters  
**When** a narrative trigger occurs  
**Then** a character initiates contact:

- Push notification or email (if opted in)
- In-app message: "Lyra has a message for you"
- Character shares story development when I open

**And** character-initiated events include:

- Story revelations
- Relationship milestones
- Warnings or advice
- Celebration of achievements

**And** events are scheduled strategically:

- Based on optimal engagement times
- Not during user-designated quiet hours
- Spaced appropriately (not spammy)

**Prerequisites:** Story 4.2 (narrative agent), Story 2.7 (character personas), Story 7.2 (nudge system)

**Technical Notes:**

- Worker: `backend/app/workers/character_initiator.py`
- Uses nudge system infrastructure (Epic 7)
- Stores pending events in `narrative_events` table
- Frontend: special treatment for character-initiated messages in companion interface

---

### Story 4.6: Add Branching Narratives Based on User Choices (Future)

As a **user**,  
I want **my choices to influence the story direction**,  
So that **the narrative feels personalized and consequential**.

**Acceptance Criteria:**

**Given** I'm at a story decision point  
**When** Eliza or another character presents choices  
**Then** I can select from 2-3 meaningful options:

- Different value focus (health vs craft vs growth)
- Risk vs safety approach
- Solo vs collaborative path

**And** my choice:

- Is stored in narrative state
- Influences future story beats
- Affects character relationships
- May unlock different hidden quests

**And** the narrative agent:

- Tracks decision history
- Generates content consistent with past choices
- Creates story coherence across branches

**Prerequisites:** Story 4.2 (narrative agent), Story 4.4 (story interface)

**Technical Notes:**

- Extend scenario templates with branch points
- Store choices in `narrative_states.story_progress.decisions` JSONB
- Narrative agent queries decision history when generating beats
- Frontend: choice modal with consequence preview

---

### Story 4.7: Implement Lore Economy and Unlockable Content (Future)

As a **user**,  
I want **to unlock deeper lore and world-building through consistent effort**,  
So that **long-term commitment feels rewarding beyond just streaks**.

**Acceptance Criteria:**

**Given** I've been consistent for weeks/months  
**When** I earn Essence points (narrative currency)  
**Then** I can unlock:

- Extended character backstories
- World history codex entries
- Alternate scenario themes
- Cosmetic customizations (avatars, themes)

**And** lore is presented beautifully:

- Codex interface with categories
- Illustrated entries (future: AI-generated art)
- Audio narration (future)

**And** Essence is earned through:

- Hidden quest completions
- Streak milestones
- Goal achievements
- Story chapter completions

**Prerequisites:** Story 4.3 (hidden quests), Story 5.1 (progress tracking)

**Technical Notes:**

- Schema: `lore_entries` table (id, scenario_id FK, category, title, content, unlock_cost, rarity)
- Schema: `user_unlocks` table (user_id FK, lore_entry_id FK, unlocked_at)
- Track Essence in `user_preferences.essence_balance`
- Frontend: codex interface similar to game wikis

---

## Epic 5: Progress & Analytics

**Epic Goal:** Build momentum storytelling through streaks, highlight reels, and the Daily Consistency Index (DCI) dashboard so users see their progress compounding over time.

**Architecture Components:** Progress service, analytics pipeline, PostgreSQL for metrics, frontend dashboards

### Story 5.1: Implement Streak Tracking System

As a **user**,  
I want **to build and maintain streaks for consistent work**,  
So that **I feel motivated to show up daily**.

**Acceptance Criteria:**

**Given** I'm working on missions  
**When** I complete at least one mission on consecutive days  
**Then** my streak counter increments

**And** I can see my current streak:

- Total days count
- Start date
- Value category streaks (health/craft/growth/connection separately)

**And** when I miss a day:

- Streak resets (or uses "streak freeze" if available)
- I'm notified compassionately (not shaming)

**And** streak milestones are celebrated:

- 7 days, 14 days, 30 days, 100 days, 365 days
- Badge/achievement unlocked
- Eliza congratulates me

**Prerequisites:** Story 3.4 (mission completion tracking)

**Technical Notes:**

- Schema: `streaks` table (user_id FK, streak_type ENUM[overall/health/craft/growth/connection], current_streak INT, longest_streak INT, last_activity_date DATE, streak_freeze_available BOOLEAN)
- Calculate daily: ARQ worker checks if user completed mission yesterday
- Frontend: prominent streak display in header/dashboard
- MVP: no streak freeze, add in future

---

### Story 5.2: Build Daily Consistency Index (DCI) Dashboard

As a **user**,  
I want **a quantitative measure of my overall consistency**,  
So that **I can see patterns and understand what's working**.

**Acceptance Criteria:**

**Given** I have at least 7 days of activity  
**When** I view the DCI dashboard  
**Then** I see my Daily Consistency Index score (0-1.0):

- Calculated from: streak, mission completion rate, goal engagement, nudge responses
- Shown as percentage (e.g., "DCI: 73%")
- Color-coded (red/yellow/green zones)

**And** I see trend visualizations:

- 7-day, 30-day, 90-day views
- Line chart of DCI over time
- Breakdown by value category

**And** I get insights:

- "You're most consistent with Health missions (82%)"
- "Your DCI peaks on Tuesday mornings"
- "20% improvement since last month"

**Prerequisites:** Story 5.1 (streak tracking), Story 3.4 (mission sessions)

**Technical Notes:**

- Service: `backend/app/services/progress_service.py`
- DCI formula: `weighted_average(streak_factor, completion_rate, engagement_depth, response_rate)`
- Store daily DCI snapshots in `dci_history` table for trend analysis
- Frontend: `frontend/src/app/progress/page.tsx`
- Use Chart.js or Recharts for visualizations

---

### Story 5.3: Generate Highlight Reels (MVP)

As a **user**,  
I want **cinematic summaries of my accomplishments**,  
So that **I can celebrate progress and share my journey**.

**Acceptance Criteria:**

**Given** I've completed significant milestones (goal completed, 7-day streak, chapter unlock)  
**When** a highlight reel is generated  
**Then** I see a beautiful summary including:

- Title: "Your 7-Day Journey in Craft"
- Key accomplishments listed
- Motivational quote or Eliza message
- Stats: missions completed, time invested, streak maintained

**And** the reel has visual polish:

- Animated transitions
- Value category colors/icons
- Timeline visualization
- Optional: music/sound effects (future)

**And** I can:

- View past highlight reels
- Export as image/PDF
- Share to social media (opt-in, privacy-aware)

**Prerequisites:** Story 5.1 (streaks), Story 3.4 (mission completion data)

**Technical Notes:**

- Service: `backend/app/services/highlight_service.py`
- Trigger: ARQ worker generates reels on milestone events
- Store in `highlight_reels` table (user_id FK, milestone_type, content JSONB, generated_at)
- Frontend: `HighlightReel.tsx` component with Framer Motion animations
- MVP: text+data reels; future: video generation with AI narration

---

### Story 5.4: Implement Progress Snapshots and Goal Timelines

As a **user**,  
I want **to see visual timelines of my goal progress**,  
So that **I can track momentum toward long-term objectives**.

**Acceptance Criteria:**

**Given** I have active goals  
**When** I view a goal's progress page  
**Then** I see:

- Timeline of all missions completed for that goal
- Milestones marked on timeline
- Velocity chart (missions/week over time)
- Estimated completion date based on current pace

**And** I can:

- Filter by date range
- See notes from each mission session
- Identify gaps (periods of inactivity)

**And** progress snapshots are stored weekly:

- Captures goal state every Sunday
- Allows historical comparison ("4 weeks ago vs now")

**Prerequisites:** Story 3.1 (goals), Story 3.4 (mission sessions)

**Technical Notes:**

- Schema: `progress_snapshots` table (goal_id FK, snapshot_date DATE, missions_completed INT, completion_percentage FLOAT, velocity FLOAT, notes TEXT)
- ARQ worker: runs weekly to create snapshots
- Frontend: `GoalTimeline.tsx` with interactive chart
- Use date-fns for date calculations

---

### Story 5.5: Add "What's Working" Analytics Insights (Future)

As a **user**,  
I want **AI-generated insights about my productivity patterns**,  
So that **I can optimize when and how I work**.

**Acceptance Criteria:**

**Given** I have at least 30 days of data  
**When** I view analytics insights  
**Then** I see personalized observations:

- "You complete 3x more missions on Tuesday mornings"
- "Health missions after 8am have 90% completion rate"
- "Your streaks break most often on Fridays"
- "Missions under 20min have highest completion rate"

**And** Eliza uses insights to:

- Recommend optimal mission times
- Adjust mission difficulty
- Suggest scheduling changes

**And** insights are updated monthly

**Prerequisites:** Story 5.2 (DCI dashboard with analytics data)

**Technical Notes:**

- Use LLM to generate natural language insights from analytics data
- Store in `user_insights` table with timestamps
- Pattern detection: time-of-day analysis, day-of-week trends, mission length preferences
- Privacy: insights never leave user's data context

---

### Story 5.6: Implement Achievement Gallery and Badges (Future)

As a **user**,  
I want **to collect badges and achievements for milestones**,  
So that **long-term progress feels tangibly rewarding**.

**Acceptance Criteria:**

**Given** I reach various milestones  
**When** I unlock achievements  
**Then** I receive badges such as:

- **The Starter**: Complete first mission
- **Week Warrior**: 7-day streak
- **Century**: 100 missions completed
- **The Relentless**: 20-day streak in one value category
- **Master Planner**: Decompose 10 goals with Eliza

**And** badges are displayed:

- In my profile/progress page
- Shareable on social media
- Visible to pod members (if in multiplayer)

**And** achievements come in tiers:

- Bronze, Silver, Gold, Platinum
- Unlocking higher tiers grants Essence

**Prerequisites:** Story 5.1 (milestones), Story 4.7 (Essence economy)

**Technical Notes:**

- Schema: `achievements` table (id, name, description, tier, unlock_criteria JSONB, icon_url)
- Schema: `user_achievements` table (user_id FK, achievement_id FK, unlocked_at, tier)
- Define achievement criteria in seed data
- Worker checks criteria daily
- Frontend: badge gallery with filters and search

---

## Epic 6: World State & Time System

**Epic Goal:** Create dynamic world zones (Arena, Observatory, Commons) with time-aware availability and presence, building the foundation for future multiplayer features.

**Architecture Components:** World service, Redis cache, WebSocket for real-time updates, time rules engine

### Story 6.1: Implement Time-Aware State Engine

As a **developer**,  
I want **a time-based rules engine for world state**,  
So that **zone availability and events can change based on user's time and productive hours**.

**Acceptance Criteria:**

**Given** the system is set up  
**When** I query world state for a user  
**Then** the engine applies time rules:

- Default rules: Arena closes 9pm-6am (user's local time)
- User overrides: Custom productive hours from onboarding
- Timezone-aware: All times in user's timezone

**And** the engine caches state in Redis:

- Cache key: `world_state:{user_id}`
- TTL: 15 minutes
- Includes: zone availability, character presence, time-based events

**And** the state updates automatically:

- ARQ worker runs every 15 minutes
- Checks all active users' time rules
- Updates Redis cache

**Prerequisites:** Story 1.4 (user preferences with timezone)

**Technical Notes:**

- Service: `backend/app/services/world_service.py`
- Use `pytz` for timezone handling
- Schema: add `time_rules JSONB` to `user_preferences` table
- Worker: `backend/app/workers/world_state_updater.py`
- See Architecture Pattern 3 for time-aware world state design

---

### Story 6.2: Create World Zones (Arena, Observatory, Commons) - MVP

As a **user**,  
I want **to explore different themed zones for different types of work**,  
So that **my environment matches my current goal focus**.

**Acceptance Criteria:**

**Given** I'm logged in  
**When** I navigate the world  
**Then** I can access three zones:

- **Arena**: Health & craft missions, energizing atmosphere
- **Observatory**: Growth & learning missions, contemplative atmosphere
- **Commons**: Connection & reflection, collaborative atmosphere

**And** each zone shows:

- Zone name and description
- Available missions filtered by value category
- Characters present in the zone
- Atmospheric details (color scheme, ambient sounds optional)

**And** zone availability respects time rules:

- Grayed out if unavailable due to time
- Shows "Opens at [time]" message

**Prerequisites:** Story 6.1 (time engine), Story 3.3 (missions)

**Technical Notes:**

- Frontend routes: `/world/arena`, `/world/observatory`, `/world/commons`
- Component: `ZoneLayout.tsx` with zone-specific theming
- API: `GET /api/v1/world/zones` returns available zones with state
- Schema: `zones` table (id, name, description, value_categories ARRAY, default_availability JSONB)
- Use Tailwind theme variants for zone color schemes

---

### Story 6.3: Add WebSocket for Real-Time World Updates (MVP)

As a **user**,  
I want **real-time updates when world state changes**,  
So that **I see zone availability and events without refreshing**.

**Acceptance Criteria:**

**Given** I'm in a world zone  
**When** world state changes (zone opens/closes, character appears, event starts)  
**Then** I receive a WebSocket message

**And** the UI updates automatically:

- Zone becomes available/unavailable
- Character presence indicator updates
- Event notifications appear

**And** the connection is resilient:

- Auto-reconnects on disconnect
- Fallback to polling if WebSocket fails
- No data loss during reconnection

**Prerequisites:** Story 6.2 (world zones)

**Technical Notes:**

- Backend: FastAPI WebSocket endpoint `/ws/world`
- Frontend: WebSocket client in `lib/websocket.ts`
- Message format: `{"type": "zone_update", "zone_id": "arena", "state": {...}}`
- Use Heartbeat/ping-pong to detect disconnects
- Fallback: poll `/api/v1/world/zones` every 60s if WebSocket unavailable

---

### Story 6.4: Implement Zone Unlocking System (Future)

As a **user**,  
I want **zones to unlock as I progress**,  
So that **the world expands as my journey deepens**.

**Acceptance Criteria:**

**Given** I'm a new user  
**When** I start my journey  
**Then** only one zone is initially available (Commons)

**And** zones unlock through progression:

- **Arena**: Unlock after completing 5 missions
- **Observatory**: Unlock after 7-day streak or narrative Chapter 2
- **Future zones**: Based on story chapters, achievements, or Essence spending

**And** unlock moments are celebrated:

- Cinematic reveal animation
- Character introduction (Lyra in Arena, Elara in Observatory)
- Guided tour of new zone

**Prerequisites:** Story 6.2 (zones), Story 4.3 (narrative progression)

**Technical Notes:**

- Schema: `user_zones` table (user_id FK, zone_id FK, unlocked_at TIMESTAMP, intro_completed BOOLEAN)
- Unlock triggers defined in `zones` table `unlock_criteria JSONB`
- Worker checks criteria when user completes missions/achievements
- Frontend: unlock animation component with Framer Motion

---

### Story 6.5: Add Multiplayer Zone Features (Future)

As a **user**,  
I want **to see other users in shared zones**,  
So that **I feel part of a community working together**.

**Acceptance Criteria:**

**Given** multiplayer is enabled  
**When** I enter a zone  
**Then** I see:

- Other users' avatars/names (anonymized or real based on settings)
- Real-time presence (who's currently in the zone)
- Activity indicators (user just completed a mission)

**And** I can interact:

- Send encouragement emoji
- View others' public progress (opt-in)
- Join shared rituals (future: group meditation, co-working sessions)

**And** zones have capacity limits:

- Max users per instance (e.g., 50 per Commons)
- Multiple instances if over capacity
- Pod members prioritized in same instance

**Prerequisites:** Story 6.2 (zones), Future authentication/multiplayer infrastructure

**Technical Notes:**

- Requires user presence tracking via WebSocket
- Schema: `zone_presence` table (user_id FK, zone_id FK, joined_at, last_activity)
- WebSocket broadcasts presence changes to all users in zone
- Privacy: users can appear "anonymous" or "private"
- Consider scalability: sharding zones by region/instance

---

## Epic 7: Nudge & Outreach

**Epic Goal:** Implement compassionate nudges (in-app, SMS, email) that gently bring users back when they drift away, without feeling naggy or transactional.

**Architecture Components:** ARQ workers, notification service, Twilio (SMS), SendGrid (email), nudge intelligence

### Story 7.1: Set Up Notification Infrastructure

As a **developer**,  
I want **multi-channel notification infrastructure**,  
So that **we can send in-app, SMS, and email nudges reliably**.

**Acceptance Criteria:**

**Given** the notification system is configured  
**When** I send a notification  
**Then** I can target multiple channels:

- In-app (stored in database, shown in UI)
- Email (via SendGrid or similar)
- SMS (via Twilio or similar)
- Push (future: mobile app)

**And** the system handles:

- User opt-in/opt-out preferences per channel
- Rate limiting (max notifications per day/week)
- Delivery tracking (sent, delivered, opened, clicked)
- Failure handling and retries

**And** environment configuration:

- Dev: all notifications logged, not sent
- Staging: sent to test numbers/emails only
- Production: sent to real users respecting preferences

**Prerequisites:** Story 1.4 (user communication preferences)

**Technical Notes:**

- Service: `backend/app/services/notification_service.py`
- Schema: `notifications` table (user_id FK, channel ENUM, content JSONB, sent_at, delivered_at, opened_at, status)
- Integrations: Twilio SDK, SendGrid SDK
- Rate limiting: Redis-based (max 3 nudges/day default)
- Environment vars: TWILIO_API_KEY, SENDGRID_API_KEY

---

### Story 7.2: Implement Drop-Off Detection and Smart Nudge Scheduling

As a **user**,  
I want **to receive gentle reminders when I've been away**,  
So that **I'm encouraged to return without feeling pressured**.

**Acceptance Criteria:**

**Given** I've been inactive  
**When** the nudge scheduler detects my absence  
**Then** nudges are sent at strategic intervals:

- Day 2: In-app reminder only
- Day 4: Email with encouragement from Eliza
- Day 7: SMS (if opted in) with personalized message

**And** nudge content is compassionate:

- "We noticed you've been away—how are you doing?"
- "Your 14-day streak is waiting for you"
- "Eliza has been thinking about your [goal name] goal"
- NOT: "You haven't completed any missions!" (shame-free)

**And** nudges adapt to user patterns:

- Sent at optimal engagement times (based on past activity)
- Respect quiet hours (user preferences)
- Stop after 3 nudges if no response

**And** when I return:

- Welcomed back warmly
- Offered "ease back in" mission (shorter, easier)

**Prerequisites:** Story 7.1 (notification infrastructure), Story 3.4 (mission activity data)

**Technical Notes:**

- Worker: `backend/app/workers/nudge_scheduler.py` (runs daily)
- Drop-off detection: user has no activity for 48+ hours
- Nudge templates stored in `nudge_templates` table
- Uses Eliza agent to personalize message content
- Track nudge effectiveness (response rate) for optimization

---

### Story 7.3: Build In-App Notification Center (MVP)

As a **user**,  
I want **an in-app notification center**,  
So that **I can see all messages from Eliza and the system**.

**Acceptance Criteria:**

**Given** I'm using the app  
**When** I open the notification center  
**Then** I see:

- Unread notifications (badge count in header)
- All past notifications (scrollable list)
- Notification types: nudges, achievements, character messages, story updates

**And** I can:

- Mark as read
- Dismiss notifications
- Take action (e.g., "Start mission" button in notification)

**And** notifications appear in real-time:

- Toast/banner for high-priority notifications
- Badge count updates automatically

**Prerequisites:** Story 7.1 (notification infrastructure)

**Technical Notes:**

- Component: `NotificationCenter.tsx` with dropdown/modal
- API: `GET /api/v1/notifications` with pagination
- WebSocket: real-time notification delivery
- Schema: `is_read BOOLEAN`, `dismissed_at TIMESTAMP` in `notifications` table
- Use shadcn/ui Toast component for banners

---

### Story 7.4: Implement Opt-In/Opt-Out Management UI

As a **user**,  
I want **fine-grained control over which notifications I receive**,  
So that **I'm not overwhelmed and can set boundaries**.

**Acceptance Criteria:**

**Given** I'm in settings  
**When** I manage notification preferences  
**Then** I can toggle:

- In-app notifications (always on, can't disable)
- Email nudges (opt-in)
- SMS nudges (opt-in, requires phone number)
- Character-initiated messages (opt-in)
- Achievement celebrations (opt-in)

**And** I can set:

- Quiet hours (no notifications during these times)
- Maximum nudges per day/week
- Preferred contact method priority

**And** changes take effect immediately

**Prerequisites:** Story 7.1 (notification infrastructure)

**Technical Notes:**

- Frontend: `frontend/src/app/settings/notifications/page.tsx`
- API: `PATCH /api/v1/users/preferences` updates communication preferences
- Store in `user_preferences.communication_preferences JSONB`
- Worker respects preferences when scheduling nudges

---

### Story 7.5: Add AI-Driven Optimal Timing Intelligence (Future)

As a **user**,  
I want **nudges to arrive at times when I'm most likely to respond**,  
So that **they're helpful rather than disruptive**.

**Acceptance Criteria:**

**Given** the system has 30+ days of my data  
**When** scheduling a nudge  
**Then** the AI predicts optimal send time:

- Analyzes my response patterns (when I've acted on past nudges)
- Considers my mission completion times
- Respects circadian rhythms and work patterns

**And** the system learns over time:

- Tracks nudge open rates and response rates by time
- Adjusts future timing based on effectiveness
- A/B tests different timing strategies

**And** I can override:

- Set preferred nudge time manually
- System uses manual preference or AI prediction (whichever is set)

**Prerequisites:** Story 7.2 (nudge scheduler), Story 5.2 (analytics data)

**Technical Notes:**

- ML model: simple time-series prediction or LLM-based reasoning
- Store optimal times in `user_insights` table
- Worker queries insights before scheduling nudges
- Track experiment data for continuous improvement

---

## Epic 8: Evidence & Reflection

**Epic Goal:** Enable users to upload evidence of accomplishments (photos, artifacts) and reflect on their journey, building toward AI-validated achievements and shared galleries.

**Architecture Components:** S3-compatible storage, file upload service, evidence review system

### Story 8.1: Set Up S3 File Storage Infrastructure

As a **developer**,  
I want **reliable cloud storage for user-uploaded files**,  
So that **evidence uploads are scalable and cost-effective**.

**Acceptance Criteria:**

**Given** the file storage is configured  
**When** a file is uploaded  
**Then** it is stored in S3-compatible storage (AWS S3, MinIO, etc.)

**And** the system handles:

- Secure presigned URLs for uploads (no direct S3 access)
- File type validation (images: JPEG, PNG; PDFs for documents)
- Size limits (10MB per file for MVP)
- Virus scanning (optional for MVP, required for production)

**And** files are organized:

- Bucket: `delight-evidence`
- Structure: `{user_id}/{mission_id}/{filename}`
- Metadata stored in database

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- Service: `backend/app/services/storage_service.py`
- Use `boto3` for S3 interaction
- Schema: `evidence_uploads` table (id, user_id FK, mission_id FK, s3_key, file_type, file_size, uploaded_at, visibility ENUM[private/public/pod])
- Environment: S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY
- Consider MinIO for local dev environment

---

### Story 8.2: Implement Evidence Upload Flow (MVP)

As a **user**,  
I want **to upload photos or documents as proof of my mission completion**,  
So that **I can build a tangible record of my accomplishments**.

**Acceptance Criteria:**

**Given** I'm completing or have completed a mission  
**When** I upload evidence  
**Then** I can:

- Select file from device (camera roll, file system)
- Preview before uploading
- Add optional caption/note

**And** the upload process:

- Shows progress bar
- Handles errors gracefully (retry, cancel)
- Confirms successful upload

**And** uploaded evidence:

- Links to the mission
- Appears in mission history
- Stored securely with privacy controls

**Prerequisites:** Story 8.1 (S3 storage), Story 3.4 (mission completion)

**Technical Notes:**

- API: `POST /api/v1/evidence/upload` returns presigned URL
- Frontend uploads directly to S3 via presigned URL
- After upload, frontend calls `POST /api/v1/evidence/confirm` to finalize
- Component: `EvidenceUploader.tsx` with drag-and-drop support
- Mobile: use file input with `accept="image/*"` for camera access

---

### Story 8.3: Create Evidence Gallery and Mission History

As a **user**,  
I want **to browse my evidence and see a visual history of my work**,  
So that **I can appreciate how far I've come**.

**Acceptance Criteria:**

**Given** I've uploaded evidence over time  
**When** I view my evidence gallery  
**Then** I see:

- Grid of thumbnails (photos/icons)
- Filter by: goal, time range, value category
- Sort by: date, mission, goal

**And** I can:

- Click thumbnail to view full-size with details
- Add/edit captions retroactively
- Delete evidence (marks as deleted, keeps in DB)
- Download originals

**And** the gallery integrates with mission timeline:

- Evidence appears on goal progress timelines
- Visual milestones (photo attached to key missions)

**Prerequisites:** Story 8.2 (evidence upload)

**Technical Notes:**

- Frontend: `frontend/src/app/evidence/page.tsx`
- API: `GET /api/v1/evidence?goal_id=&date_from=&date_to=` with pagination
- Generate thumbnails on upload (or on-demand)
- Use lazy loading for performance
- Component: `EvidenceGallery.tsx` with lightbox modal

---

### Story 8.4: Add Reflection Prompts Post-Mission (MVP)

As a **user**,  
I want **guided reflection prompts after completing missions**,  
So that **I internalize learnings and celebrate progress meaningfully**.

**Acceptance Criteria:**

**Given** I just completed a mission  
**When** the completion modal appears  
**Then** I'm offered optional reflection prompts:

- "What did you learn from this mission?"
- "How do you feel about completing this?"
- "What made this easier or harder than expected?"

**And** I can:

- Skip reflection (not required)
- Write free-form response
- Select from mood emojis
- Record voice note (future)

**And** reflections are stored:

- Linked to mission session
- Added to personal-tier memory
- Eliza can reference in future conversations

**Prerequisites:** Story 3.4 (mission completion), Story 2.2 (memory service)

**Technical Notes:**

- Schema: add `reflection TEXT` to `mission_sessions` table
- Frontend: reflection modal with textarea and emoji picker
- Reflection saved as personal memory: "Reflection on [mission]: [text]"
- Optional: use sentiment analysis to track emotional journey

---

### Story 8.5: Implement AI Validation of Evidence (Future)

As a **user**,  
I want **AI to recognize and validate my uploaded evidence**,  
So that **achievements feel verified and meaningful**.

**Acceptance Criteria:**

**Given** I upload evidence  
**When** AI analyzes the image/document  
**Then** it detects:

- Relevance to mission (e.g., photo of completed workout for health mission)
- Quality/authenticity indicators
- Specific accomplishments (e.g., "Ran 5km based on fitness tracker screenshot")

**And** validation results:

- Badge: "AI-Verified" on evidence
- Bonus rewards for verified evidence (extra Essence)
- Flags suspicious uploads (requires manual review)

**And** validation is optional:

- Users can skip AI review if preferred
- Doesn't block uploads or progress

**Prerequisites:** Story 8.2 (evidence upload)

**Technical Notes:**

- Use OpenAI Vision API or similar for image analysis
- Prompt: "Does this image show evidence of [mission goal]? Explain."
- Store validation results in `evidence_uploads.ai_validation JSONB`
- Handle false positives gracefully (don't punish users)

---

### Story 8.6: Create Shared Achievement Galleries (Future)

As a **user**,  
I want **to share selected evidence with my pod or publicly**,  
So that **I can inspire others and celebrate wins together**.

**Acceptance Criteria:**

**Given** I have evidence I'm proud of  
**When** I mark it as shareable  
**Then** it appears in:

- Pod gallery (if I'm in an accountability pod)
- Public gallery (opt-in, moderated)
- Social media preview (exportable)

**And** shared evidence includes:

- Photo/artifact
- Mission/goal context
- Optional caption
- Anonymized user info (or real name if opted in)

**And** others can:

- React with encouragement emoji
- Comment (if enabled)
- Get inspired and create similar missions

**Prerequisites:** Story 8.3 (evidence gallery), Future multiplayer/pod system

**Technical Notes:**

- Schema: `shared_evidence` table (evidence_id FK, shared_scope ENUM[pod/public], shared_at, moderation_status)
- Moderation: manual review for public gallery to prevent abuse
- API: `GET /api/v1/evidence/shared` for public gallery
- Frontend: gallery with filtering and discovery features

---

## Epic Breakdown Summary

**Total Stories:** 53 stories across 8 epics

- **Epic 1 (Foundation):** 5 stories
- **Epic 2 (Companion & Memory):** 7 stories
- **Epic 3 (Goal & Mission):** 7 stories
- **Epic 4 (Narrative Engine):** 7 stories
- **Epic 5 (Progress & Analytics):** 6 stories
- **Epic 6 (World State & Time):** 5 stories
- **Epic 7 (Nudge & Outreach):** 5 stories
- **Epic 8 (Evidence & Reflection):** 6 stories

**MVP Scope:** ~25-30 stories (stories marked as MVP or without "Future" designation)

**Implementation Order:**

1. Epic 1 (Foundation) - Required first
2. Epic 2 (Companion & Memory) - Core differentiator
3. Epic 3 (Goal & Mission) - Core productivity loop
4. Epic 5 (Progress & Analytics) - Engagement driver
5. Epic 7 (Nudge & Outreach) - Retention system
6. Epic 4 (Narrative Engine) - Enhanced experience
7. Epic 6 (World State & Time) - World building
8. Epic 8 (Evidence & Reflection) - Advanced features

Each story follows BDD format, includes prerequisites to prevent forward dependencies, and provides technical implementation guidance aligned with the Architecture document.

---

_Next Steps: Use sprint-planning workflow (Scrum Master agent) to organize these stories into sprints and begin implementation._
