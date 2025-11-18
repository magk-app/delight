# 🎯 How to Use the Experimental Agent Web Dashboard

## Quick Start (3 Steps)

### 1. Navigate to the Dashboard Directory
```bash
cd packages/backend/experiments/web
```

### 2. Start the Server
```bash
./start_dashboard.sh
```

**OR** manually:
```bash
cd packages/backend
poetry run python experiments/web/dashboard_server.py
```

### 3. Open in Browser
Visit: **http://localhost:8001**

That's it! 🎉

---

## 📂 What Has Been Built

### Complete Web Dashboard with 5 Pages:

#### 1. **Dashboard** (`/`)
Main overview page showing:
- Total memories count
- Token usage and costs (24 hours)
- Memory type distribution (pie chart)
- Top categories (bar chart)
- Token usage over time (line graph)
- Model usage breakdown
- Recent activity feed
- Knowledge graph preview
- Quick action buttons

#### 2. **Memories Browser** (`/memories`)
Browse and manage your memory store:
- **List View**: Scrollable list of all memories
- **Graph View**: Interactive D3.js force-directed graph
- **Filters**: Type, category, search text, limit
- **Memory Details**: Click any memory to see full details
- **Delete**: Remove unwanted memories
- **Graph Controls**: Reset zoom, pause physics, toggle labels

#### 3. **Configuration Panel** (`/config`)
Configure your agent system:
- **Models Tab**:
  - Chat Model (GPT-4o-mini, GPT-4o, GPT-3.5-turbo, etc.)
  - Reasoning Model (O1-preview, O1-mini, GPT-4o)
  - High-Quality Model (GPT-4o, GPT-4-turbo)
  - Embedding Model (text-embedding-3-small/large)
- **Search Tab**:
  - Similarity threshold slider (0.0 - 1.0)
  - Default search limit
  - Hybrid search weights (vector vs keyword)
- **Fact Extraction Tab**:
  - Max facts per message
  - Min fact length
  - Auto-categorization toggle
  - Max categories per fact
- **Advanced Tab**:
  - Storage backend info
  - Performance settings

#### 4. **Analytics** (`/analytics`)
Deep dive into metrics:
- Token usage by model (bar chart)
- Cost over time (line chart)
- Search performance benchmarks
- Model cost comparison (pie chart)
- Recent usage table with timestamps
- Average cost per request
- Total requests counter

#### 5. **Interactive Playground** (`/playground`)
Test and experiment:
- **Search Testing**: Try different search strategies (semantic, keyword, hybrid, etc.)
- **Memory Creation**: Create test memories with custom content and categories
- **Fact Extraction**: Extract facts from sample text
- **Performance Benchmarking**: Run multiple queries and measure speed
- **Live Console**: Real-time logging of all operations
- **WebSocket Monitor**: Check real-time connection status

---

## 🎨 Design & Features

### Visual Design
- **Modern Dark Theme**: Sleek glassmorphism design
- **Smooth Animations**: Hover effects, transitions, and loading states
- **Responsive**: Works on desktop, tablet, and mobile
- **Accessibility**: High contrast, readable fonts, clear icons

### Technical Stack
- **Backend**: FastAPI (Python async web framework)
- **Frontend**: Vanilla JavaScript (no framework bloat)
- **Charts**: Chart.js (statistics and analytics)
- **Graphs**: D3.js (interactive knowledge visualization)
- **Styling**: Custom CSS (14KB, no dependencies)
- **Real-time**: WebSockets for live updates

---

