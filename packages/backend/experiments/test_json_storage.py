"""Test the experimental memory system using JSON storage (no PostgreSQL needed).

This script demonstrates all features using JSON file storage instead of PostgreSQL.
Perfect for testing without database setup.

Run with:
    cd packages/backend
    poetry run python experiments/test_json_storage.py
"""

import asyncio
import uuid

from experiments.database.json_storage import JSONStorage
from experiments.memory.fact_extractor import FactExtractor
from experiments.memory.categorizer import DynamicCategorizer
from experiments.memory.embedding_service import EmbeddingService


async def main():
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "EXPERIMENTAL MEMORY SYSTEM - JSON STORAGE TEST" + " " * 12 + "║")
    print("╚" + "=" * 68 + "╝\n")

    print("""
This demo uses JSON file storage (no PostgreSQL required).
Features:
- Fact extraction from complex messages
- Dynamic categorization
- Embedding generation
- JSON file persistence
- Keyword and categorical search
""")

    # Initialize components
    print("🔧 Initializing components...")
    storage = JSONStorage()
    fact_extractor = FactExtractor()
    categorizer = DynamicCategorizer()
    embedding_service = EmbeddingService()

    # Test user
    user_id = uuid.uuid4()
    print(f"👤 Test User ID: {user_id}\n")

    # ===== 1. FACT EXTRACTION =====
    print("=" * 70)
    print("1️⃣  FACT EXTRACTION")
    print("=" * 70 + "\n")

    message = """
    I'm Jack, a software developer based in San Francisco.
    I'm working on Delight, an AI companion app built with Python and React.
    My launch goal is Q1 2025, and I prefer TypeScript over JavaScript.
    I usually work late at night and love async programming patterns.
    I have experience with FastAPI, PostgreSQL, and OpenAI APIs.
    """

    print(f"📝 Message ({len(message)} chars):")
    print(message)

    print("\n🔍 Extracting facts...")
    extraction_result = await fact_extractor.extract_facts(message)

    print(f"\n✅ Extracted {len(extraction_result.facts)} facts:\n")
    for i, fact in enumerate(extraction_result.facts, 1):
        print(f"  {i}. [{fact.fact_type.value.upper()}] {fact.content}")
        print(f"      Confidence: {fact.confidence:.2f}")

    input("\nPress Enter to continue to categorization...")

    # ===== 2. CATEGORIZATION =====
    print("\n" + "=" * 70)
    print("2️⃣  DYNAMIC CATEGORIZATION")
    print("=" * 70 + "\n")

    # Categorize first 3 facts
    sample_facts = extraction_result.facts[:3]

    for i, fact in enumerate(sample_facts, 1):
        print(f"\nFact {i}: \"{fact.content}\"")
        result = await categorizer.categorize(fact.content)

        print(f"  Categories: {' → '.join(result.categories)}")
        print(f"  Confidence: {result.confidence:.2f}")

    input("\nPress Enter to continue to memory creation...")

    # ===== 3. MEMORY CREATION =====
    print("\n" + "=" * 70)
    print("3️⃣  MEMORY CREATION WITH EMBEDDINGS")
    print("=" * 70 + "\n")

    print("Creating memories from extracted facts...")

    for i, fact in enumerate(extraction_result.facts, 1):
        # Categorize
        cat_result = await categorizer.categorize(fact.content)

        # Generate embedding
        embedding = await embedding_service.embed_text(fact.content)

        # Create memory
        memory = await storage.create_memory(
            user_id=user_id,
            content=fact.content,
            memory_type="personal",
            embedding=embedding,
            metadata={
                "fact_type": fact.fact_type.value,
                "confidence": fact.confidence,
                "categories": cat_result.categories,
                "category_hierarchy": cat_result.hierarchy.to_path() if cat_result.hierarchy else None
            }
        )

        print(f"  {i}. ✅ {fact.content[:50]}...")

    print(f"\n✅ Created {len(extraction_result.facts)} memories")

    input("\nPress Enter to continue to search...")

    # ===== 4. KEYWORD SEARCH =====
    print("\n" + "=" * 70)
    print("4️⃣  KEYWORD SEARCH")
    print("=" * 70 + "\n")

    queries = ["programming", "Python", "San Francisco"]

    for query in queries:
        print(f"Query: \"{query}\"")
        results = await storage.search_keyword(user_id, query, limit=3)

        if results:
            for memory, score in results:
                print(f"  [{score:.2f}] {memory.content}")
                print(f"          Categories: {', '.join(memory.metadata.get('categories', []))}")
        else:
            print("  No results found")
        print()

    input("\nPress Enter to continue to categorical search...")

    # ===== 5. CATEGORICAL SEARCH =====
    print("\n" + "=" * 70)
    print("5️⃣  CATEGORICAL SEARCH")
    print("=" * 70 + "\n")

    category_queries = [
        ["programming"],
        ["preferences"],
        ["technical", "programming"]
    ]

    for categories in category_queries:
        print(f"Categories: {categories}")
        results = await storage.search_categorical(user_id, categories, limit=5)

        if results:
            for memory in results:
                print(f"  - {memory.content}")
        else:
            print("  No results found")
        print()

    input("\nPress Enter to continue to semantic search...")

    # ===== 6. SEMANTIC SEARCH =====
    print("\n" + "=" * 70)
    print("6️⃣  SEMANTIC SEARCH (Vector Similarity)")
    print("=" * 70 + "\n")

    semantic_queries = [
        "What programming languages do I use?",
        "Where do I live?",
        "What are my work habits?"
    ]

    for query in semantic_queries:
        print(f"Query: \"{query}\"")

        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)

        # Search
        results = await storage.search_semantic(
            user_id,
            query_embedding,
            limit=3,
            threshold=0.6  # Lower threshold for demo
        )

        if results:
            for memory, similarity in results:
                print(f"  [{similarity:.3f}] {memory.content}")
        else:
            print("  No results found")
        print()

    input("\nPress Enter to see statistics...")

    # ===== 7. STATISTICS =====
    print("\n" + "=" * 70)
    print("7️⃣  STATISTICS")
    print("=" * 70 + "\n")

    # Storage statistics
    storage.print_statistics()

    # Embedding service statistics
    embedding_service.print_usage_stats()

    # Fact extractor statistics
    stats = fact_extractor.get_statistics()
    print("Fact Extractor:")
    print(f"  Total Extractions: {stats['total_extractions']}")
    print(f"  Total Facts:       {stats['total_facts_extracted']}")
    print(f"  Avg Facts/Msg:     {stats['avg_facts_per_extraction']:.1f}")
    print()

    # ===== COMPLETE =====
    print("=" * 70)
    print("✅ TEST COMPLETE!")
    print("=" * 70)
    print(f"""
Memory file: {storage.storage_path}

You can now:
1. Inspect the JSON file to see stored memories
2. Run this script again (it will load existing memories)
3. Try the PostgreSQL version when your database is set up
4. Build the web interface for interactive testing

Next steps:
- Set up PostgreSQL connection (see GETTING_STARTED.md)
- Run the full demo: poetry run python experiments/memory/examples/complete_demo.py
- Explore the code in experiments/memory/
    """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
