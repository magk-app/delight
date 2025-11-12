"""Check current database state for memory migration"""
import asyncio
import sys
from pathlib import Path

# Add the backend app directory to the path so we can import Settings
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def check_state():
    # Use the async database URL from settings (converts postgresql:// to postgresql+asyncpg://)
    try:
        database_url = settings.async_database_url
    except Exception as e:
        print("\n❌ ERROR: Could not load DATABASE_URL from environment")
        print(f"   Error: {e}")
        print("\n💡 SOLUTION:")
        print("   1. Make sure you have a .env file in packages/backend/")
        print("   2. Copy env.example to .env if needed: cp env.example .env")
        print("   3. Set DATABASE_URL in your .env file")
        print("      Format: postgresql+asyncpg://user:password@host:5432/database")
        print("      Or:     postgresql://user:password@host:5432/database")
        sys.exit(1)
    
    engine = create_async_engine(database_url, echo=False)

    async with engine.begin() as conn:
        # Check if memory_type enum exists
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'memory_type'
            ) as enum_exists;
        """))
        enum_exists = result.scalar()

        # Check if memories table exists
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'memories'
            ) as table_exists;
        """))
        table_exists = result.scalar()

        # Check if memory_collections table exists
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'memory_collections'
            ) as collections_exists;
        """))
        collections_exists = result.scalar()

        print("\n" + "="*60)
        print("DATABASE STATE CHECK")
        print("="*60)
        print(f"memory_type ENUM exists:        {enum_exists}")
        print(f"memories table exists:          {table_exists}")
        print(f"memory_collections table exists: {collections_exists}")
        print("="*60)

        if enum_exists and not table_exists:
            print("\n⚠️  PARTIAL MIGRATION STATE DETECTED!")
            print("   Enum exists but tables don't.")
            print("\n🔧 SOLUTION: Clean up orphaned enum")
            print("   Run: poetry run python cleanup_enum.py")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_state())
