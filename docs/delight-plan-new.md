# Delight by Magk - Complete MVP Implementation Plan

**Version**: 2.0 (Research-Enhanced)  
**Date**: November 2025  
**Target**: 18-week MVP to Beta Launch  
**Budget**: <$0.10 per active user per day

## Executive Summary

Delight is not just another productivity app—it's a story for ambitious people who want to transform their lives. This plan details how to build a production-ready MVP that combines:

- **Sophisticated AI** with 3-tier memory (Personal/Project/Task), knowledge graphs, and multi-step orchestration
- **Immersive Storytelling** with named protagonist (Eliza), attribute-based characters, and AI-generated narratives
- **Deep Gamification** through evidence capture, highlight reels, streaks, and living world dynamics
- **Emotional Intelligence** via proactive companions that sense isolation and provide compassionate accountability

**One-Liner**: "Your AI companion that knows your goals, understands your struggles, and grows with you as you achieve what matters most."

---

## Part 1: Architecture & Technical Foundation

### 1.1 Technology Stack (Production-Ready)

#### Frontend Stack

**Framework**: Next.js 14 (App Router) with React 18 + TypeScript 5.0+

**Styling**: Tailwind CSS 3.4+ with shadcn/ui component library

**State Management**:

- Zustand for client state (lightweight, 3KB)
- TanStack Query (React Query) for server state caching

**Real-Time**: Socket.io client for WebSocket connections

**Animations**: Framer Motion for smooth transitions and micro-interactions

**Voice**: Web Speech API (browser-native, no additional dependencies)

**PWA**: next-pwa for progressive web app capabilities (offline support, install prompts)

**Forms**: React Hook Form + Zod for validation

**Date/Time**: date-fns for time-zone aware operations

**Why This Stack**: Next.js 14 provides excellent DX with App Router, automatic code splitting, and SEO capabilities for marketing pages. Zustand + React Query gives us the perfect balance of simplicity and power. shadcn/ui provides beautiful, accessible components that we can customize extensively.

#### Backend Stack

**API Framework**: FastAPI 0.104+ (Python 3.11+)

- Async/await for non-blocking I/O
- Automatic OpenAPI/Swagger documentation
- Pydantic v2 for data validation (2-5x faster)
- Built-in WebSocket support

**Task Queue**: Celery 5.3+ with Redis as broker

- For proactive message scheduling
- Background highlight reel generation
- Story generation offloading

**Scheduling**: APScheduler for time-based triggers (morning greetings, evening reflections)

**API Gateway**: Nginx for reverse proxy and load balancing

**Why FastAPI**: Modern, fast (comparable to Node.js), excellent type safety, and best-in-class async support for handling concurrent AI operations.

#### AI & Memory Stack

**Memory Management (Hybrid Architecture)**:

Primary: **Mem0** (embedchain/mem0) for production-ready persistent memory

- Built-in categorization and deduplication
- Multi-user isolation
- Works with Qdrant/Pinecone backends
- Simple Python SDK with async support

**Vector Database**: Qdrant (self-hosted via Docker)

- Best performance/cost for MVP stage
- Rich metadata filtering
- Payload storage (store full documents)
- Easy migration path to Qdrant Cloud

**Working Memory**: Redis 7+ for session state and task context

- Sub-millisecond reads
- TTL for automatic cleanup
- Pub/sub for real-time features

**Knowledge Graph**: NetworkX (in-memory for MVP)

- Python-native, zero infrastructure
- Pickle persistence
- Clear migration path to Neo4j at scale

**Agent Orchestration**:

Primary: **LangGraph** (from LangChain)

- Graph-based workflow definition
- Stateful agents with persistence
- Support for parallel and conditional execution
- Human-in-the-loop capabilities
- Visual debugging tools

**Memory Integration**: Mem0 SDK

**Prompt Management**: Custom template system with Jinja2

**LLM Strategy (Multi-Model Router)**:

Primary: **Anthropic Claude**

- Claude Sonnet 4: Complex reasoning, goal decomposition, workflow planning
- Claude Haiku 4: Quick responses, simple tasks, proactive messages

Secondary: **OpenAI GPT-4** for creative story generation only

**Router Logic**: Task complexity → model selection

- Story generation: GPT-4 (most creative)
- Planning/reasoning: Claude Sonnet 4 (best instruction-following)
- Quick chat: Claude Haiku 4 (fast + cheap)
- Cost tracking per model for optimization

**Why This AI Stack**: Mem0 provides production-ready memory with minimal setup. Qdrant offers best self-hosted performance. LangGraph gives us sophisticated orchestration with transparency. Claude's 200K context window and strong reasoning make it ideal for our use case.

#### Data Storage

**Primary Database**: PostgreSQL 16 with pgvector extension

- ACID compliance for critical data
- JSON support for flexible schemas
- pgvector for embedding storage (backup to Qdrant)

**Cache**: Redis 7 (also used for queues and pub/sub)

**File Storage**:

- MVP: Local filesystem with backup
- Production: S3-compatible (MinIO for dev, AWS S3 for prod)

#### Infrastructure & DevOps

**Containerization**: Docker + Docker Compose

**Development**: Hot-reload for both frontend and backend

**Testing**:

- Backend: Pytest + pytest-asyncio + httpx
- Frontend: Jest + React Testing Library + Playwright E2E

**Monitoring**:

- Application: Sentry for error tracking
- Infrastructure: Prometheus + Grafana
- LLM: LangSmith for observability

**Logging**: Structured JSON logs with correlation IDs

### 1.2 Memory System Architecture (Three-Tier Implementation)

#### Personal Memory (Global Context)

**Purpose**: Long-term knowledge about the user that persists across all sessions and projects.

**Storage**:

```python
# Personal memory in Mem0
from mem0 import Memory

# Initialize with user context
memory = Memory(user_id="user_uuid")

# Add personal facts
memory.add(
    "User prefers working in the morning, 6am-10am",
    metadata={
        "scope": "personal",
        "category": "preferences",
        "created_at": datetime.now()
    }
)

# Retrieve relevant personal context
context = memory.search(
    "When does the user work best?",
    user_id="user_uuid",
    filter={"scope": "personal"}
)
```

**What's Stored**:

- User preferences (work hours, notification channels, UI theme)
- Communication style (formal vs. casual, verbosity)
- Emotional patterns (stress triggers, motivation boosters)
- Core goals and values
- Skills and attributes (Growth, Health, Craft, Connection levels)
- Historical performance data (streaks, completion rates)

**Implementation Details**:

