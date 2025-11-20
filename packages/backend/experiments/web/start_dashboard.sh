#!/bin/bash
# Start Dashboard Server Script
# Quick launcher for the Experimental Agent Web Dashboard

set -e

echo "🧪 Starting Experimental Agent Web Dashboard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we're in the correct directory
if [ ! -f "dashboard_server.py" ]; then
    echo "Error: dashboard_server.py not found"
    echo "Please run this script from the experiments/web directory"
    exit 1
fi

# Navigate to backend directory for Poetry
cd ../../

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry is not installed"
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if virtual environment is set up
if ! poetry env info &> /dev/null; then
    echo "📦 Setting up Poetry environment..."
    poetry install
fi

# Start the server
echo "🚀 Starting dashboard server on http://localhost:8001"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard:   http://localhost:8001"
echo "📚 API Docs:    http://localhost:8001/docs"
echo "🏥 Health:      http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the server
poetry run python experiments/web/dashboard_server.py
