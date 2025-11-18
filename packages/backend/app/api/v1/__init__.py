"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1 import health, users, webhooks, memories, agent_preferences, knowledge_graph

api_router = APIRouter()

# Register all v1 routers
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(webhooks.router)
api_router.include_router(memories.router)
api_router.include_router(agent_preferences.router)
api_router.include_router(knowledge_graph.router)
