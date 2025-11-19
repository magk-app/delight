"""
Token Usage Model

Tracks OpenAI API token consumption and costs across all operations:
- Chat completions
- Fact extraction
- Categorization
- Embedding generation
- Other AI operations
"""

from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, UUID, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base


class OperationType(str, enum.Enum):
    """Types of operations that consume tokens"""
    CHAT = "chat"
    FACT_EXTRACTION = "fact_extraction"
    CATEGORIZATION = "categorization"
    EMBEDDING = "embedding"
    REASONING = "reasoning"
    OTHER = "other"


class TokenUsage(Base):
    """Record of token usage for a single API call"""
    __tablename__ = "token_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Operation details
    operation_type = Column(SQLEnum(OperationType), nullable=False)
    model = Column(String(100), nullable=False)  # e.g., "gpt-4o-mini", "text-embedding-3-small"

    # Token counts
    tokens_input = Column(Integer, nullable=False, default=0)
    tokens_output = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)

    # Cost calculation (in USD)
    cost_input = Column(Float, nullable=False, default=0.0)
    cost_output = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)

    # Metadata
    metadata = Column(JSONB, nullable=True)  # Additional context (conversation_id, memory_id, etc.)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="token_usage")

    def __repr__(self):
        return (
            f"<TokenUsage(id={self.id}, model={self.model}, "
            f"tokens={self.total_tokens}, cost=${self.total_cost:.4f})>"
        )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "operation_type": self.operation_type.value,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "total_tokens": self.total_tokens,
            "cost_input": self.cost_input,
            "cost_output": self.cost_output,
            "total_cost": self.total_cost,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
