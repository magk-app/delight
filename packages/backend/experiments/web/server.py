"""Experimental Agent Web Interface.

A comprehensive dashboard for visualizing memories, tracking costs,
configuring models, and testing search strategies.

Features:
- Real-time memory analytics
- Token cost tracking and projections
- Interactive memory graph visualization
- Model configuration playground
- Search strategy comparison
- Category-based memory browsing

Run:
    poetry run python experiments/web/server.py

Then open: http://localhost:5000
"""

import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from experiments.config import get_config, ExperimentConfig
from experiments.database.json_storage import JSONStorage


# ============================================================================
# Configuration
# ============================================================================

config = get_config()
app = FastAPI(
    title="Experimental Agent Dashboard",
    description="Visual interface for memory management and model experimentation",
    version="0.1.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory=str(config.templates_dir))
static_dir = config.static_dir

# Mount static files if directories exist
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Storage backend (JSON for now, can be swapped with PostgreSQL)
storage = JSONStorage()


# ============================================================================
# Data Models
# ============================================================================

class ModelConfig(BaseModel):
    """Model configuration settings."""
    chat_model: str = Field(default="gpt-4o-mini", description="Default chat model")
    reasoning_model: str = Field(default="o1-preview", description="Complex reasoning model")
    expensive_model: str = Field(default="gpt-4o", description="High-quality output model")
    embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")


class SearchConfig(BaseModel):
    """Search configuration settings."""
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    default_search_limit: int = Field(default=10, ge=1, le=100)
    hybrid_search_weight_vector: float = Field(default=0.7, ge=0.0, le=1.0)
    graph_traversal_max_depth: int = Field(default=3, ge=1, le=10)


class FactExtractionConfig(BaseModel):
    """Fact extraction configuration."""
    max_facts_per_message: int = Field(default=20, ge=1, le=50)
    auto_categorize: bool = Field(default=True)
    max_categories_per_fact: int = Field(default=3, ge=1, le=5)
    min_fact_length: int = Field(default=10, ge=5, le=100)


class SystemConfig(BaseModel):
    """Complete system configuration."""
    models: ModelConfig = Field(default_factory=ModelConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    fact_extraction: FactExtractionConfig = Field(default_factory=FactExtractionConfig)


class TokenUsage(BaseModel):
    """Token usage statistics."""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class MemoryStats(BaseModel):
    """Memory statistics."""
    total_memories: int
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    total_embeddings: int
    avg_embedding_time_ms: float
    storage_size_bytes: int


class SearchBenchmark(BaseModel):
    """Search performance benchmark."""
    strategy: str
    query: str
    num_results: int
    latency_ms: float
    avg_score: float
    timestamp: datetime


# ============================================================================
# Analytics Storage (In-Memory for now)
# ============================================================================

class Analytics:
    """In-memory analytics storage."""

    def __init__(self):
        self.token_usage: List[TokenUsage] = []
        self.search_benchmarks: List[SearchBenchmark] = []
        self._load_from_file()

    def _load_from_file(self):
        """Load analytics from JSON file."""
        analytics_file = config.experiments_root / "data" / "analytics.json"
        if analytics_file.exists():
            try:
                with open(analytics_file, "r") as f:
                    data = json.load(f)
                    self.token_usage = [TokenUsage(**item) for item in data.get("token_usage", [])]
                    self.search_benchmarks = [SearchBenchmark(**item) for item in data.get("search_benchmarks", [])]
            except Exception as e:
                print(f"⚠️  Failed to load analytics: {e}")

    def _save_to_file(self):
        """Save analytics to JSON file."""
        analytics_file = config.experiments_root / "data" / "analytics.json"
        analytics_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(analytics_file, "w") as f:
                json.dump({
                    "token_usage": [item.dict() for item in self.token_usage],
                    "search_benchmarks": [item.dict() for item in self.search_benchmarks]
                }, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Failed to save analytics: {e}")

    def record_token_usage(self, usage: TokenUsage):
        """Record token usage."""
        self.token_usage.append(usage)
        self._save_to_file()

    def record_search_benchmark(self, benchmark: SearchBenchmark):
        """Record search benchmark."""
        self.search_benchmarks.append(benchmark)
        self._save_to_file()

    def get_token_usage_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get token usage summary for last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [u for u in self.token_usage if u.timestamp > cutoff]

        total_cost = sum(u.estimated_cost_usd for u in recent)
        by_model = defaultdict(lambda: {"tokens": 0, "cost": 0})

        for usage in recent:
            by_model[usage.model]["tokens"] += usage.total_tokens
            by_model[usage.model]["cost"] += usage.estimated_cost_usd

        return {
            "total_tokens": sum(u.total_tokens for u in recent),
            "total_cost_usd": total_cost,
            "by_model": dict(by_model),
            "num_requests": len(recent)
        }


analytics = Analytics()


# ============================================================================
# Routes - Dashboard
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Experiment Dashboard"
    })


@app.get("/memories", response_class=HTMLResponse)
async def memory_browser(request: Request):
    """Memory browser page."""
    return templates.TemplateResponse("memories.html", {
        "request": request,
        "title": "Memory Browser"
    })


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Configuration page."""
    return templates.TemplateResponse("config.html", {
        "request": request,
        "title": "Configuration"
    })


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics page."""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "title": "Analytics"
    })


