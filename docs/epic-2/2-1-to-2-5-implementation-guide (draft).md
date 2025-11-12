# Implementation Guide: Stories 2.1-2.5 (Epic 2: Companion & Memory System)

**Date:** 2025-11-10  
**Status:** Implementation Guide  
**Stories Covered:** 2.1, 2.2, 2.3, 2.4, 2.5

---

## Overview

This guide provides step-by-step implementation suggestions for building the Companion & Memory System (Epic 2), covering:

- **Story 2.1:** PostgreSQL pgvector and Memory Schema
- **Story 2.2:** Memory Service with 3-Tier Architecture
- **Story 2.3:** Eliza Agent with LangGraph
- **Story 2.4:** Companion Chat API with SSE Streaming
- **Story 2.5:** Companion Chat UI (Frontend)

---

## Prerequisites Checklist

Before starting, ensure:

- ✅ Story 1.2 is complete (database schema, pgvector extension enabled)
- ✅ Supabase PostgreSQL is connected and accessible
- ✅ Backend dependencies installed (LangChain, LangGraph, pgvector)
- ⚠️ **Missing:** OpenAI SDK needs to be added to `pyproject.toml`
- ✅ Frontend structure exists (`packages/frontend/src/app/companion/`)

---

## Story 2.1: Set Up PostgreSQL pgvector and Memory Schema

### Goal

Create database tables for the 3-tier memory system with vector embeddings.

### Implementation Steps

#### 1. Add OpenAI Dependency

First, add OpenAI SDK to backend dependencies:

```bash
cd packages/backend
poetry add openai
```

#### 2. Create Alembic Migration

Create a new migration file: `packages/backend/app/db/migrations/versions/002_create_memory_tables.py`

**Key Components:**

```python
"""create memory tables with pgvector

Revision ID: 002
Revises: 001
Create Date: 2025-11-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

def upgrade() -> None:
    # Create memory_type enum
    op.execute("""
        CREATE TYPE memory_type AS ENUM ('personal', 'project', 'task');
    """)

    # Create memories table
    op.create_table(
        'memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('memory_type', sa.Enum('personal', 'project', 'task', name='memory_type'),
                  nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),  # pgvector column
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('accessed_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('ix_memories_user_id', 'memories', ['user_id'])
    op.create_index('ix_memories_memory_type', 'memories', ['memory_type'])
    op.create_index('ix_memories_created_at', 'memories', ['created_at'])

    # Create HNSW index for vector similarity search
    op.execute("""
        CREATE INDEX ix_memories_embedding ON memories
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    # Create memory_collections table (optional, for organizing memories)
    op.create_table(
        'memory_collections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collection_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_index('ix_memory_collections_user_id', 'memory_collections', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_memory_collections_user_id', table_name='memory_collections')
    op.drop_table('memory_collections')
    op.execute('DROP INDEX IF EXISTS ix_memories_embedding')
    op.drop_index('ix_memories_created_at', table_name='memories')
    op.drop_index('ix_memories_memory_type', table_name='memories')
    op.drop_index('ix_memories_user_id', table_name='memories')
    op.drop_table('memories')
    op.execute('DROP TYPE IF EXISTS memory_type')
```

#### 3. Create SQLAlchemy Models

Create `packages/backend/app/models/memory.py`:

```python
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Text, ForeignKey, Enum as SQLEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.models.base import Base

class MemoryType(str, Enum):
    PERSONAL = "personal"
    PROJECT = "project"
    TASK = "task"

class Memory(Base):
    __tablename__ = "memories"

    id: UUID = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: UUID = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_type: MemoryType = Column(SQLEnum(MemoryType), nullable=False)
    content: str = Column(Text, nullable=False)
    embedding: Optional[list[float]] = Column(Vector(1536), nullable=True)  # 1536-dim OpenAI embeddings
    metadata: Optional[Dict[str, Any]] = Column(JSONB, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    accessed_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="memories")

class MemoryCollection(Base):
    __tablename__ = "memory_collections"

    id: UUID = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: UUID = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    collection_type: str = Column(Text, nullable=False)
    name: str = Column(Text, nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="memory_collections")
```

