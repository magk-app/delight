#!/bin/sh
set -e

echo "🚀 Starting Delight backend..."

# Check if venv exists, if not create it and install packages
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
    .venv/bin/python -m pip install --upgrade pip setuptools wheel
    .venv/bin/python -m pip install poetry
    .venv/bin/poetry export -f requirements.txt --output requirements.txt --without-hashes || {
        echo "⚠️  Poetry export failed, installing directly from pyproject.toml..."
        .venv/bin/poetry config virtualenvs.create false
        .venv/bin/poetry install --no-dev --no-interaction --no-ansi
    }
    if [ -f requirements.txt ]; then
        echo "📥 Installing from requirements.txt..."
        .venv/bin/python -m pip install --no-cache-dir -r requirements.txt
    fi
else
    echo "✅ Virtual environment found"
fi

# Verify packages
echo "✅ Verifying packages..."
.venv/bin/python -c "import uvicorn, alembic" || {
    echo "❌ Packages missing, installing..."
    if [ -f requirements.txt ]; then
        .venv/bin/python -m pip install --no-cache-dir -r requirements.txt
    else
        .venv/bin/python -m pip install poetry
        .venv/bin/poetry config virtualenvs.create false
        .venv/bin/poetry install --no-dev --no-interaction --no-ansi
    fi
}

# Run migrations
echo "📊 Running migrations..."
.venv/bin/python -m alembic upgrade head || echo "⚠️  Migrations skipped"

# Start server
echo "🌟 Starting server on port ${PORT:-8000}..."
exec .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

