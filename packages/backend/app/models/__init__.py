"""
Database models package.
Imports all models to register them with SQLAlchemy Base.
"""

from app.db.base import Base
from app.models.user import User, UserPreferences

__all__ = ["Base", "User", "UserPreferences"]
