/**
 * Quest Factory
 *
 * Creates test quests and missions via API.
 * Supports different quest types (short-term, long-term, project).
 * Auto-cleanup on test completion.
 *
 * Knowledge Base: bmad/bmm/testarch/knowledge/data-factories.md
 */

import { faker } from "@faker-js/faker";

export interface Quest {
  id: string;
  userId: string;
  title: string;
  description: string;
  type: "short_term" | "long_term" | "project";
  status: "active" | "completed" | "abandoned";
  missions?: Mission[];
}

export interface Mission {
  id: string;
  questId: string;
  title: string;
  description: string;
  status: "todo" | "in_progress" | "completed";
  order: number;
}

export class QuestFactory {
  private createdQuests: string[] = [];
  private apiBaseUrl: string;

  constructor(apiBaseUrl: string) {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Create a test quest
   */
  async createQuest(
    userId: string,
    overrides: Partial<Quest> = {}
  ): Promise<Quest> {
    const questData = {
      userId,
      title: faker.lorem.sentence(3),
      description: faker.lorem.paragraph(),
      type: "short_term" as const,
      status: "active" as const,
      ...overrides,
    };

    const response = await fetch(`${this.apiBaseUrl}/quests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(questData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create quest: ${response.statusText}`);
    }

    const created = await response.json();
    this.createdQuests.push(created.id);

    return created;
  }

  /**
   * Create a quest with missions
   */
  async createQuestWithMissions(
    userId: string,
    missionCount: number = 3,
    overrides: Partial<Quest> = {}
  ): Promise<Quest> {
    const quest = await this.createQuest(userId, overrides);

    // Create missions
    const missions: Mission[] = [];
    for (let i = 0; i < missionCount; i++) {
      const mission = await this.createMission(quest.id, { order: i });
      missions.push(mission);
    }

    return { ...quest, missions };
  }

  /**
   * Create a mission for a quest
   */
  async createMission(
    questId: string,
    overrides: Partial<Mission> = {}
  ): Promise<Mission> {
    const missionData = {
      questId,
      title: faker.lorem.sentence(2),
      description: faker.lorem.sentence(),
      status: "todo" as const,
      order: 0,
      ...overrides,
    };

    const response = await fetch(`${this.apiBaseUrl}/missions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(missionData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create mission: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Cleanup - delete all created quests
   */
  async cleanup(): Promise<void> {
    for (const questId of this.createdQuests) {
      try {
        await fetch(`${this.apiBaseUrl}/quests/${questId}`, {
          method: "DELETE",
        });
      } catch (error) {
        console.warn(`Failed to cleanup quest ${questId}:`, error);
      }
    }
    this.createdQuests = [];
  }
}
