# Phase 3 Frontend Usage Guide

Complete guide for using Phase 3 hierarchical memory and graph features in the frontend.

---

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd packages/backend
poetry run python experiments/web/dashboard_server.py
```

### 2. Start the Frontend
```bash
# In a new terminal
cd packages/frontend
pnpm dev
```

### 3. Visit the Experimental Page
```
http://localhost:3000/experimental
```

---

## 📊 Using the Graph Visualization

### Interactive Graph Tab

1. **Navigate to Graph Tab**: Click the "Graph" tab in the experimental page
2. **View Your Memory Graph**: See all entities and their relationships visualized
3. **Interact with Nodes**:
   - **Click** a node to view detailed attributes in the side panel
   - **Drag** nodes to rearrange the graph
   - **Zoom** using mouse wheel or controls
   - **Pan** by dragging the background

### Graph Features

- **Color-Coded Nodes by Type**:
  - 🟢 Green = Person
  - 🔵 Blue = Place
  - 🟣 Purple = Project
  - 🟠 Orange = Organization
  - 🩷 Pink = Object
  - 🩵 Cyan = Event
  - ⚫ Gray = Unknown

- **Animated Edges**: Relationships with strength > 0.8 have animated edges
- **Edge Thickness**: Represents relationship strength
- **MiniMap**: Navigate large graphs easily
- **Legend**: Shows all entity types and colors

---

## 💻 Using the API Client

### Import the Client

```typescript
import experimentalAPI from '@/lib/api/experimental-client';
```

### 1. Get Graph Visualization Data

```typescript
// Get graph data for a user
const graphData = await experimentalAPI.getGraphVisualization(userId);

console.log(graphData);
// {
//   nodes: [
//     {
//       id: "memory-uuid",
//       label: "yoshinoya",
//       type: "place",
//       content: "Favorite restaurant: Yoshinoya with tonkatsu for $10",
//       attributes: {
//         type: "restaurant",
//         favorite_dish: "tonkatsu bowl",
//         price: "$10",
//         locations: ["Tokyo", "America"]
//       },
//       created_at: "2025-11-19T06:00:00Z"
//     }
//   ],
//   edges: [
//     {
//       id: "rel-uuid",
//       source: "memory-uuid-1",
//       target: "memory-uuid-2",
//       label: "LOCATED_AT",
//       strength: 0.9,
//       metadata: { source: "same_message" }
//     }
//   ]
// }
```

### 2. Filter by Entity Type

```typescript
// Get only "project" entities
const projectGraph = await experimentalAPI.getGraphVisualization(
  userId,
  "project"  // entity_type filter
);
```

### 3. Create Relationships Manually

```typescript
// Create a typed relationship between two memories
const result = await experimentalAPI.createRelationship({
  from_memory_id: "jack-memory-id",
  to_memory_id: "delight-project-id",
  relationship_type: "WORKS_ON",
  strength: 0.95,
  metadata: { role: "founder" },
  bidirectional: true
});

console.log(result);
// {
//   status: "created",
//   relationship: {
//     id: "rel-uuid",
//     from_memory_id: "...",
//     to_memory_id: "...",
//     relationship_type: "WORKS_ON",
//     strength: 0.95,
//     metadata: { role: "founder" },
//     created_at: "2025-11-19T06:00:00Z"
//   }
// }
```

### 4. Get Relationships for a Memory

```typescript
// Get all relationships for a specific memory
const relationships = await experimentalAPI.getRelationships(memoryId);

console.log(relationships);
// {
//   memory_id: "jack-id",
//   relationships: [
//     {
//       id: "rel-uuid",
//       from_memory_id: "jack-id",
//       to_memory_id: "delight-id",
//       relationship_type: "WORKS_ON",
//       strength: 0.95,
//       metadata: {},
//       related_memory: {
//         id: "delight-id",
//         content: "Delight is an AI companion app...",
//         entity_id: "delight_project",
//         entity_type: "project"
//       },
//       direction: "outgoing"
//     }
//   ]
// }

// Filter by relationship type
const worksOnRelationships = await experimentalAPI.getRelationships(
  memoryId,
  "WORKS_ON"
);
```

### 5. Traverse the Graph

```typescript
// Traverse graph from a starting memory
const paths = await experimentalAPI.traverseGraph(
  startMemoryId,
  3,      // max_depth
  0.5,    // min_strength
  "WORKS_ON"  // optional relationship_type filter
);

console.log(paths);
// {
//   start_memory_id: "jack-id",
//   paths: [
//     {
//       nodes: [
//         {
//           memory_id: "jack-id",
//           entity_id: "jack_education",
//           entity_type: "person",
//           content: "I attended UCSB, MIT, Georgia Tech",
//           depth: 0
//         },
//         {
//           memory_id: "delight-id",
//           entity_id: "delight_project",
//           entity_type: "project",
//           content: "Working on Delight AI app...",
//           depth: 1
//         }
//       ],
//       edges: [
//         {
//           from_id: "jack-id",
//           to_id: "delight-id",
//           relationship_type: "WORKS_ON",
//           strength: 0.95
//         }
//       ],
//       total_strength: 0.95
//     }
//   ]
// }
```

### 6. Find Shortest Path Between Memories

```typescript
// Find shortest path from one memory to another
const pathResult = await experimentalAPI.findShortestPath(
  fromMemoryId,
  toMemoryId,
  5  // max_depth
);

