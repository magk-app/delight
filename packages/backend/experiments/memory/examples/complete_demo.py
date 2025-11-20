"""Complete demonstration of the experimental memory system.

This script demonstrates all features:
1. Fact extraction from complex messages
2. Dynamic categorization
3. Embedding generation
4. Memory creation with 3-tier system
5. Multi-modal search (all 6 strategies)
6. Smart query routing
7. Visualization and statistics

Run with:
    cd packages/backend
    poetry run python experiments/memory/examples/complete_demo.py
"""

import asyncio
import uuid
from datetime import datetime

from experiments.database.connection import get_experiment_db, print_database_info
from experiments.memory.memory_service import MemoryService
from experiments.memory.types import SearchStrategy
from app.models.memory import MemoryType


# Test user ID (replace with actual user ID or create test user)
TEST_USER_ID = uuid.uuid4()


async def demo_fact_extraction():
    """Demonstrate fact extraction from complex messages."""
    print("\n" + "=" * 70)
    print("1️⃣  FACT EXTRACTION DEMO")
    print("=" * 70 + "\n")

    from experiments.memory.fact_extractor import FactExtractor

    extractor = FactExtractor()

    # Complex message with multiple facts
    message = """
    I'm Jack, a software developer based in San Francisco.
    I'm currently working on Delight, which is an AI companion app
    built with Python, React, and PostgreSQL. My goal is to launch
    by Q1 2025 and raise a seed round.

    I prefer TypeScript over JavaScript and love async programming.
    I usually work late at night and drink lots of coffee.

    I'm also interested in AI safety and have experience with
    LangChain and OpenAI APIs.
    """

    print(f"📝 Input Message ({len(message)} characters):\n")
    print(message)
    print("\n" + "-" * 70)

    # Extract facts
    result = await extractor.extract_facts(message)

    # Print results
    extractor.print_extraction_summary(result)

    # Show facts by type
    from experiments.memory.types import FactType

    print("📊 Facts by Type:\n")
    for fact_type in FactType:
        type_facts = extractor.get_facts_by_type(result.facts, fact_type)
        if type_facts:
            print(f"  {fact_type.value.upper()} ({len(type_facts)}):")
            for fact in type_facts:
                print(f"    - {fact.content} ({fact.confidence:.2f})")
            print()

    return result.facts


async def demo_categorization(facts):
    """Demonstrate dynamic categorization."""
    print("\n" + "=" * 70)
    print("2️⃣  DYNAMIC CATEGORIZATION DEMO")
    print("=" * 70 + "\n")

    from experiments.memory.categorizer import DynamicCategorizer

    categorizer = DynamicCategorizer()

    # Categorize a few sample facts
    sample_facts = facts[:5] if len(facts) >= 5 else facts

    for fact in sample_facts:
        result = await categorizer.categorize(fact.content)
        categorizer.print_categorization(fact.content, result)


async def demo_memory_creation():
    """Demonstrate memory creation with fact extraction."""
    print("\n" + "=" * 70)
    print("3️⃣  MEMORY CREATION DEMO")
    print("=" * 70 + "\n")

    service = MemoryService()

    # Complex message
    message = """
    I'm launching my startup in Q1 2025.
    It's an AI companion app called Delight, built with Python and React.
    I'm based in San Francisco and prefer async programming.
    My tech stack includes FastAPI, PostgreSQL, and OpenAI.
    """

    print(f"Creating memories from message:\n{message}\n")

    async with get_experiment_db() as db:
        memories = await service.create_memory_from_message(
            user_id=TEST_USER_ID,
            message=message,
            memory_type=MemoryType.PERSONAL,
            db=db,
            extract_facts=True,
            auto_categorize=True,
            generate_embeddings=True,
            link_facts=True
        )

        print(f"\n✅ Created {len(memories)} memories\n")

        for i, memory in enumerate(memories, 1):
            print(f"Memory {i}:")
            print(f"  Content: {memory.content}")
            print(f"  Categories: {memory.metadata.get('categories', [])}")
            print(f"  Hierarchy: {memory.metadata.get('category_hierarchy', 'N/A')}")
            print(f"  Has Embedding: {'Yes' if memory.embedding else 'No'}")
            print()

        return memories


