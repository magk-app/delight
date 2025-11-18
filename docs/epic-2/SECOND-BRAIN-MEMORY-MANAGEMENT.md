# Second Brain: User-Facing Memory Management System

**Date:** 2025-11-18
**Epic:** 2 - Companion & Memory System (Enhancement)
**Purpose:** Enable users to view, edit, organize, and visualize their memories as a "second brain"

---

## 🎯 Vision

Transform Delight's memory system from a hidden AI backend into an **interactive second brain** that:
- ✅ **Continuously improves** through user feedback and self-correction
- ✅ **Empowers users** to view, edit, and organize their memories
- ✅ **Visualizes connections** between memories, goals, and concepts
- ✅ **Builds over time** into a rich personal knowledge graph
- ✅ **Acts as a coach** by understanding what matters most to the user

---

## 📊 System Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  - Memory Dashboard (view/search)                           │
│  - Memory Editor (edit content/metadata)                    │
│  - Knowledge Graph Visualization (connections)              │
│  - Memory Collections (organize/curate)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 CONTINUOUS IMPROVEMENT LAYER                 │
│  - User Feedback Loop (correct/merge/delete)                │
│  - Automatic Deduplication (mem0 or custom)                 │
│  - Memory Refinement (LLM-based consolidation)              │
│  - Relationship Detection (graph building)                  │
└─────────────────────────────────────────────────────────────┐
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                            │
│  - Personal/Project: mem0 (high accuracy + deduplication)   │
│  - Task: pgvector (fast, temporary)                         │
│  - Graph: Neo4j (optional for complex relationships)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Part 1: Continuously Improving Memory

### 1.1 User Feedback Loop

**Problem:** Users need to correct, merge, or delete incorrect memories

**Solution:** Real-time feedback mechanism

```typescript
interface MemoryFeedback {
  memory_id: UUID;
  feedback_type: 'correct' | 'merge' | 'delete' | 'split' | 'verify';
  corrections?: {
    content?: string;
    metadata?: Partial<MemoryMetadata>;
  };
  merge_with?: UUID[];  // IDs of memories to merge with
  reason?: string;  // Why user is providing feedback
}
```

**User Actions:**
- ✅ **Correct**: Fix incorrect memory content or metadata
- ✅ **Merge**: Combine duplicate memories
- ✅ **Delete**: Remove incorrect or unwanted memories
- ✅ **Split**: Break compound memory into separate entries
- ✅ **Verify**: Mark memory as accurate (confidence boost)

**Implementation:**
```python
# Backend: app/services/memory_feedback_service.py
class MemoryFeedbackService:
    async def apply_feedback(
        self,
        user_id: UUID,
        memory_id: UUID,
        feedback: MemoryFeedback
    ) -> Memory:
        """Apply user feedback to improve memory quality."""

        if feedback.feedback_type == 'correct':
            # Update memory with corrections
            # Regenerate embedding if content changed
            return await self._correct_memory(memory_id, feedback.corrections)

        elif feedback.feedback_type == 'merge':
            # Consolidate multiple memories into one
            return await self._merge_memories(memory_id, feedback.merge_with)

        elif feedback.feedback_type == 'delete':
            # Soft delete (mark as deleted, don't hard remove)
            return await self._soft_delete_memory(memory_id, feedback.reason)

        elif feedback.feedback_type == 'split':
            # Break compound memory into multiple
            return await self._split_memory(memory_id, feedback.splits)

        elif feedback.feedback_type == 'verify':
            # Boost confidence score
            return await self._verify_memory(memory_id)
```

**UI Component:**
```typescript
// Frontend: src/components/memory/MemoryFeedbackPanel.tsx
export function MemoryFeedbackPanel({ memory }: { memory: Memory }) {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="memory-feedback-panel">
      <Button onClick={() => setIsEditing(true)}>
        <EditIcon /> Edit Memory
      </Button>

      <Button onClick={() => handleMerge(memory.id)}>
        <MergeIcon /> Merge Duplicates
      </Button>

      <Button onClick={() => handleDelete(memory.id)} variant="danger">
        <DeleteIcon /> Remove Memory
      </Button>

      <Button onClick={() => handleVerify(memory.id)} variant="success">
        <CheckIcon /> Verify Accuracy
      </Button>

      {isEditing && <MemoryEditor memory={memory} onSave={handleSave} />}
    </div>
  );
}
```

---

### 1.2 Automatic Deduplication

**Problem:** Duplicate memories clutter the system and waste tokens

**Solution:** Hybrid approach using mem0 + custom logic

#### Option A: mem0 Built-In Deduplication (Recommended)

```python
from mem0 import Memory

# Initialize mem0 with deduplication
mem0_client = Memory(
    vector_store="qdrant",
    vector_store_config={
        "url": os.getenv("QDRANT_URL"),
        "api_key": os.getenv("QDRANT_API_KEY"),
    },
    embedding_model="text-embedding-3-small",
    llm_model="gpt-4o-mini"
)

# mem0 automatically deduplicates when adding
mem0_client.add(
    "I prefer working in the morning",
    user_id=user_id,
    metadata={"source": "preferences", "memory_type": "personal"}
)

# If similar memory exists, mem0 will:
# 1. Detect duplicate via embeddings
# 2. Merge if confidence > threshold
# 3. Update existing memory instead of creating new one
```

