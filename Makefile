.PHONY: local cloud-dev stop install dev lint test help

# Help target - show available commands
help:
	@echo "Delight Development Commands"
	@echo ""
	@echo "Infrastructure Mode:"
	@echo "  make local      - Start local development mode (Docker PostgreSQL + Redis)"
	@echo "  make cloud-dev  - Use cloud-managed services (Supabase + Upstash)"
	@echo "  make stop       - Stop local Docker services"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development servers (frontend + backend)"
	@echo "  make lint       - Run linters (ESLint + Ruff + Black)"
	@echo "  make test       - Run test suites (Jest + pytest)"
	@echo ""

# Start local development mode (Docker PostgreSQL + Redis)
local:
	@echo "🐳 Starting local development mode (Docker PostgreSQL + Redis)..."
	docker-compose up -d
	@echo ""
	@echo "✅ Local services started:"
	@echo "   PostgreSQL: localhost:5432"
	@echo "   Redis: localhost:6379"
	@echo ""
	@echo "📝 Update your backend .env file:"
	@echo "   INFRA_MODE=local"
	@echo "   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight"
	@echo "   REDIS_URL=redis://localhost:6379"
	@echo ""

# Use cloud-managed services (Supabase + Upstash)
cloud-dev:
	@echo "☁️  Using cloud-managed services (Supabase + Upstash)..."
	@echo ""
	@echo "📝 Ensure your backend .env file contains:"
	@echo "   INFRA_MODE=cloud-dev"
	@echo "   DATABASE_URL=<your-supabase-connection-string>"
	@echo "   REDIS_URL=<your-upstash-redis-url>"
	@echo ""
	@echo "🔗 Setup links:"
	@echo "   Supabase: https://supabase.com"
	@echo "   Upstash: https://upstash.com"
	@echo "   Clerk: https://clerk.com"
	@echo ""

# Stop local Docker services
stop:
	@echo "🛑 Stopping local Docker services..."
	docker-compose down
	@echo "✅ Local services stopped"

# Install all dependencies
install:
	@echo "📦 Installing dependencies..."
	@echo "Installing root dependencies (concurrently)..."
	pnpm install
	@echo "Installing frontend dependencies..."
	cd packages/frontend && pnpm install
	@echo "Installing backend dependencies..."
	cd packages/backend && poetry install
	@echo "✅ All dependencies installed"

# Start development servers
dev:
	@echo "🚀 Starting development servers..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo ""
	pnpm dev

# Run linters
lint:
	@echo "🔍 Running linters..."
	@echo "Frontend (ESLint)..."
	pnpm --filter frontend lint
	@echo "Backend (Ruff + Black)..."
	cd packages/backend && poetry run ruff check . && poetry run black --check .
	@echo "✅ Linting complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "Frontend tests..."
	pnpm --filter frontend test
	@echo "Backend tests..."
	cd packages/backend && poetry run pytest
	@echo "✅ Tests complete"