console.log(pathResult);
// {
//   from_memory_id: "jack-id",
//   to_memory_id: "tokyo-id",
//   path: [
//     {
//       memory_id: "jack-id",
//       entity_id: "jack",
//       content: "User profile",
//       relationship_to_next: "PREFERS"
//     },
//     {
//       memory_id: "yoshinoya-id",
//       entity_id: "yoshinoya",
//       content: "Favorite restaurant",
//       relationship_to_next: "LOCATED_AT"
//     },
//     {
//       memory_id: "tokyo-id",
//       entity_id: "tokyo",
//       content: "City: Tokyo",
//       relationship_to_next: null
//     }
//   ],
//   path_length: 2  // number of edges (3 nodes - 1)
// }
```

### 7. Get Complete Entity Graph

```typescript
// Get the complete entity relationship graph for a user
const entityGraph = await experimentalAPI.getEntityGraph(userId);

console.log(entityGraph);
// {
//   user_id: "user-uuid",
//   entity_graph: {
//     "jack_education": [
//       {
//         to_entity_id: "delight_project",
//         relationship_type: "WORKS_ON",
//         strength: 0.95
//       }
//     ],
//     "yoshinoya": [
//       {
//         to_entity_id: "tokyo",
//         relationship_type: "LOCATED_AT",
//         strength: 0.90
//       }
//     ],
//     "delight_project": [
//       {
//         to_entity_id: "python",
//         relationship_type: "USES",
//         strength: 0.85
//       },
//       {
//         to_entity_id: "react",
//         relationship_type: "USES",
//         strength: 0.85
//       }
//     ]
//   }
// }

// Filter by entity type
const projectGraph = await experimentalAPI.getEntityGraph(userId, "project");
```

---

## 🎨 Custom Components Using Phase 3

### Example: Memory Relationship Explorer

```typescript
'use client';

import { useState, useEffect } from 'react';
import experimentalAPI from '@/lib/api/experimental-client';

