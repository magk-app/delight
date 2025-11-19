#!/bin/bash
# Railway startup script for experimental web server
# This script ensures proper environment setup before starting the server

set -e

echo "🚀 Starting Experimental Web Server for Railway..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Navigate to backend directory
cd "$(dirname "$0")/../.." || exit 1

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry is not installed"
    exit 1
fi

# Ensure dependencies are installed (Railway should have done this, but double-check)
if [ ! -d ".venv" ] && [ ! -f "poetry.lock" ]; then
    echo "📦 Installing dependencies..."
    poetry install --no-dev --no-interaction
fi

# Set environment variables if not already set
export PORT=${PORT:-8001}
export HOST=${HOST:-0.0.0.0}

# Print configuration
echo "📊 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Database: ${DATABASE_URL:+Set} ${DATABASE_URL:-Not set}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start the server
echo "🚀 Starting server..."
poetry run python -m experiments.web.dashboard_server

