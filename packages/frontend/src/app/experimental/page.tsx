"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  MessageSquare,
  Brain,
  BarChart3,
  Settings,
  Beaker,
  Activity,
  AlertTriangle,
  Code,
  Network,
} from "lucide-react";
import { ChatInterfaceWithSidebar } from "@/components/experimental/ChatInterfaceWithSidebar";
import { MemoryVisualization } from "@/components/experimental/MemoryVisualization";
import { MemoryGraph } from "@/components/experimental/MemoryGraph";
import { AnalyticsDashboard } from "@/components/experimental/AnalyticsDashboard";
import { ConfigurationPanel } from "@/components/experimental/ConfigurationPanel";
import { UserSwitcher } from "@/components/experimental/UserSwitcher";
import { useHealthCheck } from "@/lib/hooks/useExperimentalAPI";
import { usePersistentUser } from "@/lib/hooks/usePersistentUser";

// Force dynamic rendering
export const dynamic = "force-dynamic";

type TabType = "chat" | "memories" | "graph" | "analytics" | "config";

export default function ExperimentalPage() {
  const [activeTab, setActiveTab] = useState<TabType>("chat");
  const { healthy, checking } = useHealthCheck();
  const { userId, isLoading: userLoading } = usePersistentUser();

  const handleUserChange = () => {
    // Reload page to reinitialize with new user
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header with glassmorphism */}
      <header className="bg-slate-900/50 backdrop-blur-xl shadow-2xl border-b border-slate-700/50 relative z-40">
        <div className="mx-auto max-w-7xl px-3 py-4 sm:px-4 sm:py-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="p-2 sm:p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl shadow-lg shadow-purple-500/30">
                <Beaker className="w-5 h-5 sm:w-7 sm:h-7 text-white" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
                  Delight v1 Beta
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 mt-0.5 sm:mt-1 flex items-center gap-1.5 sm:gap-2">
                  <Activity className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span className="hidden sm:inline">
                    AI-Powered Second Brain • Full Integration Test
                  </span>
                  <span className="sm:hidden">AI Second Brain</span>
                </p>
              </div>
            </div>

            {/* Backend Status & User Switcher */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* User Switcher */}
              {userId && !userLoading && (
                <div>
                  <UserSwitcher
                    currentUserId={userId}
                    onUserChange={handleUserChange}
                  />
                </div>
              )}

              {/* Backend Status Indicator */}
              <div
                className={`flex items-center gap-1.5 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2.5 rounded-lg transition-all ${
                  checking
                    ? "bg-yellow-500/10 border border-yellow-500/30"
                    : healthy
                    ? "bg-green-500/10 border border-green-500/30"
                    : "bg-red-500/10 border border-red-500/30"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    checking
                      ? "bg-yellow-400 animate-pulse"
                      : healthy
                      ? "bg-green-400 shadow-lg shadow-green-400/50"
                      : "bg-red-400 shadow-lg shadow-red-400/50"
                  }`}
                />
                <span
                  className={`text-xs sm:text-sm font-medium ${
                    checking
                      ? "text-yellow-300"
                      : healthy
                      ? "text-green-300"
                      : "text-red-300"
                  }`}
                >
                  <span className="hidden sm:inline">
                    {checking
                      ? "Checking..."
                      : healthy
                      ? "Connected to ngrok"
                      : "Backend Offline"}
                  </span>
                  <span className="sm:hidden">
                    {checking ? "..." : healthy ? "Online" : "Offline"}
                  </span>
                </span>
              </div>
            </div>
          </div>

          {/* Backend Warning */}
          {!checking && !healthy && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-3 sm:mt-4 p-3 sm:p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg sm:rounded-xl backdrop-blur-sm"
            >
              <div className="flex items-start gap-2 sm:gap-3">
                <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-xs sm:text-sm font-semibold text-yellow-300">
                    Backend Not Running
                  </p>
                  <p className="text-xs text-yellow-200/80 mt-1 sm:mt-2 hidden sm:block">
                    Start the backend to enable full chat functionality:
                  </p>
                  <code className="block mt-2 bg-slate-900/50 px-2 sm:px-3 py-2 rounded-lg text-[10px] sm:text-xs text-yellow-100 font-mono border border-yellow-500/20 overflow-x-auto">
                    <Code className="w-3 h-3 inline mr-1.5 sm:mr-2" />
                    <span className="whitespace-nowrap">
                      cd packages/backend && poetry run python
                    </span>
                    <br className="sm:hidden" />
                    <span className="whitespace-nowrap">
                      experiments/web/dashboard_server.py
                    </span>
                  </code>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-slate-900/30 backdrop-blur-xl border-b border-slate-700/50 overflow-x-auto scrollbar-hide">
        <div className="mx-auto max-w-7xl px-2 sm:px-4 lg:px-8">
          <div className="flex gap-1 sm:gap-2 min-w-max">
            <TabButton
              active={activeTab === "chat"}
              onClick={() => setActiveTab("chat")}
              icon={<MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
              label="Chat"
            />
            <TabButton
              active={activeTab === "memories"}
              onClick={() => setActiveTab("memories")}
              icon={<Brain className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
              label="Memories"
            />
            <TabButton
              active={activeTab === "graph"}
              onClick={() => setActiveTab("graph")}
              icon={<Network className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
              label="Graph"
            />
            <TabButton
              active={activeTab === "analytics"}
              onClick={() => setActiveTab("analytics")}
              icon={<BarChart3 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
              label="Analytics"
            />
            <TabButton
              active={activeTab === "config"}
              onClick={() => setActiveTab("config")}
              icon={<Settings className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
              label="Config"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-2 sm:px-4 py-4 sm:py-6 lg:px-8 min-h-[calc(100vh-12rem)] sm:min-h-[calc(100vh-16rem)] pb-20 sm:pb-16">
        <div className="min-h-[calc(100vh-12rem)] sm:min-h-[calc(100vh-16rem)]">
          {userLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-sm sm:text-base text-slate-400">
                Loading user session...
              </div>
            </div>
          ) : !userId ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-sm sm:text-base text-red-400">
                Error: Could not initialize user session
              </div>
            </div>
          ) : (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === "chat" && (
                <ChatInterfaceWithSidebar userId={userId} />
              )}
              {activeTab === "memories" && (
                <MemoryVisualization userId={userId} />
              )}
              {activeTab === "graph" && (
                <div className="h-[calc(100vh-14rem)] sm:h-[calc(100vh-20rem)]">
                  <MemoryGraph userId={userId} />
                </div>
              )}
              {activeTab === "analytics" && (
                <AnalyticsDashboard userId={userId} />
              )}
              {activeTab === "config" && <ConfigurationPanel />}
            </motion.div>
          )}
        </div>
      </main>

      {/* Footer Info */}
      <footer className="fixed bottom-0 left-0 right-0 bg-slate-900/90 backdrop-blur-xl border-t border-slate-700/50 py-2 px-3 sm:px-4 text-xs">
        <div className="mx-auto max-w-7xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-0 text-slate-400">
          <div className="flex items-center gap-1.5 sm:gap-2">
            <Beaker className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
            <span className="hidden sm:inline">
              Phase 3 • Hierarchical Memory + Graph + Visualization
            </span>
            <span className="sm:hidden">Phase 3</span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2">
            <span className="hidden sm:inline">Backend:</span>
            <span
              className={
                healthy
                  ? "text-green-400 font-medium"
                  : "text-red-400 font-medium"
              }
            >
              {healthy ? (
                <span className="hidden sm:inline">Connected to ngrok</span>
              ) : (
                <span className="hidden sm:inline">Not connected</span>
              )}
              {healthy ? (
                <span className="sm:hidden">Online</span>
              ) : (
                <span className="sm:hidden">Offline</span>
              )}
            </span>
          </div>
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
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`relative flex items-center gap-1.5 sm:gap-2 px-3 sm:px-6 py-2 sm:py-3 font-medium text-xs sm:text-sm transition-all whitespace-nowrap ${
        active ? "text-purple-300" : "text-slate-400 hover:text-slate-300"
      }`}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
      {active && (
        <motion.div
          layoutId="activeTab"
          className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-indigo-500 shadow-lg shadow-purple-500/50"
          transition={{ type: "spring", stiffness: 380, damping: 30 }}
        />
      )}
    </button>
  );
}
