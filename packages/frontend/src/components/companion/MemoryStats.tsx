"use client";

import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";

interface MemoryDistribution {
  PERSONAL: number;
  PROJECT: number;
  TASK: number;
}

// Backend API response structure
interface MemoryTypeStats {
  memory_type: string;
  count: number;
  recent_count: number;
}

interface BackendMemoryStats {
  total_memories: number;
  by_type: MemoryTypeStats[];
  recent_memories: Array<{
    id: string;
    type: string;
    content: string;
    created_at: string;
    metadata?: any;
  }>;
}

// Transformed data structure for component
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

  const fetchStats = useCallback(async () => {
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

      const data: BackendMemoryStats = await response.json();

      // Validate response structure
      if (!data || typeof data !== "object") {
        throw new Error("Invalid response format from server");
      }

      // Transform backend response to component format
      const distribution: MemoryDistribution = {
        PERSONAL: 0,
        PROJECT: 0,
        TASK: 0,
      };

      // Map backend by_type array to distribution object (defensive: check if by_type exists)
      if (Array.isArray(data.by_type)) {
        data.by_type.forEach((stat) => {
          if (stat && stat.memory_type) {
            const upperType =
              stat.memory_type.toUpperCase() as keyof MemoryDistribution;
            if (upperType in distribution) {
              distribution[upperType] = stat.count || 0;
            }
          }
        });
      }

      // Group recent memories by type (defensive: check if recent_memories exists)
      const recent_by_type: {
        [key: string]: Array<{
          content: string;
          created_at: string;
          role: string;
        }>;
      } = {};
      if (Array.isArray(data.recent_memories)) {
        data.recent_memories.forEach((mem) => {
          if (mem && mem.type) {
            const upperType = mem.type.toUpperCase();
            if (!recent_by_type[upperType]) {
              recent_by_type[upperType] = [];
            }
            recent_by_type[upperType].push({
              content: mem.content || "",
              created_at: mem.created_at || new Date().toISOString(),
              role: "assistant", // Backend doesn't provide role, defaulting to assistant
            });
          }
        });
      }

      setStats({
        distribution,
        total: data.total_memories || 0,
        recent_by_type,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

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

  if (!stats || !stats.distribution) {
    return null;
  }

  // Add default values during destructuring to prevent undefined
  const { distribution = { PERSONAL: 0, PROJECT: 0, TASK: 0 }, total = 0 } =
    stats || {};

  // Additional safety check after destructuring
  if (!distribution || typeof distribution !== "object") {
    return null;
  }

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
        {memoryTypes.map(
          ({ type, label, description, color, lightBg, darkBg, textColor }) => {
            // Defensive check: ensure distribution exists and has the key
            const count =
              (distribution &&
                distribution[type as keyof MemoryDistribution]) ||
              0;
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

                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {description}
                </p>

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
                          <span className="font-medium capitalize">
                            {mem.role}:
                          </span>
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
          }
        )}
      </div>
    </div>
  );
}