**Benefits:**
- ✅ Automatic (no manual intervention)
- ✅ Reduces token usage 40-60%
- ✅ Production-ready
- ✅ Self-improving over time

**Cost:** ~$20-50/month for self-hosted Qdrant

#### Option B: Custom Deduplication (Fallback)

```python
# app/services/memory_deduplication_service.py
class MemoryDeduplicationService:
    async def find_duplicates(
        self,
        user_id: UUID,
        similarity_threshold: float = 0.95
    ) -> List[Tuple[UUID, UUID, float]]:
        """Find duplicate memories using vector similarity."""

        # Query all user memories
        memories = await self.db.execute(
            select(Memory).where(Memory.user_id == user_id)
        )

        duplicates = []
        for mem1, mem2 in combinations(memories, 2):
            similarity = cosine_similarity(mem1.embedding, mem2.embedding)
            if similarity >= similarity_threshold:
                duplicates.append((mem1.id, mem2.id, similarity))

        return duplicates

    async def merge_duplicates(
        self,
        memory_ids: List[UUID],
        strategy: str = 'keep_recent'
    ) -> Memory:
        """Merge duplicate memories using specified strategy."""

        memories = await self._fetch_memories(memory_ids)

        if strategy == 'keep_recent':
            primary = max(memories, key=lambda m: m.created_at)
        elif strategy == 'most_accessed':
            primary = max(memories, key=lambda m: m.metadata.get('access_count', 0))
        elif strategy == 'llm_merge':
            # Use LLM to intelligently combine memories
            primary = await self._llm_merge_memories(memories)

        # Delete other memories
        for mem in memories:
            if mem.id != primary.id:
                await self.db.delete(mem)

        await self.db.commit()
        return primary
```

---

### 1.3 Memory Refinement & Consolidation

**Problem:** Old memories become stale or verbose

**Solution:** LLM-based memory refinement

```python
# app/services/memory_refinement_service.py
class MemoryRefinementService:
    async def refine_memory(
        self,
        memory: Memory,
        user_context: Optional[Dict] = None
    ) -> Memory:
        """Use LLM to refine memory content for clarity and relevance."""

        prompt = f"""
        Refine this memory for clarity while preserving key information:

        Original: {memory.content}
        Created: {memory.created_at}
        Accessed: {memory.metadata.get('access_count', 0)} times
        Context: {user_context}

        Refined version (concise, clear, preserves meaning):
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        refined_content = response.choices[0].message.content

        # Update memory
        memory.content = refined_content
        memory.metadata['refined_at'] = datetime.now().isoformat()
        memory.metadata['original_content'] = memory.content  # Backup

        # Regenerate embedding
        memory.embedding = await self.embedding_service.generate_embedding(refined_content)

        await self.db.commit()
        return memory

    async def consolidate_memories(
        self,
        user_id: UUID,
        category: str,
        time_range: timedelta = timedelta(days=30)
    ) -> Memory:
        """Consolidate multiple related memories into a summary."""

        # Find related memories in time range
        cutoff = datetime.now() - time_range
        memories = await self.db.execute(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.metadata['category'].astext == category,
                Memory.created_at >= cutoff
            )
        )

        # Use LLM to create consolidated summary
        contents = [m.content for m in memories.scalars().all()]

        prompt = f"""
        Consolidate these related memories into a single coherent summary:

        {chr(10).join(f"{i+1}. {c}" for i, c in enumerate(contents))}

        Consolidated summary:
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        consolidated = Memory(
            user_id=user_id,
            memory_type=MemoryType.PERSONAL,
            content=response.choices[0].message.content,
            metadata={
                'consolidated': True,
                'source_memory_ids': [m.id for m in memories.scalars().all()],
                'category': category,
                'time_range': str(time_range)
            }
        )

        await self.db.add(consolidated)
        await self.db.commit()
        return consolidated
```

**Refinement Triggers:**
- ⏰ **Time-based**: Refine memories older than 90 days
- 📊 **Access-based**: Refine frequently accessed memories (>20 accesses)
- 👤 **User-triggered**: Manual refinement request
- 🤖 **AI-suggested**: Eliza suggests refinement during conversation

---

### 1.4 Self-Improving Relevance Scoring

**Problem:** Not all memories are equally important

**Solution:** Dynamic relevance scoring based on usage patterns

