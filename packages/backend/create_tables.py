"""
Create database tables using SQLAlchemy create_all().

This is an alternative to Alembic migrations for development environments
where network access may be restricted.
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import engine
from app.models import Base  # This imports all models

async def create_tables():
    """Create all database tables."""
    print("🔄 Creating database tables...")

    try:
        async with engine.begin() as conn:
            # Drop all tables (for clean slate in development)
            print("⚠️  Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)

            # Create all tables
            print("✅ Creating tables from models...")
            await conn.run_sync(Base.metadata.create_all)

        print("\n✅ Database tables created successfully!")
        print("\nTables created:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_tables())
