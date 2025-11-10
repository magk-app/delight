# Delight Backend API

FastAPI backend for the Delight AI companion platform.

## Quick Start

```bash
# Install dependencies
poetry install

# Start development server
poetry run uvicorn main:app --reload
```

Visit:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

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

