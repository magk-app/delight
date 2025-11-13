"use client";

/**
 * Companion Page - Chat with Eliza
 *
 * Full-screen chat interface following UX spec design principles:
 * - Full-screen primary panel (not sidebar)
 * - Modern warmth: Clean lines + warm colors
 * - Mobile-responsive
 * - Protected by Clerk authentication
 */

import { useState } from 'react';
import { CompanionChat } from '@/components/companion/CompanionChat';
import { MemoryStats } from '@/components/companion/MemoryStats';

/**
 * Companion Page
 *
 * Main entry point for chat with Eliza.
 * Protected by Clerk middleware (see middleware.ts).
 */
export default function CompanionPage() {
  const [showMemoryStats, setShowMemoryStats] = useState(false);

  return (
    <main className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            {/* Eliza Avatar */}
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white text-lg font-bold">
              E
            </div>

            {/* Title */}
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Eliza</h1>
              <p className="text-sm text-gray-500">Your AI Companion</p>
            </div>
          </div>

          {/* Memory Stats Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowMemoryStats(!showMemoryStats)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                showMemoryStats
                  ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {showMemoryStats ? '✕ Hide' : '📊'} Memory Stats
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Interface */}
        <div className="flex-1">
          <CompanionChat />
        </div>

        {/* Memory Stats Sidebar */}
        {showMemoryStats && (
          <div className="w-80 border-l border-gray-200 bg-gray-50 overflow-y-auto p-4">
            <MemoryStats />
          </div>
        )}
      </div>
    </main>
  );
}
