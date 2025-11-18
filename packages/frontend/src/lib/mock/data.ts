/**
 * Mock data for the Delight application
 * Provides realistic seed data for all surfaces during development
 * TODO: Replace with real API calls to /api/v1/* endpoints
 */

import {
  VALUE_CATEGORIES,
  MISSION_STATUS,
  ENERGY_LEVEL,
  GOAL_STATUS,
  ZONES,
  MEMORY_TIER,
  PRIORITY,
} from '../constants';
import type {
  Goal,
  Mission,
  Memory,
  StreakSummary,
  DCIHistoryPoint,
  DCISnapshot,
  HighlightReel,
  StoryBeat,
  NarrativeState,
  WorldState,
  ZoneState,
  Character,
  MissionTriad,
} from '../types';

// ⚠️ SECURITY WARNING: This mock user ID is used for all test data.
// When connecting to real API, replace ALL references with actual user ID from Clerk.
// Search codebase for "MOCK_USER_ID" before deploying to production.
// Risk: Hard-coded user ID could expose data cross-user if not properly replaced.
const MOCK_USER_ID = 'user_mock_001';

// Goals
export const mockGoals: Goal[] = [
  {
    id: 'goal_1',
    userId: MOCK_USER_ID,
    title: 'Become a proficient full-stack developer',
    description: 'Build 3 portfolio projects and land first dev role',
    valueCategory: VALUE_CATEGORIES.CRAFT,
    targetDate: '2026-06-01',
    status: GOAL_STATUS.ACTIVE,
    createdAt: '2025-10-15T10:00:00Z',
    updatedAt: '2025-11-18T10:00:00Z',
  },
  {
    id: 'goal_2',
    userId: MOCK_USER_ID,
    title: 'Establish healthy fitness routine',
    description: 'Exercise 5x per week and improve overall wellness',
    valueCategory: VALUE_CATEGORIES.HEALTH,
    status: GOAL_STATUS.ACTIVE,
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-18T10:00:00Z',
  },
  {
    id: 'goal_3',
    userId: MOCK_USER_ID,
    title: 'Read 12 books on personal development',
    description: 'One book per month to expand mindset and knowledge',
    valueCategory: VALUE_CATEGORIES.GROWTH,
    targetDate: '2025-12-31',
    status: GOAL_STATUS.ACTIVE,
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-18T10:00:00Z',
  },
];

// Missions
export const mockMissions: Mission[] = [
  {
    id: 'mission_1',
    goalId: 'goal_1',
    userId: MOCK_USER_ID,
    title: 'Build authentication flow for portfolio app',
    description: 'Implement Clerk authentication with sign-in and sign-up',
    estimatedMinutes: 45,
    energyLevel: ENERGY_LEVEL.MEDIUM,
    valueCategory: VALUE_CATEGORIES.CRAFT,
    priorityScore: 0.9,
    priority: PRIORITY.HIGH,
    status: MISSION_STATUS.PENDING,
    createdAt: '2025-11-18T08:00:00Z',
    goal: mockGoals[0],
  },
  {
    id: 'mission_2',
    goalId: 'goal_2',
    userId: MOCK_USER_ID,
    title: 'Morning workout at the gym',
    description: '30-minute strength training session',
    estimatedMinutes: 30,
    energyLevel: ENERGY_LEVEL.HIGH,
    valueCategory: VALUE_CATEGORIES.HEALTH,
    priorityScore: 0.7,
    priority: PRIORITY.MEDIUM,
    status: MISSION_STATUS.PENDING,
    createdAt: '2025-11-18T06:00:00Z',
    goal: mockGoals[1],
  },
  {
    id: 'mission_3',
    goalId: 'goal_3',
    userId: MOCK_USER_ID,
    title: 'Read Chapter 3 of "Atomic Habits"',
    description: 'Continue reading and take notes on key insights',
    estimatedMinutes: 20,
    energyLevel: ENERGY_LEVEL.LOW,
    valueCategory: VALUE_CATEGORIES.GROWTH,
    priorityScore: 0.5,
    priority: PRIORITY.LOW,
    status: MISSION_STATUS.PENDING,
    createdAt: '2025-11-17T10:00:00Z',
    goal: mockGoals[2],
  },
  {
    id: 'mission_4',
    goalId: 'goal_1',
    userId: MOCK_USER_ID,
    title: 'Complete React hooks tutorial',
    description: 'Learn useState, useEffect, and custom hooks',
    estimatedMinutes: 60,
    energyLevel: ENERGY_LEVEL.MEDIUM,
    valueCategory: VALUE_CATEGORIES.CRAFT,
    priorityScore: 0.8,
    priority: PRIORITY.HIGH,
    status: MISSION_STATUS.COMPLETED,
    createdAt: '2025-11-17T08:00:00Z',
    completedAt: '2025-11-17T10:30:00Z',
    goal: mockGoals[0],
  },
];

