"""
ModelRouter - Intelligent model selection based on task type and user preferences

Features:
- Automatic model selection based on task complexity
- User preference overrides (fast, balanced, powerful)
- Task-specific model routing (coding, writing, analysis)
- Cost optimization (use cheaper models for simple tasks)
- Fallback mechanisms for model unavailability

Model Tiers:
- FAST: GPT-4o-mini, Claude Haiku (~$0.15/$0.60 per 1M tokens)
- BALANCED: GPT-4o, Claude Sonnet (~$2.50/$10 per 1M tokens)
- POWERFUL: GPT-4, Claude Opus, o1 (~$15/$60+ per 1M tokens)

Usage:
    router = get_model_router()
    model_config = await router.select_model(
        db, user_id, task_type="analysis", estimated_complexity=0.8
    )
    # Returns: {"provider": "openai", "model": "gpt-4o", "max_tokens": 4096, ...}
"""

import logging
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preferences import AgentPreferences, ModelPreference, ReasoningDepth
from app.core.config import settings

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Classification of AI tasks for model routing"""

    CONVERSATION = "conversation"  # Chat, casual interaction
    CODING = "coding"  # Code generation, debugging
    WRITING = "writing"  # Content creation, editing
    ANALYSIS = "analysis"  # Deep reasoning, research
    PLANNING = "planning"  # Goal planning, strategy
    EMOTION = "emotion"  # Emotional intelligence, companionship


class ModelConfig:
    """Configuration for a specific model"""

    def __init__(
        self,
        provider: str,
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        cost_per_1m_input: float = 0.0,
        cost_per_1m_output: float = 0.0,
    ):
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.cost_per_1m_input = cost_per_1m_input
        self.cost_per_1m_output = cost_per_1m_output

    def to_dict(self) -> Dict:
        return {
            "provider": self.provider,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "cost_per_1m_input": self.cost_per_1m_input,
            "cost_per_1m_output": self.cost_per_1m_output,
        }


# Model tier configurations
MODEL_TIERS = {
    "fast": {
        "openai": ModelConfig(
            provider="openai",
            model="gpt-4o-mini",
            max_tokens=4096,
            temperature=0.7,
            cost_per_1m_input=0.15,
            cost_per_1m_output=0.60,
        ),
        "anthropic": ModelConfig(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0.7,
            cost_per_1m_input=0.25,
            cost_per_1m_output=1.25,
        ),
    },
    "balanced": {
        "openai": ModelConfig(
            provider="openai",
            model="gpt-4o",
            max_tokens=8192,
            temperature=0.7,
            cost_per_1m_input=2.50,
            cost_per_1m_output=10.0,
        ),
        "anthropic": ModelConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0.7,
            cost_per_1m_input=3.0,
            cost_per_1m_output=15.0,
        ),
    },
    "powerful": {
        "openai": ModelConfig(
            provider="openai",
            model="o1-preview",
            max_tokens=8192,
            temperature=1.0,  # o1 uses fixed temperature
            cost_per_1m_input=15.0,
            cost_per_1m_output=60.0,
        ),
        "anthropic": ModelConfig(
            provider="anthropic",
            model="claude-3-opus-20240229",
            max_tokens=8192,
            temperature=0.7,
            cost_per_1m_input=15.0,
            cost_per_1m_output=75.0,
        ),
    },
}


class ModelRouter:
    """Intelligent model selection based on task and user preferences"""

    def __init__(self):
        """Initialize model router with default provider"""
        self.default_provider = "openai"  # Default to OpenAI
        self.fallback_tier = "balanced"  # Fallback to balanced models

    async def get_user_preferences(
        self, db: AsyncSession, user_id: UUID
    ) -> Optional[AgentPreferences]:
        """
        Load user's agent preferences from database

        Args:
            db: Database session
            user_id: User ID

        Returns:
            AgentPreferences or None (will use system defaults)
        """
        result = await db.execute(
            db.query(AgentPreferences).filter(AgentPreferences.user_id == user_id)
        )
        return result.scalar_one_or_none()

    def _estimate_task_complexity(
        self,
        task_type: TaskType,
        reasoning_depth: ReasoningDepth,
        estimated_complexity: Optional[float] = None,
    ) -> float:
        """
        Estimate task complexity score (0.0-1.0)

        Args:
            task_type: Type of task
            reasoning_depth: User's reasoning depth preference
            estimated_complexity: Optional manual complexity estimate

        Returns:
            Complexity score (0.0 = simple, 1.0 = very complex)
        """
        if estimated_complexity is not None:
            return max(0.0, min(1.0, estimated_complexity))

        # Base complexity by task type
        task_complexity = {
            TaskType.CONVERSATION: 0.2,
            TaskType.CODING: 0.6,
            TaskType.WRITING: 0.4,
            TaskType.ANALYSIS: 0.8,
            TaskType.PLANNING: 0.7,
            TaskType.EMOTION: 0.5,
        }

        base_score = task_complexity.get(task_type, 0.5)

        # Adjust for reasoning depth
        depth_multiplier = {
            ReasoningDepth.QUICK: 0.8,
            ReasoningDepth.MEDIUM: 1.0,
            ReasoningDepth.THOROUGH: 1.2,
        }

        final_score = base_score * depth_multiplier.get(reasoning_depth, 1.0)
        return max(0.0, min(1.0, final_score))

    def _select_tier_by_complexity(self, complexity: float) -> str:
        """
        Select model tier based on complexity score

        Args:
            complexity: Complexity score (0.0-1.0)

        Returns:
            Model tier: "fast", "balanced", or "powerful"
        """
        if complexity < 0.3:
            return "fast"
        elif complexity < 0.7:
            return "balanced"
        else:
            return "powerful"

    async def select_model(
        self,
        db: AsyncSession,
        user_id: UUID,
        task_type: TaskType = TaskType.CONVERSATION,
        estimated_complexity: Optional[float] = None,
        override_preference: Optional[ModelPreference] = None,
    ) -> Dict:
        """
        Select optimal model based on task and user preferences

        Args:
            db: Database session
            user_id: User ID
            task_type: Type of task to perform
            estimated_complexity: Optional manual complexity estimate (0.0-1.0)
            override_preference: Override user preference for this task

        Returns:
            Model configuration dict
        """
        # Load user preferences
        user_prefs = await self.get_user_preferences(db, user_id)

        # Determine model preference
        if override_preference:
            model_pref = override_preference
        elif user_prefs:
            # Check task-specific preference
            task_specific_prefs = user_prefs.task_specific_models or {}
            task_pref = task_specific_prefs.get(task_type.value)

            if task_pref:
                model_pref = ModelPreference(task_pref)
            else:
                model_pref = user_prefs.default_model_preference
        else:
            model_pref = ModelPreference.AUTO

        # Get reasoning depth
        reasoning_depth = (
            user_prefs.reasoning_depth if user_prefs else ReasoningDepth.MEDIUM
        )

        # AUTO mode: select based on complexity
        if model_pref == ModelPreference.AUTO:
            complexity = self._estimate_task_complexity(
                task_type, reasoning_depth, estimated_complexity
            )
            tier = self._select_tier_by_complexity(complexity)

            logger.info(
                f"AUTO mode: task={task_type}, complexity={complexity:.2f}, "
                f"selected tier={tier}"
            )
        else:
            # Use explicit preference
            tier_mapping = {
                ModelPreference.FAST: "fast",
                ModelPreference.BALANCED: "balanced",
                ModelPreference.POWERFUL: "powerful",
            }
            tier = tier_mapping.get(model_pref, "balanced")

            logger.info(
                f"Explicit mode: task={task_type}, preference={model_pref}, tier={tier}"
            )

        # Get model config
        provider_models = MODEL_TIERS.get(tier, MODEL_TIERS[self.fallback_tier])
        model_config = provider_models.get(
            self.default_provider, list(provider_models.values())[0]
        )

        result = model_config.to_dict()
        result["tier"] = tier
        result["task_type"] = task_type.value

        logger.info(
            f"Selected model for user {user_id}: {result['provider']}/{result['model']} "
            f"(tier: {tier}, task: {task_type.value})"
        )

        return result

    async def estimate_cost(
        self, model_config: Dict, input_tokens: int, output_tokens: int
    ) -> float:
        """
        Estimate cost for a model call

        Args:
            model_config: Model configuration from select_model()
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens

        Returns:
            Estimated cost in USD
        """
        cost_input = (input_tokens / 1_000_000) * model_config["cost_per_1m_input"]
        cost_output = (output_tokens / 1_000_000) * model_config["cost_per_1m_output"]
        total_cost = cost_input + cost_output

        logger.debug(
            f"Cost estimate: {model_config['model']} - "
            f"input: ${cost_input:.6f}, output: ${cost_output:.6f}, "
            f"total: ${total_cost:.6f}"
        )

        return total_cost

    def get_available_models(self) -> Dict[str, Dict]:
        """
        Get all available models by tier

        Returns:
            Dict mapping tier -> provider -> ModelConfig
        """
        return MODEL_TIERS


# Singleton instance
_model_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """
    Get singleton instance of ModelRouter

    Returns:
        ModelRouter instance
    """
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
