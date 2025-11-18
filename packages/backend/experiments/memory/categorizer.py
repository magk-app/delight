"""Dynamic fact categorization using LLM and clustering.

This module provides automatic hierarchical categorization of facts using:
1. LLM-based category generation (GPT-4o-mini with structured output)
2. Hierarchical category structure (4 levels: broad → specific)
3. Embedding-based clustering for grouping similar facts

Example:
    Input: "Prefers TypeScript over JavaScript"

    Output:
        Level 1: personal
        Level 2: preferences
        Level 3: programming
        Level 4: typescript

    As path: "personal/preferences/programming/typescript"
    As list: ["personal", "preferences", "programming", "typescript"]
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# Optional dependency for clustering
try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not available. Clustering features disabled.")

from experiments.config import get_config
from experiments.memory.embedding_service import EmbeddingService
from experiments.memory.types import (
    CategoryHierarchy,
    CategorizationResult,
    Fact
)


# Pydantic model for structured categorization
class CategorizationResponse(BaseModel):
    """Structured response from LLM categorization."""
    level_1: str = Field(description="Broad category (personal, project, technical, social, etc.)")
    level_2: str = Field(description="Domain category (preferences, timeline, skills, etc.)")
    level_3: Optional[str] = Field(default=None, description="Specific subcategory")
    level_4: Optional[str] = Field(default=None, description="Most specific category")
    confidence: float = Field(description="Categorization confidence (0-1)", ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of category selection")


class DynamicCategorizer:
    """Automatic hierarchical fact categorization.

    This categorizer generates multi-level categories for facts to enable:
    - Hierarchical organization of knowledge
    - Categorical search and filtering
    - Knowledge graph construction
    - Fact clustering and grouping

    The categorizer uses:
    - LLM analysis for context-aware categorization
    - Hierarchical structure (4 levels max)
    - Confidence scoring
    - Batch processing for efficiency

    Example:
        >>> categorizer = DynamicCategorizer()
        >>> result = await categorizer.categorize("I love Python programming")
        >>> result.categories
        ['personal', 'preferences', 'programming', 'python']
        >>> result.hierarchy.to_path()
        'personal/preferences/programming/python'
    """

    # System prompt for categorization
    SYSTEM_PROMPT = """You are an expert at categorizing facts into hierarchical categories.

Your task is to assign each fact to a 4-level category hierarchy:
- Level 1: Broad category
- Level 2: Domain category
- Level 3: Specific subcategory (optional)
- Level 4: Most specific (optional)

Common Level 1 Categories:
- personal: Facts about the user (identity, preferences, habits)
- project: Work projects, initiatives, ventures
- technical: Technology, tools, programming
- social: Relationships, teams, communities
- professional: Career, job, industry
- temporal: Time-related (schedules, deadlines, goals)
- experiential: Past experiences, history
- emotional: Feelings, moods, emotions
- physical: Location, health, activities

Guidelines:
1. **Be Specific**: Use all 4 levels when possible
2. **Consistent Naming**: Use lowercase, underscores for multi-word
3. **Context-Aware**: Consider the fact's semantic meaning
4. **User-Centric**: Level 1 should reflect user's perspective

Examples:

Fact: "Name is Jack"
→ personal / identity / name / jack

Fact: "Prefers TypeScript over JavaScript"
→ personal / preferences / programming / typescript

Fact: "Working on Delight AI app"
→ project / current_work / delight / ai_companion

Fact: "Uses FastAPI for backend"
→ technical / frameworks / backend / fastapi

Fact: "Launch goal: Q1 2025"
→ temporal / goals / launch / q1_2025

Fact: "Based in San Francisco"
→ personal / location / city / san_francisco

Fact: "Loves async programming"
→ personal / preferences / programming_paradigms / async

