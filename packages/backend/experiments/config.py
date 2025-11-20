"""Experimental system configuration.

This module provides shared configuration for the experimental AI agent system.
Separate from production config to allow independent experimentation.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# Load .env file automatically
from dotenv import load_dotenv

# Load from backend/.env
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️  No .env file found at {env_file}")


@dataclass
class ExperimentConfig:
    """Configuration for experimental system."""

    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    read_only_mode: bool = False  # Safety flag for testing

    # Fallback storage (when PostgreSQL unavailable)
    use_json_storage: bool = os.getenv("USE_JSON_STORAGE", "false").lower() == "true"
    json_storage_path: str = os.getenv(
        "JSON_STORAGE_PATH",
        str(Path(__file__).parent / "data" / "memories.json")
    )

    # OpenAI Models (configurable)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Embedding model
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dimensions: int = 1536

    # Chat models - choose based on needs
    # Options: gpt-4o-mini, gpt-4o, gpt-4-turbo, o1-preview, o1-mini
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")  # Default: fast & cheap
    reasoning_model: str = os.getenv("REASONING_MODEL", "o1-preview")  # For complex reasoning
    expensive_model: str = os.getenv("EXPENSIVE_MODEL", "gpt-4o")  # For high-quality outputs

    # Model selection presets
    MODELS = {
        # Fast & cheap (default)
        "mini": "gpt-4o-mini",

        # Balanced
        "4o": "gpt-4o",
        "turbo": "gpt-4-turbo",

        # Reasoning (for complex tasks)
        "o1": "o1-preview",
        "o1-mini": "o1-mini",

        # Legacy
        "gpt4": "gpt-4",
    }

    # Memory system
    max_personal_memories: int = 10000
    max_project_memories: int = 5000
    max_task_memories: int = 100
    task_memory_ttl_hours: int = 24
    similarity_threshold: float = 0.7

    # Fact extraction
    min_fact_length: int = 10
    max_facts_per_message: int = 20
    auto_categorize: bool = True
    max_categories_per_fact: int = 3

    # Search
    default_search_limit: int = 10
    max_search_limit: int = 100
    hybrid_search_weight_vector: float = 0.7  # 70% vector, 30% keyword
    graph_traversal_max_depth: int = 3

    # Agent
    max_parallel_tasks: int = 5
    max_sequential_depth: int = 10
    enable_workflow_visualization: bool = True
    require_user_approval: bool = False  # For plans

    # Web interface
    web_host: str = "localhost"
    web_port: int = 5000
    enable_websocket: bool = True

    # Safety
    max_api_calls_per_minute: int = 60
    max_tokens_per_request: int = 4000
    enable_cost_tracking: bool = True
    warn_before_expensive_operations: bool = True

    # Paths
    experiments_root: Path = Path(__file__).parent
    templates_dir: Path = experiments_root / "web" / "templates"
    static_dir: Path = experiments_root / "web" / "static"


# Global config instance
config = ExperimentConfig()


def get_config() -> ExperimentConfig:
    """Get experiment configuration."""
    return config


def set_read_only(enabled: bool = True):
    """Enable/disable read-only mode for safety."""
    config.read_only_mode = enabled
    if enabled:
        print("⚠️  READ-ONLY MODE ENABLED - No database writes allowed")
    else:
        print("✅ Read-only mode disabled - Database writes allowed")