```python
# app/services/memory_relevance_service.py
class MemoryRelevanceService:
    def calculate_relevance_score(
        self,
        memory: Memory,
        user_priority_profile: Dict[str, float],
        current_context: Dict
    ) -> float:
        """Calculate dynamic relevance score for memory."""

        base_score = 1.0

        # Factor 1: Access patterns (how often retrieved)
        access_score = math.log1p(memory.metadata.get('access_count', 0)) / 10

        # Factor 2: Time decay (recency matters)
        days_old = (datetime.now() - memory.created_at).days
        recency_score = 1 / (1 + math.log1p(days_old))

        # Factor 3: User verification (verified memories boost)
        verification_score = 1.5 if memory.metadata.get('verified') else 1.0

        # Factor 4: Alignment with user priorities
        memory_factors = memory.metadata.get('universal_factors', {})
        alignment_score = sum(
            memory_factors.get(factor, 0) * user_priority_profile.get(factor, 0)
            for factor in ['health', 'learning', 'craft', 'connection', 'discipline']
        )

        # Factor 5: Emotional significance
        emotion_intensity = memory.metadata.get('emotion', {}).get('intensity', 0)
        emotion_score = 1 + (emotion_intensity * 0.5)

        # Factor 6: Context relevance (current user state)
        context_score = self._calculate_context_match(memory, current_context)

        # Combined score
        relevance = (
            base_score *
            (1 + access_score) *
            recency_score *
            verification_score *
            (1 + alignment_score) *
            emotion_score *
            context_score
        )

        return relevance

    def _calculate_context_match(
        self,
        memory: Memory,
        current_context: Dict
    ) -> float:
        """Calculate how well memory matches current user context."""

        score = 1.0

        # If user is stressed, prioritize well-being memories
        if current_context.get('stress_level') == 'high':
            if memory.metadata.get('category') in ['health', 'well-being']:
                score *= 1.5

        # If user is discussing goals, prioritize project memories
        if current_context.get('discussing_goals'):
            if memory.memory_type == MemoryType.PROJECT:
                score *= 1.3

        # If emotion matches, boost relevance
        if current_context.get('emotion') == memory.metadata.get('emotion', {}).get('dominant'):
            score *= 1.2

        return score
```

---

## 🎨 Part 2: User-Facing Memory Dashboard

### 2.1 Memory Dashboard UI

**Route:** `/memories` or `/second-brain`

**Features:**
- 📋 **Memory List**: Paginated list of all memories
- 🔍 **Search & Filter**: By type, category, date, emotion
- 📊 **Statistics**: Memory count by type, access patterns, growth over time
- 🎯 **Quick Actions**: Edit, delete, merge, verify

**UI Design:**

```typescript
// Frontend: src/app/memories/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useMemories } from '@/lib/hooks/useMemories';
import { MemoryCard } from '@/components/memory/MemoryCard';
import { MemoryFilters } from '@/components/memory/MemoryFilters';
import { MemoryStats } from '@/components/memory/MemoryStats';

export default function MemoriesPage() {
  const {
    memories,
    isLoading,
    filters,
    setFilters,
    stats,
    refetch
  } = useMemories();

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Your Second Brain</h1>
        <p className="text-gray-600">
          View, edit, and organize your memories. {stats.total_memories} memories stored.
        </p>
      </header>

      {/* Statistics Dashboard */}
      <MemoryStats stats={stats} />

      {/* Filters */}
      <MemoryFilters filters={filters} onChange={setFilters} />

      {/* Memory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
        {isLoading ? (
          <MemoryLoadingSkeleton />
        ) : (
          memories.map(memory => (
            <MemoryCard
              key={memory.id}
              memory={memory}
              onEdit={() => handleEdit(memory)}
              onDelete={() => handleDelete(memory.id)}
              onMerge={() => handleMerge(memory.id)}
            />
          ))
        )}
      </div>

      {/* Pagination */}
      <Pagination
        currentPage={filters.page}
        totalPages={Math.ceil(stats.total_memories / filters.limit)}
        onPageChange={(page) => setFilters({ ...filters, page })}
      />
    </div>
  );
}
```

**Memory Card Component:**

```typescript
// Frontend: src/components/memory/MemoryCard.tsx
import { Memory } from '@/types/memory';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';

interface MemoryCardProps {
  memory: Memory;
  onEdit: () => void;
  onDelete: () => void;
  onMerge: () => void;
}

export function MemoryCard({ memory, onEdit, onDelete, onMerge }: MemoryCardProps) {
  const memoryTypeColors = {
    personal: 'bg-purple-100 text-purple-800',
    project: 'bg-blue-100 text-blue-800',
    task: 'bg-green-100 text-green-800'
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="pt-6">
        {/* Memory Type Badge */}
        <Badge className={memoryTypeColors[memory.memory_type]}>
          {memory.memory_type}
        </Badge>

        {/* Memory Content */}
        <p className="mt-4 text-gray-800 line-clamp-3">
          {memory.content}
        </p>

        {/* Metadata */}
        <div className="mt-4 space-y-2 text-sm text-gray-600">
          {memory.metadata.category && (
            <div className="flex items-center gap-2">
              <TagIcon className="w-4 h-4" />
              <span>{memory.metadata.category}</span>
            </div>
          )}

          {memory.metadata.emotion && (
            <div className="flex items-center gap-2">
              <EmotionIcon className="w-4 h-4" />
              <span>{memory.metadata.emotion.dominant} ({(memory.metadata.emotion.intensity * 100).toFixed(0)}%)</span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <ClockIcon className="w-4 h-4" />
            <span>{formatDistanceToNow(new Date(memory.created_at), { addSuffix: true })}</span>
          </div>

          <div className="flex items-center gap-2">
            <EyeIcon className="w-4 h-4" />
            <span>Accessed {memory.metadata.access_count || 0} times</span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex gap-2 justify-end">
        <Button variant="outline" size="sm" onClick={onEdit}>
          <EditIcon className="w-4 h-4" />
        </Button>
        <Button variant="outline" size="sm" onClick={onMerge}>
          <MergeIcon className="w-4 h-4" />
        </Button>
        <Button variant="outline" size="sm" onClick={onDelete} className="text-red-600">
          <DeleteIcon className="w-4 h-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
```

