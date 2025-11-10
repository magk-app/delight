/**
 * Companion Factory
 *
 * Initializes companion AI state for testing.
 * Creates conversations, memories, and emotional context.
 * Auto-cleanup on test completion.
 */

import { faker } from "@faker-js/faker";

export interface CompanionState {
  userId: string;
  conversationId: string;
  emotionalState?: {
    sentiment: number;
    emotions: Record<string, number>;
  };
  memories?: any[];
}

export class CompanionFactory {
  private createdConversations: string[] = [];
  private apiBaseUrl: string;

  constructor(apiBaseUrl: string) {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Initialize companion for a user
   */
  async initializeCompanion(userId: string): Promise<CompanionState> {
    const response = await fetch(`${this.apiBaseUrl}/companion/initialize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId }),
    });

    if (!response.ok) {
      throw new Error(`Failed to initialize companion: ${response.statusText}`);
    }

    const state = await response.json();
    this.createdConversations.push(state.conversationId);

    return state;
  }

  /**
   * Create a conversation with initial messages
   */
  async createConversation(
    userId: string,
    messageCount: number = 3
  ): Promise<CompanionState> {
    const state = await this.initializeCompanion(userId);

    // Send test messages
    for (let i = 0; i < messageCount; i++) {
      await fetch(`${this.apiBaseUrl}/companion/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          conversationId: state.conversationId,
          message: faker.lorem.sentence(),
        }),
      });
    }

    return state;
  }

  /**
   * Seed companion memories
   */
  async seedMemories(userId: string, memories: any[]): Promise<void> {
    await fetch(`${this.apiBaseUrl}/companion/memories/seed`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, memories }),
    });
  }

  /**
   * Cleanup - clear companion state
   */
  async cleanup(): Promise<void> {
    for (const conversationId of this.createdConversations) {
      try {
        await fetch(
          `${this.apiBaseUrl}/companion/conversations/${conversationId}`,
          {
            method: "DELETE",
          }
        );
      } catch (error) {
        console.warn(
          `Failed to cleanup conversation ${conversationId}:`,
          error
        );
      }
    }
    this.createdConversations = [];
  }
}