export function RelationshipExplorer({ memoryId }: { memoryId: string }) {
  const [relationships, setRelationships] = useState<any[]>([]);

  useEffect(() => {
    async function loadRelationships() {
      const result = await experimentalAPI.getRelationships(memoryId);
      setRelationships(result.relationships);
    }
    loadRelationships();
  }, [memoryId]);

  return (
    <div className="space-y-2">
      <h3 className="font-semibold">Related Memories</h3>
      {relationships.map(rel => (
        <div key={rel.id} className="p-3 bg-slate-800 rounded-lg">
          <div className="text-xs text-slate-400">{rel.relationship_type}</div>
          <div className="text-sm">{rel.related_memory.content}</div>
          <div className="text-xs text-slate-500">
            Strength: {(rel.strength * 100).toFixed(0)}%
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Example: Path Finder Between Memories

```typescript
'use client';

import { useState } from 'react';
import experimentalAPI from '@/lib/api/experimental-client';

export function PathFinder() {
  const [fromId, setFromId] = useState('');
  const [toId, setToId] = useState('');
  const [path, setPath] = useState<any>(null);

  async function findPath() {
    const result = await experimentalAPI.findShortestPath(fromId, toId);
    setPath(result);
  }

  return (
    <div className="space-y-4">
      <input
        value={fromId}
        onChange={e => setFromId(e.target.value)}
        placeholder="From Memory ID"
        className="w-full p-2 bg-slate-800 rounded"
      />
      <input
        value={toId}
        onChange={e => setToId(e.target.value)}
        placeholder="To Memory ID"
        className="w-full p-2 bg-slate-800 rounded"
      />
      <button onClick={findPath} className="px-4 py-2 bg-purple-600 rounded">
        Find Path
      </button>

      {path && (
        <div className="mt-4">
          <div className="text-sm text-slate-400">
            Path Length: {path.path_length} hop{path.path_length !== 1 && 's'}
          </div>
          <div className="mt-2 space-y-2">
            {path.path?.map((node: any, i: number) => (
              <div key={i} className="flex items-center gap-2">
                <div className="p-2 bg-slate-800 rounded flex-1">
                  <div className="text-xs text-slate-500">{node.entity_id}</div>
                  <div className="text-sm">{node.content}</div>
                </div>
                {node.relationship_to_next && (
                  <div className="text-xs text-purple-400">
                    → {node.relationship_to_next}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 🔗 Relationship Types Available

Use these when creating relationships:

- `WORKS_ON` - Working relationship (person → project)
- `LOCATED_AT` - Location relationship (entity → place)
- `PREFERS` - Preference relationship (person → thing)
- `BELONGS_TO` - Category membership
- `SIMILAR_TO` - Similarity relationship
- `DERIVED_FROM` - Derivation relationship
- `DEPENDS_ON` - Dependency relationship
- `PART_OF` - Composition relationship
- `RELATED_TO` - Generic relationship (automatically created)
- `USES` - Usage relationship (project → technology)

---

## 🧪 How It Works

### 1. Chat Creates Hierarchical Memories

When you send a message in the chat:

```
User: "I attended UCSB, MIT, and Georgia Tech. I love Yoshinoya's tonkatsu bowl in Tokyo."
```

The backend:
1. Extracts entities using EAV (Entity-Attribute-Value)
2. Creates hierarchical memories with nested attributes
3. Automatically creates relationships between entities from the same message

Result:
```
Entity: jack_education {
  entity_type: "person",
  attributes: {
    universities: ["UCSB", "MIT", "Georgia Tech"]
  }
}

Entity: yoshinoya {
  entity_type: "place",
  attributes: {
    type: "restaurant",
    favorite_dish: "tonkatsu bowl",
    location: "Tokyo"
  }
}

Relationship: jack_education → (RELATED_TO) → yoshinoya (strength: 0.8)
```

### 2. Graph Visualization Updates

The MemoryGraph component:
1. Fetches graph data via `/api/graph/visualize/{userId}`
2. Converts to React Flow format
3. Renders color-coded nodes and animated edges
4. Shows details in side panel on click

### 3. Query and Traverse

You can then:
- Find related memories by traversing the graph
- Discover indirect connections via shortest path
- Filter by entity type or relationship type
- Visualize the complete knowledge graph

---

## 📝 Example Workflow

```typescript
import experimentalAPI from '@/lib/api/experimental-client';

async function exampleWorkflow(userId: string) {
  // 1. Get all memories for visualization
  const graph = await experimentalAPI.getGraphVisualization(userId);
  console.log(`Found ${graph.nodes.length} entities and ${graph.edges.length} relationships`);

  // 2. Create a custom relationship
  const jackMemoryId = graph.nodes.find(n => n.label === 'jack_education')?.id;
  const delightMemoryId = graph.nodes.find(n => n.label === 'delight_project')?.id;

  if (jackMemoryId && delightMemoryId) {
    await experimentalAPI.createRelationship({
      from_memory_id: jackMemoryId,
      to_memory_id: delightMemoryId,
      relationship_type: 'WORKS_ON',
      strength: 0.98,
      metadata: { role: 'founder', start_date: '2025-01-01' }
    });
  }

  // 3. Explore relationships
  const jackRelationships = await experimentalAPI.getRelationships(jackMemoryId!);
  console.log(`Jack has ${jackRelationships.relationships.length} relationships`);

  // 4. Traverse from Jack to find all related entities
  const paths = await experimentalAPI.traverseGraph(jackMemoryId!, 3, 0.7);
  console.log(`Found ${paths.paths.length} paths from Jack`);

  // 5. Find connection between two entities
  const yoshinoyaMemoryId = graph.nodes.find(n => n.label === 'yoshinoya')?.id;
  if (jackMemoryId && yoshinoyaMemoryId) {
    const path = await experimentalAPI.findShortestPath(jackMemoryId, yoshinoyaMemoryId);
    if (path.path) {
      console.log(`Path from Jack to Yoshinoya: ${path.path_length} hops`);
      path.path.forEach(node => console.log(`- ${node.entity_id}`));
    }
  }
}
```

---

## 🎯 Key Benefits

1. **Hierarchical Storage**: Complex entities with nested attributes instead of flat facts
2. **Automatic Linking**: Entities from the same message are automatically related
3. **Rich Relationships**: 10+ typed relationship types with strength and metadata
4. **Graph Traversal**: Find connections and explore related memories
5. **Interactive Visualization**: See your knowledge graph visually
6. **Type-Safe API**: Full TypeScript support with comprehensive types

---

## 🚨 Troubleshooting

### Graph Not Loading

1. Check backend is running: `http://localhost:8001/health`
2. Check database connection in backend logs
3. Verify user has memories: Visit "Memories" tab first

### No Relationships Showing

1. Send a message in Chat to create memories
2. Check backend logs for hierarchical memory creation
3. Verify relationships in database: `/api/graph/relationships/{memory_id}`

### Graph Too Crowded

1. Use entity type filter: `getGraphVisualization(userId, "project")`
2. Adjust limit parameter: `getGraphVisualization(userId, undefined, 20)`
3. Use specific relationship queries instead of full graph

---

## 📚 Next Steps

- **Integrate Search**: Use graph-enhanced search for better results
- **Add PostgreSQL Indexes**: Optimize hierarchical queries (see PHASE3_SUMMARY.md)
- **Custom Visualizations**: Build domain-specific graph views
- **Relationship Analysis**: Find patterns and insights in connections

---

**Status**: Phase 3 is fully integrated and ready to use! 🚀
