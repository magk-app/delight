"""
Web Dashboard for Experimental Agent Memory System

A FastAPI-based web interface for visualizing and managing:
- Memory storage and retrieval
- Token usage analytics
- Model configuration
- Search performance benchmarks
- Knowledge graph visualization
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from uuid import UUID
import json
import sys

# Add parent directory to path to import from experiments
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from experimental agent (adjust imports based on your structure)
try:
    from agent_config import AgentConfig
    from storage import JSONMemoryStorage
    from schemas import Memory, TokenUsage, SearchBenchmark, MemoryStats
except ImportError:
    print("Warning: Could not import experimental agent modules. Using mock data.")
    AgentConfig = None
    JSONMemoryStorage = None


# ============================================================================
# Configuration
# ============================================================================

class WebConfig:
    """Configuration for web dashboard"""
    web_host: str = "0.0.0.0"
    web_port: int = 8001
    templates_dir: Path = Path(__file__).parent / "templates"
    static_dir: Path = Path(__file__).parent / "static"
    data_dir: Path = Path(__file__).parent / "data"
    use_json_storage: bool = True


config = WebConfig()

# ============================================================================
# Mock Classes (for when experimental agent modules aren't available)
# ============================================================================

class MockMemory:
    """Mock memory object"""
    def __init__(self, id, content, memory_type, user_id, metadata=None):
        self.id = id
        self.content = content
        self.memory_type = memory_type
        self.user_id = user_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.embedding = None

    def to_dict(self):
        return {
            "id": str(self.id),
            "content": self.content,
            "memory_type": self.memory_type,
            "user_id": str(self.user_id),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class MockStorage:
    """Mock storage for demo purposes"""
    def __init__(self):
        self.memories = []

    async def get_all_memories(self):
        return self.memories

    async def get_memory(self, memory_id: UUID):
        for m in self.memories:
            if m.id == memory_id:
                return m
        return None

    async def delete_memory(self, memory_id: UUID):
        self.memories = [m for m in self.memories if m.id != memory_id]


class MockAnalytics:
    """Mock analytics tracker"""
    def __init__(self):
        self.token_usage_history = []
        self.search_benchmarks = []

    def record_token_usage(self, usage):
        self.token_usage_history.append(usage)

    def get_token_usage_summary(self, hours=24):
        return {
            "total_tokens": 15000,
            "total_cost": 0.023,
            "by_model": {
                "gpt-4o-mini": {"tokens": 10000, "cost": 0.015},
                "gpt-4o": {"tokens": 5000, "cost": 0.008}
            }
        }


# ============================================================================
# Pydantic Models
# ============================================================================

class SystemConfig(BaseModel):
    """System configuration schema"""
    class ModelsConfig(BaseModel):
        chat_model: str = "gpt-4o-mini"
        reasoning_model: str = "o1-preview"
        expensive_model: str = "gpt-4o"
        embedding_model: str = "text-embedding-3-small"

    class SearchConfig(BaseModel):
        similarity_threshold: float = 0.7
        default_search_limit: int = 10
        hybrid_search_weight_vector: float = 0.7
        graph_traversal_max_depth: int = 3

    class FactExtractionConfig(BaseModel):
        max_facts_per_message: int = 20
        auto_categorize: bool = True
        max_categories_per_fact: int = 3
        min_fact_length: int = 10

    models: ModelsConfig = ModelsConfig()
    search: SearchConfig = SearchConfig()
    fact_extraction: FactExtractionConfig = FactExtractionConfig()


class TokenUsage(BaseModel):
    """Token usage record"""
    model: str
    tokens_input: int
    tokens_output: int
    cost: float
    timestamp: datetime = None


class MemoryStats(BaseModel):
    """Memory statistics"""
    total_memories: int
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    total_embeddings: int
    avg_embedding_time_ms: float
    storage_size_bytes: int


class SearchBenchmark(BaseModel):
    """Search performance benchmark"""
    query: str
    strategy: str
    duration_ms: float
    results_count: int
    timestamp: datetime = None


# ============================================================================
# Initialize FastAPI App
# ============================================================================

app = FastAPI(
    title="Experimental Agent Dashboard",
    description="Web interface for agent memory and analytics",
    version="0.1.0"
)

# ============================================================================
# CORS Configuration
# ============================================================================

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.static_dir)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(config.templates_dir))

# Initialize storage and analytics (use mock if real modules unavailable)
try:
    if AgentConfig and JSONMemoryStorage:
        agent_config = AgentConfig()
        storage = JSONMemoryStorage(config.data_dir / "memories.json")
        from analytics import AnalyticsTracker
        analytics = AnalyticsTracker()
    else:
        raise ImportError("Using mock storage")
except:
    print("Using mock storage and analytics")
    storage = MockStorage()
    analytics = MockAnalytics()


# ============================================================================
# Page Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard"
    })


@app.get("/memories", response_class=HTMLResponse)
async def memories_page(request: Request):
    """Memory browser page"""
    return templates.TemplateResponse("memories.html", {
        "request": request,
        "title": "Memories"
    })


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Configuration page"""
    return templates.TemplateResponse("config.html", {
        "request": request,
        "title": "Configuration"
    })


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics page"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "title": "Analytics"
    })


