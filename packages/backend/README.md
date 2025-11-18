# Delight Backend API

FastAPI backend for the Delight AI companion platform.

## Quick Start

```bash
# Install dependencies
poetry install

# Start development server (see "Running the Server" section below for options)
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Visit:

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Running the Server

Choose the command that fits your scenario:

### 🏠 Local Development (localhost only)

Best for: Standard development, fastest startup

```bash
poetry run uvicorn main:app --reload
```

### 🌐 Network-Accessible Development

Best for: Testing on mobile devices, Docker containers, or other machines on your network

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 🔧 Custom Port

Best for: When port 8000 is already in use

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 🐛 Debug Mode (Verbose Logging)

Best for: Troubleshooting issues, seeing detailed request/response logs

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### 🚀 Production-Like (No Reload)

Best for: Testing production behavior, performance testing

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

### ⚡ Production with Workers

Best for: Production deployment with multiple worker processes

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Project Structure

```
app/
├── api/v1/         # API routes
│   └── health.py   # Health check endpoint
├── core/           # Configuration and dependencies
├── models/         # SQLAlchemy database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── agents/         # LangGraph AI agents
├── workers/        # ARQ background jobs
└── db/             # Database setup and migrations
```

## Development

```bash
# Run tests
poetry run pytest

# Lint code
poetry run ruff check .

# Format code
poetry run black .

# Type check
poetry run mypy .
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

- **INFRA_MODE**: `cloud-dev` or `local`
- **DATABASE_URL**: PostgreSQL connection string
- **REDIS_URL**: Redis connection string
- **CLERK_SECRET_KEY**: Clerk authentication secret
- **OPENAI_API_KEY**: OpenAI API key

See `.env.example` for detailed configuration instructions.
