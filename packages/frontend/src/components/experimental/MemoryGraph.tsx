/**
 * Memory Graph Visualization (Phase 3)
 *
 * Interactive graph visualization using React Flow showing:
 * - Entity nodes with hierarchical attributes
 * - Typed relationships between entities
 * - Graph traversal and exploration
 * - Node details on click
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Network,
  Loader2,
  AlertTriangle,
  X,
  Info,
  Maximize2,
  Filter,
} from 'lucide-react';
import experimentalAPI from '@/lib/api/experimental-client';

interface MemoryGraphProps {
  userId: string;
  entityType?: string;
}

interface GraphNode {
  id: string;
  label: string;
  type: string;
  content: string;
  attributes: Record<string, any>;
  created_at: string | null;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  strength: number;
  metadata: Record<string, any>;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// Node color mapping by entity type
const NODE_COLORS: Record<string, string> = {
  person: '#10b981', // green
  place: '#3b82f6', // blue
  project: '#8b5cf6', // purple
  organization: '#f59e0b', // amber
  object: '#ec4899', // pink
  event: '#06b6d4', // cyan
  unknown: '#6b7280', // gray
};

export function MemoryGraph({ userId, entityType }: MemoryGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Load graph data
  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8001/api/graph/visualize/${userId}${entityType ? `?entity_type=${entityType}` : ''}`
      );

      if (!response.ok) {
        throw new Error(`Failed to load graph: ${response.statusText}`);
      }

      const data: GraphData = await response.json();

      // Convert to React Flow format
      const flowNodes: Node[] = data.nodes.map((node, index) => ({
        id: node.id,
        type: 'default',
        position: {
          // Simple circular layout
          x: 400 + 300 * Math.cos((index / data.nodes.length) * 2 * Math.PI),
          y: 300 + 300 * Math.sin((index / data.nodes.length) * 2 * Math.PI),
        },
        data: {
          label: (
            <div className="text-xs font-medium text-center">
              <div className="font-semibold">{node.label}</div>
              <div className="text-[10px] text-gray-500">{node.type}</div>
            </div>
          ),
          node: node, // Store full node data
        },
        style: {
          background: NODE_COLORS[node.type] || NODE_COLORS.unknown,
          color: 'white',
          border: '2px solid rgba(255,255,255,0.3)',
          borderRadius: '8px',
          padding: '10px',
          minWidth: '120px',
        },
      }));

      const flowEdges: Edge[] = data.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        animated: edge.strength > 0.8,
        style: {
          stroke: `rgba(148, 163, 184, ${edge.strength})`,
          strokeWidth: 1 + edge.strength,
        },
        labelStyle: {
          fill: '#94a3b8',
          fontSize: 10,
        },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err: any) {
      console.error('Failed to load graph:', err);
      setError(err.message || 'Failed to load graph');
    } finally {
      setLoading(false);
    }
  }, [userId, entityType, setNodes, setEdges]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data.node);
  }, []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="relative h-full w-full bg-gradient-to-br from-background via-card to-background rounded-xl shadow-2xl overflow-hidden border border-border">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-card/50 backdrop-blur-xl border-b border-border px-6 py-4 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary to-secondary rounded-lg">
              <Network className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Memory Graph</h2>
              <p className="text-sm text-muted-foreground">
                {nodes.length} entities, {edges.length} relationships
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-lg border transition-all ${
                showFilters
                  ? 'bg-primary/20 border-primary/30 text-primary/90'
                  : 'bg-card/50 border-border text-foreground/80 hover:text-foreground'
              }`}
            >
              <Filter className="w-4 h-4" />
            </button>

            <button
              onClick={loadGraph}
              className="p-2 bg-card/50 border border-border rounded-lg text-foreground/80 hover:text-foreground transition-all"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Network className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Graph Canvas */}
      <div className="h-full w-full pt-20">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">Loading graph...</span>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full p-12">
            <div className="text-center max-w-md">
              <AlertTriangle className="w-12 h-12 text-destructive mx-auto mb-4" />
              <p className="text-lg font-medium text-destructive mb-2">Error loading graph</p>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
          </div>
        ) : nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full p-12">
            <div className="text-center max-w-md">
              <Network className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
              <p className="text-lg font-medium text-muted-foreground mb-2">No graph data</p>
              <p className="text-sm text-muted-foreground/80">
                Start chatting to create hierarchical memories and build your knowledge graph!
              </p>
            </div>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
            className="bg-transparent"
          >
            <Background color="#475569" gap={16} />
            <Controls className="bg-card/90 border border-border" />
            <MiniMap
              className="bg-card/90 border border-border"
              nodeColor={(node) => {
                const nodeData = node.data?.node as GraphNode | undefined;
                return NODE_COLORS[nodeData?.type || 'unknown'] || NODE_COLORS.unknown;
              }}
            />

            <Panel position="bottom-left" className="bg-card/90 border border-border rounded-lg p-4">
              <div className="text-xs text-foreground/80 space-y-1">
                <div className="font-semibold mb-2">Legend</div>
                {Object.entries(NODE_COLORS).map(([type, color]) => (
                  <div key={type} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded"
                      style={{ backgroundColor: color }}
                    />
                    <span className="capitalize">{type}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </ReactFlow>
        )}
      </div>

      {/* Node Detail Panel */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ x: 400 }}
            animate={{ x: 0 }}
            exit={{ x: 400 }}
            className="absolute top-0 right-0 bottom-0 w-96 bg-card/95 backdrop-blur-xl border-l border-border shadow-2xl z-20 overflow-y-auto"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div
                    className="inline-block px-2 py-1 rounded text-xs font-medium text-white mb-2"
                    style={{ backgroundColor: NODE_COLORS[selectedNode.type] || NODE_COLORS.unknown }}
                  >
                    {selectedNode.type}
                  </div>
                  <h3 className="text-xl font-semibold text-white">{selectedNode.label}</h3>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-2 hover:bg-border rounded-lg transition-all"
                >
                  <X className="w-4 h-4 text-foreground/80" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Content</h4>
                  <p className="text-sm text-foreground leading-relaxed">
                    {selectedNode.content}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Attributes</h4>
                  <div className="space-y-2">
                    {Object.entries(selectedNode.attributes).map(([key, value]) => (
                      <div key={key} className="bg-border/50 rounded-lg p-3">
                        <div className="text-xs font-medium text-muted-foreground mb-1">{key}</div>
                        <div className="text-sm text-foreground">
                          {Array.isArray(value)
                            ? value.join(', ')
                            : typeof value === 'object'
                            ? JSON.stringify(value, null, 2)
                            : String(value)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedNode.created_at && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Created</h4>
                    <p className="text-sm text-foreground">
                      {new Date(selectedNode.created_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
