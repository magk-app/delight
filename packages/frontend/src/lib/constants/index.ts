/**
 * Core constants for the Delight application
 * Defines value categories, zones, statuses, and other system-wide enums
 */

// Value Categories - The four dimensions of growth in Delight
export const VALUE_CATEGORIES = {
  HEALTH: 'health',
  CRAFT: 'craft',
  GROWTH: 'growth',
  CONNECTION: 'connection',
} as const;

export type ValueCategory = typeof VALUE_CATEGORIES[keyof typeof VALUE_CATEGORIES];

export const VALUE_CATEGORY_INFO = {
  [VALUE_CATEGORIES.HEALTH]: {
    label: 'Health',
    icon: '💪',
    color: '#26DE81', // Warm green
    description: 'Physical wellness, exercise, nutrition, sleep',
  },
  [VALUE_CATEGORIES.CRAFT]: {
    label: 'Craft',
    icon: '🎨',
    color: '#F79F1F', // Warm amber/gold
    description: 'Creative output, building, making, producing',
  },
  [VALUE_CATEGORIES.GROWTH]: {
    label: 'Growth',
    icon: '🌱',
    color: '#A55EEA', // Soft purple
    description: 'Learning, wisdom, self-development',
  },
  [VALUE_CATEGORIES.CONNECTION]: {
    label: 'Connection',
    icon: '🤝',
    color: '#5F27CD', // Deep purple/blue
    description: 'Relationships, community, meaningful interactions',
  },
} as const;

// Mission Statuses
export const MISSION_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  DEFERRED: 'deferred',
} as const;

export type MissionStatus = typeof MISSION_STATUS[keyof typeof MISSION_STATUS];

// Energy Levels for missions
export const ENERGY_LEVEL = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
} as const;

export type EnergyLevel = typeof ENERGY_LEVEL[keyof typeof ENERGY_LEVEL];

// Goal Statuses
export const GOAL_STATUS = {
  ACTIVE: 'active',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  ARCHIVED: 'archived',
} as const;

export type GoalStatus = typeof GOAL_STATUS[keyof typeof GOAL_STATUS];

// World Zones - The three primary zones in Delight
export const ZONES = {
  ARENA: 'arena',
  OBSERVATORY: 'observatory',
  COMMONS: 'commons',
} as const;

export type Zone = typeof ZONES[keyof typeof ZONES];

export const ZONE_INFO = {
  [ZONES.ARENA]: {
    name: 'Arena',
    description: 'Health & craft missions, energizing atmosphere',
    primaryCategories: [VALUE_CATEGORIES.HEALTH, VALUE_CATEGORIES.CRAFT],
    icon: '⚔️',
    color: '#F79F1F',
  },
  [ZONES.OBSERVATORY]: {
    name: 'Observatory',
    description: 'Growth & learning missions, contemplative atmosphere',
    primaryCategories: [VALUE_CATEGORIES.GROWTH],
    icon: '🔭',
    color: '#A55EEA',
  },
  [ZONES.COMMONS]: {
    name: 'Commons',
    description: 'Connection & reflection, collaborative atmosphere',
    primaryCategories: [VALUE_CATEGORIES.CONNECTION],
    icon: '🏘️',
    color: '#5F27CD',
  },
} as const;

// Memory Tiers - The three-tier memory architecture
export const MEMORY_TIER = {
  PERSONAL: 'personal',
  PROJECT: 'project',
  TASK: 'task',
} as const;

export type MemoryTier = typeof MEMORY_TIER[keyof typeof MEMORY_TIER];

export const MEMORY_TIER_INFO = {
  [MEMORY_TIER.PERSONAL]: {
    label: 'Personal',
    description: 'Long-term identity, values, emotional patterns',
    retention: 'Permanent',
    color: '#A55EEA',
  },
  [MEMORY_TIER.PROJECT]: {
    label: 'Project',
    description: 'Goals, plans, progress snapshots',
    retention: 'Medium-term',
    color: '#F79F1F',
  },
  [MEMORY_TIER.TASK]: {
    label: 'Task',
    description: 'Mission details, actions taken',
    retention: '30 days',
    color: '#5F27CD',
  },
} as const;

// Narrative Acts and Chapters
export const NARRATIVE_ACT = {
  ACT_1: 1,
  ACT_2: 2,
  ACT_3: 3,
} as const;

export type NarrativeAct = typeof NARRATIVE_ACT[keyof typeof NARRATIVE_ACT];

// DCI (Daily Consistency Index) thresholds
export const DCI_THRESHOLDS = {
  FRAGILE: 0.3,
  STEADY: 0.6,
  STRONG: 0.8,
  EXCELLENT: 0.9,
} as const;

export const DCI_STATUS = {
  FRAGILE: 'Fragile',
  STEADY: 'Steady',
  STRONG: 'Strong',
  EXCELLENT: 'Excellent',
} as const;

// Priority levels for mission triads
export const PRIORITY = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
} as const;

export type Priority = typeof PRIORITY[keyof typeof PRIORITY];
