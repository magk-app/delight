"""
User and UserPreferences database models.
Defines core user tables with Clerk integration.
"""

import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    Core user model.
    Uses Clerk for authentication - clerk_user_id is the authoritative identifier.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(
        String(255), unique=True, nullable=False, index=True, comment="Clerk user ID"
    )
    email = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    memories = relationship(
        "Memory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    memory_collections = relationship(
        "MemoryCollection",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    token_usage = relationship(
        "TokenUsage",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, clerk_user_id={self.clerk_user_id}, email={self.email})>"


class UserPreferences(Base):
    """
    User preferences and onboarding state.
    One-to-one relationship with User.
    """

    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    custom_hours = Column(
        JSONB,
        comment="Format: {start: '09:00', end: '17:00', timezone: 'America/Los_Angeles'}",
    )
    theme = Column(String(50), default="modern")
    communication_preferences = Column(
        JSONB, comment="Format: {email: true, sms: false, in_app: true}"
    )
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences(id={self.id}, user_id={self.user_id}, theme={self.theme})>"
