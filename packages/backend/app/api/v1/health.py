"""
Health Check Endpoint
Monitors system health including database and Redis connectivity.
"""
from fastapi import APIRouter, status
from datetime import datetime
from typing import Literal

router = APIRouter()

@router.get(
    "/health",
    summary="Health Check",
    description="Check system health including database and Redis connectivity. "
                "Returns overall system status, component health, and timestamp.",
    response_description="System health status with component details",
    status_code=status.HTTP_200_OK
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
        In Story 1.1 (initial setup), this returns mock "connected" status.
        Story 1.2 will add actual database connectivity checks.
        Story 2.1 will add Redis connectivity checks.
    """
    # TODO: Add actual database connectivity check in Story 1.2
    # TODO: Add actual Redis connectivity check in Story 2.1
    
    # For now, return mock "connected" status since infrastructure isn't fully set up
    # This allows the health endpoint to work immediately for testing
    database_status: Literal["connected", "disconnected"] = "connected"
    redis_status: Literal["connected", "disconnected"] = "connected"
    
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
        "timestamp": datetime.utcnow().isoformat()
    }

