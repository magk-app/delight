"""
Database Base Configuration
SQLAlchemy declarative base and metadata for models
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class

    All models should inherit from this base:

    Example:
        from app.db.base import Base

        class User(Base):
            __tablename__ = "users"
            id = Column(UUID, primary_key=True)
    """

    pass


# Export base for models to import
__all__ = ["Base"]
