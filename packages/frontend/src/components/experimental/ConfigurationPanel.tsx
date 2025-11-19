/**
 * Configuration Panel Component (Dark Mode)
 *
 * Modern dark-themed configuration interface for AI models and system parameters
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Save,
  Bot,
  Search,
  FileText,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertCircle,
  Settings2,
} from 'lucide-react';
import { useConfig } from '@/lib/hooks/useExperimentalAPI';
import { SystemConfig } from '@/lib/api/experimental-client';

export function ConfigurationPanel() {
  const { config, loading, error, saving, updateConfig } = useConfig();
  const [localConfig, setLocalConfig] = useState<SystemConfig | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    if (config) {
      setLocalConfig(config);
    }
  }, [config]);

  const handleSave = async () => {
    if (!localConfig) return;

    try {
      await updateConfig(localConfig);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (err) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  if (loading || !localConfig) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700/50">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400 mb-4" />
        <div className="text-slate-400">Loading configuration...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700/50 p-12">
        <XCircle className="w-16 h-16 text-red-400 mb-4" />
        <div className="text-center">
          <p className="text-lg font-medium text-red-400">Error loading configuration</p>
          <p className="text-sm mt-2 text-slate-400">{error.message}</p>
          <p className="text-xs text-slate-500 mt-4">
            Make sure the experimental backend server is running on port 8001
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 overflow-y-auto max-h-full scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent pr-2">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800/80 backdrop-blur-xl rounded-xl shadow-2xl p-6 border border-slate-700/50"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
              <Settings2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">System Configuration</h2>
              <p className="text-sm text-slate-400 mt-1">
                Configure AI models and system parameters
              </p>
            </div>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium rounded-lg hover:from-purple-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-purple-500/20"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </>
            )}
          </button>
        </div>

        {/* Save Status */}
        {saveStatus !== 'idle' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className={`mt-4 p-3 rounded-lg flex items-center gap-2 ${
              saveStatus === 'success'
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}
          >
            {saveStatus === 'success' ? (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Configuration saved successfully</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4" />
                <span>Failed to save configuration</span>
              </>
            )}
          </motion.div>
        )}
      </motion.div>

      {/* Model Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-slate-800/80 backdrop-blur-xl rounded-xl shadow-2xl p-6 border border-slate-700/50"
      >
        <div className="flex items-center gap-3 mb-6">
          <Bot className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">AI Models</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Chat Model</label>
            <select
              value={localConfig.models.chat_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, chat_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            >
              <option value="gpt-4o-mini">GPT-4o Mini (Fast & Cheap)</option>
              <option value="gpt-4o">GPT-4o (Balanced)</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
            <p className="text-xs text-slate-500">Used for general chat and fact extraction</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Reasoning Model</label>
            <select
              value={localConfig.models.reasoning_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, reasoning_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            >
              <option value="o1-preview">O1 Preview (Best Reasoning)</option>
              <option value="o1-mini">O1 Mini</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
            <p className="text-xs text-slate-500">Used for complex tasks and planning</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">High-Quality Model</label>
            <select
              value={localConfig.models.expensive_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, expensive_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            >
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="o1-preview">O1 Preview</option>
            </select>
            <p className="text-xs text-slate-500">Used for premium outputs</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Embedding Model</label>
            <select
              value={localConfig.models.embedding_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, embedding_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            >
              <option value="text-embedding-3-small">Text Embedding 3 Small (Recommended)</option>
              <option value="text-embedding-3-large">Text Embedding 3 Large</option>
              <option value="text-embedding-ada-002">Ada 002 (Legacy)</option>
            </select>
            <p className="text-xs text-slate-500">Used for semantic search</p>
          </div>
        </div>
      </motion.div>

      {/* Search Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-slate-800/80 backdrop-blur-xl rounded-xl shadow-2xl p-6 border border-slate-700/50"
      >
        <div className="flex items-center gap-3 mb-6">
          <Search className="w-5 h-5 text-indigo-400" />
          <h3 className="text-lg font-semibold text-white">Search Parameters</h3>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">Similarity Threshold</label>
              <span className="text-sm font-mono text-purple-400">{localConfig.search.similarity_threshold.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={localConfig.search.similarity_threshold}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  search: { ...localConfig.search, similarity_threshold: parseFloat(e.target.value) },
                })
              }
              className="w-full h-2 bg-slate-700/50 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <p className="text-xs text-slate-500">Higher = more strict matching. Lower = more results.</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Default Search Limit</label>
            <input
              type="number"
              min="1"
              max="100"
              value={localConfig.search.default_search_limit}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  search: { ...localConfig.search, default_search_limit: parseInt(e.target.value) },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">Vector Search Weight</label>
              <span className="text-sm font-mono text-purple-400">{localConfig.search.hybrid_search_weight_vector.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={localConfig.search.hybrid_search_weight_vector}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  search: { ...localConfig.search, hybrid_search_weight_vector: parseFloat(e.target.value) },
                })
              }
              className="w-full h-2 bg-slate-700/50 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <p className="text-xs text-slate-500">Weight for vector search vs keyword search</p>
          </div>
        </div>
      </motion.div>

      {/* Fact Extraction Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-slate-800/80 backdrop-blur-xl rounded-xl shadow-2xl p-6 border border-slate-700/50"
      >
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-5 h-5 text-cyan-400" />
          <h3 className="text-lg font-semibold text-white">Fact Extraction</h3>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Max Facts Per Message</label>
            <input
              type="number"
              min="1"
              max="50"
              value={localConfig.fact_extraction.max_facts_per_message}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  fact_extraction: { ...localConfig.fact_extraction, max_facts_per_message: parseInt(e.target.value) },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Minimum Fact Length (characters)</label>
            <input
              type="number"
              min="5"
              max="100"
              value={localConfig.fact_extraction.min_fact_length}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  fact_extraction: { ...localConfig.fact_extraction, min_fact_length: parseInt(e.target.value) },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">Auto-Categorize Facts</label>
              <button
                onClick={() =>
                  setLocalConfig({
                    ...localConfig,
                    fact_extraction: { ...localConfig.fact_extraction, auto_categorize: !localConfig.fact_extraction.auto_categorize },
                  })
                }
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500/50 ${
                  localConfig.fact_extraction.auto_categorize ? 'bg-purple-600' : 'bg-slate-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    localConfig.fact_extraction.auto_categorize ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            <p className="text-xs text-slate-500">Automatically assign categories using LLM</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">Max Categories Per Fact</label>
            <input
              type="number"
              min="1"
              max="5"
              value={localConfig.fact_extraction.max_categories_per_fact}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  fact_extraction: { ...localConfig.fact_extraction, max_categories_per_fact: parseInt(e.target.value) },
                })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
          </div>
        </div>
      </motion.div>

      {/* Info Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-purple-500/10 backdrop-blur-sm rounded-xl p-4 border border-purple-500/20"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-purple-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-slate-300">
            <p className="font-medium text-purple-400 mb-1">Configuration Notes</p>
            <ul className="space-y-1 text-slate-400">
              <li>• Changes take effect immediately after saving</li>
              <li>• Model names must match OpenAI API model identifiers</li>
              <li>• Higher similarity thresholds return more precise but fewer results</li>
              <li>• Auto-categorization requires additional API calls</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