---

### 2.2 Memory Search & Filtering

**Filters Available:**
- **Memory Type**: Personal, Project, Task
- **Category**: Academic, Health, Romance, Family, etc.
- **Emotion**: Joy, Fear, Sadness, Anger, etc.
- **Date Range**: Last 7 days, 30 days, 90 days, All time
- **Verified**: Show only verified memories
- **Access Frequency**: Most accessed, Least accessed

```typescript
// Frontend: src/components/memory/MemoryFilters.tsx
interface MemoryFilters {
  memory_type?: 'personal' | 'project' | 'task';
  category?: string;
  emotion?: string;
  date_range?: 'week' | 'month' | 'quarter' | 'all';
  verified_only?: boolean;
  sort_by?: 'created_at' | 'accessed_at' | 'access_count' | 'relevance';
  search_query?: string;
}

export function MemoryFilters({ filters, onChange }: MemoryFiltersProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow space-y-4">
      {/* Search */}
      <div>
        <Input
          placeholder="Search memories..."
          value={filters.search_query || ''}
          onChange={(e) => onChange({ ...filters, search_query: e.target.value })}
          icon={<SearchIcon />}
        />
      </div>

      {/* Type Filter */}
      <div>
        <Label>Memory Type</Label>
        <Select
          value={filters.memory_type || 'all'}
          onValueChange={(value) => onChange({ ...filters, memory_type: value as any })}
        >
          <SelectItem value="all">All Types</SelectItem>
          <SelectItem value="personal">Personal</SelectItem>
          <SelectItem value="project">Project</SelectItem>
          <SelectItem value="task">Task</SelectItem>
        </Select>
      </div>

      {/* Category Filter */}
      <div>
        <Label>Category</Label>
        <Select
          value={filters.category || 'all'}
          onValueChange={(value) => onChange({ ...filters, category: value })}
        >
          <SelectItem value="all">All Categories</SelectItem>
          <SelectItem value="academic">Academic</SelectItem>
          <SelectItem value="health">Health</SelectItem>
          <SelectItem value="romance">Romance</SelectItem>
          <SelectItem value="family">Family</SelectItem>
          <SelectItem value="social">Social</SelectItem>
        </Select>
      </div>

      {/* Date Range */}
      <div>
        <Label>Date Range</Label>
        <RadioGroup
          value={filters.date_range || 'all'}
          onValueChange={(value) => onChange({ ...filters, date_range: value as any })}
        >
          <RadioGroupItem value="week">Last 7 days</RadioGroupItem>
          <RadioGroupItem value="month">Last 30 days</RadioGroupItem>
          <RadioGroupItem value="quarter">Last 90 days</RadioGroupItem>
          <RadioGroupItem value="all">All time</RadioGroupItem>
        </RadioGroup>
      </div>

      {/* Sort By */}
      <div>
        <Label>Sort By</Label>
        <Select
          value={filters.sort_by || 'created_at'}
          onValueChange={(value) => onChange({ ...filters, sort_by: value as any })}
        >
          <SelectItem value="created_at">Newest First</SelectItem>
          <SelectItem value="accessed_at">Recently Accessed</SelectItem>
          <SelectItem value="access_count">Most Accessed</SelectItem>
          <SelectItem value="relevance">Most Relevant</SelectItem>
        </Select>
      </div>

      {/* Verified Only */}
      <div className="flex items-center gap-2">
        <Checkbox
          id="verified-only"
          checked={filters.verified_only || false}
          onCheckedChange={(checked) => onChange({ ...filters, verified_only: checked as boolean })}
        />
        <Label htmlFor="verified-only">Show only verified memories</Label>
      </div>
    </div>
  );
}
```

---

### 2.3 Memory Editor

**Route:** `/memories/:id/edit`

**Features:**
- ✏️ **Edit Content**: Modify memory text
- 🏷️ **Edit Metadata**: Change category, emotion, tags
- 🔗 **Link to Goals**: Associate memory with goals/tasks
- ✅ **Verify Memory**: Mark as accurate
- 🗑️ **Delete Memory**: Remove with confirmation

