# Architecture Decision Records (ADRs)

### ADR-001: Next.js 15 + React 19 for Frontend

**Decision:** Use Next.js 15 with React 19 for the frontend framework.

**Rationale:**

- React ecosystem provides extensive component libraries and community support
- Next.js 15 offers streaming support for AI responses (SSE)
- Server Components reduce client bundle size
- App Router provides excellent routing for zone-based navigation

**Alternatives Considered:**

- SvelteKit (better animation performance, smaller ecosystem)
- SolidJS (best performance, smallest ecosystem)

**Consequences:**

- Larger initial bundle than Svelte/Solid
- Need to optimize animations with Framer Motion
- Benefit from massive React ecosystem

---

### ADR-002: FastAPI for Backend

**Decision:** Use FastAPI as the backend framework.

**Rationale:**

- Async-first architecture perfect for AI streaming
- Excellent LangChain/LangGraph integration
- Automatic OpenAPI documentation
- Python ecosystem for AI/ML libraries

**Alternatives Considered:**

- Django Ninja (more structure, less async flexibility)
- Litestar (faster, smaller ecosystem)

**Consequences:**

- Need to add background jobs separately (ARQ)
- More manual setup than Django, but more flexibility

---

### ADR-003: LangGraph + LangChain for AI Orchestration

**Decision:** Use LangGraph for stateful agent orchestration, LangChain for LLM integration.

**Rationale:**

- LangGraph's state machine model perfect for character personalities and narrative flows
- Multi-agent support for Eliza + character system
- Built-in memory abstractions
- Streaming support for token-by-token responses

**Alternatives Considered:**

- Vanilla LangChain (simpler, less structured for stateful agents)
- Custom orchestration (full control, more work)

**Consequences:**

- Learning curve for graph paradigm
- Framework dependency, but provides structure for complex AI workflows

---

### ADR-004: PostgreSQL pgvector for Vector Storage

**Decision:** Use PostgreSQL with pgvector extension for vector storage.

**Rationale:**

- Unified storage: vectors + structured data in single database
- Production-ready from day one, no migration needed
- Excellent LangChain integration (langchain-postgres)
- Reduces operational complexity (one database instead of two)
- ACID guarantees for vector operations

**Alternatives Considered:**

- Chroma (simpler initially, but requires separate service or embedded mode)
- Qdrant (best vector performance, adds operational overhead)

**Consequences:**

- Need PostgreSQL 15+ with pgvector extension installed
- Slightly more complex initial setup than embedded Chroma
- Better scalability and production-readiness long-term

---

### ADR-005: Hybrid SSE + WebSocket + HTTP for Real-Time

**Decision:** Use Server-Sent Events (SSE) for AI streaming, WebSocket for world state updates, HTTP for user actions.

**Rationale:**

- SSE perfect for one-way token streaming from AI
- WebSocket for bidirectional world state (zone availability, character presence)
- Eliminates polling delay (previously 15min), provides instant updates
- HTTP for user actions is standard and simple
- Graceful degradation: WebSocket failures fall back to polling

**Alternatives Considered:**

- Pure WebSocket (full-duplex everywhere, more complex state management)
- Pure polling (simpler, 15min latency for world changes)
- SSE only (no bidirectional communication)

**Consequences:**

- Need to manage WebSocket connections and reconnection logic
- Better UX with real-time world state changes
- Fallback to polling ensures reliability

---

### ADR-006: JSON vs JSONB for Flexible Schemas

**Decision:** Use `JSON` type (not `JSONB`) for flexible data structures in PostgreSQL.

**Rationale:**

- Simpler storage model for complex nested structures
- Preserves exact JSON formatting and key order
- Adequate performance for our use case (personality configs, quest data)

**Alternatives Considered:**

- JSONB (better performance, indexable, but binary format)
- Fully normalized tables (rigid, hard to evolve for AI-generated content)

**Consequences:**

- Slightly slower queries on JSON fields (acceptable trade-off)
- Cannot create GIN indexes on JSON columns (only JSONB supports this)
- Simpler mental model for developers
- Note: Can migrate to JSONB later if performance becomes an issue

---

### ADR-007: Clerk for Authentication

**Decision:** Use Clerk as the managed authentication service instead of building JWT-based auth.

**Rationale:**

- **Reduced Complexity:** Eliminates 2-3 stories worth of auth development (password reset, email verification, session management)
- **Security:** Clerk handles OAuth, 2FA, breach detection, password policies out-of-the-box
- **User Experience:** Pre-built UI components, social login (Google, GitHub), magic links
- **Cost Efficiency:** Free tier: 10,000 MAU, then $25/1000 MAU (reasonable for MVP)
- **Compliance:** SOC 2 Type II, GDPR, CCPA compliant (reduces legal burden)
- **Developer Experience:** Simple SDK integration, well-documented Next.js support

**Alternatives Considered:**

- Custom JWT implementation (more control, significantly more development time)
- Auth0 (similar features, more expensive at scale)
- Supabase Auth (good option, but Clerk has better Next.js integration)

**Consequences:**

- **Positive:** Faster time to market, better security, less maintenance burden
- **Negative:** Vendor lock-in (mitigated by standardized OAuth flows)
- **Migration Path:** If needed, Clerk data can be exported and migrated to custom auth

**Story Impact:**

- Story 1.3: "Implement JWT-Based Authentication" → "Integrate Clerk Authentication System"
- Story 1.4: "Create User Onboarding Flow" → Move to Epic 2 (after app features exist)

---

### ADR-008: Open Source Emotion Detection Model

**Decision:** Use `cardiffnlp/twitter-roberta-base-emotion-multilingual-latest` for emotion detection in chat messages.

**Rationale:**

- **Open Source:** Free to use, no API costs after infrastructure
- **Proven:** 400K+ downloads on Hugging Face, actively maintained
- **Performance:** Fast inference (~50ms on CPU), 7 emotions (joy, anger, sadness, fear, love, surprise, neutral)
- **Multilingual:** Supports multiple languages (future-proofing)
- **Privacy:** Self-hosted, user messages never leave our infrastructure
- **Quality:** Trained on large Twitter dataset, good generalization to conversational text

**Alternatives Considered:**

- Hume AI API (excellent quality, $0.005 per request = expensive at scale)
- GPT-4 emotion classification (works well, adds LLM cost + latency)
- facebook/wav2vec2-large-emotion (audio only, not suitable for text chat)

**Consequences:**

- **Positive:** No per-request costs, privacy-friendly, low latency
- **Negative:** Requires hosting infrastructure (CPU/GPU), model loading time on startup
- **Implementation:** Use Hugging Face Inference API for MVP (free tier), migrate to self-hosted as scale increases

**Integration:**

```python