```python
# packages/backend/app/core/memory/personal.py
from typing import List, Dict, Any
from mem0 import Memory
from datetime import datetime, timezone

class PersonalMemory:
    """Manages user's long-term personal memory"""

    def __init__(self, user_id: str, mem0_client: Memory):
        self.user_id = user_id
        self.mem0 = mem0_client
        self.scope = "personal"

    async def remember_preference(
        self,
        key: str,
        value: Any,
        category: str = "general"
    ):
        """Store a user preference"""
        content = f"User preference: {key} = {value}"
        await self.mem0.add(
            content,
            user_id=self.user_id,
            metadata={
                "scope": self.scope,
                "category": category,
                "key": key,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )

    async def recall_context(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Retrieve relevant personal context"""
        filter_dict = {"scope": self.scope}
        if category:
            filter_dict["category"] = category

        results = await self.mem0.search(
            query,
            user_id=self.user_id,
            filter=filter_dict,
            limit=limit
        )

        return results

    async def update_skill_level(
        self,
        attribute: str,  # Growth, Health, Craft, Connection
        new_level: int
    ):
        """Update attribute level in memory"""
        content = f"User {attribute} attribute is now Level {new_level}"
        await self.mem0.add(
            content,
            user_id=self.user_id,
            metadata={
                "scope": self.scope,
                "category": "attributes",
                "attribute": attribute,
                "level": new_level,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        )
```

**Retrieval Strategy**: Semantic search with metadata filtering. When starting a session, retrieve top 10 most relevant personal memories based on current context.

#### Project Memory (Mid-Term Context)

**Purpose**: Context specific to ongoing goals and projects.

**Storage**:

```python
# Project memory with project_id scoping
memory.add(
    "User is preparing for job interview at TechCorp on Nov 15",
    metadata={
        "scope": "project",
        "project_id": "goal_interview_prep",
        "goal_type": "career",
        "deadline": "2025-11-15",
        "created_at": datetime.now()
    }
)
```

**What's Stored**:

- Active goals and their context
- Task history and completion patterns
- Project-specific documents and notes
- Relationships to other goals
- Progress markers and milestones
- Blockers and challenges encountered

**Auto-Archival**: When a goal is marked complete, summarize the project memory and promote key learnings to personal memory, then clear working details.

#### Task Memory (Working Memory)

**Purpose**: Short-term context for the current session and active task.

**Storage**: Primarily Redis (fast, temporary) with selective persistence to Mem0.

**What's Stored**:

- Last N conversation turns (typically 10-20)
- Current mission state
- Recent tool outputs
- Active workflow step
- Temporary calculations or drafts

**Summarization**: At session end, LLM generates a summary of key insights, which get saved to project memory if marked important by user or AI.

#### Hybrid Retrieval System

**Performance Target**: Retrieval latency < 300ms for typical queries.

### 1.3 Knowledge Graph Architecture

**NetworkX Implementation (MVP)**

```python
# packages/backend/app/core/knowledge_graph/graph.py
import networkx as nx
from typing import Dict, List, Any, Optional
import pickle
from pathlib import Path

class KnowledgeGraph:
    """
    In-memory knowledge graph using NetworkX.
    Nodes: Goals, Tasks, Topics, Skills, People, Emotions
    Edges: Relationships with weights and metadata
    """

    def __init__(self, user_id: str, storage_path: Path):
        self.user_id = user_id
        self.storage_path = storage_path / f"{user_id}_graph.pkl"
        self.graph = nx.MultiDiGraph()  # Directed, allows multiple edges

        # Load existing graph if available
        if self.storage_path.exists():
            self.load()

    def add_goal_node(
        self,
        goal_id: str,
        goal_type: str,
        title: str,
        **attributes
    ):
        """Add or update a goal node"""
        self.graph.add_node(
            goal_id,
            node_type="goal",
            goal_type=goal_type,
            title=title,
            **attributes
        )

        # Connect to user root node
        self.graph.add_edge("user_root", goal_id, rel_type="HAS_GOAL")

    def get_related_concepts(
        self,
        node_id: str,
        max_hops: int = 2,
        rel_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Traverse graph from starting node.
        Returns all nodes within max_hops distance.
        """
        if node_id not in self.graph:
            return []

        # BFS traversal
        visited = set()
        queue = [(node_id, 0)]  # (node_id, current_hop)
        related = []

        while queue:
            current_node, hops = queue.pop(0)

            if hops > max_hops or current_node in visited:
                continue

            visited.add(current_node)
            node_data = self.graph.nodes[current_node]

            related.append({
                "node_id": current_node,
                "hops": hops,
                **node_data
            })

            # Get neighbors
            for neighbor in self.graph.neighbors(current_node):
                edge_data = self.graph.get_edge_data(current_node, neighbor)

                # Filter by relationship type if specified
                if rel_types:
                    if not any(e.get("rel_type") in rel_types for e in edge_data.values()):
                        continue

                queue.append((neighbor, hops + 1))

        return related
```

**Graph Structure**:

```
User (root)
├── Personal Profile
│   ├── Preferences
│   ├── Skills (Growth, Health, Craft, Connection)
│   └── Emotional Patterns
├── Goals
│   ├── Goal: Interview Prep
│   │   ├── Task: Practice Answers
│   │   ├── Task: Research Company
│   │   └── Task: Update Resume
│   └── Goal: Learn React
│       └── Tasks...
└── Topics/Concepts
    ├── Career
    ├── Health
    └── Relationships
```

**Migration Path to Neo4j**: When user graph exceeds 10,000 nodes or multi-user queries become common, migrate to Neo4j with Cypher queries.

### 1.4 Goal-Driven Orchestration with LangGraph

**LangGraph Workflow Implementation**

```python
# packages/backend/app/core/orchestration/workflow.py
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

class CompanionWorkflow:
    """
    Main workflow orchestrator using LangGraph.

    Nodes:
    1. Retrieve Context (from memory)
    2. Understand Intent (classify user request)
    3. Plan Steps (decompose goal)
    4. Execute Step (parallel execution if possible)
    5. Validate Output
    6. Update Memory
    7. Generate Response
    """

    def __init__(
        self,
        memory_retriever: HybridRetriever,
        knowledge_graph: KnowledgeGraph,
        llm: ChatAnthropic
    ):
        self.memory = memory_retriever
        self.graph = knowledge_graph
        self.llm = llm

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Construct the execution graph"""

        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("retrieve_context", self.retrieve_context_node)
        workflow.add_node("understand_intent", self.understand_intent_node)
        workflow.add_node("plan_steps", self.plan_steps_node)
        workflow.add_node("execute_step", self.execute_step_node)
        workflow.add_node("validate", self.validate_node)
        workflow.add_node("update_memory", self.update_memory_node)
        workflow.add_node("respond", self.respond_node)

        # Define edges
        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "understand_intent")
        workflow.add_edge("understand_intent", "plan_steps")
        workflow.add_edge("plan_steps", "execute_step")
        workflow.add_edge("execute_step", "validate")

        # Conditional edge: if validation fails, retry or skip
        workflow.add_conditional_edges(
            "validate",
            self.should_retry,
            {
                "retry": "execute_step",
                "skip": "respond",
                "continue": "update_memory"
            }
        )

        workflow.add_edge("update_memory", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile()
```

