"""Type definitions for experimental memory system.

This module defines core data structures used throughout the memory system:
- Facts: Discrete pieces of information extracted from messages
- Search intents: Analyzed query intentions for routing
- Search results: Unified result format across search strategies
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID


class SearchStrategy(str, Enum):
    """Available search strategies."""
    SEMANTIC = "semantic"  # Vector similarity search
    KEYWORD = "keyword"  # BM25 full-text search
    CATEGORICAL = "categorical"  # Filter by categories
    TEMPORAL = "temporal"  # Time-based retrieval
    GRAPH = "graph"  # Relationship traversal
    HYBRID = "hybrid"  # Combination of strategies


class FactType(str, Enum):
    """Types of facts that can be extracted."""
    IDENTITY = "identity"  # Name, role, etc.
    LOCATION = "location"  # Geographic information
    PROFESSION = "profession"  # Job, career
    PREFERENCE = "preference"  # Likes, dislikes, habits
    PROJECT = "project"  # Work projects
    TECHNICAL = "technical"  # Tech stack, tools
    TIMELINE = "timeline"  # Dates, deadlines, goals
    RELATIONSHIP = "relationship"  # Connections to people/things
    SKILL = "skill"  # Abilities, expertise
    GOAL = "goal"  # Objectives, aspirations
    EMOTION = "emotion"  # Feelings, moods
    EXPERIENCE = "experience"  # Past events, history
    OTHER = "other"  # Uncategorized


@dataclass
class Fact:
    """Single extracted fact from a message.

    Represents a discrete, atomic piece of information extracted from
    a larger message using LLM analysis.

    Attributes:
        content: The fact itself (e.g., "Name is Jack")
        fact_type: Category of fact (identity, preference, etc.)
        confidence: Extraction confidence (0-1)
        source_span: Character indices in original message (start, end)
        metadata: Additional context (extraction method, timestamps, etc.)

    Example:
        >>> fact = Fact(
        ...     content="Prefers TypeScript over JavaScript",
        ...     fact_type=FactType.PREFERENCE,
        ...     confidence=0.95,
        ...     source_span=(45, 82)
        ... )
    """
    content: str
    fact_type: FactType = FactType.OTHER
    confidence: float = 1.0
    source_span: Optional[Tuple[int, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate fact data."""
        if not self.content or not self.content.strip():
            raise ValueError("Fact content cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.source_span:
            start, end = self.source_span
            if start < 0 or end < start:
                raise ValueError("Invalid source span")


@dataclass
class SearchIntent:
    """Analyzed query intent for smart routing.

    Represents the result of analyzing a user's search query to determine
    the best search strategy and extract relevant parameters.

    Attributes:
        strategy: Recommended search strategy
        confidence: Confidence in strategy selection (0-1)
        parameters: Extracted query parameters (dates, categories, etc.)
        explanation: Human-readable reasoning for strategy choice
        fallback_strategy: Alternative strategy if primary fails

    Example:
        >>> intent = SearchIntent(
        ...     strategy=SearchStrategy.TEMPORAL,
        ...     confidence=0.92,
        ...     parameters={"start_date": "2024-11-01", "end_date": "2024-11-07"},
        ...     explanation="Query contains temporal expression 'last week'"
        ... )
    """
    strategy: SearchStrategy
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    fallback_strategy: Optional[SearchStrategy] = None

    def __post_init__(self):
        """Validate search intent."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class SearchResult:
    """Unified search result format.

    Represents a single search result with associated metadata and scoring.

    Attributes:
        memory_id: UUID of the memory
        content: Memory content text
        score: Relevance score (higher is better, typically 0-1)
        memory_type: Type of memory (personal, project, task)
        categories: Auto-generated categories
        created_at: Timestamp of memory creation
        metadata: Additional memory metadata
        match_explanation: Why this result matched (optional)
    """
    memory_id: UUID
    content: str
    score: float
    memory_type: str
    categories: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    match_explanation: Optional[str] = None


@dataclass
class CategoryHierarchy:
    """Hierarchical category structure.

    Represents a category with its position in the hierarchy.

    Attributes:
        level_1: Broad category (personal, project, technical, etc.)
        level_2: Domain category (programming, timeline, preferences, etc.)
        level_3: Specific category (languages, frameworks, habits, etc.)
        level_4: Most specific (typescript, react, morning_routine, etc.)

    Example:
        >>> cat = CategoryHierarchy(
        ...     level_1="personal",
        ...     level_2="preferences",
        ...     level_3="programming",
        ...     level_4="typescript"
        ... )
        >>> cat.to_path()
        'personal/preferences/programming/typescript'
    """
    level_1: str
    level_2: Optional[str] = None
    level_3: Optional[str] = None
    level_4: Optional[str] = None

    def to_path(self) -> str:
        """Convert hierarchy to slash-separated path."""
        parts = [self.level_1]
        if self.level_2:
            parts.append(self.level_2)
        if self.level_3:
            parts.append(self.level_3)
        if self.level_4:
            parts.append(self.level_4)
        return "/".join(parts)

    def to_list(self) -> List[str]:
        """Convert hierarchy to list of categories."""
        result = [self.level_1]
        if self.level_2:
            result.append(self.level_2)
        if self.level_3:
            result.append(self.level_3)
        if self.level_4:
            result.append(self.level_4)
        return result

    @classmethod
    def from_list(cls, categories: List[str]) -> "CategoryHierarchy":
        """Create hierarchy from list of categories."""
        if not categories:
            raise ValueError("Categories list cannot be empty")
        return cls(
            level_1=categories[0],
            level_2=categories[1] if len(categories) > 1 else None,
            level_3=categories[2] if len(categories) > 2 else None,
            level_4=categories[3] if len(categories) > 3 else None,
        )


@dataclass
class ExtractionResult:
    """Result of fact extraction from a message.

    Attributes:
        facts: List of extracted facts
        original_message: The source message
        extraction_time_ms: Time taken to extract (milliseconds)
        model_used: LLM model used for extraction
        token_usage: OpenAI token usage statistics
    """
    facts: List[Fact]
    original_message: str
    extraction_time_ms: float
    model_used: str = "gpt-4o-mini"
    token_usage: Dict[str, int] = field(default_factory=dict)


@dataclass
class CategorizationResult:
    """Result of fact categorization.

    Attributes:
        categories: List of category paths
        hierarchy: Structured category hierarchy
        confidence: Categorization confidence (0-1)
        model_used: LLM model used
    """
    categories: List[str]
    hierarchy: Optional[CategoryHierarchy] = None
    confidence: float = 1.0
    model_used: str = "gpt-4o-mini"


@dataclass
class HybridSearchConfig:
    """Configuration for hybrid search strategy.

    Attributes:
        weights: Weight for each strategy (must sum to 1.0)
        min_results_per_strategy: Minimum results from each strategy
        rerank: Whether to re-rank combined results
        rerank_model: Model to use for re-ranking (if enabled)

    Example:
        >>> config = HybridSearchConfig(
        ...     weights={
        ...         SearchStrategy.SEMANTIC: 0.7,
        ...         SearchStrategy.KEYWORD: 0.3
        ...     }
        ... )
    """
    weights: Dict[SearchStrategy, float] = field(default_factory=dict)
    min_results_per_strategy: int = 3
    rerank: bool = False
    rerank_model: Optional[str] = None

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        if self.weights:
            total = sum(self.weights.values())
            if not (0.99 <= total <= 1.01):  # Allow small floating point error
                raise ValueError(f"Weights must sum to 1.0, got {total}")


@dataclass
class MemoryGraphNode:
    """Node in the memory knowledge graph.

    Attributes:
        memory_id: UUID of memory
        content: Memory content preview
        categories: Associated categories
        relationships: Dict of relationship_type -> List[target_memory_id]
        depth: Depth in graph traversal (0 = root)
    """
    memory_id: UUID
    content: str
    categories: List[str] = field(default_factory=list)
    relationships: Dict[str, List[UUID]] = field(default_factory=dict)
    depth: int = 0


@dataclass
class MemoryGraph:
    """Memory knowledge graph structure.

    Attributes:
        root: Root node
        nodes: All nodes in graph
        edges: List of (source_id, target_id, relationship_type, weight)
    """
    root: MemoryGraphNode
    nodes: Dict[UUID, MemoryGraphNode] = field(default_factory=dict)
    edges: List[Tuple[UUID, UUID, str, float]] = field(default_factory=list)

    def add_node(self, node: MemoryGraphNode):
        """Add node to graph."""
        self.nodes[node.memory_id] = node

    def add_edge(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: str,
        weight: float = 1.0
    ):
        """Add edge to graph."""
        self.edges.append((source_id, target_id, relationship_type, weight))

        # Update node relationships
        if source_id in self.nodes:
            node = self.nodes[source_id]
            if relationship_type not in node.relationships:
                node.relationships[relationship_type] = []
            if target_id not in node.relationships[relationship_type]:
                node.relationships[relationship_type].append(target_id)


# Common relationship types for memory graph
class RelationshipType(str, Enum):
    """Types of relationships between memories."""
    RELATED_TO = "related_to"  # General relationship
    PART_OF = "part_of"  # Hierarchical (child of)
    SUPPORTS = "supports"  # Evidence/reasoning
    CONTRADICTS = "contradicts"  # Conflicting information
    TEMPORAL_SEQUENCE = "temporal_sequence"  # Time-ordered
    CAUSES = "causes"  # Causal relationship
    SIMILAR_TO = "similar_to"  # Semantic similarity
    REFERENCES = "references"  # Citation/reference
