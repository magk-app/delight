/**
 * User Factory
 *
 * Creates test users via API with faker-generated data.
 * Supports overrides for specific test scenarios.
 * Auto-cleanup on test completion.
 *
 * Knowledge Base: bmad/bmm/testarch/knowledge/data-factories.md
 *
 * Usage:
 *   const user = await userFactory.createUser({ email: 'specific@example.com' });
 */

import { faker } from "@faker-js/faker";

export interface User {
  id: string;
  email: string;
  name: string;
  clerkId?: string;
}

export class UserFactory {
  private createdUsers: string[] = [];
  private apiBaseUrl: string;

  constructor(apiBaseUrl: string) {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Create a test user with random data
   * @param overrides - Partial user data to override defaults
   */
  async createUser(overrides: Partial<User> = {}): Promise<User> {
    const userData = {
      email: faker.internet.email().toLowerCase(),
      name: faker.person.fullName(),
      ...overrides,
    };

    // Create user via API
    const response = await fetch(`${this.apiBaseUrl}/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Add auth header if needed
        ...(process.env.CLERK_SECRET_KEY && {
          Authorization: `Bearer ${process.env.CLERK_SECRET_KEY}`,
        }),
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`);
    }

    const created = await response.json();
    this.createdUsers.push(created.id);

    return created;
  }

  /**
   * Create a user with companion initialization
   * Useful for tests that need full user setup
   */
  async createUserWithCompanion(overrides: Partial<User> = {}): Promise<User> {
    const user = await this.createUser(overrides);

    // Initialize companion for user
    await fetch(`${this.apiBaseUrl}/users/${user.id}/companion/initialize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    return user;
  }

  /**
   * Cleanup - delete all created users
   * Called automatically by fixture after test
   */
  async cleanup(): Promise<void> {
    for (const userId of this.createdUsers) {
      try {
        await fetch(`${this.apiBaseUrl}/users/${userId}`, {
          method: "DELETE",
          headers: {
            ...(process.env.CLERK_SECRET_KEY && {
              Authorization: `Bearer ${process.env.CLERK_SECRET_KEY}`,
            }),
          },
        });
      } catch (error) {
        console.warn(`Failed to cleanup user ${userId}:`, error);
      }
    }
    this.createdUsers = [];
  }
}