**Transparency**: At each node, log the action taken and make it available to frontend for "workflow visualization" UI.

---

## Part 2: Core Features Implementation

### 2.1 Eliza - The Protagonist Companion

**Personality System**

```python
# packages/backend/app/core/companion/eliza.py
from enum import Enum
from typing import Dict, List
from langchain.prompts import ChatPromptTemplate

class EmotionalState(str, Enum):
    NEUTRAL = "neutral"
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    URGENT = "urgent"
    CELEBRATORY = "celebratory"
    CONCERNED = "concerned"

class Eliza:
    """
    Named protagonist companion with adaptive personality.

    Personality traits:
    - Empathetic but directive
    - Celebrates wins genuinely
    - Validates struggles without enabling avoidance
    - Adapts tone based on user state
    - Proactive: initiates conversations
    """

    def __init__(
        self,
        llm: ChatAnthropic,
        user_id: str,
        relationship_level: int = 1
    ):
        self.llm = llm
        self.user_id = user_id
        self.relationship_level = relationship_level
        self.name = "Eliza"

    def get_base_system_prompt(self, emotional_state: EmotionalState) -> str:
        """Generate system prompt based on current emotional context"""

        base = f"""You are Eliza, a named AI companion helping {self.user_id} achieve their goals.

Your personality:
- Empathetic but directive: You understand feelings but focus on action
- Genuine celebration: When they succeed, you're truly happy
- Validating without enabling: You acknowledge struggles but gently push forward
- Proactive: You initiate check-ins and suggestions

Relationship level: {self.relationship_level}/10
At this level, you are {"just getting to know each other" if self.relationship_level < 3 else "building trust" if self.relationship_level < 6 else "close companions who understand each other deeply"}.

Current emotional state: {emotional_state.value}"""

        # Tone guidance based on emotional state
        tone_guidance = {
            EmotionalState.SUPPORTIVE: "Use a warm, understanding tone. Validate their feelings.",
            EmotionalState.ENCOURAGING: "Be energetic and motivating. Focus on their capabilities.",
            EmotionalState.URGENT: "Be direct and focused. Time is important here.",
            EmotionalState.CELEBRATORY: "Show genuine excitement. Make this moment special.",
            EmotionalState.CONCERNED: "Express gentle concern. Ask if they're okay."
        }

        return base + "\n" + tone_guidance.get(emotional_state, "")
```

**Relationship Progression System**

```python
# packages/backend/app/models/relationship.py
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey

class RelationshipState(Base):
    __tablename__ = "relationship_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)

    # Discrete level
    level = Column(String, default="acquaintance")  # acquaintance, friend, close_friend, best_friend, dating

    # Multi-dimensional tracking
    trust_score = Column(Float, default=0.5)  # 0.0 to 1.0
    closeness_score = Column(Float, default=0.3)
    motivation_effectiveness = Column(Float, default=0.5)

    # XP for progression
    xp = Column(Integer, default=0)

    # Interaction tracking
    total_interactions = Column(Integer, default=0)
    last_interaction_at = Column(DateTime(timezone=True), server_default=func.now())

# Progression thresholds
RELATIONSHIP_THRESHOLDS = {
    "acquaintance": 0,      # Starting level
    "friend": 100,          # After ~1 week of daily use
    "close_friend": 500,    # After ~1 month
    "best_friend": 1500,    # After ~3 months
    "dating": 3000          # After ~6 months of consistent engagement
}

# XP earning events
XP_REWARDS = {
    "mission_completed": 5,
    "goal_achieved": 20,
    "streak_maintained": 3,
    "deep_conversation": 10,
    "vulnerable_sharing": 15,
    "feedback_given": 5
}
```

**Progression Logic**:

- XP increases with goal completion and meaningful interactions
- Trust score increases when user follows through on commitments
- Closeness score increases with vulnerability and deep conversations
- Motivation effectiveness tracked by success rate after Eliza's suggestions
- Each level unlocks new interaction types (dating unlocks romantic storylines, deeper conversations)

### 2.2 Dynamic Mission System

**Mission Model**

```python
# packages/backend/app/models/mission.py
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey, Enum
import enum

class MissionType(str, enum.Enum):
    GROWTH = "growth"      # Learning, reading, courses
    HEALTH = "health"      # Exercise, meditation, sleep
    CRAFT = "craft"        # Work, projects, creation
    CONNECTION = "connection"  # Social, relationships, networking

class MissionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"

class Mission(Base):
    __tablename__ = "missions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    goal_id = Column(String, ForeignKey("goals.id"), nullable=True)

    # Mission details
    title = Column(String(500), nullable=False)
    description = Column(String(2000))
    mission_type = Column(Enum(MissionType), nullable=False)
    status = Column(Enum(MissionStatus), default=MissionStatus.PENDING)

    # Time tracking
    estimated_minutes = Column(Integer, default=30)
    actual_minutes = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)

    # Gamification
    essence_reward = Column(Integer, default=20)  # Currency earned
    xp_reward = Column(Integer, default=15)

    # Evidence
    has_evidence = Column(Boolean, default=False)
    evidence_urls = Column(JSON, default=list)  # List of S3 URLs

    # Metadata
    order_index = Column(Integer, default=0)  # For priority sorting
    metadata = Column(JSON, default=dict)  # Flexible storage
```

### 2.3 Evidence Capture & Highlight Reels

**Highlight Reel Generation**

