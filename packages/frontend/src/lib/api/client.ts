/**
 * API Client - Central abstraction layer for all backend communication
 *
 * Currently returns mock data to enable frontend development.
 * When backend is ready, swap mock imports for real fetch calls.
 *
 * Features:
 * - Automatic camelCase/snake_case transformation
 * - Centralized error handling
 * - Easy migration path from mocks to real API
 */

import {
  mockGoals,
  mockMissions,
  mockMemories,
  mockDCISnapshot,
  mockDCIHistory,
  mockStreakSummary,
  mockHighlightReels,
  mockStoryBeats,
  mockNarrativeState,
  mockCharacters,
  mockMissionTriad,
} from '../mock/data';

import type {
  Goal,
  Mission,
  Memory,
  DCISnapshot,
  DCIHistoryPoint,
  StreakSummary,
  HighlightReel,
  StoryBeat,
  NarrativeState,
  Character,
  MissionTriad,
} from '../types';

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Future implementation: Transform snake_case keys to camelCase
 * Utility for converting backend responses to frontend format
 */
// import humps from 'humps';
// function transformResponse<T>(data: any): T {
//   return humps.camelizeKeys(data) as T;
// }

/**
 * Future implementation: Transform camelCase keys to snake_case
 * Utility for converting frontend requests to backend format
 */
// function transformRequest(data: any): any {
//   return humps.decamelizeKeys(data);
// }

// ============================================================================
// Goals API
// ============================================================================

export async function getGoals(): Promise<Goal[]> {
  // TODO: Replace with real API call when backend is ready
  // const response = await fetch(`${API_BASE_URL}/api/v1/goals`);
  // if (!response.ok) throw new Error('Failed to fetch goals');
  // const data = await response.json();
  // return transformResponse<Goal[]>(data);

  return Promise.resolve(mockGoals);
}

export async function getGoal(id: string): Promise<Goal | undefined> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/goals/${id}`);
  // if (!response.ok) throw new Error('Failed to fetch goal');
  // const data = await response.json();
  // return transformResponse<Goal>(data);

  return Promise.resolve(mockGoals.find((g) => g.id === id));
}

// ============================================================================
// Missions API
// ============================================================================

export async function getMissions(): Promise<Mission[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/missions`);
  // if (!response.ok) throw new Error('Failed to fetch missions');
  // const data = await response.json();
  // return transformResponse<Mission[]>(data);

  return Promise.resolve(mockMissions);
}

export async function getMission(id: string): Promise<Mission | undefined> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/missions/${id}`);
  // if (!response.ok) throw new Error('Failed to fetch mission');
  // const data = await response.json();
  // return transformResponse<Mission>(data);

  return Promise.resolve(mockMissions.find((m) => m.id === id));
}

export async function getMissionTriad(): Promise<MissionTriad> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/missions/triad`);
  // if (!response.ok) throw new Error('Failed to fetch mission triad');
  // const data = await response.json();
  // return transformResponse<MissionTriad>(data);

  return Promise.resolve(mockMissionTriad);
}

// ============================================================================
// Memory API
// ============================================================================

export async function getMemories(): Promise<Memory[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/memories`);
  // if (!response.ok) throw new Error('Failed to fetch memories');
  // const data = await response.json();
  // return transformResponse<Memory[]>(data);

  return Promise.resolve(mockMemories);
}

export async function searchMemories(query: string): Promise<Memory[]> {
  // TODO: Replace with real API call (semantic search)
  // const response = await fetch(`${API_BASE_URL}/api/v1/memories/search`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ query }),
  // });
  // if (!response.ok) throw new Error('Failed to search memories');
  // const data = await response.json();
  // return transformResponse<Memory[]>(data);

  // Simple mock search: filter by content
  const lowerQuery = query.toLowerCase();
  return Promise.resolve(
    mockMemories.filter((m) => m.content.toLowerCase().includes(lowerQuery))
  );
}

// ============================================================================
// Progress & DCI API
// ============================================================================

export async function getDCISnapshot(): Promise<DCISnapshot> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/progress/dci/snapshot`);
  // if (!response.ok) throw new Error('Failed to fetch DCI snapshot');
  // const data = await response.json();
  // return transformResponse<DCISnapshot>(data);

  return Promise.resolve(mockDCISnapshot);
}

export async function getDCIHistory(days: number = 30): Promise<DCIHistoryPoint[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/progress/dci/history?days=${days}`);
  // if (!response.ok) throw new Error('Failed to fetch DCI history');
  // const data = await response.json();
  // return transformResponse<DCIHistoryPoint[]>(data);

  return Promise.resolve(mockDCIHistory);
}

export async function getStreakSummary(): Promise<StreakSummary> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/progress/streak`);
  // if (!response.ok) throw new Error('Failed to fetch streak summary');
  // const data = await response.json();
  // return transformResponse<StreakSummary>(data);

  return Promise.resolve(mockStreakSummary);
}

export async function getHighlightReels(): Promise<HighlightReel[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/progress/highlights`);
  // if (!response.ok) throw new Error('Failed to fetch highlight reels');
  // const data = await response.json();
  // return transformResponse<HighlightReel[]>(data);

  return Promise.resolve(mockHighlightReels);
}

// ============================================================================
// Narrative API
// ============================================================================

export async function getStoryBeats(): Promise<StoryBeat[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/narrative/beats`);
  // if (!response.ok) throw new Error('Failed to fetch story beats');
  // const data = await response.json();
  // return transformResponse<StoryBeat[]>(data);

  return Promise.resolve(mockStoryBeats);
}

export async function getNarrativeState(): Promise<NarrativeState> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/narrative/state`);
  // if (!response.ok) throw new Error('Failed to fetch narrative state');
  // const data = await response.json();
  // return transformResponse<NarrativeState>(data);

  return Promise.resolve(mockNarrativeState);
}

export async function getCharacters(): Promise<Character[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/narrative/characters`);
  // if (!response.ok) throw new Error('Failed to fetch characters');
  // const data = await response.json();
  // return transformResponse<Character[]>(data);

  return Promise.resolve(mockCharacters);
}

// ============================================================================
// Companion Chat API (Lab)
// ============================================================================

export async function sendChatMessage(message: string): Promise<string> {
  // TODO: Replace with real streaming API call
  // const response = await fetch(`${API_BASE_URL}/api/v1/companion/chat`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ message }),
  // });
  // if (!response.ok) throw new Error('Failed to send chat message');
  // const data = await response.json();
  // return data.response;

  // Mock response
  return Promise.resolve(
    `I hear you saying: "${message}". This is a mock response. In production, this will connect to the Eliza AI companion.`
  );
}
