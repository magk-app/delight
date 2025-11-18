# Hierarchical Memory and Adaptive State Management for Delight

**Date:** 2025-11-18
**Epic:** Epic 2 - Companion & Memory System
**Purpose:** Design specification for implementing hierarchical memory and adaptive state management in Delight's AI agent system

---

## Executive Summary

This document series outlines how Delight incorporates **hierarchical memory architecture** and **adaptive state management** to create an emotionally intelligent AI companion that remembers context, learns from interactions, and orchestrates complex multi-step workflows transparently.

The system builds on Delight's core mission: **transforming overwhelming goals into achievable daily missions** through emotionally aware AI coaching, narrative world-building, and adaptive quest generation.

---

## Why Hierarchical Memory for Delight?

Delight's AI companion (Eliza) must maintain different levels of context simultaneously:

### The Challenge
- **Long-term identity**: User preferences, emotional patterns, life context (weeks/months)
- **Medium-term projects**: Current goals, ongoing ambitions, progress snapshots (days/weeks)
- **Short-term tasks**: Today's mission, current conversation, immediate emotional state (hours/minutes)

Without proper memory partitioning, the AI either:
1. **Forgets everything** between sessions (poor continuity)
2. **Drowns in irrelevant context** (slow, unfocused responses)
3. **Mixes up timeframes** (confuses yesterday's mood with last month's goal)

### The Solution: 3-Tier Hierarchical Memory

Delight implements **Personal**, **Project**, and **Task** memory tiers that align perfectly with the user's journey:

```
┌─────────────────────────────────────────────────────────────┐
│ PERSONAL MEMORY (Long-term, global context)                 │
│ - User identity, values, communication preferences          │
│ - Emotional patterns learned over time                      │
│ - Core goals and "why" behind ambitions                     │
│ - Relationship with Eliza and character personas            │
│ Duration: Permanent (updated, never deleted)                │
└─────────────────────────────────────────────────────────────┘
              │
              ├──────────────────────────────────────────────┐
              │                                              │
┌─────────────▼──────────────────┐   ┌────────────────────▼──┐
│ PROJECT MEMORY (Medium-term)   │   │ PROJECT MEMORY        │
│ - Active goal: "Run marathon"  │   │ - Goal: "Learn piano" │
│ - Milestones, decomposition    │   │ - Practice schedule   │
│ - Progress snapshots           │   │ - Technique notes     │
│ - Domain-specific knowledge    │   │ - Repertoire tracking │
│ Duration: Life of project      │   │ Duration: Ongoing     │
└────────────────────────────────┘   └───────────────────────┘
              │                                   │
    ┌─────────┴────────┐                ┌────────┴────────┐
    │                  │                │                 │
┌───▼──────┐  ┌────────▼─────┐  ┌──────▼───┐  ┌─────────▼──┐
│ TASK MEM │  │  TASK MEMORY │  │ TASK MEM │  │ TASK MEMORY│
│ Today's  │  │  Yesterday's │  │ Practice │  │ Theory quiz│
│ 5km run  │  │  recovery    │  │ session  │  │ prep       │
│ Duration:│  │  Duration:   │  │ Duration:│  │ Duration:  │
│ 24-48hrs │  │  pruned @30d │  │ 24hrs    │  │ pruned @30d│
└──────────┘  └──────────────┘  └──────────┘  └────────────┘
```

---

## How This Aligns with Delight's Architecture

### Epic 2: Companion & Memory System

The hierarchical memory system directly supports Epic 2 stories:

| Story | Memory Component | How Hierarchical Memory Enhances It |
|-------|------------------|-------------------------------------|
| **2.1: PostgreSQL pgvector** | Foundation | Graph-structured vector storage for fast, relevant retrieval |
| **2.2: 3-Tier Memory Service** | Core Implementation | Personal/Project/Task partitions with smart retrieval |
| **2.3: Eliza Agent (LangGraph)** | State Management | Goal-driven state transitions with memory-aware nodes |
| **2.4: Chat API with SSE** | Real-time Orchestration | Multi-step prompting (parallel + sequential) for responses |
| **2.5: Chat UI** | Transparency | Node-based workflow planning visible to user |
| **2.6: Emotional State Detection** | Continuous Learning | Updates personal memory with emotional patterns |
| **2.7: Character Personas** | Multi-Character Memory | Separate memory namespaces per character |

### Integration with Other Epics

**Epic 3 (Goal & Mission Management):**
- Project memory stores goal decomposition
- Task memory tracks current mission context
- Node-based workflow planning for quest generation

**Epic 4 (Narrative Engine):**
- Personal memory influences narrative theme selection
- Project memory tracks story progression
- Graph-based retrieval finds relevant narrative beats

**Epic 5 (Progress & Analytics):**
- Historical memory snapshots for DCI calculation
- Pattern recognition from task memory consolidation

---

## Key Concepts Adapted for Delight

### 1. Memory Partitions
**Article Concept**: Personal, Project, Task memory tiers
**Delight Implementation**:
- Personal: `personal_memories` table with user identity, emotional patterns
- Project: `project_memories` table linked to goals
- Task: `task_memories` table linked to missions (auto-pruned after 30 days)

### 2. Goal-Driven State Transitions
**Article Concept**: State machine with goals, constraints, tool awareness
**Delight Implementation**:
- Eliza's LangGraph agent nodes: `receive_input` → `recall_context` → `reason` → `respond` → `store_memory`
- Mission execution workflow: goal selection → planning → execution → reflection
- Character-initiated interactions based on user patterns