```typescript
// Frontend: src/components/memory/MemoryEditor.tsx
'use client';

import { useState } from 'react';
import { Memory } from '@/types/memory';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

interface MemoryEditorProps {
  memory: Memory;
  onSave: (updated: Partial<Memory>) => Promise<void>;
  onCancel: () => void;
}

export function MemoryEditor({ memory, onSave, onCancel }: MemoryEditorProps) {
  const [content, setContent] = useState(memory.content);
  const [category, setCategory] = useState(memory.metadata.category || '');
  const [emotion, setEmotion] = useState(memory.metadata.emotion?.dominant || '');
  const [tags, setTags] = useState<string[]>(memory.metadata.tags || []);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);

    await onSave({
      content,
      metadata: {
        ...memory.metadata,
        category,
        emotion: {
          ...memory.metadata.emotion,
          dominant: emotion
        },
        tags
      }
    });

    setIsSaving(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Edit Memory</h2>

      {/* Content */}
      <div className="mb-4">
        <Label htmlFor="content">Memory Content</Label>
        <Textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={4}
          className="w-full"
        />
      </div>

      {/* Category */}
      <div className="mb-4">
        <Label htmlFor="category">Category</Label>
        <Select
          id="category"
          value={category}
          onValueChange={setCategory}
        >
          <SelectItem value="academic">Academic</SelectItem>
          <SelectItem value="health">Health</SelectItem>
          <SelectItem value="romance">Romance</SelectItem>
          <SelectItem value="family">Family</SelectItem>
          <SelectItem value="social">Social</SelectItem>
          <SelectItem value="work">Work</SelectItem>
        </Select>
      </div>

      {/* Emotion */}
      <div className="mb-4">
        <Label htmlFor="emotion">Dominant Emotion</Label>
        <Select
          id="emotion"
          value={emotion}
          onValueChange={setEmotion}
        >
          <SelectItem value="joy">Joy</SelectItem>
          <SelectItem value="fear">Fear</SelectItem>
          <SelectItem value="sadness">Sadness</SelectItem>
          <SelectItem value="anger">Anger</SelectItem>
          <SelectItem value="love">Love</SelectItem>
          <SelectItem value="surprise">Surprise</SelectItem>
          <SelectItem value="neutral">Neutral</SelectItem>
        </Select>
      </div>

      {/* Tags */}
      <div className="mb-6">
        <Label htmlFor="tags">Tags</Label>
        <TagInput
          tags={tags}
          onChange={setTags}
          placeholder="Add tags..."
        />
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  );
}
```

---

### 2.4 Memory Collections

**Problem:** Users want to organize memories into curated collections

**Solution:** Memory Collections system (already in DB schema!)

```typescript
// Frontend: src/app/memories/collections/page.tsx
'use client';

import { useMemoryCollections } from '@/lib/hooks/useMemoryCollections';
import { CollectionCard } from '@/components/memory/CollectionCard';

export default function CollectionsPage() {
  const { collections, createCollection } = useMemoryCollections();

  return (
    <div className="container mx-auto px-6 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Memory Collections</h1>
        <p className="text-gray-600">
          Organize your memories into curated collections
        </p>
      </header>

      {/* Create New Collection */}
      <Button onClick={() => createCollection()}>
        <PlusIcon /> New Collection
      </Button>

      {/* Collections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        {collections.map(collection => (
          <CollectionCard key={collection.id} collection={collection} />
        ))}
      </div>
    </div>
  );
}
```

**Collection Types:**
- 🎯 **Goal Collections**: All memories related to a specific goal
- 📊 **Stressor Logs**: Track specific anxieties over time
- 💡 **Insights**: Curated learnings and realizations
- 📚 **Knowledge Areas**: Organize by topic/domain
- ⏰ **Time Capsules**: Memories from specific periods

---

## 🕸️ Part 3: Knowledge Graph Visualization

### 3.1 Graph Structure

**Nodes:**
- 🧠 **Memory Nodes**: Individual memories
- 🎯 **Goal Nodes**: User goals
- ✅ **Task Nodes**: Tasks and missions
- 🏷️ **Concept Nodes**: Categories, topics, themes
- 😊 **Emotion Nodes**: Emotional states

**Relationships:**
- `RELATES_TO`: Memory ↔ Memory (semantic similarity)
- `SUPPORTS`: Memory → Goal (memory supports goal)
- `TRIGGERED_BY`: Memory → Task (memory created from task)
- `CATEGORIZED_AS`: Memory → Concept
- `EXPRESSES`: Memory → Emotion
- `CONFLICTS_WITH`: Memory ↔ Memory (contradictory memories)

**Graph Schema:**

```typescript
interface MemoryGraphNode {
  id: string;
  type: 'memory' | 'goal' | 'task' | 'concept' | 'emotion';
  label: string;
  metadata: Record<string, any>;
  x?: number;  // Position for visualization
  y?: number;
}

interface MemoryGraphEdge {
  id: string;
  source: string;  // Node ID
  target: string;  // Node ID
  type: 'relates_to' | 'supports' | 'triggered_by' | 'categorized_as' | 'expresses' | 'conflicts_with';
  weight: number;  // Relationship strength (0-1)
  metadata?: Record<string, any>;
}

interface MemoryGraph {
  nodes: MemoryGraphNode[];
  edges: MemoryGraphEdge[];
}
```

---

### 3.2 Graph Building Service