```python
# packages/backend/app/services/highlight_service.py
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip

class HighlightReelService:
    """
    Generates cinematic highlight reels from completed missions.

    Reel structure:
    - Opening title: "Your Week in Review"
    - For each mission with evidence:
      - Photo with subtle zoom
      - Mission title overlay
      - Essence earned animation
    - Closing stats: Total Essence, Streak, Level up
    - Duration: 30-60 seconds
    """

    async def generate_weekly_reel(
        self,
        user_id: str,
        week_start: datetime
    ) -> str:
        """
        Generate highlight reel for the past week.

        Returns: URL to video file
        """

        # 1. Fetch completed missions with evidence
        missions = await self.db.execute(
            select(Mission).where(
                Mission.user_id == user_id,
                Mission.completed_at >= week_start,
                Mission.has_evidence == True
            )
        )
        missions = missions.scalars().all()

        if not missions:
            return None  # No evidence to make a reel

        clips = []

        # Opening title
        title_clip = TextClip(
            "Your Week in Review",
            fontsize=70,
            color="white",
            size=(1920, 1080),
            bg_color="black"
        ).set_duration(2)
        clips.append(title_clip)

        # For each mission, create a clip
        for mission in missions[:10]:  # Max 10 missions
            image_path = await self._download_image(mission.evidence_urls[0])

            # Create image clip with zoom effect
            img_clip = (
                ImageClip(image_path)
                .set_duration(3)
                .resize(height=1080)
                .set_position("center")
                .fx(vfx.zoom, zoom_factor=1.2)  # Subtle zoom
            )

            # Add mission title overlay
            title = TextClip(
                mission.title,
                fontsize=50,
                color="white",
                font="Arial-Bold"
            ).set_duration(3).set_position(("center", 900))

            # Composite
            composite = CompositeVideoClip([img_clip, title])
            clips.append(composite)

        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose")

        # Export
        output_path = f"/tmp/{user_id}_week_{week_start.strftime('%Y%m%d')}.mp4"
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec="libx264"
        )

        # Upload to S3
        s3_url = await self.storage.upload_file(
            output_path,
            bucket="highlight-reels",
            key=f"{user_id}/reels/week_{week_start.strftime('%Y%m%d')}.mp4"
        )

        return s3_url
```

**Background Job**: Trigger reel generation every Sunday night via Celery task.

### 2.4 Living World with Time Dynamics

**Time-Based State System**

```python
# packages/backend/app/core/world/time_system.py
from datetime import datetime, time
from enum import Enum

class TimeOfDay(str, Enum):
    MORNING = "morning"      # 6am - 12pm
    AFTERNOON = "afternoon"  # 12pm - 6pm
    EVENING = "evening"      # 6pm - 10pm
    NIGHT = "night"          # 10pm - 6am

class WorldState:
    """
    Manages world state based on real-world time.

    Features:
    - Zone availability (Arena closes at night)
    - NPC behavior (Thorne only in Arena during morning/afternoon)
    - Mission availability (morning missions vs evening missions)
    - User override for night workers
    """

    def __init__(self, user_timezone: str = "UTC"):
        self.user_timezone = user_timezone

    def get_current_time_of_day(self) -> TimeOfDay:
        """Determine current time of day in user's timezone"""

        now = datetime.now(pytz.timezone(self.user_timezone))
        current_time = now.time()

        if time(6, 0) <= current_time < time(12, 0):
            return TimeOfDay.MORNING
        elif time(12, 0) <= current_time < time(18, 0):
            return TimeOfDay.AFTERNOON
        elif time(18, 0) <= current_time < time(22, 0):
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def generate_time_based_greeting(
        self,
        time_of_day: TimeOfDay,
        scenario: str = "modern_reality"
    ) -> str:
        """Generate contextual greeting based on time"""

        greetings = {
            "modern_reality": {
                TimeOfDay.MORNING: "Good morning! The city's waking up. Coffee shops are opening. Ready to start your day?",
                TimeOfDay.AFTERNOON: "Afternoon! Most people are deep in work. How's your momentum?",
                TimeOfDay.EVENING: "Evening. The city's winding down. Time to reflect on today and plan tomorrow?",
                TimeOfDay.NIGHT: "Late night. Most have gone home. Burning the midnight oil, or wrapping up?"
            }
        }

        return greetings[scenario][time_of_day]
```

### 2.5 Character-Initiated Interactions

**Proactive Companion System**

```python
# packages/backend/app/services/proactive_service.py
from enum import Enum

class TriggerType(str, Enum):
    TIME_BASED = "time_based"           # Morning greeting, evening reflection
    EVENT_BASED = "event_based"         # Goal achieved, streak milestone
    PATTERN_BASED = "pattern_based"     # User seems stuck, long absence
    STORY_BASED = "story_based"         # Hidden quest unlocked

class ProactiveService:
    """
    Manages character-initiated interactions.

    Characters can:
    1. Check in on user's well-being
    2. Suggest new goals or activities
    3. Offer quests
    4. Celebrate achievements
    5. Trigger story events
    """

    async def check_and_trigger_interactions(self, user_id: str):
        """
        Main scheduler function. Called periodically (e.g., every hour).

        Checks:
        1. Is it time for a scheduled interaction?
        2. Did user achieve something worth celebrating?
        3. Has user been gone for a while?
        4. Is user stuck on a goal?
        5. Are there hidden quests to reveal?
        """

        # Check all trigger types
        time_triggers = await self._check_time_triggers(user_id)
        event_triggers = await self._check_event_triggers(user_id)
        pattern_triggers = await self._check_pattern_triggers(user_id)
        story_triggers = await self._check_story_triggers(user_id)

        # Prioritize and execute one trigger
        all_triggers = time_triggers + event_triggers + pattern_triggers + story_triggers

        if not all_triggers:
            return

        # Sort by priority
        trigger = max(all_triggers, key=lambda t: t["priority"])

        # Generate and send interaction
        await self._execute_trigger(user_id, trigger)
```

---

## Part 3: Frontend Implementation

### 3.1 Component Architecture

**Main Layout**

```tsx
// frontend/app/(main)/layout.tsx
import { Sidebar } from "@/components/layout/Sidebar";
import { CompanionPanel } from "@/components/companion/CompanionPanel";
import { WorldHeader } from "@/components/world/WorldHeader";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left sidebar: Navigation */}
      <Sidebar />

      {/* Main content area */}
      <main className="flex-1 overflow-auto">
        <WorldHeader />
        {children}
      </main>

      {/* Right panel: Eliza companion (collapsible) */}
      <CompanionPanel />
    </div>
  );
}
```

**Dashboard Component**

