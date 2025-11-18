/**
 * Core TypeScript types for Delight application
 * These define the data structures used throughout the app
 */

import type {
  ValueCategory,
  MissionStatus,
  EnergyLevel,
  GoalStatus,
  Zone,
  MemoryTier as MemoryTierType,
  NarrativeAct,
  Priority,
} from '../constants';

// Re-export types
export type MemoryTier = MemoryTierType;

// User and Profile
export interface User {
  id: string;
  clerkUserId: string;
  email: string;
  timezone: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserPreferences {
  userId: string;
  customHours?: Record<string, any>;
  theme: 'modern' | 'medieval' | 'scifi' | 'cyberpunk' | 'zombie';
  communicationPreferences: {
    inApp: boolean;
    email: boolean;
    sms: boolean;
    quietHoursStart?: string;
    quietHoursEnd?: string;
  };
  essenceBalance: number;
}

// Goals
export interface Goal {
  id: string;
  userId: string;
  title: string;
  description: string;
  valueCategory: ValueCategory;
  targetDate?: string;
  status: GoalStatus;
  createdAt: string;
  updatedAt: string;
}

// Missions
export interface Mission {
  id: string;
  goalId: string;
  userId: string;
  title: string;
  description: string;
  estimatedMinutes: number;
  energyLevel: EnergyLevel;
  valueCategory: ValueCategory;
  priorityScore: number;
  priority: Priority;
  status: MissionStatus;
  createdAt: string;
  completedAt?: string;
  goal?: Goal; // Optional populated goal
}

// Mission Session (for tracking active work)
export interface MissionSession {
  id: string;
  missionId: string;
  startedAt: string;
  completedAt?: string;
  actualMinutes?: number;
  notes?: string;
}

// Memory System
export interface Memory {
  id: string;
  userId: string;
  tier: MemoryTier;
  content: string;
  metadata: Record<string, any>;
  createdAt: string;
  accessedAt: string;
  relatedGoalId?: string;
  relatedMissionId?: string;
  tags?: string[];
}

// Narrative System
export interface NarrativeState {
  id: string;
  userId: string;
  scenarioId: string;
  currentAct: NarrativeAct;
  currentChapter: number;
  daysInStory: number;
  worldState: WorldState;
  createdAt: string;
  updatedAt: string;
}

export interface WorldState {
  locations: Record<string, LocationState>;
  events: WorldEvent[];
  persons: Record<string, PersonState>;
  items: {
    essence: number;
    titles: string[];
    artifacts: Artifact[];
  };
  worldTime: {
    currentAct: number;
    currentChapter: number;
    daysInStory: number;
  };
}

export interface LocationState {
  discovered: boolean;
  description: string;
  npcsPresent: string[];
  unlockCondition?: string;
}

export interface WorldEvent {
  eventId: string;
  occurredAt: string;
  impact: string;
  description: string;
}

export interface PersonState {
  relationshipLevel: number;
  lastInteraction: string;
  knowsAbout: string[];
  status: 'friendly' | 'neutral' | 'distant';
}

export interface Artifact {
  id: string;
  name: string;
  acquiredAt: string;
  description: string;
}

export interface StoryBeat {
  id: string;
  userId: string;
  narrativeStateId: string;
  act: NarrativeAct;
  chapter: number;
  title: string;
  content: string;
  emotionalTone: string;
  createdAt: string;
  unlocks?: string[];
}

// Progress and Analytics
export interface StreakSummary {
  userId: string;
  overallStreak: number;
  longestStreak: number;
  lastActivityDate: string;
  categoryStreaks: {
    health: number;
    craft: number;
    growth: number;
    connection: number;
  };
}

export interface DCISnapshot {
  userId: string;
  date: string;
  score: number;
  status: 'Fragile' | 'Steady' | 'Strong' | 'Excellent';
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

export interface HighlightReel {
  id: string;
  userId: string;
  title: string;
  milestoneType: string;
  content: {
    accomplishments: string[];
    stats: Record<string, any>;
    quote?: string;
  };
  generatedAt: string;
}

// World Zones
export interface ZoneState {
  zone: Zone;
  available: boolean;
  reason?: string;
  charactersPresent: string[];
  opensAt?: string;
}

// Companion and Characters
export interface CompanionMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  emotionalContext?: {
    detectedEmotion: string;
    emotionScores: Record<string, number>;
  };
}

export interface Character {
  id: string;
  name: string;
  role: string;
  description: string;
  zone: Zone;
  relationshipLevel: number;
}

// Evidence and Reflection
export interface Evidence {
  id: string;
  userId: string;
  missionId: string;
  fileType: 'image' | 'document';
  fileSize: number;
  caption?: string;
  uploadedAt: string;
  thumbnailUrl: string;
  fullUrl: string;
}

// Priority Triad - The three daily missions
export interface MissionTriad {
  high: Mission;
  medium: Mission;
  low: Mission;
}
