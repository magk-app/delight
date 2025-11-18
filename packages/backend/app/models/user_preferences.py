"""
AgentPreferences model - Comprehensive customization settings for AI agent behavior

Stores user-specific preferences for:
- Memory retrieval settings (recency bias, similarity thresholds)
- Model selection (which LLM to use for different tasks)
- Reasoning depth (how thorough the agent should be)
- Safety and validation settings
- Interaction style (verbosity, transparency, language)

Note: This is separate from UserPreferences (basic app settings).
      AgentPreferences controls AI behavior customization.
"""

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ModelPreference(str, Enum):
    """
    Preferred LLM models for different task types

    - AUTO: System chooses based on task complexity
    - FAST: GPT-4o-mini or similar (quick, cheap)
    - BALANCED: GPT-4o or similar (good balance)
    - POWERFUL: GPT-4 or o1 (thorough, expensive)
    """

    AUTO = "auto"
    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"


class ReasoningDepth(str, Enum):
    """
    How exhaustive the agent should be in reasoning

    - QUICK: 1-2 steps, minimal research (fast answers)
    - MEDIUM: 3-5 steps, moderate research (balanced)
    - THOROUGH: 5-10 steps, extensive research (deep analysis)
    """

    QUICK = "quick"
    MEDIUM = "medium"
    THOROUGH = "thorough"


class InteractionStyle(str, Enum):
    """
    User's preferred interaction style

    - CONCISE: Brief answers, minimal explanation
    - BALANCED: Standard responses with some detail
    - DETAILED: Verbose explanations, show thinking process
    - TRANSPARENT: Show all planning nodes and reasoning steps
    """

    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"
    TRANSPARENT = "transparent"


class AgentPreferences(Base):
    """
    User-specific customization settings for AI agent behavior

    Enables fine-tuned control over:
    - Memory retrieval (how memories are searched and ranked)
    - Model selection (which AI models to use)
    - Reasoning depth (thoroughness vs speed)
    - Safety filters (content filtering, fact-checking)
    - Interaction style (verbosity, transparency)

    Settings cascade: User preferences override system defaults.
    """

    __tablename__ = "agent_preferences"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique preference set identifier",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One preference set per user
        index=True,
        comment="User who owns these preferences",
    )

    # === Memory Settings ===
    memory_recency_bias = Column(
        Float,
        nullable=False,
        default=0.5,
        comment="Weight for recent memories (0.0=no bias, 1.0=strong recency preference)",
    )
    memory_similarity_threshold = Column(
        Float,
        nullable=False,
        default=0.4,
        comment="Minimum similarity score for memory retrieval (0.0-1.0)",
    )
    personal_memory_top_k = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Number of PERSONAL memories to retrieve in context",
    )
    project_memory_top_k = Column(
        Integer,
        nullable=False,
        default=10,
        comment="Number of PROJECT memories to retrieve in context",
    )
    task_memory_top_k = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Number of TASK memories to retrieve in context",
    )
    enable_memory_grouping = Column(
        JSONB,
        nullable=True,
        default={"by_project": True, "by_type": True},
        comment="Enable memory grouping strategies (JSONB)",
    )

    # === Model Selection Settings ===
    default_model_preference = Column(
        SQLEnum(
            ModelPreference,
            name="model_preference",
            create_type=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ModelPreference.AUTO,
        comment="Default model selection strategy",
    )
    task_specific_models = Column(
        JSONB,
        nullable=True,
        default={
            "coding": "fast",
            "writing": "balanced",
            "analysis": "powerful",
            "conversation": "fast",
        },
        comment="Model preferences per task type (JSONB)",
    )

    # === Reasoning Settings ===
    reasoning_depth = Column(
        SQLEnum(
            ReasoningDepth,
            name="reasoning_depth",
            create_type=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ReasoningDepth.MEDIUM,
        comment="Default reasoning thoroughness",
    )
    max_research_cycles = Column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum research/reasoning cycles for complex tasks",
    )
    enable_multi_hop_reasoning = Column(
        JSONB,
        nullable=True,
        default={"enabled": True, "max_hops": 5},
        comment="Multi-hop reasoning settings (JSONB)",
    )

    # === Safety and Validation Settings ===
    content_filter_level = Column(
        String(20),
        nullable=False,
        default="medium",
        comment="Content filtering strictness: low, medium, high",
    )
    enable_fact_verification = Column(
        JSONB,
        nullable=True,
        default={"enabled": False, "require_sources": False},
        comment="Fact-checking and source verification settings (JSONB)",
    )
    allowed_search_domains = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Whitelist of allowed domains for web search (empty = all allowed)",
    )
    blocked_search_domains = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Blacklist of blocked domains for web search",
    )

    # === Interaction Style Settings ===
    interaction_style = Column(
        SQLEnum(
            InteractionStyle,
            name="interaction_style",
            create_type=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=InteractionStyle.BALANCED,
        comment="Preferred response verbosity and detail level",
    )
    show_planning_nodes = Column(
        JSONB,
        nullable=True,
        default={"enabled": False, "on_request": True},
        comment="Display AI planning/reasoning process (JSONB)",
    )
    preferred_language = Column(
        String(10),
        nullable=False,
        default="en",
        comment="Preferred language for responses (ISO 639-1 code)",
    )
    use_technical_jargon = Column(
        JSONB,
        nullable=True,
        default={"enabled": True, "domains": []},
        comment="Use technical terminology (JSONB with allowed domains)",
    )

    # === Custom Settings (Extensibility) ===
    custom_settings = Column(
        JSONB,
        nullable=True,
        default={},
        comment="User-defined custom preferences (extensible JSONB)",
    )

    # === Metadata ===
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Preferences creation timestamp",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp",
    )

    # Relationships
    user = relationship("User", back_populates="agent_preferences")

    def __repr__(self) -> str:
        return (
            f"<AgentPreferences(user_id={self.user_id}, "
            f"model={self.default_model_preference}, "
            f"reasoning={self.reasoning_depth}, "
            f"style={self.interaction_style})>"
        )

    def to_dict(self) -> dict:
        """Convert preferences to dictionary for easy access"""
        return {
            "memory": {
                "recency_bias": self.memory_recency_bias,
                "similarity_threshold": self.memory_similarity_threshold,
                "top_k": {
                    "personal": self.personal_memory_top_k,
                    "project": self.project_memory_top_k,
                    "task": self.task_memory_top_k,
                },
                "grouping": self.enable_memory_grouping,
            },
            "models": {
                "default": self.default_model_preference,
                "task_specific": self.task_specific_models,
            },
            "reasoning": {
                "depth": self.reasoning_depth,
                "max_cycles": self.max_research_cycles,
                "multi_hop": self.enable_multi_hop_reasoning,
            },
            "safety": {
                "filter_level": self.content_filter_level,
                "fact_verification": self.enable_fact_verification,
                "search_domains": {
                    "allowed": self.allowed_search_domains,
                    "blocked": self.blocked_search_domains,
                },
            },
            "interaction": {
                "style": self.interaction_style,
                "show_planning": self.show_planning_nodes,
                "language": self.preferred_language,
                "technical_jargon": self.use_technical_jargon,
            },
            "custom": self.custom_settings,
        }
