# Epic 2: Companion & Memory System

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
