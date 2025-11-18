"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1 import health, users, webhooks, workflows, workflow_sse

api_router = APIRouter()

# Register all v1 routers
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(webhooks.router)
api_router.include_router(workflows.router)
api_router.include_router(workflow_sse.router)
