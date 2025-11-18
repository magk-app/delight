# Graph-Based Hierarchical Memory Retrieval - Design Document

**Version:** 1.0.0
**Date:** 2025-11-18
**Status:** Implementation Ready

---

## Overview

This document describes the design and implementation of a graph-based hierarchical retrieval system for the Delight memory system. The graph structure complements the existing 3-tier memory architecture (PERSONAL, PROJECT, TASK) by organizing memories into a knowledge graph with nodes and relationships, enabling faster and more precise context retrieval.

---

## Problem Statement

The current flat memory storage with vector embeddings works well for small-scale retrieval, but faces challenges as the knowledge base grows:

1. **Scalability**: Searching all memories becomes expensive with large datasets
2. **Precision**: Semantic search may return irrelevant results across different contexts
3. **Ambiguity**: Same keywords can have different meanings in different domains
4. **Speed**: Full vector search over 10K+ memories takes >100ms
5. **Context**: No explicit relationship modeling between related information

---

## Solution: Hierarchical Knowledge Graph

Organize memories into a **directed graph** where:
- **Nodes** represent concepts, topics, projects, people, or categories
- **Edges** represent relationships between nodes (e.g., "subtopic of", "related to", "part of")
- **Memories** are associated with one or more nodes for contextual grouping

### Two-Step Retrieval Strategy

1. **Step 1 (Fast)**: Identify relevant graph nodes using keyword matching, metadata filters, or lightweight vector search
2. **Step 2 (Precise)**: Perform fine-grained vector similarity search only within memories associated with those nodes

This reduces search space by 10-100x for typical queries, improving both speed and precision.

---

## Architecture Design

### Database Schema

```
knowledge_nodes
├── id (UUID, PK)
├── user_id (UUID, FK → users.id)
├── node_type (ENUM: 'topic', 'project', 'person', 'category', 'event')
├── name (VARCHAR(255), indexed)
├── description (TEXT)
├── embedding (VECTOR(1536), nullable, for semantic node search)
├── metadata (JSONB, for flexible attributes)
├── importance_score (FLOAT, 0-1, for node ranking)
├── access_count (INTEGER, for popularity tracking)
├── created_at (TIMESTAMP WITH TIME ZONE)
├── updated_at (TIMESTAMP WITH TIME ZONE)
└── INDEXES:
    - ix_knowledge_nodes_user_id
    - ix_knowledge_nodes_node_type
    - ix_knowledge_nodes_name (for text search)
    - ix_knowledge_nodes_embedding (HNSW for semantic search)
    - ix_knowledge_nodes_importance_score

knowledge_edges
├── id (UUID, PK)
├── user_id (UUID, FK → users.id)
├── source_node_id (UUID, FK → knowledge_nodes.id)
├── target_node_id (UUID, FK → knowledge_nodes.id)
├── edge_type (ENUM: 'subtopic_of', 'related_to', 'part_of', 'depends_on', 'precedes')
├── weight (FLOAT, 0-1, relationship strength)
├── metadata (JSONB, for context-specific attributes)
├── created_at (TIMESTAMP WITH TIME ZONE)
└── INDEXES:
    - ix_knowledge_edges_user_id
    - ix_knowledge_edges_source_node_id
    - ix_knowledge_edges_target_node_id
    - ix_knowledge_edges_edge_type
    - UNIQUE(source_node_id, target_node_id, edge_type) for duplicate prevention

memory_node_associations
├── id (UUID, PK)
├── memory_id (UUID, FK → memories.id, CASCADE)
├── node_id (UUID, FK → knowledge_nodes.id, CASCADE)
├── relevance_score (FLOAT, 0-1, how relevant memory is to node)
├── created_at (TIMESTAMP WITH TIME ZONE)
└── INDEXES:
    - ix_memory_node_assoc_memory_id
    - ix_memory_node_assoc_node_id
    - UNIQUE(memory_id, node_id) for duplicate prevention
```

### Node Types

| Node Type  | Description | Examples |
|-----------|-------------|----------|
| **topic** | Subject matter or domain | "Machine Learning", "Time Management", "Python" |
| **project** | Specific goal or initiative | "Graduate Early from Georgia Tech", "Build Portfolio Website" |
| **person** | Individual mentioned in memories | "Professor Smith", "Advisor Jane", "Friend Alex" |
| **category** | Organizational bucket | "Academic", "Career", "Health", "Social" |
| **event** | Significant occurrence | "CS6200 Midterm", "Job Interview at Google", "Spring 2025 Semester" |

### Edge Types