### 3. Graph-Based Hierarchical Retrieval
**Article Concept**: Knowledge graph with fast routing + semantic search
**Delight Implementation**:
- PostgreSQL graph structure: goals → milestones → missions
- Vector search within relevant subgraph (e.g., search memories within current goal's project)
- Hybrid retrieval: metadata filters + semantic similarity

### 4. Multi-Step Prompting
**Article Concept**: Parallel + sequential task execution
**Delight Implementation**:
- **Parallel**: Emotion detection + memory retrieval + context gathering (simultaneous)
- **Sequential**: Plan mission → decompose steps → generate quest content → validate
- ARQ workers for background multi-step workflows (quest generation, nudge scheduling)

### 5. Node-Based Workflow Planning
**Article Concept**: Visualize AI's plan as graph of nodes
**Delight Implementation**:
- Show user Eliza's reasoning process: "Here's how I'll help with your goal..."
- Mission decomposition displayed as flowchart
- Milestone updates as progress through workflow nodes

### 6. Continuous Memory Updates
**Article Concept**: Learn from interactions, update graph + vectors
**Delight Implementation**:
- After each conversation: extract key learnings → personal memory
- After mission completion: notes → task memory
- Weekly consolidation: summarize project progress → project memory

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ DELIGHT AI AGENT SYSTEM                                          │
│ (Hierarchical Memory + Adaptive State Management)               │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
│ MEMORY LAYER   │  │  STATE LAYER     │  │ ORCHESTRATION   │
│                │  │                  │  │ LAYER           │
│ 3-Tier Storage │  │ Goal-Driven FSM  │  │ Multi-Step      │
│ Graph Retrieval│  │ Tool-Aware       │  │ Workflow Nodes  │
│ Vector Search  │  │ Context Tracking │  │ Parallel/Serial │
└────────────────┘  └──────────────────┘  └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼────────┐
                    │ ELIZA AGENT      │
                    │ (LangGraph)      │
                    │                  │
                    │ Nodes:           │
                    │ - Receive Input  │
                    │ - Recall Memory  │
                    │ - Reason/Plan    │
                    │ - Respond        │
                    │ - Store Learning │
                    └──────────────────┘
```

---

## Documentation Structure

This documentation series is organized into implementation-focused guides:

1. **01-OVERVIEW.md** (this document) - Context and alignment with Delight
2. **02-MEMORY-ARCHITECTURE.md** - Detailed 3-tier + graph structure design
3. **03-STATE-MANAGEMENT.md** - Goal-driven state transitions and tool orchestration
4. **04-RETRIEVAL-STRATEGY.md** - Graph-based hierarchical retrieval implementation
5. **05-MULTI-STEP-ORCHESTRATION.md** - Parallel vs sequential prompting patterns
6. **06-WORKFLOW-PLANNING.md** - Node-based planning for transparency
7. **07-IMPLEMENTATION-GUIDE.md** - Code examples, schemas, practical integration

---

## Design Principles for Delight's Memory System

### 1. **Emotional Intelligence First**
Memory system must prioritize emotional context:
- Personal memory stores emotional patterns (what helps when user is overwhelmed)
- Retrieval biases toward emotionally relevant memories
- State transitions account for current emotional state

### 2. **Narrative Coherence**
Memory supports storytelling:
- Project memory maintains narrative consistency (character relationships, world state)
- Graph structure prevents inconsistencies (can't reference unlocked zones)
- Continuous updates feed narrative progression

### 3. **User Transparency**
No black box AI:
- Show user what Eliza remembers ("I recall you mentioned...")
- Visualize workflow planning ("Here's my plan: Step 1...")
- Allow memory editing/deletion (user control)

### 4. **Performance Under Constraints**
Cost target: $0.50/user/day:
- Efficient retrieval (graph routing reduces vector search scope)
- Smart pruning (task memory auto-deleted after 30 days)
- Batched updates (consolidate memory writes)

### 5. **Privacy and Security**
User data protection:
- Memory isolated by user_id
- Encryption at rest (PostgreSQL/Supabase)
- Export/delete capabilities (GDPR compliance)

---

## Success Criteria

The hierarchical memory system is successful when:

✅ **Continuity**: Eliza remembers conversations across sessions without prompting
✅ **Relevance**: Retrieved memories match current context (not random past details)
✅ **Speed**: Memory retrieval < 100ms (doesn't slow down responses)
✅ **Learning**: Personal memory improves recommendations over time
✅ **Transparency**: User can see what Eliza remembers and why
✅ **Cost**: Memory operations stay within $0.03/user/day budget

---

## Next Steps

1. **Read**: Review documents 02-07 for detailed specifications
2. **Implement**: Follow implementation guide (07) for code integration
3. **Test**: Validate memory retrieval, state transitions, workflow planning
4. **Iterate**: Refine based on user feedback and performance metrics

---

## References

- **Original Article**: "Hierarchical Memory and Adaptive State Management for an AI Agent" by Jack Luo
- **Delight Architecture**: `/docs/ARCHITECTURE.md`
- **Epic 2 Stories**: `/docs/epics.md` (Epic 2: Companion & Memory System)
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **PostgreSQL pgvector**: https://github.com/pgvector/pgvector

---

**Last Updated**: 2025-11-18
**Status**: Design Documentation
**Maintainer**: Jack & Delight Team