async def demo_semantic_search():
    """Demonstrate semantic (vector similarity) search."""
    print("\n" + "=" * 70)
    print("4️⃣  SEMANTIC SEARCH DEMO")
    print("=" * 70 + "\n")

    service = MemoryService()

    queries = [
        "What are my programming preferences?",
        "Tell me about my projects",
        "What technology do I use?",
    ]

    async with get_experiment_db() as db:
        for query in queries:
            print(f"Query: \"{query}\"\n")

            results = await service.search_memories(
                user_id=TEST_USER_ID,
                query=query,
                db=db,
                override_strategy=SearchStrategy.SEMANTIC,
                limit=5
            )

            if results:
                print("Results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result.score:.3f}] {result.content}")
                    print(f"      Categories: {', '.join(result.categories)}")
                print()
            else:
                print("  No results found\n")


async def demo_keyword_search():
    """Demonstrate keyword (BM25) search."""
    print("\n" + "=" * 70)
    print("5️⃣  KEYWORD SEARCH DEMO")
    print("=" * 70 + "\n")

    service = MemoryService()

    queries = [
        "Python FastAPI",
        "TypeScript React",
        "San Francisco",
    ]

    async with get_experiment_db() as db:
        for query in queries:
            print(f"Query: \"{query}\"\n")

            results = await service.search_memories(
                user_id=TEST_USER_ID,
                query=query,
                db=db,
                override_strategy=SearchStrategy.KEYWORD,
                limit=5
            )

            if results:
                print("Results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result.score:.3f}] {result.content}")
                print()
            else:
                print("  No results found\n")


async def demo_auto_routing():
    """Demonstrate smart query routing."""
    print("\n" + "=" * 70)
    print("6️⃣  SMART QUERY ROUTING DEMO")
    print("=" * 70 + "\n")

    service = MemoryService()

    # Different types of queries
    queries = [
        "What are my programming preferences?",  # → Hybrid/Semantic
        "Python FastAPI",  # → Keyword
        "What did I work on recently?",  # → Temporal
        "technical facts",  # → Categorical
    ]

    async with get_experiment_db() as db:
        for query in queries:
            print(f"\n{'=' * 60}")
            print(f"Query: \"{query}\"")
            print('=' * 60)

            # Analyze query first (without searching)
            intent = await service.search_router.analyze_query(query)

            print(f"\n🤔 Analysis:")
            print(f"  Strategy: {intent.strategy.value}")
            print(f"  Confidence: {intent.confidence:.2f}")
            print(f"  Reasoning: {intent.explanation}")
            print(f"  Parameters: {intent.parameters}")

            # Execute search
            print(f"\n🔍 Searching...")
            results = await service.search_memories(
                user_id=TEST_USER_ID,
                query=query,
                db=db,
                auto_route=True,
                limit=3
            )

            if results:
                print(f"\n✅ Found {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result.score:.3f}] {result.content}")
                    print(f"      Type: {result.memory_type} | Categories: {', '.join(result.categories)}")
                print()
            else:
                print("\n  No results found\n")


async def demo_statistics():
    """Show comprehensive statistics."""
    print("\n" + "=" * 70)
    print("7️⃣  STATISTICS & ANALYTICS")
    print("=" * 70 + "\n")

    service = MemoryService()

    # Print service statistics
    service.print_statistics()

    # Print embedding service cost
    service.embedding_service.print_usage_stats()

    # Print search router usage
    service.search_router.print_statistics()


async def main():
    """Run complete demo."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "EXPERIMENTAL MEMORY SYSTEM DEMO" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")

    print("""
This demo showcases the complete second brain memory system:
- Intelligent fact extraction from complex messages
- Automatic hierarchical categorization
- Embedding generation for semantic search
- Multi-modal search strategies
- Smart query routing
""")

    # Check database connection
    await print_database_info()

    # Wait for user
    input("Press Enter to start the demo...")

    # Run demos
    try:
        # 1. Fact extraction
        facts = await demo_fact_extraction()
        input("\nPress Enter to continue to categorization...")

        # 2. Categorization
        await demo_categorization(facts)
        input("\nPress Enter to continue to memory creation...")

        # 3. Memory creation
        await demo_memory_creation()
        input("\nPress Enter to continue to semantic search...")

        # 4. Semantic search
        await demo_semantic_search()
        input("\nPress Enter to continue to keyword search...")

        # 5. Keyword search
        await demo_keyword_search()
        input("\nPress Enter to continue to auto-routing...")

        # 6. Auto-routing
        await demo_auto_routing()
        input("\nPress Enter to see statistics...")

        # 7. Statistics
        await demo_statistics()

        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE!")
        print("=" * 70)
        print("""
Next steps:
1. Try the web interface: poetry run python experiments/web/server.py
2. Use the CLI REPL: poetry run python experiments/cli/repl.py
3. Explore the code in experiments/memory/
4. Build your own agents using this memory system!
        """)

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
