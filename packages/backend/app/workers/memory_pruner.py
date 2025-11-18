"""
ARQ background worker for memory pruning.

Scheduled to run daily at 2:00 AM to prune old task memories (30-day retention).
Personal and project memories are never pruned.
"""

import logging
from typing import Any, Dict

from arq import cron
from arq.connections import RedisSettings

from app.core.config import settings
from app.db.session import async_session_maker
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)


async def prune_task_memories_job(ctx: Dict[str, Any]) -> int:
    """
    ARQ worker job to prune old task memories.

    Deletes task memories older than 30 days. Personal and project
    memories are never pruned (permanent retention).

    Scheduled to run daily at 2:00 AM (low traffic time).

    Args:
        ctx: ARQ context dictionary (contains redis connection, etc.)

    Returns:
        Number of memories deleted

    Example:
        # Triggered automatically by ARQ scheduler at 2:00 AM
        # Or manually for testing:
        >>> from app.workers.memory_pruner import prune_task_memories_job
        >>> deleted_count = await prune_task_memories_job({})
        >>> print(f"Pruned {deleted_count} task memories")
    """
    logger.info("Starting memory pruning job...")

    try:
        # Create database session
        async with async_session_maker() as db:
            # Initialize memory service
            service = MemoryService(db)

            # Prune old task memories (30-day retention)
            deleted_count = await service.prune_old_task_memories(retention_days=30)

            logger.info(
                f"Memory pruning job completed successfully. Deleted {deleted_count} task memories."
            )

            return deleted_count

    except Exception as e:
        logger.error(
            f"Memory pruning job failed: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        # Re-raise exception to trigger ARQ retry mechanism
        raise


class WorkerSettings:
    """
    ARQ worker configuration for memory pruning.

    - Cron Schedule: Daily at 2:00 AM UTC
    - Max Retries: 3 attempts with exponential backoff (2s, 4s, 8s)
    - Redis Connection: Uses REDIS_URL from settings
    """

    # Redis connection settings
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL) if settings.REDIS_URL else None

    # Cron jobs configuration
    cron_jobs = [
        # Run daily at 2:00 AM UTC (low traffic time)
        cron(prune_task_memories_job, hour=2, minute=0, run_at_startup=False),
    ]

    # Job retry configuration
    max_tries = 3  # Retry up to 3 times on failure
    job_timeout = 600  # 10 minutes max execution time

    # Logging
    log_results = True  # Log job results (success/failure)

    # Worker configuration
    queue_name = "delight:memory-pruner"
    worker_name = "memory-pruner"


# Export for ARQ CLI
__all__ = ["WorkerSettings", "prune_task_memories_job"]
