# packages/backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for wheels and postgres
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Poetry to export lock to requirements
RUN pip install --upgrade pip setuptools wheel poetry

# Copy dependency manifests first for layer caching
COPY pyproject.toml poetry.lock* /app/

# Export and install runtime deps
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes && \
    pip install -r requirements.txt

# Now copy the app
COPY . /app

# Alembic uses alembic.ini in CWD, so we run from /app
ENV PORT=8000
EXPOSE 8000

CMD (python -m alembic upgrade head || echo "Migrations skipped") && \
    python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}

