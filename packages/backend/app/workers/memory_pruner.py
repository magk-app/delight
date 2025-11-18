"""
Memory Pruner Worker - Background job for pruning old TASK memories

Runs daily at 2:00 AM to delete TASK memories older than 30 days.
PERSONAL and PROJECT memories are never pruned.

Uses ARQ (async Redis queue) for background job scheduling.

Setup:
    1. Add to ARQ worker settings in app/core/config.py
    2. Start ARQ worker: poetry run arq app.workers.memory_pruner.WorkerSettings

Cron Schedule:
    - Every day at 2:00 AM UTC
    - Alternative: Configure via settings for user's timezone
"""

import logging
from datetime import datetime, timezone
from typing import Dict
from urllib.parse import urlparse

from arq import cron
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.memory_service import get_memory_service

logger = logging.getLogger(__name__)


async def prune_old_task_memories(ctx: Dict) -> Dict[str, int]:
    """
    Prune TASK memories older than 30 days for all users

    This is the main background job function called by ARQ.

    Args:
        ctx: ARQ context (contains Redis connection, job metadata)

    Returns:
        Dict with pruning statistics
    """
    logger.info("Starting memory pruning job...")
    start_time = datetime.now(timezone.utc)

    # Create database session
    engine = create_async_engine(
        settings.async_database_url,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with async_session() as session:
            memory_service = get_memory_service()

            # Prune for all users (user_id=None)
            deleted_count = await memory_service.prune_old_task_memories(
                session, user_id=None
            )

            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            logger.info(
                f"Memory pruning completed: {deleted_count} memories deleted "
                f"in {duration:.2f} seconds"
            )

            return {
                "deleted_count": deleted_count,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat(),
            }

    except Exception as e:
        logger.error(f"Memory pruning failed: {e}")
        raise

    finally:
        await engine.dispose()


async def prune_user_task_memories(ctx: Dict, user_id: str) -> Dict[str, int]:
    """
    Prune TASK memories for a specific user

    Can be called on-demand via ARQ enqueue:
        await redis.enqueue_job('prune_user_task_memories', user_id='...')

    Args:
        ctx: ARQ context
        user_id: User ID (string, will be converted to UUID)

    Returns:
        Dict with pruning statistics
    """
    from uuid import UUID

    logger.info(f"Starting memory pruning for user {user_id}...")
    start_time = datetime.now(timezone.utc)

    # Create database session
    engine = create_async_engine(
        settings.async_database_url,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with async_session() as session:
            memory_service = get_memory_service()

            # Prune for specific user
            deleted_count = await memory_service.prune_old_task_memories(
                session, user_id=UUID(user_id)
            )

            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            logger.info(
                f"Memory pruning completed for user {user_id}: "
                f"{deleted_count} memories deleted in {duration:.2f} seconds"
            )

            return {
                "deleted_count": deleted_count,
                "duration_seconds": duration,
                "user_id": user_id,
                "timestamp": end_time.isoformat(),
            }

    except Exception as e:
        logger.error(f"Memory pruning failed for user {user_id}: {e}")
        raise

    finally:
        await engine.dispose()


async def on_startup(ctx: Dict) -> None:
    """
    ARQ worker startup hook

    Initialize any resources needed for background jobs.
    """
    logger.info("Memory pruner worker starting up...")
    ctx["start_time"] = datetime.now(timezone.utc)


async def on_shutdown(ctx: Dict) -> None:
    """
    ARQ worker shutdown hook

    Clean up resources on shutdown.
    """
    if "start_time" in ctx:
        uptime = datetime.now(timezone.utc) - ctx["start_time"]
        logger.info(f"Memory pruner worker shutting down (uptime: {uptime})")


def parse_redis_url(url: str) -> tuple:
    """
    Parse Redis URL into host and port

    Args:
        url: Redis URL (e.g., redis://localhost:6379, redis://user:pass@host:port/db)

    Returns:
        (host, port) tuple
    """
    if not url:
        return ("localhost", 6379)

    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    return (host, port)


# ARQ worker configuration
class WorkerSettings:
    """
    ARQ worker settings for memory pruning jobs

    Usage:
        poetry run arq app.workers.memory_pruner.WorkerSettings
    """

    # Redis connection
    redis_host, redis_port = parse_redis_url(settings.REDIS_URL) if settings.REDIS_URL else ("localhost", 6379)
    redis_settings = RedisSettings(host=redis_host, port=redis_port)

    # Job functions
    functions = [prune_old_task_memories, prune_user_task_memories]

    # Startup/shutdown hooks
    on_startup = on_startup
    on_shutdown = on_shutdown

    # Cron jobs - run daily at 2:00 AM UTC
    cron_jobs = [
        cron(prune_old_task_memories, hour=2, minute=0, run_at_startup=False)
    ]

    # Worker settings
    max_jobs = 10  # Maximum concurrent jobs
    job_timeout = 600  # 10 minutes timeout
    keep_result = 86400  # Keep job results for 24 hours

    # Logging
    log_results = True

    # Retry settings
    max_tries = 3  # Retry failed jobs up to 3 times
    retry_jobs = True


# Manual execution for testing
async def run_prune_now():
    """
    Manually run memory pruning (for testing)

    Usage:
        poetry run python -c "import asyncio; from app.workers.memory_pruner import run_prune_now; asyncio.run(run_prune_now())"
    """
    result = await prune_old_task_memories({})
    print(f"Pruning result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_prune_now())
