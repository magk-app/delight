# Chatbot Capabilities & Strategies

**Last Updated:** 2025-11-19

---

## Overview

The experimental chatbot is powered by a sophisticated memory system that combines:
- **LLM Intelligence**: GPT-4o-mini for natural conversation
- **Semantic Memory**: Vector embeddings for conceptual understanding
- **Structured Knowledge**: Graph-based fact storage
- **Multi-Modal Search**: 6 different search strategies

---

## Core Capabilities

### 1. Memory-Augmented Conversation

The chatbot doesn't just respond - it **remembers** and **contextualizes**.

**How It Works**:
```
User: "I love hiking in the mountains"

Chatbot Process:
1. Search existing memories for relevant context
   → Finds: "User enjoys outdoor activities" (0.82 relevance)
2. Generate response using retrieved context
   → "That's wonderful! I remember you enjoy outdoor activities..."
3. Extract facts from user's message
   → Fact 1: "User loves hiking"
   → Fact 2: "User prefers mountain hiking"
4. Store facts for future conversations
5. Link related facts in knowledge graph
```

**Why It Matters**:
- Conversations build on previous knowledge
- No need to repeat yourself
- Personalized responses based on your history

---

### 2. Intelligent Fact Extraction

The chatbot automatically identifies and stores discrete facts from complex messages.

**Example**:
```
User: "I'm Jack, a software developer in San Francisco. I'm working on Delight,
       an AI app built with Python and React. My goal is to launch by Q1 2025."

Extracted Facts:
1. Name is Jack (identity, 0.99 confidence)
2. Profession is software developer (profession, 0.95 confidence)
3. Located in San Francisco (location, 0.98 confidence)
4. Working on Delight project (project, 0.92 confidence)
5. Delight is an AI app (project, 0.97 confidence)
6. Tech stack includes Python (technical, 0.96 confidence)
7. Tech stack includes React (technical, 0.96 confidence)
8. Launch goal: Q1 2025 (timeline, 0.95 confidence)
```

**Fact Types**:
- **Identity**: Name, age, role
- **Location**: Geographic information
- **Profession**: Job, career, occupation
- **Preference**: Likes, dislikes, habits
- **Project**: Work projects, initiatives
- **Technical**: Tools, technologies, frameworks
- **Timeline**: Dates, deadlines, goals with timeframes
- **Relationship**: Connections to people/organizations
- **Skill**: Abilities, expertise, competencies
- **Goal**: Objectives, aspirations, targets
- **Emotion**: Feelings, moods, emotional states
- **Experience**: Past events, history, background

**Benefits**:
- Granular knowledge storage (one fact per memory)
- Easy retrieval of specific information
- Better search precision

---

### 3. Hierarchical Auto-Categorization

Every fact is automatically organized into a 4-level category hierarchy.

**Example**:
```
Fact: "Prefers TypeScript over JavaScript"

Categories:
Level 1 (Broad):     personal
Level 2 (Domain):    preferences
Level 3 (Specific):  programming
Level 4 (Detail):    typescript

Path: personal/preferences/programming/typescript
```

**Level 1 Options**:
- `personal`: Facts about the user
- `project`: Work projects, ventures
- `technical`: Technology, tools, programming
- `social`: Relationships, teams, communities
- `professional`: Career, job, industry
- `temporal`: Time-related (schedules, deadlines, goals)
- `experiential`: Past experiences, history
- `emotional`: Feelings, moods, emotions
- `physical`: Location, health, activities

**Benefits**:
- Organize thousands of facts logically
- Filter by topic ("Show me all programming facts")
- Browse knowledge like a file system

---

### 4. Six Search Strategies

The chatbot can search your memories in 6 different ways, automatically choosing the best strategy for each query.

#### **Strategy 1: Semantic Search** (Vector Similarity)

**Best For**: Conceptual queries, paraphrasing, related ideas

**How It Works**:
1. Convert query to 1536-dimensional embedding
2. Find memories with closest embeddings (cosine similarity)
3. Return top matches above threshold (default 0.7)

**Example Queries**:
- "What are my programming preferences?" → Finds facts about coding likes/dislikes
- "What do I care about?" → Finds values, interests, passions
- "My career goals" → Finds aspirations, objectives

**Technical**: Uses PostgreSQL pgvector extension with `<=>` operator

---

#### **Strategy 2: Keyword Search** (Full-Text BM25)

**Best For**: Specific terms, names, exact phrases

**How It Works**:
1. Parse query into search terms
2. Use PostgreSQL full-text search (BM25-like scoring)
3. Rank by term frequency and document relevance

**Example Queries**:
- "Python FastAPI TypeScript" → Finds memories containing these exact keywords
- "San Francisco office" → Finds location-specific facts
- "John Doe collaboration" → Finds references to specific person

