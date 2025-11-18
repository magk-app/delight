/**
 * Type definitions for Delight application
 */

import type {
  ValueCategory,
  MissionStatus,
  GoalStatus,
  MemoryTier,
} from "../constants";

// Mission types
export interface Mission {
  id: string;
  title: string;
  description: string;
  valueCategory: ValueCategory;
  status: MissionStatus;
  estimatedMinutes: number;
  energyLevel: "low" | "medium" | "high";
  goalId?: string;
  goal?: {
    id: string;
    title: string;
  };
  createdAt?: string;
  completedAt?: string;
}

// Goal types
export interface Goal {
  id: string;
  title: string;
  description: string;
  valueCategory: ValueCategory;
  status: GoalStatus;
  targetDate?: string;
  createdAt?: string;
}

// Memory types
export interface Memory {
  id: string;
  content: string;
  tier: MemoryTier;
  tags?: string[];
  createdAt: string;
  accessedAt: string;
}

// Story Beat types
export interface StoryBeat {
  id: string;
  title: string;
  content: string;
  act: number;
  chapter: number;
  createdAt: string;
  emotionalTone?: string;
}

// DCI (Daily Consistency Index) types
export interface DCISnapshot {
  score: number; // 0-1
  status: string;
  breakdown: {
    streakFactor: number;
    completionRate: number;
    engagementDepth: number;
    responseRate: number;
  };
}

export interface DCIHistoryPoint {
  date: string;
  score: number;
}

// Streak types
export interface StreakSummary {
  overallStreak: number;
  longestStreak: number;
  categoryStreaks: Record<string, number>;
}

// Highlight Reel types
export interface HighlightReel {
  id: string;
  title: string;
  content: {
    accomplishments: string[];
    stats: Record<string, number>;
    quote?: string;
  };
  createdAt?: string;
}

// Narrative State types
export interface NarrativeState {
  worldState: {
    worldTime: {
      currentAct: number;
      currentChapter: number;
      daysInStory: number;
    };
    locations: Record<
      string,
      {
        discovered: boolean;
        description?: string;
      }
    >;
    persons: Record<
      string,
      {
        relationshipLevel: number;
        status: "friendly" | "neutral" | "hostile";
      }
    >;
    items: {
      essence: number;
      titles: string[];
    };
  };
}

// Character types
export interface Character {
  id: string;
  name: string;
  role: string;
  description: string;
  relationshipLevel?: number;
}

// Mission Triad type
export interface MissionTriad {
  high: Mission;
  medium: Mission;
  low: Mission;
}

