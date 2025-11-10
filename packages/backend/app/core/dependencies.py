"""
FastAPI dependencies for dependency injection.
Re-exports common dependencies for easy import in routes.
"""

from app.db.session import get_db

__all__ = ["get_db"]

