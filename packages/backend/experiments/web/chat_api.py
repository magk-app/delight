"""
Chat API endpoint for experimental agent
Connects the Next.js frontend to the chatbot functionality
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/chat", tags=["chat"])

# ============================================================================
# Request/Response Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = []

class MemoryInfo(BaseModel):
    id: str
    content: str
    memory_type: str
    score: Optional[float] = None
    categories: Optional[List[str]] = []

class ChatResponse(BaseModel):
    response: str
    memories_retrieved: List[MemoryInfo]
    memories_created: List[MemoryInfo]
    timestamp: str

# ============================================================================
# Mock Chat Service (for when dependencies aren't available)
# ============================================================================

class MockChatService:
    """Mock chat service for testing without full backend"""

    async def process_message(
        self,
        message: str,
        user_id: UUID,
        conversation_history: List[dict]
    ) -> ChatResponse:
        """Process a chat message and return mock response"""

        return ChatResponse(
            response=f"Echo: {message}\n\n(This is a mock response. To enable full AI chat with memory, ensure the database and OpenAI API are configured.)",
            memories_retrieved=[],
            memories_created=[],
            timestamp=datetime.now().isoformat()
        )

# Try to import real dependencies, fall back to mock
try:
    import sys
    from pathlib import Path

    # Add parent to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from app.db.session import AsyncSessionLocal
    from app.models.memory import MemoryType
    from experiments.memory.memory_service import MemoryService
    from experiments.config import get_config
    from openai import AsyncOpenAI

    # ============================================================================
    # Real Chat Service
    # ============================================================================

    class ChatService:
        """Service for handling chat with memory"""

        def __init__(self):
            self.config = get_config()
            self.memory_service = MemoryService()
            self.openai = AsyncOpenAI(api_key=self.config.openai_api_key)

        async def _ensure_user_exists(self, user_id: UUID, db) -> UUID:
            """Ensure user exists in database, create if needed"""
            from sqlalchemy import select
            from app.models.user import User

            # Check if user exists
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                return user_id

            # Create test user for experimental chat
            test_clerk_id = f"experimental_chat_{user_id}"
            new_user = User(
                id=user_id,
                clerk_user_id=test_clerk_id,
                email=f"experimental-{user_id.hex[:8]}@delight.local",
                display_name="Experimental Chat User"
            )

            db.add(new_user)
            await db.flush()  # Flush to make user available for foreign key
            return user_id

        async def process_message_fast(
            self,
            message: str,
            user_id: UUID,
            conversation_history: List[dict]
        ) -> tuple[ChatResponse, list]:
            """
            Process message with fast response (returns before memory processing).

            Returns:
                tuple: (ChatResponse, relevant_memories) for background processing
            """

            async with AsyncSessionLocal() as db:
                # Step 0: Ensure user exists
                await self._ensure_user_exists(user_id, db)

                # Step 1: Preprocess query to handle multiple questions
                from experiments.memory.query_preprocessor import QueryPreprocessor

                preprocessor = QueryPreprocessor()
                sub_queries = await preprocessor.extract_search_queries(message)

                # Step 2: Retrieve relevant memories for each sub-query
                print(f"\n🔍 Searching for memories (split into {len(sub_queries)} sub-queries)")
                print(f"   User ID: {user_id}")

                all_relevant_memories = []
                seen_ids = set()

                for sub_query in sub_queries:
                    print(f"\n   Sub-query: '{sub_query}'")

                    sub_results = await self.memory_service.search_memories(
                        user_id=user_id,
                        query=sub_query,
                        db=db,
                        auto_route=True,
                        limit=10,  # 10 per sub-query
                        memory_types=[MemoryType.PERSONAL, MemoryType.PROJECT]
                    )

                    # Deduplicate across sub-queries
                    for mem in sub_results:
                        mem_id = mem.memory_id if hasattr(mem, 'memory_id') else mem.id
                        if mem_id not in seen_ids:
                            all_relevant_memories.append(mem)
                            seen_ids.add(mem_id)

                    print(f"      Found {len(sub_results)} memories (total unique: {len(all_relevant_memories)})")

                # Sort by score and limit to top 15
                all_relevant_memories.sort(key=lambda m: m.score if hasattr(m, 'score') else 0, reverse=True)
                relevant_memories = all_relevant_memories[:15]

                print(f"   📊 Search returned {len(relevant_memories)} memories")
                if relevant_memories:
                    for i, mem in enumerate(relevant_memories[:3], 1):
                        print(f"   {i}. [{mem.score:.3f}] {mem.content[:80]}...")
                else:
                    print(f"   ⚠️ No memories found! This might indicate:")
                    print(f"      - No memories stored for this user")
                    print(f"      - Memories don't have embeddings")
                    print(f"      - Search threshold too high")

                # Step 2: Build context and generate AI response (FAST - no memory creation)
                memory_context = ""
                if relevant_memories:
                    memory_context = "\n\nRelevant memories about the user:\n"
                    for result in relevant_memories:
                        memory_context += f"- {result.content} (relevance: {result.score:.2f})\n"

                system_prompt = f"""You are a helpful AI assistant with access to the user's personal memories.