@app.get("/playground", response_class=HTMLResponse)
async def playground_page(request: Request):
    """Interactive playground page"""
    return templates.TemplateResponse("playground.html", {
        "request": request,
        "title": "Playground"
    })


# ============================================================================
# API Routes - Config
# ============================================================================

@app.get("/api/config")
async def get_config() -> SystemConfig:
    """Get current system configuration"""
    # Try to load saved config
    config_file = Path(__file__).parent / "data" / "system_config.json"

    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
            return SystemConfig(**saved_config)
        except Exception as e:
            print(f"⚠️  Failed to load saved config: {e}")
            # Fall through to default config

    # Return default config
    return SystemConfig(
        models=SystemConfig.ModelsConfig(
            chat_model="gpt-4o-mini",
            reasoning_model="o1-preview",
            expensive_model="gpt-4o",
            embedding_model="text-embedding-3-small"
        ),
        search=SystemConfig.SearchConfig(
            similarity_threshold=0.7,
            default_search_limit=10,
            hybrid_search_weight_vector=0.7,
            graph_traversal_max_depth=3
        ),
        fact_extraction=SystemConfig.FactExtractionConfig(
            max_facts_per_message=20,
            auto_categorize=True,
            max_categories_per_fact=3,
            min_fact_length=10
        )
    )


@app.post("/api/config")
async def update_config_api(new_config: SystemConfig) -> dict:
    """Update system configuration"""
    try:
        # Save config to JSON file for persistence
        config_file = Path(__file__).parent / "data" / "system_config.json"
        config_file.parent.mkdir(exist_ok=True)

        with open(config_file, 'w') as f:
            import json
            f.write(json.dumps(new_config.model_dump(), indent=2))

        print(f"✅ Config saved to {config_file}")
        return {"status": "success", "message": "Configuration saved successfully"}
    except Exception as e:
        print(f"❌ Failed to save config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")


@app.get("/api/models/available")
async def get_available_models() -> Dict[str, List[str]]:
    """Get list of available models"""
    return {
        "chat": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "reasoning": ["o1-preview", "o1-mini", "gpt-4o", "gpt-4-turbo"],
        "embedding": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
    }


# ============================================================================
# API Routes - Analytics
# ============================================================================

@app.get("/api/analytics/stats")
async def get_memory_stats(user_id: Optional[str] = None) -> MemoryStats:
    """Get memory statistics"""
    memories = await storage.get_all_memories()

    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]

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
        avg_embedding_time_ms=0.0,
        storage_size_bytes=0
    )


@app.get("/api/analytics/token-usage")
async def get_token_usage(hours: int = 24, user_id: Optional[str] = None) -> dict:
    """Get token usage summary from database"""
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.token_usage import TokenUsage
        from sqlalchemy import select, func
        from datetime import timedelta
        from collections import defaultdict
        from uuid import UUID

        async with AsyncSessionLocal() as db:
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours)

            # Build query
            query = select(TokenUsage).where(TokenUsage.created_at >= time_threshold)
            if user_id:
                query = query.where(TokenUsage.user_id == UUID(user_id))

            result = await db.execute(query)
            usage_records = result.scalars().all()

            # Aggregate data
            total_tokens = 0
            total_cost = 0.0
            by_model = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})

            for record in usage_records:
                total_tokens += record.total_tokens
                total_cost += record.total_cost

                by_model[record.model]["tokens"] += record.total_tokens
                by_model[record.model]["cost"] += record.total_cost
                by_model[record.model]["calls"] += 1

            return {
                "total_tokens": total_tokens,
                "total_cost": round(total_cost, 4),
                "by_model": {
                    model: {
                        "tokens": data["tokens"],
                        "cost": round(data["cost"], 4),
                        "calls": data["calls"]
                    }
                    for model, data in by_model.items()
                },
                "records_count": len(usage_records),
                "time_range_hours": hours
            }

    except Exception as e:
        print(f"Error fetching token usage: {e}")
        # Fallback to mock data if database fails
        return analytics.get_token_usage_summary(hours)


