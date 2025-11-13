"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1 import companion, health, users, webhooks

api_router = APIRouter()

# Register all v1 routers
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(webhooks.router)
api_router.include_router(companion.router)