## 🚀 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (Frontend)                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │
│  │Dashboard│  │Memories │  │ Config  │  │Analytics │  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘  │
│       │            │             │             │         │
│       └────────────┴─────────────┴─────────────┘         │
│                     │                                     │
│              JavaScript API Client                       │
│              (common.js utilities)                       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────┴──────────────────────────────────┐
│               FastAPI Server (Backend)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │         RESTful API Endpoints                    │   │
│  │  • /api/config       • /api/analytics/*         │   │
│  │  • /api/memories/*   • /api/graph/*             │   │
│  │  • /ws/updates       • /health                  │   │
│  └─────────────────────────────────────────────────┘   │
│                       │                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Data Layer (Pluggable)                   │   │
│  │  • JSON File Storage (default)                  │   │
│  │  • PostgreSQL (future)                          │   │
│  │  • Experimental Agent Integration               │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Request Flow

1. **User Action** (click button, submit form)
   ↓
2. **JavaScript Handler** (dashboard.js, config.js, etc.)
   ↓
3. **API Call** (via common.js utilities)
   ↓
4. **FastAPI Endpoint** (dashboard_server.py)
   ↓
5. **Data Processing** (fetch/update memories, config, etc.)
   ↓
6. **JSON Response** (serialized data)
   ↓
7. **Update UI** (render charts, update tables, show notifications)

---

## 📖 Usage Examples

### Example 1: Viewing Memory Distribution

1. Open dashboard at http://localhost:8001
2. Look at the **"Memory Distribution by Type"** pie chart
3. See breakdown of facts, preferences, context, and episodic memories
4. Check the **"Top Categories"** bar chart below

### Example 2: Browsing Memories

1. Click **"🧠 Memories"** in navigation
2. Use filters at top:
   - Select type: "fact"
   - Select category: "programming"
   - Search: "python"
3. Click **"📊 Graph View"** button
4. Interactive graph appears showing memory connections
5. Drag nodes around
6. Click a node to see full memory details
7. Click **"Delete Memory"** if needed

### Example 3: Configuring Models

1. Click **"⚙️ Config"** in navigation
2. In **Models** tab:
   - Change Chat Model to "gpt-4o"
   - Change Embedding to "text-embedding-3-large"
3. In **Search** tab:
   - Adjust similarity threshold slider to 0.8
   - Set default limit to 20
4. Click **"💾 Save Changes"**
5. Green success message appears

### Example 4: Testing Search

1. Click **"🎮 Playground"** in navigation
2. In **Search Testing** section:
   - Enter query: "What are my coding preferences?"
   - Select strategy: "Semantic (Vector)"
   - Set limit: 5
3. Click **"🚀 Run Search"**
4. Results appear below with similarity scores
5. Check the **Live Console** for timing information

### Example 5: Creating Test Memory

1. Go to **Playground** page
2. In **Create Test Memory** section:
   - Content: "I prefer TypeScript over JavaScript"
   - Type: "preference"
   - Categories: "programming, typescript, preferences"
3. Click **"💾 Create Memory"**
4. Success message shows the new memory ID
5. Navigate to **Memories** to see it in the list

---

## 🔧 Configuration Options

### Server Configuration

Edit `dashboard_server.py` if needed:

```python
class WebConfig:
    web_host: str = "0.0.0.0"    # Change to "localhost" for local-only
    web_port: int = 8001          # Change port if 8001 is in use
    use_json_storage: bool = True # Use JSON file storage (vs PostgreSQL)
```

### Storage Location

Memories are stored in:
```
packages/backend/experiments/web/data/memories.json
```

You can manually edit this file or use the API to manage memories.

---

## 🎯 Features in Detail

### Real-time Updates
- WebSocket connection for live updates
- Auto-refresh every 30 seconds
- Instant notifications for actions
- Live console in playground

### Interactive Charts
All charts are interactive:
- **Hover**: See exact values
- **Click**: Filter/select (where applicable)
- **Zoom**: Some charts support zooming
- **Export**: Right-click to save chart as image

### Knowledge Graph Features
- **Force Simulation**: Physics-based node positioning
- **Drag & Drop**: Move nodes around
- **Zoom & Pan**: Navigate large graphs
- **Color Coding**: Different colors for memory types
- **Labels**: Toggle visibility of node labels
- **Physics Control**: Pause/resume simulation

### Search Strategies Explained

- **Auto**: Intelligent strategy selection based on query
- **Semantic**: Vector similarity using embeddings
- **Keyword**: BM25 traditional keyword search
- **Categorical**: Filter by category tags
- **Temporal**: Time-based relevance
- **Hybrid**: Combination of vector + keyword (weighted)

---

## 🐛 Troubleshooting

### Server Won't Start

**Problem**: ModuleNotFoundError for fastapi
**Solution**:
```bash
cd packages/backend
poetry install
poetry run python experiments/web/dashboard_server.py
```

**Problem**: Port 8001 already in use
**Solution**: Change port in `dashboard_server.py` or kill the process:
```bash
lsof -i :8001
kill -9 <PID>
```

### Page Won't Load

**Problem**: Blank page or "Cannot connect"
**Solution**:
1. Check server is running (look for "🚀 Starting..." message)
2. Try http://localhost:8001 instead of 127.0.0.1
3. Check browser console for errors (F12)
4. Clear browser cache

### Charts Not Showing

**Problem**: Empty chart areas
**Solution**:
1. Check internet connection (Chart.js loads from CDN)
2. Open browser console (F12) and look for errors
3. Wait a few seconds for data to load
4. Try clicking the Refresh button

### WebSocket Connection Failed

**Problem**: "Disconnected" status in Playground
**Solution**:
1. Server must be running
2. Try clicking "Connect" button again
3. Check browser console for WebSocket errors
4. WebSocket URL is ws://localhost:8001/ws/updates

---

## 📊 Sample Data

The dashboard works with or without real data:
- **With real experimental agent**: Shows actual memories and metrics
- **Without (demo mode)**: Shows mock data for demonstration

To generate sample memories for testing:
1. Use the **Playground** → **Create Test Memory**
2. Or manually add to `data/memories.json`:

```json
{
  "memories": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "content": "User prefers dark mode in VS Code",
      "memory_type": "preference",
      "user_id": "user-123",
      "created_at": "2025-11-18T12:00:00Z",
      "metadata": {
        "categories": ["preferences", "vscode", "ui"]
      }
    }
  ]
}
```

---

## 🚀 Next Steps

### Immediate Use
1. **Explore the dashboard**: Click through all pages
2. **Create test memories**: Use the playground
3. **Try different views**: List vs Graph in Memories page
4. **Experiment with config**: Try different models and parameters

### Integration
To integrate with your experimental agent:
1. Update imports in `dashboard_server.py`
2. Replace mock storage with real `JSONMemoryStorage` or database
3. Connect real analytics tracker
4. Add authentication if deploying

### Customization
- **Colors**: Edit CSS variables in `static/css/main.css`
- **Charts**: Modify chart configs in JavaScript files
- **Layout**: Adjust grid templates in CSS
- **Features**: Add new endpoints in `dashboard_server.py`

---

## 📝 File Manifest

All files created:

### Templates (6 files)
- `templates/base.html` - Base template with navigation
- `templates/dashboard.html` - Main dashboard page
- `templates/memories.html` - Memory browser with graph
- `templates/config.html` - Configuration panel
- `templates/analytics.html` - Analytics dashboard
- `templates/playground.html` - Interactive playground

### Stylesheets (1 file)
- `static/css/main.css` - Complete styling (14KB)

### JavaScript (6 files)
- `static/js/common.js` - Shared utilities
- `static/js/dashboard.js` - Dashboard logic
- `static/js/memories.js` - Memory browser
- `static/js/config.js` - Configuration
- `static/js/analytics.js` - Analytics charts
- `static/js/playground.js` - Playground features

### Backend (1 file)
- `dashboard_server.py` - FastAPI server (18KB)

### Documentation (3 files)
- `README.md` - Complete documentation
- `INSTRUCTIONS.md` - This file
- `start_dashboard.sh` - Quick start script

### Total
**17 files**, ~70KB of code

---

## ❓ FAQ

**Q: Do I need to install anything?**
A: Just Python 3.11+ and Poetry. FastAPI and dependencies are already in pyproject.toml.

**Q: Can I use this in production?**
A: Not recommended without adding authentication. This is for development/demo.

**Q: Does it work without the experimental agent?**
A: Yes! It shows mock data in demo mode. Full features require agent integration.

**Q: Can I change the port?**
A: Yes, edit `web_port` in `dashboard_server.py` WebConfig class.

**Q: Is data persistent?**
A: Yes, stored in `data/memories.json` when using file storage.

**Q: Can multiple people use it at once?**
A: Yes, the server supports multiple concurrent connections.

**Q: How do I stop the server?**
A: Press `Ctrl+C` in the terminal where it's running.

---

## 🎓 Learning Resources

### Technologies Used
- **FastAPI**: https://fastapi.tiangolo.com
- **Jinja2**: https://jinja.palletsprojects.com
- **Chart.js**: https://www.chartjs.org
- **D3.js**: https://d3js.org
- **WebSockets**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

### Code Structure
- Modern ES6+ JavaScript (async/await, arrow functions, destructuring)
- CSS Grid and Flexbox for layouts
- CSS Custom Properties (variables) for theming
- RESTful API design patterns
- Async Python with FastAPI

---

## 💡 Tips & Tricks

1. **Keyboard Shortcuts**:
   - `Ctrl+F5` - Hard refresh (clear cache)
   - `F12` - Open browser DevTools
   - `Ctrl+Shift+I` - Also opens DevTools

2. **Browser DevTools**:
   - **Network Tab**: See all API requests
   - **Console Tab**: View logs and errors
   - **Application Tab**: Check WebSocket connection

3. **Performance**:
   - Use List View for large memory sets (100+ memories)
   - Graph View works best with <1000 nodes
   - Adjust search limit to control result count
   - Pause graph physics after positioning nodes

4. **Customization**:
   - Edit CSS variables for quick theme changes
   - Modify chart colors in JavaScript
   - Add custom badges/categories
   - Create custom search strategies

---

## 🎉 You're Ready!

The complete web dashboard is ready to use. Start the server and explore all the features!

```bash
cd packages/backend/experiments/web
./start_dashboard.sh
```

Then visit: **http://localhost:8001** 🚀

---

**Happy Exploring!** 🧪✨