Update `packages/backend/app/models/user.py` to add relationships:

```python
# Add to User model
memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
memory_collections = relationship("MemoryCollection", back_populates="user", cascade="all, delete-orphan")
```

#### 4. Verify Migration

```bash
cd packages/backend
poetry run alembic upgrade head
```

Test the migration:

```bash
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

---

## Story 2.2: Implement Memory Service with 3-Tier Architecture

### Goal

Build a service that manages personal, project, and task memories with automatic embedding generation and hybrid search.

### Implementation Steps

#### 1. Create Memory Service

Create `packages/backend/app/services/memory_service.py`:

```python
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from pgvector.sqlalchemy import Vector
from openai import AsyncOpenAI

from app.models.memory import Memory, MemoryType
from app.core.config import settings

class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions

    async def add_memory(
        self,
        user_id: UUID,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """Add a memory with automatic embedding generation."""
        # Generate embedding
        embedding = await self._generate_embedding(content)

        # Create memory record
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )

        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)

        return memory

    async def query_memories(
        self,
        user_id: UUID,
        query_text: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Memory]:
        """Query memories using hybrid search (semantic + time-weighted)."""
        # Generate query embedding
        query_embedding = await self._generate_embedding(query_text)

        # Build base query
        query = select(Memory).where(Memory.user_id == user_id)

        # Filter by memory types if specified
        if memory_types:
            query = query.where(Memory.memory_type.in_(memory_types))

        # Vector similarity search using cosine distance
        # pgvector uses 1 - cosine_similarity, so lower is more similar
        query = query.order_by(
            Memory.embedding.cosine_distance(query_embedding)
        ).limit(limit * 2)  # Get more results for time-weighting

        result = await self.db.execute(query)
        memories = result.scalars().all()

        # Apply time-weighted scoring
        scored_memories = self._apply_time_decay(memories, query_embedding)

        # Filter by threshold and return top results
        filtered = [
            m for m in scored_memories
            if m['score'] >= similarity_threshold
        ][:limit]

        # Update accessed_at for retrieved memories
        memory_ids = [m['memory'].id for m in filtered]
        await self.db.execute(
            select(Memory).where(Memory.id.in_(memory_ids))
        )
        for memory in filtered:
            memory['memory'].accessed_at = datetime.utcnow()
        await self.db.commit()

        return [m['memory'] for m in filtered]

    async def get_personal_memories(
        self,
        user_id: UUID,
        limit: int = 5
    ) -> List[Memory]:
        """Get top personal memories (always queried for context)."""
        return await self.query_memories(
            user_id=user_id,
            query_text="user preferences identity personality",
            memory_types=[MemoryType.PERSONAL],
            limit=limit
        )

    async def prune_old_task_memories(self, days_old: int = 30) -> int:
        """Prune task memories older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        result = await self.db.execute(
            select(Memory).where(
                and_(
                    Memory.memory_type == MemoryType.TASK,
                    Memory.created_at < cutoff_date
                )
            )
        )
        old_memories = result.scalars().all()

        count = len(old_memories)
        for memory in old_memories:
            await self.db.delete(memory)

        await self.db.commit()
        return count

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        response = await self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

    def _apply_time_decay(
        self,
        memories: List[Memory],
        query_embedding: List[float]
    ) -> List[Dict[str, Any]]:
        """Apply time-weighted recency boost to similarity scores."""
        scored = []

        for memory in memories:
            # Calculate cosine similarity (1 - distance)
            # Note: pgvector cosine_distance returns 0-2, where 0 is identical
            # We need to convert this to similarity score
            # For now, we'll use a simple approach: assume memories are already sorted by similarity

            # Time decay: boost recent memories
            days_since_access = (datetime.utcnow() - memory.accessed_at).days
            time_boost = 1 + math.log(1 + days_since_access + 1) ** -1

            # Access frequency boost (if tracked in metadata)
            access_count = memory.metadata.get('access_count', 1)
            frequency_boost = 1 + (math.log(access_count) * 0.1)

            # Combined score (simplified - in production, use actual cosine similarity)
            score = time_boost * frequency_boost

            scored.append({
                'memory': memory,
                'score': score
            })

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored
```

#### 2. Add OpenAI API Key to Config

Update `packages/backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
```

Update `packages/backend/env.example`:

```bash
OPENAI_API_KEY=sk-...
```

#### 3. Create Background Worker for Pruning

Create `packages/backend/app/workers/memory_pruner.py`:

```python
from arq import cron
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.services.memory_service import MemoryService
from app.core.config import settings

async def prune_task_memories(ctx):
    """ARQ worker to prune old task memories daily."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        service = MemoryService(db)
        count = await service.prune_old_task_memories(days_old=30)
        print(f"Pruned {count} old task memories")

    await engine.dispose()

