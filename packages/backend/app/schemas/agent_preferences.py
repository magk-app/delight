"""
Pydantic schemas for AgentPreferences.
Used for request validation and response serialization in API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.user_preferences import (
    ModelPreference,
    ReasoningDepth,
    InteractionStyle,
)


# ============================================================================
# AgentPreferences Schemas
# ============================================================================


class AgentPreferencesBase(BaseModel):
    """Base schema with common agent preferences fields"""

    # Memory Settings
    memory_recency_bias: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Weight for recent memories (0.0=no bias, 1.0=strong recency)",
    )
    memory_similarity_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for memory retrieval",
    )
    personal_memory_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of PERSONAL memories to retrieve",
    )
    project_memory_top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of PROJECT memories to retrieve",
    )
    task_memory_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of TASK memories to retrieve",
    )
    enable_memory_grouping: Optional[Dict[str, Any]] = Field(
        default={"by_project": True, "by_type": True},
        description="Memory grouping strategies",
    )

    # Model Selection Settings
    default_model_preference: ModelPreference = Field(
        default=ModelPreference.AUTO,
        description="Default model selection strategy",
    )
    task_specific_models: Optional[Dict[str, str]] = Field(
        default={
            "coding": "fast",
            "writing": "balanced",
            "analysis": "powerful",
            "conversation": "fast",
        },
        description="Model preferences per task type",
    )

    # Reasoning Settings
    reasoning_depth: ReasoningDepth = Field(
        default=ReasoningDepth.MEDIUM,
        description="Default reasoning thoroughness",
    )
    max_research_cycles: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum research/reasoning cycles",
    )
    enable_multi_hop_reasoning: Optional[Dict[str, Any]] = Field(
        default={"enabled": True, "max_hops": 5},
        description="Multi-hop reasoning settings",
    )

    # Safety Settings
    content_filter_level: str = Field(
        default="medium",
        description="Content filtering strictness: low, medium, high",
    )
    enable_fact_verification: Optional[Dict[str, bool]] = Field(
        default={"enabled": False, "require_sources": False},
        description="Fact-checking and source verification",
    )
    allowed_search_domains: List[str] = Field(
        default=[],
        description="Whitelist of allowed domains (empty = all allowed)",
    )
    blocked_search_domains: List[str] = Field(
        default=[],
        description="Blacklist of blocked domains",
    )

    # Interaction Style Settings
    interaction_style: InteractionStyle = Field(
        default=InteractionStyle.BALANCED,
        description="Response verbosity and detail level",
    )
    show_planning_nodes: Optional[Dict[str, bool]] = Field(
        default={"enabled": False, "on_request": True},
        description="Display AI planning/reasoning process",
    )
    preferred_language: str = Field(
        default="en",
        max_length=10,
        description="Preferred language (ISO 639-1 code)",
    )
    use_technical_jargon: Optional[Dict[str, Any]] = Field(
        default={"enabled": True, "domains": []},
        description="Use technical terminology",
    )

    # Custom Settings
    custom_settings: Dict[str, Any] = Field(
        default={},
        description="User-defined custom preferences",
    )

    @field_validator("content_filter_level")
    @classmethod
    def validate_filter_level(cls, v: str) -> str:
        """Validate content filter level"""
        if v not in ["low", "medium", "high"]:
            raise ValueError("content_filter_level must be: low, medium, or high")
        return v


class AgentPreferencesCreate(AgentPreferencesBase):
    """Schema for creating agent preferences"""

    pass


class AgentPreferencesUpdate(BaseModel):
    """Schema for updating agent preferences (partial updates allowed)"""

    # All fields optional
    memory_recency_bias: Optional[float] = Field(None, ge=0.0, le=1.0)
    memory_similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    personal_memory_top_k: Optional[int] = Field(None, ge=1, le=20)
    project_memory_top_k: Optional[int] = Field(None, ge=1, le=50)
    task_memory_top_k: Optional[int] = Field(None, ge=1, le=20)
    enable_memory_grouping: Optional[Dict[str, Any]] = None

    default_model_preference: Optional[ModelPreference] = None
    task_specific_models: Optional[Dict[str, str]] = None

    reasoning_depth: Optional[ReasoningDepth] = None
    max_research_cycles: Optional[int] = Field(None, ge=1, le=10)
    enable_multi_hop_reasoning: Optional[Dict[str, Any]] = None

    content_filter_level: Optional[str] = None
    enable_fact_verification: Optional[Dict[str, bool]] = None
    allowed_search_domains: Optional[List[str]] = None
    blocked_search_domains: Optional[List[str]] = None

    interaction_style: Optional[InteractionStyle] = None
    show_planning_nodes: Optional[Dict[str, bool]] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    use_technical_jargon: Optional[Dict[str, Any]] = None

    custom_settings: Optional[Dict[str, Any]] = None

    @field_validator("content_filter_level")
    @classmethod
    def validate_filter_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate content filter level"""
        if v is not None and v not in ["low", "medium", "high"]:
            raise ValueError("content_filter_level must be: low, medium, or high")
        return v


class AgentPreferencesResponse(AgentPreferencesBase):
    """Schema for agent preferences responses from API"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
