"""
Test script to verify search works for user 385056dd-0f39-4b3b-bf69-04c3724103be

This script will:
1. Check how many memories exist for this user
2. Check if memories have embeddings
3. Test all search strategies
4. Find memories about: city, soccer team, ethnicity
"""

import asyncio
from uuid import UUID
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.memory import Memory
from experiments.memory.search_router import SearchRouter
from experiments.memory.search_strategies import SemanticSearch, KeywordSearch


async def test_search():
    user_id = UUID('385056dd-0f39-4b3b-bf69-04c3724103be')

    print("=" * 80)
    print("SEARCH DIAGNOSTICS FOR USER", user_id)
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # 1. Count total memories
        print("\n1️⃣ CHECKING MEMORY COUNT...")
        count_stmt = select(func.count()).select_from(Memory).where(Memory.user_id == user_id)
        result = await db.execute(count_stmt)
        total = result.scalar()
        print(f"   ✅ Total memories: {total}")

        if total == 0:
            print("   ❌ NO MEMORIES FOUND! User has no memories in database.")
            print("   → Need to create memories first by chatting")
            return

        # 2. Check embedding coverage
        print("\n2️⃣ CHECKING EMBEDDING COVERAGE...")
        embed_stmt = select(func.count()).select_from(Memory).where(
            Memory.user_id == user_id,
            Memory.embedding.isnot(None)
        )
        result = await db.execute(embed_stmt)
        with_embeddings = result.scalar()
        coverage = (with_embeddings / total * 100) if total > 0 else 0

        print(f"   Total: {total}")
        print(f"   With embeddings: {with_embeddings}")
        print(f"   Without embeddings: {total - with_embeddings}")
        print(f"   Coverage: {coverage:.1f}%")

        if coverage < 50:
            print("   ⚠️ WARNING: Low embedding coverage! Semantic search may not work well.")

        # 3. Show sample memories
        print("\n3️⃣ SAMPLE MEMORIES:")
        sample_stmt = select(Memory).where(Memory.user_id == user_id).limit(10)
        result = await db.execute(sample_stmt)
        memories = result.scalars().all()

        for i, m in enumerate(memories, 1):
            has_emb = "✅" if m.embedding else "❌"
            print(f"   {i}. [{has_emb}] [{m.memory_type.value}] {m.content[:100]}")
            if m.extra_data and m.extra_data.get('categories'):
                print(f"       Categories: {m.extra_data.get('categories')}")

        # 4. Test keyword searches for specific topics
        print("\n4️⃣ TESTING KEYWORD SEARCHES...")
        keyword_search = KeywordSearch()

        test_queries = [
            "city",
            "soccer team",
            "ethnicity",
            "favorite",
        ]

        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = await keyword_search.search(
                query, user_id, db,
                limit=10,  # Increase limit
                memory_types=None  # Search ALL memory types
            )
            print(f"   Results: {len(results)}")
            for r in results[:5]:  # Show more results
                print(f"      [{r.score:.3f}] {r.content[:100]}")

        # 5. Test semantic search
        if coverage > 0:
            print("\n5️⃣ TESTING SEMANTIC SEARCH...")
            semantic_search = SemanticSearch()

            test_queries_semantic = [
                "what city do i like",
                "my favorite soccer team",
                "my ethnicity",
            ]

            for query in test_queries_semantic:
                print(f"\n   Query: '{query}'")
                try:
                    results = await semantic_search.search(
                        query, user_id, db,
                        limit=10,  # Increase limit
                        threshold=0.3,  # Keep threshold low for broad search
                        memory_types=None  # Search ALL memory types
                    )
                    print(f"   Results: {len(results)}")
                    for r in results[:5]:  # Show more results
                        print(f"      [{r.score:.3f}] {r.content[:100]}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")

        # 6. Test with search router (auto-routing)
        print("\n6️⃣ TESTING SEARCH ROUTER (AUTO-ROUTING)...")
        router = SearchRouter()

        test_queries_router = [
            "what city do i like the most",
            "my favorite soccer team",
            "tell me about my ethnicity",
        ]

        for query in test_queries_router:
            print(f"\n   Query: '{query}'")
            try:
                results = await router.search(
                    query=query,
                    user_id=user_id,
                    db=db,
                    auto_route=True,
                    limit=10,  # Increase limit
                    memory_types=None  # Search ALL memory types
                )
                print(f"   Results: {len(results)}")
                for r in results[:5]:  # Show more results
                    print(f"      [{r.score:.3f}] {r.content[:100]}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("DIAGNOSTICS COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
