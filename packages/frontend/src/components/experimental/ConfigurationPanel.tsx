/**
 * Configuration Panel Component
 *
 * Allows configuration of:
 * - AI models (chat, reasoning, embedding)
 * - Search parameters
 * - Fact extraction settings
 */

'use client';

import React, { useState, useEffect } from 'react';
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
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading configuration...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-red-600">
          <p className="text-lg font-medium">Error loading configuration</p>
          <p className="text-sm mt-2">{error.message}</p>
          <p className="text-xs text-gray-500 mt-4">
            Make sure the experimental backend server is running on port 8001
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Configuration</h2>
            <p className="text-sm text-gray-600 mt-1">
              Configure AI models and system parameters
            </p>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? 'Saving...' : '💾 Save Changes'}
          </button>
        </div>

        {/* Save Status */}
        {saveStatus !== 'idle' && (
          <div
            className={`mt-4 p-3 rounded-lg ${
              saveStatus === 'success'
                ? 'bg-green-50 text-green-800'
                : 'bg-red-50 text-red-800'
            }`}
          >
            {saveStatus === 'success'
              ? '✓ Configuration saved successfully'
              : '✗ Failed to save configuration'}
          </div>
        )}
      </div>

      {/* Model Configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🤖 AI Models</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chat Model
            </label>
            <select
              value={localConfig.models.chat_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, chat_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="gpt-4o-mini">GPT-4o Mini (Fast & Cheap)</option>
              <option value="gpt-4o">GPT-4o (Balanced)</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Used for general chat and fact extraction
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reasoning Model
            </label>
            <select
              value={localConfig.models.reasoning_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, reasoning_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="o1-preview">O1 Preview (Best Reasoning)</option>
              <option value="o1-mini">O1 Mini</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Used for complex tasks and planning
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              High-Quality Model
            </label>
            <select
              value={localConfig.models.expensive_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, expensive_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="o1-preview">O1 Preview</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Used for premium outputs
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Embedding Model
            </label>
            <select
              value={localConfig.models.embedding_model}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  models: { ...localConfig.models, embedding_model: e.target.value },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="text-embedding-3-small">
                Text Embedding 3 Small (Recommended)
              </option>
              <option value="text-embedding-3-large">
                Text Embedding 3 Large
              </option>
              <option value="text-embedding-ada-002">
                Ada 002 (Legacy)
              </option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Used for semantic search
            </p>
          </div>
        </div>
      </div>

      {/* Search Configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🔍 Search Parameters</h3>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Similarity Threshold: {localConfig.search.similarity_threshold}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={localConfig.search.similarity_threshold}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  search: {
                    ...localConfig.search,
                    similarity_threshold: parseFloat(e.target.value),
                  },
                })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Higher = more strict matching. Lower = more results.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Default Search Limit
            </label>
            <input
              type="number"
              min="1"
              max="100"
              value={localConfig.search.default_search_limit}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  search: {
                    ...localConfig.search,
                    default_search_limit: parseInt(e.target.value),
                  },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vector Search Weight: {localConfig.search.hybrid_search_weight_vector}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={localConfig.search.hybrid_search_weight_vector}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  search: {
                    ...localConfig.search,
                    hybrid_search_weight_vector: parseFloat(e.target.value),
                  },
                })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Weight for vector search vs keyword search (keyword weight = 1 - vector weight)
            </p>
          </div>
        </div>
      </div>

      {/* Fact Extraction Configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">📝 Fact Extraction</h3>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Facts Per Message
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={localConfig.fact_extraction.max_facts_per_message}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  fact_extraction: {
                    ...localConfig.fact_extraction,
                    max_facts_per_message: parseInt(e.target.value),
                  },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Fact Length (characters)
            </label>
            <input
              type="number"
              min="5"
              max="100"
              value={localConfig.fact_extraction.min_fact_length}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  fact_extraction: {
                    ...localConfig.fact_extraction,
                    min_fact_length: parseInt(e.target.value),
                  },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={localConfig.fact_extraction.auto_categorize}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    fact_extraction: {
                      ...localConfig.fact_extraction,
                      auto_categorize: e.target.checked,
                    },
                  })
                }
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Auto-Categorize Facts
              </span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">
              Automatically assign categories using LLM
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Categories Per Fact
            </label>
            <input
              type="number"
              min="1"
              max="5"
              value={localConfig.fact_extraction.max_categories_per_fact}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  fact_extraction: {
                    ...localConfig.fact_extraction,
                    max_categories_per_fact: parseInt(e.target.value),
                  },
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
