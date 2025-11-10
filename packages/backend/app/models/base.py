"""
Re-export the shared declarative Base used across the application.
All models depend on app.db.base.Base; this module keeps backwards compatibility.
"""

from app.db.base import Base

__all__ = ["Base"]
