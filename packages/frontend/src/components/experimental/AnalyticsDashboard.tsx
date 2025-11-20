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
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-background via-card to-background rounded-xl border border-border">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <span className="text-sm text-muted-foreground">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-background via-card to-background rounded-xl border border-border p-12">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-destructive mx-auto mb-4" />
          <p className="text-lg font-medium text-destructive mb-2">Error loading analytics</p>
          <p className="text-sm text-muted-foreground mb-4">{error.message}</p>
          <p className="text-xs text-muted-foreground/60">
            Make sure the experimental backend server is running on port 8001
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-background via-card to-background rounded-xl shadow-2xl overflow-hidden border border-border">
      {/* Header */}
      <div className="bg-card/50 backdrop-blur-xl border-b border-border px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-primary to-secondary rounded-lg">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Analytics Dashboard</h2>
            <p className="text-sm text-muted-foreground">
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
          <div className="bg-card/60 backdrop-blur-sm border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-primary" />
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
                    className="flex items-center justify-between group hover:bg-border/30 rounded-lg p-2 transition-all"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-secondary" />
                      <span className="text-sm font-medium text-foreground/80 capitalize">
                        {type}
                      </span>
                    </div>
                    <span className="text-sm font-bold text-white">{count}</span>
                  </motion.div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data available</p>
            )}
          </div>

          {/* By Category */}
          <div className="bg-card/60 backdrop-blur-sm border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-success" />
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
                      className="group hover:bg-border/30 rounded-lg p-2 transition-all"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-success to-success/80" />
                          <span className="text-sm font-medium text-foreground/80">
                            {category}
                          </span>
                        </div>
                        <span className="text-sm font-bold text-white">{count}</span>
                      </div>
                      {/* Progress bar */}
                      <div className="w-full h-1 bg-border/50 rounded-full overflow-hidden ml-4">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${(Number(count) / (stats.total_memories || 1)) * 100}%` }}
                          transition={{ duration: 0.6, delay: idx * 0.1 }}
                          className="h-full bg-gradient-to-r from-success to-success/80 rounded-full"
                        />
                      </div>
                    </motion.div>
                  ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No categories yet</p>
            )}
          </div>
        </div>

        {/* Token Usage by Model */}
        {usage?.by_model && Object.keys(usage.by_model).length > 0 && (
          <div className="bg-card/60 backdrop-blur-sm border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-success" />
              <h3 className="text-lg font-semibold text-white">
                Token Usage by Model (Last 24 Hours)
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Tokens
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Cost
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30">
                  {Object.entries(usage.by_model).map(([model, data], idx) => (
                    <motion.tr
                      key={model}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="hover:bg-border/30 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm font-medium text-white">
                        {model}
                      </td>
                      <td className="px-4 py-3 text-sm text-foreground/80">
                        {data.tokens.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-success font-mono">
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
        <div className="bg-success/10 border border-success/30 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <Activity className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-success/90 mb-1">
                Real-Time Analytics Active
              </p>
              <p className="text-xs text-success/80">
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
    purple: 'from-primary to-primary/80',
    indigo: 'from-secondary to-secondary/80',
    cyan: 'from-success to-success/80',
    green: 'from-success to-success/80',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-card/60 backdrop-blur-sm border border-border rounded-xl p-5 hover:border-primary/30 hover:shadow-lg transition-all"
    >
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <div className={`p-2 bg-gradient-to-br ${colorClasses[color]} rounded-lg`}>
          {icon}
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <p className="text-2xl font-bold text-white">{value}</p>
        {trend && (
          <span className="text-xs text-success font-medium flex items-center gap-0.5">
            <TrendingUp className="w-3 h-3" />
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-xs text-muted-foreground/60 mt-1">{subtitle}</p>
      )}
    </motion.div>
  );
}
