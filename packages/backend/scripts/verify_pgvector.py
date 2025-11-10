"""Quick script to verify pgvector extension is enabled."""

import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal


async def verify_pgvector():
    """Check if pgvector extension is enabled."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
        row = result.fetchone()

        if row:
            print("✅ pgvector extension is ENABLED")
            print(f"   Version: {row[1]}")
            print(f"   Schema: {row[2]}")
        else:
            print("❌ pgvector extension is NOT enabled")


if __name__ == "__main__":
    asyncio.run(verify_pgvector())
