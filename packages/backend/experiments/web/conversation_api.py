"""
Conversation Management API

Endpoints for creating, retrieving, and managing chat conversations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# ============================================================================
# Request/Response Models
# ============================================================================

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str
    metadata: Optional[dict] = None

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    message_count: int
    is_archived: bool
    created_at: str
    updated_at: str
    messages: Optional[List[MessageResponse]] = None

class ConversationCreateRequest(BaseModel):
    user_id: str
    title: Optional[str] = None

class MessageCreateRequest(BaseModel):
    conversation_id: str
    user_id: str
    role: str
    content: str
    metadata: Optional[dict] = None

# Try to import real dependencies
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from app.db.session import AsyncSessionLocal
    from app.models.conversation import Conversation, ChatMessage
    from sqlalchemy import select, desc
    from sqlalchemy.orm import selectinload

    # ============================================================================
    # Real Conversation Service
    # ============================================================================

    class ConversationService:
        """Service for managing conversations and messages"""

        async def create_conversation(
            self,
            user_id: UUID,
            title: Optional[str] = None
        ) -> ConversationResponse:
            """Create a new conversation"""

            async with AsyncSessionLocal() as db:
                conversation = Conversation(
                    user_id=user_id,
                    title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    message_count=0
                )

                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)

                return ConversationResponse(
                    id=str(conversation.id),
                    title=conversation.title,
                    message_count=conversation.message_count,
                    is_archived=conversation.is_archived,
                    created_at=conversation.created_at.isoformat(),
                    updated_at=conversation.updated_at.isoformat()
                )

        async def get_conversations(
            self,
            user_id: UUID,
            include_archived: bool = False,
            limit: int = 50
        ) -> List[ConversationResponse]:
            """Get all conversations for a user"""

            async with AsyncSessionLocal() as db:
                query = select(Conversation).where(Conversation.user_id == user_id)

                if not include_archived:
                    query = query.where(Conversation.is_archived == False)

                query = query.order_by(desc(Conversation.updated_at)).limit(limit)

                result = await db.execute(query)
                conversations = result.scalars().all()

                return [
                    ConversationResponse(
                        id=str(c.id),
                        title=c.title,
                        message_count=c.message_count,
                        is_archived=c.is_archived,
                        created_at=c.created_at.isoformat(),
                        updated_at=c.updated_at.isoformat()
                    )
                    for c in conversations
                ]

        async def get_conversation_with_messages(
            self,
            conversation_id: UUID
        ) -> ConversationResponse:
            """Get a conversation with all its messages"""

            async with AsyncSessionLocal() as db:
                query = select(Conversation).where(Conversation.id == conversation_id).options(
                    selectinload(Conversation.messages)
                )

                result = await db.execute(query)
                conversation = result.scalar_one_or_none()

                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")

                return ConversationResponse(
                    id=str(conversation.id),
                    title=conversation.title,
                    message_count=conversation.message_count,
                    is_archived=conversation.is_archived,
                    created_at=conversation.created_at.isoformat(),
                    updated_at=conversation.updated_at.isoformat(),
                    messages=[
                        MessageResponse(
                            id=str(m.id),
                            role=m.role,
                            content=m.content,
                            created_at=m.created_at.isoformat(),
                            metadata=m.metadata
                        )
                        for m in sorted(conversation.messages, key=lambda m: m.created_at)
                    ]
                )

        async def create_message(
            self,
            conversation_id: UUID,
            user_id: UUID,
            role: str,
            content: str,
            metadata: Optional[dict] = None
        ) -> MessageResponse:
            """Add a message to a conversation"""

            async with AsyncSessionLocal() as db:
                # Create message
                message = ChatMessage(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role=role,
                    content=content,
                    metadata=metadata or {}
                )

                db.add(message)

                # Update conversation message count and updated_at
                conversation_query = select(Conversation).where(Conversation.id == conversation_id)
                result = await db.execute(conversation_query)
                conversation = result.scalar_one_or_none()

                if conversation:
                    conversation.message_count += 1
                    conversation.updated_at = datetime.utcnow()

                await db.commit()
                await db.refresh(message)

                return MessageResponse(
                    id=str(message.id),
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at.isoformat(),
                    metadata=message.metadata
                )

        async def delete_conversation(self, conversation_id: UUID):
            """Delete a conversation and all its messages"""

            async with AsyncSessionLocal() as db:
                query = select(Conversation).where(Conversation.id == conversation_id)
                result = await db.execute(query)
                conversation = result.scalar_one_or_none()

                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")

                await db.delete(conversation)
                await db.commit()

        async def archive_conversation(self, conversation_id: UUID):
            """Archive a conversation"""

            async with AsyncSessionLocal() as db:
                query = select(Conversation).where(Conversation.id == conversation_id)
                result = await db.execute(query)
                conversation = result.scalar_one_or_none()

                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")

                conversation.is_archived = True
                await db.commit()

    conversation_service = ConversationService()
    print("✅ Real ConversationService loaded")

except ImportError as e:
    print(f"⚠️  ConversationService not available: {e}")
    conversation_service = None

# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreateRequest):
    """Create a new conversation"""

    if not conversation_service:
        raise HTTPException(status_code=503, detail="Conversation service not available")

    user_id = UUID(request.user_id)
    return await conversation_service.create_conversation(user_id, request.title)


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: str,
    include_archived: bool = False,
    limit: int = 50
):
    """Get all conversations for a user"""

    if not conversation_service:
        raise HTTPException(status_code=503, detail="Conversation service not available")

    user_uuid = UUID(user_id)
    return await conversation_service.get_conversations(user_uuid, include_archived, limit)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all messages"""

    if not conversation_service:
        raise HTTPException(status_code=503, detail="Conversation service not available")

    conv_uuid = UUID(conversation_id)
    return await conversation_service.get_conversation_with_messages(conv_uuid)


@router.post("/messages", response_model=MessageResponse)
async def create_message(request: MessageCreateRequest):
    """Add a message to a conversation"""

    if not conversation_service:
        raise HTTPException(status_code=503, detail="Conversation service not available")

    return await conversation_service.create_message(
        conversation_id=UUID(request.conversation_id),
        user_id=UUID(request.user_id),
        role=request.role,
        content=request.content,
        metadata=request.metadata
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""

    if not conversation_service:
        raise HTTPException(status_code=503, detail="Conversation service not available")

    conv_uuid = UUID(conversation_id)
    await conversation_service.delete_conversation(conv_uuid)
    return {"status": "deleted"}


@router.post("/{conversation_id}/archive")
async def archive_conversation(conversation_id: str):
    """Archive a conversation"""

    if not conversation_service:
        raise HTTPException(status_code=503, detail="Conversation service not available")

    conv_uuid = UUID(conversation_id)
    await conversation_service.archive_conversation(conv_uuid)
    return {"status": "archived"}


@router.get("/health")
async def conversation_health():
    """Check if conversation service is healthy"""
    return {
        "status": "healthy" if conversation_service else "unavailable",
        "service": "conversations",
        "timestamp": datetime.now().isoformat()
    }
