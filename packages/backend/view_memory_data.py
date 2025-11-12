"""
Quick script to view memory data created by tests.

Usage:
    poetry run python view_memory_data.py
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.memory import Memory, MemoryType, MemoryCollection
from app.models.user import User

# Load environment
load_dotenv(Path(__file__).parent / ".env")
engine = create_async_engine(settings.async_database_url, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def view_all_data():
    """Display all memory system data in a readable format."""
    print("\n" + "=" * 80)
    print("MEMORY SYSTEM DATA VIEWER")
    print("=" * 80)

    async with async_session() as session:
        # Users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"\n👤 Users: {len(users)}")
        for user in users:
            print(f"   - {user.clerk_user_id} ({user.email})")

        # Memory counts by type
        print(f"\n🧠 Memories by Type:")
        for memory_type in MemoryType:
            result = await session.execute(
                select(func.count(Memory.id)).where(Memory.memory_type == memory_type)
            )
            count = result.scalar()
            print(f"   - {memory_type.value.upper()}: {count}")

        # Recent memories
        result = await session.execute(
            select(Memory).order_by(Memory.created_at.desc()).limit(5)
        )
        memories = result.scalars().all()
        print(f"\n📝 Recent Memories (last {len(memories)}):")
        for mem in memories:
            content_preview = mem.content[:60] + "..." if len(mem.content) > 60 else mem.content
            print(f"   - [{mem.memory_type.value}] {content_preview}")
            if mem.extra_data:
                print(f"     Metadata: {mem.extra_data}")

        # Collections
        result = await session.execute(select(MemoryCollection))
        collections = result.scalars().all()
        print(f"\n📁 Collections: {len(collections)}")
        for coll in collections:
            print(f"   - {coll.name} ({coll.collection_type})")
            if coll.description:
                print(f"     {coll.description}")

        # Stressor memories (JSONB query demo)
        result = await session.execute(
            select(Memory)
            .where(Memory.extra_data["stressor"].as_boolean().is_(True))  # NULL-safe comparison
        )
        stressors = result.scalars().all()
        print(f"\n😰 Stressor Memories: {len(stressors)}")
        for mem in stressors:
            emotion = mem.extra_data.get("emotion", "unknown")
            intensity = mem.extra_data.get("intensity", 0)
            content_preview = mem.content[:60] + "..." if len(mem.content) > 60 else mem.content
            print(f"   - {content_preview}")
            print(f"     Emotion: {emotion}, Intensity: {intensity}")

    print("\n" + "=" * 80)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(view_all_data())