**Technical**: Uses PostgreSQL `to_tsvector` + `ts_rank_cd`

---

#### **Strategy 3: Categorical Search**

**Best For**: Topic filtering, browsing by category

**How It Works**:
1. Extract categories from query
2. Filter memories whose metadata contains matching categories
3. Can match ANY category or ALL categories

**Example Queries**:
- "programming preferences" → Categories: [programming, preferences]
- "technical skills" → Categories: [technical, skills]
- "project goals" → Categories: [project, goals]

**Technical**: Uses PostgreSQL JSONB `?|` (contains any) or `?&` (contains all) operators

---

#### **Strategy 4: Temporal Search** (Time-Based)

**Best For**: Recency queries, date ranges

**How It Works**:
1. Parse time expression ("last week", "yesterday", "Q1 2025")
2. Filter memories by created_at timestamp
3. Return most recent matches

**Example Queries**:
- "What did I work on last week?" → Finds memories from past 7 days
- "Recent programming work" → Combines temporal + categorical
- "Yesterday's tasks" → Finds memories from previous day

**Technical**: Uses PostgreSQL `created_at >= (now() - interval)`

---

#### **Strategy 5: Graph Search** (Relationship Traversal)

**Best For**: Connected knowledge, related concepts

**How It Works**:
1. Start from a root memory (or find one matching query)
2. Traverse relationships stored in metadata
3. Breadth-first search up to max depth (default: 3)
4. Return all connected memories

**Example Queries**:
- "What's related to Delight project?" → Finds all linked project facts
- "Show connections to my work" → Traverses work-related graph
- "Similar ideas to X" → Finds semantically linked concepts

**Technical**: Uses metadata `relationships` field for graph edges

---

#### **Strategy 6: Hybrid Search** (Weighted Combination)

**Best For**: Complex multi-faceted queries

**How It Works**:
1. Analyze query to determine optimal strategy mix
2. Execute multiple strategies in parallel
3. Combine results with weighted scoring
4. Re-rank by combined score

**Example Queries**:
- "Recent programming preferences" → Temporal (0.4) + Semantic (0.4) + Categorical (0.2)
- "Latest AI project updates" → Temporal (0.5) + Categorical (0.3) + Keyword (0.2)

**Default Weights**: Semantic (0.7) + Keyword (0.3)

**Technical**: Merges result sets and normalizes scores

---

### Query Routing Examples

The chatbot uses LLM analysis to automatically select the best strategy:

```
Query: "What are my programming preferences?"
→ Strategy: HYBRID (Semantic 0.6 + Categorical 0.4)
→ Reasoning: Conceptual query requiring both semantic understanding and category filtering
```

```
Query: "Python FastAPI TypeScript"
→ Strategy: KEYWORD
→ Reasoning: Specific technical terms, best matched with keyword search
```

```
Query: "What did I work on last week?"
→ Strategy: TEMPORAL
→ Reasoning: Clear temporal expression "last week"
```

```
Query: "Show me technical facts"
→ Strategy: CATEGORICAL
→ Reasoning: Asking for topic/domain filtering
```

```
Query: "What's related to my Delight project?"
→ Strategy: GRAPH
→ Reasoning: Asking for relationships/connections
```

---

## Advanced Features

### 1. Confidence Scoring

Every extracted fact has a confidence score (0-1):
- **0.9-1.0**: Very confident (e.g., "Name is Jack")
- **0.7-0.9**: Confident (e.g., "Prefers TypeScript")
- **0.5-0.7**: Moderate (e.g., "Might be interested in AI")
- **<0.5**: Low confidence (filtered out by default)

**Usage**: Can filter by minimum confidence when querying

---

### 2. Fact Linking

Related facts are automatically linked in a knowledge graph:

```
Message: "I'm Jack, a developer in SF working on Delight with Python."

Created Facts:
[1] Name is Jack
[2] Profession is developer
[3] Located in San Francisco
[4] Working on Delight
[5] Uses Python

Graph Links:
[1] → related_to → [2, 3, 4, 5]
[2] → related_to → [1, 3, 4, 5]
[3] → related_to → [1, 2, 4, 5]
[4] → related_to → [1, 2, 3, 5]
[5] → related_to → [1, 2, 3, 4]
```

**Benefits**:
- Find related facts quickly
- Build knowledge clusters
- Traverse semantic networks

---

### 3. Memory Context Injection

The chatbot injects relevant memories into its system prompt:

```
System Prompt:
"You are a helpful AI assistant with access to the user's personal memories.

Relevant memories about the user:
- Prefers TypeScript over JavaScript (relevance: 0.89)
- Loves async programming (relevance: 0.85)
- Works late at night (relevance: 0.78)

Use the provided memories to give personalized, contextual responses..."
```

