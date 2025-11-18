/**
 * Memory Visualization Component
 *
 * Displays memories in list and graph views
 * - Filter by type, category
 * - Search memories
 * - Delete memories
 * - View memory details
 */

'use client';

import React, { useState } from 'react';
import { useMemories } from '@/lib/hooks/useExperimentalAPI';
import { Memory } from '@/lib/api/experimental-client';

type ViewMode = 'list' | 'graph';

export function MemoryVisualization({ userId }: { userId?: string }) {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const { memories, loading, error, refresh, deleteMemory } = useMemories({
    user_id: userId,
    memory_type: selectedType === 'all' ? undefined : selectedType,
    limit: 50,
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

  return (
    <div className="space-y-4">
      {/* Header & Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Memory Browser</h2>
            <p className="text-sm text-gray-600 mt-1">
              View and manage your AI&apos;s memory
            </p>
          </div>
          <button
            onClick={refresh}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            🔄 Refresh
          </button>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 text-sm font-medium ${
                viewMode === 'list'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              📝 List View
            </button>
            <button
              onClick={() => setViewMode('graph')}
              className={`px-4 py-2 text-sm font-medium border-l border-gray-300 ${
                viewMode === 'graph'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              🕸️ Graph View
            </button>
          </div>

          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Types</option>
            <option value="personal">Personal</option>
            <option value="project">Project</option>
            <option value="task">Task</option>
            <option value="fact">Fact</option>
          </select>

          {/* Search */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search memories..."
            className="flex-1 px-4 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Stats Bar */}
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>
            Total: <strong>{filteredMemories.length}</strong>
          </span>
          {selectedType !== 'all' && (
            <span>
              Filtered by: <strong className="text-indigo-600">{selectedType}</strong>
            </span>
          )}
          {searchQuery && (
            <span>
              Search: <strong className="text-indigo-600">&quot;{searchQuery}&quot;</strong>
            </span>
          )}
        </div>
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="inline-flex items-center gap-3 text-gray-600">
            <svg
              className="animate-spin h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading memories...</span>
          </div>
        </div>
      ) : error ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-red-600">
            <p className="text-lg font-medium">Error loading memories</p>
            <p className="text-sm mt-2">{error.message}</p>
            <p className="text-xs text-gray-500 mt-4">
              Make sure the experimental backend server is running on port 8001
            </p>
          </div>
        </div>
      ) : filteredMemories.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-500">
            <p className="text-lg font-medium">No memories found</p>
            <p className="text-sm mt-2">
              {searchQuery || selectedType !== 'all'
                ? 'Try adjusting your filters'
                : 'Start chatting to create some memories!'}
            </p>
          </div>
        </div>
      ) : viewMode === 'list' ? (
        <ListView memories={filteredMemories} onDelete={handleDelete} />
      ) : (
        <GraphView />
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
}: {
  memories: Memory[];
  onDelete: (id: string) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow divide-y divide-gray-200">
      {memories.map((memory) => (
        <div
          key={memory.id}
          className="p-6 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              {/* Type Badge */}
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                  {memory.memory_type}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(memory.created_at).toLocaleDateString()}
                </span>
              </div>

              {/* Content */}
              <p className="text-gray-800 text-sm leading-relaxed">
                {memory.content}
              </p>

              {/* Categories */}
              {memory.metadata?.categories && memory.metadata.categories.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {memory.metadata.categories.map((category: string, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                    >
                      {category}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <button
              onClick={() => onDelete(memory.id)}
              className="text-red-600 hover:text-red-800 text-sm font-medium"
              title="Delete memory"
            >
              🗑️
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Graph View (Placeholder)
// ============================================================================

function GraphView() {
  return (
    <div className="bg-white rounded-lg shadow p-12 text-center">
      <div className="text-gray-500">
        <p className="text-lg font-medium">Graph View Coming Soon</p>
        <p className="text-sm mt-2">
          This will display an interactive knowledge graph of your memories using D3.js
        </p>
        <p className="text-xs text-gray-400 mt-4">
          For now, use the List View to browse your memories
        </p>
      </div>
    </div>
  );
}
