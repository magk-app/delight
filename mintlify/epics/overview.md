# Overview

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