@app.get("/api/analytics/search-performance")
async def get_search_performance(limit: int = 100) -> List[dict]:
    """Get recent search benchmarks"""
    benchmarks = analytics.search_benchmarks[-limit:]
    return [
        {
            "query": b.query if hasattr(b, 'query') else "test",
            "strategy": b.strategy if hasattr(b, 'strategy') else "semantic",
            "duration_ms": b.duration_ms if hasattr(b, 'duration_ms') else 0,
            "results_count": b.results_count if hasattr(b, 'results_count') else 0,
            "timestamp": b.timestamp.isoformat() if hasattr(b, 'timestamp') and b.timestamp else datetime.now().isoformat()
        }
        for b in benchmarks
    ]


@app.post("/api/analytics/token-usage")
async def record_token_usage_api(usage: TokenUsage):
    """Record token usage"""
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
    """Get memories with optional filters"""
    memories = await storage.get_all_memories()

    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]
    if memory_type:
        memories = [m for m in memories if m.memory_type == memory_type]
    if category:
        memories = [m for m in memories if category in m.metadata.get("categories", [])]

    memories = memories[:limit]
    return [m.to_dict() for m in memories]


@app.get("/api/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get single memory by ID"""
    try:
        memory = await storage.get_memory(UUID(memory_id))
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory.to_dict()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID")


@app.delete("/api/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory"""
    try:
        await storage.delete_memory(UUID(memory_id))
        return {"status": "success", "message": "Memory deleted"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory ID")


@app.get("/api/memories/categories/hierarchy")
async def get_category_hierarchy(user_id: Optional[str] = None):
    """Get hierarchical category structure"""
    memories = await storage.get_all_memories()

    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]

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
    """Get memory graph data for visualization"""
    memories = await storage.get_all_memories()

    if user_id:
        memories = [m for m in memories if str(m.user_id) == user_id]

    memories = memories[:limit]

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
    """Manage WebSocket connections"""
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
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "storage": "json" if config.use_json_storage else "postgresql",
        "version": "0.1.0"
    }


# ============================================================================
# Include Chat API Router
# ============================================================================

try:
    from chat_api import router as chat_router
    app.include_router(chat_router)
    print("✅ Chat API enabled")
except Exception as e:
    print(f"⚠️  Chat API not available: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# Include Conversation API Router
# ============================================================================

try:
    from conversation_api import router as conversation_router
    app.include_router(conversation_router)
    print("✅ Conversation API enabled")
except Exception as e:
    print(f"⚠️  Conversation API not available: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# Include Memory API Router
# ============================================================================

try:
    from memory_api import router as memory_router
    app.include_router(memory_router)
    print("✅ Memory API enabled")
except Exception as e:
    print(f"⚠️  Memory API not available: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# Include Setup API Router
# ============================================================================

try:
    from setup_api import router as setup_router
    app.include_router(setup_router)
    print("✅ Setup API enabled")
except Exception as e:
    print(f"⚠️  Setup API not available: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# User Auto-Creation Endpoint
# ============================================================================

try:
    from app.db.session import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select

    @app.post("/api/users/ensure")
    async def ensure_user(request: dict):
        """
        Ensure user exists in database, create if not.
        For experimental frontend that generates test user IDs.
        """
        user_id_str = request.get("user_id")
        if not user_id_str:
            raise HTTPException(status_code=400, detail="user_id is required")

        user_id = UUID(user_id_str)

        async with AsyncSessionLocal() as db:
            # Check if user exists
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                return {
                    "status": "exists",
                    "user_id": str(existing_user.id),
                    "message": "User already exists"
                }

            # Create new user
            new_user = User(
                id=user_id,
                clerk_user_id=f"experimental_{user_id}",  # Mock clerk ID for experimental users
                email=None,
                display_name=f"Test User {user_id_str[:8]}"
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            return {
                "status": "created",
                "user_id": str(new_user.id),
                "message": "User created successfully"
            }

    print("✅ User auto-creation API enabled")

except Exception as e:
    print(f"⚠️  User auto-creation API not available: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
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
