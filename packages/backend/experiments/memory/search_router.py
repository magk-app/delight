"""Smart query routing for automatic search strategy selection.

This module analyzes user queries using LLM to determine the best search strategy:
- Semantic: Conceptual/abstract queries
- Keyword: Specific terms/phrases
- Categorical: Topic/category filtering
- Temporal: Time-based queries
- Graph: Relationship queries
- Hybrid: Complex multi-faceted queries

The router extracts query parameters (dates, categories, keywords) and provides
a unified search interface that automatically picks the optimal strategy.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from experiments.config import get_config
from experiments.memory.search_strategies import (
    SemanticSearch,
    KeywordSearch,
    CategoricalSearch,
    TemporalSearch,
    GraphSearch,
    HybridSearch
)
from experiments.memory.types import SearchIntent, SearchStrategy, SearchResult, HybridSearchConfig


# Pydantic model for structured query analysis
class QueryAnalysisResponse(BaseModel):
    """LLM response for query intent analysis."""
    strategy: str = Field(
        description="Best search strategy: semantic, keyword, categorical, temporal, graph, or hybrid"
    )
    confidence: float = Field(description="Confidence in strategy selection (0-1)", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of why this strategy was chosen")

    # Extracted parameters
    keywords: Optional[List[str]] = Field(default=None, description="Extracted keywords for keyword search")
    categories: Optional[List[str]] = Field(default=None, description="Extracted categories for categorical search")
    time_expression: Optional[str] = Field(default=None, description="Time expression like '1 week', 'last month'")
    relationship_focus: Optional[str] = Field(default=None, description="Entity to find relationships for")

    # Hybrid configuration
    hybrid_strategies: Optional[List[str]] = Field(
        default=None,
        description="List of strategies to combine for hybrid search"
    )
    hybrid_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Weights for each strategy in hybrid search"
    )


class SearchRouter:
    """Intelligent query analysis and search routing.

    This router uses GPT-4o-mini to analyze queries and automatically
    select the best search strategy, extracting relevant parameters
    along the way.

    Example:
        >>> router = SearchRouter()
        >>> results = await router.search(
        ...     query="What programming languages do I prefer?",
        ...     user_id=user_id,
        ...     db=session,
        ...     auto_route=True
        ... )
        >>> # Automatically uses semantic + categorical search
    """

    # System prompt for query analysis
    SYSTEM_PROMPT = """You are an expert at analyzing search queries and selecting the best retrieval strategy.

Available strategies:
1. **semantic**: Vector similarity search (best for conceptual/abstract queries)
   - Examples: "What are my goals?", "programming preferences", "career aspirations"

2. **keyword**: BM25 full-text search (best for specific terms/names)
   - Examples: "Python FastAPI", "San Francisco", "TypeScript React"

3. **categorical**: Filter by categories (best for topic/domain filtering)
   - Examples: "show me programming facts", "technical preferences", "project work"

4. **temporal**: Time-based retrieval (best for recency/date queries)
   - Examples: "last week", "recent work", "Q1 2025", "yesterday"

5. **graph**: Relationship traversal (best for connected knowledge)
   - Examples: "related to Delight project", "connected to my work", "similar ideas"

6. **hybrid**: Weighted combination (best for complex multi-faceted queries)
   - Examples: "recent programming decisions", "latest AI project updates"

Instructions:
- Analyze the query intent
- Select the single best strategy (or hybrid for complex queries)
- Extract relevant parameters (keywords, categories, time expressions)
- Provide confidence score (0-1)
- Explain your reasoning briefly

For hybrid searches:
- List which strategies to combine
- Provide weights that sum to 1.0 (e.g., {"semantic": 0.7, "keyword": 0.3})

Examples:

Query: "What are my programming preferences?"
→ Strategy: hybrid
   Reasoning: Conceptual query requiring both semantic understanding and category filtering
   Hybrid: ["semantic", "categorical"]
   Weights: {"semantic": 0.6, "categorical": 0.4}
   Categories: ["programming", "preferences"]

Query: "Python FastAPI TypeScript"
→ Strategy: keyword
   Reasoning: Specific technical terms, best matched with keyword search
   Keywords: ["Python", "FastAPI", "TypeScript"]

Query: "What did I work on last week?"
→ Strategy: temporal
   Reasoning: Clear temporal expression "last week"
   Time Expression: "1 week"

Query: "What's related to my Delight project?"
→ Strategy: graph
   Reasoning: Asking for relationships/connections
   Relationship Focus: "Delight project"