```python
# Backend: app/services/memory_graph_service.py
from typing import List, Tuple, Dict
import networkx as nx
import numpy as np

class MemoryGraphService:
    """Build and analyze knowledge graph from user memories."""

    async def build_graph(self, user_id: UUID) -> Dict:
        """Build complete memory graph for user."""

        # Fetch all user data
        memories = await self._fetch_memories(user_id)
        goals = await self._fetch_goals(user_id)
        tasks = await self._fetch_tasks(user_id)

        # Build graph structure
        graph = nx.DiGraph()

        # Add memory nodes
        for memory in memories:
            graph.add_node(
                str(memory.id),
                type='memory',
                label=memory.content[:50] + '...',
                memory_type=memory.memory_type.value,
                category=memory.metadata.get('category'),
                emotion=memory.metadata.get('emotion', {}).get('dominant'),
                created_at=memory.created_at.isoformat(),
                access_count=memory.metadata.get('access_count', 0)
            )

        # Add goal nodes
        for goal in goals:
            graph.add_node(
                str(goal.id),
                type='goal',
                label=goal.title,
                status=goal.status
            )

        # Add task nodes
        for task in tasks:
            graph.add_node(
                str(task.id),
                type='task',
                label=task.title,
                status=task.status
            )

        # Build relationships
        await self._build_memory_relationships(graph, memories)
        await self._build_goal_relationships(graph, memories, goals)
        await self._build_task_relationships(graph, memories, tasks)
        await self._build_concept_relationships(graph, memories)

        # Calculate graph metrics
        metrics = self._calculate_graph_metrics(graph)

        # Convert to JSON format
        graph_data = {
            'nodes': [
                {'id': node, **data}
                for node, data in graph.nodes(data=True)
            ],
            'edges': [
                {
                    'id': f"{source}-{target}",
                    'source': source,
                    'target': target,
                    **data
                }
                for source, target, data in graph.edges(data=True)
            ],
            'metrics': metrics
        }

        return graph_data

    async def _build_memory_relationships(
        self,
        graph: nx.DiGraph,
        memories: List[Memory]
    ):
        """Build RELATES_TO edges between semantically similar memories."""

        for i, mem1 in enumerate(memories):
            for mem2 in memories[i+1:]:
                if mem1.embedding is None or mem2.embedding is None:
                    continue

                # Calculate cosine similarity
                similarity = self._cosine_similarity(mem1.embedding, mem2.embedding)

                # Add edge if similarity above threshold
                if similarity >= 0.7:
                    graph.add_edge(
                        str(mem1.id),
                        str(mem2.id),
                        type='relates_to',
                        weight=similarity,
                        bidirectional=True
                    )

    async def _build_goal_relationships(
        self,
        graph: nx.DiGraph,
        memories: List[Memory],
        goals: List[Goal]
    ):
        """Build SUPPORTS edges between memories and goals."""

        for memory in memories:
            goal_id = memory.metadata.get('goal_id')
            if goal_id:
                graph.add_edge(
                    str(memory.id),
                    str(goal_id),
                    type='supports',
                    weight=1.0
                )

    async def _build_task_relationships(
        self,
        graph: nx.DiGraph,
        memories: List[Memory],
        tasks: List[Task]
    ):
        """Build TRIGGERED_BY edges between memories and tasks."""

        for memory in memories:
            task_id = memory.metadata.get('task_id')
            if task_id:
                graph.add_edge(
                    str(task_id),
                    str(memory.id),
                    type='triggered_by',
                    weight=1.0
                )

    async def _build_concept_relationships(
        self,
        graph: nx.DiGraph,
        memories: List[Memory]
    ):
        """Build CATEGORIZED_AS edges to concept nodes."""

        # Extract unique concepts (categories, emotions, topics)
        concepts = set()
        for memory in memories:
            if category := memory.metadata.get('category'):
                concepts.add(('category', category))
            if emotion := memory.metadata.get('emotion', {}).get('dominant'):
                concepts.add(('emotion', emotion))

        # Add concept nodes
        for concept_type, concept_value in concepts:
            concept_id = f"{concept_type}:{concept_value}"
            graph.add_node(
                concept_id,
                type='concept',
                label=concept_value,
                concept_type=concept_type
            )

        # Add edges from memories to concepts
        for memory in memories:
            if category := memory.metadata.get('category'):
                graph.add_edge(
                    str(memory.id),
                    f"category:{category}",
                    type='categorized_as',
                    weight=1.0
                )

            if emotion := memory.metadata.get('emotion', {}).get('dominant'):
                intensity = memory.metadata.get('emotion', {}).get('intensity', 0.5)
                graph.add_edge(
                    str(memory.id),
                    f"emotion:{emotion}",
                    type='expresses',
                    weight=intensity
                )

    def _calculate_graph_metrics(self, graph: nx.DiGraph) -> Dict:
        """Calculate graph analytics metrics."""

        return {
            'node_count': graph.number_of_nodes(),
            'edge_count': graph.number_of_edges(),
            'density': nx.density(graph),
            'avg_clustering': nx.average_clustering(graph.to_undirected()),
            'central_nodes': self._find_central_nodes(graph),
            'communities': self._detect_communities(graph)
        }

    def _find_central_nodes(self, graph: nx.DiGraph, top_k: int = 5) -> List[Dict]:
        """Find most central nodes using PageRank."""

        pagerank = nx.pagerank(graph)
        top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            {
                'id': node_id,
                'score': score,
                'label': graph.nodes[node_id].get('label')
            }
            for node_id, score in top_nodes
        ]

    def _detect_communities(self, graph: nx.DiGraph) -> List[List[str]]:
        """Detect communities/clusters in graph."""

        # Convert to undirected for community detection
        undirected = graph.to_undirected()

        # Use Louvain community detection
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(undirected)

        return [list(comm) for comm in communities]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
```

