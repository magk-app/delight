/**
 * Mock data for development and testing
 * TODO: Replace with real API calls in production
 */

import type {
  Mission,
  Goal,
  Memory,
  StoryBeat,
  DCISnapshot,
  DCIHistoryPoint,
  StreakSummary,
  HighlightReel,
  NarrativeState,
  Character,
  MissionTriad,
} from "../types";
import {
  VALUE_CATEGORIES,
  MISSION_STATUS,
  GOAL_STATUS,
  MEMORY_TIER,
} from "../constants";

// Mock Goals
export const mockGoals: Goal[] = [
  {
    id: "goal-1",
    title: "Build a consistent morning routine",
    description:
      "Establish a morning routine that includes meditation, exercise, and journaling to start each day with intention and energy.",
    valueCategory: VALUE_CATEGORIES.WELLNESS,
    status: GOAL_STATUS.ACTIVE,
    targetDate: "2024-12-31",
    createdAt: "2024-01-15",
  },
  {
    id: "goal-2",
    title: "Complete online course on React",
    description:
      "Finish the advanced React course and build 3 portfolio projects to demonstrate mastery.",
    valueCategory: VALUE_CATEGORIES.LEARNING,
    status: GOAL_STATUS.ACTIVE,
    targetDate: "2024-11-30",
    createdAt: "2024-02-01",
  },
  {
    id: "goal-3",
    title: "Run a half marathon",
    description:
      "Train consistently and complete a half marathon race by the end of the year.",
    valueCategory: VALUE_CATEGORIES.FITNESS,
    status: GOAL_STATUS.ACTIVE,
    targetDate: "2024-12-15",
    createdAt: "2024-01-20",
  },
  {
    id: "goal-4",
    title: "Launch side project",
    description:
      "Build and launch a side project that solves a real problem and generates initial revenue.",
    valueCategory: VALUE_CATEGORIES.CAREER,
    status: GOAL_STATUS.COMPLETED,
    createdAt: "2023-11-01",
  },
];

// Mock Missions
export const mockMissions: Mission[] = [
  {
    id: "mission-1",
    title: "Morning meditation session",
    description: "10-minute guided meditation focusing on gratitude and intention setting",
    valueCategory: VALUE_CATEGORIES.WELLNESS,
    status: MISSION_STATUS.PENDING,
    estimatedMinutes: 10,
    energyLevel: "low",
    goalId: "goal-1",
    goal: { id: "goal-1", title: "Build a consistent morning routine" },
    createdAt: "2024-10-15",
  },
  {
    id: "mission-2",
    title: "Complete React hooks chapter",
    description: "Study and practice React hooks: useState, useEffect, and custom hooks",
    valueCategory: VALUE_CATEGORIES.LEARNING,
    status: MISSION_STATUS.IN_PROGRESS,
    estimatedMinutes: 45,
    energyLevel: "medium",
    goalId: "goal-2",
    goal: { id: "goal-2", title: "Complete online course on React" },
    createdAt: "2024-10-14",
  },
  {
    id: "mission-3",
    title: "5K tempo run",
    description: "Run 5 kilometers at a steady pace, focusing on maintaining consistent speed",
    valueCategory: VALUE_CATEGORIES.FITNESS,
    status: MISSION_STATUS.COMPLETED,
    estimatedMinutes: 30,
    energyLevel: "high",
    goalId: "goal-3",
    goal: { id: "goal-3", title: "Run a half marathon" },
    createdAt: "2024-10-13",
    completedAt: "2024-10-13",
  },
  {
    id: "mission-4",
    title: "Review project architecture",
    description: "Review and document the current architecture of the side project",
    valueCategory: VALUE_CATEGORIES.CAREER,
    status: MISSION_STATUS.COMPLETED,
    estimatedMinutes: 60,
    energyLevel: "medium",
    goalId: "goal-4",
    goal: { id: "goal-4", title: "Launch side project" },
    createdAt: "2024-10-12",
    completedAt: "2024-10-12",
  },
  {
    id: "mission-5",
    title: "Write blog post draft",
    description: "Draft a blog post about lessons learned from building the side project",
    valueCategory: VALUE_CATEGORIES.CREATIVITY,
    status: MISSION_STATUS.DEFERRED,
    estimatedMinutes: 90,
    energyLevel: "medium",
    createdAt: "2024-10-11",
  },
  {
    id: "mission-6",
    title: "Call family member",
    description: "Have a meaningful conversation with a family member you haven't talked to recently",
    valueCategory: VALUE_CATEGORIES.RELATIONSHIPS,
    status: MISSION_STATUS.PENDING,
    estimatedMinutes: 20,
    energyLevel: "low",
    createdAt: "2024-10-10",
  },
];

