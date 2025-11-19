"""
Conversation and ChatMessage models for persistent chat history.

Allows storing and retrieving complete conversation threads with all messages.
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Conversation(Base):
    """
    Conversation thread containing multiple messages.

    A conversation represents a complete chat session with the AI.
    Users can have multiple conversations, and can switch between them.
    """

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Conversation metadata
    title = Column(String(255), nullable=True)  # Auto-generated from first message
    message_count = Column(Integer, default=0, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", lazy="selectin")
    user = relationship("User", back_populates="conversations")

    # Indexes
    __table_args__ = (
        Index("idx_user_conversations", "user_id", "updated_at"),
        Index("idx_archived_conversations", "user_id", "is_archived", "updated_at"),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, messages={self.message_count})>"


class ChatMessage(Base):
    """
    Individual chat message within a conversation.

    Messages can be from:
    - user: User's input
    - assistant: AI's response
    - system: System notifications or instructions
    """

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)

    # Associated memories
    metadata = Column(JSONB, nullable=True)  # memories_retrieved, memories_created, etc.

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_conversation_messages", "conversation_id", "created_at"),
        Index("idx_user_messages", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, content={self.content[:50]}...)>"
