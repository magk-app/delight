"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface MemoryDistribution {
  PERSONAL: number;
  PROJECT: number;
  TASK: number;
}

interface MemoryStatsData {
  distribution: MemoryDistribution;
  total: number;
  recent_by_type: {
    [key: string]: Array<{
      content: string;
      created_at: string;
      role: string;
    }>;
  };
}

export function MemoryStats() {
  const [stats, setStats] = useState<MemoryStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/companion/debug/memory-stats`,
        {
          headers: {
            Authorization: `Bearer ${await getToken()}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch memory stats");
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function getToken(): Promise<string> {
    // This should match your auth implementation
    // For now, assuming you have access to clerk
    if (typeof window !== "undefined") {
      const clerk = (window as any).Clerk;
      if (clerk) {
        const session = await clerk.session;
        return session?.getToken() || "";
      }
    }
    return "";
  }

  if (loading) {
    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
        <p className="text-sm text-red-600 dark:text-red-400">Error: {error}</p>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const { distribution, total } = stats;

  const memoryTypes = [
    {
      type: "PERSONAL",
      label: "Personal",
      description: "Emotions, struggles, feelings (never pruned)",
      color: "bg-purple-500",
      lightBg: "bg-purple-50",
      darkBg: "bg-purple-900/20",
      textColor: "text-purple-700 dark:text-purple-300",
    },
    {
      type: "PROJECT",
      label: "Project",
      description: "Goals, plans, long-term aspirations",
      color: "bg-blue-500",
      lightBg: "bg-blue-50",
      darkBg: "bg-blue-900/20",
      textColor: "text-blue-700 dark:text-blue-300",
    },
    {
      type: "TASK",
      label: "Task",
      description: "Immediate actions, questions (30-day retention)",
      color: "bg-amber-500",
      lightBg: "bg-amber-50",
      darkBg: "bg-amber-900/20",
      textColor: "text-amber-700 dark:text-amber-300",
    },
  ];

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Memory Distribution
        </h3>
        <button
          onClick={fetchStats}
          className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
        >
          Refresh
        </button>
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-400">
        Total memories: {total}
      </div>

      {/* Distribution bars */}
      <div className="space-y-3">
        {memoryTypes.map(({ type, label, description, color, lightBg, darkBg, textColor }) => {
          const count = distribution[type as keyof MemoryDistribution] || 0;
          const percentage = total > 0 ? (count / total) * 100 : 0;
          const isExpanded = expanded === type;

          return (
            <div key={type} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <button
                  onClick={() => setExpanded(isExpanded ? null : type)}
                  className={`font-medium ${textColor} hover:opacity-70 text-left flex-1`}
                >
                  {label} ({count})
                </button>
                <span className="text-gray-500 dark:text-gray-400 text-xs">
                  {percentage.toFixed(1)}%
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className={color}
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                  style={{ height: "100%" }}
                />
              </div>

              <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>

              {/* Expanded recent memories */}
              {isExpanded && stats.recent_by_type[type]?.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className={`${lightBg} ${darkBg} rounded p-3 space-y-2 mt-2`}
                >
                  <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                    Recent memories:
                  </p>
                  {stats.recent_by_type[type].map((mem, idx) => (
                    <div
                      key={idx}
                      className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-600 pl-2"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium capitalize">{mem.role}:</span>
                        <span className="text-gray-400 dark:text-gray-500">
                          {new Date(mem.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="line-clamp-2">{mem.content}</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
