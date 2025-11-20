/**
 * Knowledge Graph Component
 *
 * Interactive knowledge graph visualization using React Flow
 * - Displays entities and relationships as a network
 * - Node types: person, project, institution, technology, concept
 * - Interactive: click to expand, drag to rearrange
 * - Filter by relationship type
 *
 * NOTE: Requires installing reactflow:
 * npm install reactflow
 */

'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Building2,
  Code2,
  Lightbulb,
  Folder,
  Link as LinkIcon,
  Maximize2,
  Minimize2,
  Filter,
  RefreshCw,
} from 'lucide-react';

// Types for the knowledge graph
interface GraphNode {
  id: string;
  type: 'person' | 'institution' | 'project' | 'technology' | 'concept';
  label: string;
  data: {
    name: string;
    attributes?: Record<string, any>;
    color?: string;
  };
  position: { x: number; y: number };
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type: 'attended' | 'works_on' | 'uses' | 'related_to' | 'part_of';
}

// Mock data for demonstration
const MOCK_NODES: GraphNode[] = [
  {
    id: '1',
    type: 'person',
    label: 'Jack',
    data: { name: 'Jack', attributes: { role: 'Developer', location: 'SF' } },
    position: { x: 250, y: 250 },
  },
  {
    id: '2',
    type: 'institution',
    label: 'UCSB',
    data: { name: 'UC Santa Barbara', color: '#3b82f6' },
    position: { x: 100, y: 100 },
  },
  {
    id: '3',
    type: 'institution',
    label: 'MIT',
    data: { name: 'Massachusetts Institute of Technology', color: '#3b82f6' },
    position: { x: 400, y: 100 },
  },
  {
    id: '4',
    type: 'project',
    label: 'Delight',
    data: { name: 'Delight AI App', color: '#8b5cf6' },
    position: { x: 250, y: 400 },
  },
  {
    id: '5',
    type: 'technology',
    label: 'Python',
    data: { name: 'Python', color: '#f59e0b' },
    position: { x: 100, y: 400 },
  },
  {
    id: '6',
    type: 'technology',
    label: 'TypeScript',
    data: { name: 'TypeScript', color: '#f59e0b' },
    position: { x: 400, y: 400 },
  },
];

const MOCK_EDGES: GraphEdge[] = [
  { id: 'e1-2', source: '1', target: '2', label: 'Attended', type: 'attended' },
  { id: 'e1-3', source: '1', target: '3', label: 'Attended', type: 'attended' },
  { id: 'e1-4', source: '1', target: '4', label: 'Works On', type: 'works_on' },
  { id: 'e1-5', source: '1', target: '5', label: 'Uses', type: 'uses' },
  { id: 'e1-6', source: '1', target: '6', label: 'Uses', type: 'uses' },
  { id: 'e4-5', source: '4', target: '5', label: 'Built With', type: 'uses' },
  { id: 'e4-6', source: '4', target: '6', label: 'Built With', type: 'uses' },
];