---

### 3.3 Graph Visualization Component

**Libraries:**
- **React Flow**: For interactive graph visualization
- **D3.js**: For advanced graph layouts (force-directed)
- **Cytoscape.js**: Alternative with rich features

**Implementation with React Flow:**

```typescript
// Frontend: src/components/memory/KnowledgeGraphView.tsx
'use client';

import { useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useMemoryGraph } from '@/lib/hooks/useMemoryGraph';

export function KnowledgeGraphView({ userId }: { userId: string }) {
  const { graph, isLoading } = useMemoryGraph(userId);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!graph) return;

    // Convert graph data to React Flow format
    const flowNodes: Node[] = graph.nodes.map(node => ({
      id: node.id,
      type: getNodeType(node.type),
      position: { x: node.x || 0, y: node.y || 0 },
      data: {
        label: node.label,
        ...node.metadata
      },
      style: getNodeStyle(node.type)
    }));

    const flowEdges: Edge[] = graph.edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: edge.type === 'relates_to',
      label: getEdgeLabel(edge.type),
      style: getEdgeStyle(edge.type, edge.weight)
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [graph]);

  const nodeTypes = {
    memory: MemoryNode,
    goal: GoalNode,
    task: TaskNode,
    concept: ConceptNode,
  };

  if (isLoading) {
    return <GraphLoadingSkeleton />;
  }

  return (
    <div className="w-full h-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>

      {/* Graph Analytics Panel */}
      <GraphAnalytics metrics={graph.metrics} />
    </div>
  );
}

// Custom node components
function MemoryNode({ data }: { data: any }) {
  const typeColors = {
    personal: 'bg-purple-500',
    project: 'bg-blue-500',
    task: 'bg-green-500'
  };

  return (
    <div className={`px-4 py-2 rounded-lg shadow-lg ${typeColors[data.memory_type]} text-white`}>
      <div className="font-semibold">{data.label}</div>
      <div className="text-xs mt-1 opacity-80">{data.category}</div>
    </div>
  );
}

function GoalNode({ data }: { data: any }) {
  return (
    <div className="px-4 py-2 rounded-full bg-yellow-500 text-white shadow-lg">
      <div className="font-semibold">🎯 {data.label}</div>
    </div>
  );
}

function ConceptNode({ data }: { data: any }) {
  return (
    <div className="px-3 py-1 rounded-md bg-gray-200 text-gray-800 border-2 border-gray-400">
      <div className="text-sm">{data.label}</div>
    </div>
  );
}

// Helper functions
function getNodeStyle(type: string) {
  const styles = {
    memory: { border: '2px solid #a855f7' },
    goal: { border: '3px solid #eab308' },
    task: { border: '2px solid #22c55e' },
    concept: { border: '1px dashed #9ca3af' }
  };
  return styles[type] || {};
}

function getEdgeStyle(type: string, weight: number) {
  const opacity = Math.max(0.3, weight);
  const strokeWidth = 1 + (weight * 3);

  return {
    opacity,
    strokeWidth
  };
}

function getEdgeLabel(type: string) {
  const labels = {
    relates_to: 'related',
    supports: 'supports',
    triggered_by: 'created from',
    categorized_as: 'is',
    expresses: 'feels'
  };
  return labels[type] || type;
}
```

---

### 3.4 Graph Analytics Panel