**Benefits**:
- Responses reflect your preferences
- AI "knows you" over time
- Continuity across sessions

---

### 4. Statistics Tracking

The system tracks comprehensive usage metrics:

**Memory Statistics**:
- Total memories created
- Facts extracted per message
- Average categorization confidence
- Memories by type (personal/project/task)
- Top categories

**Search Statistics**:
- Total searches performed
- Strategy usage distribution
- Average search latency
- Results per query

**Cost Tracking**:
- Total tokens used (OpenAI API)
- Cost by model (GPT-4o-mini, embeddings)
- Tokens per operation type

---

## Conversation Examples

### Example 1: Building Knowledge

```
User: I'm a TypeScript developer who loves functional programming.
Bot: Great! I'll remember that you're a TypeScript developer with a
     preference for functional programming.

✨ Memories Created:
- Uses TypeScript (technical/programming/typescript)
- Prefers functional programming (personal/preferences/programming_paradigms)

---

User: What programming languages do I use?
Bot: Based on what you've told me, you use TypeScript. You also mentioned
     that you love functional programming!

🧠 Memories Retrieved:
- Uses TypeScript (score: 0.92)
- Prefers functional programming (score: 0.85)
```

---

### Example 2: Project Tracking

```
User: I'm working on three projects: Delight (AI app), PersonalSite (portfolio),
      and OpenSourceLib (npm package).
Bot: Got it! I'll track these three projects for you.

✨ Memories Created:
- Working on Delight project (project/current_work/delight)
- Delight is an AI app (project/current_work/delight/ai)
- Working on PersonalSite project (project/current_work/personal_site)
- PersonalSite is a portfolio (project/current_work/personal_site/portfolio)
- Working on OpenSourceLib project (project/current_work/opensource_lib)
- OpenSourceLib is an npm package (project/current_work/opensource_lib/npm)

---

User: What are my current projects?
Bot: You're working on three projects:
     1. Delight - an AI app
     2. PersonalSite - your portfolio
     3. OpenSourceLib - an npm package

🧠 Memories Retrieved:
- Working on Delight project (score: 0.95)
- Delight is an AI app (score: 0.93)
- Working on PersonalSite project (score: 0.95)
- PersonalSite is a portfolio (score: 0.93)
- Working on OpenSourceLib project (score: 0.95)
- OpenSourceLib is an npm package (score: 0.93)
```

---

### Example 3: Timeline Tracking

```
User: I want to launch Delight by Q1 2025 and raise a seed round by Q2 2025.
Bot: I'll remember your timeline goals for Delight!

✨ Memories Created:
- Launch goal: Q1 2025 (temporal/goals/launch/q1_2025)
- Seed round goal: Q2 2025 (temporal/goals/fundraising/q2_2025)
- Project timeline for Delight (project/delight/timeline)

---

User: What are my upcoming deadlines?
Bot: Based on your goals:
     - Launch Delight by Q1 2025
     - Raise seed round by Q2 2025

🧠 Memories Retrieved:
- Launch goal: Q1 2025 (score: 0.98)
- Seed round goal: Q2 2025 (score: 0.96)
```

---

## Current Limitations & Future Improvements

### Current Limitations

1. **Redundant Storage**: Currently stores "User went to UCSB", "User went to MIT", "User went to Georgia Tech" as 3 separate facts
   - **Issue**: Inefficient for lists of related items
   - **Better**: Store as nodes with relationships (see proposed improvement below)

2. **No Deduplication**: May create duplicate memories for similar facts
   - Example: "Loves Python" and "Really enjoys Python programming" stored separately

3. **Static Categories**: 4-level hierarchy may not fit all fact types

4. **No Memory Editing**: Can only create or delete, not update

5. **Limited Graph Traversal**: Graph search requires explicit relationships

---

### Proposed Improvements

#### 1. **Entity-Relationship Storage** (for lists like schools, jobs, etc.)

**Current Problem**:
```
Fact 1: User went to UCSB
Fact 2: User went to MIT
Fact 3: User went to Georgia Tech

Storage: 3 separate memory records with embeddings
```

**Proposed Solution: Entity-Relationship Nodes**
```
Entity Node (User Profile):
{
  id: uuid-1,
  type: "person",
  name: "Jack",
  attributes: {
    profession: "developer",
    location: "San Francisco"
  }
}

Education Relationship:
{
  source: uuid-1 (Jack),
  target: uuid-2 (UCSB),
  relationship_type: "attended",
  metadata: {
    degree: "BS Computer Science",
    years: "2015-2019",
    order: 1
  }
}

Education Relationship:
{
  source: uuid-1 (Jack),
  target: uuid-3 (MIT),
  relationship_type: "attended",
  metadata: {
    degree: "MS AI",
    years: "2019-2021",
    order: 2
  }
}

Education Entity Nodes:
{
  id: uuid-2,
  type: "educational_institution",
  name: "UCSB",
  attributes: { location: "Santa Barbara, CA" }
}

{
  id: uuid-3,
  type: "educational_institution",
  name: "MIT",
  attributes: { location: "Cambridge, MA" }
}

Query: "Where did Jack go to school?"
→ Traverse education relationships
→ Return: [UCSB, MIT, Georgia Tech] in chronological order
```

