# GEMINI.md - Delight Project

This document provides a comprehensive overview of the Delight project for AI-assisted development.

## Project Overview

Delight is an emotionally intelligent AI companion that transforms overwhelming goals into achievable daily missions. It's a monorepo project using pnpm workspaces, with a frontend and a backend.

- **Frontend:** Built with Next.js, React, TypeScript, and Tailwind CSS. It uses Clerk for authentication and Playwright for end-to-end testing.
- **Backend:** A Python application powered by FastAPI. It uses SQLAlchemy for the ORM, Alembic for database migrations, and PostgreSQL with pgvector for data storage. The AI layer is built with LangChain and LangGraph. Redis is used for caching and background jobs with ARQ.

## Building and Running

The project uses a `Makefile` to simplify common tasks.

### Prerequisites

- Node.js >= 20.0.0
- pnpm >= 8.0.0
- Python 3.11+
- Poetry
- Docker Desktop (for local development)

### Key Commands

- **Install dependencies:**
  ```bash
  make install
  ```

- **Run in development mode:**
  ```bash
  make dev
  ```
  This will start both the frontend and backend servers.
  - Frontend: `http://localhost:3000`
  - Backend API: `http://localhost:8000`
  - Swagger UI: `http://localhost:8000/docs`

- **Run frontend only:**
  ```bash
  make dev:frontend
  ```

- **Run backend only:**
  ```bash
  make dev:backend
  ```

- **Build for production:**
  ```bash
  make build
  ```

- **Run linters:**
  ```bash
  make lint
  ```

- **Run tests:**
  ```bash
  make test
  ```

## Development Conventions

- **Code Style:** The backend uses `black` for code formatting and `ruff` for linting. The frontend uses ESLint.
- **Testing:** The backend uses `pytest` for unit and integration tests. The frontend uses Playwright for end-to-end testing.
- **Commits:** (Inferring from common practice, but not explicitly stated) Commit messages should follow the Conventional Commits specification.
- **Branching:** (Inferring from common practice, but not explicitly stated) Development should be done on feature branches, with pull requests to the main branch.

## Documentation

The `docs/` directory contains extensive documentation, including:

- `docs/ARCHITECTURE.md`: Technical decisions, system design, and implementation patterns.
- `docs/SETUP.md`: A detailed guide for setting up the development environment.
- `docs/dev/BMAD-DEVELOPER-GUIDE.md`: A guide to the development workflow.
