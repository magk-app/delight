"""
Health Check Endpoint
Monitors system health including database and Redis connectivity.
"""

import os
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, status
from sqlalchemy import text

from app.db.session import AsyncSessionLocal

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Check system health including database and Redis connectivity. "
    "Returns overall system status, component health, and timestamp.",
    response_description="System health status with component details",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Health check endpoint for monitoring system status.

    This endpoint checks the health of critical system components:
    - Overall system status (healthy/degraded/unhealthy)
    - Database connectivity status
    - Redis connectivity status
    - Current server timestamp

    Returns:
        dict: Health status object containing:
            - status: Overall system health (healthy | degraded | unhealthy)
            - database: Database connection status (connected | disconnected)
            - redis: Redis connection status (connected | disconnected)
            - timestamp: Current server time in ISO 8601 format

    Example Response:
        {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": "2025-11-10T12:00:00.000000"
        }

    Note:
        In Story 1.1 (initial setup), this returns mock "connected" status in test mode.
        Story 1.2 will add actual database connectivity checks.
        Story 2.1 will add Redis connectivity checks.
    """
    # In test environment, return mock statuses (Story 1.1 behavior)
    is_test_env = os.getenv("ENVIRONMENT") in ["test", "testing"]

    if is_test_env:
        # Mock values for testing (Story 1.1)
        database_status: Literal["connected", "disconnected"] = "connected"
        redis_status: Literal["connected", "disconnected"] = "connected"
    else:
        # Real connectivity checks (Story 1.2+)
        # Database connectivity check
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            database_status = "connected"
        except Exception:
            database_status = "disconnected"

        # TODO: Add actual Redis connectivity check in Story 2.1
        redis_status = "connected"

    # Determine overall system status based on components
    if database_status == "connected" and redis_status == "connected":
        system_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    elif database_status == "disconnected" and redis_status == "disconnected":
        system_status = "unhealthy"
    else:
        system_status = "degraded"

    return {
        "status": system_status,
        "database": database_status,
        "redis": redis_status,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/health/debug",
    summary="Debug Health Check",
    description="Extended health check with environment and dependency status for deployment debugging. "
    "Shows which environment variables are set (without exposing values) and which routes are registered.",
    response_description="Extended diagnostic information",
    status_code=status.HTTP_200_OK,
)
async def health_debug():
    """
    Extended health check for deployment troubleshooting.

    This diagnostic endpoint helps identify configuration issues on Railway or other
    deployment platforms. It shows:
    - Environment variable configuration status
    - Database connectivity
    - Python dependencies import status
    - Registered API routes
    - Python version

    **IMPORTANT:** This endpoint does NOT expose secret values, only whether
    variables are set or not.

    Returns:
        dict: Extended diagnostic information including:
            - status: "debug"
            - environment: Current environment name
            - database: Database connection status
            - imports: Status of critical Python packages
            - env_vars: Which environment variables are configured
            - routes: Sample of registered API routes
            - python_version: Python interpreter version

    Example Response:
        {
            "status": "debug",
            "environment": "production",
            "database": "connected",
            "imports": {
                "openai": "✅ available",
                "companion": "✅ loaded (3 routes)"
            },
            "env_vars": {
                "OPENAI_API_KEY": "✅ set",
                "CLERK_JWKS_URL": "⚠️ not set"
            },
            "routes": {
                "status": "✅ 12 routes registered",
                "sample": ["GET /health", "POST /companion/chat", ...]
            }
        }
    """
    from app.core.config import settings

    # Test database connection
    db_status = "unknown"
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            db_status = "connected" if result.scalar() == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"

    # Test critical imports
    imports_status = {}
    try:
        from openai import AsyncOpenAI
        imports_status["openai"] = "✅ available"
    except ImportError as e:
        imports_status["openai"] = f"❌ missing: {str(e)}"

    try:
        from app.api.v1 import companion
        imports_status["companion"] = f"✅ loaded ({len(companion.router.routes)} routes)"
    except Exception as e:
        imports_status["companion"] = f"❌ failed: {str(e)[:100]}"

    try:
        from app.agents.simple_eliza import SimpleElizaAgent
        imports_status["simple_eliza"] = "✅ available"
    except Exception as e:
        imports_status["simple_eliza"] = f"❌ failed: {str(e)[:100]}"

    # Check environment variables (WITHOUT exposing actual values)
    env_vars = {
        "DATABASE_URL": "✅ set" if settings.DATABASE_URL else "❌ missing",
        "CLERK_SECRET_KEY": "✅ set" if settings.CLERK_SECRET_KEY else "❌ missing",
        "CLERK_WEBHOOK_SECRET": "✅ set" if settings.CLERK_WEBHOOK_SECRET else "❌ missing",
        "CLERK_JWKS_URL": "✅ set" if settings.CLERK_JWKS_URL else "⚠️ not set (will auto-detect)",
        "OPENAI_API_KEY": "✅ set" if settings.OPENAI_API_KEY else "❌ missing (companion will fail)",
        "REDIS_URL": "✅ set" if settings.REDIS_URL else "⚠️ not set (optional)",
        "CORS_ORIGINS": settings.CORS_ORIGINS or "⚠️ using defaults (localhost only)",
    }

    # Check registered API routes
    try:
        from app.api.v1 import api_router
        all_routes = []
        for route in api_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ", ".join(sorted(route.methods))
                all_routes.append(f"{methods} {route.path}")
        routes_status = f"✅ {len(all_routes)} routes registered"
        sample_routes = all_routes[:15]  # First 15 routes
    except Exception as e:
        routes_status = f"❌ failed: {str(e)[:100]}"
        sample_routes = []

    import sys

    return {
        "status": "debug",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "database": db_status,
        "imports": imports_status,
        "env_vars": env_vars,
        "routes": {
            "status": routes_status,
            "sample": sample_routes,
        },
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
    }