```tsx
// frontend/app/(main)/dashboard/page.tsx
"use client";

import { MissionCard } from "@/components/missions/MissionCard";
import { ProgressRing } from "@/components/gamification/ProgressRing";
import { StreakDisplay } from "@/components/gamification/StreakDisplay";
import { useQuery } from "@tanstack/react-query";

export default function DashboardPage() {
  const { data: dailyMissions } = useQuery({
    queryKey: ["missions", "today"],
    queryFn: () => fetch("/api/v1/missions/today").then((r) => r.json()),
  });

  const { data: userStats } = useQuery({
    queryKey: ["user", "stats"],
    queryFn: () => fetch("/api/v1/users/me/stats").then((r) => r.json()),
  });

  return (
    <div className="p-6 space-y-8">
      {/* Header with greeting and stats */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Today's Focus</h1>
          <p className="text-gray-600 mt-1">
            {dailyMissions?.length || 0} missions waiting
          </p>
        </div>

        {/* Quick stats */}
        <div className="flex items-center gap-6">
          <StreakDisplay streak={userStats?.streak || 0} />
          <ProgressRing
            current={userStats?.xp_today || 0}
            total={userStats?.xp_goal || 100}
            label="Today's XP"
          />
        </div>
      </div>

      {/* Mission cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dailyMissions?.map((mission) => (
          <MissionCard key={mission.id} mission={mission} />
        ))}
      </div>

      {/* Attributes overview */}
      <AttributesOverview stats={userStats?.attributes} />
    </div>
  );
}
```

**Companion Chat Interface**

```tsx
// frontend/components/companion/CompanionPanel.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Mic, Paperclip } from "lucide-react";
import { useChat } from "@/hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

export function CompanionPanel() {
  const [message, setMessage] = useState("");
  const { messages, sendMessage, isLoading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!message.trim()) return;

    await sendMessage(message);
    setMessage("");
  };

  return (
    <aside className="w-96 bg-white border-l border-gray-200 flex flex-col">
      {/* Companion header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center">
            <span className="text-white font-semibold">E</span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Eliza</h3>
            <p className="text-xs text-gray-500">Your companion</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <MessageBubble
            key={idx}
            message={msg.content}
            role={msg.role}
            timestamp={msg.timestamp}
          />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Message Eliza..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            className="p-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
```

**Mission Card Component**

```tsx
// frontend/components/missions/MissionCard.tsx
"use client";

import { Play, Check, Clock, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface Mission {
  id: string;
  title: string;
  description: string;
  mission_type: "growth" | "health" | "craft" | "connection";
  estimated_minutes: number;
  essence_reward: number;
  status: string;
}

export function MissionCard({ mission }: { mission: Mission }) {
  const queryClient = useQueryClient();

  const startMission = useMutation({
    mutationFn: (missionId: string) =>
      fetch(`/api/v1/missions/${missionId}/start`, { method: "POST" }).then(
        (r) => r.json()
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["missions"] });
    },
  });

  const typeColors = {
    growth: "bg-blue-500",
    health: "bg-green-500",
    craft: "bg-purple-500",
    connection: "bg-pink-500",
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 cursor-pointer"
    >
      {/* Type badge */}
      <div
        className={`inline-block px-3 py-1 rounded-full text-xs font-medium text-white ${
          typeColors[mission.mission_type]
        } mb-4`}
      >
        {mission.mission_type}
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {mission.title}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
        {mission.description}
      </p>

      {/* Meta info */}
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div className="flex items-center gap-1">
          <Clock className="w-4 h-4" />
          <span>{mission.estimated_minutes} min</span>
        </div>
        <div className="flex items-center gap-1">
          <Zap className="w-4 h-4 text-yellow-500" />
          <span className="font-medium">+{mission.essence_reward}</span>
        </div>
      </div>

      {/* Action button */}
      <button
        onClick={() => startMission.mutate(mission.id)}
        className="w-full py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center justify-center gap-2"
      >
        <Play className="w-4 h-4" />
        Start Mission
      </button>
    </motion.div>
  );
}
```

### 3.2 Real-Time Updates with WebSockets

```tsx
// frontend/hooks/useWebSocket.ts
import { useEffect, useState } from "use";
import { io, Socket } from "socket.io-client";

export function useWebSocket(userId: string) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(process.env.NEXT_PUBLIC_WS_URL, {
      auth: {
        userId,
      },
    });

    newSocket.on("connect", () => {
      setIsConnected(true);
    });

    newSocket.on("disconnect", () => {
      setIsConnected(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [userId]);

  return { socket, isConnected };
}

// Usage in component
export function DashboardPage() {
  const { socket } = useWebSocket(userId);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!socket) return;

    // Listen for proactive messages
    socket.on("proactive_message", (data) => {
      // Show notification
      showNotification(data.message);
      // Invalidate queries to refresh UI
      queryClient.invalidateQueries({ queryKey: ["messages"] });
    });

    // Listen for mission updates
    socket.on("mission_updated", () => {
      queryClient.invalidateQueries({ queryKey: ["missions"] });
    });

    return () => {
      socket.off("proactive_message");
      socket.off("mission_updated");
    };
  }, [socket]);
}
```

---

## Part 4: Gamification System

### 4.1 Attribute System (Growth, Health, Craft, Connection)

**Database Models**

