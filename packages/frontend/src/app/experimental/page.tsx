'use client';

import { useState } from 'react';
import { ChatInterface } from '@/components/experimental/ChatInterface';
import { MemoryVisualization } from '@/components/experimental/MemoryVisualization';
import { AnalyticsDashboard } from '@/components/experimental/AnalyticsDashboard';
import { ConfigurationPanel } from '@/components/experimental/ConfigurationPanel';
import { useHealthCheck } from '@/lib/hooks/useExperimentalAPI';

// Force dynamic rendering
export const dynamic = "force-dynamic";

type TabType = 'chat' | 'memories' | 'analytics' | 'config';

export default function ExperimentalPage() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const { healthy, checking } = useHealthCheck();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 shadow-lg border-b border-purple-700">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <span className="text-4xl">🧪</span>
                <div>
                  <h1 className="text-3xl font-bold text-white">Experimental Lab</h1>
                  <p className="text-sm text-purple-100 mt-1">
                    AI Companion with Memory - Full Integration Test
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* Backend Status Indicator */}
              <div className="flex items-center gap-2 text-sm bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm">
                <div
                  className={`w-2.5 h-2.5 rounded-full ${
                    checking
                      ? 'bg-yellow-400 animate-pulse'
                      : healthy
                      ? 'bg-green-400'
                      : 'bg-red-400'
                  }`}
                />
                <span className="text-white font-medium">
                  {checking ? 'Checking...' : healthy ? 'Backend Connected' : 'Backend Offline'}
                </span>
              </div>
            </div>
          </div>

          {/* Backend Warning */}
          {!checking && !healthy && (
            <div className="mt-4 p-4 bg-yellow-500/20 border border-yellow-400/50 rounded-lg backdrop-blur-sm">
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚠️</span>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-white">
                    Experimental Backend Not Running
                  </p>
                  <p className="text-xs text-purple-100 mt-2">
                    Start the backend to enable full chat functionality:
                  </p>
                  <code className="block mt-2 bg-black/30 px-3 py-2 rounded text-xs text-purple-100 font-mono">
                    cd packages/backend && poetry run python experiments/web/dashboard_server.py
                  </code>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex gap-1">
            <TabButton
              active={activeTab === 'chat'}
              onClick={() => setActiveTab('chat')}
              icon="💬"
              label="Chat"
            />
            <TabButton
              active={activeTab === 'memories'}
              onClick={() => setActiveTab('memories')}
              icon="🧠"
              label="Memories"
            />
            <TabButton
              active={activeTab === 'analytics'}
              onClick={() => setActiveTab('analytics')}
              icon="📊"
              label="Analytics"
            />
            <TabButton
              active={activeTab === 'config'}
              onClick={() => setActiveTab('config')}
              icon="⚙️"
              label="Config"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="h-[calc(100vh-16rem)]">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'memories' && <MemoryVisualization />}
          {activeTab === 'analytics' && <AnalyticsDashboard />}
          {activeTab === 'config' && <ConfigurationPanel />}
        </div>
      </main>

      {/* Footer Info */}
      <footer className="fixed bottom-0 left-0 right-0 bg-gray-800 text-white py-2 px-4 text-xs">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <span>
            🧪 Experimental Features • Using PostgreSQL + OpenAI GPT-4o-mini
          </span>
          <span>
            Backend: <span className={healthy ? 'text-green-400' : 'text-red-400'}>
              {healthy ? 'http://localhost:8001' : 'Not connected'}
            </span>
          </span>
        </div>
      </footer>
    </div>
  );
}

// ============================================================================
// Tab Button Component
// ============================================================================

function TabButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: string;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
        active
          ? 'border-indigo-600 text-indigo-600 bg-indigo-50'
          : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
      }`}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </button>
  );
}
