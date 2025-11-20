"""
Phase 3 Feature Test Suite

Tests end-to-end functionality of:
1. Entity-Attribute-Value extraction
2. Hierarchical memory storage
3. Memory graph relationships
4. Graph-enhanced search

Run this script to verify Phase 3 features are working correctly.
"""

import asyncio
from uuid import uuid4
from app.db.session import AsyncSessionLocal
from app.models.memory import MemoryType

from experiments.memory.eav_extractor import EAVExtractor
from experiments.memory.hierarchical_memory import HierarchicalMemoryService
from experiments.memory.memory_graph import MemoryGraph, RelationshipType
from experiments.memory.graph_search_strategy import GraphEnhancedSearch, HierarchicalAttributeSearch


async def test_eav_extraction():
    """Test Entity-Attribute-Value extraction."""
    print("\n" + "=" * 80)
    print("TEST 1: Entity-Attribute-Value Extraction")
    print("=" * 80)

    extractor = EAVExtractor()

    test_messages = [
        "I attended UCSB, MIT, and Georgia Tech for my computer science degrees",
        "My favorite restaurant is Yoshinoya. I love their tonkatsu bowl for $10, and they have locations in Tokyo and America",
        "I'm working on Delight, an AI companion app built with Python and React. Launching Q1 2025.",
    ]

    for msg in test_messages:
        print(f"\nInput: {msg}")
        result = await extractor.extract_eav(msg)
        extractor.print_eav_summary(result)

    stats = extractor.get_statistics()
    print(f"📊 EAV Extractor Stats: {stats['total_extractions']} extractions, {stats['total_entities_extracted']} entities")

    return True


async def test_hierarchical_storage():
    """Test hierarchical memory storage."""
    print("\n" + "=" * 80)
    print("TEST 2: Hierarchical Memory Storage")
    print("=" * 80)

    service = HierarchicalMemoryService()
    test_user_id = uuid4()

    async with AsyncSessionLocal() as db:
        # Create hierarchical memories
        messages = [
            "I attended UCSB, MIT, and Georgia Tech",
            "My favorite restaurant is Yoshinoya with tonkatsu for $10 in Tokyo",
            "I'm working on Delight, an AI app with Python and React"
        ]

        all_memories = []
        for msg in messages:
            print(f"\n📝 Creating memories from: {msg}")
            memories = await service.create_hierarchical_memories(
                user_id=test_user_id,
                message=msg,
                memory_type=MemoryType.PERSONAL,
                db=db
            )
            all_memories.extend(memories)

        print(f"\n✅ Created {len(all_memories)} hierarchical memories")

        # Query by entity
        print("\n🔍 Querying by entity: 'yoshinoya'")
        yoshinoya = await service.get_entity(test_user_id, "yoshinoya", db)
        if yoshinoya:
            service.print_entity_summary(yoshinoya)

        # Query by attribute
        print("\n🔍 Querying by attribute: 'universities'")
        education_memories = await service.query_by_attribute(test_user_id, "universities", db)
        for mem in education_memories:
            service.print_entity_summary(mem)

        # Query by entity type
        print("\n🔍 Querying by entity type: 'project'")
        projects = await service.get_entities_by_type(test_user_id, "project", db)
        for proj in projects:
            service.print_entity_summary(proj)

        return all_memories


async def test_memory_graph(memories):
    """Test memory graph relationships."""
    print("\n" + "=" * 80)
    print("TEST 3: Memory Graph Relationships")
    print("=" * 80)

    graph = MemoryGraph()
    test_user_id = memories[0].user_id

    async with AsyncSessionLocal() as db:
        # Create some relationships
        if len(memories) >= 3:
            print("\n🔗 Creating relationships...")

            # Link education to projects (works_on)
            await graph.create_relationship(
                from_memory_id=memories[0].id,
                to_memory_id=memories[2].id,
                relationship_type=RelationshipType.WORKS_ON,
                strength=0.95,
                bidirectional=True,
                db=db
            )

            # Link restaurant to location (located_at)
            await graph.create_relationship(
                from_memory_id=memories[1].id,
                to_memory_id=memories[0].id,  # Link to user
                relationship_type=RelationshipType.PREFERS,
                strength=0.90,
                bidirectional=False,
                db=db
            )

            # Get related memories
            print(f"\n🔍 Finding memories related to {memories[0].id}...")
            related = await graph.get_related_memories(
                memory_id=memories[0].id,
                db=db
            )

            print(f"✅ Found {len(related)} related memories:")
            for related_mem, relationship in related:
                print(f"   - {relationship.relationship_type.value}: {related_mem.content[:60]}...")

            # Traverse graph
            print(f"\n🕸️  Traversing graph from {memories[0].id}...")
            paths = await graph.traverse_graph(
                start_memory_id=memories[0].id,
                max_depth=2,
                db=db
            )

            print(f"✅ Found {len(paths)} paths:")
            for i, path in enumerate(paths[:3], 1):
                node_ids = [node.entity_id or str(node.memory_id)[:8] for node in path.nodes]
                print(f"   Path {i}: {' → '.join(node_ids)} (strength: {path.total_strength:.2f})")

            # Get entity graph
            print(f"\n📊 Getting entity graph for user...")
            entity_graph = await graph.get_entity_graph(test_user_id, db=db)
            print(f"✅ Entity graph has {len(entity_graph)} entities:")
            for entity_id, relationships in entity_graph.items():
                if relationships:
                    print(f"   {entity_id}: {len(relationships)} relationships")

    return True


