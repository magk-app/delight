"""
Delight Backend API
FastAPI application with health check endpoint and Swagger UI documentation.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown.

    Startup: Test database connection (optional - allows app to start without DB)
    Shutdown: Clean up database connections
    """
    # Startup: Test database connection (optional)
    try:
        async with engine.begin() as conn:
            # Connection test - if this succeeds, database is accessible
            pass
        print("✅ Database connection established")
    except Exception as e:
        print(f"⚠️  Database connection failed (app will continue): {e}")

    yield

    # Shutdown: Clean up database connections
    try:
        await engine.dispose()
        print("✅ Database connections closed")
    except Exception as e:
        # Ignore cancellation errors during shutdown - they're expected when interrupting the server
        if isinstance(e, (asyncio.CancelledError, KeyboardInterrupt)):
            print("🛑 Server shutdown interrupted")
        else:
            print(f"⚠️  Error closing database connections: {e}")


app = FastAPI(
    title="Delight API",
    version="0.1.0",
    description="AI-powered self-improvement companion API with emotionally intelligent coaching, "
    "structured progress systems, and narrative world-building.",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc alternative documentation
    openapi_url="/openapi.json",  # OpenAPI JSON schema
    lifespan=lifespan,  # Add lifespan handler
)

# CORS configuration for frontend communication
# Parse CORS_ORIGINS from environment (comma-separated list)
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

# Add default localhost origins if not in production
if settings.ENVIRONMENT == "development":
    cors_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

print(f"🌐 CORS enabled for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Dynamic origins from environment
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Register API v1 router (includes health, users, webhooks)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns basic API metadata and links to documentation.
    """
    return {
        "name": "Delight API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
    }