@app.get("/playground", response_class=HTMLResponse)
async def playground_page(request: Request):
    """Experiments playground page."""
    return templates.TemplateResponse("playground.html", {
        "request": request,
        "title": "Playground"
    })


# ============================================================================
# API Routes - Configuration
# ============================================================================

@app.get("/api/config")
async def get_config_api() -> SystemConfig:
    """Get current system configuration."""
    return SystemConfig(
        models=ModelConfig(
            chat_model=config.chat_model,
            reasoning_model=config.reasoning_model,
            expensive_model=config.expensive_model,
            embedding_model=config.embedding_model
        ),
        search=SearchConfig(
            similarity_threshold=config.similarity_threshold,
            default_search_limit=config.default_search_limit,
            hybrid_search_weight_vector=config.hybrid_search_weight_vector,
            graph_traversal_max_depth=config.graph_traversal_max_depth
        ),
        fact_extraction=FactExtractionConfig(
            max_facts_per_message=config.max_facts_per_message,
            auto_categorize=config.auto_categorize,
            max_categories_per_fact=config.max_categories_per_fact,
            min_fact_length=config.min_fact_length
        )
    )


@app.post("/api/config")
async def update_config_api(new_config: SystemConfig) -> dict:
    """Update system configuration."""
    # Update config object
    config.chat_model = new_config.models.chat_model
    config.reasoning_model = new_config.models.reasoning_model
    config.expensive_model = new_config.models.expensive_model
    config.embedding_model = new_config.models.embedding_model

    config.similarity_threshold = new_config.search.similarity_threshold
    config.default_search_limit = new_config.search.default_search_limit
    config.hybrid_search_weight_vector = new_config.search.hybrid_search_weight_vector
    config.graph_traversal_max_depth = new_config.search.graph_traversal_max_depth

    config.max_facts_per_message = new_config.fact_extraction.max_facts_per_message
    config.auto_categorize = new_config.fact_extraction.auto_categorize
    config.max_categories_per_fact = new_config.fact_extraction.max_categories_per_fact
    config.min_fact_length = new_config.fact_extraction.min_fact_length

    return {"status": "success", "message": "Configuration updated"}


@app.get("/api/models/available")
async def get_available_models() -> Dict[str, List[str]]:
    """Get list of available models."""
    return {
        "chat": list(config.MODELS.values()) + ["gpt-3.5-turbo"],
        "reasoning": ["o1-preview", "o1-mini", "gpt-4o", "gpt-4-turbo"],
        "embedding": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
    }


# ============================================================================
# API Routes - Analytics
# ============================================================================

@app.get("/api/analytics/stats")
async def get_memory_stats(user_id: Optional[str] = None) -> MemoryStats:
    """Get memory statistics."""
    # Get all memories
    memories = await storage.get_all_memories()

    # Filter by user if specified
    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]

    # Calculate stats
    by_type = defaultdict(int)
    by_category = defaultdict(int)
    total_embeddings = 0

    for memory in memories:
        by_type[memory.memory_type] += 1
        if memory.embedding:
            total_embeddings += 1
        for category in memory.metadata.get("categories", []):
            by_category[category] += 1

    return MemoryStats(
        total_memories=len(memories),
        by_type=dict(by_type),
        by_category=dict(by_category),
        total_embeddings=total_embeddings,
        avg_embedding_time_ms=0.0,  # TODO: Calculate from analytics
        storage_size_bytes=0  # TODO: Calculate file size
    )