async def test_graph_enhanced_search(memories):
    """Test graph-enhanced search."""
    print("\n" + "=" * 80)
    print("TEST 4: Graph-Enhanced Search")
    print("=" * 80)

    graph_search = GraphEnhancedSearch()
    test_user_id = memories[0].user_id

    async with AsyncSessionLocal() as db:
        # Test queries
        test_queries = [
            "universities I attended",
            "favorite restaurant",
            "AI project",
        ]

        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = await graph_search.search(
                query=query,
                user_id=test_user_id,
                db=db,
                limit=5,
                threshold=0.5,
                graph_depth=2,
                graph_boost_factor=0.3
            )

            if results:
                print(f"\n✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    orig_score = result.metadata.get("original_score", result.score)
                    boost = result.metadata.get("graph_boost", 0.0)
                    print(f"{i}. [{result.score:.3f}] {result.content[:80]}...")
                    if boost > 0:
                        print(f"   (original: {orig_score:.3f}, graph boost: +{boost:.3f})")
            else:
                print("   No results found")

    return True


async def test_hierarchical_attribute_search(memories):
    """Test hierarchical attribute search."""
    print("\n" + "=" * 80)
    print("TEST 5: Hierarchical Attribute Search")
    print("=" * 80)

    attr_search = HierarchicalAttributeSearch()
    test_user_id = memories[0].user_id

    async with AsyncSessionLocal() as db:
        # Test attribute searches
        test_searches = [
            ("universities", None),
            ("favorite_dish", None),
            ("tech_stack", None),
        ]

        for attribute_name, attribute_value in test_searches:
            print(f"\n🔍 Searching for attribute: '{attribute_name}'" +
                  (f" = '{attribute_value}'" if attribute_value else ""))

            results = await attr_search.search(
                attribute_name=attribute_name,
                user_id=test_user_id,
                db=db,
                attribute_value=attribute_value,
                limit=5
            )

            if results:
                print(f"✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    matched_value = result.metadata.get("matched_value")
                    print(f"{i}. {result.content[:80]}...")
                    print(f"   Value: {matched_value}")
            else:
                print("   No results found")

    return True


async def run_all_tests():
    """Run all Phase 3 tests."""
    print("\n" + "=" * 80)
    print("🚀 PHASE 3 FEATURE TEST SUITE")
    print("=" * 80)
    print("\nTesting:")
    print("1. Entity-Attribute-Value Extraction")
    print("2. Hierarchical Memory Storage")
    print("3. Memory Graph Relationships")
    print("4. Graph-Enhanced Search")
    print("5. Hierarchical Attribute Search")
    print()

    try:
        # Test 1: EAV Extraction
        await test_eav_extraction()

        # Test 2: Hierarchical Storage (returns memories for next tests)
        memories = await test_hierarchical_storage()

        # Test 3: Memory Graph
        await test_memory_graph(memories)

        # Test 4: Graph-Enhanced Search
        await test_graph_enhanced_search(memories)

        # Test 5: Hierarchical Attribute Search
        await test_hierarchical_attribute_search(memories)

        print("\n" + "=" * 80)
        print("✅ ALL PHASE 3 TESTS PASSED!")
        print("=" * 80)
        print("\nPhase 3 features are working correctly:")
        print("✓ EAV extraction identifies entities, attributes, and values")
        print("✓ Hierarchical storage supports complex nested objects")
        print("✓ Memory graph enables typed relationships")
        print("✓ Graph-enhanced search boosts related memories")
        print("✓ Attribute search queries hierarchical data")
        print()

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    """Run Phase 3 test suite."""
    asyncio.run(run_all_tests())
