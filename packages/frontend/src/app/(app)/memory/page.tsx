/**
 * Memory Studio - View and organize 3-tier memory
 * Supports filtering, search, and memory detail view
 */

'use client';

import { useState } from 'react';
import { mockMemories } from '@/lib/mock/data';
import { MEMORY_TIER, MEMORY_TIER_INFO } from '@/lib/constants';
import type { Memory, MemoryTier } from '@/lib/types';

export default function MemoryPage() {
  const [selectedTier, setSelectedTier] = useState<MemoryTier | 'all'>('all');
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredMemories = mockMemories.filter((memory) => {
    const matchesTier = selectedTier === 'all' || memory.tier === selectedTier;
    const matchesSearch =
      searchQuery === '' ||
      memory.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memory.tags?.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesTier && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Memory Studio</h1>
        <p className="mt-1 text-sm text-gray-600">
          Explore and organize your 3-tier memory system
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar - Filters */}
        <div className="space-y-6">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search memories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Memory Tier Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Memory Tier
            </label>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedTier('all')}
                className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                  selectedTier === 'all'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Memories
              </button>
              {Object.values(MEMORY_TIER).map((tier) => {
                const info = MEMORY_TIER_INFO[tier];
                return (
                  <button
                    key={tier}
                    onClick={() => setSelectedTier(tier)}
                    className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                      selectedTier === tier
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <div className="font-medium">{info.label}</div>
                    <div className="text-xs opacity-75">{info.retention}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Stats */}
          <div className="rounded-lg border bg-white p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Statistics</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Memories:</span>
                <span className="font-medium">{mockMemories.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Showing:</span>
                <span className="font-medium">{filteredMemories.length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Area - Memory List and Detail */}
        <div className="lg:col-span-3 space-y-4">
          {/* Memory List */}
          {filteredMemories.length === 0 ? (
            <div className="text-center py-12 text-gray-600">
              <p>No memories found matching your filters.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredMemories.map((memory) => {
                const tierInfo = MEMORY_TIER_INFO[memory.tier];
                const isSelected = selectedMemory?.id === memory.id;

                return (
                  <button
                    key={memory.id}
                    onClick={() => setSelectedMemory(memory)}
                    className={`w-full text-left p-4 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/5 shadow-md'
                        : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                    }`}
                    aria-pressed={isSelected}
                    aria-label={`View memory: ${memory.content.substring(0, 50)}...`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span
                        className="text-xs font-medium px-2 py-1 rounded-full"
                        style={{
                          backgroundColor: `${tierInfo.color}20`,
                          color: tierInfo.color,
                        }}
                      >
                        {tierInfo.label}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(memory.createdAt).toLocaleDateString()}
                      </span>
                    </div>

                    <p className="text-sm text-gray-800 mb-2 line-clamp-2">
                      {memory.content}
                    </p>

                    {memory.tags && memory.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {memory.tags.map((tag) => (
                          <span
                            key={tag}
                            className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          )}

          {/* Memory Detail Panel */}
          {selectedMemory && (
            <div className="rounded-lg border bg-white p-6 sticky top-24">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Memory Details</h3>
                <button
                  onClick={() => setSelectedMemory(null)}
                  className="text-gray-400 hover:text-gray-600"
                  aria-label="Close memory details panel"
                >
                  ✕
                </button>
              </div>

              {/* Memory Content */}
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Content</label>
                  <p className="mt-1 text-sm text-gray-800 leading-relaxed">
                    {selectedMemory.content}
                  </p>
                </div>

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <label className="text-xs font-medium text-gray-600">Type</label>
                    <p className="text-sm text-gray-900">
                      {MEMORY_TIER_INFO[selectedMemory.tier].label}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-600">Retention</label>
                    <p className="text-sm text-gray-900">
                      {MEMORY_TIER_INFO[selectedMemory.tier].retention}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-600">Created</label>
                    <p className="text-sm text-gray-900">
                      {new Date(selectedMemory.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-600">Last Accessed</label>
                    <p className="text-sm text-gray-900">
                      {new Date(selectedMemory.accessedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Tags */}
                {selectedMemory.tags && selectedMemory.tags.length > 0 && (
                  <div className="pt-4 border-t">
                    <label className="text-xs font-medium text-gray-600 block mb-2">
                      Tags
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {selectedMemory.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="pt-4 border-t flex gap-2">
                  <button className="flex-1 px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors">
                    Add Tag
                  </button>
                  <button className="flex-1 px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors">
                    Pin Memory
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* TODO Comment */}
      <div className="text-xs text-gray-500 italic mt-8">
        // TODO: Wire to /api/v1/memories with real vector search and filtering
      </div>
    </div>
  );
}
