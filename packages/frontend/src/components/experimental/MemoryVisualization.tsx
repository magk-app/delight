/**
 * Memory Visualization Component (Modernized)
 *
 * Dark theme memory browser with:
 * - Lucide React icons (no emojis)
 * - Glassmorphism effects
 * - List and graph views
 * - Filter, search, and delete functionality
 * - Edit capabilities
 */

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  List,
  Network,
  RefreshCw,
  Search,
  Filter,
  Trash2,
  Edit2,
  Calendar,
  Tag,
  Brain,
  Loader2,
  AlertTriangle,
  X,
} from 'lucide-react';
import { useMemories } from '@/lib/hooks/useExperimentalAPI';
import { Memory } from '@/lib/api/experimental-client';
import { EditMemoryModal } from './EditMemoryModal';
import { CleanupPanel } from './CleanupPanel';

type ViewMode = 'list' | 'graph';

export function MemoryVisualization({ userId }: { userId: string }) {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingMemory, setEditingMemory] = useState<Memory | null>(null);
  const [memoryLimit, setMemoryLimit] = useState<number>(50);
  const [showCleanupPanel, setShowCleanupPanel] = useState(false);

  const { memories, loading, error, refresh, deleteMemory } = useMemories({
    user_id: userId,
    memory_type: selectedType === 'all' ? undefined : selectedType,
    limit: memoryLimit,
    autoRefresh: true,
    refreshInterval: 60000, // Refresh every 1 minute (manual refresh button available)
  });

  const filteredMemories = memories.filter((memory) =>
    searchQuery
      ? memory.content.toLowerCase().includes(searchQuery.toLowerCase())
      : true
  );

  const handleDelete = async (memoryId: string) => {
    if (confirm('Are you sure you want to delete this memory?')) {
      try {
        await deleteMemory(memoryId);
      } catch (err) {
        alert('Failed to delete memory: ' + (err as Error).message);
      }
    }
  };

  const handleEdit = (memory: Memory) => {
    setEditingMemory(memory);
  };

  const handleUpdate = async (memoryId: string, content: string) => {
    try {
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');
      await experimentalAPI.updateMemory(memoryId, { content });
      setEditingMemory(null);
      refresh(); // Refresh the list
    } catch (err) {
      alert('Failed to update memory: ' + (err as Error).message);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl shadow-2xl overflow-hidden border border-slate-700/50">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Memory Browser</h2>
              <p className="text-sm text-slate-400">
                View and manage your AI&apos;s knowledge base
              </p>
            </div>
          </div>
          <button
            onClick={refresh}
            className="p-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 hover:text-white hover:border-purple-500/50 transition-all"
            title="Refresh memories"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex rounded-lg border border-slate-700/50 overflow-hidden bg-slate-900/50">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 text-sm font-medium flex items-center gap-2 transition-all ${
                viewMode === 'list'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <List className="w-4 h-4" />
              <span>List View</span>
            </button>
            <button
              onClick={() => setViewMode('graph')}
              className={`px-4 py-2 text-sm font-medium flex items-center gap-2 border-l border-slate-700/50 transition-all ${
                viewMode === 'graph'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Network className="w-4 h-4" />
              <span>Graph View</span>
            </button>
          </div>

          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 text-sm bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
          >
            <option value="all">All Types</option>
            <option value="personal">Personal</option>
            <option value="project">Project</option>
            <option value="task">Task</option>
            <option value="fact">Fact</option>
          </select>

          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memories..."
              className="w-full pl-10 pr-4 py-2 text-sm bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Memory Limit Selector */}
          <select
            value={memoryLimit}
            onChange={(e) => setMemoryLimit(Number(e.target.value))}
            className="px-4 py-2 text-sm bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            title="Number of memories to load"
          >
            <option value={50}>50 memories</option>
            <option value={100}>100 memories</option>
            <option value={200}>200 memories</option>
            <option value={500}>500 memories</option>
            <option value={10000}>All memories</option>
          </select>

          {/* Cleanup Button */}
          <button
            onClick={() => setShowCleanupPanel(!showCleanupPanel)}
            className={`px-4 py-2 text-sm font-medium rounded-lg border transition-all flex items-center gap-2 ${
              showCleanupPanel
                ? 'bg-red-500/20 border-red-500/30 text-red-300'
                : 'bg-slate-900/50 border-slate-700/50 text-slate-300 hover:text-white hover:border-purple-500/50'
            }`}
            title="Clean up problematic memories"
          >
            <Trash2 className="w-4 h-4" />
            <span>Cleanup</span>
          </button>
        </div>

        {/* Stats Bar */}
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-400">
            Total: <strong className="text-white">{filteredMemories.length}</strong>
          </span>
          {selectedType !== 'all' && (
            <span className="flex items-center gap-1.5 text-slate-400">
              <Filter className="w-3.5 h-3.5" />
              Filtered by: <strong className="text-purple-400">{selectedType}</strong>
            </span>
          )}
          {searchQuery && (
            <span className="flex items-center gap-1.5 text-slate-400">
              <Search className="w-3.5 h-3.5" />
              Search: <strong className="text-purple-400">&quot;{searchQuery}&quot;</strong>
            </span>
          )}
        </div>
      </div>

      {/* Cleanup Panel */}
      <AnimatePresence>
        {showCleanupPanel && (
          <CleanupPanel
            userId={userId}
            onCleanupComplete={() => {
              refresh();
              setShowCleanupPanel(false);
            }}
          />
        )}
      </AnimatePresence>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
              <span className="text-sm text-slate-400">Loading memories...</span>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full p-12">
            <div className="text-center max-w-md">
              <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-red-400 mb-2">Error loading memories</p>
              <p className="text-sm text-slate-400 mb-4">{error.message}</p>
              <p className="text-xs text-slate-500">
                Make sure the experimental backend server is running on port 8001
              </p>
            </div>
          </div>
        ) : filteredMemories.length === 0 ? (
          <div className="flex items-center justify-center h-full p-12">
            <div className="text-center max-w-md">
              <Brain className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-lg font-medium text-slate-400 mb-2">No memories found</p>
              <p className="text-sm text-slate-500">
                {searchQuery || selectedType !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Start chatting to create some memories!'}
              </p>
            </div>
          </div>
        ) : viewMode === 'list' ? (
          <ListView memories={filteredMemories} onDelete={handleDelete} onEdit={handleEdit} />
        ) : (
          <GraphViewPlaceholder />
        )}
      </div>

      {/* Edit Modal */}
      {editingMemory && (
        <EditMemoryModal
          memory={editingMemory}
          onClose={() => setEditingMemory(null)}
          onSave={handleUpdate}
        />
      )}
    </div>
  );
}

// ============================================================================
// List View
// ============================================================================

function ListView({
  memories,
  onDelete,
  onEdit,
}: {
  memories: Memory[];
  onDelete: (id: string) => void;
  onEdit: (memory: Memory) => void;
}) {
  return (
    <div className="p-6 space-y-4">
      {memories.map((memory, idx) => (
        <motion.div
          key={memory.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05, duration: 0.3 }}
          className="group bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-5 hover:border-purple-500/30 hover:shadow-lg transition-all"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              {/* Type Badge */}
              <div className="flex items-center gap-2 mb-3">
                <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {memory.memory_type}
                </span>
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{new Date(memory.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Content */}
              <p className="text-slate-200 text-sm leading-relaxed mb-3">
                {memory.content}
              </p>

              {/* Categories */}
              {memory.metadata?.categories && memory.metadata.categories.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {memory.metadata.categories.map((category: string, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/20"
                    >
                      <Tag className="w-3 h-3" />
                      {category}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => onEdit(memory)}
                className="p-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-all"
                title="Edit memory"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDelete(memory.id)}
                className="p-2 bg-red-500/10 hover:bg-red-500/20 rounded-lg text-red-400 hover:text-red-300 transition-all border border-red-500/20"
                title="Delete memory"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

// ============================================================================
// Graph View (Placeholder)
// ============================================================================

function GraphViewPlaceholder() {
  return (
    <div className="flex items-center justify-center h-full p-12">
      <div className="text-center max-w-md">
        <Network className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <p className="text-lg font-medium text-slate-300 mb-2">Graph View Coming Soon</p>
        <p className="text-sm text-slate-400 mb-4">
          This will display an interactive knowledge graph of your memories using D3.js or React Flow
        </p>
        <p className="text-xs text-slate-500">
          For now, use the List View to browse your memories
        </p>
      </div>
    </div>
  );
}
