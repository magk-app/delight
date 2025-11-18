'use client';

import { useState } from 'react';
import { ChatInterface } from '@/components/experimental/ChatInterface';
import { MemoryVisualization } from '@/components/experimental/MemoryVisualization';
import { AnalyticsDashboard } from '@/components/experimental/AnalyticsDashboard';
import { ConfigurationPanel } from '@/components/experimental/ConfigurationPanel';
import { useHealthCheck } from '@/lib/hooks/useExperimentalAPI';

// Force dynamic rendering to work with Clerk middleware (Next.js 15)
export const dynamic = "force-dynamic";

type TabType = 'chat' | 'memories' | 'analytics' | 'config';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const { healthy, checking } = useHealthCheck();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Delight Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">
                AI Companion with Memory - Experimental Interface
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* Backend Status Indicator */}
              <div className="flex items-center gap-2 text-sm">
                <div
                  className={`w-2 h-2 rounded-full ${
                    checking
                      ? 'bg-yellow-500 animate-pulse'
                      : healthy
                      ? 'bg-green-500'
                      : 'bg-red-500'
                  }`}
                />
                <span className="text-gray-600">
                  {checking ? 'Checking...' : healthy ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div data-testid="user-menu">
                {/* <UserButton afterSignOutUrl="/" /> */}
              </div>
            </div>
          </div>

          {/* Backend Warning */}
          {!checking && !healthy && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start gap-2">
                <span className="text-yellow-600">⚠️</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-yellow-800">
                    Backend Server Not Running
                  </p>
                  <p className="text-xs text-yellow-700 mt-1">
                    Start the experimental backend server on port 8001 to use the full features.
                    Run: <code className="bg-yellow-100 px-1 rounded">cd packages/backend && poetry run python experiments/web/dashboard_server.py</code>
                  </p>
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
