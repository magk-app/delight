"""
SQLAlchemy declarative base for all models.
All database models should inherit from Base.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