**Benefits**:
- Single embedding for "education" concept
- Easy to add/remove schools
- Preserves order and metadata (degrees, years)
- More efficient storage (~70% reduction for lists)

**Implementation**:
```python
# New tables
entities (id, type, name, attributes_jsonb, embedding)
relationships (source_id, target_id, type, metadata_jsonb, weight)

# Query pattern
"SELECT e.name FROM entities e
 JOIN relationships r ON e.id = r.target_id
 WHERE r.source_id = :user_id AND r.type = 'attended'
 ORDER BY r.metadata->>'order'"
```

---

#### 2. **Prompt Optimization**

**Current Fact Extraction Prompt** (~800 tokens):
- Long system prompt with examples
- Repeated guidelines
- Verbose descriptions

**Optimized Version** (~400 tokens):
```
Extract discrete facts from user messages. Return JSON.

Fact types: identity, location, profession, preference, project, technical,
timeline, relationship, skill, goal, emotion, experience, other

Rules:
1. One fact = one piece of info
2. No duplicates or trivia
3. Preserve context (e.g., "Prefers X over Y" not just "Likes X")
4. Include source span [start, end]

Example:
Input: "I'm Jack, a dev in SF. Working on Delight with Python."
Output: [
  {"content": "Name is Jack", "type": "identity", "confidence": 0.99},
  {"content": "Profession is developer", "type": "profession", "confidence": 0.95},
  {"content": "Located in San Francisco", "type": "location", "confidence": 0.98},
  {"content": "Working on Delight", "type": "project", "confidence": 0.92},
  {"content": "Uses Python", "type": "technical", "confidence": 0.90}
]
```

**Savings**: ~50% token reduction = ~50% cost reduction for fact extraction

---

#### 3. **Smart Deduplication**

```python
async def find_similar_facts(new_fact: str, threshold=0.95) -> List[Memory]:
    """Find existing facts that are semantically identical"""
    embedding = await embed_text(new_fact)
    results = await semantic_search(embedding, threshold=threshold)
    return results

async def merge_or_create(new_fact: str):
    """Merge with existing or create new"""
    similar = await find_similar_facts(new_fact)

    if similar:
        # Update existing fact with higher confidence
        existing = similar[0]
        existing.confidence = max(existing.confidence, new_fact.confidence)
        existing.metadata['mentions'] += 1
        return existing
    else:
        # Create new fact
        return await create_memory(new_fact)
```

---

#### 4. **Memory Consolidation**

Periodically merge related memories:

```python
# Find all facts about "programming preferences"
facts = await search_memories(
    categories=["personal", "preferences", "programming"]
)

# Consolidate into structured summary
consolidated = {
    "languages": ["TypeScript", "Python", "Rust"],
    "paradigms": ["functional", "async"],
    "tools": ["FastAPI", "React", "PostgreSQL"],
    "preferences": {
        "TypeScript > JavaScript": 0.95,
        "async programming": 0.92
    }
}

# Store as single consolidated memory with links to source facts
```

---

## Performance Metrics

**Current System (per chat message)**:
- OpenAI API calls: 3-5 (chat, fact extraction, categorization × N facts)
- Database queries: 5-10 (search, create memories × N facts)
- Average latency: 2-4 seconds
- Average cost: $0.003-0.008 per message

**Optimized System (with proposed improvements)**:
- OpenAI API calls: 2-3 (50% reduction with prompt optimization)
- Database queries: 3-5 (40% reduction with entity-relationship model)
- Average latency: 1-2 seconds (50% faster)
- Average cost: $0.001-0.004 per message (50% cheaper)

---

## Summary

The experimental chatbot combines:
- ✅ **6 intelligent search strategies** (semantic, keyword, categorical, temporal, graph, hybrid)
- ✅ **Automatic fact extraction** (13 fact types)
- ✅ **Hierarchical categorization** (4-level taxonomy)
- ✅ **Graph-based knowledge linking**
- ✅ **Memory-augmented responses**
- ✅ **Comprehensive analytics**

**Next Steps**:
1. Implement entity-relationship storage for efficient list handling
2. Optimize prompts for 50% cost reduction
3. Add deduplication to prevent redundant memories
4. Build modern, minimalistic UI with icons (no emojis)
5. Add memory consolidation for better organization

---

**Questions? See `EXPERIMENTAL_TECHNICAL_DOCS.md` for full technical details.**
