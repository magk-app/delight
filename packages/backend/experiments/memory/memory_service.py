"""High-level memory service for the experimental second brain system.

This service provides a unified API that orchestrates:
- Fact extraction from complex messages
- Automatic hierarchical categorization
- Embedding generation for semantic search
- 3-tier memory storage (Personal/Project/Task)
- Intelligent search with automatic routing

Example:
    >>> service = MemoryService()
    >>>
    >>> # Create memories from complex message
    >>> memories = await service.create_memory_from_message(
    ...     user_id=user_id,
    ...     message="I'm Jack, working on Delight with Python. Launch goal: Q1 2025.",
    ...     memory_type=MemoryType.PERSONAL,
    ...     extract_facts=True,
    ...     auto_categorize=True
    ... )
    >>> # Creates multiple memories (one per fact), each with embeddings and categories
    >>>
    >>> # Search with automatic routing
    >>> results = await service.search_memories(
    ...     user_id=user_id,
    ...     query="What are my programming preferences?",
    ...     auto_route=True
    ... )
"""

import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.memory import Memory, MemoryCollection, MemoryType
from experiments.config import get_config
from experiments.memory.fact_extractor import FactExtractor
from experiments.memory.categorizer import DynamicCategorizer
from experiments.memory.embedding_service import EmbeddingService
from experiments.memory.search_router import SearchRouter
from experiments.memory.types import SearchResult, SearchStrategy