Use the provided memories to give personalized, contextual responses.
Be conversational and natural.
Reference specific memories when relevant.
If no memories are provided, respond naturally without making assumptions.
{memory_context}"""

                # Create messages for OpenAI
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(conversation_history[-10:])  # Last 10 messages
                messages.append({"role": "user", "content": message})

                # Generate response (BLOCKING - but fast, ~800ms)
                response = await self.openai.chat.completions.create(
                    model=self.config.chat_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )

                assistant_message = response.choices[0].message.content

                # Track token usage
                try:
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).parent.parent))
                    from services.token_tracker import TokenTracker

                    tokens_input = response.usage.prompt_tokens
                    tokens_output = response.usage.completion_tokens

                    await TokenTracker.track_usage(
                        db=db,
                        user_id=user_id,
                        operation_type="chat",
                        model=self.config.chat_model,
                        tokens_input=tokens_input,
                        tokens_output=tokens_output,
                        metadata={"message_preview": message[:100]}
                    )
                    await db.commit()  # Commit token usage immediately
                except Exception as e:
                    print(f"[Warning] Failed to track token usage: {e}")
                    # Don't fail the request if token tracking fails

                # Return response immediately (don't wait for memory creation)
                print(f"📤 Returning {len(relevant_memories)} retrieved memories")

                return (
                    ChatResponse(
                        response=assistant_message,
                        memories_retrieved=[
                            MemoryInfo(
                                id=str(m.memory_id) if hasattr(m, 'memory_id') else str(uuid4()),
                                content=m.content,
                                memory_type=m.memory_type if hasattr(m, 'memory_type') else "unknown",
                                score=m.score if hasattr(m, 'score') else None,
                                categories=m.metadata.get("categories", []) if (hasattr(m, 'metadata') and m.metadata) else []
                            )
                            for m in relevant_memories
                        ],
                        memories_created=[],  # Empty - will be processed in background
                        timestamp=datetime.now().isoformat()
                    ),
                    relevant_memories  # Pass to background task
                )

        async def process_memories_background(
            self,
            user_id: UUID,
            message: str
        ):
            """Background task to process and create memories (SLOW - 1-2 seconds)"""

            async with AsyncSessionLocal() as db:
                try:
                    print(f"[Background] Processing memories for user {user_id}...")

                    # Extract facts and create memories (SLOW - but user doesn't wait!)
                    created_memories = await self.memory_service.create_memory_from_message(
                        user_id=user_id,
                        message=message,
                        memory_type=MemoryType.PERSONAL,
                        db=db,
                        extract_facts=True,
                        auto_categorize=True,
                        generate_embeddings=True,
                        link_facts=True
                    )

                    await db.commit()

                    print(f"[Background] ✅ Created {len(created_memories)} memories for user {user_id}")
                    for mem in created_memories:
                        print(f"  - {mem.content[:80]}...")

                except Exception as e:
                    print(f"[Background] ❌ Error processing memories: {e}")
                    import traceback
                    traceback.print_exc()
                    await db.rollback()

    chat_service = ChatService()
    print("✅ Real ChatService loaded with OpenAI + PostgreSQL")

except ImportError as e:
    print(f"⚠️  Using MockChatService (missing dependencies: {e})")
    chat_service = MockChatService()

# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Send a message and get FAST AI response.

    Memory processing happens in background (async).
    User gets response in ~1 second instead of ~3 seconds!
    """

    # Use provided user_id or create a test one
    user_id = UUID(request.user_id) if request.user_id else uuid4()

    # Convert Pydantic models to dicts for OpenAI
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.conversation_history
    ]

    # Get fast response (doesn't wait for memory creation)
    if hasattr(chat_service, 'process_message_fast'):
        # Use fast async method
        response, _ = await chat_service.process_message_fast(
            message=request.message,
            user_id=user_id,
            conversation_history=conversation_history
        )

        # Process memories in background
        background_tasks.add_task(
            chat_service.process_memories_background,
            user_id=user_id,
            message=request.message
        )

        return response
    else:
        # Fallback to mock service (no background processing)
        return await chat_service.process_message(
            message=request.message,
            user_id=user_id,
            conversation_history=conversation_history
        )

@router.get("/health")
async def chat_health():
    """Check if chat service is healthy"""
    return {
        "status": "healthy",
        "service": "chat",
        "mode": "real" if isinstance(chat_service, ChatService) else "mock",
        "timestamp": datetime.now().isoformat()
    }