// Mission Triad (today's top 3 missions)
export const mockMissionTriad: MissionTriad = {
  high: mockMissions[0],
  medium: mockMissions[1],
  low: mockMissions[2],
};

// Memory entries
export const mockMemories: Memory[] = [
  {
    id: 'mem_1',
    userId: MOCK_USER_ID,
    tier: MEMORY_TIER.PERSONAL,
    content: 'User values consistency and gets overwhelmed by too many simultaneous projects. Prefers morning work sessions.',
    metadata: {
      category: 'preferences',
      confidence: 0.9,
    },
    createdAt: '2025-11-01T10:00:00Z',
    accessedAt: '2025-11-18T08:00:00Z',
    tags: ['preferences', 'work-style'],
  },
  {
    id: 'mem_2',
    userId: MOCK_USER_ID,
    tier: MEMORY_TIER.PROJECT,
    content: 'User is building a full-stack app with Next.js and FastAPI. Currently working on authentication and user management features.',
    metadata: {
      category: 'project-context',
    },
    createdAt: '2025-10-20T10:00:00Z',
    accessedAt: '2025-11-18T08:00:00Z',
    relatedGoalId: 'goal_1',
    tags: ['coding', 'web-development'],
  },
  {
    id: 'mem_3',
    userId: MOCK_USER_ID,
    tier: MEMORY_TIER.TASK,
    content: 'Completed React hooks tutorial yesterday. User noted that custom hooks pattern clicked after building 3 examples.',
    metadata: {
      category: 'learning',
    },
    createdAt: '2025-11-17T11:00:00Z',
    accessedAt: '2025-11-18T08:00:00Z',
    relatedMissionId: 'mission_4',
    tags: ['react', 'tutorial'],
  },
];

// Streak summary
export const mockStreakSummary: StreakSummary = {
  userId: MOCK_USER_ID,
  overallStreak: 12,
  longestStreak: 21,
  lastActivityDate: '2025-11-18',
  categoryStreaks: {
    health: 8,
    craft: 12,
    growth: 5,
    connection: 0,
  },
};

// DCI (Daily Consistency Index) data
export const mockDCISnapshot: DCISnapshot = {
  userId: MOCK_USER_ID,
  date: '2025-11-18',
  score: 0.73,
  status: 'Steady',
  breakdown: {
    streakFactor: 0.8,
    completionRate: 0.75,
    engagementDepth: 0.7,
    responseRate: 0.65,
  },
};

export const mockDCIHistory: DCIHistoryPoint[] = [
  { date: '2025-11-12', score: 0.65 },
  { date: '2025-11-13', score: 0.68 },
  { date: '2025-11-14', score: 0.72 },
  { date: '2025-11-15', score: 0.70 },
  { date: '2025-11-16', score: 0.75 },
  { date: '2025-11-17', score: 0.74 },
  { date: '2025-11-18', score: 0.73 },
];

// Highlight reels
export const mockHighlightReels: HighlightReel[] = [
  {
    id: 'reel_1',
    userId: MOCK_USER_ID,
    title: 'Your 7-Day Craft Streak',
    milestoneType: 'category_streak',
    content: {
      accomplishments: [
        'Completed 12 coding missions',
        'Built authentication system',
        'Learned React hooks pattern',
        'Maintained daily consistency',
      ],
      stats: {
        totalMissions: 12,
        totalMinutes: 380,
        streak: 7,
      },
      quote: 'Small daily steps compound into extraordinary results.',
    },
    generatedAt: '2025-11-18T08:00:00Z',
  },
];

// Narrative state and story beats
export const mockWorldState: WorldState = {
  locations: {
    arena: {
      discovered: true,
      description: 'A training ground for physical and creative pursuits',
      npcsPresent: ['Lyra', 'Thorne'],
    },
    observatory: {
      discovered: true,
      description: 'A quiet place for learning and reflection',
      npcsPresent: ['Elara'],
    },
    commons: {
      discovered: false,
      description: 'A gathering space for community and connection',
      npcsPresent: [],
      unlockCondition: 'Complete 5 connection missions',
    },
  },
  events: [
    {
      eventId: 'evt_1',
      occurredAt: '2025-11-15T10:00:00Z',
      impact: 'relationship+1',
      description: 'First meeting with Lyra in the Arena',
    },
  ],
  persons: {
    Lyra: {
      relationshipLevel: 3,
      lastInteraction: '2025-11-17T14:00:00Z',
      knowsAbout: ['user_craft_goals', 'coding_skills'],
      status: 'friendly',
    },
    Thorne: {
      relationshipLevel: 1,
      lastInteraction: '2025-11-15T10:00:00Z',
      knowsAbout: [],
      status: 'neutral',
    },
    Elara: {
      relationshipLevel: 2,
      lastInteraction: '2025-11-16T08:00:00Z',
      knowsAbout: ['reading_habit'],
      status: 'friendly',
    },
  },
  items: {
    essence: 485,
    titles: ['The Persistent'],
    artifacts: [
      {
        id: 'art_1',
        name: 'Medallion of Craft',
        acquiredAt: '2025-11-12T10:00:00Z',
        description: 'A bronze medallion awarded for 7-day craft consistency',
      },
    ],
  },
  worldTime: {
    currentAct: 1,
    currentChapter: 3,
    daysInStory: 45,
  },
};