// Mock Mission Triad
export const mockMissionTriad: MissionTriad = {
  high: {
    id: "mission-1",
    title: "Morning meditation session",
    description: "10-minute guided meditation focusing on gratitude and intention setting",
    valueCategory: VALUE_CATEGORIES.WELLNESS,
    status: MISSION_STATUS.PENDING,
    estimatedMinutes: 10,
    energyLevel: "low",
    goalId: "goal-1",
    goal: { id: "goal-1", title: "Build a consistent morning routine" },
  },
  medium: {
    id: "mission-2",
    title: "Complete React hooks chapter",
    description: "Study and practice React hooks: useState, useEffect, and custom hooks",
    valueCategory: VALUE_CATEGORIES.LEARNING,
    status: MISSION_STATUS.IN_PROGRESS,
    estimatedMinutes: 45,
    energyLevel: "medium",
    goalId: "goal-2",
    goal: { id: "goal-2", title: "Complete online course on React" },
  },
  low: {
    id: "mission-6",
    title: "Call family member",
    description: "Have a meaningful conversation with a family member you haven't talked to recently",
    valueCategory: VALUE_CATEGORIES.RELATIONSHIPS,
    status: MISSION_STATUS.PENDING,
    estimatedMinutes: 20,
    energyLevel: "low",
  },
};

// Mock Memories
export const mockMemories: Memory[] = [
  {
    id: "memory-1",
    content:
      "User prefers morning workouts and finds them more energizing than evening sessions. Responds well to positive reinforcement.",
    tier: MEMORY_TIER.SEMANTIC,
    tags: ["fitness", "preferences", "routine"],
    createdAt: "2024-09-15T08:00:00Z",
    accessedAt: "2024-10-14T10:30:00Z",
  },
  {
    id: "memory-2",
    content:
      "User mentioned feeling overwhelmed when too many missions are assigned at once. Prefers 3-5 missions per day maximum.",
    tier: MEMORY_TIER.EPISODIC,
    tags: ["preferences", "mission-planning"],
    createdAt: "2024-10-10T14:20:00Z",
    accessedAt: "2024-10-14T09:15:00Z",
  },
  {
    id: "memory-3",
    content:
      "User's primary value categories are Wellness, Learning, and Career. Shows strong engagement with missions in these areas.",
    tier: MEMORY_TIER.SEMANTIC,
    tags: ["values", "engagement"],
    createdAt: "2024-08-20T12:00:00Z",
    accessedAt: "2024-10-13T16:45:00Z",
  },
  {
    id: "memory-4",
    content:
      "User completed React course module 3 with high satisfaction. Expressed interest in learning Next.js next.",
    tier: MEMORY_TIER.WORKING,
    tags: ["learning", "react", "next-steps"],
    createdAt: "2024-10-13T18:00:00Z",
    accessedAt: "2024-10-14T11:00:00Z",
  },
  {
    id: "memory-5",
    content:
      "User mentioned struggling with consistency on weekends. Suggested implementing weekend-specific mission types.",
    tier: MEMORY_TIER.EPISODIC,
    tags: ["consistency", "weekends", "feedback"],
    createdAt: "2024-10-08T10:00:00Z",
    accessedAt: "2024-10-12T14:30:00Z",
  },
];

// Mock DCI Snapshot
export const mockDCISnapshot: DCISnapshot = {
  score: 0.78,
  status: "Good",
  breakdown: {
    streakFactor: 0.85,
    completionRate: 0.72,
    engagementDepth: 0.80,
    responseRate: 0.75,
  },
};

// Mock DCI History (last 7 days)
const today = new Date();
export const mockDCIHistory: DCIHistoryPoint[] = Array.from({ length: 7 }, (_, i) => {
  const date = new Date(today);
  date.setDate(date.getDate() - (6 - i));
  return {
    date: date.toISOString().split("T")[0],
    score: 0.65 + Math.random() * 0.25, // Random score between 0.65 and 0.90
  };
});

// Mock Streak Summary
export const mockStreakSummary: StreakSummary = {
  overallStreak: 12,
  longestStreak: 28,
  categoryStreaks: {
    [VALUE_CATEGORIES.WELLNESS]: 12,
    [VALUE_CATEGORIES.LEARNING]: 8,
    [VALUE_CATEGORIES.FITNESS]: 5,
    [VALUE_CATEGORIES.CAREER]: 3,
    [VALUE_CATEGORIES.RELATIONSHIPS]: 2,
  },
};

