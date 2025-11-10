/**
 * Playwright Test Fixtures
 * 
 * Extends base Playwright test with custom fixtures for Delight:
 * - userFactory: Create/cleanup test users via API
 * - questFactory: Create/cleanup test quests
 * - companionFactory: Initialize companion state for testing
 * 
 * Pattern: Pure function → fixture → mergeTests composition
 * Auto-cleanup: All factories clean up resources after tests
 * 
 * Usage:
 *   import { test, expect } from '../support/fixtures';
 *   test('my test', async ({ page, userFactory }) => { ... });
 */

import { test as base } from '@playwright/test';
import { UserFactory } from './factories/user-factory';
import { QuestFactory } from './factories/quest-factory';
import { CompanionFactory } from './factories/companion-factory';

type TestFixtures = {
  userFactory: UserFactory;
  questFactory: QuestFactory;
  companionFactory: CompanionFactory;
  apiBaseUrl: string;
};

export const test = base.extend<TestFixtures>({
  // API base URL from environment
  apiBaseUrl: async ({}, use) => {
    const apiUrl = process.env.API_URL || 'http://localhost:8000/api/v1';
    await use(apiUrl);
  },

  // User factory - create/cleanup test users
  userFactory: async ({ apiBaseUrl }, use) => {
    const factory = new UserFactory(apiBaseUrl);
    await use(factory);
    await factory.cleanup(); // Auto-cleanup all created users
  },

  // Quest factory - create/cleanup test quests
  questFactory: async ({ apiBaseUrl }, use) => {
    const factory = new QuestFactory(apiBaseUrl);
    await use(factory);
    await factory.cleanup(); // Auto-cleanup all created quests
  },

  // Companion factory - initialize companion state
  companionFactory: async ({ apiBaseUrl }, use) => {
    const factory = new CompanionFactory(apiBaseUrl);
    await use(factory);
    await factory.cleanup(); // Auto-cleanup companion state
  },
});

// Re-export expect for convenience
export { expect } from '@playwright/test';