| Edge Type | Description | Example |
|----------|-------------|---------|
| **subtopic_of** | Hierarchical relationship | "Neural Networks" → subtopic_of → "Machine Learning" |
| **related_to** | Symmetric association | "Time Management" ↔ related_to ↔ "Stress Reduction" |
| **part_of** | Component relationship | "Week 2 Milestone" → part_of → "Graduate Early Project" |
| **depends_on** | Dependency | "Apply to Grad School" → depends_on → "Complete Undergrad" |
| **precedes** | Temporal sequence | "Midterm" → precedes → "Final Exam" |

---

## Retrieval Algorithms

### Algorithm 1: Two-Step Hierarchical Retrieval

```python
async def hierarchical_search(user_id, query, memory_type=None, limit=5):
    """
    Two-step retrieval: find relevant nodes, then search memories within those nodes.

    Args:
        user_id: User identifier
        query: Natural language query
        memory_type: Optional filter (PERSONAL/PROJECT/TASK)
        limit: Max memories to return

    Returns:
        List of Memory objects with distance scores
    """
    # Step 1: Find relevant knowledge nodes (fast)
    relevant_nodes = await find_relevant_nodes(user_id, query, top_k=5)

    # Step 2: Get memories associated with those nodes
    candidate_memories = await get_memories_by_nodes(user_id, relevant_nodes, memory_type)

    # Step 3: Vector similarity search within candidates (precise)
    query_embedding = await generate_embedding(query)
    results = await vector_search_within_candidates(
        query_embedding,
        candidate_memories,
        limit
    )

    return results
```

### Algorithm 2: Graph-Guided Expansion

```python
async def graph_guided_search(user_id, query, expand_depth=1):
    """
    Start with directly relevant nodes, then expand via graph relationships.

    Args:
        user_id: User identifier
        query: Natural language query
        expand_depth: How many hops to traverse (0=direct only, 1=neighbors, 2=2-hop)

    Returns:
        Ordered list of memories with relevance scores
    """
    # Find initial nodes matching query
    initial_nodes = await find_relevant_nodes(user_id, query, top_k=3)

    # Expand via graph relationships (BFS traversal)
    expanded_nodes = await expand_nodes_via_edges(
        initial_nodes,
        depth=expand_depth,
        edge_types=['subtopic_of', 'related_to', 'part_of']
    )

    # Weight nodes by distance from initial matches
    weighted_nodes = assign_decay_weights(expanded_nodes, decay_factor=0.7)

    # Get memories from all nodes, weighted by node relevance
    memories = await get_weighted_memories(user_id, weighted_nodes)

    return memories
```

### Algorithm 3: Hybrid Search (Vector + Graph + Metadata)

```python
async def hybrid_search(user_id, query, filters=None, limit=5):
    """
    Combine vector similarity, graph structure, and metadata filters.

    Args:
        user_id: User identifier
        query: Natural language query
        filters: Dict of metadata filters (e.g., {'category': 'academic', 'stressor': True})
        limit: Max memories to return

    Returns:
        Memories ranked by composite score
    """
    query_embedding = await generate_embedding(query)

    # Parallel retrieval strategies
    vector_results = await vector_similarity_search(user_id, query_embedding, top_k=20)
    graph_results = await hierarchical_search(user_id, query, limit=20)

    # Combine with reciprocal rank fusion
    combined = reciprocal_rank_fusion([vector_results, graph_results])

    # Apply metadata filters
    if filters:
        combined = filter_by_metadata(combined, filters)

    # Re-rank by composite score
    final_results = composite_scoring(
        combined,
        weights={'vector_sim': 0.4, 'graph_relevance': 0.3, 'recency': 0.2, 'frequency': 0.1}
    )

    return final_results[:limit]
```

---

## Dynamic Graph Updates

### When to Update the Graph

| Trigger Event | Graph Update Action |
|--------------|---------------------|
| **User creates goal** | Create 'project' node, link to 'category' node |
| **User mentions new topic** | Create 'topic' node, extract relationships via LLM |
| **Memory references person** | Create 'person' node, associate memory |
| **User discusses stressor** | Link to existing category node, update importance |
| **User completes milestone** | Create 'event' node, link to project node |

### Auto-Organization via LLM

Use GPT-4o-mini to extract graph structure from memory content:

```python
async def extract_graph_entities(memory: Memory):
    """
    Use LLM to identify entities and relationships in memory content.

    Returns:
        {
            'entities': [{'type': 'topic', 'name': 'Neural Networks'}, ...],
            'relationships': [{'source': 'Neural Networks', 'target': 'ML', 'type': 'subtopic_of'}, ...]
        }
    """
    prompt = f"""
    Extract key entities and relationships from this memory:

    "{memory.content}"

    Return JSON with:
    - entities: [{{"type": "topic|project|person|category|event", "name": "...", "importance": 0-1}}]
    - relationships: [{{"source": "entity1", "target": "entity2", "type": "subtopic_of|related_to|part_of|depends_on|precedes"}}]
    """

    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
```

