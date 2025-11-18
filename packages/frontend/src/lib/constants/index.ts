/**
 * Application Constants
 * Centralized constants for value categories, statuses, memory tiers, etc.
 */

// Value Categories - Core life areas for goals and missions
export const VALUE_CATEGORIES = {
  HEALTH: "health",
  FITNESS: "fitness",
  CAREER: "career",
  RELATIONSHIPS: "relationships",
  LEARNING: "learning",
  CREATIVITY: "creativity",
  FINANCE: "finance",
  SPIRITUALITY: "spirituality",
  WELLNESS: "wellness",
} as const;

export type ValueCategory =
  (typeof VALUE_CATEGORIES)[keyof typeof VALUE_CATEGORIES];

export const VALUE_CATEGORY_INFO: Record<
  ValueCategory,
  { label: string; icon: string; color: string }
> = {
  [VALUE_CATEGORIES.HEALTH]: {
    label: "Health",
    icon: "🏥",
    color: "#ef4444", // red-500
  },
  [VALUE_CATEGORIES.FITNESS]: {
    label: "Fitness",
    icon: "💪",
    color: "#f59e0b", // amber-500
  },
  [VALUE_CATEGORIES.CAREER]: {
    label: "Career",
    icon: "💼",
    color: "#3b82f6", // blue-500
  },
  [VALUE_CATEGORIES.RELATIONSHIPS]: {
    label: "Relationships",
    icon: "❤️",
    color: "#ec4899", // pink-500
  },
  [VALUE_CATEGORIES.LEARNING]: {
    label: "Learning",
    icon: "📚",
    color: "#8b5cf6", // violet-500
  },
  [VALUE_CATEGORIES.CREATIVITY]: {
    label: "Creativity",
    icon: "🎨",
    color: "#06b6d4", // cyan-500
  },
  [VALUE_CATEGORIES.FINANCE]: {
    label: "Finance",
    icon: "💰",
    color: "#10b981", // emerald-500
  },
  [VALUE_CATEGORIES.SPIRITUALITY]: {
    label: "Spirituality",
    icon: "🧘",
    color: "#6366f1", // indigo-500
  },
  [VALUE_CATEGORIES.WELLNESS]: {
    label: "Wellness",
    icon: "✨",
    color: "#14b8a6", // teal-500
  },
};

// Mission Status
export const MISSION_STATUS = {
  PENDING: "pending",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  DEFERRED: "deferred",
  CANCELLED: "cancelled",
} as const;

export type MissionStatus =
  (typeof MISSION_STATUS)[keyof typeof MISSION_STATUS];

// Goal Status
export const GOAL_STATUS = {
  ACTIVE: "active",
  COMPLETED: "completed",
  PAUSED: "paused",
  ARCHIVED: "archived",
} as const;

export type GoalStatus = (typeof GOAL_STATUS)[keyof typeof GOAL_STATUS];

// Memory Tiers - 3-tier memory system
export const MEMORY_TIER = {
  WORKING: "working",
  EPISODIC: "episodic",
  SEMANTIC: "semantic",
} as const;

export type MemoryTier = (typeof MEMORY_TIER)[keyof typeof MEMORY_TIER];

export const MEMORY_TIER_INFO: Record<
  MemoryTier,
  { label: string; retention: string; color: string }
> = {
  [MEMORY_TIER.WORKING]: {
    label: "Working Memory",
    retention: "Short-term (hours to days)",
    color: "#3b82f6", // blue-500
  },
  [MEMORY_TIER.EPISODIC]: {
    label: "Episodic Memory",
    retention: "Medium-term (days to weeks)",
    color: "#8b5cf6", // violet-500
  },
  [MEMORY_TIER.SEMANTIC]: {
    label: "Semantic Memory",
    retention: "Long-term (weeks to months)",
    color: "#10b981", // emerald-500
  },
};

