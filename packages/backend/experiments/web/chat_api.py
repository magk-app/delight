"""
Chat API endpoint for experimental agent
Connects the Next.js frontend to the chatbot functionality
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

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

        async def process_message(
            self,
            message: str,
            user_id: UUID,
            conversation_history: List[dict]
        ) -> ChatResponse:
            """Process a chat message and return response with memories"""

            async with AsyncSessionLocal() as db:
                try:
                    # Step 1: Retrieve relevant memories
                    relevant_memories = await self.memory_service.search_memories(
                        user_id=user_id,
                        query=message,
                        db=db,
                        auto_route=True,
                        limit=5,
                        memory_types=[MemoryType.PERSONAL, MemoryType.PROJECT]
                    )

                    # Step 2: Build context and generate response
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

                    # Generate response
                    response = await self.openai.chat.completions.create(
                        model=self.config.chat_model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=500
                    )

                    assistant_message = response.choices[0].message.content

                    # Step 3: Extract facts and create memories
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

                    # Format response
                    return ChatResponse(
                        response=assistant_message,
                        memories_retrieved=[
                            MemoryInfo(
                                id=str(m.id) if hasattr(m, 'id') else str(uuid4()),
                                content=m.content,
                                memory_type=m.memory_type if hasattr(m, 'memory_type') else "unknown",
                                score=m.score if hasattr(m, 'score') else None,
                                categories=m.metadata.get("categories", []) if hasattr(m, 'metadata') else []
                            )
                            for m in relevant_memories
                        ],
                        memories_created=[
                            MemoryInfo(
                                id=str(m.id),
                                content=m.content,
                                memory_type=str(m.memory_type.value) if hasattr(m.memory_type, 'value') else str(m.memory_type),
                                categories=m.extra_data.get("categories", []) if m.extra_data else []
                            )
                            for m in created_memories
                        ],
                        timestamp=datetime.now().isoformat()
                    )

                except Exception as e:
                    await db.rollback()
                    raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    chat_service = ChatService()
    print("✅ Real ChatService loaded with OpenAI + PostgreSQL")

except ImportError as e:
    print(f"⚠️  Using MockChatService (missing dependencies: {e})")
    chat_service = MockChatService()

# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message and get AI response with memory context"""

    # Use provided user_id or create a test one
    user_id = UUID(request.user_id) if request.user_id else uuid4()

    # Convert Pydantic models to dicts for OpenAI
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.conversation_history
    ]

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

