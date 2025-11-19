/**
 * Analytics Dashboard Component (Modernized)
 *
 * Dark theme analytics dashboard with:
 * - Lucide React icons (no emojis)
 * - Glass morphism effects
 * - Memory statistics
 * - Token usage and costs
 * - Real-time updates
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Target,
  BarChart3,
  DollarSign,
  TrendingUp,
  Database,
  Zap,
  Activity,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { useMemoryStats, useTokenUsage } from '@/lib/hooks/useExperimentalAPI';

export function AnalyticsDashboard({ userId }: { userId: string }) {
  const { stats, loading: statsLoading, error: statsError } = useMemoryStats(userId, true, 10000);
  const { usage, loading: usageLoading, error: usageError } = useTokenUsage(24, userId, true, 10000);

  const loading = statsLoading || usageLoading;
  const error = statsError || usageError;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700/50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
          <span className="text-sm text-slate-400">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700/50 p-12">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-red-400 mb-2">Error loading analytics</p>
          <p className="text-sm text-slate-400 mb-4">{error.message}</p>
          <p className="text-xs text-slate-500">
            Make sure the experimental backend server is running on port 8001
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl shadow-2xl overflow-hidden border border-slate-700/50">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Analytics Dashboard</h2>
            <p className="text-sm text-slate-400">
              Memory stats and usage metrics
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Memories"
            value={stats?.total_memories || 0}
            icon={<Brain className="w-5 h-5" />}
            color="purple"
            trend="+12%"
          />
          <StatCard
            title="Total Embeddings"
            value={stats?.total_embeddings || 0}
            icon={<Target className="w-5 h-5" />}
            color="indigo"
          />
          <StatCard
            title="Total Tokens"
            value={usage?.total_tokens?.toLocaleString() || '0'}
            icon={<Zap className="w-5 h-5" />}
            color="cyan"
            subtitle="Last 24h"
          />
          <StatCard
            title="Total Cost"
            value={`$${usage?.total_cost?.toFixed(4) || '0.0000'}`}
            icon={<DollarSign className="w-5 h-5" />}
            color="green"
            subtitle="Last 24h"
          />
        </div>

        {/* Memory Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* By Type */}
          <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">
                Memory Distribution by Type
              </h3>
            </div>
            {stats?.by_type && Object.keys(stats.by_type).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.by_type).map(([type, count], idx) => (
                  <motion.div
                    key={type}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="flex items-center justify-between group hover:bg-slate-700/30 rounded-lg p-2 transition-all"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500" />
                      <span className="text-sm font-medium text-slate-300 capitalize">
                        {type}
                      </span>
                    </div>
                    <span className="text-sm font-bold text-white">{count}</span>
                  </motion.div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No data available</p>
            )}
          </div>

          {/* By Category */}
          <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-white">
                Top Categories
              </h3>
            </div>
            {stats?.by_category && Object.keys(stats.by_category).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.by_category)
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .slice(0, 5)
                  .map(([category, count], idx) => (
                    <motion.div
                      key={category}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="group hover:bg-slate-700/30 rounded-lg p-2 transition-all"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500" />
                          <span className="text-sm font-medium text-slate-300">
                            {category}
                          </span>
                        </div>
                        <span className="text-sm font-bold text-white">{count}</span>
                      </div>
                      {/* Progress bar */}
                      <div className="w-full h-1 bg-slate-700/50 rounded-full overflow-hidden ml-4">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${(Number(count) / (stats.total_memories || 1)) * 100}%` }}
                          transition={{ duration: 0.6, delay: idx * 0.1 }}
                          className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                        />
                      </div>
                    </motion.div>
                  ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No categories yet</p>
            )}
          </div>
        </div>

        {/* Token Usage by Model */}
        {usage?.by_model && Object.keys(usage.by_model).length > 0 && (
          <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <h3 className="text-lg font-semibold text-white">
                Token Usage by Model (Last 24 Hours)
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Tokens
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Cost
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/30">
                  {Object.entries(usage.by_model).map(([model, data], idx) => (
                    <motion.tr
                      key={model}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="hover:bg-slate-700/30 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm font-medium text-white">
                        {model}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {data.tokens.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-green-400 font-mono">
                        ${data.cost.toFixed(4)}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Analytics Info */}
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <Activity className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-green-300 mb-1">
                Real-Time Analytics Active
              </p>
              <p className="text-xs text-green-200/80">
                All data is now tracked in real-time from the database. Memory stats and token usage are automatically updated with each interaction.
              </p>
            </div>
          </div>
        </div>
      </div>
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
  trend,
  subtitle,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'purple' | 'indigo' | 'cyan' | 'green';
  trend?: string;
  subtitle?: string;
}) {
  const colorClasses = {
    purple: 'from-purple-500 to-purple-600',
    indigo: 'from-indigo-500 to-indigo-600',
    cyan: 'from-cyan-500 to-cyan-600',
    green: 'from-green-500 to-green-600',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-5 hover:border-purple-500/30 hover:shadow-lg transition-all"
    >
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-slate-400">{title}</p>
        <div className={`p-2 bg-gradient-to-br ${colorClasses[color]} rounded-lg`}>
          {icon}
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <p className="text-2xl font-bold text-white">{value}</p>
        {trend && (
          <span className="text-xs text-green-400 font-medium flex items-center gap-0.5">
            <TrendingUp className="w-3 h-3" />
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
      )}
    </motion.div>
  );
}