class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [prune_task_memories]
    cron_jobs = [
        cron(prune_task_memories, hour=2, minute=0)  # Run daily at 2 AM
    ]
```

#### 4. Add Tests

Create `packages/backend/tests/unit/test_memory_service.py`:

```python
import pytest
from uuid import uuid4
from app.services.memory_service import MemoryService
from app.models.memory import MemoryType

@pytest.mark.asyncio
async def test_add_memory(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()

    memory = await service.add_memory(
        user_id=user_id,
        memory_type=MemoryType.PERSONAL,
        content="I prefer working in the morning",
        metadata={"source": "conversation"}
    )

    assert memory.user_id == user_id
    assert memory.memory_type == MemoryType.PERSONAL
    assert memory.embedding is not None
    assert len(memory.embedding) == 1536

@pytest.mark.asyncio
async def test_query_memories(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()

    # Add test memories
    await service.add_memory(user_id, MemoryType.PERSONAL, "I love coding")
    await service.add_memory(user_id, MemoryType.PERSONAL, "I work best in the morning")

    # Query
    results = await service.query_memories(
        user_id=user_id,
        query_text="work schedule preferences",
        memory_types=[MemoryType.PERSONAL],
        limit=5
    )

    assert len(results) > 0
    assert all(m.memory_type == MemoryType.PERSONAL for m in results)
```

---

## Story 2.3: Build Eliza Agent with LangGraph

### Goal

Create a stateful LangGraph agent for Eliza that maintains conversation context and queries memory strategically.

### Implementation Steps

#### 1. Create Eliza Agent State

Create `packages/backend/app/agents/eliza_state.py`:

```python
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage

class ElizaState(TypedDict):
    """State for Eliza agent conversation."""
    messages: List[BaseMessage]  # Conversation history
    user_id: str
    user_context: Dict[str, Any]  # User preferences, current mission, etc.
    retrieved_memories: List[Dict[str, Any]]  # Memories from query
    emotional_state: Optional[Dict[str, Any]]  # Detected emotion (from Story 2.6)
    current_goal: Optional[str]  # What user is trying to accomplish
```

#### 2. Create Eliza Agent

Create `packages/backend/app/agents/eliza_agent.py`:

```python
from typing import Annotated
from uuid import UUID
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agents.eliza_state import ElizaState
from app.services.memory_service import MemoryService, MemoryType
from app.core.config import settings

# System prompt for Eliza
ELIZA_SYSTEM_PROMPT = """You are Eliza, an empathetic AI companion who helps users achieve their goals through supportive conversation and gentle guidance.

Your personality:
- Warm, understanding, and non-judgmental
- Encouraging but realistic
- Asks clarifying questions when needed
- Celebrates wins and offers support during challenges
- Helps break down overwhelming goals into manageable steps

Your approach:
- Always acknowledge the user's feelings
- Use the user's memories and context to personalize responses
- When the user seems overwhelmed, offer grounding techniques
- When the user is stuck, help them identify next steps
- When the user succeeds, celebrate authentically

Remember: You're here to support, not to push. Be patient and understanding."""

class ElizaAgent:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(ElizaState)

        # Add nodes
        graph.add_node("recall_context", self._recall_context)
        graph.add_node("reason", self._reason)
        graph.add_node("respond", self._respond)
        graph.add_node("store_memory", self._store_memory)

        # Define edges
        graph.set_entry_point("recall_context")
        graph.add_edge("recall_context", "reason")
        graph.add_edge("reason", "respond")
        graph.add_edge("respond", "store_memory")
        graph.add_edge("store_memory", END)

        return graph.compile()

    async def _recall_context(self, state: ElizaState) -> ElizaState:
        """Query relevant memories based on conversation."""
        user_id = UUID(state["user_id"])
        last_message = state["messages"][-1].content if state["messages"] else ""

        # Always query personal memories
        personal_memories = await self.memory_service.get_personal_memories(
            user_id=user_id,
            limit=5
        )

        # Query project memories if discussing goals
        project_memories = []
        if any(keyword in last_message.lower() for keyword in ["goal", "project", "plan", "objective"]):
            project_memories = await self.memory_service.query_memories(
                user_id=user_id,
                query_text=last_message,
                memory_types=[MemoryType.PROJECT],
                limit=3
            )

        # Query task memories for recent context
        task_memories = await self.memory_service.query_memories(
            user_id=user_id,
            query_text=last_message,
            memory_types=[MemoryType.TASK],
            limit=3
        )

        state["retrieved_memories"] = [
            {
                "type": "personal",
                "content": m.content,
                "metadata": m.metadata
            }
            for m in personal_memories
        ] + [
            {
                "type": "project",
                "content": m.content,
                "metadata": m.metadata
            }
            for m in project_memories
        ] + [
            {
                "type": "task",
                "content": m.content,
                "metadata": m.metadata
            }
            for m in task_memories
        ]

        return state

    async def _reason(self, state: ElizaState) -> ElizaState:
        """LLM processes input with context."""
        # Build context from memories
        memory_context = "\n".join([
            f"[{m['type'].upper()}] {m['content']}"
            for m in state["retrieved_memories"]
        ])

        # Build messages
        messages = [
            SystemMessage(content=ELIZA_SYSTEM_PROMPT),
            SystemMessage(content=f"User Context: {state.get('user_context', {})}"),
            SystemMessage(content=f"Relevant Memories:\n{memory_context}"),
        ] + state["messages"][-10:]  # Last 10 messages for context

        # Get LLM response
        response = await self.llm.ainvoke(messages)

        # Add response to state
        state["messages"] = state["messages"] + [response]

        return state

    async def _respond(self, state: ElizaState) -> ElizaState:
        """Format response (already done in reason, but can add post-processing)."""
        # Response is already in messages, just return
        return state

    async def _store_memory(self, state: ElizaState) -> ElizaState:
        """Store conversation to memory if significant."""
        user_id = UUID(state["user_id"])
        last_human_message = None
        last_ai_message = None

        # Find last human and AI messages
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage) and last_human_message is None:
                last_human_message = msg
            if isinstance(msg, AIMessage) and last_ai_message is None:
                last_ai_message = msg
            if last_human_message and last_ai_message:
                break

        # Store as task memory (conversation context)
        if last_human_message:
            await self.memory_service.add_memory(
                user_id=user_id,
                memory_type=MemoryType.TASK,
                content=f"User: {last_human_message.content}\nEliza: {last_ai_message.content if last_ai_message else '...'}",
                metadata={
                    "conversation": True,
                    "timestamp": state.get("user_context", {}).get("timestamp")
                }
            )

        return state

    async def chat(
        self,
        user_id: UUID,
        message: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Main entry point for chat."""
        # Initialize state
        initial_state: ElizaState = {
            "messages": [HumanMessage(content=message)],
            "user_id": str(user_id),
            "user_context": user_context or {},
            "retrieved_memories": [],
            "emotional_state": None,
            "current_goal": None
        }

        # Run graph
        final_state = await self.graph.ainvoke(initial_state)

        # Extract response
        last_message = final_state["messages"][-1]
        return last_message.content
```

#### 3. Add Tests

Create `packages/backend/tests/unit/test_eliza_agent.py`:

```python
import pytest
from uuid import uuid4
from app.agents.eliza_agent import ElizaAgent
from app.services.memory_service import MemoryService

@pytest.mark.asyncio
async def test_eliza_chat(db_session):
    memory_service = MemoryService(db_session)
    agent = ElizaAgent(memory_service)

    user_id = uuid4()
    response = await agent.chat(
        user_id=user_id,
        message="I'm feeling overwhelmed with my goals",
        user_context={"current_mission": None}
    )

    assert response is not None
    assert len(response) > 0
    # Response should be empathetic
    assert any(word in response.lower() for word in ["understand", "support", "help", "feel"])
```

---

## Story 2.4: Create Companion Chat API with SSE Streaming

### Goal

Build FastAPI endpoints that stream Eliza's responses using Server-Sent Events (SSE).

### Implementation Steps

#### 1. Create Conversation Model

Create `packages/backend/app/models/conversation.py`:

```python
from uuid import UUID
from datetime import datetime
from sqlalchemy import Column, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id: UUID = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: UUID = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    messages: list[dict] = Column(JSONB, nullable=False, default=list)
    started_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())

    user = relationship("User", back_populates="conversations")
```

Add migration for conversations table (similar to memories).

#### 2. Create Chat API Endpoint

Create `packages/backend/app/api/v1/companion.py`:

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio

from app.core.dependencies import get_db, get_current_user
from app.agents.eliza_agent import ElizaAgent
from app.services.memory_service import MemoryService
from app.models.conversation import Conversation
from app.models.user import User

router = APIRouter(prefix="/companion", tags=["companion"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    context: dict | None = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str

@router.post("/chat", response_model=ChatResponse)
async def create_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat message and return conversation ID for streaming."""
    # Get or create conversation
    if request.conversation_id:
        conversation = await db.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            user_id=current_user.id,
            messages=[]
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Add user message
    conversation.messages.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    })
    await db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message="Stream started"
    )

