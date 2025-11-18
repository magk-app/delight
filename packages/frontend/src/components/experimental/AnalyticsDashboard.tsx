/**
 * Analytics Dashboard Component
 *
 * Displays analytics and metrics:
 * - Memory statistics
 * - Token usage and costs
 * - Search performance
 * - Real-time updates
 */

'use client';

import React from 'react';
import { useMemoryStats, useTokenUsage } from '@/lib/hooks/useExperimentalAPI';

export function AnalyticsDashboard({ userId }: { userId?: string }) {
  const { stats, loading: statsLoading, error: statsError } = useMemoryStats(userId);
  const { usage, loading: usageLoading, error: usageError } = useTokenUsage(24);

  if (statsLoading || usageLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  if (statsError || usageError) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-red-600">
          <p className="text-lg font-medium">Error loading analytics</p>
          <p className="text-sm mt-2">
            {(statsError || usageError)?.message}
          </p>
          <p className="text-xs text-gray-500 mt-4">
            Make sure the experimental backend server is running on port 8001
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total Memories"
          value={stats?.total_memories || 0}
          icon="🧠"
          color="indigo"
        />
        <StatCard
          title="Total Embeddings"
          value={stats?.total_embeddings || 0}
          icon="🎯"
          color="purple"
        />
        <StatCard
          title="Total Tokens"
          value={usage?.total_tokens?.toLocaleString() || '0'}
          icon="📊"
          color="cyan"
        />
        <StatCard
          title="Total Cost"
          value={`$${usage?.total_cost?.toFixed(4) || '0.00'}`}
          icon="💰"
          color="green"
        />
      </div>

      {/* Memory Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Type */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Memory Distribution by Type
          </h3>
          {stats?.by_type && Object.keys(stats.by_type).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(stats.by_type).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-indigo-500" />
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {type}
                    </span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No data available</p>
          )}
        </div>

        {/* By Category */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Top Categories
          </h3>
          {stats?.by_category && Object.keys(stats.by_category).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(stats.by_category)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .slice(0, 5)
                .map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-cyan-500" />
                      <span className="text-sm font-medium text-gray-700">
                        {category}
                      </span>
                    </div>
                    <span className="text-sm font-bold text-gray-900">{count}</span>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No categories yet</p>
          )}
        </div>
      </div>

      {/* Token Usage by Model */}
      {usage?.by_model && Object.keys(usage.by_model).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Token Usage by Model (Last 24 Hours)
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tokens
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {Object.entries(usage.by_model).map(([model, data]) => (
                  <tr key={model} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {model}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {data.tokens.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      ${data.cost.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Stat Card Component
// ============================================================================

function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: string;
  color: 'indigo' | 'purple' | 'cyan' | 'green';
}) {
  const colorClasses = {
    indigo: 'bg-indigo-500',
    purple: 'bg-purple-500',
    cyan: 'bg-cyan-500',
    green: 'bg-green-500',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
