"""Clean up orphaned memory_type enum from failed migration"""
import asyncio
import sys
from pathlib import Path

# Add the backend app directory to the path so we can import Settings
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def cleanup():
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
    
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        print("\n🧹 Cleaning up orphaned enum...")

        # Drop the enum if it exists
        await conn.execute(text("""
            DROP TYPE IF EXISTS memory_type CASCADE;
        """))

        print("✅ Cleanup complete!")
        print("\nNow run: poetry run alembic upgrade head")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(cleanup())