class MemoryService:
    """Complete memory management with fact extraction and intelligent search.

    This service is the main entry point for the experimental memory system.
    It orchestrates all components to provide a simple, powerful API.

    Features:
    - Create memories from messages with automatic fact extraction
    - Auto-categorize facts into hierarchical categories
    - Generate embeddings for semantic search
    - 3-tier memory management (Personal/Project/Task)
    - Intelligent search with automatic strategy selection
    - Graph relationship management
    - Memory analytics and statistics

    Example:
        >>> service = MemoryService()
        >>>
        >>> # Create memory with all features
        >>> memories = await service.create_memory_from_message(
        ...     user_id=user_id,
        ...     message="Complex message with multiple facts...",
        ...     memory_type=MemoryType.PERSONAL,
        ...     extract_facts=True,      # Extract discrete facts
        ...     auto_categorize=True,     # Auto-categorize each fact
        ...     generate_embeddings=True  # Generate embeddings
        ... )
        >>>
        >>> # Search intelligently
        >>> results = await service.search_memories(
        ...     user_id=user_id,
        ...     query="programming preferences",
        ...     auto_route=True  # Automatically selects best strategy
        ... )
    """

    def __init__(self):
        """Initialize memory service with all components."""
        self.config = get_config()

        # Initialize components
        self.fact_extractor = FactExtractor()
        self.categorizer = DynamicCategorizer()
        self.embedding_service = EmbeddingService()
        self.search_router = SearchRouter()

        # Statistics
        self.total_memories_created = 0
        self.total_facts_extracted = 0
        self.total_searches = 0

    async def create_memory_from_message(
        self,
        user_id: UUID,
        message: str,
        memory_type: MemoryType,
        db: AsyncSession,
        project_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        extract_facts: bool = True,
        auto_categorize: bool = True,
        generate_embeddings: bool = True,
        link_facts: bool = True
    ) -> List[Memory]:
        """Create memory/memories from a message with optional fact extraction.

        This is the main method for creating memories. It can either:
        1. Store the message as-is (extract_facts=False)
        2. Extract multiple facts and store each separately (extract_facts=True)

        Args:
            user_id: User ID
            message: Message text
            memory_type: Type of memory (PERSONAL, PROJECT, TASK)
            db: Database session
            project_id: Optional project ID for PROJECT memories
            session_id: Optional session ID for TASK memories
            extract_facts: Extract discrete facts from message
            auto_categorize: Auto-categorize facts
            generate_embeddings: Generate embeddings for semantic search
            link_facts: Create graph relationships between extracted facts

        Returns:
            List of created Memory objects

        Example:
            >>> # Single memory (no fact extraction)
            >>> memories = await service.create_memory_from_message(
            ...     user_id=user_id,
            ...     message="Working on the backend today",
            ...     memory_type=MemoryType.TASK,
            ...     db=session,
            ...     extract_facts=False
            ... )
            >>> len(memories)
            1
            >>>
            >>> # Multiple memories (with fact extraction)
            >>> memories = await service.create_memory_from_message(
            ...     user_id=user_id,
            ...     message="I'm Jack, a developer in SF working on AI.",
            ...     memory_type=MemoryType.PERSONAL,
            ...     db=session,
            ...     extract_facts=True,
            ...     auto_categorize=True
            ... )
            >>> len(memories)
            4  # Name, profession, location, project
        """
        if self.config.read_only_mode:
            raise RuntimeError("Cannot create memories in read-only mode")

        print(f"\n🔄 Creating memory from message ({len(message)} chars)...")

        # Get or create memory collection
        collection = await self._get_or_create_collection(
            user_id=user_id,
            memory_type=memory_type,
            project_id=project_id,
            session_id=session_id,
            db=db
        )

        memories_created = []

        if extract_facts:
            # Extract discrete facts
            print("🔍 Extracting facts...")
            extraction_result = await self.fact_extractor.extract_facts(message)

            if not extraction_result.facts:
                print("⚠️  No facts extracted, storing message as-is")
                # Fall back to single memory
                memory = await self._create_single_memory(
                    content=message,
                    collection_id=collection.id,
                    auto_categorize=auto_categorize,
                    generate_embeddings=generate_embeddings,
                    db=db
                )
                memories_created.append(memory)
            else:
                print(f"✅ Extracted {len(extraction_result.facts)} facts")
                self.total_facts_extracted += len(extraction_result.facts)

                # Create memory for each fact
                for i, fact in enumerate(extraction_result.facts):
                    print(f"  📝 Fact {i+1}/{len(extraction_result.facts)}: {fact.content}")

                    memory = await self._create_single_memory(
                        content=fact.content,
                        collection_id=collection.id,
                        auto_categorize=auto_categorize,
                        generate_embeddings=generate_embeddings,
                        metadata={
                            "fact_type": fact.fact_type.value,
                            "confidence": fact.confidence,
                            "original_message": message,
                            "extraction_method": "llm_structured"
                        },
                        db=db
                    )

                    memories_created.append(memory)

                # Link facts together in graph
                if link_facts and len(memories_created) > 1:
                    print("🔗 Linking facts in graph...")
                    await self._link_memories_as_related(memories_created, db)

        else:
            # Store message as single memory
            memory = await self._create_single_memory(
                content=message,
                collection_id=collection.id,
                auto_categorize=auto_categorize,
                generate_embeddings=generate_embeddings,
                db=db
            )
            memories_created.append(memory)

        self.total_memories_created += len(memories_created)
        print(f"✅ Created {len(memories_created)} memories\n")

        return memories_created

    async def _create_single_memory(
        self,
        content: str,
        collection_id: UUID,
        auto_categorize: bool,
        generate_embeddings: bool,
        db: AsyncSession,
        metadata: Optional[dict] = None
    ) -> Memory:
        """Create a single memory with categorization and embedding.

        Args:
            content: Memory content
            collection_id: Collection ID
            auto_categorize: Generate categories
            generate_embeddings: Generate embedding
            db: Database session
            metadata: Optional metadata dict

        Returns:
            Created Memory object
        """
        if metadata is None:
            metadata = {}

        # Auto-categorize
        if auto_categorize:
            result = await self.categorizer.categorize(content)
            metadata["categories"] = result.categories
            metadata["category_hierarchy"] = result.hierarchy.to_path() if result.hierarchy else None
            metadata["categorization_confidence"] = result.confidence

        # Generate embedding
        embedding = None
        if generate_embeddings:
            embedding = await self.embedding_service.embed_text(content)

        # Create memory
        memory = Memory(
            id=uuid.uuid4(),
            collection_id=collection_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        return memory

    async def _get_or_create_collection(
        self,
        user_id: UUID,
        memory_type: MemoryType,
        project_id: Optional[UUID],
        session_id: Optional[UUID],
        db: AsyncSession
    ) -> MemoryCollection:
        """Get existing collection or create new one.

        Args:
            user_id: User ID
            memory_type: Memory type
            project_id: Optional project ID
            session_id: Optional session ID
            db: Database session

        Returns:
            MemoryCollection object
        """
        # Build collection name
        if memory_type == MemoryType.PERSONAL:
            name = f"personal_{user_id}"
        elif memory_type == MemoryType.PROJECT and project_id:
            name = f"project_{project_id}"
        elif memory_type == MemoryType.TASK and session_id:
            name = f"task_{session_id}"
        else:
            name = f"{memory_type.value}_{user_id}_{datetime.now().strftime('%Y%m%d')}"

        # Try to find existing collection
        stmt = select(MemoryCollection).where(
            MemoryCollection.user_id == user_id,
            MemoryCollection.name == name
        )
        result = await db.execute(stmt)
        collection = result.scalar_one_or_none()

        if collection:
            return collection

        # Create new collection
        collection = MemoryCollection(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            memory_type=memory_type,
            metadata={
                "project_id": str(project_id) if project_id else None,
                "session_id": str(session_id) if session_id else None,
                "created_at": datetime.now().isoformat()
            }
        )

        db.add(collection)
        await db.commit()
        await db.refresh(collection)

        return collection

    async def _link_memories_as_related(
        self,
        memories: List[Memory],
        db: AsyncSession
    ):
        """Create 'related_to' relationships between memories.

        Args:
            memories: List of memories to link
            db: Database session
        """
        # Link all memories to each other as related
        for memory in memories:
            if "relationships" not in memory.metadata:
                memory.metadata["relationships"] = {}

            # Add all other memories as related
            memory.metadata["relationships"]["related_to"] = [
                str(m.id) for m in memories if m.id != memory.id
            ]

        await db.commit()

    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        db: AsyncSession,
        auto_route: bool = True,
        override_strategy: Optional[SearchStrategy] = None,
        limit: int = 10,
        memory_types: Optional[List[MemoryType]] = None
    ) -> List[SearchResult]:
        """Search memories with intelligent routing.

        Args:
            user_id: User ID
            query: Search query
            db: Database session
            auto_route: Automatically select best strategy
            override_strategy: Force specific strategy
            limit: Maximum results
            memory_types: Optional filter by memory types

        Returns:
            List of SearchResult

        Example:
            >>> # Auto-routed search
            >>> results = await service.search_memories(
            ...     user_id=user_id,
            ...     query="programming preferences",
            ...     db=session
            ... )
            >>>
            >>> # Force keyword search
            >>> results = await service.search_memories(
            ...     user_id=user_id,
            ...     query="Python FastAPI",
            ...     db=session,
            ...     override_strategy=SearchStrategy.KEYWORD
            ... )
        """
        self.total_searches += 1

        # Convert memory types to strings
        type_filter = [mt.value for mt in memory_types] if memory_types else None

        # Use search router
        results = await self.search_router.search(
            query=query,
            user_id=user_id,
            db=db,
            auto_route=auto_route,
            override_strategy=override_strategy,
            limit=limit,
            memory_types=type_filter
        )

        return results

    def get_statistics(self) -> dict:
        """Get service usage statistics.

        Returns:
            Dictionary with comprehensive stats
        """
        return {
            "total_memories_created": self.total_memories_created,
            "total_facts_extracted": self.total_facts_extracted,
            "total_searches": self.total_searches,
            "avg_facts_per_extraction": (
                self.total_facts_extracted / self.total_memories_created
                if self.total_memories_created > 0
                else 0
            ),
            "fact_extractor": self.fact_extractor.get_statistics(),
            "categorizer": self.categorizer.get_statistics(),
            "embedding_service": self.embedding_service.get_usage_stats(),
            "search_router": self.search_router.get_statistics()
        }

    def print_statistics(self):
        """Print formatted statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("📊 Memory Service - Comprehensive Statistics")
        print("=" * 70)
        print(f"Memories Created:    {stats['total_memories_created']}")
        print(f"Facts Extracted:     {stats['total_facts_extracted']}")
        print(f"Searches Performed:  {stats['total_searches']}")
        print(f"Avg Facts/Memory:    {stats['avg_facts_per_extraction']:.2f}")
        print()

        print("Component Statistics:")
        print("-" * 70)

        # Fact extractor
        fe_stats = stats['fact_extractor']
        print(f"  Fact Extractor:")
        print(f"    Extractions:     {fe_stats['total_extractions']}")
        print(f"    Tokens Used:     {fe_stats['total_tokens_used']:,}")

        # Categorizer
        cat_stats = stats['categorizer']
        print(f"  Categorizer:")
        print(f"    Categorizations: {cat_stats['total_categorizations']}")
        print(f"    Tokens Used:     {cat_stats['total_tokens_used']:,}")

        # Embedding service
        emb_stats = stats['embedding_service']
        print(f"  Embedding Service:")
        print(f"    Requests:        {emb_stats['total_requests']:,}")
        print(f"    Tokens Used:     {emb_stats['total_tokens']:,}")
        print(f"    Cost (USD):      ${emb_stats['total_cost_usd']:.4f}")

        # Search router
        search_stats = stats['search_router']
        print(f"  Search Router:")
        print(f"    Total Searches:  {search_stats['total_searches']}")
        print(f"    Strategy Usage:")
        for strategy, count in search_stats['strategy_usage'].items():
            if count > 0:
                print(f"      {strategy:15} {count}")

        print("=" * 70 + "\n")


if __name__ == "__main__":
    """Example usage and testing (requires database)."""
    print("""
Memory Service Module
=====================

This is the main entry point for the experimental memory system.

Example Usage:
    from experiments.memory.memory_service import MemoryService
    from app.db.session import get_db
    from app.models.memory import MemoryType

    service = MemoryService()

    # Create memories from complex message
    async with get_db() as db:
        memories = await service.create_memory_from_message(
            user_id=user_id,
            message='''
                I'm Jack, a software developer in San Francisco.
                Working on Delight AI app with Python and React.
                Launch goal is Q1 2025.
            ''',
            memory_type=MemoryType.PERSONAL,
            db=db,
            extract_facts=True,
            auto_categorize=True
        )

        print(f"Created {len(memories)} memories")

        # Search
        results = await service.search_memories(
            user_id=user_id,
            query="What are my programming preferences?",
            db=db,
            auto_route=True
        )

        for result in results:
            print(f"[{result.score:.2f}] {result.content}")

        # Print statistics
        service.print_statistics()

Features:
- Automatic fact extraction from complex messages
- Hierarchical categorization
- Embedding generation
- 3-tier memory storage (Personal/Project/Task)
- Intelligent search routing
- Graph relationship management
- Comprehensive statistics tracking

See MemoryService class docstring for complete API documentation.
    """)
