# Implementation Guide: Hierarchical Memory System

**Date:** 2025-11-18
**Epic:** Epic 2 - Companion & Memory System
**Purpose:** Step-by-step implementation guide with complete code examples

---

## Table of Contents

1. [Implementation Roadmap](#implementation-roadmap)
2. [Story 2.1: Database Setup](#story-21-database-setup)
3. [Story 2.2: Memory Service](#story-22-memory-service)
4. [Story 2.3: Eliza Agent with LangGraph](#story-23-eliza-agent-with-langgraph)
5. [Story 2.4: Chat API](#story-24-chat-api)
6. [Story 2.5: Frontend Integration](#story-25-frontend-integration)
7. [Testing and Validation](#testing-and-validation)
8. [Deployment Checklist](#deployment-checklist)

---

## Implementation Roadmap

### Overview

Implementing hierarchical memory follows Epic 2 stories in sequence:

```
Story 2.1: Database Schema (pgvector)
    ↓
Story 2.2: Memory Service (3-tier + graph)
    ↓
Story 2.3: Eliza Agent (LangGraph state machine)
    ↓
Story 2.4: Chat API (SSE streaming)
    ↓
Story 2.5: Frontend UI (React components)
```

**Estimated Timeline**: 3-4 weeks for MVP implementation

| Story | Focus | Duration | Dependencies |
|-------|-------|----------|--------------|
| 2.1 | Database schema, migrations | 2-3 days | Supabase setup |
| 2.2 | Memory CRUD, retrieval logic | 4-5 days | 2.1 complete |
| 2.3 | LangGraph agent, state management | 5-7 days | 2.2 complete |
| 2.4 | FastAPI endpoints, SSE streaming | 3-4 days | 2.3 complete |
| 2.5 | React components, UI integration | 4-5 days | 2.4 complete |

---

## Story 2.1: Database Setup

### Prerequisites

✅ Supabase project created
✅ Connection string added to `.env`
✅ Alembic initialized

### Step 1: Enable pgvector Extension

```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Create Migration

```bash
cd packages/backend
poetry run alembic revision -m "create hierarchical memory tables" --autogenerate
```

Edit the generated migration file:

```python
# backend/app/db/migrations/versions/XXXX_create_hierarchical_memory_tables.py

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

def upgrade():
    # Personal Memories
    op.create_table(
        'personal_memories',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Indexes
    op.create_index('idx_personal_memories_user', 'personal_memories', ['user_id'])
    op.create_index('idx_personal_memories_category', 'personal_memories', ['category'])
    op.create_index('idx_personal_memories_tags', 'personal_memories', ['tags'], postgresql_using='gin')

    # Vector index (HNSW)
    op.execute("""
        CREATE INDEX idx_personal_memories_embedding ON personal_memories
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    # Project Memories
    op.create_table(
        'project_memories',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE')
    )

    op.create_index('idx_project_memories_user', 'project_memories', ['user_id'])
    op.create_index('idx_project_memories_goal', 'project_memories', ['goal_id'])
    op.create_index('idx_project_memories_tags', 'project_memories', ['tags'], postgresql_using='gin')

    op.execute("""
        CREATE INDEX idx_project_memories_embedding ON project_memories
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    # Task Memories
    op.create_table(
        'task_memories',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('mission_id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE')
    )

    op.create_index('idx_task_memories_user', 'task_memories', ['user_id'])
    op.create_index('idx_task_memories_mission', 'task_memories', ['mission_id'])
    op.create_index('idx_task_memories_goal', 'task_memories', ['goal_id'])
    op.create_index('idx_task_memories_expires', 'task_memories', ['expires_at'])

    op.execute("""
        CREATE INDEX idx_task_memories_embedding ON task_memories
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

def downgrade():
    op.drop_table('task_memories')
    op.drop_table('project_memories')
    op.drop_table('personal_memories')
```

### Step 3: Run Migration

```bash
poetry run alembic upgrade head
```

### Step 4: Create SQLAlchemy Models

```python
# backend/app/models/memory.py

from sqlalchemy import Column, String, Text, Float, ARRAY, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from app.db.base import Base

class PersonalMemory(Base):
    __tablename__ = "personal_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    tags = Column(ARRAY(String), nullable=False, default=[])
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class ProjectMemory(Base):
    __tablename__ = "project_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    tags = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class TaskMemory(Base):
    __tablename__ = "task_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    tags = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
```

---

## Story 2.2: Memory Service

### Step 1: Embedding Service

```python
# backend/app/services/embedding_service.py

from openai import AsyncOpenAI
from app.core.config import settings
from functools import lru_cache

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_embedding(text: str) -> list[float]:
    """Generate 1536-dim embedding using OpenAI."""

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

async def batch_generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings in batch for efficiency."""

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    return [data.embedding for data in response.data]

@lru_cache(maxsize=1000)
def get_cached_embedding(text: str) -> list[float]:
    """Cache embeddings for repeated queries."""
    # Note: This is synchronous, use for non-critical paths
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(generate_embedding(text))
```

### Step 2: Memory Service

```python
# backend/app/services/memory_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_
from datetime import datetime, timedelta
from typing import Optional, List

from app.models.memory import PersonalMemory, ProjectMemory, TaskMemory
from app.services.embedding_service import generate_embedding
from app.core.logging import logger

class MemoryService:
    """Service for managing hierarchical memories."""

    async def create_personal_memory(
        self,
        db: AsyncSession,
        user_id: str,
        content: str,
        category: str,
        metadata: dict = {},
        tags: list[str] = [],
        confidence: float = 1.0
    ) -> PersonalMemory:
        """Create a personal memory."""

        # Generate embedding
        embedding = await generate_embedding(content)

        memory = PersonalMemory(
            user_id=user_id,
            category=category,
            content=content,
            embedding=embedding,
            metadata=metadata,
            tags=tags,
            confidence=confidence
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        logger.info(f"Created personal memory for user {user_id}, category: {category}")
        return memory

    async def create_project_memory(
        self,
        db: AsyncSession,
        user_id: str,
        goal_id: str,
        content: str,
        metadata: dict = {},
        tags: list[str] = []
    ) -> ProjectMemory:
        """Create a project memory."""

        embedding = await generate_embedding(content)

        memory = ProjectMemory(
            user_id=user_id,
            goal_id=goal_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            tags=tags
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        logger.info(f"Created project memory for user {user_id}, goal {goal_id}")
        return memory

    async def create_task_memory(
        self,
        db: AsyncSession,
        user_id: str,
        mission_id: str,
        goal_id: str,
        content: str,
        metadata: dict = {},
        tags: list[str] = [],
        ttl_days: int = 30
    ) -> TaskMemory:
        """Create a task memory with auto-expiration."""

        embedding = await generate_embedding(content)
        expires_at = datetime.now() + timedelta(days=ttl_days)

        memory = TaskMemory(
            user_id=user_id,
            mission_id=mission_id,
            goal_id=goal_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            tags=tags,
            expires_at=expires_at
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        logger.info(f"Created task memory for user {user_id}, mission {mission_id}")
        return memory

    async def retrieve_memories(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        context: dict = {},
        limit: int = 10
    ) -> dict:
        """
        Retrieve relevant memories using hybrid search.

        Returns:
            {
                "personal": [memories...],
                "project": [memories...],
                "task": [memories...]
            }
        """

        # Generate query embedding
        query_embedding = await generate_embedding(query)

        results = {}

        # Personal memories (always retrieved)
        results["personal"] = await self._search_personal(
            db, user_id, query_embedding, limit=min(5, limit)
        )

        # Project memories (if goal context provided)
        if context.get("goal_id"):
            results["project"] = await self._search_project(
                db, user_id, query_embedding, context["goal_id"], limit
            )
        else:
            results["project"] = []

        # Task memories (recent, mission-specific)
        results["task"] = await self._search_task(
            db, user_id, query_embedding, context, limit
        )

        return results

    async def _search_personal(
        self,
        db: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        limit: int
    ) -> List[PersonalMemory]:
        """Search personal memories."""

        stmt = select(PersonalMemory).where(
            PersonalMemory.user_id == user_id
        ).order_by(
            PersonalMemory.embedding.cosine_distance(query_embedding)
        ).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def _search_project(
        self,
        db: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        goal_id: str,
        limit: int
    ) -> List[ProjectMemory]:
        """Search project memories for specific goal."""

        stmt = select(ProjectMemory).where(
            and_(
                ProjectMemory.user_id == user_id,
                ProjectMemory.goal_id == goal_id
            )
        ).order_by(
            ProjectMemory.embedding.cosine_distance(query_embedding)
        ).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def _search_task(
        self,
        db: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        context: dict,
        limit: int
    ) -> List[TaskMemory]:
        """Search task memories (recent, non-expired)."""

        stmt = select(TaskMemory).where(
            and_(
                TaskMemory.user_id == user_id,
                TaskMemory.expires_at > func.now()
            )
        )

        # Filter by mission if provided
        if context.get("mission_id"):
            stmt = stmt.where(TaskMemory.mission_id == context["mission_id"])

        # Filter by goal if provided
        if context.get("goal_id"):
            stmt = stmt.where(TaskMemory.goal_id == context["goal_id"])

        # Filter by time window
        if context.get("days"):
            cutoff = func.now() - func.make_interval(days=context["days"])
            stmt = stmt.where(TaskMemory.created_at >= cutoff)

        stmt = stmt.order_by(
            TaskMemory.embedding.cosine_distance(query_embedding)
        ).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def prune_expired_task_memories(self, db: AsyncSession) -> int:
        """Delete expired task memories."""

        stmt = delete(TaskMemory).where(
            TaskMemory.expires_at < func.now()
        )

        result = await db.execute(stmt)
        await db.commit()

        deleted_count = result.rowcount
        logger.info(f"Pruned {deleted_count} expired task memories")

        return deleted_count
```

---

## Story 2.3: Eliza Agent with LangGraph

### Step 1: Install LangGraph

```bash
cd packages/backend
poetry add langgraph langchain langchain-openai
```

### Step 2: Define Agent State

```python
# backend/app/agents/eliza_state.py

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class ElizaState(TypedDict):
    """State for Eliza AI agent."""

    # Input
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_input: str
    user_id: str
    session_id: str

    # Context
    current_goal_id: str | None
    current_mission_id: str | None
    emotional_state: dict
    retrieved_memories: dict

    # Reasoning
    intent: str
    needs_clarification: bool
    planned_actions: list[str]

    # Response
    response_text: str
    tool_outputs: dict

    # Metadata
    current_node: str
    error: str | None
```

### Step 3: Implement Agent Nodes

```python
# backend/app/agents/eliza_agent.py

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.eliza_state import ElizaState
from app.services.emotion_service import detect_emotion
from app.services.memory_service import MemoryService
from app.core.config import settings

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY,
    streaming=True
)

memory_service = MemoryService()

async def receive_input_node(state: ElizaState) -> ElizaState:
    """Parse input and detect emotion."""

    # Detect emotion
    emotions = await detect_emotion(state["user_input"])
    state["emotional_state"] = emotions

    # Extract intent (simplified, can use LLM)
    state["intent"] = "general"  # TODO: LLM-based intent classification

    state["current_node"] = "recall_context"
    return state

async def recall_context_node(state: ElizaState) -> ElizaState:
    """Retrieve relevant memories."""

    from app.db.session import get_db

    async with get_db() as db:
        memories = await memory_service.retrieve_memories(
            db=db,
            user_id=state["user_id"],
            query=state["user_input"],
            context={
                "goal_id": state.get("current_goal_id"),
                "mission_id": state.get("current_mission_id")
            }
        )

        state["retrieved_memories"] = {
            "personal": [m.content for m in memories["personal"]],
            "project": [m.content for m in memories["project"]],
            "task": [m.content for m in memories["task"]]
        }

    state["current_node"] = "reason"
    return state

async def reason_node(state: ElizaState) -> ElizaState:
    """Reason about response using LLM."""

    # Build context prompt
    context_text = f"""
    User's message: "{state['user_input']}"
    Emotional state: {state['emotional_state']}

    Relevant memories:
    - Personal: {state['retrieved_memories']['personal'][:2]}
    - Project: {state['retrieved_memories']['project'][:3]}
    """

    messages = [
        HumanMessage(content=context_text)
    ]

    # Get reasoning from LLM
    response = await llm.ainvoke(messages)
    state["response_text"] = response.content

    state["current_node"] = "respond"
    return state

async def respond_node(state: ElizaState) -> ElizaState:
    """Generate final response."""

    # Response already in state from reason_node
    state["current_node"] = "store_memory"
    return state

async def store_memory_node(state: ElizaState) -> ElizaState:
    """Extract learnings and store memories."""

    from app.db.session import get_db

    # Extract key learnings (simplified)
    if "goal" in state["user_input"].lower():
        async with get_db() as db:
            await memory_service.create_personal_memory(
                db=db,
                user_id=state["user_id"],
                content=f"User discussed: {state['user_input'][:100]}",
                category="conversation",
                tags=["chat", state["emotional_state"].get("dominant", "neutral")]
            )

    state["current_node"] = "end"
    return state

# Build graph
def create_eliza_graph():
    """Create LangGraph workflow for Eliza."""

    workflow = StateGraph(ElizaState)

    # Add nodes
    workflow.add_node("receive_input", receive_input_node)
    workflow.add_node("recall_context", recall_context_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("respond", respond_node)
    workflow.add_node("store_memory", store_memory_node)

    # Define edges
    workflow.set_entry_point("receive_input")
    workflow.add_edge("receive_input", "recall_context")
    workflow.add_edge("recall_context", "reason")
    workflow.add_edge("reason", "respond")
    workflow.add_edge("respond", "store_memory")
    workflow.add_edge("store_memory", END)

    return workflow.compile()

# Create compiled graph
eliza_graph = create_eliza_graph()
```

---

## Story 2.4: Chat API

### Step 1: Chat Endpoint

```python
# backend/app/api/v1/companion.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.agents.eliza_agent import eliza_graph
from app.agents.eliza_state import ElizaState
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: dict = {}

@router.post("/chat")
async def chat_with_eliza(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with Eliza AI companion.

    Returns streaming response via SSE.
    """

    user_id = current_user["user_id"]

    # Initialize state
    initial_state = ElizaState(
        messages=[],
        user_input=request.message,
        user_id=user_id,
        session_id=current_user.get("session_id", "default"),
        current_goal_id=request.context.get("goal_id"),
        current_mission_id=request.context.get("mission_id"),
        emotional_state={},
        retrieved_memories={},
        intent="",
        needs_clarification=False,
        planned_actions=[],
        response_text="",
        tool_outputs={},
        current_node="receive_input",
        error=None
    )

    # Stream response
    async def generate_stream():
        """Generate SSE stream of agent execution."""

        async for state in eliza_graph.astream(initial_state):
            # Send state updates
            yield f"data: {json.dumps({'type': 'state_update', 'node': state['current_node']})}\n\n"

            # Send response when available
            if state.get("response_text"):
                # Stream response tokens
                for i, char in enumerate(state["response_text"]):
                    yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"

        # Send completion
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

---

## Story 2.5: Frontend Integration

### Step 1: Chat Component

```tsx
// frontend/src/components/companion/ElizaChat.tsx

'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

export function ElizaChat() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    // Stream AI response
    let aiResponse = '';

    try {
      const response = await fetch('/api/v1/companion/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, context: {} })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.type === 'token') {
              aiResponse += data.content;
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];

                if (lastMessage?.role === 'assistant') {
                  lastMessage.content = aiResponse;
                } else {
                  newMessages.push({ role: 'assistant', content: aiResponse });
                }

                return newMessages;
              });
            }

            if (data.type === 'complete') {
              setIsStreaming(false);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-100 ml-auto max-w-[80%]'
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Talk to Eliza..."
          className="flex-1"
          disabled={isStreaming}
        />
        <Button onClick={sendMessage} disabled={isStreaming}>
          Send
        </Button>
      </div>
    </div>
  );
}
```

---

## Testing and Validation

### Unit Tests

```python
# backend/tests/test_memory_service.py

import pytest
from app.services.memory_service import MemoryService

@pytest.mark.asyncio
async def test_create_personal_memory(db_session, test_user):
    """Test creating personal memory."""

    service = MemoryService()

    memory = await service.create_personal_memory(
        db=db_session,
        user_id=test_user.id,
        content="User prefers morning missions",
        category="preference",
        tags=["time_preference", "mission"]
    )

    assert memory.id is not None
    assert memory.user_id == test_user.id
    assert memory.content == "User prefers morning missions"

@pytest.mark.asyncio
async def test_retrieve_memories(db_session, test_user, test_memories):
    """Test memory retrieval."""

    service = MemoryService()

    results = await service.retrieve_memories(
        db=db_session,
        user_id=test_user.id,
        query="morning mission preferences",
        context={}
    )

    assert "personal" in results
    assert len(results["personal"]) > 0
```

### Integration Tests

```python
# backend/tests/test_eliza_agent.py

import pytest
from app.agents.eliza_agent import eliza_graph
from app.agents.eliza_state import ElizaState

@pytest.mark.asyncio
async def test_eliza_conversation_flow(test_user):
    """Test complete Eliza conversation flow."""

    initial_state = ElizaState(
        messages=[],
        user_input="How should I start training for a marathon?",
        user_id=test_user.id,
        session_id="test_session",
        current_goal_id=None,
        current_mission_id=None,
        emotional_state={},
        retrieved_memories={},
        intent="",
        needs_clarification=False,
        planned_actions=[],
        response_text="",
        tool_outputs={},
        current_node="receive_input",
        error=None
    )

    # Run agent
    final_state = await eliza_graph.ainvoke(initial_state)

    # Verify flow
    assert final_state["current_node"] == "end"
    assert len(final_state["response_text"]) > 0
    assert "emotional_state" in final_state
```

---

## Deployment Checklist

### Pre-Deployment

✅ All migrations applied to production database
✅ Environment variables configured (OPENAI_API_KEY, DATABASE_URL)
✅ pgvector extension enabled in production Supabase
✅ Memory service tested with real user data
✅ LangGraph agent flows validated
✅ SSE streaming tested across browsers
✅ Frontend components responsive and accessible

### Post-Deployment

✅ Monitor memory creation/retrieval latency
✅ Track LLM costs (should be ~$0.03/user/day)
✅ Set up alerts for errors in agent nodes
✅ Verify task memory pruning runs nightly
✅ Check vector index performance
✅ Monitor user engagement with Eliza

### Performance Targets

| Metric | Target | Monitoring |
|--------|--------|------------|
| Memory retrieval | < 100ms | CloudWatch, Sentry |
| Agent response start | < 2s | API logs |
| Memory creation | < 200ms | Database metrics |
| Embedding generation | < 500ms | OpenAI logs |
| Chat uptime | > 99.5% | Status page |

---

## Summary

This implementation guide provides:

✅ **Complete code** for all Epic 2 stories
✅ **Database migrations** with pgvector setup
✅ **Memory service** with 3-tier architecture
✅ **LangGraph agent** with state management
✅ **FastAPI endpoints** with SSE streaming
✅ **React components** for chat UI
✅ **Testing examples** for validation
✅ **Deployment checklist** for production

**Next Steps**:
1. Follow stories 2.1-2.5 in sequence
2. Test each component before moving to next
3. Monitor performance and costs in production
4. Iterate based on user feedback and metrics

**Success Criteria**:
- Eliza remembers conversations across sessions
- Memory retrieval returns relevant results in < 100ms
- Users report feeling understood by AI
- Cost stays under $0.03/user/day for memory operations

---

**Last Updated**: 2025-11-18
**Status**: Implementation Guide
**Maintainer**: Jack & Delight Team