// Mock Highlight Reels
export const mockHighlightReels: HighlightReel[] = [
  {
    id: "reel-1",
    title: "Week of Consistent Growth",
    content: {
      accomplishments: [
        "Completed 15 missions across 4 value categories",
        "Maintained 7-day streak in Wellness",
        "Finished React course module 3",
        "Improved DCI score by 12%",
      ],
      stats: {
        missionsCompleted: 15,
        averageCompletionRate: 85,
        categoriesActive: 4,
        streakDays: 7,
      },
      quote: "Consistency is the key to transformation.",
    },
    createdAt: "2024-10-14",
  },
  {
    id: "reel-2",
    title: "Learning Milestone",
    content: {
      accomplishments: [
        "Completed 5 learning missions",
        "Achieved 100% completion rate in Learning category",
        "Started new course module",
      ],
      stats: {
        learningMissions: 5,
        completionRate: 100,
        hoursSpent: 8,
      },
    },
    createdAt: "2024-10-10",
  },
];

// Mock Story Beats
export const mockStoryBeats: StoryBeat[] = [
  {
    id: "beat-1",
    title: "The Awakening",
    content:
      "As the first light of dawn filtered through your window, you felt a familiar pull—the call to begin another day of your journey. Eliza's voice echoed in your mind, gentle yet persistent: 'Today is not just another day. It's a chance to build upon yesterday's foundation.'\n\nYou opened the Delight app, and there they were: three missions, carefully chosen to align with your deepest values. The high-priority mission glowed with urgency, the medium one hummed with purpose, and the low-priority one whispered of easy wins.\n\nThis was Act 1, Chapter 1 of your story. The path ahead was unknown, but you were ready to take the first step.",
    act: 1,
    chapter: 1,
    createdAt: "2024-10-01T08:00:00Z",
    emotionalTone: "hopeful, determined",
  },
  {
    id: "beat-2",
    title: "The First Victory",
    content:
      "You completed your first mission—a simple morning meditation that took only ten minutes. But as you marked it complete, something shifted. The satisfaction wasn't just from checking a box; it was from honoring a commitment to yourself.\n\nEliza appeared in your narrative feed, her words warm and encouraging: 'Every completed mission strengthens your resolve. You're not just doing tasks—you're building a new version of yourself, one mission at a time.'\n\nThe world around you began to change. The locations you'd unlocked started to feel more real, more meaningful. The characters you'd met—Lyra the Mentor, Thorne the Challenger—seemed to take notice of your progress.",
    act: 1,
    chapter: 2,
    createdAt: "2024-10-02T09:30:00Z",
    emotionalTone: "accomplished, motivated",
  },
  {
    id: "beat-3",
    title: "The Challenge",
    content:
      "Week two brought a challenge you hadn't expected. A mission you'd been avoiding—one that required more energy than you felt you had. The temptation to defer was strong, but then you remembered why you started this journey.\n\nThorne's voice cut through your hesitation: 'Growth happens outside your comfort zone. This mission isn't just about the task—it's about proving to yourself that you can do hard things.'\n\nYou took a deep breath, accepted the mission, and began. It wasn't easy, but when you finished, you felt a surge of confidence you hadn't experienced in months. This was what real progress felt like.",
    act: 1,
    chapter: 5,
    createdAt: "2024-10-08T14:00:00Z",
    emotionalTone: "challenged, triumphant",
  },
];

// Mock Narrative State
export const mockNarrativeState: NarrativeState = {
  worldState: {
    worldTime: {
      currentAct: 1,
      currentChapter: 5,
      daysInStory: 45,
    },
    locations: {
      "The Garden": {
        discovered: true,
        description: "A peaceful space for reflection and growth",
      },
      "The Forge": {
        discovered: true,
        description: "Where challenges are met and skills are honed",
      },
      "The Library": {
        discovered: true,
        description: "A repository of knowledge and learning",
      },
      "The Summit": {
        discovered: false,
        description: "The highest point of achievement, yet to be reached",
      },
    },
    persons: {
      Eliza: {
        relationshipLevel: 5,
        status: "friendly",
      },
      Lyra: {
        relationshipLevel: 4,
        status: "friendly",
      },
      Thorne: {
        relationshipLevel: 3,
        status: "neutral",
      },
    },
    items: {
      essence: 1250,
      titles: ["The Determined", "The Learner", "The Consistent"],
    },
  },
};

// Mock Characters
export const mockCharacters: Character[] = [
  {
    id: "char-1",
    name: "Eliza",
    role: "Companion",
    description:
      "Your primary AI companion, wise and supportive, always ready to guide you on your journey.",
    relationshipLevel: 5,
  },
  {
    id: "char-2",
    name: "Lyra",
    role: "Mentor",
    description:
      "A gentle mentor who provides encouragement and helps you see the bigger picture.",
    relationshipLevel: 4,
  },
  {
    id: "char-3",
    name: "Thorne",
    role: "Challenger",
    description:
      "A tough challenger who pushes you to grow by presenting difficult but rewarding missions.",
    relationshipLevel: 3,
  },
];

