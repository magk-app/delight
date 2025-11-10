# Delight 🎮✨

**A story for ambitious people who want to transform their lives**

Delight is an emotionally intelligent AI companion that transforms overwhelming goals into achievable daily missions. Through personalized storytelling, adaptive coaching, and visible progress tracking, Delight helps you build momentum when stress, overwhelm, or competing obligations threaten to derail your ambitions.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-19+-61dafb.svg)](https://reactjs.org/)
[![Status](https://img.shields.io/badge/status-in%20development-orange.svg)]()

---

## 🌟 What is Delight?

Delight isn't just another productivity app—it's your personal companion in achieving difficult goals. Imagine having a coach who understands how you feel, remembers your entire journey, and helps you take the next meaningful step even when you're overwhelmed, stuck, or have lost momentum.

The platform blends three powerful approaches: emotionally aware AI coaching that adapts to your state of mind, narrative world-building that makes your progress feel like an epic adventure, and structured progress systems that show you concrete evidence your work is paying off. Whether you're a founder juggling multiple priorities, a student managing coursework, or someone pursuing hard-to-measure life changes like moving abroad or building relationships, Delight meets you where you are.

**For non-technical users:** Think of Delight as a caring friend who never forgets your goals, always knows what you're working on, and helps you choose what to focus on next. It turns abstract ambitions into concrete actions and celebrates every step forward.

**For technical users:** Delight uses LangGraph for stateful multi-agent orchestration, a three-tier memory architecture (personal, project, task) powered by Chroma vector storage, and FastAPI + Next.js for a modern, responsive user experience. The system is designed for cost efficiency (<$0.10/user/day) while maintaining emotional intelligence through carefully crafted prompt engineering and context management.

---

## 💡 The Problem We're Solving

Ambitious people routinely set large goals but stall when stress, cognitive overload, and context switching kick in. You know exactly what needs to be done, but after lunch or a break, starting feels impossible. Five minutes into focused work, you're checking another tab. Your to-do list sprawls across tools, and prioritizing feels paralyzing.

Existing solutions fall short in critical ways:

**DIY productivity systems** (Notion templates, habit trackers) demand constant maintenance exactly when you have the least bandwidth. They collapse under real-world chaos and don't adapt to your emotional state.

**Generic AI assistants** provide surface-level advice without understanding your unique context, goals, or struggles. They reset every conversation, making you explain your situation repeatedly.

**Traditional productivity tools** focus on structure but ignore emotion. They can't tell when you're overwhelmed and need gentle guidance versus when you're ready for ambitious sprints.

**Professional coaching** is effective but expensive and unavailable during the exact moments of hesitation when you need support most.

Delight bridges these gaps by combining the empathy of human coaching, the memory of your entire journey, and the always-available support of AI—all while making progress visible and celebrating your wins in ways that compound motivation over time.

_(Detailed problem analysis available in our [Product Brief](docs/product-brief-Delight-2025-11-09.md))_

---

## ✨ What Makes Delight Different

### Emotion-First Guidance

Most tools lead with structure and expect you to adapt. Delight leads with empathy. When you open the app, it asks how you're feeling. Stressed? It suggests smaller, achievable missions. Energized? It offers ambitious challenges. This emotional attunement means the system meets you where you are instead of demanding you meet rigid requirements.

The companion learns your patterns—when you're most productive, what kinds of tasks drain you, which goals matter most. Over time, its suggestions become increasingly personalized, creating a relationship that deepens rather than resetting with each session.

### Living Memory That Compounds

Unlike chatbots that forget your conversation history or productivity apps that don't connect the dots between your projects, Delight maintains a sophisticated three-tier memory system. Personal memories capture your values, fears, and long-term aspirations. Project memories track each major goal's context and progress. Task memories ensure the AI understands specific mission details.

This means when you mention feeling stuck on your career transition three weeks later, Eliza (your companion) remembers the context, your previous attempts, and what worked before. The relationship compounds in value over time.

_(Technical details in [Architecture Documentation](docs/ARCHITECTURE.md))_

### Adaptive Micro Missions

Abstract goals like "get healthier" or "build my portfolio" don't translate to action. Delight excels at collaborative goal decomposition—working with you to break overwhelming ambitions into concrete, time-boxed missions that fit your current energy level.

Each mission is adaptive. If you're exhausted, the companion suggests a 10-minute focused session. If you're in flow, it encourages continuation or offers stretch goals. This flexibility prevents both burnout and underperformance, helping you build sustainable momentum.

### Visible Progress That Builds Trust

Nothing kills motivation faster than invisible progress. Delight makes your effort tangible through multiple lenses:

- **Streaks** show daily consistency without being punitive
- **Highlight reels** capture proof of your work with notes and optional photos
- **Progress constellation** visualizes growth across four dimensions: Growth (learning, wisdom), Health (physical wellness), Craft (creative output), Connection (relationships)
- **Daily Consistency Index (DCI)** provides a nuanced score that goes beyond simple streak counting

When you doubt whether your effort matters, Delight shows you the evidence. This visibility is the foundation of long-term engagement.

_(UX details in [Design Specification](docs/ux-design-specification.md))_

### Narrative World Building

Your productivity journey unfolds in a living narrative world that responds to your real-world progress. Choose from scenarios like modern urban reality, medieval fantasy, sci-fi academy, cyberpunk megacity, or zombie apocalypse survival. Your actual work drives story progression—complete missions to earn Essence (in-game currency), build relationships with AI characters, unlock new zones, and progress through story chapters.

This isn't superficial gamification. The narrative serves your real goals. "Prepare for job interview" becomes "Prove yourself to the Guild Council," making preparation feel like meaningful progression in a larger story. The world operates on real-world time, creating temporal rhythms that help you build healthy patterns.

Characters like Eliza (your primary companion), Lyra (craft mentor), Commander Thorne (health guide), and Archmage Elara (wisdom keeper) don't just respond—they initiate conversations, suggest new directions, and celebrate your milestones. Pre-planned story arcs with hidden quests create genuine surprises as your journey unfolds.

---

## 🎯 Who Delight Serves

### Primary Users

**Ambitious multi-track operators** who juggle multiple projects simultaneously and stall when stress spikes or priorities become unclear. Creators, founders, and high-performing professionals who need help maintaining focus when overwhelm strikes.

**Language learners and polymaths** pursuing multiple skill tracks who need a companion that tracks progress across domains, celebrates micro-wins, and helps maintain practice streaks without judgment.

**People pursuing life transformations** with abstract goals like moving abroad, finding relationships, or redefining identity—ambitions that don't fit traditional task lists and require nuanced coaching.

**Momentum switchers** with ADHD tendencies or context-heavy roles who crave structure, rapid feedback, and compassionate accountability when they drift.

### Secondary Users

**Overloaded founding teams** balancing investors, product decisions, and team leadership who need emotional awareness without adding guilt.

**Ambitious students and freelancers** juggling classes, clients, or side projects who lack access to professional coaching but need consistent support.

**Accountability pods** that want to anchor shared rituals while letting the AI handle daily scaffolding and progress tracking.

_(Complete user research in [Product Brief](docs/product-brief-Delight-2025-11-09.md))_

---

## 🚀 MVP Scope: What You Can Expect

The Minimum Viable Product focuses on proving a humane single-player loop that feels personal without requiring expensive infrastructure. We're prioritizing four core pillars:

### 1. Remembered Context at Every Session

When you open Delight, it greets you with awareness of your goals, recent work, and emotional state from previous interactions. No more starting from scratch.

### 2. Collaborative Goal Modeling

The companion helps you break down abstract goals into achievable micro-quests with clear next steps, duration estimates, and value attribution (which dimension of growth this serves).

### 3. Visible Momentum

Streaks, highlight reels, and a consistency index make progress tangible. Short cinematic recaps prove your effort is working, building trust in the system.

### 4. Compassionate Outreach

Opt-in reminders via app notifications, email, or SMS that feel like caring check-ins from a friend—not transactional reminders. These bring you back gently when you've vanished without nagging or guilt.

### What's Deferred

Social features like multiplayer zones, automated matchmaking, and guild economies come later. Voice input, heavy RPG mechanics, and deep screen-time tracking will arrive after the core loop proves retention and cost discipline.

_(Full MVP specifications in [Product Brief](docs/product-brief-Delight-2025-11-09.md))_

---

## 🏗️ How Delight Works: Architecture Overview

### The Core Loop (For Everyone)

1. **Check-in**: Delight asks how you're feeling and what's on your mind
2. **Priority triage**: It suggests three meaningful next steps based on your goals and energy
3. **Mission selection**: You choose what feels right; the companion adjusts duration and difficulty
4. **Focused work**: Complete your mission with gentle presence from the companion
5. **Celebration**: Capture proof of work, earn Essence, update your progress constellation
6. **Reflection**: Review your day's journey and plan tomorrow

### The Technical Stack (For Developers)

**Backend Architecture:**

- FastAPI for async-first API orchestration optimized for AI streaming
- PostgreSQL for structured data (missions, user profiles, progress tracking)
- Chroma vector database for semantic memory search
- Redis for working memory and session management
- ARQ for background job processing (quest generation, scheduled nudges)

**AI Layer:**

- LangGraph + LangChain for stateful multi-agent character system
- Multiple AI characters (Eliza, Lyra, Thorne, Elara) with distinct personalities
- Three-tier memory architecture: personal (values, fears, long-term context), project (goal-specific memories), task (mission details)
- OpenAI/Anthropic LLMs with configurable providers for cost optimization

**Frontend Experience:**

- Next.js 15 with React 19 for modern, performant UI with streaming support
- shadcn/ui component library for accessible, themeable interfaces
- Framer Motion for character animations and smooth transitions
- Server-Sent Events (SSE) for real-time AI response streaming

**Novel Patterns:**

- Living narrative engine that generates personalized stories with pre-planned arcs
- Character-initiated interactions where AI companions proactively reach out
- Time-aware world state that changes based on real-world time (morning opens more zones; night brings reflection)

_(Complete technical documentation in [Architecture Guide](docs/ARCHITECTURE.md) and [UX Design Spec](docs/ux-design-specification.md))_

---

## 🎮 The Experience: Sample User Flow

Let me walk you through what using Delight actually feels like.

### Morning Session

It's 8:30 AM. You open Delight feeling stressed about an upcoming presentation. The app greets you:

> **Eliza:** "Good morning, Jack. Day 5 in your journey. I notice some tension in how you're approaching today. Want to talk about it, or shall we jump straight into priorities?"

You choose to talk. Eliza asks about the presentation. You admit you're worried about public speaking. She acknowledges this, reminds you of the speaking practice you did two days ago, and suggests:

> **Priority Triad:**
>
> 1. Arena Morning Session with Commander Thorne (20 min) - Quick physical reset before cognitive work
> 2. Presentation Outline with Lyra (45 min) - Structure your talk with your craft mentor
> 3. Continue Learning: Chapter 4 of "Confident Speaking" (30 min) - Build on yesterday's momentum

You choose option 2. The full-screen mission interface appears. For 45 minutes, you outline your presentation while Eliza stays minimally present in the corner. When you drift to check email, a gentle notification asks: "Intentional break, or pulled away?"

You complete the mission. Eliza celebrates: "That outline is solid. I can see the narrative arc. Want to keep momentum with a quick rehearsal, or save energy for later?"

This is your third consecutive day of completing missions. A streak notification appears, and Essence points accumulate in your progress constellation.

### Week 3 Surprise

Three weeks in, you've focused heavily on Craft missions. One evening, a notification appears:

> **Archmage Elara seeks you in the Observatory**

You open the app. Elara, the wisdom keeper character, has initiated a conversation:

> **Elara:** "Jack. You've been focused on Craft for two weeks—your skill grows impressively. But I wonder: have you considered teaching? Beginners arrive daily, overwhelmed just as you once were. You could guide them, deepening your own understanding while unlocking Connection—meeting others on similar paths. What do you say?"

This is a character-initiated interaction based on your activity patterns. It introduces you to mentorship opportunities, unlocking new dimensions of growth you hadn't considered.

_(More user flows in [UX Design Specification](docs/ux-design-specification.md))_

---

## 🛠️ Getting Started: Installation Guide

### Prerequisites

**For Non-Technical Users:**
Running Delight locally requires some technical setup. If you're interested in trying Delight but aren't comfortable with development tools, we recommend waiting for our hosted beta launch (coming soon). Sign up for updates at [coming soon].

**For Developers:**

Delight supports **two infrastructure modes** to balance speed and flexibility:

**Required for both modes:**

- **Node.js 20+** with pnpm package manager (`npm install -g pnpm`)
- **Python 3.11+** with Poetry (`pip install poetry`)
- **Clerk account** (free tier) for authentication → [clerk.com](https://clerk.com)
- **OpenAI API key** for AI capabilities → [platform.openai.com](https://platform.openai.com)

**Additional for Local Mode only:**

- **Docker Desktop** for local PostgreSQL + Redis

---

### 🌥️ Setup Path 1: Cloud-Dev Mode (Recommended)

**Best for:** Fast setup, production parity, no Docker required  
**Free tier services:** Supabase (500MB DB), Upstash (10K Redis commands/day), Clerk (10K MAU)

#### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/delight.git
cd delight

# Install all dependencies (root + frontend + backend)
make install
# Or manually: pnpm install && cd packages/backend && poetry install
```

#### Step 2: Set Up Cloud Services

**Supabase (PostgreSQL Database):**

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to **Project Settings → Database → Connection String**
4. Copy the URI format (starts with `postgresql://`)
5. Convert to async format: Replace `postgresql://` with `postgresql+asyncpg://`

**Upstash (Redis) - Optional:**

1. Create account at [upstash.com](https://upstash.com)
2. Create new Redis database
3. Copy the connection URL from dashboard

**Alternative:** Use Docker Redis even in cloud-dev mode:

```bash
docker run -d -p 6379:6379 redis:7-alpine
# Then use REDIS_URL=redis://localhost:6379
```

**Clerk (Authentication):**

1. Create account at [clerk.com](https://clerk.com)
2. Create new application
3. Copy **Publishable Key** (starts with `pk_test_`)
4. Copy **Secret Key** (starts with `sk_test_`)

#### Step 3: Configure Environment Variables

**Frontend** (`packages/frontend/.env.local`):

```bash
# Clerk Authentication
# PUBLIC KEY - Safe to expose in browser (has NEXT_PUBLIC_ prefix)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

# SECRET KEY - Used for SERVER-SIDE Next.js middleware (NO NEXT_PUBLIC_ prefix)
# This is SAFE because Next.js keeps non-NEXT_PUBLIC_ variables server-side only
# The middleware runs on the server, so the secret never reaches the browser
CLERK_SECRET_KEY=sk_test_...

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# SECURITY NOTE:
# Next.js App Router has both client-side AND server-side code in the frontend project.
# Variables WITHOUT NEXT_PUBLIC_ prefix are ONLY available server-side (middleware, server components).
# Variables WITH NEXT_PUBLIC_ prefix are available everywhere (including browser).
```

**Backend** (`packages/backend/.env`):

```bash
# Infrastructure Mode
INFRA_MODE=cloud-dev

# Supabase Database (from Step 2)
DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres

# Redis (Upstash or Docker)
REDIS_URL=redis://localhost:6379  # or your Upstash URL

# Clerk Authentication (SECRET KEY - backend only!)
CLERK_SECRET_KEY=sk_test_...

# AI/LLM
OPENAI_API_KEY=sk-...

# Optional: Error Tracking
SENTRY_DSN=https://...

# Environment
ENVIRONMENT=development
```

#### Step 4: Start Development

```bash
# Start both frontend + backend servers
make dev

# Or start separately:
# Terminal 1: make dev:frontend
# Terminal 2: make dev:backend
```

**Access your app:**

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs (interactive API docs)

---

### 🐳 Setup Path 2: Local Mode (Full Offline)

**Best for:** Offline development, air-gapped environments, contributor preference for local control

#### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/delight.git
cd delight

# Install all dependencies
make install
```

#### Step 2: Start Local Infrastructure

```bash
# Start Docker PostgreSQL + Redis
make local
```

This starts:

- **PostgreSQL 16** with pgvector support on port 5432
- **Redis 7** on port 6379

Verify services running:

```bash
docker ps  # Should show postgres:16-alpine and redis:7-alpine
```

#### Step 3: Set Up Clerk (Still Required)

Clerk authentication runs as a managed service even in local mode (no self-hosted auth):

1. Create account at [clerk.com](https://clerk.com)
2. Create new application
3. Copy **Publishable Key** and **Secret Key**

#### Step 4: Configure Environment Variables

**Frontend** (`packages/frontend/.env.local`):

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...  # Public key (client-side)
CLERK_SECRET_KEY=sk_test_...  # Secret key (server-side middleware only)

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`packages/backend/.env`):

```bash
# Infrastructure Mode
INFRA_MODE=local

# Local Docker PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight

# Local Docker Redis
REDIS_URL=redis://localhost:6379

# Clerk Authentication (SECRET KEY - backend only!)
CLERK_SECRET_KEY=sk_test_...

# AI/LLM
OPENAI_API_KEY=sk-...

# Environment
ENVIRONMENT=development
```

#### Step 5: Start Development

```bash
# Start both frontend + backend servers
make dev
```

**Access your app:**

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs

**To stop local services:**

```bash
make stop
```

---

### 🔄 Switching Between Modes

You can easily switch between cloud-dev and local modes:

```bash
# Switch to local mode
make local
# Update backend/.env: INFRA_MODE=local, DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight

# Switch to cloud-dev mode
make stop  # Stop Docker services
# Update backend/.env: INFRA_MODE=cloud-dev, DATABASE_URL=<supabase-url>
```

---

### 🧪 Verify Your Setup

```bash
# Run linters (both modes)
make lint

# Run tests (both modes)
make test

# Check health endpoint
curl http://localhost:8000/api/v1/health
# Should return: {"status": "healthy", "database": "connected", "redis": "connected", ...}

# Check Swagger UI
curl http://localhost:8000/docs
# Should return HTML with interactive API documentation
```

---

### 🔐 Security Notes

**CRITICAL:** Understanding Clerk keys in Next.js App Router:

- **`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`** → Public key, safe to expose in browser (client-side)
- **`CLERK_SECRET_KEY`** → Secret key for server-side operations (middleware, server components)

**Important Next.js Security Concept:**

In Next.js with App Router, your "frontend" project contains BOTH:

1. **Client-side code** (runs in browser) - Can ONLY access `NEXT_PUBLIC_*` variables
2. **Server-side code** (middleware, server components) - Can access ALL variables

The `CLERK_SECRET_KEY` is used by server-side middleware (`packages/frontend/src/middleware.ts`) and **NEVER** gets sent to the browser. This is different from traditional SPAs where everything runs client-side.

**Both `.env.example` files include detailed comments about this.**

---

### 📚 Additional Resources

- **Makefile commands:** Run `make help` to see all available commands
- **Architecture details:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Workflow status:** [docs/bmm-workflow-status.yaml](docs/bmm-workflow-status.yaml)
- **Epic 1 Technical Spec:** [docs/tech-spec-epic-1.md](docs/tech-spec-epic-1.md)

_(Full API documentation available at `/docs` endpoint after starting the backend)_

---

## 📖 Project Documentation

Our documentation is designed to serve different audiences:

**For everyone:**

- [Product Brief](docs/product-brief-Delight-2025-11-09.md) - Vision, problem space, and success metrics
- [UX Design Specification](docs/ux-design-specification.md) - How the experience works and why

**For developers:**

- [Architecture Guide](docs/ARCHITECTURE.md) - Technical decisions, system design, and implementation patterns
- [Workflow Status](docs/bmm-workflow-status.yaml) - Current development phase and progress

**Coming soon:**

- Development roadmap with detailed timeline
- API documentation for integration
- Contributing guidelines for community developers

---

## 🎯 Success Measures

We measure Delight's impact through both user outcomes and business metrics:

### User Success

**Consistency and momentum:** Are users maintaining 4+ day streaks in their first two weeks? Do they complete their first mission within 48 hours and continue?

**Emotional improvement:** Does mood improve from session start to session end? Do users feel less overwhelmed?

**Visible progress:** Are highlight reels being watched? Does the progress constellation show meaningful growth across dimensions?

**Goal achievement:** Are abstract goals getting broken down into actionable plans? Are those plans being executed?

### Business Success

**Retention:** Strong Day-7 and Day-30 retention for target personas indicates the core loop is working.

**Value perception:** Trial-to-paid conversion driven by perceived value (not artificial scarcity) shows we're solving real problems.

**Cost efficiency:** Maintaining core loop cost under $0.10 per active user per day proves sustainable economics.

**Organic growth:** Unprompted testimonials, social sharing, and community buzz signal genuine product-market fit.

_(Complete metrics framework in [Product Brief](docs/product-brief-Delight-2025-11-09.md))_

---

## 🧭 Roadmap Snapshot

### Current Focus: Building the Core Loop (Weeks 1-6)

We're establishing the foundation:

- Conversational AI core with persistent memory
- Goal decomposition into micro-missions
- Priority triads and adaptive mission system
- Streak tracking and highlight reel generation
- Opt-in notification system (email, SMS, in-app)

### Near-Term Priorities (Weeks 7-12)

Once the core loop shows retention:

- Narrative engine with AI-generated story progression
- Character relationship system
- Time-based world dynamics
- Evidence capture (photos, notes) for proof of work
- Consistency dashboard with detailed analytics

### Future Vision (Post-MVP)

After validating single-player experience:

- Social features: shared zones, accountability pods
- Advanced RPG mechanics: zones, economies, guild systems
- Voice input for hands-free interaction
- Mobile-optimized experience
- Community features and mentorship systems

A detailed roadmap will live in `docs/roadmap.md` once development cadence stabilizes.

---

## 🤝 Contributing and Feedback

Delight is in early development. We're not accepting code contributions yet, but we deeply value your input:

**Share your experience:** If productivity tools have failed you, tell us why. What's missing? What would make you excited?

**Report issues:** Found a bug or rough edge? Open a GitHub issue with reproduction steps and your environment details.

**Request features:** Have ideas for improvements? Open an issue tagged "feature request" with your use case.

**Join the pilot:** Interested in early access? Mention it in an issue titled "Pilot Cohort Interest" with a brief description of your goals.

---

## 🔐 Privacy and Data Philosophy

Delight asks for the minimum context needed to help you effectively. Your emotional check-ins, goals, and progress are stored with care.

**Transparency:** Any context signals (tab focus, activity patterns) are explicitly opt-in. You always know what we're tracking.

**Control:** Review everything stored about you, revoke permissions anytime, and export your complete data on demand.

**Security:** Data encrypted at rest (database level), encrypted in transit (HTTPS/TLS), and evidence uploads use signed URLs with user-only access.

**GDPR Compliance:** Full data export and deletion capabilities built into the platform.

We believe trust is the only defensible moat for a companion. Your autonomy and privacy stay front and center.

---

## 💻 Technology Stack

**Backend Foundation:**

- Python 3.11+ with FastAPI for async-first API design
- PostgreSQL for structured data persistence
- Redis for working memory and session caching
- Chroma vector database (embedded mode) for semantic memory

**AI Orchestration:**

- LangGraph for stateful multi-agent workflows
- LangChain for LLM integration and memory abstractions
- OpenAI GPT-4 for MVP (configurable for other providers)
- Mem0-style tiered memory architecture

**Frontend Experience:**

- React 19 with Next.js 15 App Router
- TypeScript for type safety
- Tailwind CSS for styling with theme system
- shadcn/ui for accessible component primitives
- Framer Motion for character animations

**Infrastructure:**

- Vercel for frontend hosting (edge network)
- Railway or AWS for backend services
- S3-compatible storage for evidence uploads
- Deployment containerized with Docker

_(Complete technical decisions and rationale in [Architecture Guide](docs/ARCHITECTURE.md))_

---

## 🌍 Design Philosophy

### Efficiency Through Understanding

Emotional intelligence and storytelling aren't ends in themselves—they're tools that diagnose blockers and unlock action. The ultimate measure is: **Did you make meaningful progress?**

### The World Is a Character

The narrative environment matters as much as Eliza. Navigation feels rich and explorable, creating a good adventure with mystery, depth, and emergent storytelling.

### Flexible Fidelity

Delight offers both decorative richness (immersive world-building for those who want it) and efficient minimalism (clean dashboards for those who prefer simplicity). The interface adapts to your preference.

### Modern Warmth

Clean lines and sophisticated interactions avoid sterile tech aesthetics. Warm colors, thoughtful animations, and gentle micro-interactions make efficiency feel good.

### Visible Progress Compounds Trust

Every mission, streak, and milestone must be tangible. Highlight reels and environmental changes prove effort is working—this visibility drives engagement more than any feature.

_(Complete design principles in [UX Design Specification](docs/ux-design-specification.md))_

---

## ❓ Frequently Asked Questions

**Is this just a habit tracker with points?**
No. While streaks and Essence (XP) exist, they serve real work—not the other way around. Missions correspond to actual progress on your goals. The narrative makes effort feel meaningful, not just tracked.

**Can I use Delight without the story elements?**
Yes. The narrative is optional. You can focus entirely on the companion dialogue, mission system, and progress tracking if you prefer a minimalist experience.

**Will you match me with other users?**
Not in the MVP. Social features will be manual and opt-in only. We're proving the single-player loop first.

**What about cost? Will this be expensive to run?**
We're targeting under $0.10 per active user per day at MVP scale. The tech stack and AI providers are chosen specifically for cost efficiency. This allows us to offer accessible pricing.

**How is this different from Habitica?**
Habitica pioneered gamified productivity with task lists turning into RPG quests. Delight focuses on emotionally intelligent coaching that adapts to your state, deeper goal decomposition for abstract ambitions, and narrative personalization through AI-generated stories. We're complementary—Habitica excels at routine habits; Delight excels at complex, emotionally challenging goals.

**Do I need technical skills to use this?**
Not once we launch the hosted version. Right now, running Delight locally requires developer tools. If you're interested in early access without technical setup, join our waitlist (coming soon).

**Is my data safe?**
Yes. We encrypt data at rest and in transit, make all tracking opt-in and transparent, and provide full export/deletion capabilities. Privacy and trust are foundational to the platform.

---

## 🙏 Acknowledgments and Inspiration

Delight stands on the shoulders of giants:

**Habitica** pioneered gamified productivity, proving that game mechanics can drive real-world behavior change when implemented thoughtfully.

**Notion** demonstrated that powerful productivity tools can have beautiful, flexible interfaces that users genuinely enjoy.

**OpenAI** made sophisticated AI accessible to developers, enabling emotionally intelligent companions like Delight.

**The LangChain community** advanced AI agent frameworks, memory systems, and orchestration patterns that power our multi-agent architecture.

The research, frameworks, and open-source contributions from these communities make Delight possible.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You're free to use, modify, and distribute this software, even commercially, as long as you include the original copyright notice. We believe in open innovation.

---

## 🌟 Join the Journey

Delight is in early development, and we're building something genuinely different—a productivity companion that treats you as a whole person with emotions, ambitions, and unique challenges.

If you believe work can be engaging rather than exhausting, that AI should augment human capability rather than replace it, and that visible progress builds the trust needed for long-term transformation, we'd love to have you along for the ride.

**⭐ Star this repository** to follow our progress and show your support.

**Share your story:** Open an issue telling us about your productivity struggles and what would genuinely help.

**Stay updated:** Watch this repository for major milestones and release announcements.

---

<div align="center">

**Made with ❤️ by Jack and the Delight Team**

_Transform your ambitions into achievement, one mission at a time._

</div>