Now categorize the given fact."""

    def __init__(self):
        """Initialize categorizer."""
        self.config = get_config()

        if not self.config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.model = self.config.chat_model

        # Embedding service for clustering
        self.embedding_service = EmbeddingService()

        # Statistics
        self.total_categorizations = 0
        self.total_tokens_used = 0

    async def categorize(
        self,
        fact: str,
        context: Optional[str] = None
    ) -> CategorizationResult:
        """Generate hierarchical categories for a fact.

        Args:
            fact: Fact text to categorize
            context: Optional additional context to help categorization

        Returns:
            CategorizationResult with hierarchy and metadata

        Example:
            >>> result = await categorizer.categorize(
            ...     "Prefers working late at night",
            ...     context="User is a software developer"
            ... )
            >>> result.hierarchy.to_path()
            'personal/preferences/work_schedule/night'
        """
        if not fact or not fact.strip():
            raise ValueError("Fact cannot be empty")

        try:
            # Prepare prompt
            user_message = f"Categorize this fact:\n\n{fact}"
            if context:
                user_message += f"\n\nContext: {context}"

            # Call OpenAI with structured output
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format=CategorizationResponse,
                temperature=0.2  # Lower temperature for consistency
            )

            # Parse response
            categorization = response.choices[0].message.parsed

            # Build hierarchy
            hierarchy = CategoryHierarchy(
                level_1=categorization.level_1,
                level_2=categorization.level_2,
                level_3=categorization.level_3,
                level_4=categorization.level_4
            )

            # Track statistics
            self.total_categorizations += 1
            self.total_tokens_used += response.usage.total_tokens

            return CategorizationResult(
                categories=hierarchy.to_list(),
                hierarchy=hierarchy,
                confidence=categorization.confidence,
                model_used=self.model
            )

        except Exception as e:
            print(f"❌ Error categorizing fact: {e}")
            raise

    async def batch_categorize(
        self,
        facts: List[str],
        show_progress: bool = True
    ) -> List[CategorizationResult]:
        """Categorize multiple facts.

        Args:
            facts: List of fact texts
            show_progress: Print progress updates

        Returns:
            List of categorization results in same order

        Example:
            >>> facts = ["I love Python", "Based in SF", "Works late"]
            >>> results = await categorizer.batch_categorize(facts)
            >>> len(results) == len(facts)
            True
        """
        if not facts:
            return []

        results = []

        for i, fact in enumerate(facts):
            if show_progress and (i + 1) % 10 == 0:
                print(f"🔄 Categorizing: {i + 1}/{len(facts)}...")

            try:
                result = await self.categorize(fact)
                results.append(result)
            except Exception as e:
                print(f"❌ Error categorizing fact {i + 1}: {e}")
                # Add empty result to maintain order
                results.append(CategorizationResult(
                    categories=["uncategorized"],
                    confidence=0.0
                ))

        if show_progress:
            print(f"✅ Categorized {len(facts)} facts")

        return results

    async def categorize_fact_object(
        self,
        fact: Fact
    ) -> CategorizationResult:
        """Categorize a Fact object (with metadata).

        Args:
            fact: Fact object to categorize

        Returns:
            CategorizationResult

        Example:
            >>> from experiments.memory.types import Fact, FactType
            >>> fact = Fact("Loves TypeScript", FactType.PREFERENCE)
            >>> result = await categorizer.categorize_fact_object(fact)
        """
        # Use fact type as context
        context = f"This is a {fact.fact_type.value} fact"

        # Add original message as context if available
        if "original_message" in fact.metadata:
            context += f". Original message: {fact.metadata['original_message']}"

        return await self.categorize(fact.content, context=context)

    async def cluster_facts(
        self,
        facts: List[Fact],
        n_clusters: int = 5,
        show_progress: bool = True
    ) -> Dict[str, List[Fact]]:
        """Cluster similar facts using embeddings.

        This method uses K-means clustering on fact embeddings to
        automatically group related facts together.

        Args:
            facts: List of Fact objects
            n_clusters: Number of clusters to create
            show_progress: Print progress

        Returns:
            Dictionary mapping cluster names to fact lists

        Example:
            >>> clusters = await categorizer.cluster_facts(facts, n_clusters=3)
            >>> for cluster_name, cluster_facts in clusters.items():
            ...     print(f"{cluster_name}: {len(cluster_facts)} facts")
        """
        if not SKLEARN_AVAILABLE:
            print("⚠️  Clustering requires scikit-learn. Install with: poetry add scikit-learn")
            # Return all facts in one group
            return {"all_facts": facts}

        if not facts:
            return {}

        if len(facts) < n_clusters:
            n_clusters = len(facts)

        if show_progress:
            print(f"🔄 Clustering {len(facts)} facts into {n_clusters} groups...")

        # Generate embeddings
        fact_texts = [f.content for f in facts]
        embeddings = await self.embedding_service.batch_embed(
            fact_texts,
            show_progress=show_progress
        )

        # Convert to numpy array
        embeddings_array = np.array([e for e in embeddings if e is not None])

        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings_array)

        # Group facts by cluster
        clusters = defaultdict(list)
        for fact, label in zip(facts, cluster_labels):
            clusters[f"cluster_{label}"].append(fact)

        # Generate cluster names using LLM
        if show_progress:
            print("🔄 Generating cluster names...")

        named_clusters = {}
        for cluster_id, cluster_facts in clusters.items():
            # Sample facts from cluster for naming
            sample_size = min(5, len(cluster_facts))
            sample_facts = cluster_facts[:sample_size]
            sample_text = "\n".join([f"- {f.content}" for f in sample_facts])

            # Generate cluster name
            try:
                cluster_name = await self._generate_cluster_name(sample_text)
                named_clusters[cluster_name] = cluster_facts
            except:
                # Fall back to numeric name if naming fails
                named_clusters[cluster_id] = cluster_facts

        if show_progress:
            print(f"✅ Created {len(named_clusters)} clusters")

        return named_clusters

    async def _generate_cluster_name(self, sample_facts: str) -> str:
        """Generate a descriptive name for a cluster of facts.

        Args:
            sample_facts: Sample facts from the cluster

        Returns:
            Short descriptive cluster name
        """
        prompt = f"""Generate a short, descriptive name (2-4 words) for a cluster of related facts.