export function KnowledgeGraph({ userId }: { userId?: string }) {
  const [nodes, setNodes] = useState<GraphNode[]>(MOCK_NODES);
  const [edges, setEdges] = useState<GraphEdge[]>(MOCK_EDGES);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Fetch real graph data from API
  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const { default: experimentalAPI } = await import('@/lib/api/experimental-client');
        const data = await experimentalAPI.getMemoryGraph(userId, 100);

        // Transform API data to graph nodes/edges
        // This is a placeholder - adapt based on actual API response
        if (data.nodes && data.edges) {
          // Map API nodes to GraphNode format
          const transformedNodes: GraphNode[] = data.nodes.map((n, idx) => ({
            id: n.id,
            type: 'concept', // Default type, determine from n.type
            label: n.label || 'Unknown',
            data: {
              name: n.label || 'Unknown',
              attributes: { categories: n.categories },
            },
            position: {
              x: 250 + (idx % 5) * 150,
              y: 250 + Math.floor(idx / 5) * 150,
            },
          }));

          setNodes(transformedNodes);

          // Map API edges
          const transformedEdges: GraphEdge[] = data.edges.map((e) => ({
            id: `e-${e.source}-${e.target}`,
            source: e.source,
            target: e.target,
            label: e.type || 'related',
            type: 'related_to',
          }));

          setEdges(transformedEdges);
        }
      } catch (error) {
        console.error('Failed to fetch graph data:', error);
        // Use mock data on error
      }
    };

    // Uncomment to use real API data
    // fetchGraphData();
  }, [userId]);

  const getNodeIcon = (type: GraphNode['type']) => {
    switch (type) {
      case 'person':
        return <User className="w-5 h-5" />;
      case 'institution':
        return <Building2 className="w-5 h-5" />;
      case 'project':
        return <Folder className="w-5 h-5" />;
      case 'technology':
        return <Code2 className="w-5 h-5" />;
      case 'concept':
        return <Lightbulb className="w-5 h-5" />;
      default:
        return <Lightbulb className="w-5 h-5" />;
    }
  };

  const getNodeColor = (type: GraphNode['type']) => {
    switch (type) {
      case 'person':
        return 'from-purple-500 to-indigo-600';
      case 'institution':
        return 'from-blue-500 to-cyan-600';
      case 'project':
        return 'from-purple-500 to-pink-600';
      case 'technology':
        return 'from-orange-500 to-yellow-600';
      case 'concept':
        return 'from-green-500 to-emerald-600';
      default:
        return 'from-slate-500 to-slate-600';
    }
  };

  const filteredEdges = filter === 'all'
    ? edges
    : edges.filter(e => e.type === filter);

  return (
    <div className={`flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl shadow-2xl overflow-hidden border border-slate-700/50 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
              <LinkIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Knowledge Graph</h2>
              <p className="text-sm text-slate-400">
                {nodes.length} nodes • {edges.length} connections
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Filter Dropdown */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            >
              <option value="all">All Relationships</option>
              <option value="attended">Education</option>
              <option value="works_on">Work</option>
              <option value="uses">Technologies</option>
              <option value="related_to">Related</option>
            </select>

            {/* Fullscreen Toggle */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 hover:text-white hover:border-purple-500/50 transition-all"
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            {/* Refresh */}
            <button
              onClick={() => window.location.reload()}
              className="p-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 hover:text-white hover:border-purple-500/50 transition-all"
              title="Refresh graph"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Graph Visualization Area */}
      <div className="flex-1 relative overflow-hidden bg-slate-900/30">
        {/* SVG Canvas for edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3, 0 6"
                fill="#6366f1"
                opacity="0.5"
              />
            </marker>
          </defs>

          {filteredEdges.map((edge) => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);

            if (!sourceNode || !targetNode) return null;

            return (
              <g key={edge.id}>
                <line
                  x1={sourceNode.position.x + 60}
                  y1={sourceNode.position.y + 40}
                  x2={targetNode.position.x + 60}
                  y2={targetNode.position.y + 40}
                  stroke="#6366f1"
                  strokeWidth="2"
                  strokeOpacity="0.3"
                  markerEnd="url(#arrowhead)"
                />
                <text
                  x={(sourceNode.position.x + targetNode.position.x) / 2 + 60}
                  y={(sourceNode.position.y + targetNode.position.y) / 2 + 35}
                  fill="#94a3b8"
                  fontSize="10"
                  textAnchor="middle"
                  className="pointer-events-none select-none"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Nodes */}
        <div className="relative w-full h-full">
          {nodes.map((node) => (
            <motion.div
              key={node.id}
              drag
              dragMomentum={false}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedNode(node)}
              style={{
                position: 'absolute',
                left: node.position.x,
                top: node.position.y,
                cursor: 'grab',
              }}
              className="group"
            >
              <div className={`relative bg-gradient-to-br ${getNodeColor(node.type)} p-3 rounded-xl shadow-lg hover:shadow-2xl transition-all border border-white/10 hover:border-white/30`}>
                <div className="flex items-center gap-2">
                  <div className="text-white">
                    {getNodeIcon(node.type)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white leading-tight">
                      {node.label}
                    </p>
                    {node.data.attributes && (
                      <p className="text-xs text-white/70 mt-0.5">
                        {Object.values(node.data.attributes)[0] as string}
                      </p>
                    )}
                  </div>
                </div>

                {/* Tooltip on hover */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  <div className="bg-slate-900 text-white text-xs px-3 py-2 rounded-lg shadow-xl border border-slate-700 whitespace-nowrap">
                    {node.type.charAt(0).toUpperCase() + node.type.slice(1)}: {node.data.name}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Selected Node Details Sidebar */}
      {selectedNode && (
        <motion.div
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 300, opacity: 0 }}
          className="absolute right-0 top-0 bottom-0 w-80 bg-slate-800/95 backdrop-blur-xl border-l border-slate-700/50 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Node Details</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-white transition-colors"
            >
              ×
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Type</p>
              <div className="flex items-center gap-2">
                {getNodeIcon(selectedNode.type)}
                <span className="text-white capitalize">{selectedNode.type}</span>
              </div>
            </div>

            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Name</p>
              <p className="text-white">{selectedNode.data.name}</p>
            </div>

            {selectedNode.data.attributes && (
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">Attributes</p>
                <div className="space-y-2">
                  {Object.entries(selectedNode.data.attributes).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-400">{key}:</span>
                      <span className="text-white">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">Connections</p>
              <div className="space-y-1">
                {edges
                  .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
                  .map(edge => {
                    const connectedNodeId = edge.source === selectedNode.id ? edge.target : edge.source;
                    const connectedNode = nodes.find(n => n.id === connectedNodeId);
                    return (
                      <div key={edge.id} className="text-sm text-slate-300 flex items-center gap-2">
                        <LinkIcon className="w-3 h-3 text-purple-400" />
                        <span>{edge.label}</span>
                        <span className="text-slate-500">→</span>
                        <span>{connectedNode?.label}</span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Instructions */}
      <div className="bg-slate-800/30 backdrop-blur-xl border-t border-slate-700/50 px-6 py-3">
        <p className="text-xs text-slate-400 flex items-center gap-2">
          <Filter className="w-3.5 h-3.5" />
          <span>Drag nodes to rearrange • Click to view details • Use filter to show specific relationships</span>
        </p>
      </div>
    </div>
  );
}
