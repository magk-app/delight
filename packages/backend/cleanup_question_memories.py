"""
Cleanup script to delete question-based memories (bad data).

This script identifies and deletes memories that are questions rather than facts:
- Contains question words (what, where, when, why, how, who)
- Ends with "?"
- Vague statements like "user has a favorite X"

Run this after fixing the fact extractor to clean up historical bad data.
"""

import asyncio
import re
from uuid import UUID
from sqlalchemy import select, delete as sql_delete
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory


async def identify_question_memories(user_id: UUID = None):
    """Identify memories that are likely questions or vague statements."""

    question_patterns = [
        r'\?$',  # Ends with question mark
        r'^(what|where|when|why|how|who|which|do|does|did|can|could|would|should)\b',  # Starts with question word
        r'user has a (favorite|preferred)',  # Vague "user has a..." patterns
        r'^(do|does|did) (i|you|we)',  # "do i like", "does user have", etc.
    ]

    async with AsyncSessionLocal() as db:
        # Fetch memories
        query = select(Memory)
        if user_id:
            query = query.where(Memory.user_id == user_id)

        result = await db.execute(query)
        all_memories = result.scalars().all()

        question_memories = []

        for memory in all_memories:
            content_lower = memory.content.lower().strip()

            # Check if matches any question pattern
            for pattern in question_patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    question_memories.append(memory)
                    break

        return question_memories


async def cleanup_question_memories(user_id: UUID = None, dry_run: bool = True):
    """Delete question memories from database.

    Args:
        user_id: Optional user ID to filter by
        dry_run: If True, only show what would be deleted without deleting
    """

    print("=" * 80)
    print("QUESTION MEMORY CLEANUP")
    print("=" * 80)

    if dry_run:
        print("🔍 DRY RUN MODE - No deletions will be performed")
    else:
        print("⚠️  LIVE MODE - Memories WILL be deleted!")

    print()

    # Identify question memories
    question_memories = await identify_question_memories(user_id)

    if not question_memories:
        print("✅ No question memories found! Database is clean.")
        return

    print(f"Found {len(question_memories)} question/vague memories:\n")

    # Group by user for better organization
    by_user = {}
    for mem in question_memories:
        if mem.user_id not in by_user:
            by_user[mem.user_id] = []
        by_user[mem.user_id].append(mem)

    # Display findings
    for uid, mems in by_user.items():
        print(f"\n📁 User {uid}:")
        print(f"   {len(mems)} question memories found\n")

        for i, mem in enumerate(mems[:10], 1):  # Show first 10
            print(f"   {i}. [{mem.memory_type.value}] {mem.content[:80]}")
            print(f"      ID: {mem.id}")
            print(f"      Created: {mem.created_at}")
            print()

        if len(mems) > 10:
            print(f"   ... and {len(mems) - 10} more")

    # Delete if not dry run
    if not dry_run:
        print("\n" + "=" * 80)
        print("DELETING MEMORIES...")
        print("=" * 80 + "\n")

        async with AsyncSessionLocal() as db:
            memory_ids = [m.id for m in question_memories]

            # Delete in batches
            deleted_count = 0
            for memory_id in memory_ids:
                try:
                    stmt = sql_delete(Memory).where(Memory.id == memory_id)
                    await db.execute(stmt)
                    deleted_count += 1

                    if deleted_count % 10 == 0:
                        print(f"   Deleted {deleted_count}/{len(memory_ids)}...")

                except Exception as e:
                    print(f"   ❌ Failed to delete {memory_id}: {e}")

            await db.commit()
            print(f"\n✅ Successfully deleted {deleted_count} question memories")
    else:
        print("\n💡 To actually delete these memories, run with dry_run=False")

    print("\n" + "=" * 80)


async def main():
    """Run cleanup for specific user."""

    # User from your example
    user_id = UUID('385056dd-0f39-4b3b-bf69-04c3724103be')

    # First, run dry run to see what would be deleted
    print("Running DRY RUN first...\n")
    await cleanup_question_memories(user_id, dry_run=True)

    # Uncomment to actually delete:
    # print("\n\nRunning LIVE deletion...\n")
    # await cleanup_question_memories(user_id, dry_run=False)


if __name__ == "__main__":
    asyncio.run(main())