```typescript
// Frontend: src/components/memory/GraphAnalytics.tsx
interface GraphMetrics {
  node_count: number;
  edge_count: number;
  density: number;
  avg_clustering: number;
  central_nodes: Array<{ id: string; score: number; label: string }>;
  communities: string[][];
}

export function GraphAnalytics({ metrics }: { metrics: GraphMetrics }) {
  return (
    <div className="absolute top-4 right-4 bg-white p-6 rounded-lg shadow-lg max-w-md">
      <h3 className="text-lg font-bold mb-4">Knowledge Graph Analytics</h3>

      {/* Basic Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <Stat label="Memories" value={metrics.node_count} />
        <Stat label="Connections" value={metrics.edge_count} />
        <Stat label="Density" value={(metrics.density * 100).toFixed(1) + '%'} />
        <Stat label="Clustering" value={(metrics.avg_clustering * 100).toFixed(1) + '%'} />
      </div>

      {/* Central Memories */}
      <div className="mb-6">
        <h4 className="font-semibold mb-2">Most Central Memories</h4>
        <ul className="space-y-2">
          {metrics.central_nodes.map(node => (
            <li key={node.id} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-purple-500" />
              <span className="text-sm truncate">{node.label}</span>
              <span className="text-xs text-gray-500 ml-auto">
                {(node.score * 100).toFixed(0)}%
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Communities */}
      <div>
        <h4 className="font-semibold mb-2">Memory Clusters</h4>
        <p className="text-sm text-gray-600">
          {metrics.communities.length} distinct clusters found
        </p>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="text-center">
      <div className="text-2xl font-bold text-purple-600">{value}</div>
      <div className="text-xs text-gray-600">{label}</div>
    </div>
  );
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Story 2.5 Completion)
**Timeline:** 2-3 days

- ✅ Complete Story 2.5 (Companion Chat UI with essential memory)
- ✅ Validate memory storage and retrieval works
- ✅ Test case study scenarios
- ✅ Measure accuracy metrics

### Phase 2: Continuous Improvement (Story 2.6 Enhancement)
**Timeline:** 3-4 days

- 🔄 **Implement User Feedback Loop**
  - Memory correction API endpoints
  - Merge/split/delete functionality
  - Verification system

- 🔄 **Evaluate mem0 Migration**
  - Test accuracy metrics from Phase 1
  - If task loss > 1% OR accuracy < 90% → Migrate
  - Implement hybrid architecture (mem0 for Personal/Project, pgvector for Task)

- 🔄 **Implement Memory Refinement**
  - LLM-based memory consolidation
  - Automatic refinement triggers
  - Deduplication service

### Phase 3: User-Facing Dashboard (New Story: 2.7)
**Timeline:** 4-5 days

- 📊 **Build Memory Dashboard**
  - Memory list view with filters
  - Memory statistics
  - Search functionality

- ✏️ **Build Memory Editor**
  - Edit content and metadata
  - Bulk operations (merge, delete)
  - Memory verification UI

- 🗂️ **Build Collections System**
  - Create/edit collections
  - Add memories to collections
  - Collection views

### Phase 4: Knowledge Graph (New Story: 2.8)
**Timeline:** 5-6 days

- 🕸️ **Build Graph Service**
  - Graph building from memories
  - Relationship detection
  - Graph analytics

- 🎨 **Build Graph Visualization**
  - Interactive graph UI (React Flow)
  - Node/edge customization
  - Graph filtering

- 📊 **Build Graph Analytics**
  - Central nodes detection
  - Community detection
  - Insight generation

---

## 📊 Success Metrics

### Accuracy Metrics (Continuous Improvement)
- **Task Loss Rate**: < 0.5% (target: 0%)
- **Personal Memory Retention**: 100%
- **Deduplication Rate**: > 80% of duplicates removed
- **User Correction Rate**: < 5% of memories need correction

### Engagement Metrics (User Dashboard)
- **Dashboard Visit Rate**: > 30% of users view dashboard weekly
- **Memory Edit Rate**: > 10% of memories edited by users
- **Collection Usage**: > 20% of users create collections
- **Verification Rate**: > 40% of memories verified by users

### Knowledge Graph Metrics
- **Graph Density**: 0.1 - 0.3 (healthy connectivity)
- **Average Clustering**: > 0.3 (well-formed communities)
- **Central Node Coverage**: Top 10% of memories cover > 50% of relationships
- **Graph Growth Rate**: Steady increase over time

---

## 💰 Cost Analysis

### mem0 Migration Cost
- **Self-hosted Qdrant**: ~$30-50/month
- **Pinecone (Cloud)**: ~$70/month
- **OpenAI Embeddings**: ~$5/month (for new memories)
- **Total**: ~$35-75/month (vs. $0 for pure pgvector)

**ROI Justification:**
- ✅ 40-60% token reduction = $20-30/month savings in LLM costs
- ✅ Improved accuracy = better user experience = higher retention
- ✅ Auto-deduplication = cleaner memory system
- **Net Cost**: ~$15-45/month for significantly better accuracy

### Graph Visualization Cost
- **Neo4j Cloud**: ~$65/month (optional, only if needed)
- **React Flow**: Free (MIT license)
- **Compute**: ~$10/month for graph analytics
- **Total**: ~$10/month (without Neo4j)

---

## 🎯 Next Steps

1. **Complete Story 2.5** - Get basic chat + memory working
2. **Evaluate Metrics** - Test accuracy, decide on mem0 migration
3. **Implement Feedback Loop** - Enable user corrections
4. **Build Dashboard** - User-facing memory management
5. **Build Knowledge Graph** - Visualize connections
6. **Iterate Based on Usage** - Improve based on user feedback

---

## 📚 References

**Technical Documentation:**
- mem0 Docs: https://docs.mem0.ai/
- React Flow: https://reactflow.dev/
- NetworkX: https://networkx.org/
- Neo4j: https://neo4j.com/docs/

**Related Documents:**
- `docs/epic-2/MEMORY-ARCHITECTURE-COMPARISON.md` - Architecture decision framework
- `docs/stories/2-5-companion-chat-ui-with-essential-memory.md` - Current story
- `docs/stories/2-2-implement-memory-service-with-3-tier-architecture.md` - Memory service spec

---

**Last Updated:** 2025-11-18
**Status:** Specification Complete - Ready for Implementation
**Next Action:** Complete Story 2.5, then evaluate metrics for mem0 migration decision
