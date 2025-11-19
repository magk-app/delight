"""
Diagnostic script to understand why "Likes Yoshinoya" isn't retrieved for "what is my favorite restaurant".

This will:
1. Find the "Likes Yoshinoya" memory
2. Generate embedding for the query "what is my favorite restaurant"
3. Calculate cosine similarity manually
4. Check if categories would help
5. Test all search strategies
"""

import asyncio
import numpy as np
from uuid import UUID
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory
from experiments.memory.embedding_service import EmbeddingService
from experiments.memory.search_strategies import SemanticSearch, KeywordSearch, CategoricalSearch, HybridSearch
from experiments.memory.search_router import SearchRouter


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


async def test_yoshinoya_search():
    user_id = UUID('385056dd-0f39-4b3b-bf69-04c3724103be')
    query = "what is my favorite restaurant"

    print("=" * 80)
    print("YOSHINOYA SEARCH DIAGNOSTIC")
    print("=" * 80)
    print(f"User ID: {user_id}")
    print(f"Query: '{query}'")
    print("=" * 80)

    embedding_service = EmbeddingService()

    async with AsyncSessionLocal() as db:
        # 1. Find "Yoshinoya" memory
        print("\n1️⃣  FINDING YOSHINOYA MEMORY...\n")
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.content.ilike('%yoshinoya%')
        )
        result = await db.execute(stmt)
        yoshinoya_memories = result.scalars().all()

        if not yoshinoya_memories:
            print("❌ No Yoshinoya memory found!")
            print("   Searching all restaurant-related memories...")

            stmt = select(Memory).where(
                Memory.user_id == user_id,
                Memory.content.ilike('%restaurant%')
            )
            result = await db.execute(stmt)
            restaurant_memories = result.scalars().all()

            if restaurant_memories:
                print(f"   Found {len(restaurant_memories)} restaurant memories:")
                for mem in restaurant_memories:
                    print(f"   - {mem.content}")
            else:
                print("   No restaurant memories found at all!")

            return
        else:
            print(f"✅ Found {len(yoshinoya_memories)} Yoshinoya memory(ies):")
            for mem in yoshinoya_memories:
                print(f"\n   Content: {mem.content}")
                print(f"   Type: {mem.memory_type.value}")
                print(f"   ID: {mem.id}")
                print(f"   Has embedding: {'✅ Yes' if mem.embedding is not None else '❌ No'}")
                print(f"   Categories: {mem.extra_data.get('categories', []) if mem.extra_data else []}")
                print(f"   Created: {mem.created_at}")

        yoshinoya_mem = yoshinoya_memories[0]

        # 2. Check embedding
        print("\n2️⃣  CHECKING EMBEDDINGS...\n")

        if yoshinoya_mem.embedding is None:
            print("❌ Yoshinoya memory has NO embedding! Semantic search won't work.")
            print("   Generating embedding now...")
            yoshinoya_mem.embedding = await embedding_service.embed_text(yoshinoya_mem.content)
            db.add(yoshinoya_mem)
            await db.commit()
            await db.refresh(yoshinoya_mem)
            print("   ✅ Embedding generated!")
        else:
            print(f"✅ Yoshinoya memory has embedding (dimension: {len(yoshinoya_mem.embedding)})")

        # Generate query embedding
        print(f"\n   Generating embedding for query: '{query}'")
        query_embedding = await embedding_service.embed_text(query)
        print(f"   ✅ Query embedding generated (dimension: {len(query_embedding)})")

        # 3. Calculate cosine similarity
        print("\n3️⃣  CALCULATING COSINE SIMILARITY...\n")

        similarity = cosine_similarity(
            np.array(query_embedding),
            np.array(yoshinoya_mem.embedding)
        )

        print(f"   Cosine similarity: {similarity:.4f}")
        print(f"   Current threshold: 0.3")
        print(f"   Would be retrieved: {'✅ Yes' if similarity >= 0.3 else '❌ No'}")

        # 4. Test with different keywords
        print("\n4️⃣  TESTING KEYWORD VARIATIONS...\n")

        test_queries = [
            "what is my favorite restaurant",
            "favorite restaurant",
            "yoshinoya",
            "restaurant I like",
            "food places I enjoy",
        ]

        for test_query in test_queries:
            test_emb = await embedding_service.embed_text(test_query)
            sim = cosine_similarity(np.array(test_emb), np.array(yoshinoya_mem.embedding))
            print(f"   '{test_query}': {sim:.4f} {'✅' if sim >= 0.3 else '❌'}")

        # 5. Check categories
        print("\n5️⃣  CHECKING CATEGORIES...\n")

        categories = yoshinoya_mem.extra_data.get('categories', []) if yoshinoya_mem.extra_data else []
        if categories:
            print(f"   Categories: {categories}")
            print(f"   Would categorical search help: {'✅ Yes' if 'food' in str(categories).lower() or 'restaurant' in str(categories).lower() else '⚠️  Maybe'}")
        else:
            print("   ❌ No categories assigned to this memory")

        # 6. Test all search strategies
        print("\n6️⃣  TESTING SEARCH STRATEGIES...\n")

        # Semantic search
        print("   Testing Semantic Search...")
        semantic_search = SemanticSearch()
        semantic_results = await semantic_search.search(
            query=query,
            user_id=user_id,
            db=db,
            threshold=0.3,
            limit=10
        )
        yoshinoya_in_results = any(r.memory_id == yoshinoya_mem.id for r in semantic_results)
        print(f"      Results: {len(semantic_results)}")
        print(f"      Yoshinoya found: {'✅ Yes' if yoshinoya_in_results else '❌ No'}")
        if semantic_results:
            print(f"      Top results:")
            for i, r in enumerate(semantic_results[:3], 1):
                is_yoshinoya = "👈 YOSHINOYA" if r.memory_id == yoshinoya_mem.id else ""
                print(f"         {i}. [{r.score:.3f}] {r.content[:60]}... {is_yoshinoya}")

        # Keyword search
        print("\n   Testing Keyword Search...")
        keyword_search = KeywordSearch()
        keyword_results = await keyword_search.search(
            query=query,
            user_id=user_id,
            db=db,
            limit=10
        )
        yoshinoya_in_keyword = any(r.memory_id == yoshinoya_mem.id for r in keyword_results)
        print(f"      Results: {len(keyword_results)}")
        print(f"      Yoshinoya found: {'✅ Yes' if yoshinoya_in_keyword else '❌ No'}")
        if keyword_results:
            print(f"      Top results:")
            for i, r in enumerate(keyword_results[:3], 1):
                is_yoshinoya = "👈 YOSHINOYA" if r.memory_id == yoshinoya_mem.id else ""
                print(f"         {i}. [{r.score:.3f}] {r.content[:60]}... {is_yoshinoya}")

        # Hybrid search
        print("\n   Testing Hybrid Search (Semantic + Keyword + Categorical)...")
        hybrid_search = HybridSearch()
        hybrid_results = await hybrid_search.search(
            query=query,
            user_id=user_id,
            db=db,
            limit=10
        )
        yoshinoya_in_hybrid = any(r.memory_id == yoshinoya_mem.id for r in hybrid_results)
        print(f"      Results: {len(hybrid_results)}")
        print(f"      Yoshinoya found: {'✅ Yes' if yoshinoya_in_hybrid else '❌ No'}")
        if hybrid_results:
            print(f"      Top results:")
            for i, r in enumerate(hybrid_results[:3], 1):
                is_yoshinoya = "👈 YOSHINOYA" if r.memory_id == yoshinoya_mem.id else ""
                print(f"         {i}. [{r.score:.3f}] {r.content[:60]}... {is_yoshinoya}")

        # Search router (auto-routing)
        print("\n   Testing Search Router (Auto-Routing)...")
        router = SearchRouter()
        router_results = await router.search(
            query=query,
            user_id=user_id,
            db=db,
            auto_route=True,
            limit=10
        )
        yoshinoya_in_router = any(r.memory_id == yoshinoya_mem.id for r in router_results)
        print(f"      Results: {len(router_results)}")
        print(f"      Yoshinoya found: {'✅ Yes' if yoshinoya_in_router else '❌ No'}")
        if router_results:
            print(f"      Top results:")
            for i, r in enumerate(router_results[:3], 1):
                is_yoshinoya = "👈 YOSHINOYA" if r.memory_id == yoshinoya_mem.id else ""
                print(f"         {i}. [{r.score:.3f}] {r.content[:60]}... {is_yoshinoya}")

        # 7. Recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        if similarity < 0.3:
            print("\n⚠️  Cosine similarity too low!")
            print(f"   Similarity: {similarity:.4f} < 0.3 (threshold)")
            print("\n   Possible fixes:")
            print("   1. Lower semantic search threshold to 0.2 or 0.15")
            print("   2. Use hybrid search (combines semantic + keyword + categories)")
            print("   3. Improve memory content to include more context")
            print(f"      Current: \"{yoshinoya_mem.content}\"")
            print(f"      Better: \"Favorite restaurant is Yoshinoya\"")
        elif not yoshinoya_in_results:
            print("\n⚠️  Yoshinoya similarity is above threshold, but not in results!")
            print("   This suggests:")
            print("   - Other memories have higher similarity scores")
            print("   - Need to increase result limit OR improve query")
        else:
            print("\n✅ Yoshinoya found in semantic search!")
            print("   System is working correctly.")

        if not categories:
            print("\n💡 Add categories to improve categorical search:")
            print("   Categories like 'food', 'restaurant', 'preferences' would help")

        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_yoshinoya_search())