Sample facts from cluster:
{sample_facts}

Respond with just the cluster name, nothing else. Examples:
- "Programming Preferences"
- "Project Goals"
- "Location Information"
- "Technical Skills"
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20
        )

        name = response.choices[0].message.content.strip()
        return name

    def get_statistics(self) -> dict:
        """Get categorization statistics.

        Returns:
            Dictionary with usage stats
        """
        return {
            "total_categorizations": self.total_categorizations,
            "total_tokens_used": self.total_tokens_used,
            "avg_tokens_per_categorization": (
                self.total_tokens_used / self.total_categorizations
                if self.total_categorizations > 0
                else 0
            )
        }

    def print_categorization(self, fact: str, result: CategorizationResult):
        """Print formatted categorization result.

        Args:
            fact: Original fact text
            result: Categorization result
        """
        print("\n" + "=" * 60)
        print("🏷️  Fact Categorization")
        print("=" * 60)
        print(f"Fact: {fact}")
        print()
        print("Hierarchy:")
        if result.hierarchy:
            print(f"  Level 1 (Broad):    {result.hierarchy.level_1}")
            print(f"  Level 2 (Domain):   {result.hierarchy.level_2}")
            if result.hierarchy.level_3:
                print(f"  Level 3 (Specific): {result.hierarchy.level_3}")
            if result.hierarchy.level_4:
                print(f"  Level 4 (Detail):   {result.hierarchy.level_4}")
            print()
            print(f"Path: {result.hierarchy.to_path()}")
        print()
        print(f"Confidence: {result.confidence:.2f}")
        print("=" * 60 + "\n")


# Convenience function
async def quick_categorize(fact: str) -> List[str]:
    """Quick categorization without creating categorizer instance.

    Args:
        fact: Fact to categorize

    Returns:
        List of categories (hierarchical)

    Example:
        >>> from experiments.memory.categorizer import quick_categorize
        >>> categories = await quick_categorize("I love Python")
        >>> categories
        ['personal', 'preferences', 'programming', 'python']
    """
    categorizer = DynamicCategorizer()
    result = await categorizer.categorize(fact)
    return result.categories


if __name__ == "__main__":
    """Example usage and testing."""
    import asyncio

    async def main():
        categorizer = DynamicCategorizer()

        # Test single categorization
        facts_to_test = [
            "Name is Jack",
            "Prefers TypeScript over JavaScript",
            "Working on Delight AI companion app",
            "Uses FastAPI for backend development",
            "Launch goal: Q1 2025",
            "Based in San Francisco",
            "Loves async programming",
            "Drinks lots of coffee",
            "Works late at night",
            "Has experience with LangChain",
        ]

        print("Testing Dynamic Categorization\n")

        for fact in facts_to_test:
            result = await categorizer.categorize(fact)
            categorizer.print_categorization(fact, result)

        # Test batch categorization
        print("\n" + "=" * 60)
        print("Testing Batch Categorization")
        print("=" * 60 + "\n")

        results = await categorizer.batch_categorize(facts_to_test)

        print("Summary of Categories:")
        for fact, result in zip(facts_to_test, results):
            path = result.hierarchy.to_path() if result.hierarchy else "uncategorized"
            print(f"  {fact[:40]:40} → {path}")

        # Statistics
        stats = categorizer.get_statistics()
        print(f"\n\nStatistics:")
        print(f"  Total Categorizations: {stats['total_categorizations']}")
        print(f"  Total Tokens: {stats['total_tokens_used']}")
        print(f"  Avg Tokens/Categorization: {stats['avg_tokens_per_categorization']:.1f}")

    asyncio.run(main())