Now analyze the user's query."""

    def __init__(self):
        """Initialize search router."""
        self.config = get_config()

        if not self.config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.model = self.config.chat_model

        # Initialize all search strategies
        self.semantic = SemanticSearch()
        self.keyword = KeywordSearch()
        self.categorical = CategoricalSearch()
        self.temporal = TemporalSearch()
        self.graph = GraphSearch()
        self.hybrid = HybridSearch()

        # Statistics
        self.total_searches = 0
        self.strategy_usage = {strategy: 0 for strategy in SearchStrategy}

    async def analyze_query(self, query: str) -> SearchIntent:
        """Analyze query to determine best search strategy.

        Args:
            query: User search query

        Returns:
            SearchIntent with strategy and parameters

        Example:
            >>> intent = await router.analyze_query(
            ...     "What programming languages do I like?"
            ... )
            >>> intent.strategy
            SearchStrategy.HYBRID
            >>> intent.parameters
            {'categories': ['programming', 'preferences']}
        """
        try:
            # Call OpenAI with structured output
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze this query:\n\n{query}"}
                ],
                response_format=QueryAnalysisResponse,
                temperature=0.3
            )

            # Parse response
            analysis = response.choices[0].message.parsed

            # Convert to SearchStrategy enum
            try:
                strategy = SearchStrategy(analysis.strategy.lower())
            except ValueError:
                # Default to semantic if unknown
                strategy = SearchStrategy.SEMANTIC

            # Build parameters dict
            parameters = {}

            if analysis.keywords:
                parameters["keywords"] = analysis.keywords

            if analysis.categories:
                parameters["categories"] = analysis.categories

            if analysis.time_expression:
                parameters["time_expression"] = analysis.time_expression

            if analysis.relationship_focus:
                parameters["relationship_focus"] = analysis.relationship_focus

            if analysis.hybrid_strategies and analysis.hybrid_weights:
                parameters["hybrid_strategies"] = analysis.hybrid_strategies
                parameters["hybrid_weights"] = analysis.hybrid_weights

            # Create SearchIntent
            return SearchIntent(
                strategy=strategy,
                confidence=analysis.confidence,
                parameters=parameters,
                explanation=analysis.reasoning,
                fallback_strategy=(
                    SearchStrategy.SEMANTIC
                    if strategy != SearchStrategy.SEMANTIC
                    else SearchStrategy.KEYWORD
                )
            )

        except Exception as e:
            print(f"❌ Error analyzing query: {e}")
            # Fall back to semantic search
            return SearchIntent(
                strategy=SearchStrategy.SEMANTIC,
                confidence=0.5,
                explanation=f"Error in analysis, defaulting to semantic search: {e}"
            )

    async def search(
        self,
        query: str,
        user_id: UUID,
        db: AsyncSession,
        auto_route: bool = True,
        override_strategy: Optional[SearchStrategy] = None,
        limit: int = 10,
        memory_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Main search interface with automatic routing.

        Args:
            query: Search query
            user_id: User ID
            db: Database session
            auto_route: Automatically analyze and route query
            override_strategy: Force specific strategy (ignores auto_route)
            limit: Maximum results
            memory_types: Optional filter by memory types

        Returns:
            List of SearchResult

        Example:
            >>> # Automatic routing
            >>> results = await router.search(
            ...     query="recent programming work",
            ...     user_id=user_id,
            ...     db=session
            ... )

            >>> # Force specific strategy
            >>> results = await router.search(
            ...     query="Python FastAPI",
            ...     user_id=user_id,
            ...     db=session,
            ...     override_strategy=SearchStrategy.KEYWORD
            ... )
        """
        self.total_searches += 1

        # Determine strategy
        if override_strategy:
            strategy = override_strategy
            parameters = {}
            print(f"🔍 Using override strategy: {strategy.value}")
        elif auto_route:
            # Analyze query
            print(f"🤔 Analyzing query: \"{query}\"")
            intent = await self.analyze_query(query)
            strategy = intent.strategy
            parameters = intent.parameters
            print(f"✅ Selected strategy: {strategy.value} (confidence: {intent.confidence:.2f})")
            print(f"   Reasoning: {intent.explanation}")
        else:
            # Default to semantic
            strategy = SearchStrategy.SEMANTIC
            parameters = {}

        # Track strategy usage
        self.strategy_usage[strategy] += 1

        # Execute search based on strategy
        try:
            if strategy == SearchStrategy.SEMANTIC:
                results = await self.semantic.search(
                    query=query,
                    user_id=user_id,
                    db=db,
                    limit=limit,
                    memory_types=memory_types
                )

            elif strategy == SearchStrategy.KEYWORD:
                results = await self.keyword.search(
                    query=query,
                    user_id=user_id,
                    db=db,
                    limit=limit,
                    memory_types=memory_types
                )

            elif strategy == SearchStrategy.CATEGORICAL:
                categories = parameters.get("categories", [query])
                results = await self.categorical.search(
                    categories=categories,
                    user_id=user_id,
                    db=db,
                    limit=limit,
                    memory_types=memory_types
                )

            elif strategy == SearchStrategy.TEMPORAL:
                time_expr = parameters.get("time_expression")
                results = await self.temporal.search(
                    user_id=user_id,
                    db=db,
                    relative_time=time_expr,
                    limit=limit,
                    memory_types=memory_types
                )

            elif strategy == SearchStrategy.GRAPH:
                # Graph search requires a root memory ID
                # For now, we fall back to semantic
                print("⚠️  Graph search requires root memory ID, falling back to semantic")
                results = await self.semantic.search(
                    query=query,
                    user_id=user_id,
                    db=db,
                    limit=limit,
                    memory_types=memory_types
                )

            elif strategy == SearchStrategy.HYBRID:
                # Build hybrid config
                hybrid_weights = parameters.get("hybrid_weights", {
                    "semantic": 0.7,
                    "keyword": 0.3
                })

                # Convert string keys to SearchStrategy enums
                weights = {}
                for strat_str, weight in hybrid_weights.items():
                    try:
                        weights[SearchStrategy(strat_str)] = weight
                    except ValueError:
                        pass

                config = HybridSearchConfig(weights=weights)

                results = await self.hybrid.search(
                    query=query,
                    user_id=user_id,
                    db=db,
                    config=config,
                    limit=limit,
                    memory_types=memory_types
                )

            else:
                # Unknown strategy, fall back to semantic
                results = await self.semantic.search(
                    query=query,
                    user_id=user_id,
                    db=db,
                    limit=limit,
                    memory_types=memory_types
                )

            print(f"📊 Found {len(results)} results")
            return results

        except Exception as e:
            print(f"❌ Search error: {e}")
            raise

    def get_statistics(self) -> dict:
        """Get router usage statistics.

        Returns:
            Dictionary with search stats
        """
        return {
            "total_searches": self.total_searches,
            "strategy_usage": {
                strategy.value: count
                for strategy, count in self.strategy_usage.items()
            }
        }

    def print_statistics(self):
        """Print formatted statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("📊 Search Router - Usage Statistics")
        print("=" * 60)
        print(f"Total Searches: {stats['total_searches']}")
        print()
        print("Strategy Usage:")
        for strategy, count in stats['strategy_usage'].items():
            if count > 0:
                percentage = (count / stats['total_searches'] * 100) if stats['total_searches'] > 0 else 0
                print(f"  {strategy:15} {count:5} ({percentage:5.1f}%)")
        print("=" * 60 + "\n")


# Convenience function
async def quick_search(
    query: str,
    user_id: UUID,
    db: AsyncSession,
    limit: int = 10
) -> List[SearchResult]:
    """Quick search with automatic routing.

    Args:
        query: Search query
        user_id: User ID
        db: Database session
        limit: Maximum results

    Returns:
        List of SearchResult

    Example:
        >>> from experiments.memory.search_router import quick_search
        >>> results = await quick_search("programming preferences", user_id, db)
    """
    router = SearchRouter()
    return await router.search(query, user_id, db, limit=limit)


if __name__ == "__main__":
    """Example usage and testing."""
    print("""
Search Router Module
====================

This module provides intelligent query analysis and automatic search routing.

Example Usage:
    router = SearchRouter()

    # Analyze query (without executing search)
    intent = await router.analyze_query("What are my programming preferences?")
    print(f"Strategy: {intent.strategy}")
    print(f"Reasoning: {intent.explanation}")

    # Search with automatic routing
    results = await router.search(
        query="recent programming work",
        user_id=user_id,
        db=session
    )

    # Override strategy
    results = await router.search(
        query="Python FastAPI",
        user_id=user_id,
        db=session,
        override_strategy=SearchStrategy.KEYWORD
    )

Query Examples and Expected Routing:
    "What are my programming preferences?"
    → Hybrid (semantic + categorical)

    "Python FastAPI TypeScript"
    → Keyword (specific terms)

    "What did I work on last week?"
    → Temporal (time expression)

    "Show me technical facts"
    → Categorical (domain filtering)

    "What's related to Delight project?"
    → Graph (relationship query)

    "recent AI programming decisions"
    → Hybrid (temporal + categorical + semantic)

The router automatically:
- Analyzes query intent
- Selects optimal strategy
- Extracts parameters (keywords, categories, dates)
- Executes search
- Returns unified results

See SearchRouter class docstring for more details.
    """)