@router.get("/stream/{conversation_id}")
async def stream_chat(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream Eliza's response using SSE."""
    # Get conversation
    conversation = await db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get last user message
    user_messages = [m for m in conversation.messages if m["role"] == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    last_message = user_messages[-1]["content"]

    # Initialize services
    memory_service = MemoryService(db)
    agent = ElizaAgent(memory_service)

    async def generate_stream():
        """Generator for SSE stream."""
        try:
            # Get user context
            user_context = {
                "user_id": str(current_user.id),
                "email": current_user.email,
                "timezone": current_user.timezone
            }

            # Stream response from agent
            # Note: LangGraph doesn't natively support streaming, so we'll use LLM streaming
            # For now, we'll simulate streaming by chunking the response
            full_response = await agent.chat(
                user_id=current_user.id,
                message=last_message,
                user_context=user_context
            )

            # Stream response token by token (simplified - in production, use LLM streaming)
            words = full_response.split()
            for i, word in enumerate(words):
                chunk = {
                    "type": "token",
                    "content": word + (" " if i < len(words) - 1 else ""),
                    "conversation_id": str(conversation_id)
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)  # Simulate streaming delay

            # Send completion
            completion = {
                "type": "complete",
                "conversation_id": str(conversation_id)
            }
            yield f"data: {json.dumps(completion)}\n\n"

            # Save AI response to conversation
            conversation.messages.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            await db.commit()

        except Exception as e:
            error = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

#### 3. Register Router

Update `packages/backend/app/main.py`:

```python
from app.api.v1 import companion

app.include_router(companion.router, prefix="/api/v1")
```

---

## Story 2.5: Build Companion Chat UI (Frontend)

### Goal

Create a beautiful, responsive chat interface for Eliza with SSE streaming support.

### Implementation Steps

#### 1. Install Frontend Dependencies

```bash
cd packages/frontend
pnpm add framer-motion
```

#### 2. Create Chat Component

Create `packages/frontend/src/components/companion/CompanionChat.tsx`:

```typescript
"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface CompanionChatProps {
  initialMessages?: Message[];
}

export default function CompanionChat({
  initialMessages = [],
}: CompanionChatProps) {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const token = await getToken();
      const response = await fetch("/api/v1/companion/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
        }),
      });

      const data = await response.json();
      setConversationId(data.conversation_id);

      // Start SSE stream
      const eventSource = new EventSource(
        `/api/v1/companion/stream/${data.conversation_id}?token=${token}`
      );

      let assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "token") {
          setMessages((prev) => {
            const updated = [...prev];
            const lastMessage = updated[updated.length - 1];
            if (lastMessage.role === "assistant") {
              lastMessage.content += data.content;
            }
            return updated;
          });
        } else if (data.type === "complete") {
          eventSource.close();
          setIsLoading(false);
        } else if (data.type === "error") {
          eventSource.close();
          setIsLoading(false);
          console.error("Stream error:", data.message);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsLoading(false);
      };

      eventSourceRef.current = eventSource;
    } catch (error) {
      console.error("Error sending message:", error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  return (
    <div className="flex flex-col h-full max-h-screen">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-900"
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-gray-200 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
```

#### 3. Create Companion Page

Update `packages/frontend/src/app/companion/page.tsx`:

```typescript
import { Metadata } from "next";
import CompanionChat from "@/components/companion/CompanionChat";

export const metadata: Metadata = {
  title: "Companion - Delight",
  description: "Chat with Eliza, your AI companion",
};

export default function CompanionPage() {
  return (
    <div className="container mx-auto h-screen flex flex-col">
      <header className="border-b p-4">
        <h1 className="text-2xl font-bold">Eliza</h1>
        <p className="text-gray-600">Your AI companion</p>
      </header>
      <div className="flex-1 overflow-hidden">
        <CompanionChat />
      </div>
    </div>
  );
}
```

#### 4. Add API Route Proxy (if needed)

If Clerk auth tokens need to be passed through, create `packages/frontend/src/app/api/v1/companion/chat/route.ts`:

```typescript
import { auth } from "@clerk/nextjs";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { getToken } = auth();
  const token = await getToken();

  const body = await request.json();

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/companion/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    }
  );

  const data = await response.json();
  return NextResponse.json(data);
}
```

---

## Testing Checklist

### Story 2.1

- [ ] Migration runs successfully
- [ ] Memory tables created with correct schema
- [ ] HNSW index created for vector search
- [ ] Can insert memory with embedding

### Story 2.2

- [ ] Memory service can add memories
- [ ] Embeddings are generated correctly (1536 dimensions)
- [ ] Query returns relevant memories
- [ ] Time decay function works
- [ ] Pruning job runs successfully

### Story 2.3

- [ ] Eliza agent responds to messages
- [ ] Agent queries personal memories
- [ ] Agent queries project/task memories when relevant
- [ ] Conversations are stored to memory
- [ ] Agent maintains empathetic tone

### Story 2.4

- [ ] Chat endpoint creates conversations
- [ ] SSE stream works correctly
- [ ] Messages are saved to database
- [ ] Error handling works

### Story 2.5

- [ ] Chat UI displays messages
- [ ] Streaming works (tokens appear incrementally)
- [ ] Typing indicator shows during loading
- [ ] Mobile responsive
- [ ] Accessible (keyboard navigation)

---

## Common Issues & Solutions

### Issue: pgvector extension not found

**Solution:** Ensure Supabase has pgvector enabled. Run in Supabase SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: OpenAI API errors

**Solution:** Check `OPENAI_API_KEY` is set in environment variables and has sufficient credits.

### Issue: SSE not streaming

**Solution:**

- Check nginx/proxy buffering settings
- Ensure `X-Accel-Buffering: no` header is set
- Verify EventSource connection in browser DevTools

### Issue: Memory queries too slow

**Solution:**

- Ensure HNSW index is created
- Tune HNSW parameters (m, ef_construction)
- Consider caching frequently accessed memories

---

## Next Steps

After completing stories 2.1-2.5:

1. **Story 2.6:** Implement emotional state detection (uses cardiffnlp/roberta model)
2. **Epic 3:** Begin Goal & Mission Management
3. **Testing:** Add integration tests for full chat flow
4. **Performance:** Optimize memory queries and streaming

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Server-Sent Events (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
