/**
 * Memory Cleanup Panel
 *
 * Analyzes and cleans up problematic memories:
 * - Questions, vague statements, duplicates, trivial memories
 * - Shows analysis report before cleanup
 * - Executes cleanup and refreshes memory list
 */

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader2,
} from 'lucide-react';

interface CleanupPanelProps {
  userId: string;
  onCleanupComplete: () => void;
}

interface AnalysisReport {
  total_memories: number;
  issues_found: number;
  breakdown: {
    questions: number;
    vague: number;
    duplicates: number;
    trivial: number;
    no_embedding: number;
  };
  recommendations: string[];
}

export function CleanupPanel({ userId, onCleanupComplete }: CleanupPanelProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisReport | null>(null);
  const [cleanupResult, setCleanupResult] = useState<{deleted_count: number} | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError(null);

      const response = await fetch(`http://localhost:8001/api/cleanup/analyze?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze memories');
    } finally {
      setAnalyzing(false);
    }
  };

  const executeCleanup = async () => {
    if (!confirm(`Delete ${analysis?.issues_found || 0} problematic memories? This cannot be undone.`)) {
      return;
    }

    try {
      setCleaning(true);
      setError(null);

      const response = await fetch('http://localhost:8001/api/cleanup/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          delete_questions: true,
          delete_vague: true,
          delete_duplicates: true,
          delete_trivial: false, // User might want to keep some
          similarity_threshold: 0.85,
        }),
      });

      if (!response.ok) {
        throw new Error(`Cleanup failed: ${response.statusText}`);
      }

      const result = await response.json();
      setCleanupResult(result);

      // Refresh memory list
      setTimeout(() => {
        onCleanupComplete();
      }, 1000);
    } catch (err: any) {
      setError(err.message || 'Failed to execute cleanup');
    } finally {
      setCleaning(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="border-b border-slate-700/50 bg-slate-800/30 backdrop-blur-sm"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Memory Cleanup</h3>
              <p className="text-sm text-slate-400">
                Identify and remove problematic memories
              </p>
            </div>
          </div>

          {!analysis && (
            <button
              onClick={runAnalysis}
              disabled={analyzing}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium text-sm flex items-center gap-2 transition-all disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span>Analyze Memories</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-2">
            <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-300">Error</p>
              <p className="text-xs text-red-400 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Analysis Report */}
        <AnimatePresence>
          {analysis && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/50 border border-slate-700/50 rounded-lg">
                  <p className="text-xs text-slate-400 mb-1">Total Memories</p>
                  <p className="text-2xl font-bold text-white">{analysis.total_memories}</p>
                </div>
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <p className="text-xs text-red-300 mb-1">Issues Found</p>
                  <p className="text-2xl font-bold text-red-400">{analysis.issues_found}</p>
                </div>
                <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <p className="text-xs text-green-300 mb-1">Will Remain</p>
                  <p className="text-2xl font-bold text-green-400">
                    {analysis.total_memories - analysis.issues_found}
                  </p>
                </div>
                <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <p className="text-xs text-purple-300 mb-1">Reduction</p>
                  <p className="text-2xl font-bold text-purple-400">
                    {((analysis.issues_found / analysis.total_memories) * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Breakdown */}
              <div className="p-4 bg-slate-900/50 border border-slate-700/50 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-3">Issues Breakdown</h4>
                <div className="space-y-2">
                  {analysis.breakdown.questions > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">❓ Questions</span>
                      <span className="text-red-400 font-medium">{analysis.breakdown.questions}</span>
                    </div>
                  )}
                  {analysis.breakdown.vague > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">💭 Vague Statements</span>
                      <span className="text-red-400 font-medium">{analysis.breakdown.vague}</span>
                    </div>
                  )}
                  {analysis.breakdown.duplicates > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">🔄 Duplicates</span>
                      <span className="text-orange-400 font-medium">{analysis.breakdown.duplicates}</span>
                    </div>
                  )}
                  {analysis.breakdown.trivial > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">🗑️  Trivial</span>
                      <span className="text-yellow-400 font-medium">{analysis.breakdown.trivial}</span>
                    </div>
                  )}
                  {analysis.breakdown.no_embedding > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">📊 No Embeddings</span>
                      <span className="text-blue-400 font-medium">{analysis.breakdown.no_embedding}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Recommendations */}
              {analysis.recommendations && analysis.recommendations.length > 0 && (
                <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <h4 className="text-sm font-semibold text-purple-300 mb-2">Recommendations</h4>
                  <ul className="space-y-1">
                    {analysis.recommendations.map((rec, i) => (
                      <li key={i} className="text-xs text-purple-200 flex items-start gap-2">
                        <span className="text-purple-400 mt-0.5">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Cleanup Result */}
              {cleanupResult && (
                <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-300">Cleanup Complete!</p>
                    <p className="text-xs text-green-400 mt-1">
                      Successfully deleted {cleanupResult.deleted_count} problematic memories
                    </p>
                  </div>
                </div>
              )}

              {/* Actions */}
              {!cleanupResult && analysis.issues_found > 0 && (
                <div className="flex gap-3">
                  <button
                    onClick={executeCleanup}
                    disabled={cleaning}
                    className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-500 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  >
                    {cleaning ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Cleaning...</span>
                      </>
                    ) : (
                      <>
                        <Trash2 className="w-4 h-4" />
                        <span>Delete {analysis.issues_found} Problematic Memories</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={runAnalysis}
                    className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium flex items-center gap-2 transition-all"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Re-analyze</span>
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
