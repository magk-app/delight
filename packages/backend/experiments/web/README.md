# 🧪 Experimental Agent Web Dashboard

A comprehensive web-based visualization and management interface for the experimental AI agent memory system.

## 📋 Overview

This dashboard provides a modern, interactive web interface to:
- **Visualize memory statistics** and distribution
- **Track token usage** and costs across different models
- **Configure models** and search parameters
- **Browse and manage memories** with an interactive knowledge graph
- **Test search strategies** in an interactive playground
- **Monitor performance** with real-time analytics

## 🎯 Features

### 1. **Dashboard** (`/`)
- Real-time statistics (total memories, token costs, embeddings)
- Memory distribution charts (by type and category)
- Token usage over time visualization
- Model usage breakdown and costs
- Recent activity feed
- Knowledge graph preview
- Quick actions (search, export, refresh)

### 2. **Memories** (`/memories`)
- Browse all memories with filtering (type, category, search)
- Interactive knowledge graph visualization using D3.js
- Switch between list and graph views
- Click to view detailed memory information
- Delete memories
- Graph controls (zoom, physics simulation, labels)

### 3. **Configuration** (`/config`)
- **Model Configuration**:
  - Chat Model (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
  - Reasoning Model (o1-preview, o1-mini, gpt-4o)
  - High-Quality Model (gpt-4o, gpt-4-turbo)
  - Embedding Model (text-embedding-3-small, text-embedding-3-large)
- **Search Parameters**:
  - Similarity threshold slider
  - Default search limits
  - Hybrid search weights (vector vs keyword)
  - Graph traversal depth
- **Fact Extraction**:
  - Max facts per message
  - Minimum fact length
  - Auto-categorization toggle
  - Max categories per fact

### 4. **Analytics** (`/analytics`)
- Detailed token usage analytics
- Cost breakdown by model
- Token usage over time charts
- Search performance benchmarks
- Recent usage table with timestamps

### 5. **Playground** (`/playground`)
- **Search Testing**: Test different search strategies interactively
- **Memory Creation**: Create test memories with custom content and categories
- **Fact Extraction**: Extract facts from text samples
- **Performance Benchmarking**: Run multiple queries and measure performance
- **Live Console**: Real-time logging of all operations
- **WebSocket Status**: Monitor real-time connection status

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Template Engine**: Jinja2
- **Real-time**: WebSockets for live updates
- **API**: RESTful endpoints + Server-Sent Events

### Frontend
- **Styling**: Custom CSS with glassmorphism dark theme
- **Charts**: Chart.js for statistics and analytics
- **Graph Visualization**: D3.js for interactive knowledge graphs
- **Real-time**: WebSocket client for live updates

### File Structure
```
experiments/web/
├── dashboard_server.py         # Main FastAPI application
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template with navigation
│   ├── dashboard.html         # Main dashboard page
│   ├── memories.html          # Memory browser with graph
│   ├── config.html            # Configuration panel
│   ├── analytics.html         # Analytics dashboard
│   └── playground.html        # Interactive playground
├── static/
│   ├── css/
│   │   └── main.css          # Main stylesheet (14KB)
│   └── js/
│       ├── common.js         # Shared utilities and API helpers
│       ├── dashboard.js      # Dashboard page logic
│       ├── memories.js       # Memory browser and graph
│       ├── config.js         # Configuration management
│       ├── analytics.js      # Analytics charts
│       └── playground.js     # Playground functionality
└── data/
    └── memories.json         # JSON storage (when using file backend)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Poetry (for dependency management)
- FastAPI, Uvicorn, Jinja2 (installed via Poetry)

### Installation

1. **Navigate to the backend directory**:
   ```bash
   cd packages/backend
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   poetry install
   ```

3. **Start the dashboard server**:
   ```bash
   poetry run python experiments/web/dashboard_server.py
   ```

4. **Open your browser**:
   ```
   http://localhost:8001
   ```

### Alternative: Using Uvicorn directly
```bash
cd packages/backend
poetry run uvicorn experiments.web.dashboard_server:app --reload --port 8001
```

## 📖 Usage Guide

### Dashboard Navigation
The navigation bar provides quick access to all sections:
- 📊 **Dashboard** - Overview and statistics
- 🧠 **Memories** - Browse and visualize memories
- ⚙️ **Config** - Configure models and parameters
- 📈 **Analytics** - Detailed analytics and metrics
- 🎮 **Playground** - Interactive testing ground

### Configuration
1. Navigate to **Config** page
2. Select models from dropdown menus
3. Adjust search parameters with sliders
4. Configure fact extraction settings
5. Click **Save Changes** to apply

### Memory Management
1. Navigate to **Memories** page
2. Use filters to narrow down memories:
   - Filter by type (fact, preference, context, episodic)
   - Filter by category
   - Search by content
3. Switch between **List View** and **Graph View**
4. Click on memories to view details
5. Delete unwanted memories

### Search Testing
1. Navigate to **Playground** page
2. Enter a search query
3. Select search strategy:
   - **Auto**: Intelligent strategy selection
   - **Semantic**: Vector-based similarity search
   - **Keyword**: BM25 keyword matching
   - **Categorical**: Category-based filtering
   - **Temporal**: Time-based search
   - **Hybrid**: Combination of vector and keyword
4. Click **Search** to execute

### Creating Test Memories
1. Go to **Playground** → **Create Test Memory**
2. Enter memory content
3. Select memory type
4. Add categories (comma-separated)
5. Click **Create Memory**

## 🎨 Design Features

### Visual Design
- **Dark Theme**: Modern glassmorphism design with dark backgrounds
- **Color Palette**:
  - Primary: Indigo (#4f46e5)
  - Secondary: Cyan (#06b6d4)
  - Success: Green (#10b981)
  - Warning: Amber (#f59e0b)
  - Danger: Red (#ef4444)
- **Typography**: Inter for UI, JetBrains Mono for code
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-friendly grid layouts

### Interactive Elements
- Hover effects on cards and buttons
- Smooth transitions
- Loading states
- Toast notifications
- Modal dialogs
- Drag-and-drop graph nodes
- Real-time updates

## 🔧 API Endpoints

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `GET /api/models/available` - List available models

### Analytics
- `GET /api/analytics/stats` - Memory statistics
- `GET /api/analytics/token-usage?hours=24` - Token usage summary
- `GET /api/analytics/search-performance?limit=100` - Search benchmarks
- `POST /api/analytics/token-usage` - Record token usage

### Memories
- `GET /api/memories` - List memories (with filters)
- `GET /api/memories/{id}` - Get single memory
- `DELETE /api/memories/{id}` - Delete memory
- `GET /api/memories/categories/hierarchy` - Category structure

### Graph
- `GET /api/graph/memories` - Get graph visualization data

### WebSocket
- `WS /ws/updates` - Real-time updates connection

### Health
- `GET /health` - Health check endpoint

## 🎯 Use Cases

### 1. Development & Debugging
- Monitor memory creation in real-time
- Test different search strategies
- Verify fact extraction accuracy
- Track token costs during development

### 2. Performance Optimization
- Benchmark search strategies
- Analyze token usage patterns
- Identify expensive operations
- Monitor embedding generation

### 3. Model Configuration
- Experiment with different models
- Optimize cost vs quality trade-offs
- Adjust search parameters
- Fine-tune fact extraction

### 4. Knowledge Management
- Browse and organize memories
- Visualize knowledge connections
- Clean up outdated memories
- Analyze category distributions

## 📊 Chart Types

The dashboard uses several visualization types:

1. **Doughnut Charts**: Memory distribution, model cost comparison
2. **Bar Charts**: Category breakdown, search performance
3. **Line Charts**: Token usage over time, cost trends
4. **Force-Directed Graph**: Knowledge graph visualization
5. **Tables**: Recent usage, model statistics

## 🌐 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

Requires JavaScript enabled and modern CSS support (CSS Grid, Flexbox, Custom Properties).

## 🔒 Security Notes

- This is an **experimental** dashboard for development use
- **Do not expose to the internet** without authentication
- No built-in authentication or authorization
- Intended for **local development** only
- Add authentication layer for production use

## 🚨 Troubleshooting

### Server won't start
```bash
# Check if port 8001 is in use
lsof -i :8001

# Try a different port
python dashboard_server.py --port 8002
```

### Import errors
```bash
# Reinstall dependencies
cd packages/backend
poetry install
```

### WebSocket connection fails
- Check if server is running
- Verify port is accessible
- Check browser console for errors

### Charts not rendering
- Ensure Chart.js CDN is accessible
- Check browser console for JavaScript errors
- Verify internet connection for CDN resources

## 📈 Performance

- **Initial Load**: ~1-2s (includes CDN resources)
- **Dashboard Refresh**: ~200-500ms
- **Graph Rendering**: 100-1000 nodes in <2s
- **Search**: Depends on backend implementation
- **Memory**: ~50-100MB browser memory for typical usage

## 🎓 Technical Details

### State Management
- No external state management library
- Uses vanilla JavaScript with modern ES6+ features
- Event-driven architecture
- WebSocket for real-time state sync

### Data Flow
```
User Action → JavaScript Handler → API Request → FastAPI Backend
     ↓                                                    ↓
  Update UI ← API Response ← JSON Serialization ← Python Logic
```

### Async Operations
- All API calls use `async/await`
- Parallel data fetching where possible
- Error handling with try/catch
- Loading states for better UX

## 🔄 Future Enhancements

Potential improvements:
- [ ] User authentication and sessions
- [ ] Export data to CSV/JSON
- [ ] Advanced filtering and search
- [ ] Memory comparison tool
- [ ] Cost prediction and budgeting
- [ ] Multi-user support
- [ ] API rate limiting
- [ ] Caching layer
- [ ] Database backend (PostgreSQL)
- [ ] Backup and restore functionality

## 📝 License

Part of the Delight project. See main repository for license details.

## 🤝 Contributing

This is an experimental feature. Contributions welcome!

---

**Built with**: FastAPI • Jinja2 • Chart.js • D3.js • Modern CSS

**Version**: 0.1.0

**Last Updated**: November 2025