---

## Performance Optimization

### Caching Strategy

1. **Hot Node Cache**: Keep frequently accessed nodes in Redis (TTL: 1 hour)
2. **Graph Traversal Cache**: Cache BFS expansion results for common queries (TTL: 30 minutes)
3. **Node Embeddings**: Pre-compute and cache node embeddings for fast semantic search

### Query Optimization

1. **Lazy Loading**: Only load memory details when needed (not during node search)
2. **Batched Embedding Generation**: Generate embeddings for multiple nodes in single API call
3. **Index-Only Scans**: Use covering indexes to avoid table lookups where possible

### Scaling Considerations

| Dataset Size | Strategy |
|--------------|----------|
| **<1K nodes** | In-memory BFS traversal |
| **1K-10K nodes** | Index-optimized PostgreSQL queries |
| **>10K nodes** | Consider Neo4j or separate graph database |

---

## Integration with Existing System

### Backward Compatibility

- **Existing memories**: Continue to work without graph associations
- **Flat search fallback**: If no nodes found, fall back to full vector search
- **Gradual migration**: Organize memories into graph over time, not all at once

### API Changes

```python
# New endpoints (additive, not breaking)
POST /api/v1/knowledge/nodes          # Create knowledge node
GET  /api/v1/knowledge/nodes          # List nodes
POST /api/v1/knowledge/edges          # Create edge between nodes
GET  /api/v1/knowledge/graph          # Get subgraph for user

POST /api/v1/memories/search/hierarchical  # Two-step retrieval
POST /api/v1/memories/search/hybrid        # Vector + graph + metadata

# Enhanced existing endpoint
POST /api/v1/memories/search          # Add 'use_graph=true' parameter
```

---

## Testing Strategy

### Unit Tests

- Node and edge CRUD operations
- Association creation and deletion
- Graph traversal algorithms (BFS, DFS)
- Reciprocal rank fusion
- Composite scoring functions

### Integration Tests

- Two-step retrieval with real embeddings
- Graph expansion with cascading deletes
- Hybrid search with metadata filters
- LLM-based entity extraction accuracy

### Performance Tests

- Retrieval latency: <50ms for node search, <150ms for full hierarchical search
- Graph traversal: <100ms for 3-hop expansion on 10K nodes
- Index effectiveness: >90% index-only scans

---

## Cost Analysis

### Storage Overhead

| Component | Size per User | Notes |
|-----------|---------------|-------|
| Nodes | ~10 KB per node × 100 nodes = 1 MB | Typical user has 50-200 nodes |
| Edges | ~500 bytes per edge × 200 edges = 100 KB | Average 2-3 edges per node |
| Associations | ~100 bytes × 1000 = 100 KB | Most memories link to 1-3 nodes |
| **Total** | **~1.2 MB per user** | Negligible compared to memory content |

### Compute Overhead

| Operation | Cost Impact | Optimization |
|-----------|-------------|--------------|
| Node embedding | +$0.001/day | Batch generation, cache results |
| Graph traversal | +5-10ms latency | Index optimization, Redis caching |
| LLM entity extraction | +$0.005/memory | Run asynchronously, optional feature |
| **Total** | **~$0.006/user/day** | Acceptable for improved UX |

---

## Implementation Roadmap

### Phase 1: Core Models & Migrations (This PR)

- ✅ Design document (this file)
- Create `KnowledgeNode` model
- Create `KnowledgeEdge` model
- Create `MemoryNodeAssociation` model
- Alembic migration for new tables
- Unit tests for models

### Phase 2: Retrieval Service

- Implement `find_relevant_nodes()`
- Implement `hierarchical_search()`
- Implement `graph_guided_search()`
- Implement `hybrid_search()`
- Integration tests

### Phase 3: Dynamic Updates

- LLM-based entity extraction
- Auto-organization background worker
- Graph maintenance functions

### Phase 4: API & Frontend

- REST endpoints for graph operations
- Frontend graph visualization (optional)
- User-facing documentation

---

## References

- **Hierarchical Navigable Small World (HNSW)**: Current index for vector search
- **Reciprocal Rank Fusion**: Combining multiple retrieval strategies
- **LangChain Memory**: Graph-based memory patterns
- **Neo4j**: Reference graph database for scaling considerations

---

**Next Steps**: Proceed with Phase 1 implementation (models and migration).