```python
# packages/backend/app/models/attributes.py
class UserAttribute(Base):
    __tablename__ = "user_attributes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    attribute_type = Column(Enum("growth", "health", "craft", "connection"), nullable=False)

    # Progression
    level = Column(Integer, default=1)
    current_xp = Column(Integer, default=0)
    xp_to_next_level = Column(Integer, default=100)

    # Stats
    total_missions_completed = Column(Integer, default=0)
    total_time_invested_minutes = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Level-Up Calculation**

```python
# packages/backend/app/services/progression_service.py
class ProgressionService:
    """Manages attribute leveling and progression"""

    XP_BASE = 100
    XP_MULTIPLIER = 1.5

    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP required to reach a level"""
        return int(self.XP_BASE * (self.XP_MULTIPLIER ** (level - 1)))

    async def add_xp(
        self,
        user_id: str,
        attribute_type: str,
        xp_amount: int
    ) -> Dict:
        """
        Add XP to attribute and handle level-ups.

        Returns:
        {
            "leveled_up": bool,
            "new_level": int,
            "rewards": List[str]
        }
        """

        # Get current attribute
        attr = await self.db.execute(
            select(UserAttribute).where(
                UserAttribute.user_id == user_id,
                UserAttribute.attribute_type == attribute_type
            )
        )
        attr = attr.scalar_one()

        # Add XP
        attr.current_xp += xp_amount

        # Check for level-up
        leveled_up = False
        new_rewards = []

        while attr.current_xp >= attr.xp_to_next_level:
            # Level up!
            attr.current_xp -= attr.xp_to_next_level
            attr.level += 1
            leveled_up = True

            # Calculate next level XP requirement
            attr.xp_to_next_level = self.calculate_xp_for_level(attr.level + 1)

            # Award level-up rewards
            rewards = await self._get_level_rewards(attribute_type, attr.level)
            new_rewards.extend(rewards)

        await self.db.commit()

        return {
            "leveled_up": leveled_up,
            "new_level": attr.level if leveled_up else None,
            "rewards": new_rewards
        }

    async def _get_level_rewards(self, attribute_type: str, level: int) -> List[str]:
        """Determine rewards for reaching a level"""

        rewards = []

        # Every 5 levels: unlock new features
        if level % 5 == 0:
            rewards.append(f"New {attribute_type} ability unlocked")

        # Every 10 levels: character story reveal
        if level % 10 == 0:
            rewards.append(f"Story chapter: {attribute_type.capitalize()} Master")

        # Essence rewards
        essence_reward = level * 50
        rewards.append(f"+{essence_reward} Essence")

        return rewards
```

### 4.2 Essence Currency System

**Earning & Spending**

```python
# packages/backend/app/models/economy.py
class EssenceTransaction(Base):
    __tablename__ = "essence_transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    amount = Column(Integer, nullable=False)  # Positive for earning, negative for spending
    transaction_type = Column(String, nullable=False)  # mission_complete, purchase, gift

    # References
    mission_id = Column(String, ForeignKey("missions.id"), nullable=True)
    purchase_id = Column(String, nullable=True)

    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserBalance(Base):
    __tablename__ = "user_balances"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    essence_balance = Column(Integer, default=0)
    lifetime_essence_earned = Column(Integer, default=0)
    lifetime_essence_spent = Column(Integer, default=0)
```

**Shop System (Future)**

Items users can purchase with Essence:

- **Cosmetics**: Companion appearance customization, UI themes
- **Boosters**: Double XP for 1 day, instant quest refresh
- **Story Unlocks**: Side quests, character backstories
- **Utilities**: Extra mission slots, priority planning AI

### 4.3 Streak System

**Implementation**

```python
# packages/backend/app/services/streak_service.py
class StreakService:
    """Manages user streaks for daily engagement"""

    async def check_and_update_streak(self, user_id: str) -> int:
        """
        Check if user has maintained streak today.
        Update streak count.

        Returns: Current streak
        """

        user = await self.db.get(User, user_id)
        today = datetime.now(timezone.utc).date()

        # Get last activity date
        last_activity = user.last_activity_date

        if not last_activity:
            # First time
            user.current_streak = 1
            user.longest_streak = 1
            user.last_activity_date = today

        elif last_activity == today:
            # Already counted today
            pass

        elif last_activity == today - timedelta(days=1):
            # Streak continues!
            user.current_streak += 1
            user.last_activity_date = today

            # Update longest streak if needed
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak

            # Reward for milestone streaks
            if user.current_streak in [7, 30, 100]:
                await self._award_streak_milestone(user_id, user.current_streak)

        else:
            # Streak broken
            user.current_streak = 1
            user.last_activity_date = today

        await self.db.commit()
        return user.current_streak

    async def _award_streak_milestone(self, user_id: str, streak: int):
        """Award special rewards for streak milestones"""

        rewards = {
            7: {"essence": 100, "title": "Week Warrior"},
            30: {"essence": 500, "title": "Monthly Master"},
            100: {"essence": 2000, "title": "Centurion"}
        }

        reward = rewards.get(streak)
        if reward:
            # Award essence
            await self.economy.add_essence(
                user_id,
                reward["essence"],
                transaction_type="streak_milestone"
            )

            # Unlock achievement
            await self.achievements.unlock(
                user_id,
                f"streak_{streak}",
                title=reward["title"]
            )
```

### 4.4 Achievement System

**Achievement Definition**

```python
# packages/backend/app/models/achievements.py
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True)  # Unique code like "first_mission"

    # Display
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    icon_url = Column(String(500))

    # Rarity
    rarity = Column(Enum("common", "rare", "epic", "legendary"), default="common")

    # Requirements
    requirement_type = Column(String(100))  # mission_count, streak, attribute_level
    requirement_value = Column(Integer)

    # Rewards
    essence_reward = Column(Integer, default=0)

    # Metadata
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked
    order_index = Column(Integer, default=0)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id"), nullable=False)

    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged = Column(Boolean, default=False)  # Has user viewed it?
```

**Pre-Defined Achievements**

```python
ACHIEVEMENTS = [
    {
        "id": "first_mission",
        "title": "First Steps",
        "description": "Complete your first mission",
        "requirement_type": "mission_count",
        "requirement_value": 1,
        "rarity": "common",
        "essence_reward": 50
    },
    {
        "id": "week_warrior",
        "title": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "requirement_type": "streak",
        "requirement_value": 7,
        "rarity": "rare",
        "essence_reward": 100
    },
    {
        "id": "growth_master",
        "title": "Growth Master",
        "description": "Reach Growth Level 10",
        "requirement_type": "attribute_level",
        "requirement_value": 10,
        "rarity": "epic",
        "essence_reward": 200
    },
    {
        "id": "overachiever",
        "title": "Overachiever",
        "description": "Complete 10 missions in one day",
        "requirement_type": "daily_mission_count",
        "requirement_value": 10,
        "rarity": "epic",
        "essence_reward": 300
    }
]
```

---

## Part 5: Story & Narrative System

### 5.1 Story Structure

**Narrative Layers**:

1. **Personal Story Arc**: User's journey from novice to master
2. **Relationship Story**: Deepening bond with Eliza
3. **World Story**: Evolving state of the world based on collective user actions
4. **Side Quests**: Optional character-driven missions

### 5.2 Story Generation with GPT-4

```python
# packages/backend/app/services/story_service.py
class StoryService:
    """Generates personalized narrative content"""

    def __init__(self, llm: ChatOpenAI, memory: HybridRetriever):
        self.llm = llm  # GPT-4 for creativity
        self.memory = memory

    async def generate_mission_narrative(
        self,
        mission: Mission,
        user_context: str,
        world_state: Dict
    ) -> str:
        """
        Transform a mundane task into a narrative mission.

        Example:
        Task: "Practice coding for 30 minutes"
        Narrative: "The ancient tome of algorithms awaits. Commander Thorne
                   challenges you to master the arcane art of recursion..."
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a master storyteller creating epic narratives.
Transform the user's real-world task into an engaging mission description.

