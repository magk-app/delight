#!/bin/bash
set -e

echo "🚀 Starting Delight backend..."

# Check if packages are installed by trying to import uvicorn
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "⚠️  Packages not found, installing from requirements.txt..."
    if [ -f requirements.txt ]; then
        pip install --no-cache-dir -r requirements.txt
    else
        echo "❌ requirements.txt not found, installing via Poetry..."
        pip install poetry
        poetry config virtualenvs.create false
        poetry install --no-dev --no-interaction --no-ansi
    fi
else
    echo "✅ Packages already installed"
fi

# Run migrations (allow failure if DB not configured)
echo "📊 Running database migrations..."
python -m alembic upgrade head || echo "⚠️  Migrations skipped (database may not be configured)"

# Start the server
echo "🌟 Starting FastAPI server on port ${PORT:-8000}..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

