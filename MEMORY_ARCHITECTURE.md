# Memory Architecture Specification

**Version:** 2.0
**Date:** 2025-11-19
**Status:** Design Proposal

---

## Overview

This document specifies the enhanced 4-level memory hierarchy system and memory linking/graph relationships for the Delight AI companion platform.

**Current Issues:**
1. Flat memory structure - all memories at same level
2. Inefficient multi-value fact storage (e.g., "favorite cuisine: Italian", "favorite cuisine: Japanese" = 2 separate memories)
3. No entity relationships/links (e.g., can't link "Jack" → "Tokyo" when user says "I love Tokyo")
4. Difficult to query related concepts across memory graph

**Proposed Solution:**
- 4-level hierarchical taxonomy
- Entity-centric storage with attributes
- Graph-based memory linking
- Efficient multi-value attribute handling

---

## 4-Level Memory Hierarchy

### Level 1: Domain Categories (Top Level)

**Purpose:** Major categorical domains that organize all knowledge

**Categories:**
1. **personal** - Identity, preferences, habits, characteristics
2. **project** - Work, initiatives, goals, tasks
3. **technical** - Technologies, tools, frameworks, languages
4. **social** - Relationships, people, teams, organizations
5. **professional** - Career, skills, education, experience
6. **temporal** - Schedules, deadlines, timelines, events
7. **experiential** - Past events, experiences, memories, history
8. **emotional** - Feelings, moods, fears, joys, emotions
9. **physical** - Location, places, health, fitness, environment

**Database Schema:**
```sql
CREATE TYPE domain_category AS ENUM (
  'personal',
  'project',
  'technical',
  'social',
  'professional',
  'temporal',
  'experiential',
  'emotional',
  'physical'
);
```

**Example:**
- "I love Italian food" → `personal`
- "Working on Delight AI app" → `project`
- "Fear of public speaking" → `emotional`

---

### Level 2: Topics/Subcategories

**Purpose:** Specific topics within each domain

**Examples by Domain:**

| Domain | Topics |
|--------|--------|
| personal | food, music, hobbies, style, habits |
| project | delight, side_projects, open_source |
| technical | programming_languages, frameworks, tools, platforms |
| social | friends, family, colleagues, mentors |
| professional | skills, education, certifications |
| temporal | schedules, deadlines, milestones |
| experiential | travels, achievements, failures |
| emotional | fears, joys, anxieties, aspirations |
| physical | locations, gyms, offices, home |

**Database Schema:**
```sql
CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain domain_category NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(domain, name),
  INDEX idx_domain_topics (domain, name)
);
```

**Example:**
- Domain: `personal`, Topic: `food`
- Domain: `emotional`, Topic: `fears`
- Domain: `technical`, Topic: `programming_languages`

---

### Level 3: Entities (Objects)

**Purpose:** Specific objects/entities with attributes

**Entity Types:**
- Concrete objects (restaurants, people, places, tools)
- Abstract concepts (emotions, skills, goals)
- Can have multiple attributes
- Attributes can be multi-valued

**Database Schema:**
```sql
CREATE TABLE entities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  name VARCHAR(200) NOT NULL,
  entity_type VARCHAR(50), -- restaurant, person, place, tool, skill, etc.

  -- Flexible attribute storage
  attributes JSONB DEFAULT '{}',

  -- Metadata
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_user_entities (user_id, topic_id),
  INDEX idx_entity_name (name),
  INDEX gin_attributes (attributes)
);
```

**Attributes Structure (JSONB):**
```json
{
  "favorite_dishes": ["beef bowl", "tempura", "ramen"],
  "price_range": "$$",
  "last_visited": "2025-01-15",
  "rating": 4.5,
  "tags": ["japanese", "fast-food", "comfort"]
}
```

**Examples:**

**Example 1: Restaurant**
```json
{
  "domain": "personal",
  "topic": "food.restaurants",
  "entity": {
    "name": "Yoshinoya",
    "entity_type": "restaurant",
    "attributes": {
      "cuisine": "Japanese",
      "favorite_dishes": ["beef bowl", "chicken teriyaki"],
      "price_range": "$$",
      "location": "multiple",
      "frequency": "weekly"
    }
  }
}
```

**Example 2: Person**
```json
{
  "domain": "social",
  "topic": "friends",
  "entity": {
    "name": "Sarah",
    "entity_type": "person",
    "attributes": {
      "relationship": "college friend",
      "met_at": "MIT",
      "common_interests": ["AI", "hiking", "cooking"],
      "last_contact": "2025-01-10"
    }
  }
}
```

**Example 3: Programming Language**
```json
{
  "domain": "technical",
  "topic": "programming_languages",
  "entity": {
    "name": "Python",
    "entity_type": "programming_language",
    "attributes": {
      "proficiency": "expert",
      "years_experience": 5,
      "favorite_features": ["async/await", "list comprehensions", "type hints"],
      "use_cases": ["backend", "data_science", "scripting"]
    }
  }
}
```

**Example 4: Fear (Emotional)**
```json
{
  "domain": "emotional",
  "topic": "fears",
  "entity": {
    "name": "talking_to_girls",
    "entity_type": "social_anxiety",
    "attributes": {
      "severity": "moderate",
      "triggers": ["approaching strangers", "romantic interest"],
      "coping_strategies": ["practice with friends", "online dating"],
      "origin": "high school rejection"
    }
  }
}
```

---

### Level 4: Facts/Relationships

**Purpose:** Atomic facts, comparisons, relationships between entities

**Fact Types:**
1. **Attribute Facts** - Properties of entities
2. **Relationship Facts** - Connections between entities
3. **Comparison Facts** - Preferences, rankings
4. **Temporal Facts** - Events, changes over time

**Database Schema:**
```sql
CREATE TYPE fact_type AS ENUM (
  'attribute',
  'relationship',
  'comparison',
  'temporal',
  'event'
);

CREATE TABLE facts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Subject entity
  subject_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,

  -- Fact type and content
  fact_type fact_type NOT NULL,
  content TEXT NOT NULL,

  -- For relationships: target entity
  target_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
  relationship_type VARCHAR(100), -- loves, fears, prefers, works_with, etc.

  -- For comparisons
  comparison_operator VARCHAR(20), -- greater_than, less_than, prefers_over, etc.

  -- Embeddings for semantic search
  embedding vector(1536),

  -- Metadata
  confidence FLOAT DEFAULT 1.0,
  source VARCHAR(100), -- conversation, explicit, inferred
  extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  verified BOOLEAN DEFAULT FALSE,

  INDEX idx_user_facts (user_id, fact_type),
  INDEX idx_subject_entity (subject_entity_id),
  INDEX idx_target_entity (target_entity_id),
  INDEX idx_relationship (relationship_type)
);
```

**Examples:**

**Example 1: Attribute Fact**
```json
{
  "fact_type": "attribute",
  "subject_entity": "Jack",
  "content": "Jack is a software developer",
  "relationship_type": "profession"
}
```

**Example 2: Relationship Fact**
```json
{
  "fact_type": "relationship",
  "subject_entity": "Jack",
  "target_entity": "Tokyo",
  "content": "Jack loves Tokyo",
  "relationship_type": "loves"
}
```

**Example 3: Comparison Fact**
```json
{
  "fact_type": "comparison",
  "subject_entity": "Jack",
  "target_entity": "TypeScript",
  "content": "Jack prefers TypeScript over JavaScript",
  "relationship_type": "prefers",
  "comparison_operator": "prefers_over",
  "metadata": {
    "alternative": "JavaScript"
  }
}
```

**Example 4: Fear Relationship**
```json
{
  "fact_type": "relationship",
  "subject_entity": "Jack",
  "target_entity": "talking_to_girls",
  "content": "Jack has a fear of talking to girls",
  "relationship_type": "fears"
}
```

---

## Memory Linking System (Bug #3)

### Overview

**Purpose:** Create graph connections between related entities for quick traversal

**Use Cases:**
- "I love Tokyo" → Links `Jack` ↔ `Tokyo`
- "I have a fear of talking to girls" → Links `Jack` ↔ `talking_to_girls`, `talking_to_girls` ↔ `girls`
- "Sarah and I met at MIT" → Links `Jack` ↔ `Sarah`, `Sarah` ↔ `MIT`, `Jack` ↔ `MIT`

### Database Schema

```sql
CREATE TYPE link_type AS ENUM (
  'loves',
  'fears',
  'knows',
  'works_with',
  'uses',
  'attended',
  'located_in',
  'friend_of',
  'related_to',
  'prefers',
  'dislikes',
  'aspires_to',
  'experienced',
  'created',
  'owns'
);

CREATE TABLE entity_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Source and target entities
  source_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  target_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,

  -- Link properties
  link_type link_type NOT NULL,
  link_strength FLOAT DEFAULT 1.0, -- 0.0 to 1.0
  bidirectional BOOLEAN DEFAULT TRUE,

  -- Context
  context TEXT,
  fact_id UUID REFERENCES facts(id), -- Link to source fact

  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  access_count INTEGER DEFAULT 0,

  INDEX idx_user_links (user_id),
  INDEX idx_source_entity (source_entity_id, link_type),
  INDEX idx_target_entity (target_entity_id, link_type),
  INDEX idx_bidirectional (source_entity_id, target_entity_id),

  UNIQUE(source_entity_id, target_entity_id, link_type)
);
```

### Link Creation Examples

**Example 1: "I love Tokyo"**
```sql
-- Create entities if they don't exist
INSERT INTO entities (name, topic_id, entity_type, user_id)
VALUES ('Jack', <topic_id_for_self>, 'person', <user_id>);

INSERT INTO entities (name, topic_id, entity_type, user_id)
VALUES ('Tokyo', <topic_id_for_places>, 'city', <user_id>);

-- Create link
INSERT INTO entity_links (source_entity_id, target_entity_id, link_type, user_id)
VALUES (<jack_id>, <tokyo_id>, 'loves', <user_id>);

-- Create fact
INSERT INTO facts (subject_entity_id, target_entity_id, content, fact_type, relationship_type)
VALUES (<jack_id>, <tokyo_id>, 'I love Tokyo', 'relationship', 'loves');
```

**Example 2: "I have a fear of talking to girls"**
```sql
-- Create entities
INSERT INTO entities (name, topic_id, entity_type, user_id)
VALUES ('talking_to_girls', <topic_id_for_fears>, 'social_anxiety', <user_id>);

INSERT INTO entities (name, topic_id, entity_type, user_id)
VALUES ('girls', <topic_id_for_people>, 'group', <user_id>);

-- Create links
-- Jack fears talking_to_girls
INSERT INTO entity_links (source_entity_id, target_entity_id, link_type, user_id)
VALUES (<jack_id>, <talking_to_girls_id>, 'fears', <user_id>);

-- talking_to_girls relates to girls
INSERT INTO entity_links (source_entity_id, target_entity_id, link_type, user_id)
VALUES (<talking_to_girls_id>, <girls_id>, 'related_to', <user_id>);
```

### Graph Queries

**Find all things Jack loves:**
```sql
SELECT e.name, e.entity_type, el.link_strength
FROM entity_links el
JOIN entities e ON e.id = el.target_entity_id
WHERE el.source_entity_id = <jack_id>
  AND el.link_type = 'loves'
ORDER BY el.link_strength DESC;
```

**Find all of Jack's fears:**
```sql
SELECT e.name, e.entity_type, e.attributes
FROM entity_links el
JOIN entities e ON e.id = el.target_entity_id
WHERE el.source_entity_id = <jack_id>
  AND el.link_type = 'fears';
```

**Find 2-hop connections (friends of friends):**
```sql
WITH first_hop AS (
  SELECT target_entity_id
  FROM entity_links
  WHERE source_entity_id = <jack_id>
    AND link_type = 'friend_of'
)
SELECT DISTINCT e.name
FROM entity_links el
JOIN entities e ON e.id = el.target_entity_id
WHERE el.source_entity_id IN (SELECT target_entity_id FROM first_hop)
  AND el.link_type = 'friend_of'
  AND e.id != <jack_id>;
```

---

## Migration Strategy

### Phase 1: Add New Tables (Non-Breaking)
```sql
-- Add new tables without modifying existing ones
CREATE TABLE topics (...);
CREATE TABLE entities (...);
CREATE TABLE entity_links (...);
-- facts table already exists, add new columns
ALTER TABLE facts ADD COLUMN subject_entity_id UUID REFERENCES entities(id);
ALTER TABLE facts ADD COLUMN target_entity_id UUID REFERENCES entities(id);
```

### Phase 2: Dual-Write (Transition Period)
- Write to both old (memories) and new (entities) tables
- Read from new tables, fall back to old if needed
- Allows gradual migration and rollback

### Phase 3: Backfill Existing Data
```python
async def migrate_memories_to_entities():
    """Migrate existing flat memories to entity-based system"""

    async with AsyncSessionLocal() as db:
        # Get all existing memories
        memories = await db.execute(select(Memory))

        for memory in memories.scalars():
            # Extract entities from memory content
            entities = await extract_entities_from_text(memory.content)

            for entity_data in entities:
                # Create or get entity
                entity = await get_or_create_entity(
                    name=entity_data['name'],
                    topic=entity_data['topic'],
                    entity_type=entity_data['type']
                )

                # Create links
                for link in entity_data.get('links', []):
                    await create_entity_link(
                        source=entity,
                        target=link['target'],
                        link_type=link['type']
                    )

                # Create fact
                await create_fact(
                    subject=entity,
                    content=memory.content,
                    fact_type='attribute'
                )

        await db.commit()
```

### Phase 4: Deprecate Old Tables
- Once migration is complete and tested
- Remove dual-write logic
- Archive old memories table

---

## Benefits of New Architecture

### 1. Efficient Multi-Value Storage
**Before:**
```
Memory 1: "Favorite cuisine: Italian"
Memory 2: "Favorite cuisine: Japanese"
Memory 3: "Favorite cuisine: Thai"
```

**After:**
```
Entity: food.cuisines
{
  "favorite_cuisines": ["Italian", "Japanese", "Thai"],
  "preference_order": [1, 2, 3]
}
```

**Storage:** 3 memories → 1 entity with array attribute
**Query Speed:** 3 queries → 1 query

### 2. Fast Graph Traversal
**Query:** "What does Jack love?"
```sql
-- Direct link lookup (fast!)
SELECT e.name FROM entity_links el
JOIN entities e ON e.id = el.target_entity_id
WHERE el.source_entity_id = <jack_id> AND el.link_type = 'loves';
```

**Query:** "Find all fears related to social situations"
```sql
SELECT e.name, e.attributes FROM entities e
WHERE e.topic_id IN (SELECT id FROM topics WHERE name = 'fears')
  AND e.attributes @> '{"triggers": ["social"]}';
```

### 3. Relationship Discovery
- "Show me all people Jack knows who also know Sarah"
- "What are the common interests between Jack and his friends?"
- "Which restaurants are linked to Tokyo?"

### 4. Flexible Attributes
- Can add new attributes without schema changes
- Multi-valued attributes handled naturally
- Nested structures supported (JSONB)

---

## Implementation Roadmap

### Milestone 1: Schema & Models (1 week)
- [ ] Create Alembic migration for new tables
- [ ] Create SQLAlchemy models for topics, entities, entity_links
- [ ] Update facts model with entity references
- [ ] Write database indexes

### Milestone 2: Entity Service (1 week)
- [ ] EntityService class for CRUD operations
- [ ] Entity extraction from natural language
- [ ] Automatic entity linking
- [ ] Entity deduplication logic

### Milestone 3: Integration with Chat (1 week)
- [ ] Update MemoryService to use entities
- [ ] Fact extraction to create entities + links
- [ ] Graph-based search queries
- [ ] Dual-write implementation

### Milestone 4: UI & Visualization (1 week)
- [ ] Entity browser UI
- [ ] Interactive graph visualization (React Flow)
- [ ] Link management (create, edit, delete)
- [ ] Entity attribute editing

### Milestone 5: Migration & Testing (1 week)
- [ ] Backfill script for existing memories
- [ ] Performance testing
- [ ] Integration testing
- [ ] Documentation

**Total Estimated Time:** 5 weeks

---

## Open Questions

1. **Entity Deduplication:** How to handle similar entities?
   - "Tokyo" vs "Tokyo, Japan" vs "東京"
   - Use fuzzy matching + embeddings?

2. **Link Strength Calculation:** How to determine link_strength?
   - Frequency of co-occurrence?
   - Explicit user rating?
   - ML-based relationship extraction?

3. **Topic Hierarchy:** Should topics have parent-child relationships?
   - "restaurants.japanese.ramen"
   - Or keep flat with tags?

4. **Entity Merge:** What if user creates duplicate entities?
   - Automatic merge with confirmation?
   - Manual merge UI?

---

**Next Steps:**
1. Review and approve this architecture
2. Create database migration
3. Implement EntityService
4. Update MemoryService integration
5. Build entity browser UI