export const mockNarrativeState: NarrativeState = {
  id: 'narr_1',
  userId: MOCK_USER_ID,
  scenarioId: 'scenario_modern',
  currentAct: 1,
  currentChapter: 3,
  daysInStory: 45,
  worldState: mockWorldState,
  createdAt: '2025-10-15T10:00:00Z',
  updatedAt: '2025-11-18T08:00:00Z',
};

export const mockStoryBeats: StoryBeat[] = [
  {
    id: 'beat_1',
    userId: MOCK_USER_ID,
    narrativeStateId: 'narr_1',
    act: 1,
    chapter: 3,
    title: 'Building Momentum',
    content: `The morning fog clings to the streets as you step outside. You've been at this for 45 days now—long enough that the routine feels natural, yet fresh enough that every completed mission still brings a quiet satisfaction.

Lyra sent you a message yesterday. "I've been watching your progress," she wrote. "You're not the same person who started this journey." She's right. The scattered approach you used to take—jumping between projects, never finishing anything—that version of you is fading.

Today, you have three clear missions. The authentication system won't build itself. Your gym session waits. A chapter of Atomic Habits beckons.

The choice is yours, but for the first time in a long while, you're not paralyzed by choice. You know what matters.`,
    emotionalTone: 'confident, determined',
    createdAt: '2025-11-18T06:00:00Z',
  },
  {
    id: 'beat_2',
    userId: MOCK_USER_ID,
    narrativeStateId: 'narr_1',
    act: 1,
    chapter: 2,
    title: 'Meeting Lyra',
    content: `The Arena is busier than you expected. Builders work on projects, their focused energy filling the space. You're here because Eliza suggested it. "Someone there can help you with your craft goals," she said.

A woman with paint-stained hands approaches. "You must be the new one Eliza mentioned. I'm Lyra." Her gaze is direct but not unkind. "Let me guess—you want to build something, but you keep starting and not finishing?"

You nod, surprised at how well she understands.

"That's common," she continues. "The problem isn't talent or time. It's that you're trying to do too much at once. Here's what we'll do: Pick one project. Just one. Work on it for 20 minutes tomorrow. Then we'll talk again."

Something about her certainty makes you believe it might actually work this time.`,
    emotionalTone: 'hopeful, curious',
    createdAt: '2025-11-15T10:00:00Z',
  },
];

// World zones
export const mockZoneStates: ZoneState[] = [
  {
    zone: ZONES.ARENA,
    available: true,
    charactersPresent: ['Lyra', 'Thorne'],
  },
  {
    zone: ZONES.OBSERVATORY,
    available: true,
    charactersPresent: ['Elara'],
  },
  {
    zone: ZONES.COMMONS,
    available: false,
    reason: 'Unlocks after completing 5 connection missions',
    charactersPresent: [],
  },
];

// Characters
export const mockCharacters: Character[] = [
  {
    id: 'char_1',
    name: 'Eliza',
    role: 'Primary Companion',
    description: 'Your empathetic guide who knows your journey and helps you stay on track',
    zone: ZONES.ARENA,
    relationshipLevel: 5,
  },
  {
    id: 'char_2',
    name: 'Lyra',
    role: 'Craft Mentor',
    description: 'Master artisan who helps you build and create with consistency',
    zone: ZONES.ARENA,
    relationshipLevel: 3,
  },
  {
    id: 'char_3',
    name: 'Commander Thorne',
    role: 'Health Guide',
    description: 'Veteran warrior who teaches discipline and physical wellness',
    zone: ZONES.ARENA,
    relationshipLevel: 1,
  },
  {
    id: 'char_4',
    name: 'Archmage Elara',
    role: 'Wisdom Keeper',
    description: 'Scholar who guides your learning and intellectual growth',
    zone: ZONES.OBSERVATORY,
    relationshipLevel: 2,
  },
];