Style:
- Epic but not cringe
- Relevant to their actual goal
- References their progress and context
- Matches the world's tone (modern fantasy)

World state: {world_state}
User context: {user_context}"""),
            ("human", "Transform this task into a mission:\n{task}")
        ])

        response = await self.llm.ainvoke(
            prompt.format(
                world_state=json.dumps(world_state),
                user_context=user_context,
                task=f"{mission.title}: {mission.description}"
            )
        )

        return response.content

    async def generate_completion_story(
        self,
        mission: Mission,
        user_stats: Dict
    ) -> str:
        """Generate celebratory narrative for completing a mission"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a short, celebratory narrative for mission completion.
Reference their progress and make them feel like a hero.

2-3 sentences max."""),
            ("human", """User completed: {mission}
Current stats: Level {level}, Streak {streak}

Write a celebration:""")
        ])

        response = await self.llm.ainvoke(
            prompt.format(
                mission=mission.title,
                level=user_stats.get("level", 1),
                streak=user_stats.get("streak", 0)
            )
        )

        return response.content
```

### 5.3 Hidden Quests & Discovery

**Hidden Quest System**

```python
# packages/backend/app/models/quests.py
class HiddenQuest(Base):
    __tablename__ = "hidden_quests"

    id = Column(String, primary_key=True)

    # Display
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    narrative_intro = Column(String(2000))  # Story when revealed

    # Unlock conditions
    unlock_condition_type = Column(String(100))  # attribute_level, mission_count, etc.
    unlock_condition_value = Column(Integer)

    # Quest steps
    steps = Column(JSON)  # List of steps

    # Rewards
    essence_reward = Column(Integer)
    story_unlock = Column(String(500))  # What story content is revealed

    # Metadata
    character = Column(String(100))  # Which character offers this quest
    is_repeatable = Column(Boolean, default=False)

class UserQuestProgress(Base):
    __tablename__ = "user_quest_progress"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quest_id = Column(String, ForeignKey("hidden_quests.id"), nullable=False)

    # Progress
    current_step = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)

    # Timestamps
    revealed_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
```

**Example Hidden Quest**:

```python
HIDDEN_QUEST_EXAMPLE = {
    "id": "elisas_secret",
    "title": "Eliza's Secret",
    "description": "Eliza has something important to tell you.",
    "narrative_intro": """
    Late one evening, after weeks of working together, Eliza seems different.
    There's a weight in her words you haven't heard before.

    "I need to tell you something," she says. "About why I'm really here..."
    """,
    "unlock_condition_type": "relationship_level",
    "unlock_condition_value": 5,  # Close friend level
    "character": "eliza",
    "steps": [
        {
            "id": "step_1",
            "description": "Listen to Eliza's story",
            "type": "conversation"
        },
        {
            "id": "step_2",
            "description": "Complete 3 missions while reflecting on her words",
            "type": "mission_count",
            "requirement": 3
        },
        {
            "id": "step_3",
            "description": "Have a deep conversation about trust",
            "type": "conversation"
        }
    ],
    "essence_reward": 500,
    "story_unlock": "Eliza's backstory chapter 1"
}
```

---

## Part 6: Implementation Timeline (18 Weeks)

### Phase 1: Foundation (Weeks 1-4)

**Week 1: Project Setup & Infrastructure**

- [ ] Initialize monorepo structure
- [ ] Set up Docker Compose (Postgres, Redis, Qdrant)
- [ ] Configure FastAPI project with Poetry
- [ ] Set up Next.js with TypeScript and Tailwind
- [ ] Implement authentication (JWT)
- [ ] Basic CI/CD pipeline

**Week 2: Memory System Core**

- [ ] Integrate Mem0 SDK
- [ ] Implement PersonalMemory, ProjectMemory, TaskMemory classes
- [ ] Set up Qdrant for vector storage
- [ ] Build HybridRetriever
- [ ] Create memory API endpoints
- [ ] Test memory persistence and retrieval

**Week 3: Knowledge Graph & LangGraph**

- [ ] Implement NetworkX knowledge graph
- [ ] Build graph operations (add nodes, traverse, find paths)
- [ ] Set up LangGraph workflow
- [ ] Create basic agent state machine
- [ ] Test workflow execution

**Week 4: Database Models & APIs**

- [ ] Design all database schemas (users, missions, goals, achievements, etc.)
- [ ] Implement SQLAlchemy models
- [ ] Create Alembic migrations
- [ ] Build CRUD API endpoints
- [ ] Write API tests

**Deliverable**: Backend foundation with working memory system, authentication, and database.

### Phase 2: Core Features (Weeks 5-10)

**Week 5: Mission System**

- [ ] Implement Mission model and service
- [ ] Build mission generation logic (AI-assisted)
- [ ] Create mission CRUD APIs
- [ ] Implement mission state machine (pending → in_progress → completed)
- [ ] Test mission workflow

**Week 6: Companion Intelligence (Eliza)**

- [ ] Implement Eliza personality system
- [ ] Set up Claude integration
- [ ] Build conversation API with streaming
- [ ] Implement emotional state detection
- [ ] Test companion responses

**Week 7: Gamification Core**

- [ ] Implement attribute system (Growth, Health, Craft, Connection)
- [ ] Build progression service (XP, leveling)
- [ ] Create essence economy
- [ ] Implement streak tracking
- [ ] Build achievement system

**Week 8: Evidence Capture**

- [ ] Set up file upload API
- [ ] Implement S3/MinIO storage
- [ ] Build thumbnail generation
- [ ] Link evidence to missions
- [ ] Test image upload flow

**Week 9: Proactive System**

- [ ] Implement ProactiveService
- [ ] Build trigger detection logic
- [ ] Set up Celery for background jobs
- [ ] Configure APScheduler
- [ ] Implement notification service

**Week 10: Time-Based World**

- [ ] Implement WorldState and time system
- [ ] Build zone availability logic
- [ ] Create NPC schedule system
- [ ] Generate time-based greetings
- [ ] Test world dynamics

**Deliverable**: Fully functional backend with all core features.

### Phase 3: Frontend & UX (Weeks 11-14)

**Week 11: Frontend Foundation**

- [ ] Set up Next.js App Router
- [ ] Implement design system with shadcn/ui
- [ ] Build main layout (sidebar, header, companion panel)
- [ ] Create authentication UI
- [ ] Set up React Query for server state

**Week 12: Dashboard & Missions**

- [ ] Build dashboard page
- [ ] Create MissionCard component
- [ ] Implement mission list views
- [ ] Build mission detail modal
- [ ] Add mission start/complete actions

**Week 13: Companion Chat Interface**

- [ ] Build CompanionPanel component
- [ ] Implement chat message bubbles
- [ ] Add streaming response UI
- [ ] Create typing indicator
- [ ] Build voice input (optional)

**Week 14: Gamification UI**

- [ ] Build attribute progress displays
- [ ] Create StreakDisplay component
- [ ] Implement achievement showcase
- [ ] Design level-up celebration modal
- [ ] Add essence balance display

**Deliverable**: Complete frontend with all core user flows.

### Phase 4: Integration & Polish (Weeks 15-16)

**Week 15: Full Integration**

- [ ] Connect frontend to all backend APIs
- [ ] Implement WebSocket for real-time updates
- [ ] Build notification system
- [ ] Add error handling and retry logic
- [ ] Optimize API performance

**Week 16: Testing & Bug Fixes**

- [ ] Write E2E tests with Playwright
- [ ] Conduct user testing with 5-10 people
- [ ] Fix critical bugs
- [ ] Optimize memory retrieval performance
- [ ] Polish animations and transitions

**Deliverable**: Stable, tested MVP ready for pilot.

### Phase 5: Deployment & Pilot (Weeks 17-18)

**Week 17: Deployment**

- [ ] Set up production infrastructure (Railway/AWS)
- [ ] Configure environment variables and secrets
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure backups
- [ ] Test deployment pipeline
- [ ] Deploy MVP to production

**Week 18: Soft Launch & Iteration**

- [ ] Onboard 20-30 pilot users
- [ ] Monitor usage and collect feedback
- [ ] Set up analytics dashboards
- [ ] Fix high-priority issues
- [ ] Prepare for public beta

**Deliverable**: Delight MVP live with pilot users.

---

## Part 7: Success Metrics & Validation

### 7.1 Primary Metrics

**Engagement**:

- Day-7 retention: ≥65%
- Session frequency: ≥4 sessions/week
- Session duration: 10-20 minutes average

**Memory & Personalization**:

- Memory hit rate: ≥90% of sessions
- Conversation quality rating: ≥4/5

**Productivity**:

- Mission completion rate: ≥75%
- Time to first win: <24 hours

**Emotional**:

- Emotional support rating: ≥4/5
- Story engagement: ≥50% explore narrative

### 7.2 Cost Metrics

**Per-User Daily Costs**:

- LLM API calls: $0.03-0.06
- Vector DB operations: $0.01
- Storage & compute: $0.02
- **Total target**: <$0.10/day

**Optimization Strategies**:

- Cache frequent queries
- Use Haiku for simple tasks
- Batch operations
- Implement request throttling

---

## Part 8: Risk Mitigation

### 8.1 Technical Risks

**Risk**: AI costs exceed budget

- **Mitigation**: Aggressive caching, model routing, per-user quotas
- **Monitoring**: Daily cost dashboard

**Risk**: Memory system doesn't scale

- **Mitigation**: Optimize queries, implement tiered storage
- **Fallback**: Simplify retrieval, reduce context

**Risk**: LLM quality inconsistency

- **Mitigation**: Extensive prompt testing, fallback models
- **Fallback**: Template-based responses

### 8.2 Product Risks

**Risk**: Gamification feels gimmicky

- **Mitigation**: User testing, toggle option
- **Pivot**: Simplify narrative, focus on core

**Risk**: Users don't attach to companion

- **Mitigation**: Personality testing, customization
- **Pivot**: De-emphasize companion, focus on memory

---

## Part 9: Post-MVP Roadmap

### Phase 2: Enhanced Narrative (Months 2-3)

- Branching story paths
- Multiple companions
- Expanded world map
- Seasonal content

### Phase 3: Social Features (Months 4-5)

- Accountability partners
- Guild system
- Collaborative quests
- Community challenges

### Phase 4: Advanced AI (Months 6-8)

- Multimodal (voice, images)
- Proactive suggestions
- Calendar/tool integrations
- Advanced analytics

### Phase 5: Monetization (Months 9-12)

- Freemium model ($10-15/month)
- Premium features
- Team/enterprise plans
- Target: $5K-10K MRR by Month 12

---

## Part 10: Getting Started

### 10.1 Immediate Next Steps

**Project Setup**:

- [ ] Clone/create repository
- [ ] Set up development environment
- [ ] Obtain API keys (OpenAI, Anthropic)
- [ ] Configure local databases

**Design**:

- [ ] Finalize color palette
- [ ] Create design system
- [ ] Sketch core user flows

**Team**:

- [ ] Share plan with collaborators
- [ ] Set up communication channels
- [ ] Schedule weekly syncs

### 10.2 First Sprint (Week 1)

**Backend**:

- [ ] FastAPI project structure
- [ ] PostgreSQL + Redis setup
- [ ] Basic authentication
- [ ] Health check endpoint

**Frontend**:

- [ ] Next.js scaffold
- [ ] Tailwind configuration
- [ ] Login page
- [ ] Basic layout

**Deliverable**: Can create account, log in, see empty dashboard.

---

## Conclusion

This comprehensive 18-week plan provides a complete roadmap to building Delight MVP with:

✅ **Sophisticated AI** via 3-tier memory, knowledge graphs, and LangGraph orchestration  
✅ **Emotional Intelligence** through Eliza's adaptive personality and proactive engagement  
✅ **Deep Gamification** with attributes, streaks, evidence capture, and highlight reels  
✅ **Living World** that evolves with real-world time and user actions  
✅ **Production-Ready Stack** optimized for cost (<$0.10/user/day) and scale

### Success Factors

- Focus on core user loop: Mission → Complete → Celebrate → Repeat
- Prioritize memory quality over quantity
- Make Eliza feel genuinely supportive
- Balance narrative immersion with productivity utility
- Track metrics religiously, iterate based on data

### The North Star

When users open Delight, they should feel:

1. **Remembered**: "It knows where I left off"
2. **Supported**: "Eliza understands what I'm going through"
3. **Motivated**: "I want to complete this mission"
4. **Celebrated**: "My wins matter"

If we achieve this, retention and growth will follow.

**Let's build something that ambitious people love—a tool that helps them transform their lives, one mission at a time.**

---

**Document Version**: 2.0 (Research-Enhanced)  
**Last Updated**: November 9, 2025  
**Status**: Ready for Implementation  
**Target**: 18-week MVP to Beta Launch  
**Next Review**: After Week 2 sprint