@app.get("/api/analytics/token-usage")
async def get_token_usage(hours: int = 24) -> dict:
    """Get token usage summary."""
    return analytics.get_token_usage_summary(hours)


@app.get("/api/analytics/search-performance")
async def get_search_performance(limit: int = 100) -> List[SearchBenchmark]:
    """Get recent search benchmarks."""
    return analytics.search_benchmarks[-limit:]


@app.post("/api/analytics/token-usage")
async def record_token_usage_api(usage: TokenUsage):
    """Record token usage."""
    analytics.record_token_usage(usage)
    return {"status": "success"}


# ============================================================================
# API Routes - Memories
# ============================================================================

@app.get("/api/memories")
async def get_memories(
    user_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Get memories with optional filters."""
    memories = await storage.get_all_memories()

    # Apply filters
    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]
    if memory_type:
        memories = [m for m in memories if m.memory_type == memory_type]
    if category:
        memories = [m for m in memories if category in m.metadata.get("categories", [])]

    # Limit results
    memories = memories[:limit]

    # Convert to dict
    return [m.to_dict() for m in memories]


@app.get("/api/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get single memory by ID."""
    try:
        memory = await storage.get_memory(UUID(memory_id))
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory.to_dict()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID")


@app.delete("/api/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory."""
    try:
        await storage.delete_memory(UUID(memory_id))
        return {"status": "success", "message": "Memory deleted"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID")


@app.get("/api/memories/categories/hierarchy")
async def get_category_hierarchy(user_id: Optional[str] = None):
    """Get hierarchical category structure."""
    memories = await storage.get_all_memories()

    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]

    # Build hierarchy
    hierarchy = defaultdict(lambda: defaultdict(int))
    for memory in memories:
        categories = memory.metadata.get("categories", [])
        memory_type = memory.memory_type
        for category in categories:
            hierarchy[memory_type][category] += 1

    return dict(hierarchy)


# ============================================================================
# API Routes - Graph Data
# ============================================================================

@app.get("/api/graph/memories")
async def get_memory_graph(user_id: Optional[str] = None, limit: int = 100):
    """Get memory graph data for visualization."""
    memories = await storage.get_all_memories()

    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]

    memories = memories[:limit]

    # Build graph structure
    nodes = []
    edges = []

    for memory in memories:
        nodes.append({
            "id": str(memory.id),
            "label": memory.content[:50] + "..." if len(memory.content) > 50 else memory.content,
            "type": memory.memory_type,
            "categories": memory.metadata.get("categories", []),
            "created_at": memory.created_at.isoformat()
        })

        # Create edges based on relationships in metadata
        relationships = memory.metadata.get("relationships", {})
        for rel_type, target_ids in relationships.items():
            for target_id in target_ids:
                edges.append({
                    "source": str(memory.id),
                    "target": str(target_id),
                    "type": rel_type
                })

    return {
        "nodes": nodes,
        "edges": edges
    }


# ============================================================================
# WebSocket - Live Updates
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "storage": "json" if config.use_json_storage else "postgresql",
        "version": "0.1.0"
    }


# ============================================================================
# Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("=" * 80)
    print("🧪 Experimental Agent Dashboard")
    print("=" * 80)
    print(f"📊 Dashboard: http://{config.web_host}:{config.web_port}")
    print(f"📚 API Docs: http://{config.web_host}:{config.web_port}/docs")
    print(f"💾 Storage: {'JSON' if config.use_json_storage else 'PostgreSQL'}")
    print(f"🎨 Templates: {config.templates_dir}")
    print(f"📁 Static: {config.static_dir}")
    print("=" * 80)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Experimental Agent Dashboard...")
    print(f"   Visit: http://{config.web_host}:{config.web_port}")

    uvicorn.run(
        app,
        host=config.web_host,
        port=config.web_port,
        log_level="info"
    )
